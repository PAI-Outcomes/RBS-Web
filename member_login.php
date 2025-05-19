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
<?php include 'includes/header_nav.php'; ?>
<!------------------------------------------------------------------->
<div id="wrapper"><!-- wrapper -->

<h1>Member Login</h1><hr />

	<div class="box_third">
		<form action="/members/index.cgi" method="POST">
		<p>Username</p>
		<input type="text" name="USER" value="" class="loginbox" autocorrect="off" autocapitalize="off">
		<p>Password</p>
		<input type="password" name="PASS" value="" class="loginbox" autocorrect="off" autocapitalize="off">
		<input type="Submit" value="Log In" class="button-form-login">
		</form>
	</div><!--end pharm_login-->

</div><!-- end wrapper -->
<!-- Footer ----------------------------------------------------->
<?php include 'includes/footer.php'; ?>
<!--------------------------------------------------------------->

</body>
</html>
