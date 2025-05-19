<?php

// Create connection
include 'D:/www/includes/mysql.php';
require_once('D:/www/includes/FPDF/fpdf.php');
require_once('D:/www/includes/FPDI/fpdi.php');
require_once('D:/www/includes/FPDF/draw.php');
require_once('D:/www/includes/PHPWord.php');

class PDF extends PDF_Draw {
}

// Check connection
if (mysqli_connect_errno($mysqli))
  {
  echo "Failed to connect to MySQL: " . mysqli_connect_error();
  }

$createdate= date('Y-m-d H:i:s');

$submit      = $_POST["submit"];
$PH_ID = $_COOKIE[PH_ID];
$employee_id  = $_POST["employee_id"];
$learnable_id = $_POST["learnable_id"];


$pageno = 1; #This must be incremented (++) on each page added.

if ($submit == 'Submit') {
  get_pdf($mysqli, $employee_id, $learnable_id);
}
##      <link rel="stylesheet" href="style.css" type="text/css" />

?>

<!DOCTYPE html>
   <head>
      <meta http-equiv="Content-type" content="text/html; charset=utf-8">
      <title>Credentialing Certificate Print</title>
      <style>
        
      </style>
   </head>
<body>

<div class="wrapper_small">

<h2>Credentialing Certificate Print</h2>
<hr />

<form action="Cred_Certificate_Download.php" method="post">
<p>Choose Employee:
<select name="employee_id">
<option>Select Employee...</option>

<?php
$result = mysqli_query($mysqli,"SELECT id, fname, lname FROM pharmassess.credentialing_employees WHERE Pharmacy_ID = $PH_ID ORDER BY lname;");

if (isset($employee_id)) {
   echo "<option value=\"" . $employee_id . "\"  selected=\selected\">" . $ncpdp . " - Last Selected Pharmacy</option>\n";
}

while ($row = mysqli_fetch_assoc($result)) {
  echo "<option value=\"" . $row{'id'} . "\">" . $row{'fname'} . "  " . $row{'lname'} . "</option>\n";
}

mysqli_free_result($result);
echo "</select>";
?>

<p>Choose Certificate:
<select name="learnable_id">
<option>Select Certificate...</option>

<?php
$result = mysqli_query($mysqli,"SELECT title, learnableid FROM pharmassess.credentialing_bridge_ref ORDER BY title;");

if (isset($learnable_id)) {
   echo "<option value=\"" . $learnable_id . "\"  selected=\selected\">" . $ncpdp . " - Last Selected Pharmacy</option>\n";
}

while ($row = mysqli_fetch_assoc($result)) {
  echo "<option value=\"" . $row{'learnableid'} . "\">".$row{'title'}."</option>\n";
}

mysqli_free_result($result);
echo "</select>";
?>

<hr />

<INPUT name="submit" class="button-form" style="width: 58px" TYPE="submit" VALUE="Submit">

</form>
<hr />

<?php
function get_pdf($mysqli, $eid, $lid) {

### RECON GLOBALS TO BE USED FOR ALL DOCUMENTS ################################
include "\\\\out-paiwebprd01\\WWW/varstest.php";
  $recon{'Today'}               = date('m/d/Y');      

  $date = explode('/', $recon{'Today'});

  $recon{'Month'}               = $date[0];
  $recon{'Month_SP'}            = date("F");
  $recon{'Day'}                 = $date[1];
  $recon{'Full_Year'}           = $date[2];
  $recon{'Year'}                = substr($date[2], 2, 2);
  $recon{'Date'}                = date("F d, Y");


  $pdf = new PDF();
  
  //Set global PDF values
  $pdf->SetCompression(false);
  $pdf->SetAutoPageBreak(false);
  $pdf->SetFont('Helvetica');
  $pdf->SetFontSize(30);
  $pdf->SetTextColor(13,42,77);

  #### Pull Pharmacy Data
  if ($result = mysqli_query($mysqli, "SELECT UserName, b.Title, CompletionDate, Score 
                                         FROM pharmassess.credentialing_employees_training a
                                              JOIN pharmassess.credentialing_bridge_ref b ON a.LearnableID = b.LearnableID
					WHERE Employee_ID = '$eid' 
                                        && a.LearnableID = $lid")) {
    $pull = mysqli_fetch_assoc($result);
    $brackets = array(')','(');
    if($pull == false) {
     echo "<script>alert('No Certificate Found'$learnable_id);</script>";
	return;
    }

    mysqli_free_result($result);
  }
  else {
    $error = "Problem querying your data.";
    echo "Problem querying your data. -" . mysqli_error($mysqli);
  }


  #### Combine Pharmacy and ReconRx Data for output
  $auth_form = 121;

  $input = array_merge($pull, $recon);

  
  #### Get Form Information
  if ($result = mysqli_query($mysqli, "SELECT id AS frm_id, location, pages
	                                 FROM pharmassess.credform_mst_testing a
				        WHERE id IN ($auth_form)
                                     ;")) {

    while ($form = mysqli_fetch_array($result)) {
     $dir = "\\\\out-paiwebprd01\\WWW\\members.pharmassess.com/";
     $location = str_replace("../","$dir",$form{'location'});

      for ($pg = 1; $pg <= $form{pages}; $pg++) {
        $pdf->AddPage();
	if ($pg == 1) {       
          $pdf->setSourceFile($location);

	}
        $page = $pdf->importPage($pg);
        $pdf->useTemplate($page, null, null, 0, 0, true);

        add_data($mysqli, $pdf, $form{'frm_id'}, $pg, $input, $test_type);
	$GLOBALS['pageno']++;
	
      }

      $form_name = $form{'form_name'} . ".pdf";
      array_push($form_id, $form{'frm_id'});    
    }
  }
  else {
    $error = "Problem querying your data.";
    echo "Problem querying your data. " . mysqli_error($mysqli);
  }

  $packet = "../testing/" . $input{'NCPDP'} . "$form_name";
  if ($test_type == 1) {
    $pdf->Output($packet);
  }
  else {
    $pdf->Output($packet, "D");
  }

  echo "File download should have started!<br>";
}	


function add_data($mysqli, $pdf, $form_id, $pg, $input, $test_type) {
  $dbase = $GLOBALS['db'];

  if ($result = mysqli_query($mysqli,"SELECT * FROM pharmassess.credform_dtl WHERE form_mst_id = $form_id;")) {
    while ($dtl = mysqli_fetch_array($result)) {
      $val = $dtl{'value'};
      $docusign = $dtl{'docusign'};
      $tab_type = $dtl{'ds_type'};
      $pge = $GLOBALS['pageno'];
        if (array_key_exists($dtl{'value'}, $input)) {
          $val = $input{$dtl{'value'}};
	}
	else {
          $val = $dtl{'value'};
        }

      if ($dtl{'value'} == 'Title') {
        $pdf->SetFontSize(20);
	if ($pdf->GetStringWidth($val) > 160) {
          $pdf->SetFontSize(18);
        }
	if ($pdf->GetStringWidth($val) > 170) {
          $pdf->SetFontSize(16);
        }
      }
      if ($dtl{'value'} == 'Score') {
        $pdf->SetFontSize(10);
	$val = "$val%";
      }

      $pdf->SetXY($dtl{'x_cord'}, $dtl{'y_cord'});
      $pdf->Write(0, $val);
    }
  }
  else {
    $error = "Problem querying your data.";
    echo "Problem querying your data. -" . mysqli_error($mysqli);
  }
}

?>

</div><!-- end wrapper -->

</body>
</html> 

<?php

mysqli_close($mysqli);
?> 
