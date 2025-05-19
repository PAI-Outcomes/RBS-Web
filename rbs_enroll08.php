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
if ($rbs_services_compounding != "" && $rbs_services_ivr != "") {
                $sql = " 
		  UPDATE pharmassess.enrollment SET  
		         rbs_services_compounding    = '$rbs_services_compounding', 
	     	         rbs_services_340b           = '$rbs_services_340b', 
		         rbs_services_delivery       = '$rbs_services_delivery', 
		         rbs_services_drive_thru     = '$rbs_services_drive_thru', 
		         rbs_services_eprescribing   = '$rbs_services_eprescribing', 
		         rbs_services_ltc            = '$rbs_services_ltc', 
		         rbs_services_mail_service   = '$rbs_services_mail_service', 
		         rbs_services_online_refills = '$rbs_services_online_refills', 
		         rbs_services_vaccinations   = '$rbs_services_vaccinations', 
		         rbs_services_rural          = '$rbs_services_rural', 
		         rbs_services_rural_distance = '$rbs_services_rural_distance',
		         rbs_services_specialty      = '$rbs_services_specialty', 
		         rbs_services_ivr            = '$rbs_services_ivr', 
		         rbs_services_ivr_vendor     = '$rbs_services_ivr_vendor', 
		         rbs_services_ivr_vendor     = '$rbs_services_ivr_vendor', 
		         rbs_services_closed_door    = '$rbs_services_closed_door', 
		         rbs_services_home_infusion  = '$rbs_services_home_infusion', 
		         rbs_page                    = '$rbs_page' 
	 	   WHERE id                          =  $returning_rec_id 
		";

  if ($pull = $mysqli->prepare("$sql")) {
    $pull->execute();
    header('Location: rbs_enroll09.php');
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
		$sqlx = "SELECT $field FROM pharmassess.enrollment WHERE id= ?";
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
	


	$('input:radio[name=rbs_services_ivr]').click(function() {
		if ($('#ivr').is(':checked') ) { 
			$('#ivr_more').show();
		} else {
			$('#ivr_more').hide();
			$('#ivr_vendor').val('');
		}
	});
	$('input:radio[name=rbs_services_ivr]:checked').click();

	$('input:radio[name=rbs_services_rural]').click(function() {
		if ($('#rural').is(':checked') ) { 
			$('#rural_more').show();
		} else {
			$('#rural_more').hide();
			$('#rural_distance').val('');
		}
	});
	$('input:radio[name=rbs_services_rural]:checked').click();
	
});
</script>

<div id="wrapper"><!-- wrapper -->

	<div id="content_container_front">
	<div id="mainbody_front">

	<h1>Pharmacy Services Information</h1>
	<form name="enroll" id="enroll" action="<?php echo $_SERVER['PHP_SELF']; ?>" onsubmit="return checkRequiredFields(this);" method="post">

	<div class="rbs-two-column-wrapper">
	
		<p>Does your pharmacy provide the following services?</p>
		
		<table style="min-width: 240px; width: 100%;">
			<tr>
				<td>Compounding Pharmacy</td>
				<td>
					<input type="radio" name="rbs_services_compounding" value="Yes" <?php if ($pull_services_compounding == 'Yes') { echo 'checked'; } ?> class="required"> Yes 
					<input type="radio" name="rbs_services_compounding" value="No" <?php if ($pull_services_compounding == 'No') { echo 'checked'; } ?>> No
				</td>
			</tr>
			<tr>
				<td>Contracted to Distribute Under 340B</td>
				<td>
					<input type="radio" name="rbs_services_340b" value="Yes" <?php if ($pull_services_340b == 'Yes') { echo 'checked'; } ?> class="required"> Yes 
					<input type="radio" name="rbs_services_340b" value="No" <?php if ($pull_services_340b == 'No') { echo 'checked'; } ?>> No
				</td>
			</tr>
			<tr>
				<td>Delivery</td>
				<td>
					<input type="radio" name="rbs_services_delivery" value="Yes" <?php if ($pull_services_delivery == 'Yes') { echo 'checked'; } ?> class="required"> Yes 
					<input type="radio" name="rbs_services_delivery" value="No" <?php if ($pull_services_delivery == 'No') { echo 'checked'; } ?>> No
				</td>
			</tr>
			<tr>
				<td>Drive Thru</td>
				<td>
					<input type="radio" name="rbs_services_drive_thru" value="Yes" <?php if ($pull_services_drive_thru == 'Yes') { echo 'checked'; } ?> class="required"> Yes 
					<input type="radio" name="rbs_services_drive_thru" value="No" <?php if ($pull_services_drive_thru == 'No') { echo 'checked'; } ?>> No
				</td>
			</tr>
			<tr>
				<td>E-Prescribing Capabilities</td>
				<td>
					<input type="radio" name="rbs_services_eprescribing" value="Yes" <?php if ($pull_services_eprescribing == 'Yes') { echo 'checked'; } ?> class="required"> Yes 
					<input type="radio" name="rbs_services_eprescribing" value="No" <?php if ($pull_services_eprescribing == 'No') { echo 'checked'; } ?>> No
				</td>
			</tr>
			<tr>
				<td>Long Term Care</td>
				<td>
					<input type="radio" name="rbs_services_ltc" value="Yes" <?php if ($pull_services_ltc == 'Yes') { echo 'checked'; } ?> class="required"> Yes 
					<input type="radio" name="rbs_services_ltc" value="No" <?php if ($pull_services_ltc == 'No') { echo 'checked'; } ?>> No
				</td>
			</tr>
			<tr>
				<td>Mail Service Pharmacy</td>
				<td>
					<input type="radio" name="rbs_services_mail_service" value="Yes" <?php if ($pull_services_mail_service == 'Yes') { echo 'checked'; } ?> class="required"> Yes 
					<input type="radio" name="rbs_services_mail_service" value="No" <?php if ($pull_services_mail_service == 'No') { echo 'checked'; } ?>> No
				</td>
			</tr>
			<tr>
				<td>Online Refills</td>
				<td>
					<input type="radio" name="rbs_services_online_refills" value="Yes" <?php if ($pull_services_online_refills == 'Yes') { echo 'checked'; } ?> class="required"> Yes 
					<input type="radio" name="rbs_services_online_refills" value="No" <?php if ($pull_services_online_refills == 'No') { echo 'checked'; } ?>> No
				</td>
			</tr>
			<tr>
				<td>Vaccinations</td>
				<td>
					<input type="radio" name="rbs_services_vaccinations" value="Yes" <?php if ($pull_services_vaccinations == 'Yes') { echo 'checked'; } ?> class="required"> Yes 
					<input type="radio" name="rbs_services_vaccinations" value="No" <?php if ($pull_services_vaccinations == 'No') { echo 'checked'; } ?>> No
				</td>
			</tr>
			<tr>
				<td>Specialty Pharmacy</td>
				<td>
					<input type="radio" name="rbs_services_specialty" value="Yes" <?php if ($pull_services_specialty == 'Yes') { echo 'checked'; } ?> class="required"> Yes 
					<input type="radio" name="rbs_services_specialty" value="No" <?php if ($pull_services_specialty == 'No') { echo 'checked'; } ?>> No
				</td>
			</tr>
			<tr>
				<td>IVR (Interactive Voice Response)</td>
				<td>
					<input type="radio" id="ivr" name="rbs_services_ivr" value="Yes" <?php if ($pull_services_ivr == 'Yes') { echo 'checked'; } ?> class="required"> Yes 
					<input type="radio" name="rbs_services_ivr" value="No" <?php if ($pull_services_ivr == 'No') { echo 'checked'; } ?>> No
				</td>
			</tr>
			<tr id="ivr_more" style="display: none;">
				<td colspan=2 class="tab20">
					Which IVR vendor do you use?<br />
					<select name="rbs_services_ivr_vendor" id="ivr_vendor" class="rbs-input-text-form">
					<?php 
					if ($pull_services_ivr_vendor == "") {
						echo "<option value=\"\" selected></option>\n";
					} else {
						echo "<option value=\"$pull_services_ivr_vendor\" selected>$pull_services_ivr_vendor</option>\n";
					} 
					
					$sql = "
					SELECT Vals FROM officedb.opts 
					WHERE OPTS_ID = 1190 #IVR Vendors
					ORDER BY Vals ASC
					";
					if ($pull = $mysqli->query("$sql")) {
						while ($row = $pull->fetch_assoc()) {
							$options_string = $row['Vals'];
						}
						$options_array = preg_split("/, |,/", $options_string);
						asort($options_array);
						foreach ($options_array as $option) {
							if (preg_match('/N\/A|other/i', $option)) { continue; }
							echo "<option value=\"$option\">$option</option>\n";
						}
					}
					echo "<option value=\"Other\">Other</option>\n";
					?>
					</select>
				</td>
			</tr>
			<tr>
				<td>Closed Door</td>
				<td>
					<input type="radio" id=closed_door" name="rbs_services_closed_door" value="Yes" <?php if ($pull_services_closed_door == 'Yes') { echo 'checked'; } ?> class="required"> Yes 
					<input type="radio" name="rbs_services_closed_door" value="No" <?php if ($pull_services_cloded_door == 'No') { echo 'checked'; } ?>> No
				</td>
			</tr>
			<tr>
				<td>Home Infusion</td>
				<td>
					<input type="radio" id="home_infusion" name="rbs_services_home_infusion" value="Yes" <?php if ($pull_services_home_infusion == 'Yes') { echo 'checked'; } ?> class="required"> Yes 
					<input type="radio" name="rbs_services_home_infusion" value="No" <?php if ($pull_services_home_infusion == 'No') { echo 'checked'; } ?>> No
				</td>
			</tr>
			<tr>
				<td>Is your pharmacy rural?</td>
				<td>
					<input type="radio" id="rural" name="rbs_services_rural" value="Yes" <?php if ($pull_services_rural == 'Yes') { echo 'checked'; } ?> class="required"> Yes 
					<input type="radio" name="rbs_services_rural" value="No" <?php if ($pull_services_rural == 'No') { echo 'checked'; } ?>> No
				</td>
			</tr>
			<tr id="rural_more" style="display: none;">
				<td colspan=2 class="tab20">
					Distance in miles to closest retail pharmacy:<br />
					<select name="rbs_services_rural_distance" id="rural_distance" class="rbs-input-text-form">
					<?php 
					if ($pull_services_rural_distance == "") {
						echo "<option value=\"\" selected></option>\n";
					} else {
						echo "<option value=\"$pull_services_rural_distance\" selected>$pull_services_rural_distance</option>\n";
					} 
					
					$sql = "
					SELECT Vals FROM officedb.opts 
					WHERE OPTS_ID = 1065 #Rural
					ORDER BY Vals ASC
					";
					if ($pull = $mysqli->query("$sql")) {
						while ($row = $pull->fetch_assoc()) {
							$options_string = $row['Vals'];
						}
						$options_string = str_replace('"', "", $options_string);
						$options_array = explode(",", $options_string);
						#asort($options_array);
						foreach ($options_array as $option) {
							echo "<option value=\"$option\">$option</option>\n";
						}
					}
					?>
					</select>
				</td>
			</tr>
		</table>

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
