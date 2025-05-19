<?php
include 'D:/WWW/vars.php';

##include '../includes/mysql.php';

if (isset($_COOKIE["direct_id"]) && isset($_COOKIE["direct_detail_id"])) {
	$direct_id  = $_COOKIE["direct_id"];
	$direct_detail_id  = $_COOKIE["direct_detail_id"];
} else {
	header('Location: continue_enrollment.php');
	exit();
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

###IMPORT DATA ####################################################
if ( $import_enrollment == 'Y' || $import_archq == 'Y' ) {

	if ($import_archq == 'Y') {
	}

	if ($import_enrollment == 'Y') {
		if ($stmt = $mysqli->prepare("
			SELECT *
			  FROM pharmassess.direct_enrollment_detail a
			  JOIN pharmassess.enrollment b ON (a.enrollment_id = b.id)
                         WHERE a.id = $direct_detail_id
			;")) {

				$stmt->execute();
				$all_data = $stmt->get_result();
				while ($rec = $all_data->fetch_assoc()) {
					$import['2'] = $rec['rbs_ncpdp'];
					$import['3'] = $rec['rbs_npi'];
					$import['4'] = $rec['rbs_legalname'];
					$import['5'] = $rec['rbs_pharmname'];
					$import['6'] = $rec['rbs_main_address1'];
					$import['7'] = $rec['rbs_main_address2'];
					$import['8'] = $rec['rbs_main_city'];
					$import['9'] = $rec['rbs_main_county_parish'];
					$import['10'] = $rec['rbs_main_state'];
					$import['11'] = $rec['rbs_main_zip'];
					$import['12'] = $rec['rbs_phone'];
					$import['13'] = $rec['rbs_fax'];
					$import['14'] = $rec['rbs_main_contact_name'];
					$import['15'] = $rec['rbs_main_contact_title'];
					$import['16'] = $rec['rbs_main_contact_email'];
					$import['17'] = $rec['rbs_main_address1'];
					$import['18'] = $rec['rbs_main_address2'];
					$import['19'] = $rec['rbs_main_city'];
					$import['20'] = $rec['rbs_main_county_parish'];
					$import['21'] = $rec['rbs_main_state'];
					$import['22'] = $rec['rbs_main_zip'];

					$import['24'] = $rec['rbs_contact_comp_title'];
					$import['25'] = $rec['rbs_contact_comp_name'];
					$import['26'] = '';
					$import['27'] = $rec['rbs_contact_comp_phone'];
					$import['28'] = '';
					$import['29'] = $rec['rbs_contact_comp_email'];

					$import['30'] = $rec['rbs_contact_cred_title'];
					$import['31'] = $rec['rbs_contact_cred_name'];
					$import['32'] = '';
					$import['33'] = $rec['rbs_contact_cred_phone'];
					$import['34'] = '';
					$import['35'] = $rec['rbs_contact_cred_email'];

					$import['56'] = $rec['rbs_owner1_name'];
					$import['59'] = $rec['rbs_owner1_pct'];

					$import['66'] = $rec['rbs_fed_tax_id'];
					$import['67'] = $rec['rbs_medicaid1'];
					$import['68'] = $rec['rbs_medicaid_state1'];
					$import['69'] = '';
					$import['70'] = $rec['rbs_business_liability_insurance_policy_number'];
					$import['71'] = '';
					$import['72'] = $rec['rbs_business_liability_insurance_policy_exp'];
					$import['73'] = '';
					$import['74'] = '';
					$import['75'] = $rec['rbs_state_license_number'];
					$import['76'] = '';
					$import['77'] = $rec['rbs_state_license_exp'];
					$import['78'] = $rec['rbs_dea'];
					$import['79'] = '';
					$import['80'] = $rec['rbs_dea_exp'];
					$import['81'] = '';
					$import['82'] = '';

					$import['154'] = $rec['rbs_hours_monday'];
					$import['155'] = $rec['rbs_hours_tuesday'];
					$import['156'] = $rec['rbs_hours_wednesday'];
					$import['157'] = $rec['rbs_hours_thursday'];
					$import['158'] = $rec['rbs_hours_friday'];
					$import['159'] = $rec['rbs_hours_saturday'];
					$import['160'] = $rec['rbs_hours_sunday'];
					$import['162'] = $rec['rbs_24hour_service'];

					$import['219'] = $rec['rbs_services_340b'];

					$import['224'] = $rec['rbs_vaccinations'];
				}
			}
		else {
			printf("Prepared Statement Error: %s\n", $mysqli->error);
			$errorcheck = 1;
		}
	}

	$upd_vals = '';
	foreach ( $import as $key =>$value ) {
		$upd_vals .= "($direct_detail_id, $key, '$value'),";
	}
	$upd_vals = rtrim($upd_vals, ',');


	if ($stmt = $mysqli->prepare("
		REPLACE INTO pharmassess.direct_cred (enrollment_detail_id, qa_id, value)
              	VALUES $upd_vals
		;")) {
		$stmt->execute();
		$stmt->close();
	}
	else {
		printf("Prepared Statement Error: %s\n", $mysqli->error);
		$errorcheck = 1;
	}

	
	if ($errorcheck != 1) {
		header('Location: direct_cred.php?category=Basic');
		exit();
	}
	
}
###################################################################

if (empty($pull_type)) {
	if (isset($_COOKIE['type'])) { $pull_type = $_COOKIE['type']; } else { $pull_type = ''; }
}
?>

<!doctype html> 
<html lang="en">
<head>
<?php include '../includes/include_meta.php'; ?>
<title>Pharm Assess, Inc. </title>
<?php include '../includes/include_styles.php'; ?>
<link type="text/css" rel="stylesheet" media="screen" href="/css/rbs_enroll.css" />
<?php include '../includes/include_analytics.php'; ?>
</head>
<body>

<!--Header and Navigation-------------------------------------------->
<?php include '../includes/direct_header_nav.php'; ?>
<!------------------------------------------------------------------->
<div id="wrapper"><!-- wrapper -->

<?php #echo "VALS: $upd_vals<br>"; ?>

	<h1>Begin Your Credentialing</h1>
	<form name="continue" action="<?php echo $_SERVER['PHP_SELF']; ?>" onsubmit="return validateForm()" method="post">
	<h2>Data Import</h2>
	<div class="rbs-two-column-wrapper">

		<div class="rbs-two-column">
			<div class="field_title_long"><u>Type</u></div><br>

			<INPUT TYPE="checkbox" NAME="import_enrollment" VALUE="Y" CHECKED>
			<div class="field_title_long">Enrollment Data</div><br><br>
			
			<INPUT TYPE="checkbox" NAME="import_archq" VALUE="Y" CHECKED>
			<div class="field_title_long">ArchQ Data</div>
			
			<br />
			<br />
			<INPUT class="button-form-direct" TYPE="submit" VALUE="Continue">
		</div> <!-- rbs-two-column -->

		<div class="rbs-two-column">
			<div class="field_title_long"><u>Instructions</u></div><br>
			<p>Please make sure your information on NCPDP is up-to-date.  If you would not like to import this data, please uncheck the appropriate boxes to the left.</p>
		</div> <!-- rbs-two-column -->

	</div> <!-- end rbs-two-column-wrapper -->
	
	</form>


</div><!-- end wrapper -->
<!-- Footer ----------------------------------------------------->
<?php include '../includes/footer.php'; ?>
<!--------------------------------------------------------------->

</body>
</html>
