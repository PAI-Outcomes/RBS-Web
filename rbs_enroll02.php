<?php

include 'includes/mysql.php';

$rbs_page = basename($_SERVER['PHP_SELF']);
$curdate = date("Y-m-d");
$errorcheck = 0;
$row_cnt = 0;

$url = "$_SERVER[HTTP_HOST]";
if ($url == "dev.pharmassess.com") {
	$emailsend = "false";
} else {
	$emailsend = "true";
}

if (isset($_COOKIE["cont1"]) && isset($_COOKIE["cont2"])&& isset($_COOKIE["cont3"])) {
	$returning_ncpdp  = $_COOKIE["cont1"];
	$returning_npi    = $_COOKIE["cont2"];
	$returning_rec_id = $_COOKIE["cont3"];
} else {
	header('Location: continue_enrollment.php');
	exit();
}
include 'includes/status.php';

if (($pull_status == "") || ($pull_status == "complete")) {
	setcookie("cont1", "", time()+10800);
	setcookie("cont2", "", time()+10800);
	setcookie("cont3", "", time()+10800);
	$returning_ncpdp  = "";
	$returning_npi    = "";
	$returning_rec_id = "";
	
	if ($pull_status == "complete") {
		$pull_status = "";
	}
}

###GATHER POST DATA################################################
$all_post = "";
foreach ($_POST as $param_name => $param_val) {
	if (isset($param_val) && $param_val != "") { 
		#echo "Param: $param_name; Value: $param_val<br />\n";
		$$param_name = $param_val; 
		$all_post .= "$param_name: $param_val, ";
	} else { 
		$$param_name = ""; 
	}
}
$all_post = rtrim($all_post, ', ');
###################################################################

###SET VALUES TO DB################################################
if ($rbs_main_address1 != "") {
	if ($stmt = $mysqli->prepare("
		UPDATE pharmassess.enrollment SET  
		rbs_main_address1=?, 
		rbs_main_address2=?, 
		rbs_main_city=?, 
		rbs_main_state=?, 
		rbs_main_zip=?, 
		rbs_main_county_parish=?, 
		rbs_mailing_address1=?, 
		rbs_mailing_address2=?, 
		rbs_mailing_city=?, 
		rbs_mailing_state=?, 
		rbs_mailing_zip=?, 
		rbs_mailing_county_parish=?, 
		rbs_page=? 
		
		WHERE id =? 
		;")) {
		$stmt->bind_param('ssssisssssissi', $rbs_main_address1, $rbs_main_address2, $rbs_main_city, $rbs_main_state, $rbs_main_zip, $rbs_main_county_parish, $rbs_mailing_address1, $rbs_mailing_address2, $rbs_mailing_city, $rbs_mailing_state, $rbs_mailing_zip, $rbs_mailing_county_parish, $rbs_page, $returning_rec_id);
		$stmt->execute();
		$stmt->close();
	}
	else {
		printf("Prepared Statement Error: %s\n", $mysqli->error);
		$errorcheck = 1;
	}
	
	if ($errorcheck != 1) {
		if ($pull_status != "pending") {
			header('Location: rbs_enroll_review.php#enroll02');
		} else {
			header('Location: rbs_enroll03.php');
		}
		exit();
	}
	
}
###################################################################

###READ VALUES FROM DB#############################################
$sql = "
SELECT COLUMN_NAME
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA='pharmassess' && TABLE_NAME='enrollment';
";
if ($pull = $mysqli->prepare("$sql")) {
	$pull->execute();
	$all_data = $pull->get_result();
    while ($row = $all_data->fetch_assoc()) {
		$field = $row['COLUMN_NAME'];
		$sqlx = "SELECT $field FROM pharmassess.enrollment WHERE id = ?";
		if ($value_pull = $mysqli->prepare("$sqlx")) {
			$value_pull->bind_param('i', $returning_rec_id);
			$value_pull->execute();
			$single_field_data = $value_pull->get_result();
			while ($row2 = $single_field_data->fetch_assoc()) {
				$efield = str_replace('rbs', 'pull', $field);
				$$efield = $row2["$field"];
				#echo "$efield = ". $row2["$field"] . "<br />";
			}
		}
    }
}
###################################################################

// if ($errorcheck != 1) {
	// if (($pull_status == "pending") && ($emailsend == "true")) {
		
		// require_once 'includes/PHPMailer/class.phpmailer.php';
		
		// if (preg_match('/RBS/i', $rbs_type)) {
			// $notification_email = "enrollmentRBS@pharmassess.com";
		// } else {
			// $notification_email = "enrollmentRBSCredentialing@pharmassess.com";
		// }
		
		// $update = new PHPMailer();
		// $update->From      = 'cs@pharmassess.com';
		// $update->FromName  = 'New RBS Enrollment';
		// $update->AddAddress( $notification_email );
		// #$update->AddCC( 'josh@pharmassess.com' );
		// $update->Subject   = "New RBS ($rbs_type) Enrollment Started";
		// $update->Body      = "
// $pull_pharmname has started their RBS ($rbs_type) online enrollment!\n
// Contact Info:
// Primary Contact: $pull_main_contact_name
// Call: $pull_phone
// Email: $pull_email
// ";
		// $update->Send();
		
		// include_once 'includes/log_activity.php';
		// $action = "$pull_pharmname started RBS enrollment";
		// log_activity($pull_pharmname, $action, $returning_ncpdp);
		
	// }
// }

#-Send-Mail---Internal-Notification--------------------------
if ($errorcheck != 1) {
	if (($pull_status == "pending") && ($emailsend == "true")) {
		$to = "RBS@tdsclinical.com";
		$subject = "NEW Outcomes ${pull_type} Online Enrollment!";
		$content = "<p>". $pull_pharmname . " has started their "  . $pull_type . " enrollment!</p><p>Contact Name: " . $pull_main_contact_name ."</p> <p>Call: " . $pull_phone. "</p> <p>Email: ". $pull_email. "</p>";

		if ($emailsend == "true") {
                  system("cmd /c D:\\RedeemRx\\Programs\\SendEmails\\send_email.bat \"$to\" \"$subject\" \"$content\"");
		}
	}
}
#--------------------------------------------------------------

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

<!--Header and Navigation-------------------------------------------->
<?php include 'includes/header_nav.php'; ?>
<!------------------------------------------------------------------->

<script src="//code.jquery.com/ui/1.10.3/jquery-ui.js"></script>
<script src="/includes/jquery.maskedinput.min.js" type="text/javascript"></script>
<script src="/includes/checkRequiredFields.js"></script>

<script>
$(function() {
	$('.zip').mask("99999",{placeholder:" "});
});
</script>

<div id="wrapper"><!-- wrapper -->

	<div id="content_container_front">
	<div id="mainbody_front">

	<h1>Pharmacy Address</h1>
	<form name="enroll" action="<?php echo $_SERVER['PHP_SELF']; ?>" onsubmit="return checkRequiredFields(this)" method="post">

	<div class="rbs-two-column-wrapper clear">

	<p>Enter your pharmacy information in the fields below.</p> 

	</div> <!-- end rbs-two-column-wrapper -->

	<div class="rbs-two-column-wrapper">

		<div class="rbs-two-column">
			
			<h2>Physical Address</h2>

			<div class="field_title">Address Line 1</div>
			<INPUT class="rbs-input-text-form required" TYPE="text" NAME="rbs_main_address1" VALUE="<?php echo $pull_main_address1; ?>">

			<div class="field_title">Address Line 2</div>
			<INPUT class="rbs-input-text-form" TYPE="text" NAME="rbs_main_address2" VALUE="<?php echo $pull_main_address2; ?>">

			<div class="field_title">City</div>
			<INPUT class="rbs-input-text-form required" TYPE="text" NAME="rbs_main_city" VALUE="<?php echo $pull_main_city; ?>">

			<div class="field_title">State</div>
			<select name="rbs_main_state" class="rbs-dropdown-form required">
			<?php if ($pull_main_state == "") {
				echo "<option value=\"\" selected></option>";
			} else {
				echo "<option value=\"$pull_main_state\" selected>$pull_main_state</option>";
			} ?>
			<option value="AL">AL</option>
			<option value="AK">AK</option>
			<option value="AZ">AZ</option>
			<option value="AR">AR</option>
			<option value="CA">CA</option>
			<option value="CO">CO</option>
			<option value="CT">CT</option>
			<option value="DE">DE</option>
			<option value="DC">DC</option>
			<option value="FL">FL</option>
			<option value="GA">GA</option>
			<option value="HI">HI</option>
			<option value="ID">ID</option>
			<option value="IL">IL</option>
			<option value="IN">IN</option>
			<option value="IA">IA</option>
			<option value="KS">KS</option>
			<option value="KY">KY</option>
			<option value="LA">LA</option>
			<option value="ME">ME</option>
			<option value="MD">MD</option>
			<option value="MA">MA</option>
			<option value="MI">MI</option>
			<option value="MN">MN</option>
			<option value="MS">MS</option>
			<option value="MO">MO</option>
			<option value="MT">MT</option>
			<option value="NE">NE</option>
			<option value="NV">NV</option>
			<option value="NH">NH</option>
			<option value="NJ">NJ</option>
			<option value="NM">NM</option>
			<option value="NY">NY</option>
			<option value="NC">NC</option>
			<option value="ND">ND</option>
			<option value="OH">OH</option>
			<option value="OK">OK</option>
			<option value="OR">OR</option>
			<option value="PA">PA</option>
			<option value="PR">PR</option>
			<option value="RI">RI</option>
			<option value="SC">SC</option>
			<option value="SD">SD</option>
			<option value="TN">TN</option>
			<option value="TX">TX</option>
			<option value="UT">UT</option>
			<option value="VT">VT</option>
			<option value="VA">VA</option>
			<option value="WA">WA</option>
			<option value="WV">WV</option>
			<option value="WI">WI</option>
			<option value="WY">WY</option>
			</select>
			
			<div class="field_title">Zip</div>
			<INPUT class="rbs-input-text-form zip required" TYPE="text" NAME="rbs_main_zip" VALUE="<?php echo $pull_main_zip; ?>">
			
			<div class="field_title">County or Parish</div>
			<INPUT class="rbs-input-text-form required" TYPE="text" NAME="rbs_main_county_parish" VALUE="<?php echo $pull_main_county_parish; ?>">
			
		</div> <!-- rbs-two-column -->

		<div class="rbs-two-column">
			
			<h2>Mailing Address
				<input type="checkbox" id="same_address" name="same_address"><p style="display: inline; font-size: 10px;">Same as physical</p>
			</h2>
			
			<div class="field_title">Address Line 1</div>
			<INPUT class="rbs-input-text-form required" TYPE="text" NAME="rbs_mailing_address1" VALUE="<?php echo $pull_mailing_address1; ?>">

			<div class="field_title">Address Line 2</div>
			<INPUT class="rbs-input-text-form" TYPE="text" NAME="rbs_mailing_address2" VALUE="<?php echo $pull_mailing_address2; ?>">

			<div class="field_title">City</div>
			<INPUT class="rbs-input-text-form required" TYPE="text" NAME="rbs_mailing_city" VALUE="<?php echo $pull_mailing_city; ?>">
			
			<div class="field_title">State</div>
			<select name="rbs_mailing_state" class="rbs-dropdown-form required">
			<?php if ($pull_mailing_state == "") {
				echo "<option value=\"\" selected></option>";
			} else {
				echo "<option value=\"$pull_mailing_state\" selected>$pull_mailing_state</option>";
			} ?>
			<option value="AL">AL</option>
			<option value="AK">AK</option>
			<option value="AZ">AZ</option>
			<option value="AR">AR</option>
			<option value="CA">CA</option>
			<option value="CO">CO</option>
			<option value="CT">CT</option>
			<option value="DE">DE</option>
			<option value="DC">DC</option>
			<option value="FL">FL</option>
			<option value="GA">GA</option>
			<option value="HI">HI</option>
			<option value="ID">ID</option>
			<option value="IL">IL</option>
			<option value="IN">IN</option>
			<option value="IA">IA</option>
			<option value="KS">KS</option>
			<option value="KY">KY</option>
			<option value="LA">LA</option>
			<option value="ME">ME</option>
			<option value="MD">MD</option>
			<option value="MA">MA</option>
			<option value="MI">MI</option>
			<option value="MN">MN</option>
			<option value="MS">MS</option>
			<option value="MO">MO</option>
			<option value="MT">MT</option>
			<option value="NE">NE</option>
			<option value="NV">NV</option>
			<option value="NH">NH</option>
			<option value="NJ">NJ</option>
			<option value="NM">NM</option>
			<option value="NY">NY</option>
			<option value="NC">NC</option>
			<option value="ND">ND</option>
			<option value="OH">OH</option>
			<option value="OK">OK</option>
			<option value="OR">OR</option>
			<option value="PA">PA</option>
			<option value="PR">PR</option>
			<option value="RI">RI</option>
			<option value="SC">SC</option>
			<option value="SD">SD</option>
			<option value="TN">TN</option>
			<option value="TX">TX</option>
			<option value="UT">UT</option>
			<option value="VT">VT</option>
			<option value="VA">VA</option>
			<option value="WA">WA</option>
			<option value="WV">WV</option>
			<option value="WI">WI</option>
			<option value="WY">WY</option>
			</select>
			
			<div class="field_title">Zip</div>
			<INPUT class="rbs-input-text-form zip required" TYPE="text" NAME="rbs_mailing_zip" VALUE="<?php echo $pull_mailing_zip; ?>">
			
			<div class="field_title">County or Parish</div>
			<INPUT class="rbs-input-text-form required" TYPE="text" NAME="rbs_mailing_county_parish" VALUE="<?php echo $pull_mailing_county_parish; ?>">
			
		</div> <!-- rbs-two-column -->

	</div> <!-- end rbs-two-column-wrapper -->

	<div style="clear: both;"></div>
	<div id="errors"></div>
	
	<div class="rbs-two-column-wrapper">	
		<INPUT class="button-form-enroll" TYPE="submit" VALUE="<?php if ($pull_status != "pending") {echo "Update and Review";} else {echo "Next Page";} ?>">
	</div> <!-- end rbs-two-column-wrapper -->

	</div><!-- end mainbody_front -->

	<!-- Sidebar -------------------------------------------------------->
	<?php include 'includes/sidebar_enrollment.php'; ?>
	<!------------------------------------------------------------------->
	</form>
	</div><!-- end content_container_front -->

</div><!-- end wrapper -->
<!-- Footer ----------------------------------------------------->
<?php include 'includes/footer.php'; ?>
<!--------------------------------------------------------------->

<script>
$("#same_address").on("change", function(){
	if (this.checked) {
		$("[name='rbs_mailing_address1']").val($("[name='rbs_main_address1']").val());
		$("[name='rbs_mailing_address2']").val($("[name='rbs_main_address2']").val());
		$("[name='rbs_mailing_city']").val($("[name='rbs_main_city']").val());
		$("[name='rbs_mailing_state']").val($("[name='rbs_main_state']").val());
		$("[name='rbs_mailing_zip']").val($("[name='rbs_main_zip']").val());
		$("[name='rbs_mailing_county_parish']").val($("[name='rbs_main_county_parish']").val());
	}
});
</script> 

</body>
</html>

<?php $mysqli->close(); ?>
