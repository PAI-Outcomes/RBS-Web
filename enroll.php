<?php
	setcookie("cont1", "", time()-100);
	setcookie("cont2", "", time()-100);
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
<?php include 'includes/header_nav.php'; ?>
<!------------------------------------------------------------------->
<div id="wrapper"><!-- wrapper -->

	<h1>How to Enroll</h1>

	<p>Select a program option below to begin the process.</p>
	<p>Once completed, a customer service representative will be in contact with your pharmacy. For questions during enrollment, you may <a href="contact.php">contact us</a> at the toll free number (888) 255-6526 (8:30am-5:30pm CST M-F).</p>
	<br />
	
	<div style="margin: 10px 0 25px 0;">
		<div style="float: left; width: 50%; text-align: center;">
			<p>
			<a href="rbs_enroll01.php?type=Cred" style="font-size: 24px; line-height: 32px; text-decoration: underline;">Enroll Now<br />in RBS Credentialing</a>
			</p>
		</div>
		<div style="float: left; width: 50%; text-align: center;">
			<p>
			<a href="rbs_enroll01.php?type=RBS" style="font-size: 24px; line-height: 32px; text-decoration: underline;">Enroll Now<br />in RBS</a>
			</p>
		</div>
		<div style="clear: both;"></div>
	</div>

	<hr />

	<p style="margin: 20px 0px 20px 10px;"><a href="continue_enrollment.php">Click here</a> to continue an enrollment you already started.</p>

	<br />
	<p><strong>Completed and signed documents can be returned here:</strong></p>
	<p><strong>Address:</strong><br />
	P.O. Box 12428<br />
	Overland Park, KS 66282</p>


</div><!-- end wrapper -->
<!-- Footer ----------------------------------------------------->
<?php include 'includes/footer.php'; ?>
<!--------------------------------------------------------------->

</body>
</html>
