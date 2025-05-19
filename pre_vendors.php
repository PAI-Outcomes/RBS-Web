<?php
$con=mysqli_connect("192.168.2.2","pharm","assess","officedb");
if (mysqli_connect_errno($con))
  {
  echo "Failed to connect to database: " . mysqli_connect_error();
  }
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

	<h1>Preferred Vendors</h1>

	<div id="preferredvendors">
	<table width="500px" border="0" cellspacing="0" cellpadding="0" class="main">

	<?php
	$result = mysqli_query($con,"SELECT Vendor_Name, Website, Logo_Name FROM officedb.vendor WHERE Status='Active' && Preferred='Yes' ORDER BY Vendor_Name;");
	while ($row = mysqli_fetch_assoc($result)) {
		$website = $row{'Website'};
			if((strpos("x".$website, 'https') == 0) && ($website != "")) {
				$website = 'http://' . $website;
			} else if ($website == "") {
				$website = "#";
			}
		$image = $row{'Logo_Name'};
		$image = '/images/' . $image;
			
		echo "<tr>";
		echo "<td><a href=\"" . $website . "\">" . $row{'Vendor_Name'} . "</a></td>";
		echo "<td><img src=\"" . $image . "\" /></td>";
		echo "</tr>\n" ;
	}
	?>

	<tr>
	<td colspan=2 style="border: 0px;"><br><a href="pharm_rbs.php">Return to Pharm AssessRBS</a></td>
	</tr>

	</table>

</div><!-- end wrapper -->
<!-- Footer ----------------------------------------------------->
<?php include 'includes/footer.php'; ?>
<!--------------------------------------------------------------->

</body>
</html>