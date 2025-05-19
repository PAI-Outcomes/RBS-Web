<?php

// ini_set('display_errors',1);
// ini_set('display_startup_errors',1);
// error_reporting(-1);

include 'includes/mysql.php';

$rbs_page = basename($_SERVER['PHP_SELF']);
$curdate = date("Y-m-d");
$errorcheck = 0;
$row_cnt = 0;

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
	$returning_ncpdp = "";
	$returning_npi   = "";
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
if ($rbs_fed_tax_id != "" && $rbs_state_tax_id != "") {
	if ($stmt = $mysqli->prepare("
		UPDATE pharmassess.enrollment SET  
		rbs_fed_tax_class = ?, 
		rbs_fed_tax_id = ?, 
		rbs_state_tax_id = ?, 
		rbs_medicareb = ?, 
		rbs_medicaid1 = ?, 
		rbs_medicaid_state1 = ?, 
		rbs_swvendor = ?, 
		rbs_switch = ?, 
		rbs_pri_wholesaler = ?, 
		rbs_wholesaler_acct_number = ?, 
		rbs_dea = ?, 
		rbs_dea_exp = ?, 
		rbs_state_license_number = ?, 
		rbs_state_license_exp = ?, 
		rbs_state_controlled_substance_license_number = ?, 
		rbs_state_controlled_substance_license_exp = ?, 
		rbs_business_liability_insurance_policy_number = ?, 
		rbs_business_liability_insurance_policy_exp = ?, 
		
		rbs_page=? 
		
		WHERE id=? 
		;")) {
		$stmt->bind_param('sssssssssssssssssssi', 
		$rbs_fed_tax_class, 
		$rbs_fed_tax_id, 
		$rbs_state_tax_id, 
		$rbs_medicareb, 
		$rbs_medicaid1, 
		$rbs_medicaid_state1, 
		$rbs_swvendor, 
		$rbs_switch, 
		$rbs_pri_wholesaler, 
		$rbs_wholesaler_acct_number, 
		$rbs_dea, 
		$rbs_dea_exp, 
		$rbs_state_license_number, 
		$rbs_state_license_exp, 
		$rbs_state_controlled_substance_license_number, 
		$rbs_state_controlled_substance_license_exp, 
		$rbs_business_liability_insurance_policy_number, 
		$rbs_business_liability_insurance_policy_exp, 
		$rbs_page, $returning_rec_id);
		$stmt->execute();
		$stmt->close();
	}
	else {
		printf("Prepared Statement Error: %s\n", $mysqli->error);
		$errorcheck = 1;
	}
	
	if ($errorcheck != 1) {
		if ($pull_status != "pending") {
			header('Location: rbs_enroll_review.php#enroll07');
		} else {
			header('Location: rbs_enroll08.php');
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
	$(".datepicker").mask("99/99/9999");
	$(".datepicker").datepicker();
	$("#anim").change(function() {
		$(".datepicker").datepicker( "option", "showAnim", $( this ).val() );
	});
	$('.phone').mask('(999) 999-9999');
	
});
</script>

<div id="wrapper"><!-- wrapper -->

	<div id="content_container_front">
	<div id="mainbody_front">

	<h1>Pharmacy Credentialing Information</h1>
	<form name="enroll" id="enroll" action="<?php echo $_SERVER['PHP_SELF']; ?>" onsubmit="return checkRequiredFields(this);" method="post">

	<div class="rbs-two-column-wrapper">
	
		<div class="rbs-two-column">

			<div class="field_title">Federal Tax Class</div>
			<!-- <INPUT class="rbs-input-text-form" TYPE="text" NAME="rbs_fed_tax_class" VALUE="<?php echo $pull_fed_tax_class; ?>"> -->
			<select name="rbs_fed_tax_class" class="rbs-dropdown-form required">
			<option value="<?php echo $pull_fed_tax_class; ?>"  <?php if ($pull_fed_tax_class != "")  {echo "selected";} ?>><?php echo $pull_fed_tax_class; ?></option>
			<option value="C-Corp">C-Corp</option>
			<option value="LLC">LLC</option>
			<option value="Non Profit/Exempt">Non Profit/Exempt</option>
			<option value="Partnership">Partnership</option>
			<option value="S-Corp">S-Corp</option>
			<option value="Sole Proprietor">Sole Proprietor</option>
			</select>

			<div class="field_title">Federal Tax ID (FEIN)</div>
			<INPUT class="rbs-input-text-form required" TYPE="text" NAME="rbs_fed_tax_id" VALUE="<?php echo $pull_fed_tax_id; ?>">

			<div class="field_title">State Tax ID</div>
			<INPUT class="rbs-input-text-form required" TYPE="text" NAME="rbs_state_tax_id" VALUE="<?php echo $pull_state_tax_id; ?>">
			
			<div class="field_title">Medicare Part B ID / PTAN Number</div>
			<INPUT class="rbs-input-text-form" TYPE="text" NAME="rbs_medicareb" VALUE="<?php echo $pull_medicareb; ?>">

			<div class="field_title">Medicaid Number</div> <!-- 01 -->
			<INPUT class="rbs-input-text-form required" TYPE="text" NAME="rbs_medicaid1" VALUE="<?php echo $pull_medicaid1; ?>">
			
			<div class="field_title">Medicaid State</div> <!-- 01 -->
			<select name="rbs_medicaid_state1" class="rbs-dropdown-form required">
			<?php if ($pull_medicaid_state1 == "") {
				echo "<option value=\"\" selected></option>";
			} else {
				echo "<option value=\"$pull_medicaid_state1\" selected>$pull_medicaid_state1</option>";
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

			<div class="field_title">Software Vendor</div>
			<select name="rbs_swvendor" id="swvendor" class="rbs-input-text-form swvendor required">
			<?php 
			if ($pull_swvendor == "") {
				echo "<option value=\"\" selected></option>";
			} else {
				echo "<option value=\"$pull_swvendor\" selected>$pull_swvendor</option>";
			} 
			
			$sql = "
			SELECT Vals FROM officedb.opts 
			WHERE OPTS_ID = 1100 #Software Vendors 
			ORDER BY Vals ASC
			";
			if ($pull = $mysqli->query("$sql")) {
				while ($row = $pull->fetch_assoc()) {
					$SW_Vendors_String = $row['Vals'];
				}
				$SW_Vendors_Array = explode(",", $SW_Vendors_String);
				asort($SW_Vendors_Array);
				foreach ($SW_Vendors_Array as $vendor) {
					echo "<option value=\"$vendor\">$vendor</option>";
				}
			}
			echo "<option value=\"Other\">Other</option>";
			?>
			</select>
			
			<!--
			<div class="field_title">Switch Company</div>
			<INPUT class="rbs-input-text-form" TYPE="text" NAME="rbs_switch" VALUE="<?php echo $pull_switch; ?>">
			-->
			
			<div class="field_title">Switch Company</div>
			<select name="rbs_switch" class="rbs-input-text-form required">
			<?php 
			if ($pull_switch == "") {
				echo "<option value=\"\" selected></option>";
			} else {
				echo "<option value=\"$pull_switch\" selected>$pull_switch</option>";
			} 
			
			$sql = "
			SELECT Vals FROM officedb.opts 
			WHERE OPTS_ID = 1110 #Switch Vendors
			";
			if ($pull = $mysqli->query("$sql")) {
				while ($row = $pull->fetch_assoc()) {
					$Switch_Vendors_String = $row['Vals'];
				}
				$Switch_Vendors_Array = explode(",", $Switch_Vendors_String);
				asort($Switch_Vendors_Array);
				foreach ($Switch_Vendors_Array as $vendor) {
					if (preg_match("/N\/A/", $vendor)) { continue; }
					echo "<option value=\"$vendor\">$vendor</option>";
				}
			}
			echo "<option value=\"Other\">Other</option>";
			?>
			</select>

			<div class="field_title">Primary Wholesaler</div>
			<INPUT class="rbs-input-text-form required" TYPE="text" NAME="rbs_pri_wholesaler" VALUE="<?php echo $pull_pri_wholesaler; ?>">
			
			<div class="field_title">Wholesaler Acct. Number</div>
			<INPUT class="rbs-input-text-form required" TYPE="text" NAME="rbs_wholesaler_acct_number" VALUE="<?php echo $pull_wholesaler_acct_number; ?>">			
			
		</div> <!-- rbs-two-column -->

		<div class="rbs-two-column">
			
			<div class="field_title">DEA Number</div>
			<INPUT class="rbs-input-text-form required" TYPE="text" NAME="rbs_dea" VALUE="<?php echo $pull_dea; ?>">
			
			<div class="field_title">DEA Expiration</div>
			<INPUT class="rbs-input-text-form datepicker required" TYPE="text" NAME="rbs_dea_exp" VALUE="<?php echo $pull_dea_exp; ?>">

			<div class="field_title">Pharmacy State Permit Number</div>
			<INPUT class="rbs-input-text-form required" TYPE="text" NAME="rbs_state_license_number" VALUE="<?php echo $pull_state_license_number; ?>">
			
			<div class="field_title">Pharmacy State Permit Expiration</div>
			<INPUT class="rbs-input-text-form datepicker required" TYPE="text" NAME="rbs_state_license_exp" VALUE="<?php echo $pull_state_license_exp; ?>">
			
			<div class="field_title">State Controlled Substance License Number (BNDD, DPS, etc.) <span class="small_example">(if applicable)</span></div>
			<INPUT class="rbs-input-text-form" TYPE="text" NAME="rbs_state_controlled_substance_license_number" VALUE="<?php echo $pull_state_controlled_substance_license_number; ?>">
			
			<div class="field_title">State Controlled Substance License Exp.</div>
			<div class="small_example">(if applicable)</div>
			<INPUT class="rbs-input-text-form datepicker" TYPE="text" NAME="rbs_state_controlled_substance_license_exp" VALUE="<?php echo $pull_state_controlled_substance_license_exp; ?>">
			
			<div class="field_title">Business Liability Insurance Policy Number</div>
			<INPUT class="rbs-input-text-form required" TYPE="text" NAME="rbs_business_liability_insurance_policy_number" VALUE="<?php echo $pull_business_liability_insurance_policy_number; ?>">
			
			<div class="field_title">Business Liability Insurance Policy Expiration</div>
			<INPUT class="rbs-input-text-form datepicker required" TYPE="text" NAME="rbs_business_liability_insurance_policy_exp" VALUE="<?php echo $pull_business_liability_insurance_policy_exp; ?>">
			
		</div> <!-- rbs-two-column -->

	</div> <!-- end rbs-two-column-wrapper -->
	
	<div style="clear: both;"></div>
	<div id="errors"></div>

	<div class="rbs-two-column-wrapper">
		<?php 
		if ($pull_status = "pending") {
			echo "<INPUT class='button-form-enroll' TYPE='button' VALUE='Back' onClick='window.history.back();'>";
		}
                ?>
		<INPUT ID="submit" class="button-form-enroll" TYPE="submit" VALUE="<?php if ($pull_status != "pending") {echo "Update and Review";} else {echo "Next Page";} ?>">
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

</body>
</html>

<?php $mysqli->close(); ?>
