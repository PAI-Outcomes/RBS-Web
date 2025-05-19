<?php

include 'includes/mysql.php';

$rbs_page = basename($_SERVER['PHP_SELF']);
$curdate = date("Y-m-d");
$errorcheck = 0;
$row_cnt = 0;

if (isset($_COOKIE["cont1"]) && isset($_COOKIE["cont2"])&& isset($_COOKIE["cont3"])) {
	$returning_ncpdp = $_COOKIE["cont1"];
	$returning_npi   = $_COOKIE["cont2"];
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

#--------------------------------------------------------------------------------

$rbs_hours_monday  = $open_hours_monday.":".$open_mins_monday." ".$open_ampm_monday." to ";
$rbs_hours_monday .= $close_hours_monday.":".$close_mins_monday." ".$close_ampm_monday;
if ($open_closed_monday == "closed") { $rbs_hours_monday = "closed"; }

$rbs_hours_tuesday  = $open_hours_tuesday.":".$open_mins_tuesday." ".$open_ampm_tuesday." to ";
$rbs_hours_tuesday .= $close_hours_tuesday.":".$close_mins_tuesday." ".$close_ampm_tuesday;
if ($open_closed_tuesday == "closed") { $rbs_hours_tuesday = "closed"; }

$rbs_hours_wednesday  = $open_hours_wednesday.":".$open_mins_wednesday." ".$open_ampm_wednesday." to ";
$rbs_hours_wednesday .= $close_hours_wednesday.":".$close_mins_wednesday." ".$close_ampm_wednesday;
if ($open_closed_wednesday == "closed") { $rbs_hours_wednesday = "closed"; }

$rbs_hours_thursday  = $open_hours_thursday.":".$open_mins_thursday." ".$open_ampm_thursday." to ";
$rbs_hours_thursday .= $close_hours_thursday.":".$close_mins_thursday." ".$close_ampm_thursday;
if ($open_closed_thursday == "closed") { $rbs_hours_thursday = "closed"; }

$rbs_hours_friday  = $open_hours_friday.":".$open_mins_friday." ".$open_ampm_friday." to ";
$rbs_hours_friday .= $close_hours_friday.":".$close_mins_friday." ".$close_ampm_friday;
if ($open_closed_friday == "closed") { $rbs_hours_friday = "closed"; }

$rbs_hours_saturday  = $open_hours_saturday.":".$open_mins_saturday." ".$open_ampm_saturday." to ";
$rbs_hours_saturday .= $close_hours_saturday.":".$close_mins_saturday." ".$close_ampm_saturday;
if ($open_closed_saturday == "closed") { $rbs_hours_saturday = "closed"; }

$rbs_hours_sunday  = $open_hours_sunday.":".$open_mins_sunday." ".$open_ampm_sunday." to ";
$rbs_hours_sunday .= $close_hours_sunday.":".$close_mins_sunday." ".$close_ampm_sunday;
if ($open_closed_sunday == "closed") { $rbs_hours_sunday = "closed"; }

###################################################################

###SET VALUES TO DB################################################
if ($open_closed_monday    != "" && 
    $open_closed_tuesday   != "" && 
	$open_closed_wednesday != "" && 
	$open_closed_thursday  != "" && 
	$open_closed_friday    != "" && 
	$open_closed_saturday  != "" && 
	$open_closed_sunday    != "" 
   ) {
	if ($stmt = $mysqli->prepare("
		UPDATE pharmassess.enrollment SET 
		rbs_hours_monday=?, 
		rbs_hours_tuesday=?, 
		rbs_hours_wednesday=?, 
		rbs_hours_thursday=?, 
		rbs_hours_friday=?, 
		rbs_hours_saturday=?, 
		rbs_hours_sunday=?, 
		rbs_24hour_service=?,
		rbs_page=? 
		WHERE id =?
		;")) {
		$stmt->bind_param('sssssssssi', $rbs_hours_monday, $rbs_hours_tuesday, $rbs_hours_wednesday, $rbs_hours_thursday, $rbs_hours_friday, $rbs_hours_saturday, $rbs_hours_sunday, $rbs_24hour_service, $rbs_page, $returning_rec_id);
		$stmt->execute();
		$stmt->close();
	}
	else {
		printf("Prepared Statement Error: %s\n", $mysqli->error);
		$errorcheck = 1;
	}
	
	if ($errorcheck != 1) {
		if ($pull_status != "pending") {
			header('Location: rbs_enroll_review.php#enroll03');
		} else {
			header('Location: rbs_enroll04.php');
			#exit();
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
		$sqlx = "SELECT $field FROM pharmassess.enrollment WHERE id= ?";
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
	
	$('.zip').mask("99999",{placeholder:" "});
	
	$("#open_closed_monday").change(function(){
		if ( $(this).val() == "open" ) { 
			$(".mon_hours").prop('disabled', false);
		} else {
			$(".mon_hours").prop('disabled', true);
		}
	}); 
	$("#open_closed_monday").change();
	
	$("#open_closed_tuesday").change(function(){
		if ( $(this).val() == "open" ) { 
			$(".tues_hours").prop('disabled', false);
		} else {
			$(".tues_hours").prop('disabled', true);
		}
	});  
	$("#open_closed_tuesday").change();
	
	$("#open_closed_wednesday").change(function(){
		if ( $(this).val() == "open" ) { 
			$(".wed_hours").prop('disabled', false);
		} else {
			$(".wed_hours").prop('disabled', true);
		}
	}); 
	$("#open_closed_wednesday").change();
	
	$("#open_closed_thursday").change(function(){
		if ( $(this).val() == "open" ) { 
			$(".thu_hours").prop('disabled', false);
		} else {
			$(".thu_hours").prop('disabled', true);
		}
	}); 
	$("#open_closed_thursday").change();
	
	$("#open_closed_friday").change(function(){
		if ( $(this).val() == "open" ) { 
			$(".fri_hours").prop('disabled', false);
		} else {
			$(".fri_hours").prop('disabled', true);
		}
	}); 
	$("#open_closed_friday").change();
	
	$("#open_closed_saturday").change(function(){
		if ( $(this).val() == "open" ) { 
			$(".sat_hours").prop('disabled', false);
		} else {
			$(".sat_hours").prop('disabled', true);
		}
	}); 
	$("#open_closed_saturday").change();

	$("#open_closed_sunday").change(function(){
		if ( $(this).val() == "open" ) { 
			$(".sun_hours").prop('disabled', false);
		} else {
			$(".sun_hours").prop('disabled', true);
		}
	}); 
	$("#open_closed_sunday").change();
});

// function validateForm() {

	// var x=document.forms["enroll"]["open_closed_monday"].value;
	// if (x==null || x=="") {
		// alert("Please indicate if your pharmacy is open or closed on each day.");
		// return false;
	// }
	
	// var x=document.forms["enroll"]["open_closed_tuesday"].value;
	// if (x==null || x=="") {
		// alert("Please indicate if your pharmacy is open or closed on each day.");
		// return false;
	// }
	
	// var x=document.forms["enroll"]["open_closed_wednesday"].value;
	// if (x==null || x=="") {
		// alert("Please indicate if your pharmacy is open or closed on each day.");
		// return false;
	// }
	
	// var x=document.forms["enroll"]["open_closed_thursday"].value;
	// if (x==null || x=="") {
		// alert("Please indicate if your pharmacy is open or closed on each day.");
		// return false;
	// }
	
	// var x=document.forms["enroll"]["open_closed_friday"].value;
	// if (x==null || x=="") {
		// alert("Please indicate if your pharmacy is open or closed on each day.");
		// return false;
	// }
	
	// var x=document.forms["enroll"]["open_closed_saturday"].value;
	// if (x==null || x=="") {
		// alert("Please indicate if your pharmacy is open or closed on each day.");
		// return false;
	// }
	
	// var x=document.forms["enroll"]["open_closed_sunday"].value;
	// if (x==null || x=="") {
		// alert("Please indicate if your pharmacy is open or closed on each day.");
		// return false;
	// }
	
	// var x=document.forms["enroll"]["rbs_24hour_service"].value;
	// if (x==null || x=="") {
		// alert("Please indicate if your pharmacy is On Call 24 Hours.");
		// return false;
	// }
  
// }
</script>

<div id="wrapper"><!-- wrapper -->

	<div id="content_container_front">
	<div id="mainbody_front">

	<h1>Pharmacy Hours</h1>
	<form name="enroll" action="<?php echo $_SERVER['PHP_SELF']; ?>" onsubmit="return checkRequiredFields(this)" method="post">

	<div class="rbs-two-column-wrapper clear">
		<p>Please input your hours of operation for open days. Indicate if your pharmacy is open or closed each day of the week on the left.</p> 
	</div> <!-- end rbs-two-column-wrapper -->

	<div class="rbs-two-column-wrapper">

		<div class="rbs-two-column-small">

		<div class="field_title">Open/Closed</div>
		<select name="open_closed_monday" id="open_closed_monday" class="rbs-dropdown-form required">
		<option value="" <?php if ($pull_hours_monday == "") {echo "selected";} ?> ></option>
		<option value="open" <?php if (($pull_hours_monday != "") && ($pull_hours_monday != "closed")) {echo "selected";} ?> >open</option>
		<option value="closed" <?php if ($pull_hours_monday == "closed") {echo "selected";} ?> >closed</option>
		</select>

		<div class="field_title">Open/Closed</div>
		<select name="open_closed_tuesday" id="open_closed_tuesday" class="rbs-dropdown-form required">
		<option value="" <?php if ($pull_hours_tuesday == "") {echo "selected";} ?> ></option>
		<option value="open" <?php if (($pull_hours_tuesday != "") && ($pull_hours_tuesday != "closed")) {echo "selected";} ?> >open</option>
		<option value="closed" <?php if ($pull_hours_tuesday == "closed") {echo "selected";} ?> >closed</option>
		</select>

		<div class="field_title">Open/Closed</div>
		<select name="open_closed_wednesday" id="open_closed_wednesday" class="rbs-dropdown-form required">
		<option value="" <?php if ($pull_hours_wednesday == "") {echo "selected";} ?> ></option>
		<option value="open" <?php if (($pull_hours_wednesday != "") && ($pull_hours_wednesday != "closed")) {echo "selected";} ?> >open</option>
		<option value="closed" <?php if ($pull_hours_wednesday == "closed") {echo "selected";} ?> >closed</option>
		</select>

		<div class="field_title">Open/Closed</div>
		<select name="open_closed_thursday" id="open_closed_thursday" class="rbs-dropdown-form required">
		<option value="" <?php if ($pull_hours_thursday == "") {echo "selected";} ?> ></option>
		<option value="open" <?php if (($pull_hours_thursday != "") && ($pull_hours_thursday != "closed")) {echo "selected";} ?> >open</option>
		<option value="closed" <?php if ($pull_hours_thursday == "closed") {echo "selected";} ?> >closed</option>
		</select>

		<div class="field_title">Open/Closed</div>
		<select name="open_closed_friday" id="open_closed_friday" class="rbs-dropdown-form required">
		<option value="" <?php if ($pull_hours_friday == "") {echo "selected";} ?> ></option>
		<option value="open" <?php if (($pull_hours_friday != "") && ($pull_hours_friday != "closed")) {echo "selected";} ?> >open</option>
		<option value="closed" <?php if ($pull_hours_friday == "closed") {echo "selected";} ?> >closed</option>
		</select>

		<div class="field_title">Open/Closed</div>
		<select name="open_closed_saturday" id="open_closed_saturday" class="rbs-dropdown-form required">
		<option value="" <?php if ($pull_hours_saturday == "") {echo "selected";} ?> ></option>
		<option value="open" <?php if (($pull_hours_saturday != "") && ($pull_hours_saturday != "closed")) {echo "selected";} ?> >open</option>
		<option value="closed" <?php if ($pull_hours_saturday == "closed") {echo "selected";} ?> >closed</option>
		</select>

		<div class="field_title">Open/Closed</div>
		<select name="open_closed_sunday" id="open_closed_sunday" class="rbs-dropdown-form required">
		<option value="" <?php if ($pull_hours_sunday == "") {echo "selected";} ?> ></option>
		<option value="open" <?php if (($pull_hours_sunday != "") && ($pull_hours_sunday != "closed")) {echo "selected";} ?> >open</option>
		<option value="closed" <?php if ($pull_hours_sunday == "closed") {echo "selected";} ?> >closed</option>
		</select>

		</div> <!-- End Column -->

		<div class="rbs-two-column-large">

		<div class="field_title">Monday</div>
		<?php 
		// echo "<span style=\"color: #CCC\">(Currently set: " . $pull_hours_monday.")</span>";
		if ($pull_hours_monday != "closed") {
		$monday = explode(" ", $pull_hours_monday);
		$open = explode(":", $monday[0]);
		$openh = $open[0];
		$openm = $open[1];
		$openampm = $monday[1];
		$close = explode(":", $monday[3]);
		$closeh = $close[0];
		$closem = $close[1];
		$closeampm = $monday[4];
		} else {
		unset($openh); unset($openm); unset($openampm);
		unset($closeh); unset($closem); unset($closeampm);
		}
		?>

		<select name="open_hours_monday" class="rbs-dropdown-form mon_hours">
		<option value="<?php if (isset($openh)) { echo $openh; } else { echo ""; } ?>"><?php if (isset($openh)) { echo $openh; } else { echo ""; } ?></option>
		<option value="1">1</option>
		<option value="2">2</option>
		<option value="3">3</option>
		<option value="4">4</option>
		<option value="5">5</option>
		<option value="6">6</option>
		<option value="7">7</option>
		<option value="8">8</option>
		<option value="9">9</option>
		<option value="10">10</option>
		<option value="11">11</option>
		<option value="12">12</option>
		<option value=""></option>
		</select>
		<select name="open_mins_monday" class="rbs-dropdown-form mon_hours">
		<option value="<?php if (isset($openm)) { echo $openm; } else { echo ""; } ?>"><?php if (isset($openm)) { echo $openm; } else { echo ""; } ?></option>
		<option value="00">00</option>
		<option value="15">15</option>
		<option value="30">30</option>
		<option value="45">45</option>
		<option value=""></option>
		</select>
		<select name="open_ampm_monday" class="rbs-dropdown-form mon_hours">
		<option value="<?php if (isset($openampm)) { echo $openampm; } else { echo ""; } ?>"><?php if (isset($openampm)) { echo $openampm; } else { echo ""; } ?>
		<option value="am">am</option>
		<option value="pm">pm</option>
		<option value=""></option>
		</select>
		<span> to </span>
		<select name="close_hours_monday" class="rbs-dropdown-form mon_hours">
		<option value="<?php if (isset($closeh)) { echo $closeh; } else { echo ""; } ?>"><?php if (isset($closeh)) { echo $closeh; } else { echo ""; } ?></option>
		<option value="1">1</option>
		<option value="2">2</option>
		<option value="3">3</option>
		<option value="4">4</option>
		<option value="5">5</option>
		<option value="6">6</option>
		<option value="7">7</option>
		<option value="8">8</option>
		<option value="9">9</option>
		<option value="10">10</option>
		<option value="11">11</option>
		<option value="12">12</option>
		<option value=""></option>
		</select>
		<select name="close_mins_monday" class="rbs-dropdown-form mon_hours">
		<option value="<?php if (isset($closem)) { echo $closem; } else { echo ""; } ?>"><?php if (isset($closem)) { echo $closem; } else { echo ""; } ?></option>
		<option value="00">00</option>
		<option value="15">15</option>
		<option value="30">30</option>
		<option value="45">45</option>
		<option value=""></option>
		</select>
		<select name="close_ampm_monday" class="rbs-dropdown-form mon_hours">
		<option value="<?php if (isset($closeampm)) { echo $closeampm; } else { echo ""; } ?>"><?php if (isset($closeampm)) { echo $closeampm; } else { echo ""; } ?></option>
		<option value="am">am</option>
		<option value="pm">pm</option>
		<option value=""></option>
		</select>


		<div class="field_title">Tuesday</div>
		<?php 
		// echo "<span style=\"color: #CCC\">(Currently set: " . $pull_hours_tuesday.")</span>";
		if ($pull_hours_tuesday != "closed") {
		$tuesday = explode(" ", $pull_hours_tuesday);
		$open = explode(":", $tuesday[0]);
		$openh = $open[0];
		$openm = $open[1];
		$openampm = $tuesday[1];
		$close = explode(":", $tuesday[3]);
		$closeh = $close[0];
		$closem = $close[1];
		$closeampm = $tuesday[4];
		} else {
		unset($openh); unset($openm); unset($openampm);
		unset($closeh); unset($closem); unset($closeampm);
		}
		?>

		<select name="open_hours_tuesday" class="rbs-dropdown-form tues_hours">
		<option value="<?php if (isset($openh)) { echo $openh; } else { echo ""; } ?>"><?php if (isset($openh)) { echo $openh; } else { echo ""; } ?></option>
		<option value="1">1</option>
		<option value="2">2</option>
		<option value="3">3</option>
		<option value="4">4</option>
		<option value="5">5</option>
		<option value="6">6</option>
		<option value="7">7</option>
		<option value="8">8</option>
		<option value="9">9</option>
		<option value="10">10</option>
		<option value="11">11</option>
		<option value="12">12</option>
		<option value=""></option>
		</select>
		<select name="open_mins_tuesday" class="rbs-dropdown-form tues_hours">
		<option value="<?php if (isset($openm)) { echo $openm; } else { echo ""; } ?>"><?php if (isset($openm)) { echo $openm; } else { echo ""; } ?></option>
		<option value="00">00</option>
		<option value="15">15</option>
		<option value="30">30</option>
		<option value="45">45</option>
		<option value=""></option>
		</select>
		<select name="open_ampm_tuesday" class="rbs-dropdown-form tues_hours">
		<option value="<?php if (isset($openampm)) { echo $openampm; } else { echo ""; } ?>"><?php if (isset($openampm)) { echo $openampm; } else { echo ""; } ?>
		<option value="am">am</option>
		<option value="pm">pm</option>
		<option value=""></option>
		</select>
		<span> to </span>
		<select name="close_hours_tuesday" class="rbs-dropdown-form tues_hours">
		<option value="<?php if (isset($closeh)) { echo $closeh; } else { echo ""; } ?>"><?php if (isset($closeh)) { echo $closeh; } else { echo ""; } ?></option>
		<option value="1">1</option>
		<option value="2">2</option>
		<option value="3">3</option>
		<option value="4">4</option>
		<option value="5">5</option>
		<option value="6">6</option>
		<option value="7">7</option>
		<option value="8">8</option>
		<option value="9">9</option>
		<option value="10">10</option>
		<option value="11">11</option>
		<option value="12">12</option>
		<option value=""></option>
		</select>
		<select name="close_mins_tuesday" class="rbs-dropdown-form tues_hours">
		<option value="<?php if (isset($closem)) { echo $closem; } else { echo ""; } ?>"><?php if (isset($closem)) { echo $closem; } else { echo ""; } ?></option>
		<option value="00">00</option>
		<option value="15">15</option>
		<option value="30">30</option>
		<option value="45">45</option>
		<option value=""></option>
		</select>
		<select name="close_ampm_tuesday" class="rbs-dropdown-form tues_hours">
		<option value="<?php if (isset($closeampm)) { echo $closeampm; } else { echo ""; } ?>"><?php if (isset($closeampm)) { echo $closeampm; } else { echo ""; } ?></option>
		<option value="am">am</option>
		<option value="pm">pm</option>
		<option value=""></option>
		</select>


		<div class="field_title">Wednesday</div>
		<?php 
		// echo "<span style=\"color: #CCC\">(Currently set: " . $pull_hours_wednesday.")</span>";
		if ($pull_hours_wednesday != "closed") {
		$wednesday = explode(" ", $pull_hours_wednesday);
		$open = explode(":", $wednesday[0]);
		$openh = $open[0];
		$openm = $open[1];
		$openampm = $wednesday[1];
		$close = explode(":", $wednesday[3]);
		$closeh = $close[0];
		$closem = $close[1];
		$closeampm = $wednesday[4];
		} else {
		unset($openh); unset($openm); unset($openampm);
		unset($closeh); unset($closem); unset($closeampm);
		}
		?>

		<select name="open_hours_wednesday" class="rbs-dropdown-form wed_hours">
		<option value="<?php if (isset($openh)) { echo $openh; } else { echo ""; } ?>"><?php if (isset($openh)) { echo $openh; } else { echo ""; } ?></option>
		<option value="1">1</option>
		<option value="2">2</option>
		<option value="3">3</option>
		<option value="4">4</option>
		<option value="5">5</option>
		<option value="6">6</option>
		<option value="7">7</option>
		<option value="8">8</option>
		<option value="9">9</option>
		<option value="10">10</option>
		<option value="11">11</option>
		<option value="12">12</option>
		<option value=""></option>
		</select>
		<select name="open_mins_wednesday" class="rbs-dropdown-form wed_hours">
		<option value="<?php if (isset($openm)) { echo $openm; } else { echo ""; } ?>"><?php if (isset($openm)) { echo $openm; } else { echo ""; } ?></option>
		<option value="00">00</option>
		<option value="15">15</option>
		<option value="30">30</option>
		<option value="45">45</option>
		<option value=""></option>
		</select>
		<select name="open_ampm_wednesday" class="rbs-dropdown-form wed_hours">
		<option value="<?php if (isset($openampm)) { echo $openampm; } else { echo ""; } ?>"><?php if (isset($openampm)) { echo $openampm; } else { echo ""; } ?>
		<option value="am">am</option>
		<option value="pm">pm</option>
		<option value=""></option>
		</select>
		<span> to </span>
		<select name="close_hours_wednesday" class="rbs-dropdown-form wed_hours">
		<option value="<?php if (isset($closeh)) { echo $closeh; } else { echo ""; } ?>"><?php if (isset($closeh)) { echo $closeh; } else { echo ""; } ?></option>
		<option value="1">1</option>
		<option value="2">2</option>
		<option value="3">3</option>
		<option value="4">4</option>
		<option value="5">5</option>
		<option value="6">6</option>
		<option value="7">7</option>
		<option value="8">8</option>
		<option value="9">9</option>
		<option value="10">10</option>
		<option value="11">11</option>
		<option value="12">12</option>
		<option value=""></option>
		</select>
		<select name="close_mins_wednesday" class="rbs-dropdown-form wed_hours">
		<option value="<?php if (isset($closem)) { echo $closem; } else { echo ""; } ?>"><?php if (isset($closem)) { echo $closem; } else { echo ""; } ?></option>
		<option value="00">00</option>
		<option value="15">15</option>
		<option value="30">30</option>
		<option value="45">45</option>
		<option value=""></option>
		</select>
		<select name="close_ampm_wednesday" class="rbs-dropdown-form wed_hours">
		<option value="<?php if (isset($closeampm)) { echo $closeampm; } else { echo ""; } ?>"><?php if (isset($closeampm)) { echo $closeampm; } else { echo ""; } ?></option>
		<option value="am">am</option>
		<option value="pm">pm</option>
		<option value=""></option>
		</select>


		<div class="field_title">Thursday</div>
		<?php 
		// echo "<span style=\"color: #CCC\">(Currently set: " . $pull_hours_thursday.")</span>";
		if ($pull_hours_thursday != "closed") {
		$thursday = explode(" ", $pull_hours_thursday);
		$open = explode(":", $thursday[0]);
		$openh = $open[0];
		$openm = $open[1];
		$openampm = $thursday[1];
		$close = explode(":", $thursday[3]);
		$closeh = $close[0];
		$closem = $close[1];
		$closeampm = $thursday[4];
		} else {
		unset($openh); unset($openm); unset($openampm);
		unset($closeh); unset($closem); unset($closeampm);
		}
		?>

		<select name="open_hours_thursday" class="rbs-dropdown-form thu_hours">
		<option value="<?php if (isset($openh)) { echo $openh; } else { echo ""; } ?>"><?php if (isset($openh)) { echo $openh; } else { echo ""; } ?></option>
		<option value="1">1</option>
		<option value="2">2</option>
		<option value="3">3</option>
		<option value="4">4</option>
		<option value="5">5</option>
		<option value="6">6</option>
		<option value="7">7</option>
		<option value="8">8</option>
		<option value="9">9</option>
		<option value="10">10</option>
		<option value="11">11</option>
		<option value="12">12</option>
		<option value=""></option>
		</select>
		<select name="open_mins_thursday" class="rbs-dropdown-form thu_hours">
		<option value="<?php if (isset($openm)) { echo $openm; } else { echo ""; } ?>"><?php if (isset($openm)) { echo $openm; } else { echo ""; } ?></option>
		<option value="00">00</option>
		<option value="15">15</option>
		<option value="30">30</option>
		<option value="45">45</option>
		<option value=""></option>
		</select>
		<select name="open_ampm_thursday" class="rbs-dropdown-form thu_hours">
		<option value="<?php if (isset($openampm)) { echo $openampm; } else { echo ""; } ?>"><?php if (isset($openampm)) { echo $openampm; } else { echo ""; } ?>
		<option value="am">am</option>
		<option value="pm">pm</option>
		<option value=""></option>
		</select>
		<span> to </span>
		<select name="close_hours_thursday" class="rbs-dropdown-form thu_hours">
		<option value="<?php if (isset($closeh)) { echo $closeh; } else { echo ""; } ?>"><?php if (isset($closeh)) { echo $closeh; } else { echo ""; } ?></option>
		<option value="1">1</option>
		<option value="2">2</option>
		<option value="3">3</option>
		<option value="4">4</option>
		<option value="5">5</option>
		<option value="6">6</option>
		<option value="7">7</option>
		<option value="8">8</option>
		<option value="9">9</option>
		<option value="10">10</option>
		<option value="11">11</option>
		<option value="12">12</option>
		<option value=""></option>
		</select>
		<select name="close_mins_thursday" class="rbs-dropdown-form thu_hours">
		<option value="<?php if (isset($closem)) { echo $closem; } else { echo ""; } ?>"><?php if (isset($closem)) { echo $closem; } else { echo ""; } ?></option>
		<option value="00">00</option>
		<option value="15">15</option>
		<option value="30">30</option>
		<option value="45">45</option>
		<option value=""></option>
		</select>
		<select name="close_ampm_thursday" class="rbs-dropdown-form thu_hours">
		<option value="<?php if (isset($closeampm)) { echo $closeampm; } else { echo ""; } ?>"><?php if (isset($closeampm)) { echo $closeampm; } else { echo ""; } ?></option>
		<option value="am">am</option>
		<option value="pm">pm</option>
		<option value=""></option>
		</select>


		<div class="field_title">Friday</div>
		<?php 
		// echo "<span style=\"color: #CCC\">(Currently set: " . $pull_hours_friday.")</span>";
		if ($pull_hours_friday != "closed") {
		$friday = explode(" ", $pull_hours_friday);
		$open = explode(":", $friday[0]);
		$openh = $open[0];
		$openm = $open[1];
		$openampm = $friday[1];
		$close = explode(":", $friday[3]);
		$closeh = $close[0];
		$closem = $close[1];
		$closeampm = $friday[4];
		} else {
		unset($openh); unset($openm); unset($openampm);
		unset($closeh); unset($closem); unset($closeampm);
		}
		?>

		<select name="open_hours_friday" class="rbs-dropdown-form fri_hours">
		<option value="<?php if (isset($openh)) { echo $openh; } else { echo ""; } ?>"><?php if (isset($openh)) { echo $openh; } else { echo ""; } ?></option>
		<option value="1">1</option>
		<option value="2">2</option>
		<option value="3">3</option>
		<option value="4">4</option>
		<option value="5">5</option>
		<option value="6">6</option>
		<option value="7">7</option>
		<option value="8">8</option>
		<option value="9">9</option>
		<option value="10">10</option>
		<option value="11">11</option>
		<option value="12">12</option>
		<option value=""></option>
		</select>
		<select name="open_mins_friday" class="rbs-dropdown-form fri_hours">
		<option value="<?php if (isset($openm)) { echo $openm; } else { echo ""; } ?>"><?php if (isset($openm)) { echo $openm; } else { echo ""; } ?></option>
		<option value="00">00</option>
		<option value="15">15</option>
		<option value="30">30</option>
		<option value="45">45</option>
		<option value=""></option>
		</select>
		<select name="open_ampm_friday" class="rbs-dropdown-form fri_hours">
		<option value="<?php if (isset($openampm)) { echo $openampm; } else { echo ""; } ?>"><?php if (isset($openampm)) { echo $openampm; } else { echo ""; } ?>
		<option value="am">am</option>
		<option value="pm">pm</option>
		<option value=""></option>
		</select>
		<span> to </span>
		<select name="close_hours_friday" class="rbs-dropdown-form fri_hours">
		<option value="<?php if (isset($closeh)) { echo $closeh; } else { echo ""; } ?>"><?php if (isset($closeh)) { echo $closeh; } else { echo ""; } ?></option>
		<option value="1">1</option>
		<option value="2">2</option>
		<option value="3">3</option>
		<option value="4">4</option>
		<option value="5">5</option>
		<option value="6">6</option>
		<option value="7">7</option>
		<option value="8">8</option>
		<option value="9">9</option>
		<option value="10">10</option>
		<option value="11">11</option>
		<option value="12">12</option>
		<option value=""></option>
		</select>
		<select name="close_mins_friday" class="rbs-dropdown-form fri_hours">
		<option value="<?php if (isset($closem)) { echo $closem; } else { echo ""; } ?>"><?php if (isset($closem)) { echo $closem; } else { echo ""; } ?></option>
		<option value="00">00</option>
		<option value="15">15</option>
		<option value="30">30</option>
		<option value="45">45</option>
		<option value=""></option>
		</select>
		<select name="close_ampm_friday" class="rbs-dropdown-form fri_hours">
		<option value="<?php if (isset($closeampm)) { echo $closeampm; } else { echo ""; } ?>"><?php if (isset($closeampm)) { echo $closeampm; } else { echo ""; } ?></option>
		<option value="am">am</option>
		<option value="pm">pm</option>
		<option value=""></option>
		</select>


		<div class="field_title">Saturday</div>
		<?php 
		// echo "<span style=\"color: #CCC\">(Currently set: " . $pull_hours_saturday.")</span>";
		if ($pull_hours_saturday != "closed") {
		$saturday = explode(" ", $pull_hours_saturday);
		$open = explode(":", $saturday[0]);
		$openh = $open[0];
		$openm = $open[1];
		$openampm = $saturday[1];
		$close = explode(":", $saturday[3]);
		$closeh = $close[0];
		$closem = $close[1];
		$closeampm = $saturday[4];
		} else {
		unset($openh); unset($openm); unset($openampm);
		unset($closeh); unset($closem); unset($closeampm);
		}
		?>

		<select name="open_hours_saturday" class="rbs-dropdown-form sat_hours">
		<option value="<?php if (isset($openh)) { echo $openh; } else { echo ""; } ?>"><?php if (isset($openh)) { echo $openh; } else { echo ""; } ?></option>
		<option value="1">1</option>
		<option value="2">2</option>
		<option value="3">3</option>
		<option value="4">4</option>
		<option value="5">5</option>
		<option value="6">6</option>
		<option value="7">7</option>
		<option value="8">8</option>
		<option value="9">9</option>
		<option value="10">10</option>
		<option value="11">11</option>
		<option value="12">12</option>
		<option value=""></option>
		</select>
		<select name="open_mins_saturday" class="rbs-dropdown-form sat_hours">
		<option value="<?php if (isset($openm)) { echo $openm; } else { echo ""; } ?>"><?php if (isset($openm)) { echo $openm; } else { echo ""; } ?></option>
		<option value="00">00</option>
		<option value="15">15</option>
		<option value="30">30</option>
		<option value="45">45</option>
		<option value=""></option>
		</select>
		<select name="open_ampm_saturday" class="rbs-dropdown-form sat_hours">
		<option value="<?php if (isset($openampm)) { echo $openampm; } else { echo ""; } ?>"><?php if (isset($openampm)) { echo $openampm; } else { echo ""; } ?>
		<option value="am">am</option>
		<option value="pm">pm</option>
		<option value=""></option>
		</select>
		<span> to </span>
		<select name="close_hours_saturday" class="rbs-dropdown-form sat_hours">
		<option value="<?php if (isset($closeh)) { echo $closeh; } else { echo ""; } ?>"><?php if (isset($closeh)) { echo $closeh; } else { echo ""; } ?></option>
		<option value="1">1</option>
		<option value="2">2</option>
		<option value="3">3</option>
		<option value="4">4</option>
		<option value="5">5</option>
		<option value="6">6</option>
		<option value="7">7</option>
		<option value="8">8</option>
		<option value="9">9</option>
		<option value="10">10</option>
		<option value="11">11</option>
		<option value="12">12</option>
		<option value=""></option>
		</select>
		<select name="close_mins_saturday" class="rbs-dropdown-form sat_hours">
		<option value="<?php if (isset($closem)) { echo $closem; } else { echo ""; } ?>"><?php if (isset($closem)) { echo $closem; } else { echo ""; } ?></option>
		<option value="00">00</option>
		<option value="15">15</option>
		<option value="30">30</option>
		<option value="45">45</option>
		<option value=""></option>
		</select>
		<select name="close_ampm_saturday" class="rbs-dropdown-form sat_hours">
		<option value="<?php if (isset($closeampm)) { echo $closeampm; } else { echo ""; } ?>"><?php if (isset($closeampm)) { echo $closeampm; } else { echo ""; } ?></option>
		<option value="am">am</option>
		<option value="pm">pm</option>
		<option value=""></option>
		</select>


		<div class="field_title">Sunday</div>
		<?php 
		// echo "<span style=\"color: #CCC\">(Currently set: " . $pull_hours_sunday.")</span>";
		if ($pull_hours_sunday != "closed") {
		$sunday = explode(" ", $pull_hours_sunday);
		$open = explode(":", $sunday[0]);
		$openh = $open[0];
		$openm = $open[1];
		$openampm = $sunday[1];
		$close = explode(":", $sunday[3]);
		$closeh = $close[0];
		$closem = $close[1];
		$closeampm = $sunday[4];
		} else {
		unset($openh); unset($openm); unset($openampm);
		unset($closeh); unset($closem); unset($closeampm);
		}
		?>

		<select name="open_hours_sunday" class="rbs-dropdown-form sun_hours">
		<option value="<?php if (isset($openh)) { echo $openh; } else { echo ""; } ?>"><?php if (isset($openh)) { echo $openh; } else { echo ""; } ?></option>
		<option value="1">1</option>
		<option value="2">2</option>
		<option value="3">3</option>
		<option value="4">4</option>
		<option value="5">5</option>
		<option value="6">6</option>
		<option value="7">7</option>
		<option value="8">8</option>
		<option value="9">9</option>
		<option value="10">10</option>
		<option value="11">11</option>
		<option value="12">12</option>
		<option value=""></option>
		</select>
		<select name="open_mins_sunday" class="rbs-dropdown-form sun_hours">
		<option value="<?php if (isset($openm)) { echo $openm; } else { echo ""; } ?>"><?php if (isset($openm)) { echo $openm; } else { echo ""; } ?></option>
		<option value="00">00</option>
		<option value="15">15</option>
		<option value="30">30</option>
		<option value="45">45</option>
		<option value=""></option>
		</select>
		<select name="open_ampm_sunday" class="rbs-dropdown-form sun_hours">
		<option value="<?php if (isset($openampm)) { echo $openampm; } else { echo ""; } ?>"><?php if (isset($openampm)) { echo $openampm; } else { echo ""; } ?>
		<option value="am">am</option>
		<option value="pm">pm</option>
		<option value=""></option>
		</select>
		<span> to </span>
		<select name="close_hours_sunday" class="rbs-dropdown-form sun_hours">
		<option value="<?php if (isset($closeh)) { echo $closeh; } else { echo ""; } ?>"><?php if (isset($closeh)) { echo $closeh; } else { echo ""; } ?></option>
		<option value="1">1</option>
		<option value="2">2</option>
		<option value="3">3</option>
		<option value="4">4</option>
		<option value="5">5</option>
		<option value="6">6</option>
		<option value="7">7</option>
		<option value="8">8</option>
		<option value="9">9</option>
		<option value="10">10</option>
		<option value="11">11</option>
		<option value="12">12</option>
		<option value=""></option>
		</select>
		<select name="close_mins_sunday" class="rbs-dropdown-form sun_hours">
		<option value="<?php if (isset($closem)) { echo $closem; } else { echo ""; } ?>"><?php if (isset($closem)) { echo $closem; } else { echo ""; } ?></option>
		<option value="00">00</option>
		<option value="15">15</option>
		<option value="30">30</option>
		<option value="45">45</option>
		<option value=""></option>
		</select>
		<select name="close_ampm_sunday" class="rbs-dropdown-form sun_hours">
		<option value="<?php if (isset($closeampm)) { echo $closeampm; } else { echo ""; } ?>"><?php if (isset($closeampm)) { echo $closeampm; } else { echo ""; } ?></option>
		<option value="am">am</option>
		<option value="pm">pm</option>
		<option value=""></option>
		</select>

		</div> <!-- End Column -->

		<div class="clear"></div>

	</div> <!-- end rbs-two-column-wrapper -->
	
	<hr />

	<div class="rbs-two-column-wrapper">
		<div class="rbs-two-column">
			<div class="field_title">On Call 24 Hours?</div>
			<select name="rbs_24hour_service" class="rbs-dropdown-form required">
			<option value=""    <?php if ($pull_24hour_service == "")    {echo "selected";} ?>></option>
			<option value="No"  <?php if ($pull_24hour_service == "No")  {echo "selected";} ?>>No</option>
			<option value="Yes" <?php if ($pull_24hour_service == "Yes") {echo "selected";} ?>>Yes</option>
			</select>
		</div><!-- End Column -->
	</div><!-- Two Column Wrapper -->

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
