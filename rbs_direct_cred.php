<?php

// Create connection
#$con=mysqli_connect("192.168.2.2","pharm","assess","ReconRxDB");
#include '../includes/mysql.php';
#require_once('../includes/FPDF/fpdf.php');
#require_once('../includes/FPDI/fpdi.php');
#require_once('../includes/FPDF/draw.php');
#require_once('../includes/PHPWord.php');

require_once './includes/sendmail_mandrill.php';
require_once './includes/mysql.php';
require_once('./includes/FPDF/fpdf.php');
require_once('./includes/FPDI/fpdi.php');
require_once('./includes/FPDF/draw.php');

class PDF extends PDF_Draw {
}

// Check connection
if (mysqli_connect_errno($mysqli))
  {
  echo "Failed to connect to MySQL: " . mysqli_connect_error();
  }

$createdate= date('Y-m-d H:i:s');

$cred_form   = $_POST["cred_form"];
$ncpdp       = $_POST["ncpdp"];
#$pharmacy_id = $_POST["pharmacy_id"];
$submit      = $_POST["submit"];

if ($submit == 'Submit') {
  get_pdf($mysqli, $ncpdp, $cred_form);
}

$ncpdp = '1701362';

?>

<!DOCTYPE html>
   <head>
      <meta http-equiv="Content-type" content="text/html; charset=utf-8">
      <title>RBS Direct Credentialing</title>
      <link rel="stylesheet" href="style.css" type="text/css" />
      <style>
        
      </style>
   </head>
<body>

<div class="wrapper_small">

<h2>RBS Direct Credentialing</h2>
<hr />

<form action="rbs_direct_cred.php" method="post">
<p>Choose NCPDP:
<select name="ncpdp">
<option>Select Pharmacy...</option>

<?php
$result = mysqli_query($mysqli,"SELECT Pharmacy_Id, ncpdp, pharmacy_name FROM officedb.pharmacy WHERE Type LIKE '%RBS Direct%' AND ncpdp IN ('1701362','1103388','1106788','1167825') ORDER BY pharmacy_name;");

if (isset($ncpdp)) {
   echo "<option value=\"" . $ncpdp . "\"  selected=\selected\">" . $ncpdp . " - Last Selected Pharmacy</option>\n";
}

while ($row = mysqli_fetch_assoc($result)) {
  echo "<option value=\"" . $row{'ncpdp'} . "\">" . $row{'ncpdp'} . " - " . $row{'pharmacy_name'} . "</option>\n";
}

mysqli_free_result($result);
echo "</select>";

echo "<p>Choose Credentialing Contract:";
echo "<select name=\"cred_form\">";
echo "<option>Select Form...</option>";


if ($result = mysqli_query($mysqli,"SELECT id, form_name
	                              FROM rbsreporting.form_mst
				     WHERE form_type = 'CRD'
                                       AND active = 1 
				  ORDER BY form_name;")) {
				  
  while ($row = mysqli_fetch_array($result)) {
    echo "<option value=\"" . $row{'id'} . "\">" . $row{'form_name'} . "</option>\n" ;
  }
} else {
  echo "<option value=\"\">" . "ERROR LOADING..." . mysqli_error($mysqli) . "</option>\n" ;
}

mysqli_free_result($result);
?>

</select>
<hr />

<INPUT name="submit" class="button-form" style="width: 58px" TYPE="submit" VALUE="Submit">

</form>
<hr />

<?php
function get_pdf($mysqli, $ncpdp, $cred_form) {
#  echo "INTO get_pdf<br>";
### RECON GLOBALS TO BE USED FOR ALL DOCUMENTS ################################
  $recon{'Rx_Name'}             = "ReconRx/Pharm Assess, Inc.";
  $recon{'Rx_DBA'}              = "Pharm Assess, Inc. dba ReconRx";
  $recon{'Rx_DBA_TDS'}          = "TDS dba ReconRx";
  $recon{'Rx_ID'}               = "PHARM ASSESS";
  $recon{'Rx_Password'}         = "PArbs1996";

  $recon{'Rx_Signer'}          = "John Schaefer";
  $recon{'Rx_Signer_Title'}    = "Chief Legal Officer";
  $recon{'Rx_Signer_Email'}    = "JSchaefer@TDSClinical.com";

  $recon{'Rx_Contact'}          = "Monty Rogers";
  $recon{'Rx_Contact_Title'}    = "Chief Strategy Officer";
  $recon{'Rx_Contact_Email'}    = "RECON@TDSClinical.com";
  $recon{'Rx_Contact_Phone'}    = "(913) 897-4343";
  $recon{'Rx_Contact_Phone_NB'} = "913 897-4343";
  $recon{'Rx_Contact_Ext'}      = "ext. 117";
  $recon{'Rx_Alt_Contact'}      = "Jessie Kanatzar";
  $recon{'Rx_Alt_Contact_Email'}= "PAIT@TDSClinical.com";
  $recon{'Rx_Fax_Number'}       = "(888) 618-8535";
  $recon{'Rx_Fax_Number_NB'}    = "888 618-8535";
  $recon{'Rx_Fax_Number2'}      = "(913) 897-4344";
  $recon{'Rx_Mailing_Address'}  = "PO Box 12750";
  $recon{'Rx_Pa_Address'}       = "PO Box 12428";
  $recon{'Rx_Mailing_City'}     = "Overland Park";
  $recon{'Rx_Mailing_State'}    = "KS";
  $recon{'Rx_Mailing_Zip'}      = "66282";
  $recon{'Rx_CS'}               = "Customer Service";
  $recon{'Rx_CS_Email'}         = "RECON@TDSClinical.com";
  $recon{'Rx_IT'}               = "IT";
  $recon{'Rx_IT_Email'}         = "PAIT@TDSClinical.com";
  $recon{'Rx_Prod_Email'}       = "TPP_Notice@TDSClinical.com";
  $recon{'Rx_Toll_Free_Phone'}  = "(888) 255-6526";
  $recon{'Rx_Toll_Free_Fax'}    = "(888) 618-0262";
  $recon{'Rx_Service_Center'}   = "2368";
  $recon{'Rx_Submitter_ID'}     = "94960";
  $recon{'Today'}               = date('m/d/Y');      
  $input{'Today'}               = date('m/d/Y');      

  $date = explode('/', $recon{'Today'});

  $recon{'Month'}               = $date[0];
  $recon{'Day'}                 = $date[1];
  $recon{'Full_Year'}           = $date[2];
  $recon{'Year'}                = substr($date[2], 2, 2);
  $input{'Date'}                = date("F d, Y");

  $pdf = new PDF();
  $pagenox = 198; #location on the page to display page number (x)
  $pagenoy = 270; #location on the page to display page number (y)		
  
  //Set global PDF values
  $pdf->SetCompression(false);
  $pdf->SetAutoPageBreak(false);
  $pdf->SetFont('Helvetica');
  $pdf->SetFontSize(10);
  $pdf->SetTextColor(0, 0, 0);

  #### Pull Pharmacy Data
  $sql = "SELECT qa_id, value
            FROM pharmassess.direct_cred
           WHERE enrollment_detail_id IN (SELECT a.id
                                            FROM pharmassess.direct_enrollment_detail a
                                            JOIN pharmassess.enrollment b ON (a.enrollment_id = b.id)
                                           WHERE b.rbs_ncpdp = '$ncpdp')
	ORDER BY qa_id";

  if ($pharms = $mysqli->prepare("$sql")) {
 	$pharms->execute();
	$pharms->store_result();
	$pharms->bind_result($id, $value);
	
	while ($pharms->fetch()) {
		#echo "$id -> $value<br>";
		$input[$id] = $value;
		if ( $id >= 154 AND $id <= 160 ) {
			$open  = $id . '_O';
			$close = $id . '_C';
			if ( $value == 'closed' ) {
				$input[$open]  = $value;
				$input[$close] = $value;
			}
			else {
	                        $pcs = explode(' to ', $value);
				$input[$open]  = $pcs[0];
				$input[$close] = $pcs[1];
			}
		}
	}
	$pharms->close();
  }
  else {
    echo "Problem querying your data. " . mysqli_error($mysqli);
  }

  #### Combine Pharmacy and ReconRx Data for output

#  foreach ($input as $key => $value) {
#    echo "{$key} => {$value}<br>";
#  }
  
  #### Get Form Information
  if ($result = mysqli_query($mysqli, "SELECT id AS frm_id, form_name, location, pages
	                                 FROM rbsreporting.form_mst
					WHERE id = $cred_form;")) {
    while ($form = mysqli_fetch_array($result)) {
#      echo "Before FOR loop<br>";
       #### Loop through pages of Form adding $input values
      for ($pg = 1; $pg <= $form{pages}; $pg++) {
        $pdf->AddPage();
	if ($pg == 1) {       
          $pdf->setSourceFile($form{'location'});
	}
        $page = $pdf->importPage($pg);
        $pdf->useTemplate($page, null, null, 0, 0, true);

        add_data($mysqli, $pdf, $form{'frm_id'}, $pg, $input);
      }

      $form_name = $form{'form_name'} . ".pdf";
    }
  }
  else {
    $error = "Problem querying your data.";
    echo "Problem querying your data. " . mysqli_error($mysqli);
  }

#  $form = $form{'form_name'} . ".pdf";
#  $pdf->Output("F", "../docs/tmp_doc.pdf");
#  $pdf->Output("tmp_doc.pdf", "D");
  $pdf->Output($form_name, "D");

  echo "File download should have started!<br>";
}	

function add_data($mysqli, $pdf, $form_id, $pg, $input) {
#  echo "INTO add_data<br>";
  if ($result = mysqli_query($mysqli,"SELECT * FROM rbsreporting.form_dtl WHERE form_mst_id = $form_id AND form_page = $pg AND docusign = 0;")) {
    while ($dtl = mysqli_fetch_array($result)) {
      $val = $dtl{'value'};

      if (preg_match_all("/[{}]/", $val)) {
        $pcs = preg_split('/\s+/', $val);
	foreach ($pcs as $pc) {
	  $key = preg_replace("/[{},]/", "", $pc);
	  $pc = preg_replace("/,/", "", $pc);
	  if (array_key_exists($key, $input)) {
            #$val = preg_replace("/$pc/", $input{$key}, $val);
            $val = preg_replace("/$key/", $input{$key}, $val);
	  }
	  else {
            $val = preg_replace("/$key/", '', $val);
          }
        }
        $val = preg_replace("/{|}/", "", $val);
      }
      else {
##        if (array_key_exists($dtl{'value'}, $input)) {
        if (array_key_exists($dtl{'value'}, $input)) {
          $val = $input{$dtl{'value'}};
	}
	else {
          if (is_numeric($dtl{'value'})) {
            $val = '';
	  }
	  else {
            $val = $dtl{'value'};
	  }
        }
      }
#      echo "Value inserted: $val<br>";
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
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------

mysqli_close($mysqli);
?> 
