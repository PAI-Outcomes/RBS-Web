<!doctype html> 
<html lang="en">
<head>
<?php include 'includes/include_meta.php'; ?>
<title>Retail Business Solution</title>
<?php include 'includes/include_styles.php'; ?>
<?php include 'includes/include_analytics.php'; ?>
</head>
<body>

<!--Header and Navigation-------------------------------------------->
<?php include 'includes/header_nav.php'; ?>
<!------------------------------------------------------------------->

<script src="//code.jquery.com/ui/1.10.3/jquery-ui.js"></script>
<link rel="stylesheet" href="//code.jquery.com/ui/1.10.3/themes/smoothness/jquery-ui.css" />

 <script>
$(function() {
	var icons = {
		header: "ui-icon-circle-arrow-e",
		activeHeader: "ui-icon-circle-arrow-s"
	};
	$( "#accordion" ).accordion({
		icons: icons,
		heightStyle: "content"
	});
	$( "#toggle" ).button().click(function() {
		if ( $( "#accordion" ).accordion( "option", "icons" ) ) {
			$( "#accordion" ).accordion( "option", "icons", null );
		} else {
			$( "#accordion" ).accordion( "option", "icons", icons );
		}
	});
	
	//$( ".ui-accordion-header" ).click(function() {
		//alert( "Handler for .click() called." );
		//$('html,body').animate({scrollTop: $($(this)).offset().top}, 1000);
	//});
});
</script>

<div id="wrapper"><!-- wrapper -->

	<h1>Retail Business Solution</h1>
	<p>Solutions for Today's Challenges Can be Simplified Through Our Services.</p>
	
<div id="accordion">

	<h3><strong>Learn More About RBS</strong></h3>
	<div>
		<p>Download our marketing documents by clicking a program!</p>
		
		<div class="box_half">
			<div style="float: left;">
				<a href="/downloads/2017.10_rbs_credentialing.pdf" target="_blank"><img src="images/rbs_credentialing.jpg" alt="PharmAssess RBS Information" border="0" /></a>
			</div>
			<div style="float: left; margin-top: 15px;">
				<h2><a href="/downloads/2017.10_rbs_credentialing.pdf" target="_blank">RBS Credentialing</a></h2>
				<p>(PDF Download)</p>
			</div>
			<br style="clear: both;" />
		</div>
		
		<div class="box_half">
			<div style="float: left;">
				<a href="/downloads/2016.08_rbs_marketing.pdf" target="_blank"><img src="images/rbs_full_services_list.jpg" alt="PharmAssess RBS Information" border="0" /></a>
			</div>
			<div style="float: left; margin-top: 15px;">
				<h2><a href="/downloads/2016.08_rbs_marketing.pdf" target="_blank">RBS</a></h2>
				<p>(PDF Download)</p>
			</div>
			<br style="clear: both;" />
		</div>

		<p style="clear: both;">Watch the video below, then read more about each section by clicking to expand.</p>
		
		<style>
		.videoWrapper {
			position: relative;
			padding-bottom: 56.25%; /* 16:9 */
			padding-top: 25px;
			height: 0;
		}
		.videoWrapper iframe {
			position: absolute;
			top: 0;
			left: 0;
			width: 100%;
			height: 100%;
		}
		</style>
		<div class="videoWrapper">
                   <iframe src="https://player.vimeo.com/video/247215871" width="640" height="360" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>
		</div>
		
	</div>

	<h3>Credentialing</h3>
	<div>
		<p>Are you compliant with new FWA and HIPAA requirements? Purchasing or leasing a FWA or HIPAA software system online doesn't necessarily mean you will be compliant when an auditor arrives in your pharmacy.  As HIPAA guidelines continue to become more stringent, we are seeing PBMs and commercial third party payers audit pharmacies for compliance with a training program for pharmacy staff.  For those pharmacies that are non-compliant, penalties and fines can be substantial.  Most pharmacies that subscribe to online FWA and HIPAA programs admit they are behind in having 100% of their staff credentialed.  RBS provides a comprehensive manual (includes FWA, HIPAA, Continuous Quality Improvement, etc.) as well as FWA and HIPAA training programs accompanied with tests and individual employee certificates! Additionally, we track all employees to assure your pharmacy is 100% compliant, including checking all pharmacy staff against the OIG and GSA exclusion lists.  We also make available template Business Associate (BA) agreements, Notice of Privacy Practices (NOPP), Caregiver Consent Forms, Technician Training Manual and more! </p>
		<p>All of this is available in addition to a fully customizable Pharmacy and Employee Policy and Procedure Manual for all of your pharmacy staff.</p>
	</div>

	<h3>Pharmacy Technician Training Manual</h3>
	<div>
		<p>Several State Boards of Pharmacy require pharmacies to have a formal pharmacy technician training program for pharmacy technicians.  RBS has a turnkey program for our RBS clients.  The program includes an individualized manual and assistance in compliance to this state-specific regulation.</p>
	</div>

	<h3>Audit Assistance</h3>
	<div>
		<p>With pharmacy benefit managers (PBMs) seeking additional sources of revenue, independent pharmacies have become prime targets for third party audits. Our program will assist pharmacies prior to as well as during the audit process. This includes proactive reminders and suggestions before a formal audit presents, direction in what the auditors likely will be looking for, review of targeted prescriptions once notification has been received about an upcoming audit and assistance in a response to the PBM contesting recoupment of funds, if necessary.</p>
	</div>

	<h3>Cash Prescription Pricing Program</h3>
	<div>
		<p>Through our internally administered program, we make sure your cash pricing is competitive on a local level. We perform ongoing market research on a local, regional and national basis every month to assure we maximize your cash prescription gross margin and, at the same time, price all prescriptions at a competitive level.  Most participating pharmacies compete aggressively with special local and national programs while consistently achieving gross margins ranging from 51% to 70%. As a RBS member, you are eligible to receive up to $0.25 per paid claim on all of your retail Brand and Generic cash prescriptions that are submitted through our program.</p>
	</div>

	<h3>340B Analysis</h3>
	<div>
		<p>Whether evaluating a decision to participate in a 340B program or confirming the fill fee rates you have already accepted are covering your overall prescription cost, our 340B Profitability Program can assist.  We perform pre-340B analysis and compare this revenue to what the 340B fill fee will generate once you are contracted with the 340B administrator.  This will assure you join a 340B program receiving acceptable reimbursement when entering the program.  If your pharmacy has already enrolled in a 340B program, our profitability program will assist to provide the detailed reporting necessary to re-negotiate an acceptable fill fee with the 340B administrator.  Once your pharmacy is active with a 340B program, our services also include ongoing claim audits and reconciliation on third party payer claims that have been accepted into the 340B program.</p>
	</div>

	<h3>Business Insurance Analysis</h3>
	<div>
		<p>Our program will evaluate your overall business insurance portfolio. We understand that in times of tragedy or turmoil, it is important to have an insurance agent you can depend on. We have partnered with Mertz Insurance for over 15 years and they provide a service you can trust. They will analyze your current Property & Casualty and Professional Liability Insurance to determine if you have the right amount of coverage AND if you are paying the right price. Through Mertz insurance, RBS can potentially save you thousands of dollars per year in unnecessary premiums.</p>
	</div>

	<!--
	<h3>Return Goods Vendor</h3>
	<div>
		<p>By utilizing our preferred return goods vendor, you can maximize the value of your expired medications. Our preferred vendor provides fast, reliable and convenient way to process returns and charges your pharmacy one reasonable flat fee per return. This means that your pharmacy will receive ALL of the money due to you via manufacturer check or wholesaler credit. Unlike other return goods vendors, our preferred vendor does not take a percentage of all money due to you.</p>
	</div>
	-->

	<h3>Flu Vaccine Marketing Program</h3>
	<div>
		<p>As an RBS member, you will have access to a Flu Vaccine Marketing Program. This program provides a variety of materials and information to assist you in marketing your vaccination services to your community and surrounding employer groups. We can assist you with advertisements in local newspapers, material to distribute to walk-in customers, administration logs and more!</p>
	</div>

	<h3>Accounting Services</h3>
	<div>
		<p>As you know, one of the most important relationships any business can have is the one with your accountant. Pharm Assess, Inc. has worked with the same accounting firm for over 20 years and trusts them in providing only the very best service to our RBS members. Our preferred accounting vendor can help your pharmacy with bookkeeping, accounting and cash flow management services.</p>
	</div>

	<h3>Blood Pressure Kiosk</h3>
	<div>
		<p>Through our relationship with our preferred blood pressure kiosk vendor, you have access to a high quality Blood Pressure Kiosk that is serviced and calibrated quarterly. RBS members receive a blood pressure kiosk at no additional charge!</p>
	</div>
	
	<h3>iMedicare</h3>
	<div>
		<p>Included in your RBS membership, you will have access to the iMedicare program. iMedicare is designed to assist your pharmacy in quickly comparing Medicare Part D plans for your patients! As you know, utilizing traditional methods of comparing plans can be very time consuming. iMedicare drastically reduces this burden and allows you to efficiently assist your patients. iMedicare provides several avenues of assisting your Medicare Part D plan comparisons, helping you save time and money!</p>
	</div>
	
	<h3>EQuIPP&reg; Dashboard</h3>
	<div>
		<p>Pharm AssessRBS provides access to the EQuIPP&reg; software to pharmacy members. This software was created by Pharmacy Quality Solutions (PQS) and is affiliated with Pharmacy Quality Alliance which is the company that provides Star Rating measures for Medicare Part D plans.</p>
		
		<p>EQuIPP&reg; is a web-based platform that delivers performance information to participating pharmacies to help them understand their current level of performance on key quality measures that are important to payers. We make the EQuIPP&reg; dashboard available to our members in hopes of (1) empowering each pharmacy to better understand their own ratings in order to make a plan on impacting their rating, if needed and (2) using the pharmacy related measures to represent our pharmacy members with contracting strategies as it pertains to Medicare Part D preferred networks.</p>
	</div>
	
	<h3>Adherence Measures Performance Support (AMPS)</h3>
	<div>
		<p>Exclusively available to our member pharmacies, we have internally developed the Adherence Measures Performance Support (AMPS) program! AMPS is focused on quality improvement specifically in the areas identified by CMS, sometimes referred to as "Star Ratings". This is an addition to our Special Programs portion of our website designed to provide pharmacies with practices, policies, and education that will guide them into improved patient care, better adherence, increased patient convenience and satisfaction, as well as tangible improvements in the Star Ratings of our pharmacies.</p>
	</div>
	
	<h3>Website Maintenance and Development</h3>
	<div>
		<p>Once you are a RBS member, we will assist your pharmacy in developing and maintaining an organized and efficient website! We are able to customize the website with your specific pharmacy information to improve your visibility with your current and potential customer base. If you software vendor allows, we are even able to incorporate online refills onto your website!</p>
	</div>

</div>


</div><!-- end wrapper -->
<!-- Footer ----------------------------------------------------->
<?php include 'includes/footer.php'; ?>
<!--------------------------------------------------------------->

</body>
</html>
