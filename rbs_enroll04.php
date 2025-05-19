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

###DELETE VALUES FROM DB (Employees)###############################
if ($delete == "yes") {
	if ($dstmt = $mysqli->prepare("
		DELETE FROM pharmassess.employees WHERE 
		ncpdp=? && 
		npi=? && 
		fname=? && 
		lname=? && 
		license=? 
		;")) {
		$dstmt->bind_param('iisss', $returning_ncpdp, $returning_npi, $dfname, $dlname, $dlicense);
		$dstmt->execute();
		$dstmt->close();
	}
	else {
		printf("Prepared Statement Error: %s\n", $mysqli->error);
		$errorcheck = 1;
	}
}
###################################################################

###SET VALUES TO DB (Employees)####################################
if ($all_post != "") {
	if ($stmt = $mysqli->prepare("
		REPLACE INTO pharmassess.employees SET 
		ncpdp=?, 
		npi=?, 
		fname=?, 
		lname=?, 
		license=?, 
		type=?, 
		exp_date=?, 
		discipline=?
		;")) {
		$stmt->bind_param('iissssss', $returning_ncpdp, $returning_npi, $fname, $lname, $license, $type, $exp_date, $discipline);
		$stmt->execute();
		$stmt->close();
	}
	else {
		printf("Prepared Statement Error: %s\n", $mysqli->error);
		$errorcheck = 1;
	}
	
}
###################################################################

###SET VALUES FROM DB#############################################
###################################################################

###READ VALUES FROM DB#############################################
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
	
	$( ".license_info" ).hide();

	$("#license_yes_no").change(function(){
		if ( $(this).val() == "yes" ) {
			$("#license").val('');
			$("#exp_date").val('');
			$( ".license_info" ).show();
		} else {
			$( ".license_info" ).hide();
			$("#license").val('N/A');
			$("#exp_date").val('N/A');
		}
	}); 
	
});
</script>

<div id="wrapper"><!-- wrapper -->

	<div id="content_container_front">
	<div id="mainbody_front">

	
	<form name="enroll" action="<?php echo $rbs_page; ?>" onsubmit="return checkRequiredFields(this)" method="post">


	<h1>Pharmacy Employee Information</h1>

	<div class="rbs-two-column-wrapper clear">
		<p>List all employees with access to PHI or who are involved in any stage of the prescription fulfilment process (i.e. Pharmacist, Technician, Cashier/Clerk, Delivery, etc.). You will need to enter ALL Owner(s) and a Pharmacist-in-Charge before continuing to the next page.</p>
	</div> <!-- end rbs-two-column-wrapper -->

	<div class="rbs-two-column-wrapper owners">
	
		<div class="owner">

			<div class="rbs-two-column">
			
				<div class="field_title">First Name</div>
				<INPUT class="rbs-input-text-form required" TYPE="text" NAME="fname" placeholder="John" VALUE="">
				
				<div class="field_title">Last Name</div>
				<INPUT class="rbs-input-text-form required" TYPE="text" NAME="lname" placeholder="Smith" VALUE="">
				
				<div class="field_title">Does this employee have a License?</div>
				<select name="license_yes_no" id="license_yes_no" class="rbs-dropdown-form required">
				<option value=""></option>
				<option value="no">No</option>
				<option value="yes">Yes</option>
				</select>
				
				<div class="field_title license_info">License Number</div>
				<INPUT class="rbs-input-text-form license_info" TYPE="text" NAME="license" id="license" VALUE="N/A" placeholder="PST.000000">
				
				<div class="field_title license_info">License Expiration</div>
				<INPUT class="rbs-input-text-form datepicker license_info" TYPE="text" NAME="exp_date" id="exp_date" VALUE="N/A" placeholder="mm/dd/yyyy">
			
			</div> <!-- end rbs-two-column -->

			<div class="rbs-two-column">
			
				<div class="field_title">Employee Type</div>
				<select name="type" class="rbs-dropdown-form required">
				<?php 
				echo "<option value=\"\" selected></option>\n";
				
				$sql = "
				SELECT Vals FROM officedb.opts 
				WHERE OPTS_ID = 3000 #Job Titles
				ORDER BY Vals ASC
				";
				if ($pull = $mysqli->query("$sql")) {
					while ($row = $pull->fetch_assoc()) {
						$SW_Vendors_String = $row['Vals'];
					}
					$SW_Vendors_Array = preg_split("/, |,/", $SW_Vendors_String);
					asort($SW_Vendors_Array);
					foreach ($SW_Vendors_Array as $vendor) {
						if (preg_match('/N\/A|other/i', $vendor)) { continue; }
						echo "<option value=\"$vendor\">$vendor</option>\n";
					}
				}
				?>
				</select>
				
				<div class="field_title">Has this employee received disciplinary action from the State Board of Pharmacy?</div>
				<select name="discipline" class="rbs-dropdown-form required">
				<option value=""></option>
				<option value="no">No</option>
				<option value="yes">Yes</option>
				</select>
				
				<br /><INPUT class="button-form" TYPE="submit" VALUE="Add Staff Member">
				
				<p>When all staff members have been entered, click
				<?php 
				if ($pull_status != "pending") {
					echo " \"Update and Review\" ";
				} else {
					echo " \"Next Page\" ";
				}
				?>
				</p>
				
			</div> <!-- end rbs-two-column -->
			
			
			<hr style="clear: both;" />
		
		</div> <!-- end owner -->

	</div> <!-- end rbs-two-column-wrapper -->
	
	</form>
	
	
	<div class="rbs-two-column-wrapper clear">

	<?php

	$numrows = 0;
	$owner = 0;
	$pic = 0;

	if ($pull = $mysqli->prepare("
	SELECT fname, lname, license, type, exp_date, discipline 
	FROM pharmassess.employees WHERE ncpdp = ? && npi = ? 
	ORDER BY lname, fname")) {
		echo "<p>Staff Members Entered:</p>";
		echo "<table style=\"width: 100%;\">\n";
		echo "<tr><th>Name</th><th>License</th><th>Type</th><th>Exp. Date</th><th>Disciplinary</th><th>&nbsp;</th></tr>\n";
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
			echo "<tr>";
			echo "<td>$fname $lname</td><td>$license</td><td>$type</td><td>$exp_date</td><td>$discipline</td>";
			echo "
			<td><form action=\"$rbs_page\" method=\"post\">
			<INPUT class=\"button-form-small\" TYPE=\"submit\" VALUE=\"delete\">
			<input type=\"hidden\" name=\"delete\" value=\"yes\">
			<input type=\"hidden\" name=\"dfname\" value=\"$fname\">
			<input type=\"hidden\" name=\"dlname\" value=\"$lname\">
			<input type=\"hidden\" name=\"dlicense\" value=\"$license\">
			</form></td>
			";
			echo "</tr>\n";
			$numrows = $numrows + 1;
			if ($row['type'] == "Owner") { $owner = 1; }
			if ($row['type'] == "PIC") { $pic = 1; }
		}
		echo "</table>";
		$pull->close();
	} else {
		printf("Prepared Statement Error: %s\n", $mysqli->error);
	}

	?>

	</div> <!-- end rbs-two-column-wrapper -->

	<br class="clear" /><br />
	<hr />

	<div class="rbs-two-column-wrapper">
	<?php 

	if ($pull_status != "pending") {
		echo "<form action=\"rbs_enroll_review.php#enroll04\" onsubmit=\"return validateEmployees()\" method=\"post\">";
		echo "<INPUT class=\"button-form-enroll\" TYPE=\"submit\" VALUE=\"Update and Review\">";
	} else {
		echo "<form action=\"rbs_enroll05.php\" onsubmit=\"return validateEmployees()\" method=\"post\">";
		if ($numrows > 0) {
			if ($pull_status = "pending") {
				echo "<INPUT class='button-form-enroll' TYPE='button' VALUE='Back' onClick='window.history.back();'>";
			}

			echo "<INPUT class=\"button-form-enroll\" TYPE=\"submit\" VALUE=\"Next Page\">";
		}
	}
	 
	if ($pic == 0 || $owner == 0) {
		echo "<script>function validateEmployees() {";

                if ($pic == 0) {
			echo "alert(\"A Pharmacist-in-Charge must be entered.\");";
                }
		else {
			echo "alert(\"At least one Owner must be entered.\");";
		}

		echo "return false; } </script>";
	}
	
	?>
	</div> <!-- end rbs-two-column-wrapper -->
	

	<div style="clear: both;"></div>
	<div id="errors"></div>

	</div><!-- end mainbody_front -->

	<!-- Sidebar -------------------------------------------------------->
	<?php include 'includes/sidebar_enrollment.php'; ?>
	<!------------------------------------------------------------------->
	
	</div><!-- end content_container_front -->

</div><!-- end wrapper -->
<!-- Footer ----------------------------------------------------->
<?php include 'includes/footer.php'; ?>
<!--------------------------------------------------------------->

</body>
</html>

<?php $mysqli->close(); ?>
