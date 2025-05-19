<?php

// ini_set('display_errors',1);
// ini_set('display_startup_errors',1);
// error_reporting(-1);

include 'includes/mysql.php';
include_once 'includes/log_activity.php';

$rbs_page = basename($_SERVER['PHP_SELF']);
$curdate = date("Y-m-d");
$errorcheck = 0;
$admin_mode = 0;
$row_cnt = 0;
$today = date('m/d/Y h:i A');
$coo_ext;

### Is this an admin mode review?
if (isset($_POST['admin_ncpdp'])) { $admin_ncpdp = $_POST['admin_ncpdp']; } else { $admin_ncpdp = ""; }
if (isset($_POST['admin_npi'])) { $admin_npi = $_POST['admin_npi']; } else { $admin_npi = ""; }
if (isset($_POST['admin_id']))  { $admin_id  = $_POST['admin_id'];  } else { $admin_id  = ""; }
if (isset($_POST['coo_date']))  { $coo_date = $_POST['coo_date'];  } else { $coo_date = ""; } 

if (isset($_COOKIE["LOGIN"])) { $user = $_COOKIE["LOGIN"]; } else { $user = ""; }

if ($admin_ncpdp > 0 && $admin_npi > 0 && $user != "") {
	$returning_ncpdp  = $admin_ncpdp;
	$returning_npi    = $admin_npi;
	$returning_rec_id = $admin_id;
	$admin_mode = 1;
}

if ($admin_mode == 0) {
### If NOT an admin
if (isset($_COOKIE["cont1"]) && isset($_COOKIE["cont2"])&& isset($_COOKIE["cont3"])) {
	$returning_ncpdp  = $_COOKIE["cont1"];
	$returning_npi    = $_COOKIE["cont2"];
	$returning_rec_id = $_COOKIE["cont3"];
	} else {
		#header('Location: continue_enrollment.php');
		#exit();
	}

	$rbs_status = "review";
}

// if (isset($_COOKIE["cont1"]) && isset($_COOKIE["cont2"])) {
	// $returning_ncpdp = $_COOKIE["cont1"];
	// $returning_npi   = $_COOKIE["cont2"];
// } else {
	// header('Location: continue_enrollment.php');
	// exit();
// }
// include 'includes/status.php';

// if (($pull_status == "") || ($pull_status == "complete")) {
	// setcookie("cont1", "", time()+10800);
	// setcookie("cont2", "", time()+10800);
	// $returning_ncpdp = "";
	// $returning_npi   = "";
	
	// if ($pull_status == "complete") {
		// $pull_status = "";
	// }
// }

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

###SET VALUES TO DB################################################
if ($admin_mode == 0) {
	
	$rbs_status = "review";
	
	### If NOT an admin
	if ($stmt = $mysqli->prepare("
			UPDATE pharmassess.enrollment SET
			rbs_status=?, rbs_page=? 
			WHERE id=?
			;")) {
			$stmt->bind_param('ssi', $rbs_status, $rbs_page, $returning_rec_id);
			$stmt->execute();
			$stmt->close();
		}
		else {
			printf("Prepared Statement Error: %s\n", $mysqli->error);
			$errorcheck = 1;
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
		$sqlx = "SELECT $field FROM pharmassess.enrollment WHERE id = ?";
		if ($value_pull = $mysqli->prepare("$sqlx")) {
			$value_pull->bind_param('i', $returning_rec_id);
			$value_pull->execute();
			$single_field_data = $value_pull->get_result();
			while ($row2 = $single_field_data->fetch_assoc()) {
				$efield = str_replace('rbs', 'pull', $field);
				if ($field == 'id') {
				  $efield = 'pull_id';
				}
				if ($field == 'coo') {
				  $efield = 'pull_coo';
				}

				$$efield = $row2["$field"];
				#echo "$efield = ". $row2["$field"] . "<br />";
			}
		}
    }
}
###################################################################

$pull_type_db = $pull_type;
if (preg_match('/cred/i', $pull_type)) { 
	$pull_type = "RBS Credentialing"; 
} else { 
	$pull_type = "RBS"; 
}

if (empty($hidden)) { $hidden = ''; }
if ($hidden == "true") { #If the 'Archive' button is clicked...

	$status = "archive";
	
	if ($pull = $mysqli->prepare("
	UPDATE pharmassess.enrollment SET rbs_status=? WHERE id=?
	")) {
		$pull->bind_param('si', $status, $pull_id);
		$pull->execute();
		$pull->close();
		
		$action = "Archived RBS enrollment for $pull_ncpdp";
		log_activity($user, $action, $pull_ncpdp);
		
	} else {
		printf("Prepared Statement Error: %s\n", $mysqli->error);
	}
	
	if ($rbsdesktop != "true") {
		header('Location: /admin/enrollments.php');
		exit();
	}
}

$goforarchive = 0;

if (empty($paidesktop)) { $paidesktop = ''; }
if ($paidesktop == "true") { #If the 'Add to PAI Desktop' button is clicked...
	$pic_name = '';
	$pic_license = '';
	$pic_exp = '';
	
	$owner_name = '';
	$pic_license = '';
	$pic_exp = '';

	if ($pullcontacts = $mysqli->prepare("
	SELECT * FROM pharmassess.employees 
	WHERE NCPDP=? && NPI=?
	&& (type = 'PIC')
	LIMIT 1
	")) {
		$pullcontacts->bind_param('ii', $pull_ncpdp, $pull_npi);
		$pullcontacts->execute();
		$getcontactinfo = $pullcontacts->get_result();
		while ($row = $getcontactinfo->fetch_assoc()) {
			$pic_name = $row["fname"] . ' ' . $row["lname"];
			$pic_license = $row["license"];
			$pic_exp = $row["exp_date"];
			$pic_exp = date("Y-m-d", strtotime($pic_exp));
		}
		$pullcontacts->close();
	} 
	
	$contactinfo = "";
	if ($pic_license != "" && $pic_exp != "") {
		if ($submit != 'Update PAI Desktop') {
			$contactinfo .= "
			PIC_License_Number = '$pic_license', 
			PIC_License_Expiration_Date = '$pic_exp', 
			PIC_Contact_Name = '$pic_name', 
			";
		} else {
			$contactinfo .= "
			PIC_License_Number =
				CASE 
				WHEN PIC_License_Number IS NULL THEN '$pic_license'
				ELSE PIC_License_Number
				END,
			PIC_License_Expiration_Date =
				CASE 
				WHEN PIC_License_Expiration_Date IS NULL THEN '$pic_exp'
				ELSE PIC_License_Expiration_Date
				END,
			PIC_Contact_Name =
				CASE 
				WHEN PIC_Contact_Name IS NULL THEN '$pic_name'
				ELSE PIC_Contact_Name
				END,
			";
		}
	}

	$owners = "";
	$owners = $pull_owner1_name; #Owner 1 will always be filled out
	if ($pull_owner2_name != '') {
		$owners .= ", $pull_owner2_name";
	}
	if ($pull_owner3_name != '') {
		$owners .= ", $pull_owner3_name";
	}
	if ($pull_owner4_name != '') {
		$owners .= ", $pull_owner4_name";
	}
	
	if ($owners != "") {
		if ($submit != 'Update PAI Desktop') {
			$contactinfo .= "
			Owner_Contact_Name = '$owners', 
			";
		} else {
			$contactinfo .= "
			Owner_Contact_Name =
				CASE 
				WHEN Owner_Contact_Name IS NULL THEN '$owners'
				ELSE Owner_Contact_Name
				END,
			";
		}
	} 

	$main_address    = $pull_main_address1.' '.$pull_main_address2;
	$mailing_address = $pull_mailing_address1.' '.$pull_mailing_address2;
	
	if ($pull_services_vaccinations != '' && $pull_services_vaccinations != 'None') {
		$vax = 'Yes';
	} else {
		$vax = 'No';
	}
	
	if ($pull_24hour_service == "yes") {
		$pull_24hour_service = "Yes";
	} elseif ($pull_24hour_service == "no") {
		$pull_24hour_service = "No";
	}
	
	// if ($pull_hours_saturday == 'closed') { 
		// $pull_hours_saturday = 'Closed'; 
	// }
	// if ($pull_hours_sunday == 'closed') { 
		// $pull_hours_sunday = 'Closed'; 
	// }
	
	$status_field = "";
	$fee_field    = "";
	if (preg_match('/cred/i', $pull_type_db)) {
		$status_field = "Status_Cred";
		$fee_field = "Cred_Fee"; 
	} elseif (preg_match('/direct/i', $pull_type_db)) {
		$status_field = "Status_RBS_Direct";
		$fee_field = "RBS_Direct_Fee"; 
	} else {
		$status_field = "Status_RBS";
		$fee_field = "RBS_Fee"; 
	}
	
	$pull_dea_exp = date("Y-m-d", strtotime($pull_dea_exp));
	$pull_state_license_exp = date("Y-m-d", strtotime($pull_state_license_exp));
	$pull_business_liability_insurance_policy_exp = date("Y-m-d", strtotime($pull_business_liability_insurance_policy_exp));

	$plantype = 'P';

	if ($submit == 'Add to PAI Desktop') {

  	  if ($insert = $mysqli->prepare("
		INSERT INTO officedb.entity_ids 
		SET description = ?,
		type            = ?
	   ;")) 
	  {

	  $insert->bind_param('is',
	    $pull_ncpdp,
	    $plantype 
	  );

	  $insert->execute();

	  if ($pull = $mysqli->prepare("SELECT LAST_INSERT_ID()")) {
	    $pull->execute();
	    $ins = $pull->get_result();
	    $rec = $ins->fetch_array();
	    $admin_pharmacy_id = $rec[0];
	    $pull->close();
	  } else {
		printf("Prepared Statement Error: %s\n", $mysqli->error);
	    }
	  }
	}
	else {
	  if ($pullpharm = $mysqli->prepare("
	  SELECT Pharmacy_ID FROM officedb.pharmacy
	  WHERE NCPDP=? && NPI=?
	  LIMIT 1
	")) {
		$pullpharm->bind_param('ii', $pull_ncpdp, $pull_npi);
		$pullpharm->execute();
		$getpharmacyid = $pullpharm->get_result();
		while ($row = $getpharmacyid->fetch_assoc()) {
			$admin_pharmacy_id = $row["Pharmacy_ID"];
		}
		$pullpharm->close();
	  } 
	}

	if ($submit != 'Update PAI Desktop') {
		#### INSERT INTO WEBLOGIN LOGIC
		$success = 0;
		$sql = "SELECT id
                          FROM officedb.weblogin
                         WHERE login = '$pull_email'";
		$result = $mysqli->query($sql);

		if ($result->num_rows > 0) {
			while($row = $result->fetch_assoc()) {
				$login_id = $row["id"];
		       
				$ins_sql = "INSERT INTO officedb.weblogin_dtl (login_id, pharmacy_id, program)
		                            VALUES ('$login_id', '$admin_pharmacy_id', '$pull_type_db')";
			}
		} else {
			$ins_sql = "INSERT INTO officedb.weblogin (login, password, type, access, programs, comments, permission_level, display_in_menus)
				    VALUES ('$pull_email', AES_ENCRYPT('$pull_pw','PAI20181217!'), 'User', '$admin_pharmacy_id', '$pull_type_db', '', 'NONE', 'No')";
		}
		
		if ($mysqli->query($ins_sql) === TRUE) {
			$success = 1;
		} else {
			$err_msg = "Error Inserting Record: " . $mysqli->error;;
		}	     		

		$coo_dte_fmt = '';

		$db_tbl = 'officedb.pharmacy';

                if($pull_coo > 0) {
		  $db_tbl  = 'officedb.pharmacy_coo';
		  $coo_dte_fmt = "'$coo_date'";
		}
		else {
		  $pull_coo = 'NULL';
		  $coo_dte_fmt = 'NULL';
		}
		
		$sql = "
		INSERT INTO $db_tbl 
		SET 
		Pharmacy_ID = $admin_pharmacy_id,
		NPI = $pull_npi, 
		NCPDP = $pull_ncpdp, 
                COO_Flag = $pull_coo,
		Legal_Name = \"$pull_legalname\", 
		Pharmacy_Name = \"$pull_pharmname\", 
		Business_Phone = '$pull_phone', 
		Address = '$main_address', 
		City = '$pull_main_city', 
		State = '$pull_main_state', 
		Zip = '$pull_main_zip', 
		County = '$pull_main_county_parish', 
		Email_Address = '$pull_email',
                Store_User = '$pull_email',
                Store_Pass = '$pull_pw',
		Fax_Number = '$pull_fax',
		Mailing_Address = '$mailing_address', 
		Mailing_City = '$pull_mailing_city', 
		Mailing_State = '$pull_mailing_state', 
		Mailing_Zip = '$pull_mailing_zip', 
		Website = '$pull_website', 
		Software_Vendor = '$pull_swvendor', 
		Primary_Switch = '$pull_switch', 
		Comm_Pref = '$pull_comm_pref', 
		Send_Reports_To = 'Primary', 
	
		Hours_of_Operation_MF  = '$pull_hours_monday', 
		Hours_of_Operation_Sat = '$pull_hours_saturday', 
		Hours_of_Operation_Sun = '$pull_hours_sunday', 
	
		Hours_Sunday = '$pull_hours_sunday',
		Hours_Monday = '$pull_hours_monday',
		Hours_Tuesday = '$pull_hours_tuesday',
		Hours_Wednesday = '$pull_hours_wednesday',
		Hours_Thursday = '$pull_hours_thursday',
		Hours_Friday = '$pull_hours_friday',
		Hours_Saturday = '$pull_hours_saturday',
	
		State_Sales_Tx_ID = '$pull_state_tax_id',  
		Status = 'Pending', 
		$status_field = 'Pending',
		$fee_field = '$pull_fee',
		Type = '$pull_type_db',
		FEIN = '$pull_fed_tax_id', 
		Fed_Tax_Classification = '$pull_fed_tax_class', 
		Medicare_Part_B_ID_PTAN = '$pull_medicareb', 
		Medicaid_Primary_State = '$pull_medicaid_state1', 
		Affiliate_Name = \"$pull_pri_wholesaler\", 
		Affiliate_Customer_ID = '$pull_wholesaler_acct_number', 
		Vaccinations = '$vax',
                Closed_Door = '$pull_services_closed_door',
                Home_Infusion = '$pull_services_home_infusion',
		DEA = '$pull_dea', 
		DEA_Expiration = '$pull_dea_exp', 
		State_Permit_Number = '$pull_state_license_number', 
		State_Permit_Expiration_Date = '$pull_state_license_exp', 
		Pharmacy_with_24Hour_Service = '$pull_24hour_service', 
		Liability_Ins_Policy_Number = '$pull_business_liability_insurance_policy_number',
		Liability_Ins_Expiration_Date = '$pull_business_liability_insurance_policy_exp',
	
                COO_date = $coo_dte_fmt,
		Notes = \"Pharmacy added to PAI Desktop automatically via RBS Enrollment admin area by $user, $today.\"	
		";
	}
	else {
		#### UPDATE WEBLOGIN LOGIC
		$success = 0;
		$upd_sql = "UPDATE officedb.weblogin_dtl 
			       SET program = CONCAT(program,':', '$pull_type_db')
	                     WHERE pharmacy_id = '$admin_pharmacy_id'";

		if ($mysqli->query($upd_sql) === TRUE) {
			$success = 1;
		} else {
			$err_msg = "Error Updating Record: " . $mysqli->error;;
		}

		$sql = "
		UPDATE officedb.pharmacy 
		SET 
		Legal_Name =
			CASE 
			WHEN Legal_Name IS NULL THEN \"$pull_legalname\"
			ELSE Legal_Name
			END,
		Pharmacy_Name =
			CASE 
			WHEN Pharmacy_Name IS NULL THEN \"$pull_pharmname\"
			ELSE Pharmacy_Name
			END,
		Business_Phone =
			CASE 
			WHEN Business_Phone IS NULL THEN '$pull_phone'
			ELSE Business_Phone
			END,
		Address =
			CASE 
			WHEN Address IS NULL THEN '$main_address'
			ELSE Address
			END,
		City =
			CASE 
			WHEN City IS NULL THEN '$pull_main_city'
			ELSE City
			END,
		State =
			CASE 
			WHEN State IS NULL THEN '$pull_main_state'
			ELSE State
			END,
		Zip =
			CASE 
			WHEN Zip IS NULL THEN '$pull_main_zip'
			ELSE Zip
			END,
		County =
			CASE 
			WHEN County IS NULL THEN '$pull_main_county_parish'
			ELSE County
			END,
		Email_Address =
			CASE 
			WHEN Email_Address IS NULL THEN '$pull_email'
			ELSE Email_Address
			END,
		Fax_Number =
			CASE 
			WHEN Fax_Number IS NULL THEN '$pull_fax'
			ELSE Fax_number
			END,
		Mailing_Address =
			CASE 
			WHEN Mailing_Address IS NULL THEN '$mailing_address'
			ELSE Mailing_Address
			END,
		Mailing_City =
			CASE 
			WHEN Mailing_City IS NULL THEN '$pull_mailing_city'
			ELSE Mailing_City
			END,
		Mailing_State =
			CASE 
			WHEN Mailing_State IS NULL THEN '$pull_mailing_state'
			ELSE Mailing_State
			END,
		Mailing_Zip =
			CASE 
			WHEN Mailing_Zip IS NULL THEN '$pull_mailing_zip'
			ELSE Mailing_Zip
			END,
		Website =
			CASE 
			WHEN Website IS NULL THEN '$pull_website'
			ELSE Website
			END,
		Software_Vendor =
			CASE 
			WHEN Software_Vendor IS NULL THEN '$pull_swvendor'
			ELSE Software_Vendor
			END,
		Primary_Switch =
			CASE 
			WHEN Primary_Switch IS NULL THEN '$pull_switch'
			ELSE Primary_Switch
			END,
		Comm_Pref =
			CASE 
			WHEN Comm_Pref IS NULL THEN '$pull_comm_pref'
			ELSE Comm_Pref
			END,
		Send_Reports_To =
			CASE 
			WHEN Send_Reports_To IS NULL THEN 'Primary'
			ELSE Send_Reports_To
			END,
		Hours_of_Operation_MF =
			CASE 
			WHEN Hours_of_Operation_MF IS NULL THEN '$pull_hours_monday'
			ELSE Hours_of_Operation_MF
			END,
		Hours_of_Operation_Sat =
			CASE 
			WHEN Hours_of_Operation_Sat IS NULL THEN '$pull_hours_saturday'
			ELSE Hours_of_Operation_Sat
			END,
		Hours_of_Operation_Sun =
			CASE 
			WHEN Hours_of_Operation_Sun IS NULL THEN '$pull_hours_sunday'
			ELSE Hours_of_Operation_Sun
			END,
		Hours_Monday =
			CASE 
			WHEN Hours_Monday IS NULL THEN '$pull_hours_monday'
			ELSE Hours_Monday
			END,
		Hours_Tuesday =
			CASE 
			WHEN Hours_Tuesday IS NULL THEN '$pull_hours_tuesday'
			ELSE Hours_Tuesday
			END,
		Hours_Wednesday =
			CASE 
			WHEN Hours_Wednesday IS NULL THEN '$pull_hours_wednesday'
			ELSE Hours_Wednesday
			END,
		Hours_Thursday =
			CASE 
			WHEN Hours_Thursday IS NULL THEN '$pull_hours_thursday'
			ELSE Hours_Thursday
			END,
		Hours_Friday =
			CASE 
			WHEN Hours_Friday IS NULL THEN '$pull_hours_friday'
			ELSE Hours_Friday
			END,
		Hours_Saturday =
			CASE 
			WHEN Hours_Saturday IS NULL THEN '$pull_hours_saturday'
			ELSE Hours_Saturday
			END,
		Hours_Sunday =
			CASE 
			WHEN Hours_Sunday IS NULL THEN '$pull_hours_sunday'
			ELSE Hours_Sunday
			END,
		State_Sales_Tx_ID =
			CASE 
			WHEN State_Sales_Tx_ID IS NULL THEN '$pull_state_tax_id'
			ELSE State_Sales_Tx_ID
			END,
		Status =
			CASE 
			WHEN Status IS NULL THEN 'Pending'
			ELSE Status
			END,
		$status_field =
			CASE 
			WHEN $status_field IS NULL THEN 'Pending'
			ELSE $status_field
			END,
		$fee_field =
			CASE 
			WHEN $fee_field IS NULL THEN '$pull_fee'
			ELSE $fee_field
			END,
		Type =
			CASE 
			WHEN Type IS NULL THEN '$pull_type_db'
			ELSE Type
			END,
		FEIN =
			CASE 
			WHEN FEIN IS NULL THEN '$pull_fed_tax_id'
			ELSE FEIN
			END,
		Fed_Tax_Classification =
			CASE 
			WHEN Fed_Tax_Classification IS NULL THEN '$pull_fed_tax_class'
			ELSE Fed_Tax_Classification
			END,
		Medicare_Part_B_ID_PTAN =
			CASE 
			WHEN Medicare_Part_B_ID_PTAN IS NULL THEN '$pull_medicareb'
			ELSE Medicare_Part_B_ID_PTAN
			END,
		Medicaid_Primary_State =
			CASE 
			WHEN Medicaid_Primary_State IS NULL THEN '$pull_medicaid_state1' 
			ELSE Medicaid_Primary_State
			END,
		Affiliate_Name =
			CASE 
			WHEN Affiliate_Name IS NULL THEN \"$pull_pri_wholesaler\"
			ELSE Affiliate_Name
			END,
		Affiliate_Customer_ID =
			CASE 
			WHEN Affiliate_Customer_ID IS NULL THEN '$pull_wholesaler_acct_number'
			ELSE Affiliate_Customer_ID
			END,
		Vaccinations =
			CASE 
			WHEN Vaccinations IS NULL THEN '$vax'
			ELSE Vaccinations
			END,
		Closed_Door =
			CASE 
			WHEN Closed_Door IS NULL THEN '$pull_services_closed_door'
			ELSE Closed_Door
			END,
		Home_Infusion =
			CASE 
			WHEN Home_Infusion IS NULL THEN '$pull_services_home_infusion'
			ELSE Home_Infusion
			END,
		DEA =
			CASE 
			WHEN DEA IS NULL THEN '$pull_dea'
			ELSE DEA
			END,
		DEA_Expiration =
			CASE 
			WHEN DEA_Expiration IS NULL THEN '$pull_dea_exp'
			ELSE DEA_Expiration
			END,
		State_Permit_Number =
			CASE 
			WHEN State_Permit_Number IS NULL THEN '$pull_state_license_number'
			ELSE State_Permit_Number
			END,
		State_Permit_Expiration_Date =
			CASE 
			WHEN State_Permit_Expiration_Date IS NULL THEN '$pull_state_license_exp'
			ELSE State_Permit_Expiration_Date
			END,
		Pharmacy_with_24Hour_Service =
			CASE 
			WHEN Pharmacy_with_24Hour_Service IS NULL THEN '$pull_24hour_service'
			ELSE Pharmacy_with_24Hour_Service
			END,
		Liability_Ins_Policy_Number =
			CASE 
			WHEN Liability_Ins_Policy_Number IS NULL THEN '$pull_business_liability_insurance_policy_number'
			ELSE Liability_Ins_Policy_Number
			END,
		Liability_Ins_Expiration_Date =
			CASE 
			WHEN Liability_Ins_Expiration_Date IS NULL THEN '$pull_business_liability_insurance_policy_exp'
			ELSE Liability_Ins_Expiration_Date
			END,
		Notes =
			CASE 
			WHEN Notes IS NULL THEN \"Pharmacy added to PAI Desktop automatically via RBS Enrollment admin area by $user, $today.\"	
			ELSE Notes
			END
		WHERE NCPDP= '$pull_ncpdp'
		&& NPI= '$pull_npi'
		";
	}

	$sql_save = $sql;

	if ($addtodesktop = $mysqli->prepare("$sql")) {
		$addtodesktop->execute();
		$addtodesktop->close();

                ####################
		# Insert Contact Data

                if ($pull_ncpdp != '') {
                  add_contact($mysqli, $admin_pharmacy_id, '20', $owners, '', $pull_owner1_email, $pull_owner1_phone, $pull_owner1_cell, '');
                  add_contact($mysqli, $admin_pharmacy_id, '21', $pull_main_contact_name, $pull_main_contact_title, $pull_main_contact_email, $pull_main_contact_phone, $pull_main_contact_cell, '');
                  add_contact($mysqli, $admin_pharmacy_id, '25', $pull_contact_cred_name, $pull_contact_cred_title, $pull_contact_cred_email, $pull_contact_cred_phone, $pull_contact_cred_cell, '');
                }
                else {
                  echo "Error detected: Please try again later";
                }

                ####################

		
		$action = "Added $pull_pharmname ($pull_ncpdp) to PAI Desktop";
		log_activity($user, $action, $pull_ncpdp);
		
		$sql = "
		SELECT * FROM pharmassess.employees 
		WHERE 
		NCPDP = $pull_ncpdp 
		GROUP BY fname, lname
		";
		if ($addemployees = $mysqli->prepare("$sql")) {
			$addemployees->execute();
			
			 //echo "<pre>$sql</pre>";
			// exit();
			
			$getemployees = $addemployees->get_result();
			while ($erow = $getemployees->fetch_assoc()) {
				$fname = $erow["fname"];
				$lname = $erow["lname"];
				$license = $erow["license"];
				$type = $erow["type"];
				$exp_date = $erow["exp_date"];
				$exp_date = date("Y-m-d", strtotime($exp_date));
				
				$sql = "
				REPLACE INTO pharmassess.credentialing_employees
				SET 
				ncpdp = $pull_ncpdp, 
				status = 'Active', 
				fname = '$fname', 
				lname = '$lname', 
				title = '$type', 
				fwa_c = '1999-01-01',
				fwa_m = '1999-01-01', 
				hipaa_exp  = '1999-01-01', 
				coi_coc  = '1999-01-01', 
				handbook = '1999-01-01', 
				oig_gsa  = '1999-01-01',
				date_hired = '1999-01-01',
                                Pharmacy_ID = $admin_pharmacy_id
				#license = '$license', 
				#exp_date = '$exp_date'
				";
				if ($addemployee = $mysqli->prepare("$sql")) {
					$addemployee->execute();
					$addemployee->close();
					shell_exec("perl D:\\WWW\\members.pharmassess.com\\admin\\includes\\check_oig_gsa.pl $pull_ncpdp $pull_type_db $fname $lname");
				}
			}
			$addemployees->close();
			
			sleep(1);
			$action = "Added employees from $pull_pharmname ($pull_ncpdp) to RBS Credentialing";
			log_activity($user, $action, $pull_ncpdp);
			
			#echo "<pre>$sql</pre>";
			
			$goforarchive = 1;
			
		}
		
		$goforarchive = 1;
		
	} else {
		printf("Prepared Statement Error: %s\n", $mysqli->error);
		$goforarchive = 0;
	}
	
	if ($goforarchive == 1) {
		$status = "archive";
		if ($pull = $mysqli->prepare("
		UPDATE pharmassess.enrollment SET rbs_status=? WHERE rbs_ncpdp=? && rbs_npi=?
		")) {
			$pull->bind_param('sii', $status, $pull_ncpdp, $pull_npi);
			$pull->execute();
			$pull->close();
			sleep(1);
			$action = "Archived $pull_type enrollment for $pull_pharmname ($pull_ncpdp)";
			log_activity($user, $action, $pull_ncpdp);
		}
		
		#if ($paidesktop != "true") {
#			header('Location: /admin/enrollments.php');
#			exit();
		#}
	}
	
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

<?php #echo "$sql_save<br>"; ?>

<script src="//code.jquery.com/ui/1.10.3/jquery-ui.js"></script>
<script src="/includes/jquery.maskedinput.min.js" type="text/javascript"></script>
<script src="/includes/checkRequiredFields.js"></script>

<div id="wrapper"><!-- wrapper -->

	<div id="content_container_front">
	<div id="mainbody_front">

		<h1>Review your <?php echo $pull_type; ?> Enrollment</h1>

		<a name="enroll01"></a> 
		<h2 class="review_page_title">Pharmacy Information</h2>
		<div class="review_page">
		
			<div class="rbs-two-column">
				<div class="review_title">Pharmacy Name</div>
				<p class="data"><?php echo $pull_pharmname; ?></p>
				
				<div class="review_title">Pharmacy Legal Name</div>
				<p class="data"><?php echo $pull_legalname; ?></p>
				
				<div class="review_title">Pharmacy Main Email</div>
				<p class="data"><?php echo $pull_email; ?></p>

				<div class="review_title">NCPDP Number</div>
				<p class="data"><?php echo $pull_ncpdp; ?></p>
				
				<div class="review_title">NPI Number</div>
				<p class="data"><?php echo $pull_npi; ?></p>
				
			</div> <!-- rbs-two-column -->

			<div class="rbs-two-column">
				
				<div class="review_title">Phone Number</div>
				<p class="data"><?php echo $pull_phone; ?></p>
				
				<div class="review_title">Fax Number</div>
				<p class="data"><?php echo $pull_fax; ?></p>
				
				<div class="review_title">Pharmacy Website</div>
				<p class="data"><?php echo $pull_website; ?></p>
				
			</div> <!-- rbs-two-column -->
			
			<hr style="clear:both" /><br />

			<h1>Main Contact Information</h1>

			<p><strong>Contract documents will be pre-populated with the main contact information entered below</strong>, an email with the attached contract documents will be sent to the main contact email.</p>

			<div class="rbs-two-column">

				<div class="review_title">Main Contact Name</div>
				<p class="data"><?php echo $pull_main_contact_name; ?></p>

				<div class="review_title">Main Contact Title</div>
				<p class="data"><?php echo $pull_main_contact_title; ?></p>

				<div class="review_title">Main Contact Email</div>
				<p class="data"><?php echo $pull_main_contact_email; ?></p>
				
			</div> <!-- rbs-two-column -->

			<div class="rbs-two-column">

				<div class="review_title">Main Contact Cell</div>
				<p class="data"><?php echo $pull_main_contact_cell; ?></p>

				<div class="review_title">Main Contact Phone</div>
				<p class="data"><?php echo $pull_main_contact_phone; ?></p>

				<div class="review_title">Communication Preference*</div>
				<p class="data"><?php echo $pull_comm_pref; ?></p>
				
				<!--
				<div class="review_title">Phone Ext</div>
				<INPUT class="rbs-input-text-form" TYPE="text" NAME="rbs_main_contact_ext" VALUE="<?php echo $pull_main_contact_ext; ?>">
				-->
				
			</div> <!-- rbs-two-column -->

			<?php if ($admin_mode == 0): ?>
				<p class="review_link"><a href="rbs_enroll01.php">edit this section</a></p>
			<?php endif; ?>

			<br style="clear:both" /> 
			
		</div> <!-- end review_page -->
		
		
		<a name="enroll02"></a> 
		<h2 class="review_page_title">Pharmacy Address</h2>
		<div class="review_page">
		
			<div class="rbs-two-column">
				
				<h2>Physical Address</h2>

				<div class="review_title">Address Line 1</div>
				<p class="data"><?php echo $pull_main_address1; ?></p>

				<div class="review_title">Address Line 2</div>
				<p class="data"><?php echo $pull_main_address2; ?></p>

				<div class="review_title">City</div>
				<p class="data"><?php echo $pull_main_city; ?></p>

				<div class="review_title">State</div>
				<p class="data"><?php echo $pull_main_state; ?></p>
				
				<div class="review_title">Zip</div>
				<p class="data"><?php echo $pull_main_zip; ?></p>
				
				<div class="review_title">County or Parish</div>
				<p class="data"><?php echo $pull_main_county_parish; ?></p>
				
			</div> <!-- rbs-two-column -->

			<div class="rbs-two-column">
				
				<h2>Mailing Address</h2>
				
				<div class="review_title">Address Line 1</div>
				<p class="data"><?php echo $pull_mailing_address1; ?></p>

				<div class="review_title">Address Line 2</div>
				<p class="data"><?php echo $pull_mailing_address2; ?></p>

				<div class="review_title">City</div>
				<p class="data"><?php echo $pull_mailing_city; ?></p>
				
				<div class="review_title">State</div>
				<p class="data"><?php echo $pull_mailing_state; ?></p>
				
				<div class="review_title">Zip</div>
				<p class="data"><?php echo $pull_mailing_zip; ?></p>
				
				<div class="review_title">County or Parish</div>
				<p class="data"><?php echo $pull_mailing_county_parish; ?></p>
				
			</div> <!-- rbs-two-column -->
			
			<?php if ($admin_mode == 0): ?>
				<p class="review_link"><a href="rbs_enroll02.php">edit this section</a></p>
			<?php endif; ?>

			<br style="clear:both" /> 
		
		</div> <!-- end review_page -->
		
		
		<a name="enroll03"></a> 
		<h2 class="review_page_title">Pharmacy Hours</h2>
		<div class="review_page">
		
			<div class="rbs-two-column">
				
				<div class="review_title">Monday</div>
				<p class="data"><?php echo $pull_hours_monday; ?></p>
				
				<div class="review_title">Tuesday</div>
				<p class="data"><?php echo $pull_hours_tuesday; ?></p>
				
				<div class="review_title">Wednesday</div>
				<p class="data"><?php echo $pull_hours_wednesday; ?></p>
				
				<div class="review_title">Thursday</div>
				<p class="data"><?php echo $pull_hours_thursday; ?></p>
				
				<div class="review_title">Friday</div>
				<p class="data"><?php echo $pull_hours_friday; ?></p>
				
			</div> <!-- rbs-two-column -->
			<div class="rbs-two-column">
				
				<div class="review_title">Saturday</div>
				<p class="data"><?php echo $pull_hours_saturday; ?></p>
				
				<div class="review_title">Sunday</div>
				<p class="data"><?php echo $pull_hours_sunday; ?></p>
				
				<div class="review_title">On Call 24 Hours?</div>
				<p class="data"><?php echo $pull_24hour_service; ?></p>

			</div> <!-- rbs-two-column -->
		
			<?php if ($admin_mode == 0): ?>
				<p class="review_link"><a href="rbs_enroll03.php">edit this section</a></p>
			<?php endif; ?>

			<br style="clear:both" /> 
		
		</div> <!-- end review_page -->
		
		
		<a name="enroll04"></a> 	
		<h2 class="review_page_title">Pharmacy Employee Information</h2>
		<div class="review_page">
		
			<?php
			if ($pull = $mysqli->prepare("
			SELECT fname, lname, license, type, exp_date, discipline 
			FROM pharmassess.employees WHERE ncpdp = ? && npi = ? 
			ORDER BY lname, fname")) {
				echo "<p>Staff Members Entered:</p>";
				echo "<table style=\"width: 100%;\">\n";
				echo "<tr><th>Name</th><th>License</th><th>Type</th><th>Exp. Date</th><th>Disciplinary</th></tr>\n";
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
					echo "</tr>\n";
					$numrows = $numrows + 1;
					if ($row['type'] == "Owner") { $owner = 1; }
					if ($row['type'] == "Pharmacist-in-Charge") { $pic = 1; }
				}
				echo "</table>";
				$pull->close();
			} else {
				printf("Prepared Statement Error: %s\n", $mysqli->error);
			}

			?>
			
			<br />
	
			<?php if ($admin_mode == 0): ?>
				<p class="review_link"><a href="rbs_enroll04.php">edit this section</a></p>
			<?php endif; ?>

			<br style="clear:both" /> 
		
		</div> <!-- end review_page -->
	
	
		<a name="enroll05"></a> 
		<h2 class="review_page_title">Pharmacy Owner(s)</h2>
		<div class="review_page">
		
			<?php for ($i=1; $i<=4; $i++): ?>
			
				<?php 
					$ownerNum = $i;
					if (preg_match('/^\s*$/', ${"pull_owner".$ownerNum."_name"})) {
						continue;
					}
				?>
		
				<div class="owner">

					<div class="rbs-two-column">
					
						<div class="review_title">Owner Name</div>
						<p class="data"><?php echo ${"pull_owner".$ownerNum."_name"}; ?></p>
						
						<div class="review_title">Owner Email</div>
						<p class="data"><?php echo ${"pull_owner".$ownerNum."_email"}; ?></p>
					
					</div> <!-- end rbs-two-column -->

					<div class="rbs-two-column">
					
						<div class="review_title">Owner Phone</div>
						<p class="data"><?php echo ${"pull_owner".$ownerNum."_phone"}; ?></p>
						
						<div class="review_title">Owner Cell</div>
						<p class="data"><?php echo ${"pull_owner".$ownerNum."_cell"}; ?></p>
						
						<div class="review_title">Percentage of Ownership</div>
						<p class="data"><?php echo ${"pull_owner".$ownerNum."_pct"}; ?>%</p>
						
					</div> <!-- end rbs-two-column -->
					
					<hr style="clear: both;" />
					
				</div> <!-- end owner -->
			
			<?php endfor; ?>
				

	
			<?php if ($admin_mode == 0): ?>
				<p class="review_link"><a href="rbs_enroll05.php">edit this section</a></p>
			<?php endif; ?>

			<br style="clear:both" /> 
		
		</div> <!-- end review_page -->
		
		
		<a name="enroll06"></a> 
		<h2 class="review_page_title">Credentialing Contact</h2>
		<div class="review_page">
		
			<div class="contact">
			
				<p>This employee will work with our office in managing the pharmacy account as it relates to pharmacy / staff credentialing.</p>

				<div class="rbs-two-column">
				
					<div class="review_title">Name</div>
					<p class="data"><?php echo $pull_contact_comp_name; ?></p>
					
					<div class="review_title">Title</div>
					<p class="data"><?php echo $pull_contact_comp_title; ?></p>
				
				</div> <!-- end rbs-two-column -->

				<div class="rbs-two-column">
				
					<div class="review_title">Phone</div>
					<p class="data"><?php echo $pull_contact_comp_phone; ?></p>
					
					<div class="review_title">Email</div>
					<p class="data"><?php echo $pull_contact_comp_email; ?></p>
					
				</div> <!-- end rbs-two-column -->
				
				
				<div style="clear: both;"></div>
			
			</div> <!-- end contact -->
		
			<?php if ($admin_mode == 0): ?>
				<p class="review_link"><a href="rbs_enroll06.php">edit this section</a></p>
			<?php endif; ?>

			<br style="clear:both" /> 
		
		</div> <!-- end review_page -->
		
		
		<a name="enroll07"></a> 
		<h2 class="review_page_title">Pharmacy Credentialing</h2>
		<div class="review_page">
		
			<div class="rbs-two-column">

				<div class="review_title">Federal Tax Class</div>
				<p class="data"><?php echo $pull_fed_tax_class; ?></p>

				<div class="review_title">Federal Tax ID (FEIN)</div>
				<p class="data"><?php echo $pull_fed_tax_id; ?></p>

				<div class="review_title">State Tax ID</div>
				<p class="data"><?php echo $pull_state_tax_id; ?></p>
				
				<div class="review_title">Medicare Part B ID / PTAN Number</div>
				<p class="data"><?php echo $pull_medicareb; ?></p>

				<div class="review_title">Medicaid Number</div> <!-- 01 -->
				<p class="data"><?php echo $pull_medicaid1; ?></p>
				
				<div class="review_title">Medicaid State</div> <!-- 01 -->
				<p class="data"><?php echo $pull_medicaid_state1; ?></p>

				<div class="review_title">Software Vendor</div>
				<p class="data"><?php echo $pull_swvendor; ?></p>
				
				<div class="review_title">Switch Company</div>
				<p class="data"><?php echo $pull_switch; ?></p>

				<div class="review_title">Primary Wholesaler</div>
				<p class="data"><?php echo $pull_pri_wholesaler; ?></p>
				
				<div class="review_title">Wholesaler Acct. Number</div>
				<p class="data"><?php echo $pull_wholesaler_acct_number; ?></p>				
				
			</div> <!-- rbs-two-column -->

			<div class="rbs-two-column">
				
				<div class="review_title">DEA Number</div>
				<p class="data"><?php echo $pull_dea; ?></p>	
				
				<div class="review_title">DEA Expiration</div>
				<p class="data"><?php echo $pull_dea_exp; ?></p>	

				<div class="review_title">Pharmacy State Permit Number</div>
				<p class="data"><?php echo $pull_state_license_number; ?></p>	
				
				<div class="review_title">Pharmacy State Permit Expiration</div>
				<p class="data"><?php echo $pull_state_license_exp; ?></p>	
				
				<div class="review_title">State Controlled Substance License Number (BNDD, DPS, etc.)</div>
				<p class="data"><?php echo $pull_state_controlled_substance_license_number; ?></p>	
				
				<div class="review_title">State Controlled Substance License Exp.</div>
				<p class="data"><?php echo $pull_state_controlled_substance_license_exp; ?></p>	
				
				<div class="review_title">Business Liability Insurance Policy Number</div>
				<p class="data"><?php echo $pull_business_liability_insurance_policy_number; ?></p>	
				
				<div class="review_title">Business Liability Insurance Policy Expiration</div>
				<p class="data"><?php echo $pull_business_liability_insurance_policy_exp; ?></p>	
				
			</div> <!-- rbs-two-column -->
		
			<?php if ($admin_mode == 0): ?>
				<p class="review_link"><a href="rbs_enroll07.php">edit this section</a></p>
			<?php endif; ?>

			<br style="clear:both" /> 
		
		</div> <!-- end review_page -->
		
		
		<a name="enroll08"></a> 
		<h2 class="review_page_title">Pharmacy Services</h2>
		<div class="review_page">
		
			<table style="min-width: 240px; width: 100%;">
				<tr>
					<td>Compounding Pharmacy</td>
					<td><?php echo $pull_services_compounding; ?></td>
				</tr>
				<tr>
					<td>Contracted to Distribute Under 340B</td>
					<td><?php echo $pull_services_340b; ?></td>
				</tr>
				<tr>
					<td>Delivery</td>
					<td><?php echo $pull_services_delivery; ?></td>
				</tr>
				<tr>
					<td>Drive Thru</td>
					<td><?php echo $pull_services_drive_thru; ?></td>
				</tr>
				<tr>
					<td>E-Prescribing Capabilities</td>
					<td><?php echo $pull_services_eprescribing; ?></td>
				</tr>
				<tr>
					<td>Long Term Care</td>
					<td><?php echo $pull_services_ltc; ?></td>
				</tr>
				<tr>
					<td>Mail Service Pharmacy</td>
					<td><?php echo $pull_services_mail_service; ?></td>
				</tr>
				<tr>
					<td>Online Refills</td>
					<td><?php echo $pull_services_online_refills; ?></td>
				</tr>
				<tr>
					<td>Vaccinations</td>
					<td><?php echo $pull_services_vaccinations; ?></td>
				</tr>
				<tr>
					<td>Specialty Pharmacy</td>
					<td><?php echo $pull_services_specialty; ?></td>
				</tr>
				<tr>
					<td>IVR (Interactive Voice Response)</td>
					<td>
						<?php 
						echo $pull_services_ivr; 
						if ($pull_services_ivr_vendor != '') {
							echo "<br />($pull_services_ivr_vendor)";
						}
						?>
					</td>
				</tr>
				<tr>
					<td>Closed Door</td>
					<td><?php echo $pull_services_closed_door; ?></td>
				</tr>
				<tr>
					<td>Home Infusion</td>
					<td><?php echo $pull_services_home_infusion; ?></td>
				</tr>
				<tr>
					<td>Is your pharmacy rural?</td>
					<td>
						<?php 
						echo $pull_services_rural; 
						if ($pull_services_rural_distance != '') {
							echo "<br />($pull_services_rural_distance miles to closest retail pharmacy)";
						}
						?>
					</td>
				</tr>
			</table>
			
			<br />
		
			<?php if ($admin_mode == 0): ?>
				<p class="review_link"><a href="rbs_enroll08.php">edit this section</a></p>
			<?php endif; ?>

			<br style="clear:both" /> 
		
		</div> <!-- end review_page -->
		
		
		<a name="enroll09"></a> 
		<h2 class="review_page_title">Additional Information</h2>
		<div class="review_page">
		
			<div class="rbs-two-column">
		
				<div class="review_title">How did you hear about us?</div>
				<p class="data"><?php echo $pull_how_did_you_hear_about_us; ?></p>
			
			</div> <!-- rbs-two-column -->
			
			<div class="rbs-two-column">
			
				<div class="review_title">Promo Code</div>
				<p class="data"><?php echo $pull_promo_code; ?></p>
			
			</div> <!-- rbs-two-column -->

			<?php if ($admin_mode == 0): ?>
				<p class="review_link"><a href="rbs_enroll09.php">edit this section</a></p>
			<?php endif; ?>

			<br style="clear:both" /> 
		
		</div> <!-- end review_page -->
		

		<br class="clear" />
		<?php if ($admin_mode == 0): ?>
			<form action="rbs_enroll_complete.php" method="post">
			<INPUT class="button-form-enroll" TYPE="submit" VALUE="Submit Enrollment">
			</form>
		<?php endif; ?>
		
		
	</div><!-- end mainbody_front -->

	<!-- Sidebar -------------------------------------------------------->
	<div id="sidebarWrapper">
		<div id="sidebar">
			<?php if ($admin_mode == 0): ?>
				<h2>Review Your Information</h2>
				<p>Take a moment to review the information you have provided. You can go back and edit any section by clicking "edit this section". Once you have finished reviewing, scroll to the bottom and click "Submit Enrollment". 
			<?php else: ?>
			
				<?php
				echo "$all_post";
				echo "<br /><h2>$pull_pharmname Info:</h2><br />";
				echo "<div class=\"review_title\">Current Progress</div>";
				echo "<p class=\"data\">$pull_page</p>";
				echo "<div class=\"review_title\">Date Started</div>";
				echo "<p class=\"data\">$pull_enrollment_start</p>";
				echo "<hr />";
				echo "<div class=\"review_title\">Enrollment Email</div>";
				echo "<p class=\"data\">$pull_email</p>";
				echo "<div class=\"review_title\">Enrollment PW</div>";
				echo "<p class=\"data\">$pull_pw</p>";
				echo "<hr />";
				
				if ($pull_status == "complete") {

					if ($pull_enrollment_complete == "") { $pull_enrollment_complete = "Not Recorded"; }
					echo "<div class=\"review_title\">Date Completed</div>";
					echo "<p class=\"data\">$pull_enrollment_complete</p>";
					echo "<hr />";
					
					if ($pull_status != "archive") {
						
		                          $db_tbl  = 'officedb.pharmacy';
					  $inDesktop = 0;
					  $inRBS = 0;
						$sql = "
						SELECT NCPDP, Pharmacy_Name, Type, Status_RBS, Status_Cred, Status_RBS_Direct
						FROM $db_tbl 
						WHERE NCPDP = ?
						";
						if ($pull = $mysqli->prepare("$sql")) {
							$pull->bind_param('i', $pull_ncpdp);
							$pull->execute();
							$checkstore = $pull->get_result();
							while ($row = $checkstore->fetch_assoc()) {
								$pai_ncpdp   = $row['NCPDP'];
								$pai_name    = $row['Pharmacy_Name'];
								$pai_type    = $row['Type'];
								$inDesktop++;
								if ($row["Status_RBS"] != '' || $row["Status_Cred"] != '' || $row["Status_RBS_Direct"] != '') {
									$inRBS++;
								}								
							}
							$pull->close();
						}
					
						if ($inDesktop <= 0) {
							echo "<form action=\"rbs_enroll_review.php\" method=\"post\" onsubmit=\"return check_coo_date()\">";
							echo "<input type=\"hidden\" name=\"admin_ncpdp\" value=\"$pull_ncpdp\">";
							echo "<input type=\"hidden\" name=\"admin_npi\" value=\"$pull_npi\">";
							echo "<input type=\"hidden\" name=\"admin_id\" value=\"$pull_id\">";
							echo "<input type=\"hidden\" name=\"paidesktop\" value=\"true\">";
							echo "<input type=\"hidden\" id=\"coo_date\" name=\"coo_date\" value=\"$coo_date\">";
							echo "<INPUT class=\"button-form\" TYPE=\"submit\" NAME=\"submit\" VALUE=\"Add to PAI Desktop\">";
							echo "</form><br />\n\n";
						} elseif ($inRBS <= 0) {
							echo "<form action=\"rbs_enroll_review.php\" method=\"post\">";
							echo "<input type=\"hidden\" name=\"admin_ncpdp\" value=\"$pull_ncpdp\">";
							echo "<input type=\"hidden\" name=\"admin_npi\" value=\"$pull_npi\">";
							echo "<input type=\"hidden\" name=\"admin_id\" value=\"$pull_id\">";
							echo "<input type=\"hidden\" name=\"paidesktop\" value=\"true\">";
							echo "<INPUT class=\"button-form\" TYPE=\"submit\" NAME=\"submit\" VALUE=\"Update PAI Desktop\">";
							echo "</form><br />\n\n";
						} else {
							echo "<p style=\"color: #F00;\">Found in PAI Desktop as $pai_name</p>\n";
						}
						
						echo "<form action=\"rbs_enroll_review.php\" method=\"post\">";
						echo "<input type=\"hidden\" name=\"admin_ncpdp\" value=\"$pull_ncpdp\">";
						echo "<input type=\"hidden\" name=\"admin_npi\" value=\"$pull_npi\">";
						echo "<input type=\"hidden\" name=\"admin_id\" value=\"$pull_id\">";
						echo "<input type=\"hidden\" name=\"hidden\" value=\"true\">";
						echo "<INPUT class=\"button-form\" TYPE=\"submit\" VALUE=\"Archive\">";
						echo "</form><br />\n\n";
						
					}
					
				} else {
					if ($pull_status != "archive") {
						echo "<form action=\"rbs_enroll_review.php\" method=\"post\">";
						echo "<input type=\"hidden\" name=\"admin_ncpdp\" value=\"$pull_ncpdp\">";
						echo "<input type=\"hidden\" name=\"admin_npi\" value=\"$pull_npi\">";
						echo "<input type=\"hidden\" name=\"admin_id\" value=\"$pull_id\">";
						echo "<input type=\"hidden\" name=\"hidden\" value=\"true\">";
						echo "<INPUT class=\"button-form\" TYPE=\"submit\" VALUE=\"Archive (Incomplete)\">";
						echo "</form><br />\n\n";
					}
				}

				if ($pull_type_db == "RBS Direct") {
					$sql = "SELECT credentialing_status
                                                  FROM pharmassess.direct_enrollment_detail
                                                 WHERE enrollment_id = ?";
					if ($pull = $mysqli->prepare("$sql")) {
						$pull->bind_param('i', $admin_id);
						$pull->execute();
						$checkstore = $pull->get_result();
						while ($row = $checkstore->fetch_assoc()) {
							$cred_status = $row['credentialing_status'];
						}
						$pull->close();
					}
    					echo "<div class=\"review_title\">Credentialing Status</div>";
					echo "<p class=\"data\">$cred_status</p>";
					echo "<hr />";

					echo "<form action=\"/direct/cred_review.php\">";
					echo "<input type=\"hidden\" name=\"enrollment_id\" value=\"$pull_id\">";
					echo "<input type=\"hidden\" name=\"category\" value=\"Basic\">";
					echo "<INPUT class=\"button-form\" TYPE=\"submit\" VALUE=\"View Credentialing Data\">";
					echo "</form>";
				}
				
				echo "<form action=\"/members/enrollments.cgi\">";
				echo "<INPUT TYPE=\"hidden\" NAME=\"status\" VALUE=\"pending\">";
				echo "<INPUT class=\"button-form\" TYPE=\"submit\" VALUE=\"Back to Enrollments\">";
				echo "</form>";
				
				?>
			
			<?php endif; ?>
		</div> <!-- end sidebarWrapper -->
	</div> <!-- end sidebar -->
	<!------------------------------------------------------------------->
	</form>
	</div><!-- end content_container_front -->

</div><!-- end wrapper -->
<!-- Footer ----------------------------------------------------->
<?php include 'includes/footer.php'; ?>

<script>

function check_coo_date() {
  var str = document.getElementById("COO_Date").value; 
  if(str==="") {
    alert('Invalid Contract Date');
    return false;
  }

}

function assign_coo_date(val) {
  var str = document.getElementById("COO_Date").value; 
  var array = str.split("/")
  var new_date = array[2]+"-"+array[0]+"-"+array[1];
  document.getElementById("coo_date").value  =  new_date;
}

$(function() {
	
	$(".datepicker").mask("99/99/9999");
	$( ".datepicker" ).datepicker();
	$( "#anim" ).change(function() {
	  $( ".datepicker" ).datepicker( "option", "showAnim", $( this ).val() );
	});
  
});
</script>

<?php


function add_contact($mysqli, $pharmacy_id, $contact_ctl_id, $name, $title, $email, $phone, $cell, $fax) {
  #  echo "INTO add_data<br>";
    
  if ($insert = $mysqli->prepare("
     REPLACE INTO officedb.pharmacy_contacts SET
        pharmacy_id = ?,
        contact_ctl_id = ?,
        name = ?,
        title = ?,
        email = ?,
        phone = ?,
        cellphone = ?,
        fax = ?
  ;")) {
     $insert->bind_param('iissssss',
     $pharmacy_id,
     $contact_ctl_id,	     
     $name,
     $title,
     $email,
     $phone,
     $cell,
     $fax
  );

    $insert->execute();

    echo $mysqli->error;

    $insert->close();
  }
  else {
    printf("Prepared Statement Error: %s\n", $mysqli->error);
    $myFile = "errors.txt";
    $fh = fopen($myFile, 'w') or die("can't open file");
    fwrite($fh, $mysqli->error);
    fclose($fh);
  }
}

$mysqli->close();
?>

</body>
</html>
