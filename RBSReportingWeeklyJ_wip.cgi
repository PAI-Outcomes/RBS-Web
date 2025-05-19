require "D:/RedeemRx/MyData/RBSDesktop_routines.pl";
require "D:/RedeemRx/cgi-bin/cgi-lib.pl";

use File::Basename;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use Env qw(PATH REMOTE_ADDR PERL5LIB PERLLIB);

$| = 1;
my $start = time();
my ($prog, $dir, $ext) = fileparse($0, '\..*');
$nbsp = "&nbsp\;";

$ret = &ReadParse(*in);
&CgiDie("Error in reading and parsing of CGI input") if !defined $ret;

$ReportWeek = $in{'ReportWeek'};

($ReportWeek) = &StripJunk($ReportWeek);

#______________________________________________________________________________

&readsetCookies;

#&MyPharmassessReportingWeeklyHeader;
&MyPharmassessMembersHeader;

#______________________________________________________________________________
# Create the inputfile format name
my ($min, $hour, $day, $month, $year) = (localtime)[1,2,3,4,5];
$year  += 1900;	# reported as "years since 1900".
$month += 1;	# reported ast 0-11, 0==January
$syear  = sprintf("%4d", $year);
$smonth = sprintf("%02d", $month);
$sday   = sprintf("%02d", $day);
$tdate  = sprintf("%04d/%02d/%02d", $year, $month, $day);
$rdate  = sprintf("%04d-%02d-%02d", $year, $month, $day);
$ttime  = sprintf("%02d:%02d", $hour, $min);

$yearcur = $year;
$yearm1  = $year - 1;
$yearm2  = $year - 2;
$ymc = $year;
$ym1 = $yearm1;
$ym2 = $yearm2;

if ( $ReportWeek == 0 || $ReportWeek =~ /^\s*$/ ) {
   $ReportWeek = $rdate;
}

#______________________________________________________________________________

if ( $USER ) {
#  &MembersHeaderBlock("INREPORTING");
  &MembersHeaderBlock;
} else {
   &MembersLogin;
#  &MyPharmassessMembersTrailer;
  
   print qq#</BODY>\n#;
   print qq#</HTML>\n#;
   exit(0);
}

#______________________________________________________________________________

&readPharmacies;

my @NCPDPSArray = ();

my $dbin      = "RWDBNAME";	# RBS Reporting Weekly data
my $DBNAME    = $DBNAMES{"$dbin"};
my $TABLERW   = $DBTABN{"$dbin"};
my $FIELDSRW  = $DBFLDS{"$dbin"};
my $FIELDS2RW = $DBFLDS{"$dbin"} . "2";

# connect to the RBS Reporting Database (with two tables, monthly & weekly)

%attr = ( PrintWarn=>1, RaiseError=>1, PrintError=>1, AutoCommit=>1, InactiveDestroy=>0, HandleError => \&handle_error );
$dbRW = DBI->connect("DBI:mysql:$DBNAME:$DBHOST",$dbuser,$dbpwd, \%attr) || &handle_error;
   
#______________________________________________________________________________

$timeframe = "Weekly";

my $LATESTDATE = 0;

my ($PHCOUNT) = &readWeeklyData;

if ( $PHCOUNT == -1 ) {
   # Owner login, no reporting data!
   &displayNoDataFound;
} else {
   &displayReport($PHCOUNT);
}

#______________________________________________________________________________

# Close the Database
$dbRW->disconnect;

&MyPharmassessMembersTrailer;

exit(0);

#______________________________________________________________________________

sub displayReport {
  my ($PHCOUNT) = @_;

  print qq#<!-- displayReport --><br>\n#;

  if ( ReportWeek == 0 || $ReportWeek =~ /^\s*$/ ) {
     $ReportWeek = $LATESTDATE;
  }

  @pcs = split("-", $ReportWeek, 3);
  $week = sprintf("%02d/%02d/%04d", $pcs[1], $pcs[2], $pcs[0]);

  print qq#<div id="wrapper_weekly"><!-- wrapper -->\n#;

  print qq#<table class="header"><tr>\n#;
#  print qq#<td width="350px"><img class="reports-table" src="../images/PharmAssess_Logo_Main1-1024x212.png"></td>\n#;
  print qq#<td class="paddingtitle"><h2>Weekly Report</h2>\n#;
  print qq#for $Pharmacy_Names{$PH_ID}</td>\n# if ( $Pharmacy_Names{$PH_ID} !~ /^\s*$/ );
  print qq#</tr></table>\n#;
  print qq#<br>\n#;

  print qq#<table class="reports-table">\n#;
  print qq#<tr class="reports-firstrow"><th colspan=5>Week Ending $week</th></tr>\n#;
 
  print qq#<tr>\n#;
  print qq#<td width="25%" class="right">$nbsp     </td>\n#;
  print qq#<td class="right"><strong>Scripts       </strong></td>\n#;
  print qq#<td class="right"><strong>Revenue       </strong></td>\n#;
  print qq#<td width="20%" class="right"><strong>Gross Margin  </strong></td>\n#;
  print qq#<td class="right"><strong>% Gross Margin</strong></td>\n#;
  print qq#</tr>\n#;

  foreach $Pharmacy_ID (@NCPDPSArray) {
     $NCPDP = $Pharmacy_NCPDPs{$Pharmacy_ID};
     $RepKey = "$NCPDP##$ReportWeek";
   
     $Rep_MWType        = $Rep_MWType{$RepKey};
     $Rep_NCPDP         = $Rep_NCPDP{$RepKey};
     $Rep_Pharmacy_Name = $Pharmacy_Names{$Pharmacy_ID};
     $PharmacyName      = "$Rep_Pharmacy_Name";
     $PharmacyName     .= "<br>$NCPDP";
     $Rep_Date          = $Rep_Date{$RepKey};
     $Rep_Scripts       = $Rep_Scripts{$RepKey};
     $Rep_Revenue       = $Rep_Revenue{$RepKey};
     $Rep_Cost          = $Rep_Cost{$RepKey};
   
     $Rep_Gross_Margin     = $Rep_Revenue - $Rep_Cost;

     if ( $Rep_Revenue == 0 || $Rep_Revenue =~ /^\s*$/ ) {
        $Rep_PCT_Gross_Margin = 0;
     } else {
        $Rep_PCT_Gross_Margin = $Rep_Gross_Margin / $Rep_Revenue;
     }
   
     $Rep_Total_Scripts          += $Rep_Scripts;
     $Rep_Total_Revenue          += $Rep_Revenue;
     $Rep_Total_Gross_Margin     += $Rep_Gross_Margin;

     ($ORep_Scripts)              = &commify($Rep_Scripts);
     ($ORep_Revenue)              = &dolout($Rep_Revenue);
     ($ORep_Gross_Margin)         = &dolout($Rep_Gross_Margin);
     ($ORep_PCT_Gross_Margin)     = &pctout($Rep_PCT_Gross_Margin);
   
     print qq#<tr>\n#;
#    print qq#<td><strong>$Rep_Pharmacy_Name</strong></td>\n#;
     print qq#<td><strong>$PharmacyName</strong></td>\n#;
     print qq#<td class="right">$ORep_Scripts         </td>\n#;
     print qq#<td class="right">$ORep_Revenue         </td>\n#;
     print qq#<td class="right">$ORep_Gross_Margin    </td>\n#;
     print qq#<td class="right">$ORep_PCT_Gross_Margin</td>\n#;
     print qq#</tr>\n#;
  }

  $Rep_Total_PCT_Gross_Margin = $Rep_Total_Gross_Margin / $Rep_Total_Revenue;

  ($ORep_Total_Scripts)          = &commify($Rep_Total_Scripts);
  ($ORep_Total_Revenue)          = &dolout($Rep_Total_Revenue);
  ($ORep_Total_Gross_Margin)     = &dolout($Rep_Total_Gross_Margin);
  ($ORep_Total_PCT_Gross_Margin) = &pctout($Rep_Total_PCT_Gross_Margin);

  print qq#<tr>\n#;
  print qq#<td>Total</td>\n#;
  print qq#<td class="right">$ORep_Total_Scripts    </td>\n#;
  print qq#<td class="right">$ORep_Total_Revenue         </td>\n#;
  print qq#<td class="right">$ORep_Total_Gross_Margin    </td>\n#;
  print qq#<td class="right">$ORep_Total_PCT_Gross_Margin</td>\n#;
  print qq#</tr>\n#;

  print "<tr><td colspan=5>$nbsp</td></tr>\n";

# ----------------------
 
  print "<tr><th colspan=5>YTD Totals</th></tr>\n";
  print qq#<tr>\n#;
  print qq#<td width="25%">$nbsp     </td>\n#;
  print qq#<td class="right"><strong>Scripts       </strong></td>\n#;
  print qq#<td class="right"><strong>Revenue       </strong></td>\n#;
  print qq#<td width="20%" class="right"><strong>Gross Margin  </strong></td>\n#;
  print qq#<td class="right"><strong>% Gross Margin</strong></td>\n#;
  print qq#</tr>\n#;

  my $Rep_YTD_Scripts  = 0;
  my $Rep_YTD_Revenue  = 0;
  my $Rep_YTD_Cost     = 0;
  my $Rep_Num_of_Weeks = 0;

  foreach $Pharmacy_ID (@NCPDPSArray) {
     $NCPDP = $Pharmacy_NCPDPs{$Pharmacy_ID};

     $Rep_YTD_Scripts  = 0;
     $Rep_YTD_Revenue  = 0;
     $Rep_YTD_Cost     = 0;
     $Rep_Num_of_Weeks = 0;

     foreach $RepKey ( sort {$Rep_Date{$a} cmp $Rep_Date{$b} } keys %Rep_Date) {
       next if ( $RepKey !~ /^$NCPDP/ );

#      next if ( $Rep_Date{$RepKey} !~ /$yearcur/ );
   
       $Rep_YTD_Scripts       += $Rep_Scripts{$RepKey};
       $Rep_YTD_Revenue       += $Rep_Revenue{$RepKey};
       $Rep_YTD_Cost          += $Rep_Cost{$RepKey};
       $Rep_Num_of_Weeks++ if ( $Rep_Scripts{$RepKey} > 0 );
   
   #   print "$RepKey- Rep_Scripts(): $Rep_Scripts{$RepKey}, Rep_Num_of_Weeks: $Rep_Num_of_Weeks<br>\n";
     }
     $Rep_Pharmacy_Name = $Pharmacy_Names{$Pharmacy_ID};
     $PharmacyName      = "$Rep_Pharmacy_Name";
     $PharmacyName     .= "<br>$NCPDP";
   
     $Rep_YTD_Gross_Margin     = int($Rep_YTD_Revenue - $Rep_YTD_Cost);
     if ( $Rep_YTD_Revenue == 0 || $Rep_YTD_Revenue =~ /^\s*$/ ) {
        $Rep_YTD_PCT_Gross_Margin = 0;
     } else {
        $Rep_YTD_PCT_Gross_Margin = $Rep_YTD_Gross_Margin / $Rep_YTD_Revenue;
     }
    
     $Rep_YTD_Total_Scripts          += $Rep_YTD_Scripts;
     $Rep_YTD_Total_Revenue          += $Rep_YTD_Revenue;
     $Rep_YTD_Total_Gross_Margin     += $Rep_YTD_Gross_Margin;
   
     ($ORep_YTD_Scripts)                = &commify($Rep_YTD_Scripts);
     ($ORep_YTD_Revenue)                = &bigdolout($Rep_YTD_Revenue);
     ($ORep_YTD_Gross_Margin)           = &bigdolout($Rep_YTD_Gross_Margin);
     ($ORep_YTD_PCT_Gross_Margin)       = &pctout($Rep_YTD_PCT_Gross_Margin);
  
     print qq#<tr>\n#;
#    print qq#<td><strong>$Rep_Pharmacy_Name</strong></td>\n#;
     print qq#<td><strong>$PharmacyName</strong></td>\n#;
     print qq#<td class="right">$ORep_YTD_Scripts         </td>\n#;
     print qq#<td class="right">$ORep_YTD_Revenue         </td>\n#;
     print qq#<td class="right">$ORep_YTD_Gross_Margin    </td>\n#;
     print qq#<td class="right">$ORep_YTD_PCT_Gross_Margin</td>\n#;
     print qq#</tr>\n#;
  }

  ($ORep_YTD_Total_Scripts)          = &commify($Rep_YTD_Total_Scripts);
# print "$RepKey: Rep_YTD_Total_Revenue: $Rep_YTD_Total_Revenue<br>\n";
  ($ORep_YTD_Total_Revenue)          = &bigdolout($Rep_YTD_Total_Revenue);
  ($ORep_YTD_Total_Gross_Margin)     = &bigdolout($Rep_YTD_Total_Gross_Margin);
  ($ORep_YTD_Total_PCT_Gross_Margin) = &pctout($Rep_YTD_Total_Gross_Margin / $Rep_YTD_Total_Revenue);

  print qq#<tr>\n#;
  print qq#<td>Total</td>\n#;
  print qq#<td class="right">$ORep_YTD_Total_Scripts         </td>\n#;
  print qq#<td class="right">$ORep_YTD_Total_Revenue         </td>\n#;
  print qq#<td class="right">$ORep_YTD_Total_Gross_Margin    </td>\n#;
  print qq#<td class="right">$ORep_YTD_Total_PCT_Gross_Margin</td>\n#;
  print qq#</tr>\n#;

# ----------------------

  print "<tr><td colspan=5>$nbsp</td></tr>\n";
  print "<tr><th colspan=5>YTD Weekly Average</th></tr>\n";

  print qq#<tr>\n#;
  print qq#<td width="25%">$nbsp         </td>\n#;
  print qq#<td class="right"><strong>Scripts       </strong></td>\n#;
  print qq#<td class="right"><strong>Revenue       </strong></td>\n#;
  print qq#<td width="20%" class="right"><strong>Gross Margin  </strong></td>\n#;
  print qq#<td class="right"><strong>% Gross Margin</strong></td>\n#;
  print qq#</tr>\n#;

  foreach $Pharmacy_ID (@NCPDPSArray) {
     $NCPDP = $Pharmacy_NCPDPs{$Pharmacy_ID};
     $RepKey = "$NCPDP##$ReportWeek";

     $Rep_Pharmacy_Name = $Pharmacy_Names{$Pharmacy_ID};
     $PharmacyName      = "$Rep_Pharmacy_Name";
     $PharmacyName     .= "<br>$NCPDP";

     $Rep_YTD_Scripts  = 0;
     $Rep_YTD_Revenue  = 0;
     $Rep_YTD_Cost     = 0;
     $Rep_Num_of_Weeks = 0;

     foreach $RepKey ( sort {$Rep_Date{$a} cmp $Rep_Date{$b} } keys %Rep_Date) {
       next if ( $RepKey !~ /^$NCPDP/ );

#      next if ( $Rep_Date{$RepKey} !~ /$yearcur/ );
   
       $Rep_YTD_Scripts       += $Rep_Scripts{$RepKey};
       $Rep_YTD_Revenue       += $Rep_Revenue{$RepKey};
       $Rep_YTD_Cost          += $Rep_Cost{$RepKey};
       $Rep_Num_of_Weeks++ if ( $Rep_Scripts{$RepKey} > 0 );
    }

#   print "Rep_Num_of_Weeks: $Rep_Num_of_Weeks<br>\n";
    if ( $Rep_Num_of_Weeks == 0 || $Rep_Num_of_Weeks =~ /^\s*$/ ) {
      $Rep_YTD_AVG_Scripts          = 0;
      $Rep_YTD_AVG_Revenue          = 0;
      $Rep_YTD_AVG_Gross_Margin     = 0;
      $Rep_YTD_AVG_PCT_Gross_Margin = 0;
    } else {
      $Rep_YTD_AVG_Scripts          = int($Rep_YTD_Scripts / $Rep_Num_of_Weeks);
      $Rep_YTD_AVG_Revenue          = int($Rep_YTD_Revenue / $Rep_Num_of_Weeks);
      $Rep_YTD_AVG_Gross_Margin     = int(($Rep_YTD_Revenue - $Rep_YTD_Cost) / $Rep_Num_of_Weeks);
      $Rep_YTD_AVG_PCT_Gross_Margin = $Rep_YTD_AVG_Gross_Margin / $Rep_YTD_AVG_Revenue;
    }

    $jRep_YTD_Revenue{$NCPDP} = $Rep_YTD_Revenue;
    $jRep_YTD_Scripts{$NCPDP} = $Rep_YTD_Scripts;
    $jRep_YTD_Cost{$NCPDP}    = $Rep_YTD_Cost;
     
    ($ORep_YTD_AVG_Scripts)                = &bignumout($Rep_YTD_AVG_Scripts);
    ($ORep_YTD_AVG_Revenue)                = &bigdolout($Rep_YTD_AVG_Revenue);
    ($ORep_YTD_AVG_Gross_Margin)           = &bigdolout($Rep_YTD_AVG_Gross_Margin);
    ($ORep_YTD_AVG_PCT_Gross_Margin)       = &pctout($Rep_YTD_AVG_PCT_Gross_Margin);

    print qq#<tr>\n#;
#   print qq#<td><strong>$Rep_Pharmacy_Name</strong></td>\n#;
    print qq#<td><strong>$PharmacyName</strong></td>\n#;
    print qq#<td class="right">$ORep_YTD_AVG_Scripts         </td>\n#;
    print qq#<td class="right">$ORep_YTD_AVG_Revenue         </td>\n#;
    print qq#<td class="right">$ORep_YTD_AVG_Gross_Margin    </td>\n#;
    print qq#<td class="right">$ORep_YTD_AVG_PCT_Gross_Margin</td>\n#;
    print qq#</tr>\n#;

    $Rep_YTD_AVG_Total_Scripts          += $Rep_YTD_AVG_Scripts;
    $Rep_YTD_AVG_Total_Revenue          += $Rep_YTD_AVG_Revenue;
    $Rep_YTD_AVG_Total_Gross_Margin     += $Rep_YTD_AVG_Gross_Margin;
  }
  $Rep_YTD_AVG_Total_PCT_Gross_Margin = $Rep_YTD_AVG_Total_Gross_Margin / $Rep_YTD_AVG_Total_Revenue;

  ($ORep_YTD_AVG_Total_Scripts)          = &bignumout($Rep_YTD_AVG_Total_Scripts);
  ($ORep_YTD_AVG_Total_Revenue)          = &bigdolout($Rep_YTD_AVG_Total_Revenue);
  ($ORep_YTD_AVG_Total_Gross_Margin)     = &bigdolout($Rep_YTD_AVG_Total_Gross_Margin);
  ($ORep_YTD_AVG_Total_PCT_Gross_Margin) = &pctout($Rep_YTD_AVG_Total_PCT_Gross_Margin);

  print qq#<tr>\n#;
  print qq#<td>Total</td>\n#;
  print qq#<td class="right">$ORep_YTD_AVG_Total_Scripts         </td>\n#;
  print qq#<td class="right">$ORep_YTD_AVG_Total_Revenue         </td>\n#;
  print qq#<td class="right">$ORep_YTD_AVG_Total_Gross_Margin    </td>\n#;
  print qq#<td class="right">$ORep_YTD_AVG_Total_PCT_Gross_Margin</td>\n#;
  print qq#</tr>\n#;
# ----------------------

  print "</table>\n";
# print "Rep_YTD_Scripts: $Rep_YTD_Scripts<br>\n";

  print qq#<br>\n#;

# ----------------------

  print qq#<table class="reports-table">\n#;
  print qq#<tr>\n#;
  print qq#<td width="25%">$nbsp</td>\n#;
  print qq#<td class="right"><strong>Average Sale per Script</strong></td>\n#;
  print qq#<td class="right"><strong>Average GM per Script</strong></td>\n#;
  print qq#</tr>\n#;

  foreach $Pharmacy_ID (@NCPDPSArray) {
     $NCPDP = $Pharmacy_NCPDPs{$Pharmacy_ID};
     $Rep_Pharmacy_Name = $Pharmacy_Names{$Pharmacy_ID};
     $PharmacyName      = "$Rep_Pharmacy_Name";
     $PharmacyName     .= "<br>$NCPDP";
     $Rep_YTD_Revenue   = $jRep_YTD_Revenue{$NCPDP};
     $Rep_YTD_Scripts   = $jRep_YTD_Scripts{$NCPDP};
     $Rep_YTD_Cost      = $jRep_YTD_Cost{$NCPDP};
     $Rep_YTD_Gross_Margin = $Rep_YTD_Revenue - $Rep_YTD_Cost;

     if ( $Rep_YTD_Scripts == 0 || $Rep_YTD_Scripts =~ /^\s*$/ ) {
        $AVG_sale_per_Script       = 0;
        $AVG_GM_per_Script         = 0;
        ($OAVG_sale_per_Script)    = 0;
        ($OAVG_GM_per_Script)      = 0;
     } else {
        $AVG_sale_per_Script       = $Rep_YTD_Revenue      / $Rep_YTD_Scripts;
        $AVG_GM_per_Script         = $Rep_YTD_Gross_Margin / $Rep_YTD_Scripts;
        ($OAVG_sale_per_Script)    = &dolout($AVG_sale_per_Script);
        ($OAVG_GM_per_Script)      = &dolout($AVG_GM_per_Script);
     }

     print qq#<tr>\n#;
#    print qq#<td><strong>$Rep_Pharmacy_Name</strong></td>\n#;
     print qq#<td><strong>$PharmacyName</strong></td>\n#;
     print qq#<td class="right">$OAVG_sale_per_Script</td>\n#;
     print qq#<td class="right">$OAVG_GM_per_Script</td>\n#;
     print qq#</tr>\n#;

     $Total_Rep_YTD_Revenue += $Rep_YTD_Revenue;
     $Total_Rep_YTD_Scripts += $Rep_YTD_Scripts;
     $Total_Rep_YTD_Cost    += $Rep_YTD_Cost;
  }

  $Total_Rep_YTD_Gross_Margin   = $Total_Rep_YTD_Revenue - $Total_Rep_YTD_Cost;
  $Total_AVG_sale_per_Script    = $Total_Rep_YTD_Revenue      / $Total_Rep_YTD_Scripts;
  $Total_AVG_GM_per_Script      = $Total_Rep_YTD_Gross_Margin / $Total_Rep_YTD_Scripts;

  ($OTotal_AVG_sale_per_Script) = &dolout($Total_AVG_sale_per_Script);
  ($OTotal_AVG_GM_per_Script)   = &dolout($Total_AVG_GM_per_Script);

  print qq#<tr>\n#;
  print qq#<td><strong>Overall</strong></td>\n#;
# print qq#<td><strong>Overall<br>(#, &commify($Total_Rep_YTD_Scripts), qq# Total Scripts)</strong></td>\n#;
  print qq#<td class="right">$OTotal_AVG_sale_per_Script</td>\n#;
  print qq#<td class="right">$OTotal_AVG_GM_per_Script</td>\n#;
  print qq#</tr>\n#;

  print "</table>\n";
  
  print "<center><p>*Gross Modifier Not Included*</p></center>";
  
  #print "<br>\n";

 
# ----------------------

  print qq#</div><!-- end wrapper -->\n#;
}

#______________________________________________________________________________
 
sub readWeeklyData {
  my ($ReportWeek_Year, $ReportWeek_Month, $ReportWeek_Day) = split("-", $ReportWeek, 3);

  my $PHCOUNT =  0;
  my $NCPDPS  = "";

  if ( $TYPE =~ /SuperUser|Admin/i && !$PH_ID) {
     ($PHCOUNT, $NCPDPS) = &find_NCPDPS_Owner($USER);
  } else {
     $PHCOUNT = 1;
#     $NCPDPS = $Pharmacy_NCPDPs{$PH_ID};
     $NCPDPS = $PH_ID;
#     push(@NCPDPSArray, $PH_ID);
  }

  # open RBSReporting DB, read Weekly data
  
  $LATESTDATE = 0;
  my $sql = "";

  $TABLE = $TABLERW;
  $sql  = "SELECT Pharmacy_Name, NCPDP, Date, Total_Scripts, Total_Revenue, Total_Cost, Pharmacy_ID ";
  $sql .= "FROM $DBNAME.$TABLE ";
  $sql .= "WHERE ";
  $sql .= " Pharmacy_ID IN ($NCPDPS) && " if ($NCPDPS !~ /ALL/i );
  $sql .= " DATE >= '${ReportWeek_Year}-01-01' && DATE <= '$ReportWeek' ";
  $sql .= "ORDER BY Pharmacy_Name, NCPDP, Date DESC";

  $sthx  = $dbRW->prepare("$sql");
  $sthx->execute;

  my $NumOfRows = $sthx->rows;
  $PHCOUNT = $NumOfRows;
  my $Pharmacy_ID_sav = '';

  if ( $NumOfRows > 0 ) {
    while ( my ($Pharmacy_Name, $NCPDP, $Date, $Total_Scripts, $Total_Revenue, $Total_Cost, $Pharmacy_ID) = $sthx->fetchrow_array() ) {
       next if ($Pharmacy_Status_RBSs{$Pharmacy_ID} =~ /^Inactive/i );
  
       $NCPDP = sprintf("%07d", $NCPDP);
#       push(@NCPDPSArray, $NCPDP);
##       push(@NCPDPSArray, $Pharmacy_ID) if ($Pharmacy_ID != $Pharmacy_ID_sav);

       $RepKey               = "$NCPDP##$Date";
       $Rep_MWType{$RepKey}  = "Week";
       $Rep_NCPDP{$RepKey}   = substr("00000000" . $NCPDP, -7);
       $Rep_Date{$RepKey}    = $Date;
       $Rep_Scripts{$RepKey} = $Total_Scripts;
       $Rep_Revenue{$RepKey} = $Total_Revenue;
       $Rep_Cost{$RepKey}    = $Total_Cost;
  
       $Rep_Pharmacy_Name{$RepKey} = $Pharmacy_Names{$Pharmacy_ID} || $Pharmacy_Name;
  
       $Pharmacy_ID_sav = $Pharmacy_ID;
       $LATESTDATE = $Date if ( !$LATESTDATE );
    }
  } else {
    $PHCOUNT = -1;
  }
  $sthx->finish;
  
  return($PHCOUNT);
}

#______________________________________________________________________________

sub dolout {
  my ($in) = @_;
  $out = "\$" . &commify(sprintf("%0.2f", $in));
  return($out);
}

#______________________________________________________________________________

sub bigdolout {
  my ($in) = @_;
  $out = "\$" . &commify(sprintf("%0.0f", $in));
  return($out);
}

#______________________________________________________________________________

sub numout {
  my ($in) = @_;
  $out = &commify(sprintf("%0.2f", $in));
  return($out);
}

#______________________________________________________________________________

sub bignumout {
  my ($in) = @_;
  $out = &commify(sprintf("%0.0f", $in));
  return($out);
}
#______________________________________________________________________________

sub pctout {
  my ($in) = @_;
  $out = sprintf("%0.2f \%", $in * 100);
  return($out);
}
#______________________________________________________________________________

sub find_NCPDPS_Owner {
  my ($OWNER)   = @_;
  my $NCPDPS  = '';
  my $PHCOUNT =  0;

  my $DBNAME  = 'Officedb';
  my $TABLE   = 'weblogin_dtl';

  my $sql = "SELECT Pharmacy_ID
               FROM $DBNAME.$TABLE
              WHERE login_id = $OWNER";

  $sthx  = $dbRW->prepare("$sql");
  $sthx->execute;

  my $NumOfRows = $sthx->rows;

  while ( my ($Pharmacy_ID) = $sthx->fetchrow_array() ) {
     if ( $Pharmacy_ID == 0 ) {
        $NCPDPS .= "ALL, ";
     } else {
       ## push(@NCPDPSArray, $Pharmacy_ID);
       push(@NCPDPSArray, $Pharmacy_ID) if ($Pharmacy_ID != $Pharmacy_ID_sav);
        $NCPDPS .= "$Pharmacy_ID, ";
        $PHCOUNT++;
     }
  }

  $NCPDPS =~ s/,\s*$//;
  $sthx->finish;

  return ($PHCOUNT, $NCPDPS);
}
#______________________________________________________________________________

sub displayNoDataFound {
  # Read in canned file, use variables to fill in "<%var%>" values

  my $FILE = "RBSReportingNoData.html";
  my ($message, @array) = &read_canned_file($FILE);
  foreach $line (@array) {
     print "$line\n";
  }
}

#______________________________________________________________________________
