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

<script type="text/javascript" src="/includes/jquery_marquee.js"></script>
<script type="text/javascript">
	<!--
	$(function () {
		// basic version is: $('div.demo marquee').marquee() - but we're doing some sexy extras
		
		$('marquee').marquee('pointer').mouseover(function () {
			$(this).trigger('stop');
		}).mouseout(function () {
			$(this).trigger('start');
		}).mousemove(function (event) {
			if ($(this).data('drag') == true) {
				this.scrollLeft = $(this).data('scrollX') + ($(this).data('x') - event.clientX);
			}
		}).mousedown(function (event) {
			$(this).data('drag', true).data('x', event.clientX).data('scrollX', this.scrollLeft);
		}).mouseup(function () {
			$(this).data('drag', false);
		});
	});
	//-->
</script>


<!-- jlh. 09/15/2015
<div class="notification_scroll">
	<div class="notification_click"><strong><a href="/downloads/2015.06_rbs_credentialing_MD.pdf" target='_new'>Learn More</a></strong></div>
	<marquee behavior="scroll" scrollamount="2" direction="left">
		<p><strong>SPECIAL PROMOTION</strong>: Sign up now for RBS Credentialing and receive a discounted rate of $75/mo!</p>
	</marquee>
	<div style="clear: both;"></div>
</div>
-->

	<h1>Welcome to Pharm Assess</h1>
	
	<p>At Pharm Assess, Inc., our goal is to assist independent pharmacy owners achieve the highest level of business success by assuring compliance with State and Federal regulations, gaining efficiency in key aspects of your business, and implementing and maintaining programs that enhance revenue!</p>
	<p>Please take a moment to explore our website to see how we can increase your pharmacy's bottom line!</p>
	
	<div class="box_home">
		<h2><a href="/pharm_rbs.php">Retail Business Solution (RBS) <span style="font-size: 12px; white-space: nowrap;">(click here)</span></a></h2>
		<p>Comprehensive business solution that supports compliance with pharmacy and staff credentialing, audit assistance, third party payer contract assistance with all payers, reconciliation and tracking of third party payer payments, financial reporting, 340B assistance, and much more!</p>
	</div>

	<div class="box_home">
		<h2><a href="/cash_pricing_program.php">Cash Pricing Program to Maximize Revenues <span style="font-size: 12px; white-space: nowrap;">(click here)</span></a></h2>
		<p>A complete cash pricing program designed to enhance your gross margins while verifying your cash pricing is competitive on a local and regional level.</p>
	</div>

	<div class="box_home">
		<h2><a href="/recon.php">Reconciliation and Tracking of Third Party Payer Reimbursement <span style="font-size: 12px; white-space: nowrap;">(click here)</span></a></h2>
		<p>Cash flow is paramount in independent pharmacy. More than a reconciliation program, our system is designed to actively pursue money due from third party payers up to 15 days BEFORE any other reconciliation program.  Whether payment is partially paid, late or lost, our services enhance your cash flow.  We secure your money faster and make sure it resides in your bank account and available for use when you need it.</p>
	</div>
	
</div><!-- end wrapper -->
<!-- Footer ----------------------------------------------------->
<?php include 'includes/footer.php'; ?>
<!--------------------------------------------------------------->

</body>
</html>
