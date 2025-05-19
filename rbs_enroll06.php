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
if ($rbs_contact_comp_name != "") {
	if ($stmt = $mysqli->prepare("
		UPDATE pharmassess.enrollment SET  
		rbs_contact_comp_name  = ?, 
		rbs_contact_comp_title = ?, 
		rbs_contact_comp_email = ?, 
		rbs_contact_comp_phone = ?, 
		
		rbs_page=? 
		
		WHERE id=? 
		;")) {
		$stmt->bind_param('sssssi', 
		$rbs_contact_comp_name, $rbs_contact_comp_title, $rbs_contact_comp_email, $rbs_contact_comp_phone,
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
			header('Location: rbs_enroll_review.php#enroll06');
		} else {
			header('Location: rbs_enroll07.php');
		}
		#exit();
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

function validateForm() {


	
}
</script>

<div id="wrapper"><!-- wrapper -->

	<div id="content_container_front">
	<div id="mainbody_front">

	<h1>Credentialing Contact</h1>
	<form name="enroll" action="<?php echo $_SERVER['PHP_SELF']; ?>" onsubmit="return checkRequiredFields(this)" method="post">

	<div class="rbs-two-column-wrapper">
	
		<div class="contact">
		
			<p>This employee will work with our office in managing the pharmacy account as it relates to pharmacy / staff credentialing.</p>

			<div class="rbs-two-column">
			
				<div class="field_title">Name (First, MI, Last)</div>
				<INPUT class="rbs-input-text-form required" TYPE="text" NAME="rbs_contact_comp_name" VALUE="<?php echo $pull_contact_comp_name; ?>">
				
				<div class="field_title">Title</div>
				<INPUT class="rbs-input-text-form required" TYPE="text" NAME="rbs_contact_comp_title" VALUE="<?php echo $pull_contact_comp_title; ?>">
			
			</div> <!-- end rbs-two-column -->

			<div class="rbs-two-column">
			
				<div class="field_title">Phone</div>
				<INPUT class="rbs-input-text-form phone required" TYPE="text" NAME="rbs_contact_comp_phone" VALUE="<?php echo $pull_contact_comp_phone; ?>">
				
				<div class="field_title">Email</div>
				<INPUT class="rbs-input-text-form required" TYPE="text" NAME="rbs_contact_comp_email" VALUE="<?php echo $pull_contact_comp_email; ?>">
				
			</div> <!-- end rbs-two-column -->
			
			
			<hr style="clear: both;" />
		
		</div> <!-- end contact -->
		

	</div> <!-- end rbs-two-column-wrapper -->

	<div style="clear: both;"></div>
	<div id="errors"></div>
	
	<div class="rbs-two-column-wrapper">
		<?php 
		if ($pull_status = "pending") {
			echo "<INPUT class='button-form-enroll' TYPE='button' VALUE='Back' onClick='window.history.back();'>";
		}
                ?>
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

</body>
</html>

<?php $mysqli->close(); ?>
