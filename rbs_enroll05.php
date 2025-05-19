<?php

include 'includes/mysql.php';

$rbs_page = basename($_SERVER['PHP_SELF']);
$curdate = date("Y-m-d");
$errorcheck = 0;
$row_cnt = 0;

if (isset($_COOKIE["cont1"]) && isset($_COOKIE["cont2"]) && isset($_COOKIE["cont3"])) {
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
	$returning_rec_id  = "";
	
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
if ($rbs_owner1_name != "") {
	if ($stmt = $mysqli->prepare("
		UPDATE pharmassess.enrollment SET  
		rbs_owner1_name  = ?, 
		rbs_owner1_title = ?, 
		rbs_owner1_email = ?, 
		rbs_owner1_phone = ?, 
		rbs_owner1_cell  = ?, 
		rbs_owner1_pct   = ?, 

		rbs_owner2_name  = ?, 
		rbs_owner2_title = ?, 
		rbs_owner2_email = ?, 
		rbs_owner2_phone = ?, 
		rbs_owner2_cell  = ?, 
		rbs_owner2_pct   = ?, 

		rbs_owner3_name  = ?, 
		rbs_owner3_title = ?, 
		rbs_owner3_email = ?, 
		rbs_owner3_phone = ?, 
		rbs_owner3_cell  = ?, 
		rbs_owner3_pct   = ?, 

		rbs_owner4_name  = ?, 
		rbs_owner4_title = ?, 
		rbs_owner4_email = ?, 
		rbs_owner4_phone = ?, 
		rbs_owner4_cell  = ?, 
		rbs_owner4_pct   = ?, 
		rbs_page=? 
		
		WHERE id =? 
		;")) {
		$stmt->bind_param('sssssisssssisssssisssssisi', 
		$rbs_owner1_name, $rbs_owner1_title, $rbs_owner1_email, $rbs_owner1_phone, $rbs_owner1_cell, $rbs_owner1_pct,
		$rbs_owner2_name, $rbs_owner2_title, $rbs_owner2_email, $rbs_owner2_phone, $rbs_owner2_cell, $rbs_owner2_pct,
		$rbs_owner3_name, $rbs_owner3_title, $rbs_owner3_email, $rbs_owner3_phone, $rbs_owner3_cell, $rbs_owner3_pct,
		$rbs_owner4_name, $rbs_owner4_title, $rbs_owner4_email, $rbs_owner4_phone, $rbs_owner4_cell, $rbs_owner4_pct,
		$rbs_page, $returning_rec_id);
		$stmt->execute();
		$stmt->close();
	} else {
		printf("Prepared Statement Error: %s\n", $mysqli->error);
		$errorcheck = 1;
	}
	
	if ($errorcheck != 1) {
		if ($pull_status != "pending") {
			header('Location: rbs_enroll_review.php#enroll05');
		} else {
			header('Location: rbs_enroll06.php');
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
		$sqlx = "SELECT $field FROM pharmassess.enrollment WHERE rbs_ncpdp = ? && rbs_npi = ?";
		if ($value_pull = $mysqli->prepare("$sqlx")) {
			$value_pull->bind_param('ii', $returning_ncpdp, $returning_npi);
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

if ( preg_match('/^\s*$/', $pull_owner1_pct) ) {
	$pull_owner1_pct = 0;
}
if ( preg_match('/^\s*$/', $pull_owner2_pct) ) {
	$pull_owner2_pct = 0;
}
if ( preg_match('/^\s*$/', $pull_owner3_pct) ) {
	$pull_owner3_pct = 0;
}
if ( preg_match('/^\s*$/', $pull_owner4_pct) ) {
	$pull_owner4_pct = 0;
}

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
var pct1 = 0;
var pct2 = 0;
var pct3 = 0;
var pct4 = 0;

$(function() {
	$(".datepicker").mask("99/99/9999");
	$(".datepicker").datepicker();
	$("#anim").change(function() {
		$(".datepicker").datepicker( "option", "showAnim", $( this ).val() );
	});
	$('.phone').mask('(999) 999-9999');
	
	$( ".add_owner" ).click(function() {
		$(this).next().show();
		$(this).hide();
		$(this).closest('div').nextAll('.add_owner').first().show();
	});
	
	pct1 = <?php echo $pull_owner1_pct; ?>;
	$( "#slider1" ).slider({
		value:<?php echo $pull_owner1_pct; ?>,
		min: 0,
		max: 100,
		step: 5,
		slide: function( event, ui ) {
			$( "#amount1" ).val( ui.value + '% of ownership' )+ '% of ownership';
			pct1 = ui.value;
		}
	});
	$( "#amount1" ).val( $( "#slider1" ).slider( "value" ) + '% of ownership' );
	
	pct2 = <?php echo $pull_owner2_pct; ?>;
	$( "#slider2" ).slider({
		value:<?php echo $pull_owner2_pct; ?>,
		min: 0,
		max: 100,
		step: 5,
		slide: function( event, ui ) {
			$( "#amount2" ).val( ui.value + '% of ownership' );
			pct2 = ui.value;
		}
	});
	$( "#amount2" ).val( $( "#slider2" ).slider( "value" ) + '% of ownership' );
	
	pct3 = <?php echo $pull_owner3_pct; ?>;
	$( "#slider3" ).slider({
		value:<?php echo $pull_owner3_pct; ?>,
		min: 0,
		max: 100,
		step: 5,
		slide: function( event, ui ) {
			$( "#amount3" ).val( ui.value + '% of ownership' );
			pct3 = ui.value;
		}
	});
	$( "#amount3" ).val( $( "#slider3" ).slider( "value" ) + '% of ownership' );
	
	pct4 = <?php echo $pull_owner4_pct; ?>;
	$( "#slider4" ).slider({
		value:<?php echo $pull_owner4_pct; ?>,
		min: 0,
		max: 100,
		step: 5,
		slide: function( event, ui ) {
			$( "#amount4" ).val( ui.value + '% of ownership' );
			pct4 = ui.value;
		}
	});
	$( "#amount4" ).val( $( "#slider4" ).slider( "value" ) + '% of ownership' );
	
});

function validatePct() {
	
	var errors = '';
	var error_found = 0;
	
	var PctSum = pct1 + pct2 + pct3 + pct4;

	if ( PctSum != 100 ) {
		//alert('PctSum: ' + PctSum);
		//return false;
		error_found++;
	}
	
	if (error_found > 0) {
		errors = 'Percentage(s) of ownership must total to 100% (currently ' + PctSum + '%)\n';
		var displayErrorsID = document.getElementById("errors");
		if (displayErrorsID === null) {
			alert(errors);
		} else {
			errors = errors.replace(new RegExp('\r?\n','g'), '<br />');
			displayErrorsID.innerHTML = errors;
		}
		return false;
	} else {
		return true;
	}
	
}
</script>

<div id="wrapper"><!-- wrapper -->

	<div id="content_container_front">
	<div id="mainbody_front">

	<h1>Pharmacy Ownership</h1>
	<form name="enroll" action="<?php echo $_SERVER['PHP_SELF']; ?>" onsubmit="return validatePct() && checkRequiredFields(this);" method="post">

	<div class="rbs-two-column-wrapper clear">
		<p>List all Pharmacy Owner(s). Percentage of ownership must equal 100%.</p> 
	</div> <!-- end rbs-two-column-wrapper -->

	<div class="rbs-two-column-wrapper owners">
	
	
	<?php

	$ownerNum = 1;

	if ($pull = $mysqli->prepare("
	SELECT fname, lname, license, type, exp_date, discipline 
	FROM pharmassess.employees WHERE ncpdp = ? && npi = ? && type LIKE '%owner%'
	ORDER BY lname, fname")) {
		$pull->bind_param('ii', $returning_ncpdp, $returning_npi);
		$pull->execute();
		$employees = $pull->get_result();
		while ($row = $employees->fetch_assoc()):
			
			if ($ownerNum > 4) {
				continue;
			}
			
			$fname = $row['fname'];
			$lname = $row['lname'];
			
			if (empty(${"pull_owner".$ownerNum."_name"})) {
				${"pull_owner".$ownerNum."_name"} = "$fname $lname";
			}
			
			#exit PHP block to HTML
			?>
			
			<div class="owner">

				<div class="rbs-two-column">
				
					<div class="field_title">Owner Name</div>
					<INPUT class="rbs-input-text-form required" TYPE="text" NAME="<?php echo "rbs_owner${ownerNum}_name"; ?>" VALUE="<?php echo ${"pull_owner".$ownerNum."_name"}; ?>">
					
					<!--
					<div class="field_title">Owner Title</div>
					<INPUT class="rbs-input-text-form required" TYPE="text" NAME="<?php echo "rbs_owner${ownerNum}_title"; ?>" VALUE="<?php echo ${"pull_owner".$ownerNum."_title"}; ?>">
					-->
					
					<div class="field_title">Owner Email</div>
					<INPUT class="rbs-input-text-form required" TYPE="text" NAME="<?php echo "rbs_owner${ownerNum}_email"; ?>" VALUE="<?php echo ${"pull_owner".$ownerNum."_email"}; ?>">
				
				</div> <!-- end rbs-two-column -->

				<div class="rbs-two-column">
				
					<div class="field_title">Owner Phone</div>
					<INPUT class="rbs-input-text-form phone required" TYPE="text" NAME="<?php echo "rbs_owner${ownerNum}_phone"; ?>" VALUE="<?php echo ${"pull_owner".$ownerNum."_phone"}; ?>">
					
					<div class="field_title">Owner Cell</div>
					<INPUT class="rbs-input-text-form phone required" TYPE="text" NAME="<?php echo "rbs_owner${ownerNum}_cell"; ?>" VALUE="<?php echo ${"pull_owner".$ownerNum."_cell"}; ?>">
									
					<input class="required" type="text" name="<?php echo "rbs_owner${ownerNum}_pct"; ?>" id="<?php echo "amount${ownerNum}"; ?>" readonly style="border:0; color:#f6931f; font-weight:bold;">
					<div id="<?php echo "slider${ownerNum}"; ?>" style="width: 250px;"></div>
					
					<br />
					
				</div> <!-- end rbs-two-column -->
				
				
				<hr style="clear: both;" />
			
			</div> <!-- end owner -->
			
			<?php
			#resume PHP block

			$ownerNum++;
		endwhile;
		$pull->close();
	} else {
		printf("Prepared Statement Error: %s\n", $mysqli->error);
	}

	?>		

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
