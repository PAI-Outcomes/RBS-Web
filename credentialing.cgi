require "D:/RedeemRx/MyData/RBSDesktop_routines.pl";
require "D:/RedeemRx/cgi-bin/cgi-lib.pl";

use File::Basename;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use Env qw(PATH REMOTE_ADDR PERL5LIB PERLLIB);

$| = 1;
my $start = time();
($prog, $dir, $ext) = fileparse($0, '\..*');

$title = "$prog";
$title = qq#${COMPANY} - $title# if ( $COMPANY );

&readsetCookies;

$ret = &ReadParse(*in);
&CgiDie("Error in reading and parsing of CGI input") if !defined $ret;

&read_canned_header($RBSHeader);

#______________________________________________________________________________

if ( $USER ) {
   &MembersHeaderBlock;
} else {
   &MembersLogin;
   &MyPharmassessMembersTrailer;

   print qq#</BODY>\n#;
   print qq#</HTML>\n#;
   exit(0);
}

#______________________________________________________________________________
# Create the inputfile format name
my ($min, $hour, $day, $month, $year) = (localtime)[1,2,3,4,5];
$year  += 1900;	# reported as "years since 1900".
$month += 1;	# reported ast 0-11, 0==January
$syear  = sprintf("%4d", $year);
$smonth = sprintf("%02d", $month);
$sday   = sprintf("%02d", $day);
$tdate  = sprintf("%04d-%02d-%02d", $year, $month, $day);
$ddate  = sprintf("%02d/%02d/%04d", $month, $day, $year);
$ttime  = sprintf("%02d:%02d", $hour, $min);

#______________________________________________________________________________

my $alert = '';

&update_employee() if ( $in{'action'} );

&do_report() if ( $in{'mev_conf'} );

#if ( $in{'action'} =~/Add|Update|Term|Save/i ) {
if ( $in{'action'} || $in{'mev_conf'} ) {
  $disp_cred = 'inline-block';
}
else {
  $disp_cred = 'none';
}

if ( $in{'action'} =~/Add|Update|Term/i ) {
  $disp_manage = 'inline-block';
}
else {
  $disp_manage = 'none';
}

$ntitle = "Credentialing and Compliance";
print qq#<h1>$ntitle</h1>\n\n#;

&printCredInfo($PH_ID, 'RBS', $disp_cred, $disp_manage, $alert);

&MyPharmassessMembersTrailer;

exit(0);

sub update_employee {
  $dbin     = "R8DBNAME";
  $DBNAME   = $DBNAMES{"$dbin"};
  $TABLE    = $DBTABN{"$dbin"};
  my $sql;
  my $action = '';
  my $change_type = 'O';

  $dbx = DBI->connect("DBI:mysql:$DBNAME:$DBHOST",$dbuser,$dbpwd,
         { PrintError => 1, RaiseError => 1, InactiveDestroy => 0 } ) || die "$DBI::errstr";

  if ( $in{'license'} !~ /^\s+$/ ) {
   $lic_exp = "'$in{'license_exp'}'";
  }
  else {
   $lic_exp = "NULL";
  }

  &readPharmacies();

  if ( $in{'action'} =~ /Add/ ) {
    $sql = "INSERT INTO pharmassess.credentialing_employees
               SET ncpdp = '$Pharmacy_NCPDPs{$PH_ID}',
                   Pharmacy_ID = $PH_ID,
                   status = 'Active',
                   fname = '$in{'fname'}',
                   lname = '$in{'lname'}',
                   title = '$in{'title'}',
                   license = '$in{'license'}',
                   exp_date = $lic_exp,
                   date_hired = '$in{'date_hired'}',
                   fwa_c = '1999-01-01',
		   fwa_m = '1999-01-01',
	  	   hipaa_exp = '1999-01-01', 
		   coi_coc = '1999-01-01',
		   handbook = '1999-01-01',
                   oig_gsa = '1999-01-01'";
    
    $action = "Employee Added";
  }
  elsif ( $in{'action'} =~ /Update/ ) {
    $comp_name = $in{'fname'} . ' ' . $in{'lname'};
    $sql = "UPDATE pharmassess.credentialing_employees
               SET 
                   fname = '$in{'fname'}',
                   lname = '$in{'lname'}',
                   title = '$in{'title'}',
                   license = '$in{'license'}',
                   exp_date = $lic_exp,
                   date_hired = '$in{'date_hired'}'
             WHERE id = $in{'emp_id'}";

    if ( $comp_name ne $in{'disp_name'} ) {
      $change_type = 'N';
    }
    else {
      $change_type = 'T';
    }

    $action = "Employee Updated";
  }
  elsif ( $in{'action'} =~ /Term/ ) {
    $sql = "UPDATE pharmassess.credentialing_employees
               SET status = 'Inactive'
             WHERE id = $in{'emp_id'}";
    $action = "Employee Termed";
  }
  elsif ( $in{'action'} =~ /Save/ ) {
    $sql  = "SELECT action
               FROM officedb.logs
              WHERE ncpdp = $PH_ID
                 && exec = '/members/credentialing.cgi'
                 && date >= '$tdate 00:00:00'
                 && action != 'MEV Confirmed'
           ORDER BY action";

#    print "SQL: $sql<br>";

    my $sthx  = $dbx->prepare("$sql");
    $sthx->execute;
    my $NumOfRows = $sthx->rows;

    if ( $NumOfRows > 0 ) {
      $message = "$Pharmacy_Names{$PH_ID} ($Pharmacy_NCPDPs{$PH_ID}) made the following changes:<br><br>";

      while ( my ($action) = $sthx->fetchrow_array() ) {
        (@pcs) = split(/:/, $action);
        (@dtl) = split(/\|/, $pcs[2]);
        $message .= "$pcs[0] - $dtl[0] $dtl[1] Title: $dtl[2]<br>";
      }
 
      $to = 'RBS@Outcomes.com';
#      $to = 'afedosyuk@tdsclinical.com';
#      $to = 'bprowell@tdsclinical.com';

#      &send_email('NoReply', $to, 'Pharmacy Profile Updated', $message);
      $alert = 'Changes Saved';
    }
    $sthx->finish();
  }

  if ( $in{'action'} =~/Add|Update|Term/i ) {
    $alert = $action;
    $action_db = "$action:$change_type:$in{'fname'}|$in{'lname'}|$in{'title'}";
    &logActivity($USER, $action_db, $PH_ID);
    $dbx->do($sql) or die $DBI::errstr;
  }

  $dbx->disconnect;
}

#______________________________________________________________________________

sub do_report {
  $dbx = DBI->connect("DBI:mysql:$DBNAME:$DBHOST",$dbuser,$dbpwd,
         { PrintError => 1, RaiseError => 1, InactiveDestroy => 0 } ) || die "$DBI::errstr";

  my $title = "Pharm Assess, Inc. - Monthly Employee Verification";
  my $content = "<html><head></head><body>";

  $content .= "<h2 style=\"text-align: center;\"><strong>$title</strong></h2>";
  $content .= "<p style=\"font-size: 18pt; text-align: center;\"><strong>Completed Online</strong></p>";
         
  $content .= "<center><table class=\"employees\" style=\"border: 1px solid black; border-collapse: collapse;\">";
  
  $content .= "<tr>
                 <td colspan=5><center>
                 <strong>$Pharmacy_Names{$PH_ID}</strong> &nbsp; NCPDP: $Pharmacy_NCPDPs{$PH_ID} &nbsp; Sent: $ddate
                 </center></td>
               </tr>";
   
  #Employee #Title #License #License Expiration #Termed?
  $content .= "<tr>
                 <th style=\"border: 1pt solid #000; text-align: left; border-style: collapse;\">Employee Name</th>
                 <th style=\"border: 1pt solid #000; border-style: collapse;\">Title</th>
                 <th style=\"border: 1pt solid #000; border-style: collapse;\">License#</th>
                 <th style=\"border: 1pt solid #000; border-style: collapse;\">License Expiration</th>
                 <th style=\"border: 1pt solid #000; border-style: collapse;\">Termed?</th>
               </tr>";
         
  $sql2 = "SELECT fname, lname, title, license, exp_date, ncpdp
             FROM pharmassess.credentialing_employees 
            WHERE Pharmacy_ID = $PH_ID
               && status = 'Active' 
         ORDER BY lname, fname";

  $sth2 = $dbx->prepare($sql2);
  $empfound = $sth2->execute;

  while ( $emps = $sth2->fetchrow_hashref() ) {
    $fname = $emps->{"fname"};
    $lname = $emps->{"lname"};
    $name = "$fname $lname";
    $employee_title = $emps->{"title"};
    $license = $emps->{"license"};
    $exp_date = $emps->{"exp_date"};
                  
    $content .= "<tr>
                   <td style=\"border: 1pt solid #000; text-align: left; border-style: collapse;\">$name</td>
                   <td style=\"border: 1pt solid #000; text-align: center; border-style: collapse;\">$employee_title</td>
                   <td style=\"border: 1pt solid #000; text-align: center; border-style: collapse;\">$license</td>
                   <td style=\"border: 1pt solid #000; text-align: center; border-style: collapse;\">$exp_date</td>
                   <td style=\"border: 1pt solid #000; border-style: collapse;\">&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;</td>
                 </tr>";
  }

  $sth2->finish();
         
#  $content .= "<tr><td colspan=5 style=\"border: 1pt solid #000; border-style: collapse;\">&nbsp; &nbsp;</td></tr>";
  $content .= "<tr style=\"height: 50px\"><td colspan=5 style=\"border: 1pt solid #000; border-style: collapse;\"><span style=\"font-size: 14pt;\">Verified By:  $in{'auth_name'} &nbsp; &nbsp; Date: $ddate $ttime</span></td></tr>"; 
 
  $content .= "</table></center>";

  # ----------------------------------------------------------------------- #
         
  $content .= "</body></html>";

  $html_file_path = "D:\\RBSDesktop\\Reports\\$Pharmacy_NCPDPs{$PH_ID}_MEV.html";
  open ($html_file, "> $html_file_path")  || die "Couldn't open output file\n\t$!\n\n";
  print $html_file $content;
  close $html_file;

#  $pdf_file = "D:\\Reports\\$Pharmacy_NCPDPs{$PH_ID}_MEV.pdf";
  $pdf_file = "D:\\WWW\\members.pharmassess.com\\members\\WebShare\\Credentialing\\MEV\\$Pharmacy_NCPDPs{$PH_ID}_MEV.pdf";
 
  $cmd = "\"D:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe\" $html_file_path $pdf_file 2> nul";
  ($cmd, $out) = &docmd_local($cmd);

##  $cmd = "\"D:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe\" $html_file_path $pdf_file 2> nul";
##  ($cmd, $out) = &docmd_local($cmd);

#  chmod(0777, $pdf_file);
  chmod 0777, $pdf_file or die "Couldn't chmod $pdf_file: $!";


  &logActivity($USER, 'MEV Confirmed', $PH_ID);
  $dbx->disconnect;
  $alert = 'Successfully Confirmed';
}

#______________________________________________________________________________

sub docmd_local {

  my ($cmd) = @_;
  my $out = "";

  chomp($out = `$cmd`);
  $cmd = "";
  $out =~ s///g;
  my @array = split("\n", $out);
  $out = "";
  foreach $pc (@array) {
     $out .= "$pc\n" if ( $pc !~ /^\s*$/ ); # remove blank lines
  }

  return($cmd, $out);
}
