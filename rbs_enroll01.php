<?php

include 'D:/WWW/vars.php';


$rbs_page = basename($_SERVER['PHP_SELF']);
$curdate = date("Y-m-d");
$errorcheck = 0;
$submit_action = 0;
$row_cnt = 0;

if (isset($_COOKIE["cont1"]) && isset($_COOKIE["cont2"])) {
	$returning_ncpdp  = $_COOKIE["cont1"];
	$returning_npi    = $_COOKIE["cont2"];
	$returning_rec_id = $_COOKIE["cont3"];
} else {
	$returning_ncpdp  = "";
	$returning_npi    = "";
	$returning_rec_id = "";
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

###USER CHECK FOR DUPS#############################################
if ($pull_status == "") {
	if (($rbs_ncpdp != "" && $rbs_ncpdp > 100) && ($rbs_npi != "" && $rbs_npi > 100) && ($rbs_email != "") && ($rbs_pw != "")) {
		if ($stmt = $mysqli->prepare("
	   	  SELECT pharmacy_id, COO FROM pharmassess.enrollment a
                    LEFT JOIN officedb.pharmacy b  on b.NCPDP = a.rbs_ncpdp 
                   WHERE a.rbs_ncpdp= ?
                   ORDER BY COO DESC
		  ;")) {

		  $stmt->bind_param('i', $rbs_ncpdp);
		  $stmt->execute();
		  $stmt->store_result();
	          $stmt->bind_result($coo_id, $old_coo);
                  $stmt->fetch(); 
		  $row_cnt = $stmt->num_rows;

		  $stmt->close();
			
		  if ($row_cnt > 0) {
		    if(($coo) && ($old_coo != $coo_id)) {
			    
		      $submit_action = 0;
		    } 
		    else {
		      $submit_action = 1; 
		    }
		  }
		}
		else {
			printf("Prepared Statement Error: %s\n", $mysqli->error);
			$errorcheck = 0;
		}
	}
} else {
	$submit_action = 2; #Already has a 'status', therefore use UPDATE
}

if(!$coo_id) {
  $coo_id = '0';
}

if ($submit_action == 0) {
	if (($rbs_ncpdp != "") && ($rbs_npi != "") && ($rbs_email != "") && ($rbs_pw != "")) {
		if ($stmt = $mysqli->prepare("
			INSERT INTO pharmassess.enrollment SET 
			rbs_ncpdp=?, 
			rbs_npi=?, 
			rbs_enrollment_start=?, 
			rbs_type=?,
			rbs_email=?, 
			rbs_pw=?, 
			rbs_fax=?, 
			rbs_website=?, 
			rbs_phone=?, 
			rbs_pharmname=?, 
			rbs_legalname=?, 
			rbs_main_contact_name=?, 
			rbs_main_contact_title=?, 
			rbs_main_contact_email=?, 
			rbs_main_contact_cell=?, 
			rbs_main_contact_phone=?, 
			rbs_main_contact_ext=?, 
			rbs_comm_pref=?, 
			rbs_page=?, 
                        COO=?
			;")) {
			$stmt->bind_param('iisssssssssssssssssi', $rbs_ncpdp, $rbs_npi, $curdate, $rbs_type, $rbs_email, $rbs_pw, $rbs_fax, $rbs_website,  $rbs_phone, $rbs_pharmname, $rbs_legalname, $rbs_main_contact_name, $rbs_main_contact_title, $rbs_main_contact_email, $rbs_main_contact_cell, $rbs_main_contact_phone, $rbs_main_contact_ext, $rbs_comm_pref, $rbs_page, $coo_id);
			$stmt->execute();
		}
		else {
			printf("Prepared Statement Error: %s\n", $mysqli->error);
			$errorcheck = 1;
		}
		
		if ($errorcheck != 1) {
			setcookie("cont1", "$rbs_ncpdp", time()+43200);
			setcookie("cont2", "$rbs_npi", time()+43200);
		        if ($stmt = $mysqli->prepare("SELECT LAST_INSERT_ID();")) {
		          $stmt->execute();
		          $stmt->store_result();
	                  $stmt->bind_result($record_id);
                          $stmt->fetch(); 
			}

			setcookie("cont3", "$record_id", time()+43200);

			$stmt->close();
			header('Location: rbs_enroll02.php');
			exit();
		}
	}
}

if ($submit_action == 2) {
	if (($rbs_pharmname != "")) {
		if ($stmt = $mysqli->prepare("
			UPDATE pharmassess.enrollment SET 
			rbs_email=?, 
			rbs_fax=?, 
			rbs_website=?, 
			rbs_phone=?, 
			rbs_pharmname=?,
			rbs_legalname=?, 
			rbs_main_contact_name=?, 
			rbs_main_contact_title=?, 
			rbs_main_contact_email=?, 
			rbs_main_contact_cell=?, 
			rbs_main_contact_phone=?, 
			rbs_main_contact_ext=?, 
			rbs_comm_pref=?, 
			rbs_page=? 
			WHERE rbs_ncpdp=? && rbs_npi=?
			;")) {
			$stmt->bind_param('ssssssssssssssii', $rbs_email, $rbs_fax, $rbs_website, $rbs_phone, $rbs_pharmname, $rbs_legalname, $rbs_main_contact_name, $rbs_main_contact_title, $rbs_main_contact_email, $rbs_main_contact_cell, $rbs_main_contact_phone, $rbs_main_contact_ext, $rbs_comm_pref, $rbs_page, $returning_ncpdp, $returning_npi);
			$stmt->execute();
			$stmt->close();
		}
		else {
			printf("Prepared Statement Error: %s\n", $mysqli->error);
			$errorcheck = 1;
		}
		
		if ($errorcheck != 1) {
			if ($pull_status == "review") {
				header('Location: rbs_enroll_review.php');
			} else {
				header('Location: rbs_enroll02.php');
			}
			exit();
		}
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
		$sqlx = "SELECT $field FROM pharmassess.enrollment WHERE rbs_ncpdp = ? && rbs_npi = ? ORDER BY ID DESC LIMIT 1";
		if ($value_pull = $mysqli->prepare("$sqlx")) {
			$value_pull->bind_param('ii', $returning_ncpdp, $returning_npi);
			$value_pull->execute();
			$single_field_data = $value_pull->get_result();
			while ($row2 = $single_field_data->fetch_assoc()) {
				$efield = str_replace('rbs', 'pull', $field);
				$$efield = $row2["$field"];
				##echo "$efield = ". $row2["$field"] . "<br />";
			}
		}
    }
}
###################################################################

if (empty($pull_type)) {
	if (isset($_GET['type'])) { $pull_type = $_GET['type']; } else { $pull_type = ''; }
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
$(function() {
	$('.phone').mask('(999) 999-9999');
});
</script>

<div id="wrapper"><!-- wrapper -->
	<div id="content_container_front">

	<div id="mainbody_front">

	<h1>Let's get started!</h1>
	<form name="enroll" action="<?php echo $_SERVER['PHP_SELF']; ?>" onsubmit="return checkRequiredFields(this)" method="post">
	
	<INPUT TYPE="hidden" NAME="rbs_type" VALUE="<?php echo $pull_type; ?>">
        <INPUT TYPE="hidden" ID="coo" NAME="coo" VALUE="<?php echo $coo; ?>">

	<div class="rbs-two-column-wrapper clear">

	<?php
	if ($submit_action == 1) {
		echo "<span class=\"notice\">We're sorry, it appears that this pharmacy has already started an enrollment. To continue an enrollment, <a href=\"continue_enrollment.php\">Click here</a>. Call (888) 255-6526 for help.</span>";
	}
	?>

	<p><strong>Already Started? <a style="text-decoration: underline;" href="continue_enrollment.php">Click here</a> to continue.</strong></p> 
	<p>Enter your pharmacy information in the fields below.</p> 

	<hr class="clear" />

	<p>Pre-Populate with ArchQ data by filling in your NCPDP & NPI and clicking >> <INPUT class="button-form-small" TYPE="button" VALUE="Import" onclick="checkArchQ('<?php echo $pull_type; ?>')"></p>

	</div> <!-- end rbs-two-column-wrapper -->

	<div class="rbs-two-column-wrapper">

	<div class="rbs-two-column">
		<div class="field_title">Pharmacy NCPDP</div>
		<INPUT class="rbs-input-text-form ncpdp required" TYPE="text" ID="NCPDP" NAME="rbs_ncpdp"placeholder="Please enter NCPDP first(7 digits)" VALUE="<?php echo $pull_ncpdp;?>" maxlength="7" onkeyup="checkNCPDP(this.value)">

		<div class="field_title">Pharmacy NPI</div>
		<INPUT class="rbs-input-text-form npi required" TYPE="text" ID="NPI" NAME="rbs_npi" VALUE="<?php echo $pull_npi; ?>" maxlength="10">
		<div class="field_title">Pharmacy Name</div>
		<INPUT class="rbs-input-text-form required" ID="PharmName" TYPE="text" NAME="rbs_pharmname" VALUE="<?php echo $pull_pharmname; ?>">
		
		<div class="field_title">Pharmacy Legal Name</div>
		<INPUT class="rbs-input-text-form required" TYPE="text" NAME="rbs_legalname" VALUE="<?php echo $pull_legalname; ?>">
		
		<div class="field_title">Pharmacy Main Email</div>
		<INPUT class="rbs-input-text-form required" TYPE="text" ID="EMAIL" NAME="rbs_email" VALUE="<?php echo $pull_email; ?>" onchange="checkLogin(this.value)">

		
	</div> <!-- rbs-two-column -->

	<div class="rbs-two-column">
		
		<div class="field_title">Phone Number</div>
		<INPUT class="rbs-input-text-form phone required" TYPE="text" NAME="rbs_phone" VALUE="<?php echo $pull_phone; ?>">
		
		<div class="field_title">Fax Number</div>
		<INPUT class="rbs-input-text-form phone required" TYPE="text" NAME="rbs_fax" VALUE="<?php echo $pull_fax; ?>">
		
		<div class="field_title">Pharmacy Website</div>
		<INPUT class="rbs-input-text-form" TYPE="text" NAME="rbs_website" VALUE="<?php echo $pull_website; ?>">
		
		<?php
		if ($pull_status != "") {
		echo "<div class=\"field_title\">Enrollment Password*</div>";
		#$hidden_password = preg_replace("|.|","*",$pull_pw); 
		$hidden_password = preg_replace('/(?!^)\S/', '*', $pull_pw);
		echo "<p class=\"data\">$hidden_password</p>";
		} else {
		echo "<div class=\"field_title\">Create Your Enrollment Password<strong>*</strong></div>";
		echo "<INPUT ID=\"password\" class=\"rbs-input-text-form required\" TYPE=\"password\" NAME=\"rbs_pw\" VALUE=\"$pull_pw\">";
		echo "<div class=\"field_title\">Confirm Enrollment Password</div>";
		echo "<INPUT ID=\"password_confirm\" class=\"rbs-input-text-form required\" TYPE=\"password\" NAME=\"rbs_pw_conf\" VALUE=\"$pull_pw\">";
		}
		?>
		
	</div> <!-- rbs-two-column -->
	<p class="clear" style="font-size: 16px;">*If at any time you close out of your enrollment, you can continue later, <i><strong>but you must remember your password you create here.</strong></i> <a href="continue_enrollment.php">Click here</a> to continue an enrollment you already started. Your pre-populated contracts will be sent to you password protected with this password.</p>
	</div> <!-- end rbs-two-column-wrapper -->

	<hr class="clear" />

	<h1>Main Contact Information</h1>

	<p><strong>Contract documents will be pre-populated with the main contact information entered below</strong>, an email with the attached contract documents will be sent to the main contact email.</p>

	<div class="rbs-two-column-wrapper">

	<div class="rbs-two-column">

		<div class="field_title">Main Contact Name (First, MI, Last)</div>
		<INPUT class="rbs-input-text-form required" TYPE="text" NAME="rbs_main_contact_name" VALUE="<?php echo $pull_main_contact_name; ?>">

		<div class="field_title">Main Contact Title</div>
		<INPUT class="rbs-input-text-form required" TYPE="text" NAME="rbs_main_contact_title" VALUE="<?php echo $pull_main_contact_title; ?>">

		<div class="field_title">Main Contact Email</div>
		<INPUT class="rbs-input-text-form required" TYPE="text" NAME="rbs_main_contact_email" VALUE="<?php echo $pull_main_contact_email; ?>">
		
	</div> <!-- rbs-two-column -->

	<div class="rbs-two-column">

		<div class="field_title">Main Contact Cell</div>
		<INPUT class="rbs-input-text-form phone required" TYPE="text" NAME="rbs_main_contact_cell" VALUE="<?php echo $pull_main_contact_cell; ?>">

		<div class="field_title">Main Contact Phone</div>
		<INPUT class="rbs-input-text-form phone required" TYPE="text" NAME="rbs_main_contact_phone" VALUE="<?php echo $pull_main_contact_phone; ?>">

		<div class="field_title">Communication Preference*</div>
		<select name="rbs_comm_pref" class="rbs-dropdown-form required">
		<?php if ($pull_comm_pref == "") {
			echo "<option value=\"\" selected></option>";
		} else {
			echo "<option value=\"$pull_comm_pref\" selected>$pull_comm_pref</option>";
		} ?>
		<!-- <option value=""></option> -->
		<option value="Email">Email</option>
		<option value="Fax">Fax</option>
		<option value="Both">Both</option>
		</select>
		
		<!--
		<div class="field_title">Phone Ext</div>
		<INPUT class="rbs-input-text-form" TYPE="text" NAME="rbs_main_contact_ext" VALUE="<?php echo $pull_main_contact_ext; ?>">
		-->
		
	</div> <!-- rbs-two-column -->

	</div> <!-- end rbs-two-column-wrapper -->

	<div style="clear: both;"></div>
	<div id="errors"></div>
	
	<div class="rbs-two-column-wrapper">
	<INPUT class="button-form-enroll" TYPE="submit" VALUE="<?php if ($pull_status == "review") {echo "Update and Review";} else {echo "Next Page";} ?>">

	<p>*Please note, you may receive communications from us regarding useful information as it pertains to our programs.</p>

	</div> <!-- end rbs-two-column-wrapper -->

	</div><!-- end mainbody_front -->

	<!-- Sidebar -------------------------------------------------------->
	<?php include 'includes/sidebar_enrollment.php'; ?>
	<!------------------------------------------------------------------->

<script>

if(document.getElementById("coo").value == '') {	

  $( "input" ).prop( "disabled", true );
  $( "select" ).prop( "disabled", true );
  $("[name='rbs_ncpdp']").prop("disabled", false);
  $('#NCPDP').on('keypress', function(ev) {
    var keyCode = window.event ? ev.keyCode : ev.which;
    //codes for 0-9
    if (keyCode < 48 || keyCode > 57) {
        //codes for backspace, delete, enter
        if (keyCode != 0 && keyCode != 8 && keyCode != 13 && !ev.ctrlKey) {
            ev.preventDefault();
        }
    }
  });
  $('#NPI').on('keypress', function(ev) {
    var keyCode = window.event ? ev.keyCode : ev.which;
    //codes for 0-9
    if (keyCode < 48 || keyCode > 57) {
        //codes for backspace, delete, enter
        if (keyCode != 0 && keyCode != 8 && keyCode != 13 && !ev.ctrlKey) {
            ev.preventDefault();
        }
    }
  });
  function checkNCPDP(val) {

    if(val.length == '7'){
      $.ajax({
        type: 'POST',
        url: '/ajax/pharmacy_data.pl',
        data: { 'ncpdp': val },
        success: function(res) {
        var regex = /[0-9]/g;
        var found = res.result.match(regex);
	var checked;
	if (res.result.match(regex)) {
	  if(res.rbs_sts != null) {
            var yesno = confirm("This pharmacy is already in our system. Would you like to change the ownership?");
	    if(yesno) {
	      document.getElementById("coo").value = yesno;
  	      document.getElementById("PharmName").value    = res.name;
              $( "INPUT" ).prop( "disabled", false );
              $( "select" ).prop( "disabled", false );
	    }
	    else {
              document.getElementById("NCPDP").value = '';	
              $( "INPUT" ).prop( "disabled", true );
              $( "select" ).prop( "disabled", true );
              $("[name='rbs_ncpdp']").prop("disabled", false);
	    }
	  }
	  else {
            $( "INPUT" ).prop( "disabled", false );
            $( "select" ).prop( "disabled", false );
	  }
	}
	else {
	  document.getElementById("coo").value = '';
	}
      },
        error: function() {alert("Could not connect to the Server.");}
      });
    }
  }

  function checkLogin(val) {
      $.ajax({
        type: 'POST',
        url: '/ajax/login_data.pl',
        data: { 'login': val },
        success: function(res) {
        var regex = /[A-Z]/g;
	if (res.login.match(regex)) {
            alert("This email is already in our system. Please choose another email");
            document.getElementById("EMAIL").value = '';	
            document.getElementById("EMAIL").focus();	
	}
      },
        error: function() {alert("Could not connect to the Server.");}
      });
  }

  function checkArchQ(type) {
    val1 = document.getElementById("NCPDP").value;
    if(val1.length == '7'){
      val2 = document.getElementById("NPI").value;
      if(val2.length == '10'){
        $.ajax({
          type: 'POST',
          url: 'ajax/archq_data.pl',
          data: { 'ncpdp': val1, 'npi': val2, 'prog': type },
          success: function(res) {
          var regex = /Success/g;
          if (res.result.match(regex)) {
            var d = new Date();
            d.setTime(d.getTime() + (7*24*60*60*1000));
            var expires = "expires="+ d.toUTCString();
    	    document.cookie = "cont1=" + val1 + ";" + expires + ";path=/";
    	    document.cookie = "cont2=" + val2 + ";" + expires + ";path=/";
    	    document.cookie = "cont3=" + res.id + ";" + expires + ";path=/";
            location.reload();
          }
          else {
            alert('Sorry.  We were not able to locate your data');
          }
        },
          error: function() {alert("Could not connect to the Server.");}
        });
      }
      else {
        alert('Please fill in NPI and try again.');
      }
    }
    else {
      alert('Please fill in NCPDP and try again.');
    }
  }

  document.getElementById("EMAIL").focus();	
}
else {
  $("[name='rbs_ncpdp']").prop("disabled", true);
  $("[name='rbs_npi']").prop("disabled", true);
}

</script
	</form>
	</div><!-- end content_container_front -->

</div><!-- end wrapper -->
<!-- Footer ----------------------------------------------------->
<?php include 'includes/footer.php'; ?>
<!--------------------------------------------------------------->

</body>
</html>

<?php $mysqli->close(); ?>
