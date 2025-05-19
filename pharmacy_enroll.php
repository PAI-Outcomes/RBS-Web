<?php

include '../includes/mysql.php';

$rbs_page = basename($_SERVER['PHP_SELF']);
$errorcheck = 0;
$row_cnt = 0;

setcookie("enroll_id", "0", time()+43200);

if (isset($_COOKIE["direct_id"])) {
	$direct_id = $_COOKIE["direct_id"];
} else {
	header('Location: continue_enrollment.php');
	exit();
}

###GATHER POST DATA################################################
$all_post = "";
foreach ($_POST as $param_name => $param_val) {
	if (isset($param_val) && $param_val != "") { 
		$$param_name = $param_val; 
		$all_post .= "$param_name: $param_val, ";
	} else { 
		$$param_name = ""; 
	}
}

foreach ($_GET as $param_name => $param_val) {
	if (isset($param_val) && $param_val != "") { 
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
		DELETE FROM pharmassess.direct_enrollment_detail
                WHERE id = ? 
		;")) {
		$dstmt->bind_param('i', $enroll_detail_id);
		$dstmt->execute();
		$dstmt->close();
	}
	else {
		printf("Prepared Statement Error: %s\n", $mysqli->error);
		$errorcheck = 1;
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
<title>Pharm Assess, Inc.</title>
<?php include '../includes/include_styles.php'; ?>
<link type="text/css" rel="stylesheet" media="screen" href="/css/rbs_enroll.css" />
<link rel="stylesheet" href="//code.jquery.com/ui/1.10.3/themes/smoothness/jquery-ui.css" />
<?php include '../includes/include_analytics.php'; ?>
</head>
<body>

<!--Header and Navigation-------------------------------------------->
<?php include '../includes/direct_header_nav.php'; ?>
<!------------------------------------------------------------------->

<script src="//code.jquery.com/ui/1.10.3/jquery-ui.js"></script>
<script src="../includes/jquery.maskedinput.min.js" type="text/javascript"></script>
<script src="../includes/checkRequiredFields.js"></script>
<script>
function continue_enrollment(id, page) {
        var d = new Date();
        d.setTime(d.getTime() + (7*24*60*60*1000));
        var expires = "expires="+ d.toUTCString();
	document.cookie = "enroll_id=" + id + ";" + expires + ";path=/";
	location.href = page;
}

function continue_credentialing(id, type) {
	var page = '';

	if ( type == 'new' ) {
		page = 'credentialing_setup.php';
		//page = 'direct_cred.php?category=Basic';
	}
	else {
		page = 'direct_cred.php?category=Basic';
	}		

        var d = new Date();
        d.setTime(d.getTime() + (7*24*60*60*1000));
        var expires = "expires="+ d.toUTCString();
	document.cookie = "direct_detail_id=" + id + ";" + expires + ";path=/";
	location.href = page;
}

function remove_pharmacy(cid, eid) {
	var page = '';

	if ( confirm("Are you sure you want to remove this pharmacy?") == true ) {
		page ='<?php echo "$rbs_page"; ?>?delete=yes&enroll_detail_id=' + cid + '&enroll_id=' + eid;
	  	location.href = page;
	}
}

</script>

<div id="wrapper"><!-- wrapper -->

	<div id="content_container_front">
	<div id="mainbody_front">

	<?php echo "DEL: $delete - $enroll_detail_id<br>$all_post<br>"; ?>
	
	</div> <!-- end rbs-two-column-wrapper -->

	<div class="rbs-two-column-wrapper clear">
	<h1>Pharmacy Information</h1>
		<p>Please add all pharmacies you would like to enroll into RBS Direct.</p>
	</div> <!-- end rbs-two-column-wrapper -->

	<div class="rbs-two-column-wrapper clear">

	<?php

	$numrows  = 0;
	$complete = 0;
	$anchor   = 0;

###READ VALUES FROM DB#############################################
echo "$sqlx<br>";
if ($value_pull = $mysqli->prepare("$sqlx")) {
	$value_pull->bind_param('i', $returning_rec_id);
	$value_pull->execute();
	$single_field_data = $value_pull->get_result();
	while ($row2 = $single_field_data->fetch_assoc()) {
		$efield = str_replace('rbs', 'pull', $field);
		$$efield = $row2["$field"];
	}
}
###################################################################


	if ($pull = $mysqli->prepare("
        SELECT a.id, a.enrollment_id, b.rbs_ncpdp, b.rbs_npi, b.rbs_pharmname, a.enrollment_status, a.credentialing_status, b.rbs_page
          FROM pharmassess.direct_enrollment_detail a
          JOIN pharmassess.enrollment b ON (a.enrollment_id = b.id)
         WHERE direct_enrollment_id = $direct_id")) {
		echo "<p>Pharmacies Entered:</p>";
		echo "<form>";
		echo "<table style=\"width: 100%;\">\n";
		echo "<tr><th>NCPDP</th><th>NPI</th><th>Pharmacy Name</th><th>Enroll Status</th><th>Cred Status</th><th>&nbsp;</th></tr>\n";
		$pull->bind_param('i', $returning_ncpdp, $returning_npi);
		$pull->execute();
		$pharmacies = $pull->get_result();
		while ($row = $pharmacies->fetch_assoc()) {
			$c_id = $row['id'];
			$e_id = $row['enrollment_id'];
			$ncpdp = $row['rbs_ncpdp'];
			$npi = $row['rbs_npi'];
			$pharm_name = $row['rbs_pharmname'];
			$enroll_status = $row['enrollment_status'];
			$cred_status = $row['credentialing_status'];
			$enroll_page = $row['rbs_page'];
			echo "<tr>";
			echo "<td>$ncpdp</td>";
			echo "<td>$npi</td>";
			echo "<td>$pharm_name</td>";
			
			if ($enroll_status == "Complete") {
				echo "<td><INPUT class=\"button-form-direct\" TYPE=\"button\" VALUE=\"Review\" onClick=\"continue_enrollment($e_id, 'rbs_enroll_review.php')\"></td>";
			}
			else {
				echo "<td><INPUT class=\"button-form-direct\" TYPE=\"button\" VALUE=\"Resume\" onClick=\"continue_enrollment($e_id, $enroll_page)\"></td>";
			}

			if ($result = $mysqli->query("SELECT id FROM pharmassess.direct_cred WHERE enrollment_detail_id = $c_id")) {
	                        $row_cnt = $result->num_rows;
				$result->close();
			}
			else {
				$row_cnt = 0;
			}

			if ($cred_status == 'Complete' ) {
			  echo "<td><INPUT class=\"button-form-direct\" TYPE=\"button\" VALUE=\"Review\" onClick=\"continue_credentialing($c_id, 'continue')\"></td>";
			}
			elseif ($row_cnt > 0 ) {
			  echo "<td><INPUT class=\"button-form-direct\" TYPE=\"button\" VALUE=\"Resume\" onClick=\"continue_credentialing($c_id, 'continue')\"></td>";
			}
			else {
		   	  echo "<td><INPUT class=\"button-form-direct\" TYPE=\"button\" VALUE=\"Start\" onClick=\"continue_credentialing($c_id, 'new')\"></td>";
		        }
			
			echo "<td><INPUT class=\"button-form-direct\" TYPE=\"button\" VALUE=\"Remove\" onClick=\"remove_pharmacy($c_id, $e_id)\"></td></tr>";

			$numrows = $numrows + 1;
			if (($enroll_status == "Complete") && ($cred_status == "Complete")) { $complete = $complete + 1; }
		}
		echo "</table>";
		echo "</form>";
		$pull->close();
	} else {
		printf("Prepared Statement Error: %s\n", $mysqli->error);
	}

	?>

	</div> <!-- end rbs-two-column-wrapper -->

	<br class="clear" /><br />
	<form action="rbs_enroll01.php" method="post">
	<INPUT class="button-form-enroll" TYPE="submit" VALUE="Add Pharmacy">
	</form>

	<hr />

	<div class="rbs-two-column-wrapper">
	<?php 

#	if ($numrows > 0) {
	if (($numrows > 0) && ($numrows == $complete)) {
		echo "<form action=\"rbs_enroll01.php\" onsubmit=\"return validateEmployees()\" method=\"post\">";
		echo "<INPUT class=\"button-form-enroll\" TYPE=\"submit\" VALUE=\"Finish Enrollment\">";
		echo "</form>";
	}
	 
	if ($anchor == 0) {
		echo "
		<script>
		function validateEmployees() {
		  alert(\"A Pharmacist-in-Charge must be entered.\");
		  return false;
		}
		</script>
		";
	}
	
	?>
	</div> <!-- end rbs-two-column-wrapper -->
	

	<div style="clear: both;"></div>
	<div id="errors"></div>

	</div><!-- end mainbody_front -->

	<!-- Sidebar -------------------------------------------------------->
	<?php include '../includes/sidebar_enrollment.php'; ?>
	<!------------------------------------------------------------------->
	
	</div><!-- end content_container_front -->

</div><!-- end wrapper -->
<!-- Footer ----------------------------------------------------->
<?php include '../includes/footer.php'; ?>
<!--------------------------------------------------------------->

</body>
</html>

<?php $mysqli->close(); ?>
