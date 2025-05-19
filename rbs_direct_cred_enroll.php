<?php

#$url = "$_SERVER[HTTP_HOST]";
#if (preg_match('/dev/', $url)) {
#	$emailsend = "true";
#} else {
#	$emailsend = "true";
#}

require_once './includes/sendmail_mandrill.php';
require_once './includes/mysql.php';
require_once('./includes/FPDF/fpdf.php');
require_once('./includes/FPDI/fpdi.php');
require_once('./includes/FPDF/draw.php');
#require_once('./includes/PHPWord.php');

$rbs_page = basename($_SERVER['PHP_SELF']);
$errorcheck = 0;
$problem = 0;

$curdate = date("Y-m-d");
$rbs_enrollment_complete = $curdate;

$datetoday = date("F d, Y");
$rbs{'Date'} = date("F d");
#$rbs{'Date'} = date("F d, Y");

$date = explode('/', date('m/d/Y'));

$rbs['RBS_Signer']          = "John Schaefer";
$rbs['RBS_Signer_Title']    = "Chief Legal Officer";
$rbs['RBS_Signer_Email']    = "PAIT@TDSClinical.com";
$rbs['rbs_company']         = "Pharm Assess";

$rbs['Month']               = $date[0];
$rbs['Day']                 = $date[1];
$rbs['Year']                = substr($date[2], 2, 2);
$rbs['Full_Year']           = $date[2];
$rbs['Quote_Exp']           = date("F d, Y", strtotime("+90 day"));

#if (isset($_COOKIE["direct_id"])) {
#	$direct_id  = $_COOKIE["direct_id"];
#} else {
#	header('Location: continue_enrollment.php');
#	exit();
#}

$direct_id = '1';

$returning_ncpdp = '5665953';
$returning_npi = '1234567789';

class PDF extends PDF_Draw {
}

##### Get Total Pharmacies Enrolling ###################################
$ph_counter = 1;
$sql = "SELECT enrollment_id
          FROM pharmassess.direct_enrollment_detail
          WHERE direct_enrollment_id = $direct_id
       ORDER BY id";

if ($pharms = $mysqli->prepare("$sql")) {
	$pharms->execute();
	$pharms->store_result();
	$total_pharms = $pharms->num_rows;
	$all_data = $pharms->get_result();
	$pharms->bind_result($id);
	
	while ($pharms->fetch()) {
		$enrollment[$ph_counter] = $id;
		$ph_counter++;
	}
	$pharms->close();
}

###################################################################

####Combine Pharmacy and RBS Data for output##################
#$pull['Primary_Contact_Name'] = 'Anton Fedosyuk';
#$pull['Authorized_Contact_Email'] = 'afedosyuk@tdsclinical.com';
$pull['Primary_Contact_Name'] = 'Brian Prowell';
#$pull['Authorized_Contact_Email'] = 'awelch@tdsclinical.com';
$pull['Primary_Contact_Email'] = 'bprowell@tdsclinical.com';

$input = array_merge($pull, $rbs);

###################################################################

$input['Primary_Contact_Name'] = str_replace(",", "", $input['Primary_Contact_Name']);
$folder = 'enrollments/'. $input['NCPDP'];
if (!file_exists($folder)) {
	mkdir($folder,0777);
}

$input['Owners'] = '';
$input['Owners'] = $input['Owner1_Name']; #Owner 1 will always be filled out
if ($input['Owner2_Name'] != '') {
	$input['Owners'] .= ", " . $input['Owner2_Name'];
}
if ($input['Owner2_Name'] != '') {
	$input['Owners'] .= ", " . $input['Owner3_Name'];
}
if ($input['Owner3_Name'] != '') {
	$input['Owners'] .= ", " . $input['Owner3_Name'];
}

if ($input['Address2'] != "") {
	$input['Street'] = $input['Address'] . ", " . $input['Address2'];
} else {
	$input['Street'] = $input['Address'];
}

###START PDF BUILDING PROCESS######################################
// initiate FPDI
$pdf = new PDF();
$pageno = 1; #This must be incremented (++) on each page added.
$pagenox = 198; #location on the page to display page number (x)
$pagenoy = 270; #location on the page to display page number (y)

#//Set global PDF values
$pdf->SetCompression(false);
$pdf->SetAutoPageBreak(false);
$pdf->SetFont('Helvetica');
$pdf->SetFontSize(11);
$pdf->SetTextColor(0, 0, 0);
###################################################################

$program = "RBS Direct";

if (preg_match('/Rx30|ComputerRx|HBS|LPS/i', $input['Software_Vendor'])) {
  $form = 'RBS_Direct_Agreement_TDS.pdf';
  $frms = '22';
  $amount = '250.00';
} 
else {
  $form = 'Non-TDS RBS Agreement.pdf';
  $frms = '1';
  $amount = '295.00';
}	  

$input['RBS_Amount'] = $amount;

### Add Authorized_Agent_Disclosure_Form Word File
$frms .= ', 8';
#####

### Create EFT Authorization Form Word File
#if (preg_match('/Pioneer/i', $input['Software_Vendor'])) {
#  $frms .= ', 12';
#}
#####

### Create EFT Authorization Form Word File
#if (preg_match('/QS\/1/i', $input['Software_Vendor'])) {
#  $frms .= ', 13';
#}
#####

### Create EFT Authorization Form Word File
#if (preg_match('/ComputerRx/i', $input['Software_Vendor'])) {
#  $frms .= ', 10';
#}
#else {
  $frms .= ', 9';
#}
#####

### Create Quote
#$frms .= ', 11';
#####

$db = 'rbsreporting';

$form_id = array();
$SignHere = [];
$DateSigned = [];
$Text = [];
$Zip = [];
$Number = [];
$Checkbox = [];

$Recon_SignHere = [];
$Recon_DateSigned = [];

echo "FORM: $frms\n";

if ($result = mysqli_query($mysqli, "SELECT id AS frm_id, location, pages, instructions, packet
                                       FROM $db.form_mst
				      WHERE id IN ($frms)
                                   ORDER BY packet")) {
  while ($form = mysqli_fetch_array($result)) {
#    $form{'location'} = substr($form{'location'}, 3);

    #### Loop through pages of Form adding $input values
    for ($pg = 1; $pg <= $form['pages']; $pg++) {
      $pdf->AddPage();
      if ($pg == 1) {       
        $pdf->setSourceFile($form['location']);
      }
      $page = $pdf->importPage($pg);
      $pdf->useTemplate($page, null, null, 0, 0, true);

      if ($pg == 11 || $pg == 12) {
        add_pharm_data($mysqli, $pdf, $form['frm_id'], $pg, $enrollment);
      }
      else {
        add_data($mysqli, $pdf, $form['frm_id'], $pg, $input);
      }

      $pdf->SetXY($pagenox, $pagenoy); 
      $pdf->Write(0, "$pageno"); 
      $pageno++; 
    }

    array_push($form_id, $form['frm_id']);
  }
}
else {
    printf("Prepared Statement Error: %s\n", $mysqli->error);
}


$packet = "enrollments/" . $input{'NCPDP'} . "/" . $input{'NCPDP'} . "_RBS_Agreement_Packet.pdf";

$pdf->Output($packet);

$config = new DocuSign\eSign\Configuration();
$apiClient = new DocuSign\eSign\Client\ApiClient($config);

try {
  $sendHandler = new SendEnvelope($apiClient);
  $result = $sendHandler->send($packet, $input['Primary_Contact_Name'], $input['Primary_Contact_Email'], $input['RBS_Signer'], $input['RBS_Signer_Email']);
} catch (Exception $e) {
  print ($e->getMessage());

  if ($e instanceof DocuSign\eSign\ApiException) {
    print ("\nAPI error information: \n");
    print ($e->getResponseObject());
  }
}

exit;

### Create Pharmacy Policy and Procedure Manual Word File
$templateProcessor = new \PhpOffice\PhpWord\TemplateProcessor('docs/RBS_Pharmacy_Policy_Procedure_Manual_Client_Questionnaire.docx');
$templateProcessor->setValue('year', htmlspecialchars($input['Full_Year']));
$templateProcessor->setValue('pharmacy', htmlspecialchars($input['Pharmacy_Name']));
$templateProcessor->setValue('ncpdp', htmlspecialchars($input['NCPDP']));
$templateProcessor->setValue('npi', htmlspecialchars($input['NPI']));
$templateProcessor->setValue('street', htmlspecialchars($input['Street']));
$templateProcessor->setValue('city', htmlspecialchars($input['City']));
$templateProcessor->setValue('state', htmlspecialchars($input['State']));
$templateProcessor->setValue('zip', htmlspecialchars($input['Zip']));
$templateProcessor->setValue('owners', htmlspecialchars($input['Owners']));
$templateProcessor->setValue('compliance', htmlspecialchars($input['Company_Contact_Name']));
$templateProcessor->setValue('monday', htmlspecialchars($input['Hours_Monday']));
$templateProcessor->setValue('tuesday', htmlspecialchars($input['Hours_Tuesday']));
$templateProcessor->setValue('wednesday', htmlspecialchars($input['Hours_Wednesday']));
$templateProcessor->setValue('thursday', htmlspecialchars($input['Hours_Thursday']));
$templateProcessor->setValue('friday', htmlspecialchars($input['Hours_Friday']));
$templateProcessor->setValue('saturday', htmlspecialchars($input['Hours_Saturday']));
$templateProcessor->setValue('sunday', htmlspecialchars($input['Hours_Sunday']));
$templateProcessor->saveAs('enrollments/'. $input['NCPDP'].'/' . $input['NCPDP'] . '_RBS_Pharmacy_Policy_Procedure_Manual_Client_Questionnaire.docx');

### Create Staff Sheet Excel File
include '/includes/phpexcel/Classes/PHPExcel.php';
include '/includes/phpexcel/Classes/PHPExcel/IOFactory.php';

$SSNameIn  = 'docs/Staff_Sheet.xlsx';
$SSNameOut = 'enrollments/'. $input['NCPDP'] .'/' . $input['NCPDP'] . '_Staff_Sheet.xlsx';

$excel2 = PHPExcel_IOFactory::createReader('Excel2007');
$excel2 = $excel2->load($SSNameIn); // Template

$print_row = 7;
$excel2->setActiveSheetIndex(0);

$excel2->getActiveSheet()->setCellValue("A4", $input['Pharmacy_Name'])
					     ->setCellValue("C4", "NCPDP: ${input['NCPDP']}");
						 
if ($pull = $mysqli->prepare("
		SELECT fname, lname, license, type, exp_date, discipline 
		FROM pharmassess.employees WHERE ncpdp = ? && npi = ? 
		ORDER BY lname, fname")) {
	$pull->bind_param('ii', $returning_ncpdp, $returning_npi);
	$pull->execute();
	$employees = $pull->get_result();
    while ($row = $employees->fetch_assoc()) {
		$fname = $row['fname'];
		$lname = $row['lname'];
		$license = $row['license'];
		$type = $row['type'];
		$exp_date = $row['exp_date'];
		$discipline = $row['discipline'];
		#echo "<tr><td>$fname $lname</td><td>$license</td><td>$type</td><td>$exp_date</td><td>$discipline</td>";

		$excel2->getActiveSheet()->setCellValue("A${print_row}", "$fname $lname")
								 ->setCellValue("B${print_row}", $type)
								 ->setCellValue("C${print_row}", $license)
								 ->setCellValue("D${print_row}", $exp_date)
								 ;
		$print_row++;
    }
	$pull->close();
}
						 
$objWriter = PHPExcel_IOFactory::createWriter($excel2, 'Excel2007');
$objWriter->save($SSNameOut);

$savedir = "\\\\PASRV1\\DataShare\\Pharm AssessRBS\\Enrollment Forms\\Online Enrollments\\${input['NCPDP']}";
if (!file_exists($savedir)) {
    mkdir($savedir);
}

foreach (glob("enrollments/${input['NCPDP']}/{*.docx,*.xlsx}", GLOB_BRACE) as $file) {
	#echo "file: $file<br />";
	$pcs = explode('/', $file);
	$filename = array_pop($pcs);
	rename($file, "$savedir\\$filename");
}

// Moved Email Sending to bottom of page //

?>

<!doctype html> 
<html lang="en">
<head>
<title>Pharm Assess, Inc.</title>
<?php include 'includes/include_styles.php'; ?>
<link type="text/css" rel="stylesheet" media="screen" href="/css/rbs_enroll.css" />
<link rel="stylesheet" href="//code.jquery.com/ui/1.10.3/themes/smoothness/jquery-ui.css" />
<?php include 'includes/include_analytics.php'; ?>
</head>
<body>

<?php include 'includes/header_nav.php'; ?>

<div id="wrapper"><!-- wrapper -->
	<div id="content_container_front">
		<div id="mainbody_front">

			<h1>Thank you!</h1>

			<p>Thank you for completing the online portion of the enrollment process! An account manager will be reaching out to you soon.</p>
			
			<hr />
			
			<img src="/images/pa_rbs_logo.png" style="display: block; margin: 0 auto 0;" />
			
			<p style="text-align: center;"><a href="/index.php">Click here to go back to www.pharmassess.com</a></p>

			<?php

			// if ($emailsend == "false") {
				// echo "<p>url: $url | emailsend: $emailsend</p>\n";
			// }

			// if (file_exists($zipfile)) {
				// echo "<p class=\"download\"><a href=\"".$zipfile."\"><img src=\"images/clip.png\">Click Here to Download Contracts</a>";
				// echo "<div class=\"review_page\"><p><strong>Important</strong>: Your contracts have been saved in an encrypted zip file, this is to protect your information. The password will be the <strong>enrollment password</strong> you created at the beginning of the online enrollment process.</p></div>";
			// } else {
				// echo "<p style=\"color: #F00;\"><strong>There was a problem generating your contracts, please call or email rbs for assistance.</strong></p>";
				// $problem = 1;
			// }

			?>

		</div><!-- end mainbody_front -->

		<!-- Sidebar -------------------------------------------------------->
		<?php include 'includes/sidebar_enrollment.php'; ?>
		<!------------------------------------------------------------------->

	</div><!-- end content_container_front -->

</div><!-- end wrapper -->

<?php include 'includes/footer.php'; ?>

<?php 

#Pharmacy Email Content
$content = "
<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Transitional//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd\">
<html>
    <head>
        <meta http-equiv=\"Content-Type\" content=\"text/html; charset=UTF-8\" />
        
        <!-- Facebook sharing information tags -->
        <meta content=\"RBS Broadcast Communication\" />
        
        <title>RBS Broadcast Communication</title>

    <style type=\"text/css\">
      /* Client-specific Styles */
      #outlook a{padding:0;} /* Force Outlook to provide a \"view in browser\" button. */
      body{width:100% !important;} .ReadMsgBody{width:100%;} .ExternalClass{width:100%;} /* Force Hotmail to display emails at full width */
      body{-webkit-text-size-adjust:none;} /* Prevent Webkit platforms from changing default text sizes. */

      /* Reset Styles */
      body{margin:0; padding:0;}
      img{border:0; height:auto; line-height:100%; outline:none; text-decoration:none;}
      table td{border-collapse:collapse;}
      #table_main{height:100% !important; margin:0; padding:0; width:100% !important;}

      /* Template Styles */
      
      body, p, h1, h2 {
      text-align: left;
      }
      
      a {
      color: #917d15;
      }
      
      #table_main {
      background-color: #FFF;
      padding: 0px;
      margin: 8px 0px 0px 0px;
      }
      
      h1 {
      font-size: 20px;
      font-weight: none;
      line-height: 24px;
      color: #000;
      padding-bottom: 5px;
      border-bottom: 2px solid #000;
      }
      
      h2 {
      font-size: 20px;
      font-weight: bold;
      line-height: 24px;
      color: #917d15;
      }
      
      #table_content {
      background-color: #FFF;
      font-family: Helvetica, Arial;
      font-size: 14px;
      line-height: 18px;
      color: #000;
      padding: 0px;
      margin: 0px;
      }
      
    </style>
  </head>
  
    <body leftmargin=\"0\" marginwidth=\"0\" topmargin=\"0\" marginheight=\"0\">
    
  <table border=\"0\" cellpadding=\"0\" cellspacing=\"0\" height=\"100%\" width=\"100%\" id=\"table_main\">
  <tr><td>
  <center>    
    
    <!-- Header Logo and Contact Info -->
    
    <table border=\"0\" cellpadding=\"5\" cellspacing=\"0\" width=\"600\" id=\"table_content\">
    <tr><td width=60%>
    <img src=\"http://www.pharmassess.com/images/pa_rbs_logo.jpg\" alt=\"Pharm AssessRBS: Retail Business Solution\" />
    </td>
    <td style=\"padding-left: 8px;\">
    <strong><u>Contact Us:</u></strong><br />
    web: <a href=\"http://www.pharmassess.com/\" target=\"_blank\" style=\"color: #917d15;\">www.pharmassess.com</a><br />
    call: (888) 255-6526<br />
    email: <a href=\"mailto: CS@pharmassess.com?subject=RBS Broadcast Communication Question\" style=\"color: #917d15;\"> CS@pharmassess.com</a>
    </td></tr>
    </table>
    
    <!-- End Header -->
    
    <table border=\"0\" cellpadding=\"5\" cellspacing=\"0\" width=\"600\">
    <tr><td>

    <hr style=\"width: 600px;\" />
    
    <!-- Begin Message Content -->

<!--TITLE -->
<h2>Pharm Assess Online Enrollment Completed!</h2>
<!--END TITLE -->
    
<p>
Thank you for completing the online portion of the Pharm Assess enrollment, you are almost done with the enrollment process! Attached you will find a copy of your contracts (you may have already downloaded these from the website). Simply print, sign, and fax these documents back to <strong>(913) 897-4344</strong>.
</p>

<p>
Please note: The attached ZIP file containing your contracts has been password protected to protect your information. The password is the same as the enrollment password you created at the beginning of the online enrollment process. If you have any trouble, or can't remember your password, contact Pharm Assess for assistance.
</p>

<p>
We look forward to working with you! If you have any questions, please give us a call at (888) 255-6526 or send us an email at <a href=\"mailto:CS@pharmassess.com?subject=Pharm Assess Enrollment Question\" style=\"color: #006e8f;\">CS@pharmassess.com</a>.
    
    <!-- End Message Content -->

    <hr style=\"width: 600px;\" />
    
    </td></tr>
    </table>
    
    <div style=\"padding-bottom: 25px;\"></div>
    
  </center>
  </td></tr>
  </table>
  
  </body>
</html>
";

#-Send-Mail-Attachement---To-Pharmacy------------------------
// $to = $pull_main_contact_email;
// $from_email = 'cs@pharmassess.com';
// $from_name = "${pull_type} Enrollment";
// $subject = "Pharm Assess Online Enrollment Completed!";
// if ($emailsend == "true") {
	// sendmail_attachment_mandrill($to, $from_name, $from_email, $subject, $content, $zipfile);
// }
#--------------------------------------------------------------

#-Send-Mail---Internal-Notification--------------------------
if (preg_match('/RBS/i', $pull_type)) {
  $to = 'enrollmentRBS@pharmassess.com,pbettendorf@tdsclinical.com,alancia@tdsclinical.com';
} else {
  $to = 'enrollmentRBSCredentialing@pharmassess.com,pbettendorf@tdsclinical.com';
}

$subject    = "Pharm Assess ${pull_type} Online Enrollment Completed!";
$content    = "<p>$pull_pharmname has completed their ${pull_type} enrollment!</p><p>Contact Name: $pull_main_contact_name</p><p>Call: $pull_phone</p><p>Email: $pull_email</p>";


if ($emailsend == "true") {
  system("cmd /c D:\\RedeemRx\\Programs\\SendEmails\\send_email.bat \"$to\" \"$subject\" \"$content\"");
}
#--------------------------------------------------------------

include_once 'includes/log_activity.php';
$action = "$pull_pharmname completed Pharm Assess ${pull_type} enrollment";
if ($problem == 1) { 
	$action .= " PROBLEMS FOUND!!!";
}
log_activity($pull_pharmname, $action, $pull_ncpdp);

function add_data($mysqli, $pdf, $form_id, $pg, $input) {
  $dbase = $GLOBALS['db'];
#  echo "INTO add_data<br>";
  if ($result = mysqli_query($mysqli,"SELECT * FROM $dbase.form_dtl WHERE form_mst_id = $form_id AND form_page = $pg;")) {
    while ($dtl = mysqli_fetch_array($result)) {
      $val = $dtl{'value'};
      $docusign = $dtl{'docusign'};
      $tab_type = $dtl{'ds_type'};

      if ( $docusign ) {
        $sender_id = substr($val,0,1);
        $val = substr($val, 2);
        $x = intval($dtl{'x_cord'});
	$y = intval($dtl{'y_cord'});

        if ( $sender_id == 'R' ) {
          if ( $tab_type == 'SignHere' ) {
            array_push($GLOBALS['SignHere'], new DocuSign\eSign\Model\SignHere([ # DocuSign SignHere field/tab
                       'document_id' => '1', 'page_number' => $GLOBALS['pageno'], 'recipient_id' => '1',
                       'tab_label' => "$val", 'x_position' => $x, 'y_position' => $y
                      ]));
          }
  	  elseif ( $tab_type == 'DateSigned' ) {
            array_push($GLOBALS['DateSigned'], new DocuSign\eSign\Model\DateSigned([ # DocuSign SignHere field/tab
                       'document_id' => '1', 'page_number' => $GLOBALS['pageno'], 'recipient_id' => '1',
                       'tab_label' => "$val", 'x_position' => $x, 'y_position' => $y
                      ]));
          }
  	  elseif ( $tab_type == 'Text' ) {
            array_push($GLOBALS['Text'], new DocuSign\eSign\Model\Text([ # DocuSign Text field/tab
                       'document_id' => '1', 'page_number' => $GLOBALS['pageno'], 'recipient_id' => '1',
                       'tab_label' => "$val", 'x_position' =>$x, 'y_position' => $y
                      ]));
	  }
          elseif ( $tab_type == 'Number' ) {
            array_push($GLOBALS['Number'], new DocuSign\eSign\Model\Number([ # DocuSign Text field/tab
                       'document_id' => '1', 'page_number' => $GLOBALS['pageno'], 'recipient_id' => '1',
                       'tab_label' => "$val", 'x_position' => $x, 'y_position' => $y
                      ]));
	  }
	  elseif ( $tab_type == 'Zip' ) {
            array_push($GLOBALS['Zip'], new DocuSign\eSign\Model\Zip([ # DocuSign Zip field/tab
                       'document_id' => '1', 'page_number' => $GLOBALS['pageno'], 'recipient_id' => '1',
	               'tab_label' => "$val", 'x_position' => $x, 'y_position' => $y
                      ]));
	  }
	  elseif ( $tab_type == 'Checkbox' ) {
            array_push($GLOBALS['Checkbox'], new DocuSign\eSign\Model\Checkbox([ # DocuSign Checkbox field/tab
                       'document_id' => '1', 'page_number' => $GLOBALS['pageno'], 'recipient_id' => '1',
                       'tab_label' => "$val", 'x_position' =>$x, 'y_position' => $y
                      ]));
	  }
	}
	else {
          if ( $tab_type == 'SignHere' ) {
            array_push($GLOBALS['Recon_SignHere'], new DocuSign\eSign\Model\SignHere([ # DocuSign SignHere field/tab
                       'document_id' => '1', 'page_number' => $GLOBALS['pageno'], 'recipient_id' => '1',
                       'tab_label' => "$val", 'x_position' => $x, 'y_position' => $y
                      ]));
          }
  	  elseif ( $tab_type == 'DateSigned' ) {
            array_push($GLOBALS['Recon_DateSigned'], new DocuSign\eSign\Model\DateSigned([ # DocuSign SignHere field/tab
                       'document_id' => '1', 'page_number' => $GLOBALS['pageno'], 'recipient_id' => '1',
                       'tab_label' => "$val", 'x_position' => $x, 'y_position' => $y
                      ]));
          }
	}
      }
      else {
        if (preg_match_all("/[{}]/", $val)) {
          $pcs = preg_split('/\s+/', $val);
          foreach ($pcs as $pc) {
            $key = preg_replace("/[{},]/", "", $pc);
	    $pc = preg_replace("/,/", "", $pc);
            if (array_key_exists($key, $input)) {
              $val = preg_replace("/$pc/", $input{$key}, $val);
  	    }
          }
        }
        else {
          if (array_key_exists($dtl{'value'}, $input)) {
            $val = $input{$dtl{'value'}};
	  }
	  else {
            $val = $dtl{'value'};
          }
        }
        $pdf->SetXY($dtl{'x_cord'}, $dtl{'y_cord'});
        $pdf->Write(0, $val);
      }
    }
  }
  else {
    $error = "Problem querying your data.";
    echo "Problem querying your data. -" . mysqli_error($mysqli);
  }
} 

function add_pharm_data($mysqli, $pdf, $form_id, $pg, $enrollment) {
  $dbase = $GLOBALS['db'];
  $counter = 1;	

  if ( $pg == 11 ) {
    $pharm_counter = 1;
  }
  else {
    $pharm_counter = 4;
  }

  if ($result = mysqli_query($mysqli,"SELECT * FROM $dbase.form_dtl WHERE form_mst_id = $form_id AND form_page = $pg ORDER BY y_cord;")) {
    while ($dtl = mysqli_fetch_array($result)) {
      $val = $dtl['value'];
      $docusign = $dtl['docusign'];
      $tab_type = $dtl['ds_type'];

      ###### Get Pharmacy Enrollment Data #########################
      if ( $val == 'Pharmacy_Name' || $counter == 1) {
        if ($pharm_counter > count($enrollment)) {
          break;
	}

	$enrollment_id = $enrollment[$pharm_counter];

        if ($retval = mysqli_query($mysqli, "SELECT 
                                                 rbs_pharmname AS Pharmacy_Name,
	                                         rbs_ncpdp AS NCPDP,
		                                 rbs_npi AS NPI,
                                                 rbs_main_address1 AS Address,
                                                 rbs_main_address2 AS Address2,
                                                 rbs_main_city AS City,
                                                 rbs_main_state AS State,
                                                 rbs_main_zip AS Zip,
                                                 rbs_phone AS Business_Phone,
                                                 rbs_fax AS Fax_Number,
                                                 rbs_main_contact_name AS Primary_Contact_Name,
                                                 rbs_main_contact_title AS Primary_Contact_Title,
                                                 rbs_main_contact_email AS Primary_Contact_Email,
                                                 rbs_main_contact_phone AS Primary_Contact_Phone,
                                                 rbs_contact_comp_name AS Company_Contact_Name
                                               FROM pharmassess.enrollment 
			                      WHERE id = $enrollment_id")) {
          $data = mysqli_fetch_assoc($retval);

          $brackets = array(')','(');

          mysqli_free_result($retval);
        }
        else {
          printf("Prepared Statement Error: %s\n", $mysqli->error);
	}
        $pharm_counter++;
      }
      ###############################################################

#      echo "FIELD: $val VALUE: " . $data{$val} . "\n";


      if (preg_match_all("/[{}]/", $val)) {
        $pcs = preg_split('/\s+/', $val);
        foreach ($pcs as $pc) {
          $key = preg_replace("/[{},]/", "", $pc);
	  $pc = preg_replace("/,/", "", $pc);
          if (array_key_exists($key, $data)) {
            $val = preg_replace("/$pc/", $data{$key}, $val);
	  }
        }
      }
      else {
        if (array_key_exists($dtl{'value'}, $data)) {
          $val = $data{$dtl{'value'}};
	}
        else {
          $val = $dtl{'value'};
        }
      }
      $pdf->SetXY($dtl{'x_cord'}, $dtl{'y_cord'});
      $pdf->Write(0, $val);
      $counter++;
    }
  }
  else {
    $error = "Problem querying your data.";
    echo "Problem querying your data. -" . mysqli_error($mysqli);
  }
}  

$mysqli->close();

?>

</body>
</html>
