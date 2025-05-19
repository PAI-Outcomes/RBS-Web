<?php

setcookie("cont1", "", time()-100);
setcookie("cont2", "", time()-100);
setcookie("cont3", "", time()-100);

##include 'includes/mysql.php';
include 'D:/WWW/vars.php';

###GATHER POST DATA################################################
if (isset($_POST['ncpdp'])) { $ncpdp = $_POST['ncpdp']; } else { $ncpdp = ""; }
if (isset($_POST['npi'])) { $npi = $_POST['npi']; } else { $npi = ""; }
if (isset($_POST['email'])) { $email = $_POST['email']; } else { $email = ""; }
if (isset($_POST['pw'])) { $pw = $_POST['pw']; } else { $pw = ""; }
$errorcheck = 0;
###################################################################

$valid_ncpdp = "none";
$valid_npi = "none";
$valid_email = "none";
$valid_pw = "none";

###READ VALUES FROM DB#############################################
if (($ncpdp != "") && ($npi != "") && ($email != "") && ($pw != "")) {
	if ($pull = $mysqli->prepare("
	SELECT rbs_ncpdp, rbs_npi, rbs_email, rbs_pw, rbs_page, id 
	FROM pharmassess.enrollment 
	WHERE 
	rbs_ncpdp = ? && 
	rbs_npi = ? && 
	rbs_email = ? && 
	rbs_pw = ?
        ORDER BY ID
	")) {
		$pull->bind_param('iiss', $ncpdp, $npi, $email, $pw);
		$pull->execute();
		$pull->store_result();
		$row_cnt = $pull->num_rows;
		$pull->bind_result($check_ncpdp, $check_npi, $check_email, $check_pw, $rbs_page, $rec_id);
		while ($pull->fetch()) {
			$valid_ncpdp = $check_ncpdp;
			$valid_npi = $check_npi;
			$valid_email = $check_email;
			$valid_email = $check_pw;
		}
		$pull->close();
	}
	else {
		printf("Prepared Statement Error: %s\n", $mysqli->error);
		$errorcheck = 1;
	}
	
	if (empty($rbs_page)) {
		$rbs_page = "rbs_enroll02.php";
	}
		
	if (($errorcheck != 1) && ($row_cnt > 0)) {
		if(($valid_ncpdp != "") && ($valid_npi != "")) {
			setcookie("cont1", "$valid_ncpdp", time()+43200);
			setcookie("cont2", "$valid_npi", time()+43200);
			setcookie("cont3", "$rec_id", time()+43200);
			header("Location: $rbs_page");
			exit();
		}
	}
}
###################################################################
?>

<!doctype html> 
<html lang="en">
<head>
<?php include 'includes/include_meta.php'; ?>
<title>Pharm Assess, Inc.</title>
<?php include 'includes/include_styles.php'; ?>
<link type="text/css" rel="stylesheet" media="screen" href="/css/rbs_enroll.css" />
<?php include 'includes/include_analytics.php'; ?>
</head>
<body>

<!--Header and Navigation-------------------------------------------->
<?php include 'includes/header_nav.php'; ?>
<!------------------------------------------------------------------->
<div id="wrapper"><!-- wrapper -->

	<script>
	function validateForm()
	{
	var x=document.forms["continue"]["ncpdp"].value;
	if (x==null || x=="")
	  {
	  alert("NCPDP must be filled out");
	  return false;
	  }
	  
	var x=document.forms["continue"]["npi"].value;
	if (x==null || x=="")
	  {
	  alert("NPI must be filled out");
	  return false;
	  }
	  
	var x=document.forms["continue"]["email"].value;
	if (x==null || x=="")
	  {
	  alert("Email must be filled out");
	  return false;
	  }
	  
	var x=document.forms["continue"]["pw"].value;
	if (x==null || x=="")
	  {
	  alert("Password must be filled out");
	  return false;
	  }

	}
	</script>

	<h1>Continue Your Enrollment</h1>
	<form name="continue" action="<?php echo $_SERVER['PHP_SELF']; ?>" onsubmit="return validateForm()" method="post">
	<div class="rbs-two-column-wrapper">

		<div class="rbs-two-column">
			<div class="field_title">Pharmacy NCPDP</div>
			<INPUT class="rbs-input-text-form" TYPE="text" NAME="ncpdp" VALUE="<?php echo $ncpdp; ?>">

			<div class="field_title">Pharmacy NPI</div>
			<INPUT class="rbs-input-text-form" TYPE="text" NAME="npi" VALUE="<?php echo $npi; ?>">

			<div class="field_title">Pharmacy General Email</div>
			<INPUT class="rbs-input-text-form" TYPE="text" NAME="email" VALUE="<?php echo $email; ?>">
			
			<div class="field_title">Enrollment Password</div>
			<INPUT class="rbs-input-text-form" TYPE="password" NAME="pw" VALUE="<?php echo $pw; ?>">
			
			<br />
			<INPUT class="button-form" TYPE="submit" VALUE="Continue Enrollment">
		</div> <!-- rbs-two-column -->

		<div class="rbs-two-column">
			<p>Please log in to continue your enrollment. These fields should be the first four items completed when you started your enrollment. Once logged in, you will be directed right where you left off.</p>
			<?php
			if (($ncpdp != "") && ($npi != "") && ($email != "") && ($row_cnt == 0)) {
				echo "<span class=\"error\">The information entered did not find any pending enrollments.</span>";
			}
			?>
		</div> <!-- rbs-two-column -->

	</div> <!-- end rbs-two-column-wrapper -->
	
	</form>


</div><!-- end wrapper -->
<!-- Footer ----------------------------------------------------->
<?php include 'includes/footer.php'; ?>
<!--------------------------------------------------------------->

</body>
</html>
