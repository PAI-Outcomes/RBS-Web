<?php

$errorcheck = 0;
$user = "";
$pass = "";

include 'includes/pass_saver.php';
include 'D:/WWW/vars.php';


###GATHER POST DATA################################################
if (isset($_POST['user'])) { $user = $_POST['user']; } else { $user = ""; }
if (isset($_POST['pass'])) { $pass = $_POST['pass']; } else { $pass = ""; }
###################################################################

$valid_user = "none";
$valid_pass = "none";

###READ LOGIN VALUES FROM DB#######################################
if (($user != "") && ($pass != "")) {
	if ($pull = $mysqli->prepare("SELECT ID, Password, Type FROM officedb.weblogin WHERE login=? && CAST(AES_DECRYPT(password,'PAI20181217!') AS CHAR)= ? && Type = 'Admin' && Programs LIKE '%RBS%';")) {
		$pull->bind_param('ss', $user, $pass);
		$pull->execute();
		$pull->store_result();
		$row_cnt = $pull->num_rows;
		$pull->bind_result($id, $lpassword, $ltype);
		$pull->fetch();
		$pull->close();
	}
	else {
		printf("Prepared Statement Error: %s\n", $mysqli->error);
		$errorcheck = 1;
	}
	
	$safepass = simple_crypt($key, $pass, 'encrypt');
		
	if (($errorcheck != 1) && ($row_cnt > 0)) {
		if(($user != "") && ($pass != "")) {
			setcookie("userpai", "$user", time()+43200);
			setcookie("passpai", "$safepass", time()+43200);
			setcookie("uid", "$id", time()+43200);
			
			#include_once 'includes/log_activity.php';
			$action = "Logged into admin area.";
			#log_activity($user, $action, null);
			
			header("Location: admin/cred_pharmacy.php");
			exit();
		}
	}
}
###################################################################

?>

<?php
$url = "$_SERVER[HTTP_HOST]";
?>

<!doctype html> 
<html lang="en">
<head>
<?php include 'includes/include_meta.php'; ?>
<title>Pharm Assess, Inc.</title>
<?php include 'includes/include_styles.php'; ?>
<?php include 'includes/include_analytics.php'; ?>
</head>
<body>

<!--Header and Navigation-------------------------------------------->
<?php include 'includes/admin_header_nav.php'; ?>
<!------------------------------------------------------------------->
<div id="wrapper"><!-- wrapper -->

	<h1>Admin Login</h1><hr />
	
<?php
if ($url == "dev.pharmassess.com") {
	echo "<FORM ACTION=\"admin_login.php\" METHOD=\"POST\">";
} else {
	echo "<FORM ACTION=\"https://www.pharmassess.com/admin_login.php\" METHOD=\"POST\">";
}
#<form name="continue" action="admin_login.php" method="post">
?>

	<div class="cipn-two-column">
		<div class="field_title">Admin Email</div>
		<INPUT class="cipn-input-text-form" TYPE="text" NAME="user" VALUE="<?php echo $user; ?>">
		
		<div class="field_title">Admin Password</div>
		<INPUT class="cipn-input-text-form" TYPE="password" NAME="pass" VALUE="">
		
		<INPUT class="button-form" TYPE="submit" VALUE="Login">
	</div> <!-- cipn-two-column -->
	</form>

	<div class="cipn-two-column">
	<br /><p>Login here for administrative access. If you did not mean to visit this page,<br />you can get back to the homepage by <a href="/">clicking here</a>.</p>
	<?php
	if (($user != "") && ($pass != "") && ($row_cnt == 0)) {
		echo "<span class=\"error\">The information entered did not find any admin logins.</span>";
		#echo "<p><br /><br />Pass:<br /> $pass <br /><br />Test:<br /> $test</p>";
	}
	?>
	</div> <!-- cipn-two-column -->

</div><!-- end wrapper -->
<!-- Footer ----------------------------------------------------->
<?php include 'includes/footer.php'; ?>
<!--------------------------------------------------------------->

</body>
</html>
