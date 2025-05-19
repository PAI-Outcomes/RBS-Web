
require "D:/RedeemRx/MyData/RBSDesktop_routines.pl";
require "D:/RedeemRx/cgi-bin/cgi-lib.pl";
require "D:/RedeemRx/MyData/RBSReporting_routines.pl";

use File::Basename;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use Env qw(PATH REMOTE_ADDR PERL5LIB PERLLIB);
use Math::Round;
use Data::Dumper qw(Dumper);

$| = 1; # don't buffer output
#______________________________________________________________________________
#
my ($prog, $dir, $ext) = fileparse($0, '\..*');
$nbsp = "&nbsp\;";

$BeyondRx = 610641;

$ret = &ReadParse(*in);

# A bit of error checking never hurt anyone
&CgiDie("Error in reading and parsing of CGI input") if !defined $ret;

$RTYPE        = 'Monthly';
$Submit       = $in{'Submit'};
$ReportMonth  = '2020-02-01';
#$PH_ID = 1215;
$PH_ID = 1734;

($ReportMonth)= &StripJunk($ReportMonth);

if ( $Submit =~ /Friendly/i ) {
   $printonly++;
} else {
   $printonly = 0;
}

&readsetCookies;

if ( $printonly ) {
   &MyPharmassessReportingMonthlyHeaderPrint;
} else {
   &MyPharmassessReportingMonthlyHeader;
   &MembersHeaderBlock;
}

&readPharmacies;
$inNCPDP = $Pharmacy_NCPDPs{$PH_ID};

# Create the inputfile format name
my ($min, $hour, $day, $month, $year) = (localtime)[1,2,3,4,5];
$year  += 1900;	# reported as "years since 1900".

$ThisReportRepKey = "$PH_ID##$ReportMonth";

($jyear, $jmonth, $jday) = split("-", $ReportMonth, 3);
$inYear  = $jyear;
$inMonth = $jmonth;
$doMonth = sprintf("%04d%02d", $inYear, $inMonth);
$year2   = $inyear - 2 ."01";

$yearcur = $jyear;
$yearm1  = $jyear - 1;
$yearm2  = $jyear - 2;
$ymc     = $jyear;
$ym1     = $yearm1;
$ym2     = $yearm2;

$jqtr = 0;
if ($jmonth ==  3) { $jqtr = 1; }
if ($jmonth ==  6) { $jqtr = 2; }
if ($jmonth ==  9) { $jqtr = 3; }
if ($jmonth == 12) { $jqtr = 4; }

#______________________________________________________________________________

#($isMember, $VALID) = &isMember($USER, $PASS);

#if ($USER) {
#} else {
#   &MembersLogin;
#   print qq#</BODY>\n#;
#   print qq#</HTML>\n#;
#   exit(0);
#}

$dbinRM    = "RMDBNAME";	# RBS Reporting Monthly data
$DBNAMERM  = $DBNAMES{"$dbinRM"};
$TABLERM   = $DBTABN{"$dbinRM"};

$dbinRB    = "RBDBNAME";	# RBS Reporting Weekly data
$DBNAMERB  = $DBNAMES{"$dbinRB"};
$TABLERB   = $DBTABN{"$dbinRB"};

# connect to the RBS Reporting Database (with two tables, monthly & weekly)

%attr = ( PrintWarn=>1, RaiseError=>1, PrintError=>1, AutoCommit=>1, InactiveDestroy=>0, HandleError => \&handle_error );
$dbx = DBI->connect("DBI:mysql:$DBNAMERM:$DBHOST",$dbuser,$dbpwd, \%attr) || &handle_error;
   
$progext = "${prog}${ext}";
%Jay_LTCs= ();
$Pharmacy_ID = $PH_ID;

&readRebates;	# Must be read in before 'readMonthlyData' !!!!
&readMonthlyData;

#if ($jmonth =~ /3|6|9|12/) {
#  &readSummaries;
#}

$Pharmacy_Name = $Pharmacy_Names{$PH_ID};

print qq#<script src="js/highcharts.js"></script>\n#; #MOVE TO CANNED FILE
 
($LDOM)  = &LastDayOfMonth($inYear, $inMonth);
$DateRangeStart = sprintf("%04d%02d%02d", $jyear, $jmonth, 1);
$DateRangeEnd   = sprintf("%04d%02d%02d", $jyear, $jmonth, $LDOM);

$PharmacyWanted   = $inNCPDP;
$Detail           = 'YRBS'; #Claim Detail Data - RBS Database
$RebateBrand      =  0;     #Rebate factored later.
$RebateGeneric    =  0;     #Rebate factored later.
$NPIstring        = '';     #No NPI string.
$ExcBINstring     = '';     #No BIN exclusion string.
#$CASHBINS         = '';
#%BINSfound        = ();
#%RedeemRxBINS     = ();
  
# -----------------------------------------------------------------------------

$CSfmt      = "%0.1f\%";
$CSdolfmt   = "\$%0.2f";
%CSC        = ();
%CSCDollars = ();

#if ( $printonly == 0 ) {
#   &displayComments;
#}

print qq#<div id="wrapper">\n#;

#&displayReportHeaderNEW;
#&displayScriptCount;

#-------------------------------------------------------------------------------
# Controlled Substance charts
# jlh. 10/01/2015. Added per Monty conversation with me and Alborz

#if ($yearcur >= 2015) {
#  &displayBGUtilization;
#}

#  &displayClaimInfo; #New vs. Refill Claims
#  &displayScriptCountStacked;

#&displaySales;

#&displayScriptSalesStacked;

#&displayAverageSalePerScript;

#&displayPatientInfo;
&displayMedSync;

#&SalesByPayer;

#&getControlledSubstanceTotals;

if ( $doCS ) {
##  my $section_title = "Controlled Substances - $Pharmacy_Name";
##  print qq#<div class="page">\n#;
##  print qq#<div class="page_header"><h3>$section_title</h3></div>\n#;

#   &displayControlledSubstanceClaims_ALL;
##   &displayControlledSubstanceDollars_ALL;
#   &displayControlledSubstanceUnits_ALL;
#   &displayControlledSubstanceClaims_CASH;
#   &displayControlledSubstanceDollars_CASH;
#   &displayControlledSubstanceUnits_CASH;

  print qq#<div style="clear:both"></div>\n#;  
  print qq#</div> <!-- end page -->\n#;
##} else {
##   print qq#<h3>No Controlled Substances data found for this pharmacy.</h3>\n#;
}


print qq#</div><!-- end wrapper -->\n#;

# Close the Database
$dbx->disconnect;

if ( $printonly ) {
   &MyPharmassessReportingTrailerPrint;
} else {
   &MyPharmassessReportingTrailerPrint;
}

exit(0);

#______________________________________________________________________________

sub displayReportHeader {

  my @pcs = split("-", $ReportMonth, 3);
  $pcs[1] += 0;
  $ReportMonthDisplay = "$MONTHS{$pcs[1]} $pcs[0]";

  print qq#<table class="header">\n#;
  print qq#<tr>\n#;
  print qq#<td class="logo"><img src="/images/PharmAssess_Logo_Main1-1024x212.png" style="width: 100%; max-width: 400px;"></td>\n#;
  print qq#<td>$TYPE Report<br>$ReportMonthDisplay</td>\n#;
  print qq#<td>$Pharmacy_Name_Global</td>\n#;

  print qq#<td class="noprint">\n#;
  $URLH = "$progext";
  print qq#<FORM ACTION="$URLH" METHOD="POST">\n#;
  print qq#<INPUT TYPE="hidden" NAME="ReportMonth" VALUE="$ReportMonth">\n#;
  print qq#<INPUT TYPE="Submit" NAME="Submit" VALUE="Printer Friendly View">\n#;
  print qq#\n</FORM>\n#;

  print qq#</td>\n#;
  print qq#</tr>\n#;
  print qq#</table>\n#;
  
  if ( $disclaimer ) {
     print qq#<div class="summary" style="text-align: center;">$disclaimer</div>\n#;
  }
}

sub displayReportHeaderNEW {
  my @pcs = split("-", $ReportMonth, 3);
  $pcs[1] += 0;
  $ReportMonthDisplay = "$MONTHS{$pcs[1]} $pcs[0]";

  print qq#<h1 class="rbsreporting">$TYPE Report - $ReportMonthDisplay</h1>\n#;

  print qq#<td class="noprint">\n#;
  $URLH = "$progext";
  print qq#<FORM ACTION="$URLH" METHOD="POST">\n#;
  print qq#<INPUT TYPE="hidden" NAME="ReportMonth" VALUE="$ReportMonth">\n#;
  print qq#<INPUT TYPE="Submit" NAME="Submit" VALUE="Printer Friendly View">\n#;
  print qq#\n</FORM>\n#;
}

#______________________________________________________________________________

sub displayScriptCount {
  
  ### Build Data Hashes ### -------------------------------------------------------------
  my %Data_Script_Count_Brand   = ();
  my %Data_Script_Count_Generic = ();
  my %Data_Script_Count_Total   = ();
  
  for (my $lyear=$yearm2; $lyear<=$yearcur; $lyear++) {
    for (my $lmonth=1; $lmonth<=12; $lmonth++) {

      next if ($lyear >= $yearcur && $lmonth > $jmonth);
    
      $lmonth = sprintf("%02d", $lmonth);
      
      my $RepKey = "$inNCPDP##$lyear-$lmonth-01"; #Build key to retrieve data
      my $DataLoadKey = "$lyear##$lmonth";        #Build key to send data to graph
    
      my $Brand_Scripts   = $Rep_Total_Brand{$RepKey} || 0;
      my $Generic_Scripts = $Rep_Total_Generic{$RepKey} || 0;
      my $Total_Scripts   = ($Brand_Scripts + $Generic_Scripts) || 0;
      
      #Check data for blanks, replace with 'null' for graph display
      if ($Brand_Scripts =~ /^\s*$/ || $Brand_Scripts <= 0) {
        $Brand_Scripts = "null";
      }
      if ($Generic_Scripts =~ /^\s*$/ || $Generic_Scripts <= 0) {
        $Generic_Scripts = "null";
      }
      if ($Total_Scripts =~ /^\s*$/ || $Total_Scripts <= 0) {
        $Total_Scripts = "null";
      }
      
      $Data_Script_Count_Brand{$DataLoadKey}   = $Brand_Scripts;
      $Data_Script_Count_Generic{$DataLoadKey} = $Generic_Scripts;
      $Data_Script_Count_Total{$DataLoadKey}   = $Total_Scripts;

    }
  }

  my $section_title = "Script Count - $Pharmacy_Name";
  print qq#<div class="page">\n#;
  print qq#<div class="page_header"><h3>$section_title</h3></div>\n#;
  
  ### Start Main Graph ### ---------------------------------------------------------------
  $decimalplaces = 0;
  $rotation      = 0;
  $container     = "ID_Total_Script_Count";
  $type          = "Total Script Count";
  $yaxistitle    = "Count Per Month";
  $class         = "mainchart";
  $marginright   = "110";
  $legend        = "true";
  %data = %Data_Script_Count_Total;
  &build_mainchart;
  print qq#<div id="$container" class="$class"></div>\n#;
  print qq#<div style="clear:both"></div>\n#;
  ### End Graph ### ---------------------------------------------------------------------
  
  ### Start Small Left Graph ### ---------------------------------------------------------------
  $decimalplaces = 0;
  $rotation      = -75;
  $container     = "ID_Total_Script_Count_Brand";
  $type          = "Brand";
  $yaxistitle    = "Count Per Month";
  $class         = "chartsmall_left";
  $marginright   = "30";
  $legend        = "false";
  %data          = %Data_Script_Count_Brand;
  &build_mainchart;
  print qq#<div style="width: 50%; float: left;"><div id="$container" class="$class"></div></div>\n#;
  ### End Graph ### ---------------------------------------------------------------------
  
  ### Start Small Right Graph ### ---------------------------------------------------------------
  $decimalplaces = 0;
  $rotation      = -75;
  $container     = "ID_Total_Script_Count_Generic";
  $type          = "Generic";
  $yaxistitle    = "Count Per Month";
  $class         = "chartsmall_left";
  $marginright   = "30";
  $legend        = "false";
  %data          = %Data_Script_Count_Generic;
  &build_mainchart;
  print qq#<div style="width: 50%; float: right;"><div id="$container" class="$class"></div></div>\n#;
  ### End Graph ### ---------------------------------------------------------------------
  
  print qq#<div style="clear:both"></div>\n#;  
  print qq#</div> <!-- end page -->\n#;
  
}

#______________________________________________________________________________

sub displayScriptCountStacked {
  ### Build Data Hashes ### -------------------------------------------------------------  
  my %Data_YTD_Script_Count_Total = ();
  
  for (my $lyear=$yearm2; $lyear<=$yearcur; $lyear++) {
    my $DataLoadKey = "$lyear";      #Build key to send data to graph
    my $RepKey = "$lyear"; #Build key to retrieve data
    my $Brand_Scripts_YTD           = 0;
    my $Generic_Scripts_YTD         = 0;
    my $Total_Scripts_YTD           = 0;

    for (my $lmonth=1; $lmonth<=$inMonth; $lmonth++) {
      my $rmonth = sprintf("%02d", $lmonth);
      my $YTDRepKey = "$inNCPDP##${lyear}-${rmonth}-01"; #Build key to retrieve data

      $Brand_Scripts_YTD           += $Rep_Total_Brand{$YTDRepKey} || 0;
      $Generic_Scripts_YTD         += $Rep_Total_Generic{$YTDRepKey} || 0;
      $Total_Scripts_YTD           += ($Rep_Total_Brand{$YTDRepKey} + $Rep_Total_Generic{$YTDRepKey}) || 0;
    }

    my $Brand_Scripts   = $Rep_Total_Brand{$RepKey} || 0;
    my $Generic_Scripts = $Rep_Total_Generic{$RepKey} || 0;
    my $Total_Scripts   = ($Brand_Scripts + $Generic_Scripts) || 0;

    my $Brand_Scripts_RM   = $Brand_Scripts - $Brand_Scripts_YTD;
    my $Generic_Scripts_RM = $Generic_Scripts - $Generic_Scripts_YTD;
    my $Total_Scripts_RM   = $Total_Scripts - $Total_Scripts_YTD;

    #Check data for blanks, replace with 'null' for graph display
    if ($Brand_Scripts =~ /^\s*$/ || $Brand_Scripts <= 0) {
      $Brand_Scripts = "null";
    }
    if ($Generic_Scripts =~ /^\s*$/ || $Generic_Scripts <= 0) {
      $Generic_Scripts = "null";
    }
    if ($Total_Scripts =~ /^\s*$/ || $Total_Scripts <= 0) {
      $Total_Scripts = "null";
    }

    if ($Brand_Scripts_RM =~ /^\s*$/ || $Brand_Scripts_RM <= 0) {
      $Brand_Scripts_RM = "null";
    }
    if ($Generic_Scripts_RM =~ /^\s*$/ || $Generic_Scripts_RM <= 0) {
      $Generic_Scripts_RM = "null";
    }
    if ($Total_Scripts_RM =~ /^\s*$/ || $Total_Scripts_RM <= 0) {
      $Total_Scripts_RM = "null";
    }
      
    #Load data to hashes with appropriate key for graph display
    $Data_YTD_Script_Count_Brand{"${DataLoadKey}##R"} = $Brand_Scripts_RM;
    $Data_YTD_Script_Count_Generic{"${DataLoadKey}##R"} = $Generic_Scripts_RM;
    $Data_YTD_Script_Count_Total{"${DataLoadKey}##R"} = $Total_Scripts_RM;
    $Data_YTD_Script_Count_Brand{"${DataLoadKey}##T"} = $Brand_Scripts_YTD;
    $Data_YTD_Script_Count_Generic{"${DataLoadKey}##T"} = $Generic_Scripts_YTD;
    $Data_YTD_Script_Count_Total{"${DataLoadKey}##T"} = $Total_Scripts_YTD;
  }
  ### End Data Hashes ### ---------------------------------------------------------------

  $section_title = "Script Information YTD - $Pharmacy_Name";
  print qq#<div class="page">\n#;
  print qq#<div class="page_header"><h3>$section_title</h3></div>\n#;
  
  ### Start Main Graph ### ---------------------------------------------------------------
  $decimalplaces = 0;
  $rotation      = 0;
  $container     = "ID_Total_Script_Count_YTD";
  $type          = "Total Script Count YTD";
  $yaxistitle    = "";
  $class         = "mainchart";
  $marginright   = "110";
  $legend        = "true";
  %data = %Data_YTD_Script_Count_Total;
  &build_mainchart_stacked2;
  print qq#<div id="$container" class="$class"></div>\n#;
  print qq#<div style="clear:both"></div>\n#;
  ### End Graph ### ---------------------------------------------------------------------

  ### Start Small Left Graph ### ---------------------------------------------------------------
  $decimalplaces = 0;
  $rotation      = -75;
  $container     = "ID_Total_Script_Count_Brand_YTD";
  $type          = "Brand";
  $yaxistitle    = "";
  $class         = "chartsmall_left";
  $marginright   = "30";
  $legend        = "false";
  %data = %Data_YTD_Script_Count_Brand;
  &build_mainchart_stacked2;
  print qq#<div style="width: 50%; float: left;"><div id="$container" class="$class"></div></div>\n#;
  ### End Graph ### ---------------------------------------------------------------------
  
  ### Start Small Right Graph ### ---------------------------------------------------------------
  $decimalplaces = 0;
  $rotation      = -75;
  $container     = "ID_Total_Script_Count_Generic_QTR";
  $type          = "Generic";
  $yaxistitle    = "";
  $class         = "chartsmall_left";
  $marginright   = "30";
  $legend        = "false";
  %data = %Data_YTD_Script_Count_Generic;
  &build_mainchart_stacked2;
  print qq#<div style="width: 50%; float: right;"><div id="$container" class="$class"></div></div>\n#;
  print qq#<div style="clear:both"></div>\n#;
  ### End Graph ### ---------------------------------------------------------------------
  
  ### Summary / Graph Comments ### ------------------------------------------------------
  my $summary = $Rep_sScript_Count{$ThisReportRepKey};
  if ( $summary !~ /^\s*$/ ) {
    print qq#<div class="summary">$summary</div>\n#;
  }
  ### End Summary ### -------------------------------------------------------------------
  
  print qq#</div> <!-- end page -->\n#;
}


sub displayScriptSalesStacked {
  ### Build Data Hashes ### -------------------------------------------------------------  
  my %Data_YTD_Script_Revenue_Total = ();
  
  for (my $lyear=$yearm2; $lyear<=$yearcur; $lyear++) {
    my $DataLoadKey = "$lyear";      #Build key to send data to graph
    my $RepKey = "$lyear"; #Build key to retrieve data
    my $Brand_Scripts_Revenue_YTD   = 0;
    my $Generic_Scripts_Revenue_YTD = 0;
    my $Total_Scripts_Revenue_YTD   = 0;

    for (my $lmonth=1; $lmonth<=$inMonth; $lmonth++) {
      my $rmonth = sprintf("%02d", $lmonth);
      my $YTDRepKey = "$inNCPDP##${lyear}-${rmonth}-01"; #Build key to retrieve data

      $Brand_Scripts_Revenue_YTD   += $Rep_Total_Brand_Revenue{$YTDRepKey} || 0;
      $Generic_Scripts_Revenue_YTD += $Rep_Total_Generic_Revenue{$YTDRepKey} || 0;
      $Total_Scripts_Revenue_YTD   += ($Rep_Total_Brand_Revenue{$YTDRepKey} + $Rep_Total_Generic_Revenue{$YTDRepKey}) || 0;
    }

    my $Brand_Scripts_Revenue   = $Rep_Total_Brand_Revenue{$RepKey} || 0;
    my $Generic_Scripts_Revenue = $Rep_Total_Generic_Revenue{$RepKey} || 0;
    my $Total_Scripts_Revenue   = ($Brand_Scripts_Revenue + $Generic_Scripts_Revenue) || 0;

    my $Brand_Scripts_Revenue_RM   = $Brand_Scripts_Revenue - $Brand_Scripts_Revenue_YTD;
    my $Generic_Scripts_Revenue_RM = $Generic_Scripts_Revenue - $Generic_Scripts_Revenue_YTD;
    my $Total_Scripts_Revenue_RM   = $Total_Scripts_Revenue - $Total_Scripts_Revenue_YTD;

    #Check data for blanks, replace with 'null' for graph display
    if ($Brand_Scripts_Revenue =~ /^\s*$/ || $Brand_Scripts_Revenue <= 0) {
      $Brand_Scripts_Revenue = "null";
    }
    if ($Generic_Scripts_Revenue =~ /^\s*$/ || $Generic_Scripts_Revenue <= 0) {
      $Generic_Scripts_Revenue = "null";
    }
    if ($Total_Scripts_Revenue =~ /^\s*$/ || $Total_Scripts_Revenue <= 0) {
      $Total_Scripts_Revenue = "null";
    }

    if ($Brand_Scripts_Revenue_RM =~ /^\s*$/ || $Brand_Scripts_Revenue_RM <= 0) {
      $Brand_Scripts_Revenue_RM = "null";
    }
    if ($Generic_Scripts_Revenue_RM =~ /^\s*$/ || $Generic_Scripts_Revenue_RM <= 0) {
      $Generic_Scripts_Revenue_RM = "null";
    }
    if ($Total_Scripts_Revenue_RM =~ /^\s*$/ || $Total_Scripts_Revenue_RM <= 0) {
      $Total_Scripts_Revenue_RM = "null";
    }
      
    #Load data to hashes with appropriate key for graph display

    $Data_YTD_Script_Revenue_Brand{"${DataLoadKey}##R"} = $Brand_Scripts_Revenue_RM;
    $Data_YTD_Script_Revenue_Generic{"${DataLoadKey}##R"} = $Generic_Scripts_Revenue_RM;
    $Data_YTD_Script_Revenue_Total{"${DataLoadKey}##R"} = $Total_Scripts_Revenue_RM;
    $Data_YTD_Script_Revenue_Brand{"${DataLoadKey}##T"} = $Brand_Scripts_Revenue_YTD;
    $Data_YTD_Script_Revenue_Generic{"${DataLoadKey}##T"} = $Generic_Scripts_Revenue_YTD;
    $Data_YTD_Script_Revenue_Total{"${DataLoadKey}##T"} = $Total_Scripts_Revenue_YTD;
  }
  ### End Data Hashes ### ---------------------------------------------------------------

  $section_title = "Sales YTD - $Pharmacy_Name";
  print qq#<div class="page">\n#;
  print qq#<div class="page_header"><h3>$section_title</h3></div>\n#;

  ### Start Main Graph ### ---------------------------------------------------------------
  $decimalplaces = 0;
  $rotation      = 0;
  $container     = "ID_Total_Script_Revenue_YTD";
  $type          = "Total Script Revenue YTD";
  $yaxistitle    = "";
  $class         = "mainchart";
  $marginright   = "110";
  $legend        = "true";
  %data = %Data_YTD_Script_Revenue_Total;
  &build_mainchart_stacked2;
  print qq#<div id="$container" class="$class"></div>\n#;
  print qq#<div style="clear:both"></div>\n#;
  ### End Graph ### ---------------------------------------------------------------------

  ### Start Small Left Graph ### ---------------------------------------------------------------
  $decimalplaces = 0;
  $rotation      = -75;
  $container     = "ID_Total_Script_Revenue_Brand_YTD";
  $type          = "Brand";
  $yaxistitle    = "";
  $class         = "chartsmall_left";
  $marginright   = "30";
  $legend        = "false";
  %data = %Data_YTD_Script_Revenue_Brand;
  &build_mainchart_stacked2;
  print qq#<div style="width: 50%; float: left;"><div id="$container" class="$class"></div></div>\n#;
  ### End Graph ### ---------------------------------------------------------------------
  
  ### Start Small Right Graph ### ---------------------------------------------------------------
  $decimalplaces = 0;
  $rotation      = -75;
  $container     = "ID_Total_Script_Revenue_Generic_YTD";
  $type          = "Generic";
  $yaxistitle    = "";
  $class         = "chartsmall_left";
  $marginright   = "30";
  $legend        = "false";
  %data = %Data_YTD_Script_Revenue_Generic;
  &build_mainchart_stacked2;
  print qq#<div style="width: 50%; float: right;"><div id="$container" class="$class"></div></div>\n#;
  ### End Graph ### ---------------------------------------------------------------------
  print qq#<div style="clear:both"></div>\n#;
  
  ### Summary / Graph Comments ### ------------------------------------------------------
  my $summary = $Rep_sScript_Count{$ThisReportRepKey};
  if ( $summary !~ /^\s*$/ ) {
    print qq#<div class="summary">$summary</div>\n#;
  }
  ### End Summary ### -------------------------------------------------------------------
  
  print qq#</div> <!-- end page -->\n#;
}


sub displayScriptCountQTR {
  
  ### Build Data Hashes ### -------------------------------------------------------------  
  my %Data_QTR_Script_Count_Brand = ();
  my %Data_QTR_Script_Count_Generic = ();
  my %Data_QTR_Script_Count_Total = ();
  
  for (my $lyear=$yearm2; $lyear<=$yearcur; $lyear++) {
    for (my $lqtr=1; $lqtr<=4; $lqtr++) {
  
      my $QtrRepKey = "$inNCPDP##$lyear##Q$lqtr"; #Build key to retrieve data
      my $QtrDataLoadKey = "$lyear##Q$lqtr";      #Build key to send data to graph
    
      my $Brand_Scripts   = $Rep_Total_Brand{$QtrRepKey} || 0;
      my $Generic_Scripts = $Rep_Total_Generic{$QtrRepKey} || 0;
      my $Total_Scripts   = ($Brand_Scripts + $Generic_Scripts) || 0;
      
      #Check data for blanks, replace with 'null' for graph display
      if ($Brand_Scripts =~ /^\s*$/ || $Brand_Scripts <= 0) {
        $Brand_Scripts = "null";
      }
      if ($Generic_Scripts =~ /^\s*$/ || $Generic_Scripts <= 0) {
        $Generic_Scripts = "null";
      }
      if ($Total_Scripts =~ /^\s*$/ || $Total_Scripts <= 0) {
        $Total_Scripts = "null";
      }
      
      #Load data to hashes with appropriate key for graph display
      $Data_QTR_Script_Count_Brand{$QtrDataLoadKey} = $Brand_Scripts;
      $Data_QTR_Script_Count_Generic{$QtrDataLoadKey} = $Generic_Scripts;
      $Data_QTR_Script_Count_Total{$QtrDataLoadKey} = $Total_Scripts;

    }
  }
  ### End Data Hashes ### ---------------------------------------------------------------

  $section_title = "Script Information by QTR - $Pharmacy_Name";
  print qq#<div class="page">\n#;
  print qq#<div class="page_header"><h3>$section_title</h3></div>\n#;
  
  ### Start Main Graph ### ---------------------------------------------------------------
  $decimalplaces = 0;
  $rotation      = 0;
  $container     = "ID_Total_Script_Count_QTR";
  $type          = "Total Script Count QTR";
  $yaxistitle    = "";
  $class         = "mainchart";
  $marginright   = "110";
  $legend        = "true";
  %data = %Data_QTR_Script_Count_Total;
  &build_mainchart_stacked;
  print qq#<div id="$container" class="$class"></div>\n#;
  print qq#<div style="clear:both"></div>\n#;
  ### End Graph ### ---------------------------------------------------------------------

  ### Start Small Left Graph ### ---------------------------------------------------------------
  $decimalplaces = 0;
  $rotation      = -75;
  $container     = "ID_Total_Script_Count_Brand_QTR";
  $type          = "Brand";
  $yaxistitle    = "";
  $class         = "chartsmall_left";
  $marginright   = "30";
  $legend        = "false";
  %data = %Data_QTR_Script_Count_Brand;
  &build_mainchart_stacked;
  print qq#<div style="width: 50%; float: left;"><div id="$container" class="$class"></div></div>\n#;
  ### End Graph ### ---------------------------------------------------------------------
  
  ### Start Small Right Graph ### ---------------------------------------------------------------
  $decimalplaces = 0;
  $rotation      = -75;
  $container     = "ID_Total_Script_Count_Generic_QTR";
  $type          = "Generic";
  $yaxistitle    = "";
  $class         = "chartsmall_left";
  $marginright   = "30";
  $legend        = "false";
  %data = %Data_QTR_Script_Count_Generic;
  &build_mainchart_stacked;
  print qq#<div style="width: 50%; float: right;"><div id="$container" class="$class"></div></div>\n#;
  ### End Graph ### ---------------------------------------------------------------------
  
  print qq#<div style="clear:both"></div>\n#;
  
  ### Summary / Graph Comments ### ------------------------------------------------------
  my $summary = $Rep_sScript_Count{$ThisReportRepKey};
  if ( $summary !~ /^\s*$/ ) {
    print qq#<div class="summary">$summary</div>\n#;
  }
  ### End Summary ### -------------------------------------------------------------------
  
  print qq#</div> <!-- end page -->\n#;
}


sub displaySales {
  
  ### Build Data Hashes ### -------------------------------------------------------------
  my %Data_Sales_Brand = ();
  my %Data_Sales_Generic = ();
  my %Data_Sales_Total = ();
  
  for (my $lyear=$yearm2; $lyear<=$yearcur; $lyear++) {
    for (my $lmonth=1; $lmonth<=12; $lmonth++) {
    
      next if ($lyear >= $yearcur && $lmonth > $jmonth);
    
      $lmonth = sprintf("%02d", $lmonth);
      
      my $RepKey = "$inNCPDP##$lyear-$lmonth-01"; #Build key to retrieve data
      my $DataLoadKey = "$lyear##$lmonth";        #Build key to send data to graph
    
      my $Brand_Sales   = $Rep_Total_Brand_Revenue{$RepKey} || 0;
      my $Generic_Sales = $Rep_Total_Generic_Revenue{$RepKey} || 0;
      my $Total_Sales   = ($Brand_Sales + $Generic_Sales) || 0;
      
      ### Calculations ### ----------------------------------------------------
      ### End Calculations ### ------------------------------------------------
      
      #Check data for blanks, replace with 'null' for graph display
      if ($Brand_Sales =~ /^\s*$/ || $Brand_Sales == 0) {
        $Brand_Sales = "null";
      }
      if ($Generic_Sales =~ /^\s*$/ || $Generic_Sales == 0) {
        $Generic_Sales = "null";
      }
      if ($Total_Sales =~ /^\s*$/ || $Total_Sales == 0) {
        $Total_Sales = "null";
      }
      
      #Load data to hashes with appropriate key for graph display
      $Data_Sales_Brand{$DataLoadKey} = $Brand_Sales;
      $Data_Sales_Generic{$DataLoadKey} = $Generic_Sales;
      $Data_Sales_Total{$DataLoadKey} = $Total_Sales;

    }
  }
  ### End Data Hashes ### ---------------------------------------------------------------
  
  my $section_title = "Sales - $Pharmacy_Name";
  print qq#<div class="page">\n#;
  print qq#<div class="page_header"><h3>$section_title</h3></div>\n#;
  
  ### Start Main Graph ### ---------------------------------------------------------------
  $decimalplaces = 2;
  $rotation      = 0;
  $container     = "ID_Total_Sales";
  $type          = "Total Sales";
  $yaxistitle    = "Dollars Per Month";
  $class         = "mainchart";
  $marginright   = "110";
  $legend        = "true";
  %data = %Data_Sales_Total;
  &build_mainchart;
  print qq#<div id="$container" class="$class"></div>\n#;
  print qq#<div style="clear:both"></div>\n#;
  ### End Graph ### ---------------------------------------------------------------------
  
  ### Start Small Left Graph ### ---------------------------------------------------------------
  $decimalplaces = 2;
  $rotation      = -75;
  $container     = "ID_Total_Sales_Brand";
  $type          = "Brand";
  $yaxistitle    = "Dollars Per Month";
  $class         = "chartsmall_left";
  $marginright   = "30";
  $legend        = "false";
  %data = %Data_Sales_Brand;
  &build_mainchart;
  print qq#<div style="width: 50%; float: left;"><div id="$container" class="$class"></div></div>\n#;
  ### End Graph ### ---------------------------------------------------------------------
  
  ### Start Small Right Graph ### ---------------------------------------------------------------
  $decimalplaces = 2;
  $rotation      = -75;
  $container     = "ID_Total_Sales_Generic";
  $type          = "Generic";
  $yaxistitle    = "Dollars Per Month";
  $class         = "chartsmall_left";
  $marginright   = "30";
  $legend        = "false";
  %data = %Data_Sales_Generic;
  &build_mainchart;
  print qq#<div style="width: 50%; float: right;"><div id="$container" class="$class"></div></div>\n#;
  ### End Graph ### ---------------------------------------------------------------------
  
  print qq#<div style="clear:both"></div>\n#;  
  print qq#</div> <!-- end page -->\n#;
}

#______________________________________________________________________________

sub displaySalesQTR {
  
  ### Build Data Hashes ### -------------------------------------------------------------  
  my %Data_QTR_Sales_Brand = ();
  my %Data_QTR_Sales_Generic = ();
  my %Data_QTR_Sales_Total = ();
  
  for (my $lyear=$yearm2; $lyear<=$yearcur; $lyear++) {
    for (my $lqtr=1; $lqtr<=4; $lqtr++) {
    
      my $QtrRepKey = "$inNCPDP##$lyear##Q$lqtr"; #Build key to retrieve data
      my $QtrDataLoadKey = "$lyear##Q$lqtr";      #Build key to send data to graph
    
      my $Brand_Sales   = $Rep_Total_Brand_Revenue{$QtrRepKey} || 0;
      my $Generic_Sales = $Rep_Total_Generic_Revenue{$QtrRepKey} || 0;
      my $Total_Sales   = ($Brand_Sales + $Generic_Sales) || 0;
      
      #Check data for blanks, replace with 'null' for graph display
      if ($Brand_Sales =~ /^\s*$/ || $Brand_Sales == 0) {
        $Brand_Sales = "null";
      }
      if ($Generic_Sales =~ /^\s*$/ || $Generic_Sales == 0) {
        $Generic_Sales = "null";
      }
      if ($Total_Sales =~ /^\s*$/ || $Total_Sales == 0) {
        $Total_Sales = "null";
      }
      
      #Load data to hashes with appropriate key for graph display
      $Data_QTR_Sales_Brand{$QtrDataLoadKey} = $Brand_Sales;
      $Data_QTR_Sales_Generic{$QtrDataLoadKey} = $Generic_Sales;
      $Data_QTR_Sales_Total{$QtrDataLoadKey} = $Total_Sales;

    }
  }
  ### End Data Hashes ### ---------------------------------------------------------------

  $section_title = "Sales by QTR - $Pharmacy_Name";
  print qq#<div class="page">\n#;
  print qq#<div class="page_header"><h3>$section_title</h3></div>\n#;
  
  ### Start Main Graph ### ---------------------------------------------------------------
  $decimalplaces = 0;
  $rotation      = 0;
  $container     = "ID_Total_Sales_QTR";
  $type          = "Total Sales QTR";
  $yaxistitle    = "";
  $class         = "mainchart";
  $marginright   = "110";
  $legend        = "true";
  %data = %Data_QTR_Sales_Total;
  &build_mainchart_stacked;
  print qq#<div id="$container" class="$class"></div>\n#;
  print qq#<div style="clear:both"></div>\n#;
  ### End Graph ### ---------------------------------------------------------------------

  ### Start Small Left Graph ### ---------------------------------------------------------------
  #Set &build_mainchart_stacked parameters
  $decimalplaces = 0;
  $rotation      = -75;
  $container     = "ID_Total_Sales_Brand_QTR";
  $type          = "Brand";
  $yaxistitle    = "";
  $class         = "chartsmall_left";
  $marginright   = "30";
  $legend        = "false";
  %data = %Data_QTR_Sales_Brand;
  &build_mainchart_stacked;
  print qq#<div style="width: 50%; float: left;"><div id="$container" class="$class"></div></div>\n#;
  ### End Graph ### ---------------------------------------------------------------------
  
  ### Start Small Right Graph ### ---------------------------------------------------------------
  $decimalplaces = 0;
  $rotation      = -75;
  $container     = "ID_Total_Sales_Generic_QTR";
  $type          = "Generic";
  $yaxistitle    = "";
  $class         = "chartsmall_left";
  $marginright   = "30";
  $legend        = "false";
  %data = %Data_QTR_Sales_Generic;
  &build_mainchart_stacked;
  print qq#<div style="width: 50%; float: right;"><div id="$container" class="$class"></div></div>\n#;
  ### End Graph ### ---------------------------------------------------------------------
  
  print qq#<div style="clear:both"></div>\n#;
  
  ### Summary / Graph Comments ### ------------------------------------------------------
  my $summary = $Rep_sSales{$ThisReportRepKey};
  if ( $summary !~ /^\s*$/ ) {
    print qq#<div class="summary">$summary</div>\n#;
  }
  ### End Summary ### -------------------------------------------------------------------
  
  print qq#</div> <!-- end page -->\n#;
}

#______________________________________________________________________________

sub displayGrossMargin {
  
  ### Build Data Hashes ### -------------------------------------------------------------
  my %Data_GM_Brand = ();
  my %Data_GM_Generic = ();
  my %Data_GM_Total = ();
  
  for (my $lyear=$yearm2; $lyear<=$yearcur; $lyear++) {
    for (my $lmonth=1; $lmonth<=12; $lmonth++) {
    
      next if ($lyear >= $yearcur && $lmonth > $jmonth);
      
      $lmonth = sprintf("%02d", $lmonth);
      
      my $RepKey = "$inNCPDP##$lyear-$lmonth-01"; #Build key to retrieve data
      my $DataLoadKey = "$lyear##$lmonth";        #Build key to send data to graph
    
      my $Brand_GM   = $Rep_Total_Brand_Revenue{$RepKey} - $Rep_Total_Brand_Cost{$RepKey};
      my $Generic_GM = $Rep_Total_Generic_Revenue{$RepKey} - $Rep_Total_Generic_Cost{$RepKey};
      my $Total_GM   = ( 
                         $Rep_Total_Brand_Revenue{$RepKey} + $Rep_Total_Generic_Revenue{$RepKey} 
                         - $Rep_Total_Brand_Cost{$RepKey}    - $Rep_Total_Generic_Cost{$RepKey}
                       );
      
      #Check data for blanks, replace with 'null' for graph display
      if ($Brand_GM =~ /^\s*$/ || $Brand_GM == 0) {
        $Brand_GM = "null";
      }
      if ($Generic_GM =~ /^\s*$/ || $Generic_GM == 0) {
        $Generic_GM = "null";
      }
      if ($Total_GM =~ /^\s*$/ || $Total_GM == 0) {
        $Total_GM = "null";
      }
      
      #Load data to hashes with appropriate key for graph display
      $Data_GM_Brand{$DataLoadKey} = $Brand_GM;
      $Data_GM_Generic{$DataLoadKey} = $Generic_GM;
      $Data_GM_Total{$DataLoadKey} = $Total_GM;

    }
  }
  ### End Data Hashes ### ---------------------------------------------------------------

  my $section_title = "Gross Margin - $Pharmacy_Name";
  print qq#<div class="page">\n#;
  print qq#<div class="page_header"><h3>$section_title</h3></div>\n#;
  
  ### Start Main Graph ### ---------------------------------------------------------------
  $decimalplaces = 2;
  $rotation      = 0;
  $container     = "ID_Total_Gross_Margin";
  $type          = "Total Gross Margin";
  $yaxistitle    = "Dollars Per Month";
  $class         = "mainchart";
  $marginright   = "110";
  $legend        = "true";
  %data = %Data_GM_Total;
  &build_mainchart;
  print qq#<div id="$container" class="$class"></div>\n#;
  print qq#<div style="clear:both"></div>\n#;
  ### End Graph ### ---------------------------------------------------------------------
  
  ### Start Small Left Graph ### ---------------------------------------------------------------
  $decimalplaces = 2;
  $rotation      = -75;
  $container     = "ID_Total_Gross_Margin_Brand";
  $type          = "Brand";
  $yaxistitle    = "Dollars Per Month";
  $class         = "chartsmall_left";
  $marginright   = "30";
  $legend        = "false";
  %data = %Data_GM_Brand;
  &build_mainchart;
  print qq#<div style="width: 50%; float: left;"><div id="$container" class="$class"></div></div>\n#;
  ### End Graph ### ---------------------------------------------------------------------
  
  ### Start Small Right Graph ### ---------------------------------------------------------------
  $decimalplaces = 2;
  $rotation      = -75;
  $container     = "ID_Total_Gross_Margin_Generic";
  $type          = "Generic";
  $yaxistitle    = "Dollars Per Month";
  $class         = "chartsmall_left";
  $marginright   = "30";
  $legend        = "false";
  %data = %Data_GM_Generic;
  &build_mainchart;
  print qq#<div style="width: 50%; float: right;"><div id="$container" class="$class"></div></div>\n#;
  ### End Graph ### ---------------------------------------------------------------------
  
  print qq#<div style="clear:both"></div>\n#;  
  print qq#</div> <!-- end page -->\n#;
  ###---###---###---###---###---###---###---###---###---###---###---###---###---###---###---###
  
}

#______________________________________________________________________________

sub displayGrossMarginQTR {
  
  ### Build Data Hashes ### -------------------------------------------------------------
  my %Data_QTR_GM_Brand = ();
  my %Data_QTR_GM_Generic = ();
  my %Data_QTR_GM_Total = ();
  
  for (my $lyear=$yearm2; $lyear<=$yearcur; $lyear++) {
    for (my $lqtr=1; $lqtr<=4; $lqtr++) {
    
      my $QtrRepKey = "$inNCPDP##$lyear##Q$lqtr"; #Build key to retrieve data
      my $QtrDataLoadKey = "$lyear##Q$lqtr";      #Build key to send data to graph
    
      my $Brand_GM   = $Rep_Total_Brand_Revenue{$QtrRepKey} - $Rep_Total_Brand_Cost{$QtrRepKey};
      my $Generic_GM = $Rep_Total_Generic_Revenue{$QtrRepKey} - $Rep_Total_Generic_Cost{$QtrRepKey};
      my $Total_GM   = ( 
                         $Rep_Total_Brand_Revenue{$QtrRepKey} + $Rep_Total_Generic_Revenue{$QtrRepKey} 
                         - $Rep_Total_Brand_Cost{$QtrRepKey}    - $Rep_Total_Generic_Cost{$QtrRepKey}
                       );
      
      #Check data for blanks, replace with 'null' for graph display
      if ($Brand_GM =~ /^\s*$/ || $Brand_GM == 0) {
        $Brand_GM = "null";
      }
      if ($Generic_GM =~ /^\s*$/ || $Generic_GM == 0) {
        $Generic_GM = "null";
      }
      if ($Total_GM =~ /^\s*$/ || $Total_GM == 0) {
        $Total_GM = "null";
      }
      
      #Load data to hashes with appropriate key for graph display
      $Data_QTR_GM_Brand{$QtrDataLoadKey}   = $Brand_GM;
      $Data_QTR_GM_Generic{$QtrDataLoadKey} = $Generic_GM;
      $Data_QTR_GM_Total{$QtrDataLoadKey}   = $Total_GM;
    }
  }
  ### End Data Hashes ### ---------------------------------------------------------------

  my $section_title = "Gross Margin by QTR - $Pharmacy_Name";
  print qq#<div class="page">\n#;
  print qq#<div class="page_header"><h3>$section_title</h3></div>\n#;
  
  ### Start Main Graph ### ---------------------------------------------------------------
  $decimalplaces = 2;
  $rotation      = 0;
  $container     = "ID_Total_Gross_Margin_QTR";
  $type          = "Total Gross Margin QTR";
  $yaxistitle    = "Dollars Per Month";
  $class         = "mainchart";
  $marginright   = "110";
  $legend        = "true";
  %data = %Data_QTR_GM_Total;
  &build_mainchart_stacked;
  print qq#<div id="$container" class="$class"></div>\n#;
  print qq#<div style="clear:both"></div>\n#;
  ### End Graph ### ---------------------------------------------------------------------
  
  ### Start Small Left Graph ### ---------------------------------------------------------------
  $decimalplaces =   2;
  $rotation      = -75;
  $container     = "ID_Total_Gross_Margin_Brand_QTR";
  $type          = "Brand";
  $yaxistitle    = "Dollars Per Month";
  $class         = "chartsmall_left";
  $marginright   = "30";
  $legend        = "false";
  %data = %Data_QTR_GM_Brand;
  &build_mainchart_stacked;
  print qq#<div style="width: 50%; float: left;"><div id="$container" class="$class"></div></div>\n#;
  ### End Graph ### ---------------------------------------------------------------------
  
  ### Start Small Right Graph ### ---------------------------------------------------------------
  $decimalplaces = 2;
  $rotation      = -75;
  $container     = "ID_Total_Gross_Margin_Generic_QTR";
  $type          = "Generic";
  $yaxistitle    = "Dollars Per Month";
  $class         = "chartsmall_left";
  $marginright   = "30";
  $legend        = "false";
  %data = %Data_QTR_GM_Generic;
  &build_mainchart_stacked;
  print qq#<div style="width: 50%; float: right;"><div id="$container" class="$class"></div></div>\n#;
  ### End Graph ### ---------------------------------------------------------------------
  
  print qq#<div style="clear:both"></div>\n#;
  
  ### Summary / Graph Comments ### ------------------------------------------------------
  my $summary = $Rep_sGross_Margin{$ThisReportRepKey};
  if ( $summary !~ /^\s*$/ ) {
    print qq#<div class="summary">$summary</div>\n#;
  }
  ### End Summary ### -------------------------------------------------------------------
  
  print qq#</div> <!-- end page -->\n#;
}

#______________________________________________________________________________

sub displayGrossMarginPercent {
  
  ### Build Data Hashes ### -------------------------------------------------------------
  my %Data_GM_Percent_Brand = ();
  my %Data_GM_Percent_Generic = ();
  my %Data_GM_Percent_Total = ();
  
  for (my $lyear=$yearm2; $lyear<=$yearcur; $lyear++) {
    for (my $lmonth=1; $lmonth<=12; $lmonth++) {
    
      next if ($lyear >= $yearcur && $lmonth > $jmonth);
      
      $lmonth = sprintf("%02d", $lmonth);
      
      my $RepKey = "$inNCPDP##$lyear-$lmonth-01"; #Build key to retrieve data
      my $DataLoadKey = "$lyear##$lmonth";        #Build key to send data to graph
    
      my $Brand_GM_Percent = 0;
      my $Generic_GM_Percent = 0;
      my $Total_GM_Percent = 0;
      
      if ($Rep_Total_Brand_Revenue{$RepKey} > 0) {
        $Brand_GM_Percent   = ($Rep_Total_Brand_Revenue{$RepKey} - $Rep_Total_Brand_Cost{$RepKey}) / $Rep_Total_Brand_Revenue{$RepKey};
      $Brand_GM_Percent   = $Brand_GM_Percent*100;
      }
      if ($Rep_Total_Generic_Revenue{$RepKey} > 0) {
        $Generic_GM_Percent = ($Rep_Total_Generic_Revenue{$RepKey} - $Rep_Total_Generic_Cost{$RepKey}) / $Rep_Total_Generic_Revenue{$RepKey};
      $Generic_GM_Percent = $Generic_GM_Percent*100;
      }
      if ( ($Rep_Total_Brand_Revenue{$RepKey} + $Rep_Total_Generic_Revenue{$RepKey}) > 0) {
        $Total_GM_Percent   = ( $Rep_Total_Brand_Revenue{$RepKey} + $Rep_Total_Generic_Revenue{$RepKey} - $Rep_Total_Brand_Cost{$RepKey} - $Rep_Total_Generic_Cost{$RepKey} ) / ( $Rep_Total_Brand_Revenue{$RepKey} + $Rep_Total_Generic_Revenue{$RepKey} );
      $Total_GM_Percent = $Total_GM_Percent*100;
        }
      
      #Check data for blanks, replace with 'null' for graph display
      if ($Brand_GM_Percent =~ /^\s*$/ || $Brand_GM_Percent == 0) {
        $Brand_GM_Percent = "null";
      }
      if ($Generic_GM_Percent =~ /^\s*$/ || $Generic_GM_Percent == 0) {
        $Generic_GM_Percent = "null";
      }
      if ($Total_GM_Percent =~ /^\s*$/ || $Total_GM_Percent == 0) {
        $Total_GM_Percent = "null";
      }
      
      #Load data to hashes with appropriate key for graph display
      $Data_GM_Percent_Brand{$DataLoadKey} = $Brand_GM_Percent;
      $Data_GM_Percent_Generic{$DataLoadKey} = $Generic_GM_Percent;
      $Data_GM_Percent_Total{$DataLoadKey} = $Total_GM_Percent;

    }
  }
  ### End Data Hashes ### ---------------------------------------------------------------
  
  my $section_title = "Gross Margin Percent - $Pharmacy_Name";
  print qq#<div class="page">\n#;
  print qq#<div class="page_header"><h3>$section_title</h3></div>\n#;
  
  ### Start Main Graph ### ---------------------------------------------------------------
  $decimalplaces = 5;
  $rotation      = 0;
  $container     = "ID_Total_Gross_Margin_Percent";
  $type          = "Total Gross Margin Percent";
  $yaxistitle    = "Percentage";
  $class         = "mainchart";
  $marginright   = "110";
  $legend        = "true";
  %data = %Data_GM_Percent_Total;
  &build_mainchart;
  print qq#<div id="$container" class="$class"></div>\n#;
  print qq#<div style="clear:both"></div>\n#;
  ### End Graph ### ---------------------------------------------------------------------
  
  ### Start Small Left Graph ### ---------------------------------------------------------------
  $decimalplaces = 5;
  $rotation      = -75;
  $container     = "ID_Total_Gross_Margin_Percent_Brand";
  $type          = "Brand";
  $yaxistitle    = "Percentage";
  $class         = "chartsmall_left";
  $marginright   = "30";
  $legend        = "false";
  %data = %Data_GM_Percent_Brand;
  &build_mainchart;
  print qq#<div style="width: 50%; float: left;"><div id="$container" class="$class"></div></div>\n#;
  ### End Graph ### ---------------------------------------------------------------------
  
  ### Start Small Right Graph ### ---------------------------------------------------------------
  $decimalplaces = 5;
  $rotation      = -75;
  $container     = "ID_Total_Gross_Margin_Percent_Generic";
  $type          = "Generic";
  $yaxistitle    = "Percentage";
  $class         = "chartsmall_left";
  $marginright   = "30";
  $legend        = "false";
  %data = %Data_GM_Percent_Generic;
  &build_mainchart;
  print qq#<div style="width: 50%; float: right;"><div id="$container" class="$class"></div></div>\n#;
  ### End Graph ### ---------------------------------------------------------------------
  
  print qq#<div style="clear:both"></div>\n#;
  
  ### Summary / Graph Comments ### ------------------------------------------------------
  my $summary = $Rep_sGross_Margin_Percent{$ThisReportRepKey};
  if ( $summary !~ /^\s*$/ ) {
    print qq#<div class="summary">$summary</div>\n#;
  }
  ### End Summary ### -------------------------------------------------------------------
  
  print qq#</div> <!-- end page -->\n#;
}

#______________________________________________________________________________

sub displayAverageSalePerScript {
  
  ### Build Data Hashes ### -------------------------------------------------------------
  my %Data_Avg_Sale_Per_Script_Brand = ();
  my %Data_Avg_Sale_Per_Script_Generic = ();
  my %Data_Avg_Sale_Per_Script_Total = ();
  
  for (my $lyear=$yearm2; $lyear<=$yearcur; $lyear++) {
    for (my $lmonth=1; $lmonth<=12; $lmonth++) {
    
      next if ($lyear >= $yearcur && $lmonth > $jmonth);
      
      $lmonth = sprintf("%02d", $lmonth);
      
      my $RepKey = "$inNCPDP##$lyear-$lmonth-01"; #Build key to retrieve data
      my $DataLoadKey = "$lyear##$lmonth";        #Build key to send data to graph
    
      my $Brand_Avg_Sale_Per_Script = 0;
      my $Generic_Avg_Sale_Per_Script = 0;
      my $Total_Avg_Sale_Per_Script = 0;
      
      if ($Rep_Total_Brand{$RepKey} > 0) {
        $Brand_Avg_Sale_Per_Script   = ($Rep_Total_Brand_Revenue{$RepKey}) / $Rep_Total_Brand{$RepKey};
      }
      if ($Rep_Total_Generic{$RepKey} > 0) {
        $Generic_Avg_Sale_Per_Script = ($Rep_Total_Generic_Revenue{$RepKey}) / $Rep_Total_Generic{$RepKey};
      }
      if ( ($Rep_Total_Brand{$RepKey} + $Rep_Total_Generic{$RepKey}) > 0) {
        $Total_Avg_Sale_Per_Script   = ( $Rep_Total_Brand_Revenue{$RepKey} + $Rep_Total_Generic_Revenue{$RepKey} ) / ( $Rep_Total_Brand{$RepKey} + $Rep_Total_Generic{$RepKey} );
        }
      
      #Check data for blanks, replace with 'null' for graph display
      if ($Brand_Avg_Sale_Per_Script =~ /^\s*$/ || $Brand_Avg_Sale_Per_Script == 0) {
        $Brand_Avg_Sale_Per_Script = "null";
      }
      if ($Generic_Avg_Sale_Per_Script =~ /^\s*$/ || $Generic_Avg_Sale_Per_Script == 0) {
        $Generic_Avg_Sale_Per_Script = "null";
      }
      if ($Total_Avg_Sale_Per_Script =~ /^\s*$/ || $Total_Avg_Sale_Per_Script == 0) {
        $Total_Avg_Sale_Per_Script = "null";
      }
      
      #Load data to hashes with appropriate key for graph display
      $Data_Avg_Sale_Per_Script_Brand{$DataLoadKey} = $Brand_Avg_Sale_Per_Script;
      $Data_Avg_Sale_Per_Script_Generic{$DataLoadKey} = $Generic_Avg_Sale_Per_Script;
      $Data_Avg_Sale_Per_Script_Total{$DataLoadKey} = $Total_Avg_Sale_Per_Script;

    }
  }
  ### End Data Hashes ### ---------------------------------------------------------------

  my $section_title = "Average Sale Per Script - $Pharmacy_Name";
  print qq#<div class="page">\n#;
  print qq#<div class="page_header"><h3>$section_title</h3></div>\n#;
  
  ### Start Main Graph ### ---------------------------------------------------------------
  #Set &build_mainchart parameters
  $decimalplaces = 2;
  $rotation      = 0;
  $container     = "ID_Average_Sale_Per_Script";
  $type          = "Average Sale Per Script";
  $yaxistitle    = "Dollars";
  $class         = "mainchart";
  $marginright   = "110";
  $legend        = "true";
  %data = %Data_Avg_Sale_Per_Script_Total;
  &build_mainchart;
  print qq#<div id="$container" class="$class"></div>\n#;
  print qq#<div style="clear:both"></div>\n#;
  ### End Graph ### ---------------------------------------------------------------------
  
  ### Start Small Left Graph ### ---------------------------------------------------------------
  $decimalplaces = 2;
  $rotation      = -75;
  $container     = "ID_Average_Sale_Per_Script_Brand";
  $type          = "Brand";
  $yaxistitle    = "Dollars";
  $class         = "chartsmall_left";
  $marginright   = "30";
  $legend        = "false";
  %data = %Data_Avg_Sale_Per_Script_Brand;
  &build_mainchart;
  print qq#<div style="width: 50%; float: left;"><div id="$container" class="$class"></div></div>\n#;
  ### End Graph ### ---------------------------------------------------------------------
  
  ### Start Small Right Graph ### ---------------------------------------------------------------
  $decimalplaces = 2;
  $rotation      = -75;
  $container     = "ID_Average_Sale_Per_Script_Generic";
  $type          = "Generic";
  $yaxistitle    = "Dollars";
  $class         = "chartsmall_left";
  $marginright   = "30";
  $legend        = "false";
  %data = %Data_Avg_Sale_Per_Script_Generic;
  &build_mainchart;
  print qq#<div style="width: 50%; float: right;"><div id="$container" class="$class"></div></div>\n#;
  ### End Graph ### ---------------------------------------------------------------------
  
  print qq#<div style="clear:both"></div>\n#;
  
  ### Summary / Graph Comments ### ------------------------------------------------------
  my $summary = $Rep_sAverage_Sale_Per_Script{$ThisReportRepKey};
  if ( $summary !~ /^\s*$/ ) {
    print qq#<div class="summary">$summary</div>\n#;
  }
  ### End Summary ### -------------------------------------------------------------------
  
  print qq#</div> <!-- end page -->\n#;
}

sub displayAverageGrossMarginPerScript {
  
  ### Build Data Hashes ### -------------------------------------------------------------
  my %Data_Avg_Gross_Margin_Per_Script_Brand = ();
  my %Data_Avg_Gross_Margin_Per_Script_Generic = ();
  my %Data_Avg_Gross_Margin_Per_Script_Total = ();
  
  for (my $lyear=$yearm2; $lyear<=$yearcur; $lyear++) {
    for (my $lmonth=1; $lmonth<=12; $lmonth++) {
    
      next if ($lyear >= $yearcur && $lmonth > $jmonth);
      
      $lmonth = sprintf("%02d", $lmonth);
      
      my $RepKey = "$inNCPDP##$lyear-$lmonth-01"; #Build key to retrieve data
      my $DataLoadKey = "$lyear##$lmonth";        #Build key to send data to graph
    
      my $Brand_Avg_Gross_Margin_Per_Script = 0;
      my $Generic_Avg_Gross_Margin_Per_Script = 0;
      my $Total_Avg_Gross_Margin_Per_Script = 0;
      
      if ($Rep_Total_Brand{$RepKey} > 0) {
        $Brand_Avg_Gross_Margin_Per_Script   = ($Rep_Total_Brand_Revenue{$RepKey} - $Rep_Total_Brand_Cost{$RepKey}) / $Rep_Total_Brand{$RepKey};
      }
      if ($Rep_Total_Generic{$RepKey} > 0) {
        $Generic_Avg_Gross_Margin_Per_Script = ($Rep_Total_Generic_Revenue{$RepKey} - $Rep_Total_Generic_Cost{$RepKey}) / $Rep_Total_Generic{$RepKey};
      }
      if ( ($Rep_Total_Brand{$RepKey} + $Rep_Total_Generic{$RepKey}) > 0) {
        $Total_Avg_Gross_Margin_Per_Script   = ( $Rep_Total_Brand_Revenue{$RepKey} + $Rep_Total_Generic_Revenue{$RepKey} - $Rep_Total_Brand_Cost{$RepKey} - $Rep_Total_Generic_Cost{$RepKey} ) / ( $Rep_Total_Brand{$RepKey} + $Rep_Total_Generic{$RepKey} );
        }
      
      #Check data for blanks, replace with 'null' for graph display
      if ($Brand_Avg_Gross_Margin_Per_Script =~ /^\s*$/ || $Brand_Avg_Gross_Margin_Per_Script == 0) {
        $Brand_Avg_Gross_Margin_Per_Script = "null";
      }
      if ($Generic_Avg_Gross_Margin_Per_Script =~ /^\s*$/ || $Generic_Avg_Gross_Margin_Per_Script == 0) {
        $Generic_Avg_Gross_Margin_Per_Script = "null";
      }
      if ($Total_Avg_Gross_Margin_Per_Script =~ /^\s*$/ || $Total_Avg_Gross_Margin_Per_Script == 0) {
        $Total_Avg_Gross_Margin_Per_Script = "null";
      }
      
      #Load data to hashes with appropriate key for graph display
      $Data_Avg_Gross_Margin_Per_Script_Brand{$DataLoadKey} = $Brand_Avg_Gross_Margin_Per_Script;
      $Data_Avg_Gross_Margin_Per_Script_Generic{$DataLoadKey} = $Generic_Avg_Gross_Margin_Per_Script;
      $Data_Avg_Gross_Margin_Per_Script_Total{$DataLoadKey} = $Total_Avg_Gross_Margin_Per_Script;

    }
  }
  ### End Data Hashes ### ---------------------------------------------------------------

  my $section_title = "Average Gross Margin Per Script - $Pharmacy_Name";
  print qq#<div class="page">\n#;
  print qq#<div class="page_header"><h3>$section_title</h3></div>\n#;
  
  ### Start Main Graph ### ---------------------------------------------------------------
  $decimalplaces = 2;
  $rotation      = 0;
  $container     = "ID_Average_GM_Per_Script";
  $type          = "Average Gross Margin Per Script";
  $yaxistitle    = "Dollars";
  $class         = "mainchart";
  $marginright   = "110";
  $legend        = "true";
  %data = %Data_Avg_Gross_Margin_Per_Script_Total;
  &build_mainchart;
  print qq#<div id="$container" class="$class"></div>\n#;
  print qq#<div style="clear:both"></div>\n#;
  ### End Graph ### ---------------------------------------------------------------------
  
  ### Start Small Left Graph ### ---------------------------------------------------------------
  $decimalplaces = 2;
  $rotation      = -75;
  $container     = "ID_Average_GM_Per_Script_Brand";
  $type          = "Brand";
  $yaxistitle    = "Dollars";
  $class         = "chartsmall_left";
  $marginright   = "30";
  $legend        = "false";
  %data = %Data_Avg_Gross_Margin_Per_Script_Brand;
  &build_mainchart;
  print qq#<div style="width: 50%; float: left;"><div id="$container" class="$class"></div></div>\n#;
  ### End Graph ### ---------------------------------------------------------------------
  
  ### Start Small Right Graph ### ---------------------------------------------------------------
  $decimalplaces = 2;
  $rotation      = -75;
  $container     = "ID_Average_GM_Per_Script_Generic";
  $type          = "Generic";
  $yaxistitle    = "Dollars";
  $class         = "chartsmall_left";
  $marginright   = "30";
  $legend        = "false";
  %data = %Data_Avg_Gross_Margin_Per_Script_Generic;
  &build_mainchart;
  print qq#<div style="width: 50%; float: right;"><div id="$container" class="$class"></div></div>\n#;
  ### End Graph ### ---------------------------------------------------------------------
  
  print qq#<div style="clear:both"></div>\n#;
  
  ### Summary / Graph Comments ### ------------------------------------------------------
  my $summary = $Rep_sAverage_Gross_Margin_Per_Script{$ThisReportRepKey};
  if ( $summary !~ /^\s*$/ ) {
    print qq#<div class="summary">$summary</div>\n#;
  }
  ### End Summary ### -------------------------------------------------------------------
  
  print qq#</div> <!-- end page -->\n#;
}

#______________________________________________________________________________

sub displayComments {

  print qq#<div id="sidebarWrapper">\n#;
  
  print qq#<h2>Events to Note:</h2>\n#;
  
  print qq#<div id="sidebar">\n#;

  $TABLE = 'Special_Comments';
  $sql  = " SELECT NCPDP, Title, Comment, Date_From, Date_To ";
  $sql .= " FROM $DBNAMERM.$TABLE WHERE NCPDP=$inNCPDP && Comment != '' ";
  $sql .= " && ( Date_From <= '$ReportMonth' && Date_To >= '$ReportMonth' ) ";
  $sql .= " ORDER BY Title, Comment";

  ($sqlout = $sql) =~ s/\n/<br>\n/g;

  $getSpecComments  = $dbx->prepare("$sql");
  $getSpecComments->execute;

  my $NumOfRows = $getSpecComments->rows;
  
  if ($NumOfRows > 0) {
    while ( my @row = $getSpecComments->fetchrow_array() ) {
       my ($NCPDP, $Title, $Comment, $Date_From, $Date_To) = @row;
       print qq#<strong>$Title</strong><br />$Comment<br /><br />\n#;
    }
  }

  $getSpecComments->finish;

  $sql  = "SELECT Comments, DATE_FORMAT(Date, '%Y/%m') FROM $DBNAMERM.$TABLERM WHERE NCPDP=$inNCPDP && Comments != '' ";
  $sql .= "&& Date >= '$yearm2-01-01' ";
  $sql .= "ORDER BY Date DESC";

  ($sqlout = $sql) =~ s/\n/<br>\n/g;

  $getcomments  = $dbx->prepare("$sql");
  $getcomments->execute;

  my $NumOfRows = $getcomments->rows;
  
  if ($NumOfRows > 0) {
    while ( my @row = $getcomments->fetchrow_array() ) {
       $comment = "<UL>";
       my ($Comments, $Date) = @row;
       $Comments =~ s/^\s+|\s+$//g; ##Removes spaces at both ends
       $Comments =~ s/\<br \/\>//g; ##Removed old tags that gave us spacing.  
       my @tmp = split(/\n/,$Comments);
       foreach $pc (@tmp) {
          $pc =~ s/^\s+|\s+$//g; ##Removes spaces at both ends
         $comment .= "<LI>$pc</LI>" if ($pc);
       }
       $comment .= "</UL>";
       print qq#<strong>$Date</strong><br />$comment<br /><br />\n#;
    }
  } 

  print qq#</div> <!-- end sidebarWrapper -->\n#;
  print qq#</div> <!-- end sidebar -->\n#;

  $getcomments->finish;
}

#______________________________________________________________________________

sub readSummaries {
  
  $TABLE = "summaries";

  my $sql = "
  SELECT NCPDP, Date, Script_Count, Sales, Gross_Margin, Gross_Margin_Percent, Average_Sale_Per_Script, Average_Gross_Margin_Per_Script, Patient_Info, Disclaimer 
  FROM $DBNAMERM.$TABLE 
  WHERE 1=1 
  && Pharmacy_ID = $Pharmacy_ID
  && Date LIKE '%$ReportMonth%' 
  ";

  ($sqlout = $sql) =~ s/\n/<br>\n/g;

  $sthx  = $dbx->prepare("$sql");
  $sthx->execute;

  my $NumOfRows = $sthx->rows;

  while ( my @row = $sthx->fetchrow_array() ) {

     my ( $sNCPDP, $sDate, $sScript_Count, $sSales, $sGross_Margin, $sGross_Margin_Percent, $sAverage_Sale_Per_Script, $sAverage_Gross_Margin_Per_Script, $sPatient_Info, $sDisclaimer) = @row;
 
     $RepKey                             = "$Pharmacy_ID##$sDate";
     $Rep_MWType{$RepKey}                = "Summary";
     $Rep_sDate{$RepKey}                 = $sDate;
     $Rep_sScript_Count{$RepKey}         = $sScript_Count;
     $Rep_sSales{$RepKey}                = $sSales;
     $Rep_sGross_Margin{$RepKey}         = $sGross_Margin;
     $Rep_sGross_Margin_Percent{$RepKey} = $sGross_Margin_Percent;
     $Rep_sAverage_Sale_Per_Script{$RepKey} = $sAverage_Sale_Per_Script;
     $Rep_sAverage_Gross_Margin_Per_Script{$RepKey} = $sAverage_Gross_Margin_Per_Script;
     $Rep_sPatient_Info{$RepKey}         = $sPatient_Info;
     $Rep_sDisclaimer{$RepKey}           = $sDisclaimer;

  }
  $sthx->finish;
}

#______________________________________________________________________________

sub build_mainchart {

print <<BM;

<!-- Line Chart Generation -->

<script type="text/javascript">
\$(function () {
  var chart;
  \$(document).ready(function() {
    chart = new Highcharts.Chart({
      chart: {
        renderTo: '$container',
        type: 'line',
        marginRight: $marginright,
        marginBottom: 24,
        width: null,
        height: null
      },
      credits: {
        enabled: false
      },
      title: {
        text: '$type',
        x: -20 //center
      },
      xAxis: {
        categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        labels: {
          rotation: $rotation
        }
      },
      yAxis: {
        gridLineWidth: 2,
        title: {
          text: '$yaxistitle'
        },
        plotLines: [{
          value: 0,
          width: 1,
          color: '#808080'
        }],
        minPadding: 0.5,
        maxPadding: 0.5
      },
      tooltip: {
        formatter: function() {
          var s = 'Month: '+ this.x;

          \$.each(this.points, function(i, point) {
            s += '<br/>'+'<b>'+ point.series.name +'</b>: '+
            Highcharts.numberFormat(this.y,$decimalplaces);
          });

          return s;
        },
        shared: true,
        borderColor: '#000000',
        crosshairs: true
      },
      legend: {
        enabled: $legend,
        layout: 'vertical',
        align: 'right',
        verticalAlign: 'top',
        x: -20,
        y:  50,
        borderWidth: 0
      },
      plotOptions: {
        series: {
          animation: false
        }
      },
      series: [{
        name: '$yearm2',
        color: '#c0504d',
        data: [$data{"$ym2##01"}, $data{"$ym2##02"}, $data{"$ym2##03"}, $data{"$ym2##04"}, $data{"$ym2##05"}, $data{"$ym2##06"}, $data{"$ym2##07"}, $data{"$ym2##08"}, $data{"$ym2##09"}, $data{"$ym2##10"}, $data{"$ym2##11"}, $data{"$ym2##12"}]
      }, {
        name: '$yearm1',
        color: '#9bbb59',
        data: [$data{"$ym1##01"}, $data{"$ym1##02"}, $data{"$ym1##03"}, $data{"$ym1##04"}, $data{"$ym1##05"}, $data{"$ym1##06"}, $data{"$ym1##07"}, $data{"$ym1##08"}, $data{"$ym1##09"}, $data{"$ym1##10"}, $data{"$ym1##11"}, $data{"$ym1##12"}]
      }, {
      name: '$yearcur',
        color: '#4f81bd',
        data: [$data{"$ymc##01"}, $data{"$ymc##02"}, $data{"$ymc##03"}, $data{"$ymc##04"}, $data{"$ymc##05"}, $data{"$ymc##06"}, $data{"$ymc##07"}, $data{"$ymc##08"}, $data{"$ymc##09"}, $data{"$ymc##10"}, $data{"$ymc##11"}, $data{"$ymc##12"}]
      }]
    });
  });
});
</script>

BM

}

#______________________________________________________________________________

sub build_mainchart_stacked {

#Uses Quarterly data to build stacks.
  
print <<BMS;

<!-- Stacked Chart Generation -->

<script type="text/javascript">
\$(function () {
  \$('#$container').highcharts({
    chart: {
      type: 'column',
      marginRight: 0,
      marginLeft: 100,
      marginBottom: 24      
    },
    credits: {
      enabled: false
    },
    title: {
      text: '$type',
      x: 20 //center
    },
    xAxis: {
      categories: ['$yearm2', '$yearm1', '$yearcur']
    },
    yAxis: {
      min: 0,
      title: {
        text: '$type',
        x: 0 //center
      },
      stackLabels: {
        enabled: true,
        style: {
          fontWeight: 'bold',
          color: 'gray'
        },
        formatter: function() {
          return Highcharts.numberFormat(Math.round(this.total), 0);
        }
      }
    },
    legend: {
      enabled: false,
      align: 'right',
      x: 10,
      verticalAlign: 'top',
      y: 0,
      floating: false,
      backgroundColor: 'white',
      borderColor: '#CCC',
      borderWidth: 1,
      shadow: false
    },
    tooltip: {
      //shared: true,
      formatter: function() {
        var display = '<b>'+ this.x +'</b><br/>'+
        '<b>'+this.series.name+'</b>'+': ' + Highcharts.numberFormat(this.y, 0) +'<br/>'+
        'Year: '+ Highcharts.numberFormat(this.point.stackTotal, 0);

        return display;
      },
      backgroundColor: 'white',
      borderColor: '#000',
      borderWidth: 1
    },
    plotOptions: {
      column: {
        stacking: 'normal',
        dataLabels: {
          enabled: true,
          color: 'black',
          crop: false,
          formatter: function() {
            if (this.y != null) {
              return this.series.name + ': ' + (1000*Math.round((this.y)/1000))/1000 + 'k';
            }
          }
        }
      }
    },
    series: [{
      name: 'Q4',
      color: '#FFF',
      borderWidth: 2,
      borderColor: '#000',
      data: [$data{"${ym2}##Q4"}, $data{"${ym1}##Q4"}, $data{"${ymc}##Q4"}],
      pointPadding: 0.1,
      groupPadding: 0
    }, {
      name: 'Q3',
      color: '#FFF',
      borderWidth: 2,
      borderColor: '#4f81bd',
      data: [$data{"${ym2}##Q3"}, $data{"${ym1}##Q3"}, $data{"${ymc}##Q3"}],
      pointPadding: 0.1,
      groupPadding: 0
    }, {
      name: 'Q2',
      color: '#FFF',
      borderWidth: 2,
      borderColor: '#9bbb59',
      data: [$data{"${ym2}##Q2"}, $data{"${ym1}##Q2"}, $data{"${ymc}##Q2"}],
      pointPadding: 0.1,
      groupPadding: 0
    }, {
      name: 'Q1',
      color: '#FFF',
      borderWidth: 2,
      borderColor: '#c0504d',
      data: [$data{"${ym2}##Q1"}, $data{"${ym1}##Q1"}, $data{"${ymc}##Q1"}],
      pointPadding: 0.1,
      groupPadding: 0
    }]
  });
});
  
</script>

BMS

}

#______________________________________________________________________________

sub build_mainchart_stacked2 {

#Uses Monthly data to build stacks.
  
print <<BMS;

<!-- Stacked Chart Generation -->

<script type="text/javascript">
\$(function () {
  \$('#$container').highcharts({
    chart: {
      type: 'column',
      marginRight: 0,
      marginLeft: 100,
      marginBottom: 24      
    },
    credits: {
      enabled: false
    },
    title: {
      text: '$type',
      x: 20 //center
    },
    xAxis: {
      categories: ['$yearm2', '$yearm1', '$yearcur']
    },
    yAxis: {
      min: 0,
      title: {
        text: '$type',
        x: 0 //center
      },
      stackLabels: {
        enabled: true,
        style: {
          fontWeight: 'bold',
          color: 'gray'
        },
        formatter: function() {
          return Highcharts.numberFormat(Math.round(this.total), 0);
        }
      }
    },
    legend: {
      enabled: false
    },
    tooltip: {
        pointFormat: '<span style="color:#000;">{series.name}</span>: <b>{point.y}</b><br/>',
        shared: false
    },
    plotOptions: {
      column: {
        stacking: 'normal',
        dataLabels: {
          enabled: true,
          color: 'black',
          formatter: function () {
		    if (this.series.name == 'YTD') {
              	return Highcharts.numberFormat(Math.round(this.y), 0);
            }
          }
        }
      }
    },
    series: [{
      name: 'Remaining',
      color: '#FFF',
      borderWidth: 2,
      borderColor: '#2f73d8',
      data: [$data{"${ym2}##R"}, $data{"${ym1}##R"}, $data{"${ymc}##R"}]
    }, {
      name: 'YTD',
      color: '#FFF',
      borderWidth: 2,
      borderColor: '#0d233a',
      data: [$data{"${ym2}##T"}, $data{"${ym1}##T"}, $data{"${ymc}##T"}]
    }]
  });
});
  
</script>

BMS

}

#______________________________________________________________________________


sub SalesByPayer {

  $showPlansMAX = 25; ## 25-27 total with CASH and RedeemRx
  
  my $NCPDP   = $inNCPDP || $dispNCPDP;
  my $sbp_data_present = 0;

  my $rmonth;

  $rmonth = sprintf("%02d", $inMonth);

  my $sql = "SELECT ncpdp FROM rbsreporting.sales_by_payer_tds WHERE NCPDP = $NCPDP && Year = $jyear && Qtr_YTD = $inMonth";

  $checkData  = $dbx->prepare("$sql");
  $checkData->execute;
  $sbp_data_present = $checkData->rows;
  $checkData->finish;

  if ($sbp_data_present > 0) {
    print qq#<div class="page">#;
    print qq#<div class="page_header"><h3>Sales by Payer - $Pharmacy_Name</h3></div><br />#;

    $timeframe     = "date >= '${yearcur}-01-01' && date <= '${yearcur}-${rmonth}-31' ";
    $timeframehist = "date >= '${yearm1}-01-01'  && date <= '${yearm1}-${rmonth}-31' ";
    
    $sql = "

    SELECT * FROM (
      SELECT * FROM (
        SELECT Plan, 
               (Brand_Count + Generic_Count) Count,
               (Generic_Count) Generic_Count,
               ROUND((( Generic_Count /(Generic_Count + Brand_Count))*100), 1) GDR_Percent,
               FORMAT((Brand_Sale + Generic_Sale),0) Sales, 
               FORMAT((((Brand_Sale + Generic_Sale) / 
                 (SELECT sum(Total_Brand_Revenue + Total_Generic_Revenue) 
                    FROM rbsreporting.monthly 
                   WHERE NCPDP = $NCPDP && $timeframe
                 )
               )*100), 1) Percent, 

               FORMAT(((Brand_Sale + Generic_Sale) - ((Brand_Cost) + (Generic_Cost))), 0) GM, 
               FORMAT(((((Brand_Sale + Generic_Sale) - ((Brand_Cost) + (Generic_Cost)))/(Brand_Sale + Generic_Sale))*100), 1) GM_Percent, 
               FORMAT(((Brand_Sale + Generic_Sale) / (Brand_Count + Generic_Count)), 2) Sale_Per_Script, 
               FORMAT((((Brand_Sale + Generic_Sale) - ((Brand_Cost) + (Generic_Cost))) / (Brand_Count + Generic_Count)), 2) GM_Per_Script, 
               FORMAT((Days_Supply / (Days_Supply_Count)), 1) Avg_Days_Supply 

          FROM rbsreporting.sales_by_payer_tds
         WHERE NCPDP = $NCPDP && Year = $jyear && Qtr_YTD = $inMonth
            && Plan IN ('CASH', 'RedeemRx')
      ) a
      UNION
      SELECT * FROM (
        SELECT Plan, 
               (Brand_Count + Generic_Count) Count,
               (Generic_Count) Generic_Count,
               ROUND((( Generic_Count /(Generic_Count + Brand_Count))*100), 1) GDR_Percent,
               FORMAT((Brand_Sale + Generic_Sale),0) Sales, 
               FORMAT((((Brand_Sale + Generic_Sale) / 
                 (SELECT sum(Total_Brand_Revenue + Total_Generic_Revenue) 
                    FROM rbsreporting.monthly 
                   WHERE NCPDP = $NCPDP && $timeframe
                 )
               )*100), 1) Percent, 
               FORMAT(((Brand_Sale + Generic_Sale) - ((Brand_Cost) + (Generic_Cost))), 0) GM, 
               FORMAT(((((Brand_Sale + Generic_Sale) - ((Brand_Cost) + (Generic_Cost)))/(Brand_Sale + Generic_Sale))*100), 1) GM_Percent, 
               FORMAT(((Brand_Sale + Generic_Sale) / (Brand_Count + Generic_Count)), 2) Sale_Per_Script, 
               FORMAT((((Brand_Sale + Generic_Sale) - ((Brand_Cost) + (Generic_Cost))) / (Brand_Count + Generic_Count)), 2) GM_Per_Script, 
               FORMAT((Days_Supply / (Days_Supply_Count)), 1) Avg_Days_Supply 

          FROM rbsreporting.sales_by_payer_tds 
         WHERE NCPDP = $NCPDP && Year = $jyear && Qtr_YTD = $inMonth
         ORDER BY (Brand_Sale + Generic_Sale) DESC 
         LIMIT $showPlansMAX 
      ) b
    ) c
    ORDER BY REPLACE(Sales, ',', '')+0 DESC
    ";
  
    ($sqlout = $sql) =~ s/\n/<br>\n/g;
    ##print "Sales By Payer sql: $sqlout<br>\n";
  
    $getSBPdata = $dbx->prepare("$sql");
    $getSBPdata->execute;
    $SBPNumOfRows = $getSBPdata->rows;
    if ($SBPNumOfRows > 0) {
      my $shown_count = 0;
      my $shown_total = 0;
      my $generic_count_total = 0;
      my $shown_percent = 0;
      my $shown_gm = 0;
      print "<table class=\"tableizer-table\">";
      print "<tr><th>Plan</th><th>Rx Count</th><th>GDR</th><th>Sales</th><th>% of Sales</th><th>Sale/ Script</th><th>Avg. Days Supply</th></tr>";
      while ( my @row = $getSBPdata->fetchrow_array() ) {
        my ($plan, $count, $generic_count, $gdr_percent, $sales, $percent, $gm, $gm_percent, $sale_per_script, $gm_per_script, $avg_day_supply) = @row;
        my $count_disp = commify($count);
    
        #Exception to blank out GM values for stores with BAD DATA
        if ($yearcur <= 2014 && $NCPDP =~ /1912751|2601993|2586521|2638053|2601917/) {
          $gm = 0;
          $gm_percent = 0;
          $gm_per_script = 0;
        }
    
        print "<tr><td style=\"text-align: left;\">$plan</td><td>$count_disp</td><td>$gdr_percent%</td><td>\$$sales</td><td>$percent%</td><td>\$$sale_per_script</td><td>$avg_day_supply</td></tr>";
        $shown_count   += $count;
        $generic_count_total += $generic_count;
        $sales =~ s/,//g;
        $shown_total   += $sales;
        $shown_percent += $percent;
        $gm =~ s/,//g;
        $shown_gm      += $gm;
      }
      
      ### Sales, Rebated Cost, Count by year as reported by us.
      $sql = "
      SELECT sum(Total_Brand_Revenue + Total_Generic_Revenue) as Sales, 
      sum( 
      (case when Brand_Rebate IS NOT NULL then (Total_Brand_Cost*(1 - Brand_Rebate)) else Total_Brand_Cost end) + 
      (case when Generic_Rebate IS NOT NULL then (Total_Generic_Cost*(1 - Generic_Rebate)) else Total_Generic_Cost end) 
      ) as Rebated_Cost,
      sum(Total_Brand + Total_Generic) as Count,
      ROUND(((SUM(Total_Generic) / (SUM(Total_Generic) + SUM(Total_Brand)))*100),1) as Total_GDR_Perent
      FROM ( 
      SELECT NCPDP, date, date_format(date, '%Y%m') as datef, Total_Brand_Revenue, Total_Generic_Revenue, Total_Brand_Cost, Total_Generic_Cost, Total_Brand, Total_Generic
      FROM rbsreporting.monthly 
      WHERE 
      NCPDP = $NCPDP && $timeframe 
      ) pharm 
      LEFT JOIN (SELECT NCPDP, YYYYMM, Brand_Rebate, Generic_Rebate FROM rbsreporting.rebates) rebates 
      ON (pharm.NCPDP = rebates.NCPDP && BINARY pharm.datef = BINARY YYYYMM)
      ;
      ";
      $getTotalSales = $dbx->prepare("$sql");
      $getTotalSales->execute;
      $NumOfRows = $getTotalSales->rows;
      if ($NumOfRows > 0) {
        while ( my @row = $getTotalSales->fetchrow_array() ) {
          ($total_rx_sales, $total_rx_cost, $total_rx_count, $total_gdr_percent) = @row;
        }
      }
      $getTotalSales->finish;
    
      ### Use OUR reported numbers for totals, not Sales By Payer actual totals
      $reported_total_gm = $total_rx_sales - $total_rx_cost;
      $total_count = $total_rx_count;
      $total_gm = $reported_total_gm;
    
      my $total_count_LESS_shown_count = ($total_count - $shown_count) || 1;
      my $other_sale_per_script = commify(sprintf "%.2f", (($total_rx_sales - $shown_total)/$total_count_LESS_shown_count));
      my $other_gm_per_script   = commify(sprintf "%.2f", (($total_gm - $shown_gm)/$total_count_LESS_shown_count));
      my $other_count           = commify($total_count - $shown_count);
      my $other_gm_percent      = commify(sprintf "%.1f", ((($total_gm - $shown_gm)/($total_rx_sales - $shown_total))*100));
      my $other_total           = commify(sprintf "%.0f", ($total_rx_sales - $shown_total));
      my $other_percent         = sprintf "%.1f", (100 - $shown_percent);
      my $other_gm              = commify(sprintf "%.0f", ($total_gm - $shown_gm));
    
      #Exception to blank out GM values for stores with BAD DATA
      if ($yearcur <= 2014 && $NCPDP =~ /1912751|2601993|2586521|2638053|2601917/) {
        $other_gm = 0;
        $other_gm_percent = 0;
        $other_gm_per_script = 0;
      }
    
      if ( $SBPNumOfRows >= $showPlansMAX ) {
      }
    
      print "<tr><th colspan=10>&nbsp;</th></tr>";
    
      $total_sale_per_script = commify(sprintf "%.2f", ($total_rx_sales/$total_count));
      $total_gm_per_script   = commify(sprintf "%.2f", ($total_gm/$total_count));
      $total_count           = commify($total_count);
      $total_gm_percent      = commify(sprintf "%.1f", (($total_gm/$total_rx_sales)*100));
      $ymc_annual_total_rx_sales = $total_rx_sales;
      # jlh. 05/07/2015
      $total_rx_sales        = commify(sprintf "%.0f", $total_rx_sales);
      $total_gm              = commify(sprintf "%.0f", $total_gm);
    
      $total_percent         = sprintf "%.1f", (100); #Always 100.0%
    
      #Exception to blank out GM values for stores with BAD DATA
      if ($yearcur <= 2014 && $NCPDP =~ /1912751|2601993|2586521|2638053|2601917/) {
        $total_gm = 0;
        $total_gm_percent = 0;
        $total_gm_per_script = 0;
      }
    
      #Total Row
      print "<tr><td style=\"text-align: left;\">Totals (YTD)</td><td>$total_count</td><td>$total_gdr_percent%</td><td>\$$total_rx_sales</td><td>$total_percent%</td><td>\$$total_sale_per_script</td><td>---</td></tr>";
    
    
      ### Sales, Rebated Cost, Count by year as reported by us.
      $sql = "
      SELECT sum(Total_Brand_Revenue + Total_Generic_Revenue) as Sales, 
      sum( 
      (case when Brand_Rebate IS NOT NULL then (Total_Brand_Cost*(1 - Brand_Rebate)) else Total_Brand_Cost end) + 
      (case when Generic_Rebate IS NOT NULL then (Total_Generic_Cost*(1 - Generic_Rebate)) else Total_Generic_Cost end) 
      ) as Rebated_Cost,
      sum(Total_Brand + Total_Generic) as Count,
      ROUND(((SUM(Total_Generic) / (SUM(Total_Generic) + SUM(Total_Brand)))*100),1) as Total_GDR_Percent
      FROM ( 
      SELECT NCPDP, date, date_format(date, '%Y%m') as datef, Total_Brand_Revenue, Total_Generic_Revenue, Total_Brand_Cost, Total_Generic_Cost, Total_Brand, Total_Generic
      FROM rbsreporting.monthly 
      WHERE 
      NCPDP = $NCPDP && $timeframehist
      ) pharm 
      LEFT JOIN (SELECT NCPDP, YYYYMM, Brand_Rebate, Generic_Rebate FROM rbsreporting.rebates) rebates 
      ON (pharm.NCPDP = rebates.NCPDP && BINARY pharm.datef = BINARY YYYYMM)
      ;
      ";
      $getTotalSalesHist = $dbx->prepare("$sql");
      $getTotalSalesHist->execute;
      $NumOfRows = $getTotalSalesHist->rows;
      if ($NumOfRows > 0) {
        while ( my @row = $getTotalSalesHist->fetchrow_array() ) {
          ($total_rx_sales_hist, $total_rx_cost_hist, $total_rx_count_hist, $total_gdr_percent_hist) = @row;
        }
      }
      $getTotalSalesHist->finish;
    
      $reported_total_gm_hist = $total_rx_sales_hist - $total_rx_cost_hist;
    
      if ($total_rx_count_hist > 0) {
        $total_sale_per_script_hist = commify(sprintf "%.2f", ($total_rx_sales_hist/$total_rx_count_hist));
        $total_gm_per_script_hist   = commify(sprintf "%.2f", ($reported_total_gm_hist/$total_rx_count_hist));
      } else {
        $total_sale_per_script_hist = 0;
        $total_gm_per_script_hist = 0;
      }
      
      if ($total_rx_count_hist > 0) {
        $total_count_hist           = commify($total_rx_count_hist);
      } else {
        $total_count_hist = 0;
      }
    
      if ($total_rx_sales_hist > 0) {
        $total_gm_percent_hist      = commify(sprintf "%.1f", (($reported_total_gm_hist/$total_rx_sales_hist)*100));
        $total_rx_sales_hist        = commify(sprintf "%.0f", $total_rx_sales_hist);
      } else {
        $total_gm_percent_hist = 0;
        $total_rx_sales_hist = 0;
      }
    
        $total_gm_hist              = commify(sprintf "%.0f", $reported_total_gm_hist);
    
        $total_percent_hist         = sprintf "%.1f", (100); #Always 100.0%

    
      #Exception to blank out GM values for stores with BAD DATA
      if ($yearcur <= 2014 && $NCPDP =~ /1912751|2601993|2586521|2638053|2601917/) {
        $total_gm_hist = 0;
        $total_gm_percent_hist = 0;
        $total_gm_per_script_hist = 0;
      }
    
      #Total Row - Last Year
      print "<tr><td style=\"text-align: left;\">Prior Year</td><td>$total_count_hist</td><td>$total_gdr_percent_hist%</td><td>\$$total_rx_sales_hist</td><td>---</td><td>\$$total_sale_per_script_hist</td><td>---</td></tr>";  
    
      print "</table>";
    }
    $getSBPdata->finish;
    print "</div>"; #End Page
    
  }
  
}

#______________________________________________________________________________

sub RBSAverages {

   my $NCPDP = $inNCPDP || $dispNCPDP;
   my $YEAR  = $year-1; #Current year, minus 1, financials are a year behind
   
   my $class = "";

   my $sql  = "
SELECT
RowType, Pharmacy_Name, NCPDP, Pharmacy_Type, Location, Size, format(Total_Count,0), Brand_Count, Generic_Count, concat('\$', format(Total_Sale,0)), Brand_Sale, Generic_Sale, concat('\$', format(Total_GM,0)), Brand_GM, Generic_GM, Total_GM_Percent, Brand_GM_Percent, Generic_GM_Percent, Total_Sale_Per_Script, Brand_Sale_Per_Script, Generic_Sale_Per_Script, Total_GM_Per_Script, Brand_GM_Per_Script, Generic_GM_Per_Script, Unique_Patients, Average_Unique_Patients, Average_Scripts_Per_Unique_Patient, Average_Sale_Per_Unique_Patient, Average_GM_Per_Unique_Patient, New_Claim_Count, New_Claim_Sales, Refill_Claim_Count, Refill_Claim_Sales, Controlled_Count_ALL, Controlled_Count_ALL_Percent, Controlled_Sale_ALL, Controlled_Sale_ALL_Percent, Legent_Count_ALL, Legent_Count_ALL_Percent, Legend_Sale_ALL, Legend_Sale_ALL_Percent, Controlled_Count_CASH, Controlled_Count_CASH_Percent, Controlled_Sale_CASH, Controlled_Sale_CASH_Percent, Legent_Count_CASH, Legent_Count_CASH_Percent, Legend_Sale_CASH, Legend_Sale_CASH_Percent
FROM rbsreporting.rbs_averages
WHERE 1=1
&& RowType = 'L'
&& NCPDP   = $NCPDP
&& YYYYMM  = '$doMonth'
";

   ($sqlout = $sql) =~ s/\n/<br>\n/g;

   $checkData  = $dbx->prepare("$sql");
   $checkData->execute;
   $rowsfound = $checkData->rows;
  
   if ($rowsfound > 0) {
  
      while ( my @row = $checkData->fetchrow_array() ) {
    
         my (
$RowType,$Pharmacy_Name,$NCPDP,$Pharmacy_Type,$Location,$Size,$Total_Count,$Brand_Count,$Generic_Count,$Total_Sale,$Brand_Sale,$Generic_Sale,$Total_GM,$Brand_GM,$Generic_GM,$Total_GM_Percent,$Brand_GM_Percent,$Generic_GM_Percent,$Total_Sale_Per_Script,$Brand_Sale_Per_Script,$Generic_Sale_Per_Script,$Total_GM_Per_Script,$Brand_GM_Per_Script,$Generic_GM_Per_Script,$Unique_Patients,$Average_Unique_Patients,$Average_Scripts_Per_Unique_Patient,$Average_Sale_Per_Unique_Patient,$Average_GM_Per_Unique_Patient,$New_Claim_Count,$New_Claim_Sales,$Refill_Claim_Count,$Refill_Claim_Sales,$Controlled_Count_ALL,$Controlled_Count_ALL_Percent,$Controlled_Sale_ALL,$Controlled_Sale_ALL_Percent,$Legent_Count_ALL,$Legent_Count_ALL_Percent,$Legend_Sale_ALL,$Legend_Sale_ALL_Percent,$Controlled_Count_CASH,$Controlled_Count_CASH_Percent,$Controlled_Sale_CASH,$Controlled_Sale_CASH_Percent,$Legent_Count_CASH,$Legent_Count_CASH_Percent,$Legend_Sale_CASH,$Legend_Sale_CASH_Percent
) = @row;

         $key = $NCPDP;
         $RowTypes{$key}                            = $RowType;
         $Pharmacy_Names{$key}                      = $Pharmacy_Name;
         $NCPDPs{$key}                              = $NCPDP;
         $Pharmacy_Types{$key}                      = $Pharmacy_Type;
         $Locations{$key}                           = $Location;
         $Sizes{$key}                               = $Size;
         $Total_Counts{$key}                        = $Total_Count;
         $Brand_Counts{$key}                        = $Brand_Count;
         $Generic_Counts{$key}                      = $Generic_Count;
         $Total_Sales{$key}                         = $Total_Sale;
         $Brand_Sales{$key}                         = $Brand_Sale;
         $Generic_Sales{$key}                       = $Generic_Sale;
         $Total_GMs{$key}                           = $Total_GM;
         $Brand_GMs{$key}                           = $Brand_GM;
         $Generic_GMs{$key}                         = $Generic_GM;
         $Total_GM_Percents{$key}                   = $Total_GM_Percent;
         $Brand_GM_Percents{$key}                   = $Brand_GM_Percent;
         $Generic_GM_Percents{$key}                 = $Generic_GM_Percent;
         $Total_Sale_Per_Scripts{$key}              = $Total_Sale_Per_Script;
         $Brand_Sale_Per_Scripts{$key}              = $Brand_Sale_Per_Script;
         $Generic_Sale_Per_Scripts{$key}            = $Generic_Sale_Per_Script;
         $Total_GM_Per_Scripts{$key}                = $Total_GM_Per_Script;
         $Brand_GM_Per_Scripts{$key}                = $Brand_GM_Per_Script;
         $Generic_GM_Per_Scripts{$key}              = $Generic_GM_Per_Script;
         $Unique_Patients{$key}                     = $Unique_Patients;
         $Average_Unique_Patientss{$key}            = $Average_Unique_Patients;
         $Average_Scripts_Per_Unique_Patients{$key} = $Average_Scripts_Per_Unique_Patient;
         $Average_Sale_Per_Unique_Patients{$key}    = $Average_Sale_Per_Unique_Patient;
         $Average_GM_Per_Unique_Patients{$key}      = $Average_GM_Per_Unique_Patient;
         $New_Claim_Counts{$key}                    = $New_Claim_Count;
         $New_Claim_Saless{$key}                    = $New_Claim_Sales;
         $Refill_Claim_Counts{$key}                 = $Refill_Claim_Count;
         $Refill_Claim_Saless{$key}                 = $Refill_Claim_Sales;
         $Controlled_Count_ALLs{$key}               = $Controlled_Count_ALL;
         $Controlled_Count_ALL_Percents{$key}       = $Controlled_Count_ALL_Percent;
         $Controlled_Sale_ALLs{$key}                = $Controlled_Sale_ALL;
         $Controlled_Sale_ALL_Percents{$key}        = $Controlled_Sale_ALL_Percent;
         $Legent_Count_ALLs{$key}                   = $Legent_Count_ALL;
         $Legent_Count_ALL_Percents{$key}           = $Legent_Count_ALL_Percent;
         $Legend_Sale_ALLs{$key}                    = $Legend_Sale_ALL;
         $Legend_Sale_ALL_Percents{$key}            = $Legend_Sale_ALL_Percent;
         $Controlled_Count_CASHs{$key}              = $Controlled_Count_CASH;
         $Controlled_Count_CASH_Percents{$key}      = $Controlled_Count_CASH_Percent;
         $Controlled_Sale_CASHs{$key}               = $Controlled_Sale_CASH;
         $Controlled_Sale_CASH_Percents{$key}       = $Controlled_Sale_CASH_Percent;
         $Legent_Count_CASHs{$key}                  = $Legent_Count_CASH;
         $Legent_Count_CASH_Percents{$key}          = $Legent_Count_CASH_Percent;
         $Legend_Sale_CASHs{$key}                   = $Legend_Sale_CASH;
         $Legend_Sale_CASH_Percent{$key}            = $Legend_Sale_CASH_Percent;

         &loadSummaries($NCPDP, $Pharmacy_Type, $Location);
         &loadRegions($NCPDP, $Pharmacy_Type, $Location, $Size);
         &loadSizes($NCPDP, $Pharmacy_Type, $Location, $Size);

      }
   } else {
     print "No Rows found for NCPDP $NCPDP<br>\n";
   }
   $checkData->finish;
  
   print qq#<div class="page">#;
   print qq#<div class="page_header"><h3>$inYear RBS Averages - $Pharmacy_Name</h3></div><br />#;
 
   print qq#<table class="tableizer-table">\n#;
   
   $F1FMT = "%0.01f";		# One Decimal,  NO Dollar Sign
   $F2FMT = "%0.02f";		# Two Decimals, NO Dollar Sign
   $DSFMT = "\$%0.02f";		# Two Decimals WITH Dollar Sign
   $PCFMT = "%0.01f\%";

#  -------------------
   ($TMP_Generic_Count            = $Generic_Counts{$key})           =~ s/,|\$//g;
   ($TMP_Total_Count              = $Total_Counts{$key})             =~ s/,|\$//g;
   ($TMP_Refill_Claim_Count       = $Refill_Claim_Counts{$key})      =~ s/,|\$//g;
   ($TMP_Controlled_Count_ALL     = $Controlled_Count_ALLs{$key})    =~ s/,|\$//g;
   ($TMP_Total_Sales              = $Total_Sales{$key})              =~ s/,|\$//g;
   ($TMP_Generic_Sales            = $Generic_Sales{$key})            =~ s/,|\$//g;
   ($TMP_Refill_Claim_Sales       = $Refill_Claim_Saless{$key})      =~ s/,|\$//g;
   ($TMP_Controlled_Sale_ALL      = $Controlled_Sale_ALLs{$key})     =~ s/,|\$//g;
   ($TMP_Total_GMs                = $Total_GMs{$key})                =~ s/,|\$|\$//g;
   ($TMP_Generic_GMs              = $Generic_GMs{$key})              =~ s/,|\$//g;
   ($TMP_Total_GM_Percents        = $Total_GM_Percents{$key})        =~ s/,|\$//g;
   ($TMP_Brand_GM_Percents        = $Brand_GM_Percents{$key})        =~ s/,|\$//g * 100;
   ($TMP_Generic_GM_Percents      = $Generic_GM_Percents{$key})      =~ s/,|\$//g;
   ($TMP_Total_Sale_Per_Scripts   = $Total_Sale_Per_Scripts{$key})   =~ s/,|\$//g;
   ($TMP_Brand_Sale_Per_Scripts   = $Brand_Sale_Per_Scripts{$key})   =~ s/,|\$//g;
   ($TMP_Generic_Sale_Per_Scripts = $Generic_Sale_Per_Scripts{$key}) =~ s/,|\$//g;
   ($TMP_Total_GM_Per_Scripts     = $Total_GM_Per_Scripts{$key})     =~ s/,|\$//g;
   ($TMP_Brand_GM_Per_Scripts     = $Brand_GM_Per_Scripts{$key})     =~ s/,|\$//g;
   ($TMP_Generic_GM_Per_Scripts   = $Generic_GM_Per_Scripts{$key})   =~ s/,|\$//g;
   ($TMP_Average_Scripts_Per_Unique_Patients = $Average_Scripts_Per_Unique_Patients{$key}) =~ s/,|\$//g;
   ($TMP_Average_Sale_Per_Unique_Patients    = $Average_Sale_Per_Unique_Patients{$key})    =~ s/,|\$//g;
   ($TMP_Average_GM_Per_Unique_Patients      = $Average_GM_Per_Unique_Patients{$key})      =~ s/,|\$//g;

   $TMP_Total_GM_Percents         = sprintf($PCFMT, $TMP_Total_GM_Percents * 100);
   $TMP_Brand_GM_Percents         = sprintf($PCFMT, $TMP_Brand_GM_Percents * 100);
   $TMP_Generic_GM_Percents       = sprintf($PCFMT, $TMP_Generic_GM_Percents * 100);
   $TMP_Total_Sale_Per_Scripts    = sprintf($DSFMT, $TMP_Total_Sale_Per_Scripts);
   $TMP_Brand_Sale_Per_Scripts    = sprintf($DSFMT, $TMP_Brand_Sale_Per_Scripts);
   $TMP_Generic_Sale_Per_Scripts  = sprintf($DSFMT, $TMP_Generic_Sale_Per_Scripts);
   $TMP_Total_GM_Per_Scripts      = sprintf($DSFMT, $TMP_Total_GM_Per_Scripts);
   $TMP_Brand_GM_Per_Scripts      = sprintf($DSFMT, $TMP_Brand_GM_Per_Scripts);
   $TMP_Generic_GM_Per_Scripts    = sprintf($DSFMT, $TMP_Generic_GM_Per_Scripts);

   $TMP_Average_Scripts_Per_Unique_Patients = sprintf($F1FMT, $TMP_Average_Scripts_Per_Unique_Patients);
   $TMP_Average_Sale_Per_Unique_Patients    = sprintf($DSFMT, $TMP_Average_Sale_Per_Unique_Patients);
   $TMP_Average_GM_Per_Unique_Patients      = sprintf($DSFMT, $TMP_Average_GM_Per_Unique_Patients);

   if ( $TMP_Total_Count == 0 ) {
      $PCT_Generic              = "UNDEF";
      $PCT_Refill               = "UNDEF";
      $PCT_Controlled_Count_ALL = "UNDEF";
   } else {
      $PCT_Generic               = sprintf($PCFMT, ($TMP_Generic_Count        / $TMP_Total_Count) * 100 );
      $PCT_Refill                = sprintf($PCFMT, ($TMP_Refill_Claim_Count   / $TMP_Total_Count) * 100 );
      $PCT_Controlled_Count_ALL  = sprintf($PCFMT, ($TMP_Controlled_Count_ALL / $TMP_Total_Count) * 100 );
   }

   if ( $TMP_Total_Sales == 0 ) {
      $PCT_Generic_Sales       = "UNDEF";
      $PCT_Refill_Claim_Sales  = "UNDEF";
      $PCT_Controlled_Sale_ALL = "UNDEF";
   } else {
      $PCT_Generic_Sales       = sprintf($PCFMT, ($TMP_Generic_Sales       / $TMP_Total_Sales) * 100);
      $PCT_Refill_Claim_Sales  = sprintf($PCFMT, ($TMP_Refill_Claim_Sales  / $TMP_Total_Sales) * 100);
      $PCT_Controlled_Sale_ALL = sprintf($PCFMT, ($TMP_Controlled_Sale_ALL / $TMP_Total_Sales) * 100);
   }
   if ( $TMP_Total_GMs == 0 ) {
      $PCT_Generic_GMs         = "UNDEF";
   } else {
      $PCT_Generic_GMs         = sprintf($PCFMT, ($TMP_Generic_GMs         / $TMP_Total_GMs) * 100);
   }
#  -------------------
   ($SUM_TMP_Generic_Count            = $SUM_Generic_Counts{$key})           =~ s/,|\$SUM_//g;
   ($SUM_TMP_Total_Count              = $SUM_Total_Counts{$key})             =~ s/,|\$SUM_//g;
   ($SUM_TMP_Refill_Claim_Count       = $SUM_Refill_Claim_Counts{$key})      =~ s/,|\$SUM_//g;
   ($SUM_TMP_Controlled_Count_ALL     = $SUM_Controlled_Count_ALLs{$key})    =~ s/,|\$SUM_//g;
   ($SUM_TMP_Total_Sales              = $SUM_Total_Sales{$key})              =~ s/,|\$SUM_|\$//g;
   ($SUM_TMP_Generic_Sales            = $SUM_Generic_Sales{$key})            =~ s/,|\$SUM_//g;
   ($SUM_TMP_Refill_Claim_Sales       = $SUM_Refill_Claim_Saless{$key})      =~ s/,|\$SUM_//g;
   ($SUM_TMP_Controlled_Sale_ALL      = $SUM_Controlled_Sale_ALLs{$key})     =~ s/,|\$SUM_//g;
   ($SUM_TMP_Total_GMs                = $SUM_Total_GMs{$key})                =~ s/,|\$SUM_|\$//g;
   ($SUM_TMP_Generic_GMs              = $SUM_Generic_GMs{$key})              =~ s/,|\$SUM_//g;
   ($SUM_TMP_Total_GM_Percents        = $SUM_Total_GM_Percents{$key})        =~ s/,|\$SUM_//g;
   ($SUM_TMP_Brand_GM_Percents        = $SUM_Brand_GM_Percents{$key})        =~ s/,|\$SUM_//g;
   ($SUM_TMP_Generic_GM_Percents      = $SUM_Generic_GM_Percents{$key})      =~ s/,|\$SUM_//g;
   ($SUM_TMP_Total_Sale_Per_Scripts   = $SUM_Total_Sale_Per_Scripts{$key})   =~ s/,|\$SUM_//g;
   ($SUM_TMP_Brand_Sale_Per_Scripts   = $SUM_Brand_Sale_Per_Scripts{$key})   =~ s/,|\$SUM_//g;
   ($SUM_TMP_Generic_Sale_Per_Scripts = $SUM_Generic_Sale_Per_Scripts{$key}) =~ s/,|\$SUM_//g;
   ($SUM_TMP_Total_GM_Per_Scripts     = $SUM_Total_GM_Per_Scripts{$key})     =~ s/,|\$SUM_//g;
   ($SUM_TMP_Brand_GM_Per_Scripts     = $SUM_Brand_GM_Per_Scripts{$key})     =~ s/,|\$SUM_//g;
   ($SUM_TMP_Generic_GM_Per_Scripts   = $SUM_Generic_GM_Per_Scripts{$key})   =~ s/,|\$SUM_//g;
   ($SUM_TMP_Average_Scripts_Per_Unique_Patients = $SUM_Average_Scripts_Per_Unique_Patients{$key}) =~ s/,|\$SUM_//g;
   ($SUM_TMP_Average_Sale_Per_Unique_Patients    = $SUM_Average_Sale_Per_Unique_Patients{$key})    =~ s/,|\$SUM_//g;
   ($SUM_TMP_Average_GM_Per_Unique_Patients      = $SUM_Average_GM_Per_Unique_Patients{$key})      =~ s/,|\$SUM_//g;

   $SUM_TMP_Total_GM_Percents         = sprintf($PCFMT, $SUM_TMP_Total_GM_Percents * 100);
   $SUM_TMP_Brand_GM_Percents         = sprintf($PCFMT, $SUM_TMP_Brand_GM_Percents * 100);
   $SUM_TMP_Generic_GM_Percents       = sprintf($PCFMT, $SUM_TMP_Generic_GM_Percents * 100);
   $SUM_TMP_Total_Sale_Per_Scripts    = sprintf($DSFMT, $SUM_TMP_Total_Sale_Per_Scripts);
   $SUM_TMP_Brand_Sale_Per_Scripts    = sprintf($DSFMT, $SUM_TMP_Brand_Sale_Per_Scripts);
   $SUM_TMP_Generic_Sale_Per_Scripts  = sprintf($DSFMT, $SUM_TMP_Generic_Sale_Per_Scripts);
   $SUM_TMP_Total_GM_Per_Scripts      = sprintf($DSFMT, $SUM_TMP_Total_GM_Per_Scripts);
   $SUM_TMP_Brand_GM_Per_Scripts      = sprintf($DSFMT, $SUM_TMP_Brand_GM_Per_Scripts);
   $SUM_TMP_Generic_GM_Per_Scripts    = sprintf($DSFMT, $SUM_TMP_Generic_GM_Per_Scripts);

   $SUM_TMP_Average_Scripts_Per_Unique_Patients = sprintf($F1FMT, $SUM_TMP_Average_Scripts_Per_Unique_Patients);
   $SUM_TMP_Average_Sale_Per_Unique_Patients    = sprintf($DSFMT, $SUM_TMP_Average_Sale_Per_Unique_Patients);
   $SUM_TMP_Average_GM_Per_Unique_Patients      = sprintf($DSFMT, $SUM_TMP_Average_GM_Per_Unique_Patients);

   if ( $SUM_TMP_Total_Count == 0 ) {
      $SUM_PCT_Generic              = "UNDEF";
      $SUM_PCT_Refill               = "UNDEF";
      $SUM_PCT_Controlled_Count_ALL = "UNDEF";
   } else {
      $SUM_PCT_Generic               = sprintf($PCFMT, ($SUM_TMP_Generic_Count        / $SUM_TMP_Total_Count) * 100 );
      $SUM_PCT_Refill                = sprintf($PCFMT, ($SUM_TMP_Refill_Claim_Count   / $SUM_TMP_Total_Count) * 100 );
      $SUM_PCT_Controlled_Count_ALL  = sprintf($PCFMT, ($SUM_TMP_Controlled_Count_ALL / $SUM_TMP_Total_Count) * 100 );
   }

   if ( $SUM_TMP_Total_Sales == 0 ) {
      $SUM_PCT_Generic_Sales       = "UNDEF";
      $SUM_PCT_Refill_Claim_Sales  = "UNDEF";
      $SUM_PCT_Controlled_Sale_ALL = "UNDEF";
   } else {
      $SUM_PCT_Generic_Sales       = sprintf($PCFMT, ($SUM_TMP_Generic_Sales       / $SUM_TMP_Total_Sales) * 100);
      $SUM_PCT_Refill_Claim_Sales  = sprintf($PCFMT, ($SUM_TMP_Refill_Claim_Sales  / $SUM_TMP_Total_Sales) * 100);
      $SUM_PCT_Controlled_Sale_ALL = sprintf($PCFMT, ($SUM_TMP_Controlled_Sale_ALL / $SUM_TMP_Total_Sales) * 100);
   }

   if ( $SUM_TMP_Total_GMs == 0 ) {
      $SUM_PCT_Generic_GMs         = "UNDEF";
   } else {
      $SUM_PCT_Generic_GMs         = sprintf($PCFMT, ($SUM_TMP_Generic_GMs         / $SUM_TMP_Total_GMs) * 100);
   }
#  -------------------
   ($REG_TMP_Generic_Count            = $REG_Generic_Counts{$key})           =~ s/,|\$REG_//g;
   ($REG_TMP_Total_Count              = $REG_Total_Counts{$key})             =~ s/,|\$REG_//g;
   ($REG_TMP_Refill_Claim_Count       = $REG_Refill_Claim_Counts{$key})      =~ s/,|\$REG_//g;
   ($REG_TMP_Controlled_Count_ALL     = $REG_Controlled_Count_ALLs{$key})    =~ s/,|\$REG_//g;
   ($REG_TMP_Total_Sales              = $REG_Total_Sales{$key})              =~ s/,|\$REG_|\$//g;
   ($REG_TMP_Generic_Sales            = $REG_Generic_Sales{$key})            =~ s/,|\$REG_//g;
   ($REG_TMP_Refill_Claim_Sales       = $REG_Refill_Claim_Saless{$key})      =~ s/,|\$REG_//g;
   ($REG_TMP_Controlled_Sale_ALL      = $REG_Controlled_Sale_ALLs{$key})     =~ s/,|\$REG_//g;
   ($REG_TMP_Total_GMs                = $REG_Total_GMs{$key})                =~ s/,|\$REG_|\$//g;
   ($REG_TMP_Generic_GMs              = $REG_Generic_GMs{$key})              =~ s/,|\$REG_//g;
   ($REG_TMP_Total_GM_Percents        = $REG_Total_GM_Percents{$key})        =~ s/,|\$REG_//g;
   ($REG_TMP_Brand_GM_Percents        = $REG_Brand_GM_Percents{$key})        =~ s/,|\$REG_//g;
   ($REG_TMP_Generic_GM_Percents      = $REG_Generic_GM_Percents{$key})      =~ s/,|\$REG_//g;
   ($REG_TMP_Total_Sale_Per_Scripts   = $REG_Total_Sale_Per_Scripts{$key})   =~ s/,|\$REG_//g;
   ($REG_TMP_Brand_Sale_Per_Scripts   = $REG_Brand_Sale_Per_Scripts{$key})   =~ s/,|\$REG_//g;
   ($REG_TMP_Generic_Sale_Per_Scripts = $REG_Generic_Sale_Per_Scripts{$key}) =~ s/,|\$REG_//g;
   ($REG_TMP_Total_GM_Per_Scripts     = $REG_Total_GM_Per_Scripts{$key})     =~ s/,|\$REG_//g;
   ($REG_TMP_Brand_GM_Per_Scripts     = $REG_Brand_GM_Per_Scripts{$key})     =~ s/,|\$REG_//g;
   ($REG_TMP_Generic_GM_Per_Scripts   = $REG_Generic_GM_Per_Scripts{$key})   =~ s/,|\$REG_//g;
   ($REG_TMP_Average_Scripts_Per_Unique_Patients = $REG_Average_Scripts_Per_Unique_Patients{$key}) =~ s/,|\$REG_//g;
   ($REG_TMP_Average_Sale_Per_Unique_Patients    = $REG_Average_Sale_Per_Unique_Patients{$key})    =~ s/,|\$REG_//g;
   ($REG_TMP_Average_GM_Per_Unique_Patients      = $REG_Average_GM_Per_Unique_Patients{$key})      =~ s/,|\$REG_//g;

   $REG_TMP_Total_GM_Percents         = sprintf($PCFMT, $REG_TMP_Total_GM_Percents * 100);
   $REG_TMP_Brand_GM_Percents         = sprintf($PCFMT, $REG_TMP_Brand_GM_Percents * 100);
   $REG_TMP_Generic_GM_Percents       = sprintf($PCFMT, $REG_TMP_Generic_GM_Percents * 100);
   $REG_TMP_Total_Sale_Per_Scripts    = sprintf($DSFMT, $REG_TMP_Total_Sale_Per_Scripts);
   $REG_TMP_Brand_Sale_Per_Scripts    = sprintf($DSFMT, $REG_TMP_Brand_Sale_Per_Scripts);
   $REG_TMP_Generic_Sale_Per_Scripts  = sprintf($DSFMT, $REG_TMP_Generic_Sale_Per_Scripts);
   $REG_TMP_Total_GM_Per_Scripts      = sprintf($DSFMT, $REG_TMP_Total_GM_Per_Scripts);
   $REG_TMP_Brand_GM_Per_Scripts      = sprintf($DSFMT, $REG_TMP_Brand_GM_Per_Scripts);
   $REG_TMP_Generic_GM_Per_Scripts    = sprintf($DSFMT, $REG_TMP_Generic_GM_Per_Scripts);

   $REG_TMP_Average_Scripts_Per_Unique_Patients = sprintf($F1FMT, $REG_TMP_Average_Scripts_Per_Unique_Patients);
   $REG_TMP_Average_Sale_Per_Unique_Patients    = sprintf($DSFMT, $REG_TMP_Average_Sale_Per_Unique_Patients);
   $REG_TMP_Average_GM_Per_Unique_Patients      = sprintf($DSFMT, $REG_TMP_Average_GM_Per_Unique_Patients);

   if ( $REG_TMP_Total_Count == 0 ) {
      $REG_PCT_Generic              = "UNDEF";
      $REG_PCT_Refill               = "UNDEF";
      $REG_PCT_Controlled_Count_ALL = "UNDEF";
   } else {
      $REG_PCT_Generic               = sprintf($PCFMT, ($REG_TMP_Generic_Count        / $REG_TMP_Total_Count) * 100 );
      $REG_PCT_Refill                = sprintf($PCFMT, ($REG_TMP_Refill_Claim_Count   / $REG_TMP_Total_Count) * 100 );
      $REG_PCT_Controlled_Count_ALL  = sprintf($PCFMT, ($REG_TMP_Controlled_Count_ALL / $REG_TMP_Total_Count) * 100 );
   }

   if ( $REG_TMP_Total_Sales == 0 ) {
      $REG_PCT_Generic_Sales       = "UNDEF";
      $REG_PCT_Refill_Claim_Sales  = "UNDEF";
      $REG_PCT_Controlled_Sale_ALL = "UNDEF";
   } else {
      $REG_PCT_Generic_Sales       = sprintf($PCFMT, ($REG_TMP_Generic_Sales       / $REG_TMP_Total_Sales) * 100);
      $REG_PCT_Refill_Claim_Sales  = sprintf($PCFMT, ($REG_TMP_Refill_Claim_Sales  / $REG_TMP_Total_Sales) * 100);
      $REG_PCT_Controlled_Sale_ALL = sprintf($PCFMT, ($REG_TMP_Controlled_Sale_ALL / $REG_TMP_Total_Sales) * 100);
   }
   if ( $REG_TMP_Total_GMs == 0 ) {
      $REG_PCT_Generic_GMs         = "UNDEF";
   } else {
      $REG_PCT_Generic_GMs         = sprintf($PCFMT, ($REG_TMP_Generic_GMs         / $REG_TMP_Total_GMs) * 100);
   }
#  -------------------
   ($SIZ_TMP_Generic_Count            = $SIZ_Generic_Counts{$key})           =~ s/,|\$SIZ_//g;
   ($SIZ_TMP_Total_Count              = $SIZ_Total_Counts{$key})             =~ s/,|\$SIZ_//g;
   ($SIZ_TMP_Refill_Claim_Count       = $SIZ_Refill_Claim_Counts{$key})      =~ s/,|\$SIZ_//g;
   ($SIZ_TMP_Controlled_Count_ALL     = $SIZ_Controlled_Count_ALLs{$key})    =~ s/,|\$SIZ_//g;
   ($SIZ_TMP_Total_Sales              = $SIZ_Total_Sales{$key})              =~ s/,|\$SIZ_|\$//g;
   ($SIZ_TMP_Generic_Sales            = $SIZ_Generic_Sales{$key})            =~ s/,|\$SIZ_//g;
   ($SIZ_TMP_Refill_Claim_Sales       = $SIZ_Refill_Claim_Saless{$key})      =~ s/,|\$SIZ_//g;
   ($SIZ_TMP_Controlled_Sale_ALL      = $SIZ_Controlled_Sale_ALLs{$key})     =~ s/,|\$SIZ_//g;
   ($SIZ_TMP_Total_GMs                = $SIZ_Total_GMs{$key})                =~ s/,|\$SIZ_|\$//g;
   ($SIZ_TMP_Generic_GMs              = $SIZ_Generic_GMs{$key})              =~ s/,|\$SIZ_//g;
   ($SIZ_TMP_Total_GM_Percents        = $SIZ_Total_GM_Percents{$key})        =~ s/,|\$SIZ_//g;
   ($SIZ_TMP_Brand_GM_Percents        = $SIZ_Brand_GM_Percents{$key})        =~ s/,|\$SIZ_//g;
   ($SIZ_TMP_Generic_GM_Percents      = $SIZ_Generic_GM_Percents{$key})      =~ s/,|\$SIZ_//g;
   ($SIZ_TMP_Total_Sale_Per_Scripts   = $SIZ_Total_Sale_Per_Scripts{$key})   =~ s/,|\$SIZ_//g;
   ($SIZ_TMP_Brand_Sale_Per_Scripts   = $SIZ_Brand_Sale_Per_Scripts{$key})   =~ s/,|\$SIZ_//g;
   ($SIZ_TMP_Generic_Sale_Per_Scripts = $SIZ_Generic_Sale_Per_Scripts{$key}) =~ s/,|\$SIZ_//g;
   ($SIZ_TMP_Total_GM_Per_Scripts     = $SIZ_Total_GM_Per_Scripts{$key})     =~ s/,|\$SIZ_//g;
   ($SIZ_TMP_Brand_GM_Per_Scripts     = $SIZ_Brand_GM_Per_Scripts{$key})     =~ s/,|\$SIZ_//g;
   ($SIZ_TMP_Generic_GM_Per_Scripts   = $SIZ_Generic_GM_Per_Scripts{$key})   =~ s/,|\$SIZ_//g;
   ($SIZ_TMP_Average_Scripts_Per_Unique_Patients = $SIZ_Average_Scripts_Per_Unique_Patients{$key}) =~ s/,|\$SIZ_//g;
   ($SIZ_TMP_Average_Sale_Per_Unique_Patients    = $SIZ_Average_Sale_Per_Unique_Patients{$key})    =~ s/,|\$SIZ_//g;
   ($SIZ_TMP_Average_GM_Per_Unique_Patients      = $SIZ_Average_GM_Per_Unique_Patients{$key})      =~ s/,|\$SIZ_//g;

   $SIZ_TMP_Total_GM_Percents         = sprintf($PCFMT, $SIZ_TMP_Total_GM_Percents * 100);
   $SIZ_TMP_Brand_GM_Percents         = sprintf($PCFMT, $SIZ_TMP_Brand_GM_Percents * 100);
   $SIZ_TMP_Generic_GM_Percents       = sprintf($PCFMT, $SIZ_TMP_Generic_GM_Percents * 100);
   $SIZ_TMP_Total_Sale_Per_Scripts    = sprintf($DSFMT, $SIZ_TMP_Total_Sale_Per_Scripts);
   $SIZ_TMP_Brand_Sale_Per_Scripts    = sprintf($DSFMT, $SIZ_TMP_Brand_Sale_Per_Scripts);
   $SIZ_TMP_Generic_Sale_Per_Scripts  = sprintf($DSFMT, $SIZ_TMP_Generic_Sale_Per_Scripts);
   $SIZ_TMP_Total_GM_Per_Scripts      = sprintf($DSFMT, $SIZ_TMP_Total_GM_Per_Scripts);
   $SIZ_TMP_Brand_GM_Per_Scripts      = sprintf($DSFMT, $SIZ_TMP_Brand_GM_Per_Scripts);
   $SIZ_TMP_Generic_GM_Per_Scripts    = sprintf($DSFMT, $SIZ_TMP_Generic_GM_Per_Scripts);

   $SIZ_TMP_Average_Scripts_Per_Unique_Patients = sprintf($F1FMT, $SIZ_TMP_Average_Scripts_Per_Unique_Patients);
   $SIZ_TMP_Average_Sale_Per_Unique_Patients    = sprintf($DSFMT, $SIZ_TMP_Average_Sale_Per_Unique_Patients);
   $SIZ_TMP_Average_GM_Per_Unique_Patients      = sprintf($DSFMT, $SIZ_TMP_Average_GM_Per_Unique_Patients);

   if ( $SIZ_TMP_Total_Count == 0 ) {
      $SIZ_PCT_Generic              = "UNDEF";
      $SIZ_PCT_Refill               = "UNDEF";
      $SIZ_PCT_Controlled_Count_ALL = "UNDEF";
   } else {
      $SIZ_PCT_Generic               = sprintf($PCFMT, ($SIZ_TMP_Generic_Count        / $SIZ_TMP_Total_Count) * 100 );
      $SIZ_PCT_Refill                = sprintf($PCFMT, ($SIZ_TMP_Refill_Claim_Count   / $SIZ_TMP_Total_Count) * 100 );
      $SIZ_PCT_Controlled_Count_ALL  = sprintf($PCFMT, ($SIZ_TMP_Controlled_Count_ALL / $SIZ_TMP_Total_Count) * 100 );
   }

   if ( $SIZ_TMP_Total_Sales == 0 ) {
      $SIZ_PCT_Generic_Sales       = "UNDEF";
      $SIZ_PCT_Refill_Claim_Sales  = "UNDEF";
      $SIZ_PCT_Controlled_Sale_ALL = "UNDEF";
   } else {
      $SIZ_PCT_Generic_Sales       = sprintf($PCFMT, ($SIZ_TMP_Generic_Sales       / $SIZ_TMP_Total_Sales) * 100);
      $SIZ_PCT_Refill_Claim_Sales  = sprintf($PCFMT, ($SIZ_TMP_Refill_Claim_Sales  / $SIZ_TMP_Total_Sales) * 100);
      $SIZ_PCT_Controlled_Sale_ALL = sprintf($PCFMT, ($SIZ_TMP_Controlled_Sale_ALL / $SIZ_TMP_Total_Sales) * 100);
   }
   if ( $SIZ_TMP_Total_GMs == 0 ) {
      $SIZ_PCT_Generic_GMs         = "UNDEF";
   } else {
      $SIZ_PCT_Generic_GMs         = sprintf($PCFMT, ($SIZ_TMP_Generic_GMs         / $SIZ_TMP_Total_GMs) * 100);
   }
#  -------------------

   my $ncpdp          = $NCPDP;
   my $Pharmacy_Name  = $Pharmacy_Names{$key} . "<br>" . $key;
   my $rbs_avg_class  = $Pharmacy_Types{$key};
   my $region         = $Locations{$key};
   my $sales_category = $Sizes{$key};
   $RBSa_table_header_row = "<tr><th>$nbsp</th><th>$Pharmacy_Name</th><th>RBS $rbs_avg_class<br />Average</th><th>$region</th><th>$sales_category</th></tr>\n";
   print $RBSa_table_header_row;
   
   print qq#<tr><td style="text-align: left;">Total Script Count</td><td>$Total_Counts{$key}</td><td>$SUM_Total_Counts{$key}</td><td>$REG_Total_Counts{$key}</td><td>$SIZ_Total_Counts{$key}</td></tr>#;
   print qq#<tr><td style="text-align: left;">% Generic</td><td>$PCT_Generic</td><td>$SUM_PCT_Generic</td><td>$REG_PCT_Generic</td><td>$SIZ_PCT_Generic</td></tr>#;
   print qq#<tr><td style="text-align: left;">% Refill</td><td>$PCT_Refill</td><td>$SUM_PCT_Refill</td><td>$REG_PCT_Refill</td><td>$SIZ_PCT_Refill</td></tr>#;

   print qq#<tr><td style="text-align: left;">% Controlled</td><td>$PCT_Controlled_Count_ALL</td><td>$SUM_PCT_Controlled_Count_ALL</td><td>$REG_PCT_Controlled_Count_ALL</td><td>$SIZ_PCT_Controlled_Count_ALL</td></tr>#;
   
   print qq#<tr><td colspan=5>$nbsp</td></tr>\n#;
   
   print qq#<tr><td style="text-align: left;">Total Sale</td><td>$Total_Sales{$key}</td><td>$SUM_Total_Sales{$key}</td><td>$REG_Total_Sales{$key}</td><td>$SIZ_Total_Sales{$key}</td></tr>#;
   print qq#<tr><td style="text-align: left;">% Generic</td><td>$PCT_Generic_Sales</td><td>$SUM_PCT_Generic_Sales</td><td>$REG_PCT_Generic_Sales</td><td>$SIZ_PCT_Generic_Sales</td></tr>#;
   print qq#<tr><td style="text-align: left;">% Refill</td><td>$PCT_Refill_Claim_Sales</td><td>$SUM_PCT_Refill_Claim_Sales</td><td>$REG_PCT_Refill_Claim_Sales</td><td>$SIZ_PCT_Refill_Claim_Sales</td></tr>#;

   print qq#<tr><td style="text-align: left;">% Controlled</td><td>$PCT_Controlled_Sale_ALL</td><td>$SUM_PCT_Controlled_Sale_ALL</td><td>$REG_PCT_Controlled_Sale_ALL</td><td>$SIZ_PCT_Controlled_Sale_ALL</td></tr>#;
   
   print qq#<tr><td colspan=5>$nbsp</td></tr>\n#;
 
   print qq#<tr><td style="text-align: left;">Total GM</td><td>$Total_GMs{$key}</td><td>$SUM_Total_GMs{$key}</td><td>$REG_Total_GMs{$key}</td><td>$SIZ_Total_GMs{$key}</td></tr>#;
   print qq#<tr><td style="text-align: left;">% Generic</td><td>$PCT_Generic_GMs</td><td>$SUM_PCT_Generic_GMs</td><td>$REG_PCT_Generic_GMs</td><td>$SIZ_PCT_Generic_GMs</td></tr>#;
   
   print qq#<tr><td colspan=5>$nbsp</td></tr>\n#;
   
   print qq#<tr><td style="text-align: left;">Average GM%</td><td>$TMP_Total_GM_Percents</td><td>$SUM_TMP_Total_GM_Percents</td><td>$REG_TMP_Total_GM_Percents</td><td>$SIZ_TMP_Total_GM_Percents</td></tr>#;
   print qq#<tr><td style="text-align: left;">Average Brand GM%</td><td>$TMP_Brand_GM_Percents</td><td>$SUM_TMP_Brand_GM_Percents</td><td>$REG_TMP_Brand_GM_Percents</td><td>$SIZ_TMP_Brand_GM_Percents</td></tr>#;
   print qq#<tr><td style="text-align: left;">Average Generic GM%</td><td>$TMP_Generic_GM_Percents</td><td>$SUM_TMP_Generic_GM_Percents</td><td>$REG_TMP_Generic_GM_Percents</td><td>$SIZ_TMP_Generic_GM_Percents</td></tr>#;
   
   print qq#<tr><td colspan=5>$nbsp</td></tr>\n#;
   
   print qq#<tr><td style="text-align: left;">Average Sale/Script</td><td>$TMP_Total_Sale_Per_Scripts</td><td>$SUM_TMP_Total_Sale_Per_Scripts</td><td>$REG_TMP_Total_Sale_Per_Scripts</td><td>$SIZ_TMP_Total_Sale_Per_Scripts</td></tr>#;
   print qq#<tr><td style="text-align: left;">Average Brand Sale/Script</td><td>$TMP_Brand_Sale_Per_Scripts</td><td>$SUM_TMP_Brand_Sale_Per_Scripts</td><td>$REG_TMP_Brand_Sale_Per_Scripts</td><td>$SIZ_TMP_Brand_Sale_Per_Scripts</td></tr>#;
   print qq#<tr><td style="text-align: left;">Average Generic Sale/Script</td><td>$TMP_Generic_Sale_Per_Scripts</td><td>$SUM_TMP_Generic_Sale_Per_Scripts</td><td>$REG_TMP_Generic_Sale_Per_Scripts</td><td>$SIZ_TMP_Generic_Sale_Per_Scripts</td></tr>#;
   
   print qq#<tr><td colspan=5>$nbsp</td></tr>\n#;
   
   print qq#<tr><td style="text-align: left;">Average GM/Script</td><td>$TMP_Total_GM_Per_Scripts</td><td>$SUM_TMP_Total_GM_Per_Scripts</td><td>$REG_TMP_Total_GM_Per_Scripts</td><td>$SIZ_TMP_Total_GM_Per_Scripts</td></tr>#;
   print qq#<tr><td style="text-align: left;">Average Brand GM/Script</td><td>$TMP_Brand_GM_Per_Scripts</td><td>$SUM_TMP_Brand_GM_Per_Scripts</td><td>$REG_TMP_Brand_GM_Per_Scripts</td><td>$SIZ_TMP_Brand_GM_Per_Scripts</td></tr>#;
   print qq#<tr><td style="text-align: left;">Average Generic GM/Script</td><td>$TMP_Generic_GM_Per_Scripts</td><td>$SUM_TMP_Generic_GM_Per_Scripts</td><td>$REG_TMP_Generic_GM_Per_Scripts</td><td>$SIZ_TMP_Generic_GM_Per_Scripts</td></tr>#;
   
   print qq#<tr><td colspan=5>$nbsp</td></tr>\n#;
   
   print qq#<tr><td style="text-align: left;">Average Scripts/Patient</td><td>$TMP_Average_Scripts_Per_Unique_Patients</td><td>$SUM_TMP_Average_Scripts_Per_Unique_Patients</td><td>$REG_TMP_Average_Scripts_Per_Unique_Patients</td><td>$SIZ_TMP_Average_Scripts_Per_Unique_Patients</td></tr>#;
   print qq#<tr><td style="text-align: left;">Average Sale/Patient</td><td>$TMP_Average_Sale_Per_Unique_Patients</td><td>$SUM_TMP_Average_Sale_Per_Unique_Patients</td><td>$REG_TMP_Average_Sale_Per_Unique_Patients</td><td>$SIZ_TMP_Average_Sale_Per_Unique_Patients</td></tr>#;
   print qq#<tr><td style="text-align: left;">Average GM/Patient</td><td>$TMP_Average_GM_Per_Unique_Patients</td><td>$SUM_TMP_Average_GM_Per_Unique_Patients</td><td>$REG_TMP_Average_GM_Per_Unique_Patients</td><td>$SIZ_TMP_Average_GM_Per_Unique_Patients</td></tr>#;
   
   
   print qq#</table>#;
      
   print qq#</div>#;
}

#______________________________________________________________________________

sub ncpa {

  my $NCPDP = $inNCPDP || $dispNCPDP;
  my $YEAR  = $yearm1; #Current year, minus 1, financials are a year behind
  
  my $ncpa_data_present = 0;
  my $class = "";
  
  
  
  #Use one query to get pharm Class (like 'LTC'), as well as how many rows in financial table for report year
  my $sql  = "
  SELECT pharmacy.NCPDP, Class, count(financials.ncpdp) Financial_Rows
  FROM officedb.pharmacy 
  LEFT JOIN rbsreporting.financials 
  ON (pharmacy.NCPDP = financials.ncpdp) && (year = ${YEAR}) && (ncpa_category_number < ${YEAR}500)
  WHERE 
  Status_RBS = 'Active' 
  && RBSReporting = 'Yes'
  GROUP BY pharmacy.NCPDP
  ";

  $checkData  = $dbx->prepare("$sql");
  $checkData->execute;
  $data_check = $checkData->rows;
  
  if ($data_check > 0) {
  
    %dcClasses = ();
    %dcCounts = ();
    
    $retail_ncpdps = '';
    $ltc_ncpdps    = '';
    
    $retail_count = 0;
    $ltc_count = 0;
  
    while ( my @row = $checkData->fetchrow_array() ) {
    
      my ($dcNCPDP, $dcClass, $dcCount) = @row;
      $dcClasses{$dcNCPDP} = $dcClass;
      $dcCounts{$dcNCPDP}  = $dcCount;
      
      #Don't want to add test stores to Averages
      next if ($dcNCPDP =~ /1111111|2222222/);
      
      #Build NCPDP strings, for retail and LTC, for RBS AVGs query later
      if ($dcClass =~ /LTC/ && $dcCount > 0) {
        $ltc_ncpdps    .= "$dcNCPDP,";
        $Jay_LTCs{$dcNCPDP}++;
        $ltc_count++;
      } elsif ($dcClass !~ /LTC/ && $dcCount > 0) {
        $retail_ncpdps .= "$dcNCPDP,";
        $retail_count++;
      }
    
    }
  
    #remove trailing commas
    $ltc_ncpdps    =~ s/,+$//;
    $retail_ncpdps =~ s/,+$//;
  
    #Now determine if financial data is available for this store.
    $ncpa_data_present = $dcCounts{$NCPDP};
  
  }
  $checkData->finish;
  
  ### Calculate Region Based on State #####
  $state = $Pharmacy_States{$PH_ID};
  $region = "";
  if ($state =~ /AK|AZ|CA|HI|ID|NV|NM|OR|UT|WA/) {
    $region = "West";
  } elsif ($state =~ /AR|CO|IA|KS|MN|MO|MT|NE|ND|OK|SD|TX|WI|WY/) {
    $region = "West-Central";
  } elsif ($state =~ /IL|IN|MI|OH|PA|WV/) {
    $region = "East-Central";
  } elsif ($state =~ /CT|DE|DC|ME|MD|MA|NH|NJ|NY|RI|VT|VA/) {
    $region = "Northeast";
  } elsif ($state =~ /AL|FL|GA|KY|LA|MS|NC|SC|TN/) {
    $region = "Southeast";
  }
  #########################################
  
  ### Pre-Calculate Sales Category (based on *OUR* Sales By Payer annual Rx sales) ###
  #Sales By Payer (new) MUST BE RAN FOR THIS TO WORK
  #Will be recalculated later with actual financial data if available
  $sales_category = "";
  if ($ymc_annual_total_rx_sales < 2500000) {
    $sales_category = "Sales Under \$2.5M";
  } elsif ($ymc_annual_total_rx_sales >= 2500000 && $ymc_annual_total_rx_sales < 3500000) {
    $sales_category = "Sales \$2.5M to \$3.5M";
  } elsif ($ymc_annual_total_rx_sales >= 3500000 && $ymc_annual_total_rx_sales < 6500000) {
    $sales_category = "Sales \$3.5M to \$6.5M";
  } elsif ($ymc_annual_total_rx_sales >= 6500000) {
    $sales_category = "Sales Over \$6.5M";
  }
  #########################################
  
  ###Set to '> 0' to hide everything and show a static HTML table if there is no financial data.
  if ($ncpa_data_present > 0) {
   
    %ncpa_data = ();
    
    #Determine which NCPDPs to use for RBS average.
    $ncpdps_for_rbs_avg = '';
    $rbs_avg_class = '';
    if ($dcClasses{$NCPDP} =~ /LTC/) {
      $ncpdps_for_rbs_avg = $ltc_ncpdps;
      $rbs_avg_class = 'LTC';
      $rbsavg_count = $ltc_count;
    } else {
      $ncpdps_for_rbs_avg = $retail_ncpdps;
      $rbs_avg_class = 'Retail';
      $rbsavg_count = $retail_count;
    }
    if ($ncpdps_for_rbs_avg =~ /^\s*$/) {
      $ncpdps_for_rbs_avg = '0';
    }
      
    $pharm_expense_total   = 0;
    $pharm_expense_percent = 0;
    $ncpa_average_total    = 0;
    $ncpa_top25_total      = 0;
    $ncpa_sales_total      = 0;
    $ncpa_location_total   = 0;
    
    ### Single Pharmacy Data Collection ###########################################################
    my $NumOfRows = 0;
    $sql  = "
    ### Sales and Rebated Cost by year
    SELECT sum(Total_Brand_Revenue + Total_Generic_Revenue) as Sales, sum(Rebated_Brand_Cost + Rebated_Generic_Cost) as Rebated_Cost, financials_sales.amount as financials_sales, othersales.amount as Other_Sales, financials_costs.amount as financials_costs, othercosts.amount as Other_Costs
    FROM ( SELECT yearly.*, 
                  (case when Brand_Rebate IS NOT NULL then (Total_Brand_Cost*(1 - Brand_Rebate)) else Total_Brand_Cost end) as Rebated_Brand_Cost, 
                  (case when Generic_Rebate IS NOT NULL then (Total_Generic_Cost*(1 - Generic_Rebate)) else Total_Generic_Cost end) as Rebated_Generic_Cost 
             FROM ( SELECT * FROM ( SELECT monthly.NCPDP, date, date_format(date, '%Y%m') as datef, 
                                           Total_Brand_Revenue, Total_Generic_Revenue, Total_Brand_Cost, Total_Generic_Cost
                                      FROM rbsreporting.monthly 
                                     WHERE monthly.NCPDP = $NCPDP
                                        && date LIKE '$YEAR%' 
                                  GROUP BY datef
                                  ) raw
                        LEFT JOIN (SELECT NCPDP as NCPDPrebate, YYYYMM, Brand_Rebate, Generic_Rebate FROM rbsreporting.rebates) rebates 
                               ON (raw.NCPDP = NCPDPrebate && BINARY raw.datef = BINARY YYYYMM)
                  ) yearly
         ) rebated
LEFT JOIN (SELECT ncpdp, ncpa_category_number, truncate(sum(net_income), 2) as amount 
             FROM rbsreporting.financials 
            WHERE ncpa_category_number LIKE '%101' 
               && year = $YEAR 
         GROUP BY ncpa_category_number, ncpdp
          ) financials_sales
       ON (rebated.NCPDP = financials_sales.ncpdp)
LEFT JOIN (SELECT ncpdp, ncpa_category_number, truncate(sum(net_income), 2) as amount 
             FROM rbsreporting.financials 
            WHERE ncpa_category_number LIKE '%102' 
               && year = $YEAR 
         GROUP BY ncpa_category_number, ncpdp
          ) othersales
       ON (rebated.NCPDP = othersales.ncpdp)
LEFT JOIN (SELECT ncpdp, ncpa_category_number, truncate(sum(net_income), 2) as amount 
             FROM rbsreporting.financials 
            WHERE ncpa_category_number LIKE '%201' 
               && year = $YEAR 
         GROUP BY ncpa_category_number, ncpdp
          ) financials_costs
       ON (rebated.NCPDP = financials_costs.ncpdp)
LEFT JOIN (SELECT ncpdp, ncpa_category_number, truncate(sum(net_income), 2) as amount 
             FROM rbsreporting.financials 
            WHERE ncpa_category_number LIKE '%202' 
               && year = $YEAR 
         GROUP BY ncpa_category_number, ncpdp) othercosts
      ON (rebated.NCPDP = othercosts.ncpdp)";

    my $sales = 0;
    my $financials_sales = 0;
    my $costs = 0;
    my $financials_costs = 0;
    my $other_sales = 0;
    my $other_costs = 0;
    
    if ($ncpa_data_present > 0) {
      $getSalesCost  = $dbx->prepare("$sql");
      $getSalesCost->execute;
      $NumOfRows = $getSalesCost->rows;
      if ($NumOfRows > 0) {
        while ( my @row = $getSalesCost->fetchrow_array() ) {
           ($sales, $costs, $financials_sales, $other_sales, $financials_costs, $other_costs) = @row;
           #print qq#($sales, $costs, $financials_sales, $other_sales, $financials_costs, $other_costs)\n#;
        }
      }
      $getSalesCost->finish;

      if ( $sales =~ /^\s*$/ ) {
         ($sales, $costs, $financials_sales, $other_sales, $financials_costs, $other_costs) = &getdatafrom_rbsreportingfinancials($NCPDP);
      }
    }
    
    ### START USING FINANCIAL SALES/COST - Per Monty/Amy 2/12/2015
    $sales       = $financials_sales;
    $costs       = $financials_costs * -1;
    $other_costs = $other_costs * -1;
    
    ### RBS Averages Data Collection ##############################################################
    my $rbsavg = 0;
    $rbsavg_expense_percent = 0;
    my $NumOfRows = 0;
    $sql  = "
    ### Sales and Rebated Cost RBS Average
    SELECT 
    (sum(Total_Brand_Revenue + Total_Generic_Revenue))/rbs_count.count as RBSavg_Sales, 
    (sum(Rebated_Brand_Cost + Rebated_Generic_Cost))/rbs_count.count as RBSavg_Rebated_Cost, 
    (financials_sales.amount)/rbs_count.count as RBSavg_financials_sales, 
    (othersales.amount)/rbs_count.count as RBSavg_Other_Sales, 
    (financials_costs.amount)/rbs_count.count as RBSavg_financials_costs, 
    (othercosts.amount)/rbs_count.count as RBSavg_Other_Costs
    #, rbs_count.count

    FROM (
      SELECT 1 as JOINER, yearly.*, 
      (case when Brand_Rebate IS NOT NULL then (Total_Brand_Cost*(1 - Brand_Rebate)) else Total_Brand_Cost end) as Rebated_Brand_Cost, 
      (case when Generic_Rebate IS NOT NULL then (Total_Generic_Cost*(1 - Generic_Rebate)) else Total_Generic_Cost end) as Rebated_Generic_Cost 
      FROM (
        SELECT * FROM (
          SELECT monthly.NCPDP, date, date_format(date, '%Y%m') as datef, 
          Total_Brand_Revenue, Total_Generic_Revenue, Total_Brand_Cost, Total_Generic_Cost
          FROM rbsreporting.monthly 
          WHERE 
          date LIKE '$YEAR%' 
          && NCPDP IN ($ncpdps_for_rbs_avg)
        ) raw
        LEFT JOIN (SELECT NCPDP as NCPDPrebate, YYYYMM, Brand_Rebate, Generic_Rebate 
                     FROM rbsreporting.rebates) rebates 
               ON (raw.NCPDP = NCPDPrebate && BINARY raw.datef = BINARY YYYYMM)
      ) yearly
    ) rebated 

    LEFT JOIN (SELECT 1 as JOINER, ncpa_category_number, truncate(sum(net_income), 2) as amount 
    FROM rbsreporting.financials 
    WHERE ncpa_category_number LIKE '%101' && year = $YEAR && NCPDP IN ($ncpdps_for_rbs_avg) 
    ) financials_sales
    ON (rebated.JOINER = financials_sales.JOINER)

    LEFT JOIN (SELECT 1 as JOINER, ncpa_category_number, truncate(sum(net_income), 2) as amount 
    FROM rbsreporting.financials 
    WHERE ncpa_category_number LIKE '%102' && year = $YEAR && NCPDP IN ($ncpdps_for_rbs_avg) 
    ) othersales
    ON (rebated.JOINER = othersales.JOINER)

    LEFT JOIN (SELECT 1 as JOINER, ncpa_category_number, truncate(sum(net_income), 2) as amount 
    FROM rbsreporting.financials 
    WHERE ncpa_category_number LIKE '%201' && year = $YEAR && NCPDP IN ($ncpdps_for_rbs_avg) 
    ) financials_costs
    ON (rebated.JOINER = financials_costs.JOINER)

    LEFT JOIN (SELECT 1 as JOINER, ncpa_category_number, truncate(sum(net_income), 2) as amount 
    FROM rbsreporting.financials 
    WHERE ncpa_category_number LIKE '%202' && year = $YEAR && NCPDP IN ($ncpdps_for_rbs_avg) 
    ) othercosts
    ON (rebated.JOINER = othercosts.JOINER)

    LEFT JOIN (
    SELECT 1 as JOINER, count(DISTINCT(NCPDP)) as count 
    FROM rbsreporting.financials 
    WHERE NCPDP IN ($ncpdps_for_rbs_avg)
    ) rbs_count
    ON (rebated.JOINER = rbs_count.JOINER)
    ";
    
    my $rbsavg_sales = 0;
    my $rbsavg_cost = 0;
    my $rbsavg_other_sales = 0;
    my $rbsavg_other_costs = 0;
    $getRBSAVGSalesCost  = $dbx->prepare("$sql");
    $getRBSAVGSalesCost->execute;
    $NumOfRows = $getRBSAVGSalesCost->rows;
    if ($NumOfRows > 0) {
      while ( my @row = $getRBSAVGSalesCost->fetchrow_array() ) {
        ($rbsavg_sales, $rbsavg_costs, $rbsavg_financials_sales, $rbsavg_other_sales, $rbsavg_financials_costs, $rbsavg_other_costs) = @row;
      }
    }
    $getRBSAVGSalesCost->finish;
    
    $rbsavg_sales = $rbsavg_financials_sales;
    $rbsavg_costs = $rbsavg_financials_costs;
      
    ### Calculate Sales Category ############
    $sales_category = "";
    if ($sales < 2500000) {
      $sales_category = "Sales Under \$2.5M";
    } elsif ($sales >= 2500000 && $sales < 3500000) {
      $sales_category = "Sales \$2.5M to \$3.5M";
    } elsif ($sales >= 3500000 && $sales < 6500000) {
      $sales_category = "Sales \$3.5M to \$6.5M";
    } elsif ($sales >= 6500000) {
      $sales_category = "Sales Over \$6.5M";
    }
    
    print qq#<div class="page">#;
    print qq#<div class="page_header"><h3>$YEAR NCPA Comparison - $Pharmacy_Name</h3></div><br />#;
  
    print qq#<table class="tableizer-table">\n#;
  
   $ncpa_table_header_row = "<tr><th>$nbsp</th><th>$Pharmacy_Name</th><th>Store %</th><th>RBS $rbs_avg_class<br />Average</th><th>NCPA<br />Average</th><th>NCPA Top<br />25 Average</th><th>$sales_category</th><th>$region</th></tr>\n";
#    $ncpa_table_header_row = "<tr><th>$nbsp</th><th>$Pharmacy_Name</th><th>Store %</th><th>RBS $rbs_avg_class<br />Average</th><th>NCPA<br />Average</th><th>$sales_category</th><th>$region</th></tr>\n";
    
    print $ncpa_table_header_row;
      
    ###Row 1, Rx Sales
    $all_sales = $sales + $other_sales;
    $all_sales_disp = commify(sprintf "%.0f", $all_sales);
    #--------------------------------------------------------#
    $rbsavg_all_sales = $rbsavg_sales + $rbsavg_other_sales;
    $rbsavg_rxsales = 0;
    if ($rbsavg_all_sales > 0) {
      $rbsavg_rxsales = sprintf "%.1f", (($rbsavg_sales/$rbsavg_all_sales)*100);
    }
    #--------------------------------------------------------#
    ncpa_row($all_sales, $sales, $rbsavg_rxsales, $YEAR, "Rx Sales", "${YEAR}101");
  
    ###Row 2, All Other Sales
    #--------------------------------------------------------#
    $rbsavg_all_sales = $rbsavg_sales + $rbsavg_other_sales;
    
    $rbsavg_osales = 0;
    if ($rbsavg_all_sales > 0) {
      $rbsavg_osales = sprintf "%.1f", (($rbsavg_other_sales/$rbsavg_all_sales)*100);
    }
    #--------------------------------------------------------#
    ncpa_row($all_sales, $other_sales, $rbsavg_osales, $YEAR, "All Other Sales", "${YEAR}102");
  
    ###Row 3, Total Sales
    if ( $Jay_LTCs{$inNCPDP} ) {
       # ltc LTC Pharmacy Found
       print "<tr> <td>Total Sales</td> <td>\$$all_sales_disp</td> <td>100.0%</td> <td>100.0%</td> <td>-</td> <td>-</td> <td>-</td> <td>-</td> </tr>\n";
    } else {
       print "<tr><td>Total Sales</td><td>\$$all_sales_disp</td><td>100.0%</td><td>100.0%</td><td>100.0%</td><td>100.0%</td><td>100.0%</td><td>100.0%</td></tr>\n";
    }
    
    ###Blank Row
    print "<tr><td colspan=8>$nbsp</td></tr>\n";
      
    
    
    #Pass in -20000 to only load NCPA data into hashes (used below) for passed id ( ie ${YEAR{201}} )
    my $JUSTLOADHASHES = -20000;
    ncpa_row($JUSTLOADHASHES, $JUSTLOADHASHES, $JUSTLOADHASHES, $YEAR, "Rx Costs (HASH LOAD ONLY)", "${YEAR}201");
    ncpa_row($JUSTLOADHASHES, $JUSTLOADHASHES, $JUSTLOADHASHES, $YEAR, "Rx Costs (HASH LOAD ONLY)", "${YEAR}202");
    
    ### [0] = NCPA Average Data
    $ncpa_rx_costs             = sprintf "%.1f", ($ncpa_data{"${YEAR}201"}[0] / $ncpa_data{"${YEAR}101"}[0])*100;
    $ncpa_other_costs          = sprintf "%.1f", ($ncpa_data{"${YEAR}202"}[0] / $ncpa_data{"${YEAR}102"}[0])*100;
  
    ### [1] = NCPA Top 25 Average Data
    $ncpa_top25_rx_costs       = sprintf "%.1f", ($ncpa_data{"${YEAR}201"}[1] / $ncpa_data{"${YEAR}101"}[1])*100;
    $ncpa_top25_other_costs    = sprintf "%.1f", ($ncpa_data{"${YEAR}202"}[1] / $ncpa_data{"${YEAR}102"}[1])*100;
    
    ### [2] = Sales Category Data
    $ncpa_sales_rx_costs       = sprintf "%.1f", ($ncpa_data{"${YEAR}201"}[2] / $ncpa_data{"${YEAR}101"}[2])*100;
    $ncpa_sales_other_costs    = sprintf "%.1f", ($ncpa_data{"${YEAR}202"}[2] / $ncpa_data{"${YEAR}102"}[2])*100;
    
    ### [3] = Location Data
    $ncpa_location_rx_costs    = sprintf "%.1f", ($ncpa_data{"${YEAR}201"}[3] / $ncpa_data{"${YEAR}101"}[3])*100;
    $ncpa_location_other_costs = sprintf "%.1f", ($ncpa_data{"${YEAR}202"}[3] / $ncpa_data{"${YEAR}102"}[3])*100;
    $rx_costs_disp = commify(sprintf "%.0f",$costs);

    $rx_costs_percent_disp = sprintf "%.1f", 0;
    if ($sales > 0) {
      $rx_costs_percent_disp = sprintf "%.1f",(($costs/$sales)*100);
    }
    
    $rbsavg_rxcosts = 0;
    if ($rbsavg_sales > 0) {
      $rbsavg_rxcosts = sprintf "%.1f", ((-$rbsavg_costs/$rbsavg_sales)*100);
    }
    
    if ( $Jay_LTCs{$inNCPDP} ) {
       # ltc LTC Pharmacy Found
      print "<tr><td>Rx Costs</td><td>\$$rx_costs_disp</td><td>$rx_costs_percent_disp%</td><td>$rbsavg_rxcosts%</td><td>-</td><td>-</td><td>-</td></tr>\n";
    } else {
#     print "<tr><td>Rx Costs</td><td>\$$rx_costs_disp</td><td>$rx_costs_percent_disp%</td><td>$rbsavg_rxcosts%</td><td>$ncpa_rx_costs%</td><td>$ncpa_top25_rx_costs%</td><td>$ncpa_sales_rx_costs%</td><td>$ncpa_location_rx_costs%</td></tr>\n";

      if ( $ReportMonth != '2015-12-01' ) {
         print "<tr><td>Rx Costs</td><td>\$$rx_costs_disp</td><td>$rx_costs_percent_disp%</td><td>$rbsavg_rxcosts%</td><td>$ncpa_rx_costs%</td><td>$ncpa_top25_rx_costs%</td><td>$ncpa_sales_rx_costs%</td><td>$ncpa_location_rx_costs%</td></tr>\n"
      } else {
         print "<tr><td>Rx Costs</td><td>\$$rx_costs_disp</td><td>$rx_costs_percent_disp%</td><td>77.2%</td><td>$ncpa_rx_costs%</td><td>$ncpa_sales_rx_costs%</td><td>$ncpa_location_rx_costs%</td></tr>\n"
      }
    }
    #--------------------------------------------------------#

    
    
    ###Row 5, All Other Costs of Goods Sold
    #--------------------------------------------------------#
    $other_costs_disp = commify(sprintf "%.0f",$other_costs);
    if ($other_costs > 0) {
      $other_costs_percent_disp = sprintf "%.1f",(($other_costs/$other_sales)*100);
    } else {
      $other_costs_percent_disp = sprintf "%.1f", 0;
    }
    
    $rbsavg_ocosts = 0;
    if ($rbsavg_other_sales > 0) {
      #$rbsavg_ocosts = sprintf "%.1f", (($rbsavg_other_costs/$rbsavg_all_sales)*100);
      $rbsavg_ocosts = sprintf "%.1f", ((-$rbsavg_other_costs/$rbsavg_other_sales)*100);
    }
    
    if ( $Jay_LTCs{$inNCPDP} ) {
       # ltc LTC Pharmacy Found
       print "<tr><td>All Other Costs</td><td>\$$other_costs_disp</td><td>$other_costs_percent_disp%</td><td>$rbsavg_ocosts%</td><td>-</td><td>-</td><td>-</td></tr>\n";
    } else {
      print "<tr><td>All Other Costs</td><td>\$$other_costs_disp</td><td>$other_costs_percent_disp%</td><td>$rbsavg_ocosts%</td><td>$ncpa_other_costs%</td><td>$ncpa_top25_other_costs%</td><td>$ncpa_sales_other_costs%</td><td>$ncpa_location_other_costs%</td></tr>\n";
#       print "<tr><td>All Other Costs</td><td>\$$other_costs_disp</td><td>$other_costs_percent_disp%</td><td>$rbsavg_ocosts%</td><td>$ncpa_other_costs%</td><td>$ncpa_sales_other_costs%</td><td>$ncpa_location_other_costs%</td></tr>\n";
    }
    
    ###Blank Row
    print "<tr><td colspan=8>$nbsp</td></tr>\n";
    
    ###Calculate GP Numbers
    $rx_gp = $sales - $costs;
    $rx_gp = sprintf "%.0f", $rx_gp;
    $rx_gp_disp = commify($rx_gp);
    $other_gp = $other_sales - $other_costs;
    $other_gp = sprintf "%.0f", $other_gp;
    $other_gp_disp = commify($other_gp);
    $total_gp = $rx_gp + $other_gp;
    $total_gp = sprintf "%.0f", $total_gp;
    $total_gp_disp = commify($total_gp);
      
    $rx_gp_percent = 0;
    if ($all_sales > 0) {
      $rx_gp_percent = ($rx_gp/$sales)*100; #Changed 2015/02/13 Per Monty/Amy
    }
    $rx_gp_percent_disp = sprintf "%.1f", $rx_gp_percent;
    if ($other_sales > 0) {
      $other_gp_percent = ($other_gp/$other_sales)*100; #Changed 2015/02/13 Per Monty/Amy
    } else {
      $other_gp_percent = 0;
    }
    $other_gp_percent_disp = sprintf "%.1f", $other_gp_percent;
    
    $total_gp_percent = 0;
    if ($all_sales > 0) {
      $total_gp_percent = ($total_gp/$all_sales)*100;
    }
    $total_gp_percent_disp = sprintf "%.1f", $total_gp_percent;
    
    #--------------------------------------------------------#
    $rbsavg_rx_gp = $rbsavg_sales + $rbsavg_costs;
    $rbsavg_other_gp = $rbsavg_other_sales + $rbsavg_other_costs;
    $rbsavg_total_gp = $rbsavg_rx_gp + $rbsavg_other_gp;
    $rbsavg_rx_gp_percent = 0;
    if ($rbsavg_sales > 0) {
      $rbsavg_rx_gp_percent = ($rbsavg_rx_gp/$rbsavg_sales)*100;
    }
    $rbsavg_rx_gp_percent_disp = sprintf "%.1f", $rbsavg_rx_gp_percent;
    if ($rbsavg_other_sales > 0) {
    #$rbsavg_other_gp_percent = ($rbsavg_other_gp/$rbsavg_all_sales)*100; #ORIGINAL 
      $rbsavg_other_gp_percent = ($rbsavg_other_gp/$rbsavg_other_sales)*100;
    } else {
      ###Prevent Potential "Divide By Zero" Error, if no "other sales" stated
      $rbsavg_other_gp_percent = 0;
    }
    $rbsavg_other_gp_percent_disp = sprintf "%.1f", $rbsavg_other_gp_percent;
    $rbsavg_total_gp_percent = 0;
    if ($rbsavg_all_sales > 0) {
      $rbsavg_total_gp_percent = ($rbsavg_total_gp/$rbsavg_all_sales)*100;
    }
    $rbsavg_total_gp_percent_disp = sprintf "%.1f", $rbsavg_total_gp_percent;
    #--------------------------------------------------------#
    
    ### Categories
    ### 101 = Rx Sales     201 = Rx Costs, 
    ### 102 = Other Sales  202 = Other Costs
  
    ### [0] = NCPA Average Data
    #$ncpa_rx_gp    = sprintf "%.1f", ($ncpa_data{"${YEAR}101"}[0] - $ncpa_data{"${YEAR}201"}[0]);
    #$ncpa_other_gp = sprintf "%.1f", ($ncpa_data{"${YEAR}102"}[0] - $ncpa_data{"${YEAR}202"}[0]);
    #$ncpa_total_gp = sprintf "%.1f", ($ncpa_rx_gp + $ncpa_other_gp);
    #$sales_category_value = sprintf "%.1f", $sales_category_value;
    
    ### [1] = NCPA Top 25 Average Data
    #$ncpa_top25_rx_gp    = sprintf "%.1f", ($ncpa_data{"${YEAR}101"}[1] - $ncpa_data{"${YEAR}201"}[1]);
    #$ncpa_top25_other_gp = sprintf "%.1f", ($ncpa_data{"${YEAR}102"}[1] - $ncpa_data{"${YEAR}202"}[1]);
    #$ncpa_top25_total_gp = sprintf "%.1f", ($ncpa_top25_rx_gp + $ncpa_top25_other_gp);
    
    ### [2] = Sales Category Data
    #$ncpa_sales_rx_gp    = sprintf "%.1f", ($ncpa_data{"${YEAR}101"}[2] - $ncpa_data{"${YEAR}201"}[2]);
    #$ncpa_sales_other_gp = sprintf "%.1f", ($ncpa_data{"${YEAR}102"}[2] - $ncpa_data{"${YEAR}202"}[2]);
    #$ncpa_sales_total_gp = sprintf "%.1f", ($ncpa_sales_rx_gp + $ncpa_sales_other_gp);
    
    ### [3] = Location Data
    #$ncpa_location_rx_gp    = sprintf "%.1f", ($ncpa_data{"${YEAR}101"}[3] - $ncpa_data{"${YEAR}201"}[3]);
    #$ncpa_location_other_gp = sprintf "%.1f", ($ncpa_data{"${YEAR}102"}[3] - $ncpa_data{"${YEAR}202"}[3]);
    #$ncpa_location_total_gp = sprintf "%.1f", ($ncpa_location_rx_gp + $ncpa_location_other_gp);
    
  
    ### NEW CALCULATION AS FOLLOWS - Per Monty/Amy 2/13/2015
  
    ### [0] = NCPA Average Data
    $ncpa_rx_gp    = sprintf "%.1f", (($ncpa_data{"${YEAR}101"}[0] - $ncpa_data{"${YEAR}201"}[0]) / $ncpa_data{"${YEAR}101"}[0])*100;
    $ncpa_other_gp = sprintf "%.1f", (($ncpa_data{"${YEAR}102"}[0] - $ncpa_data{"${YEAR}202"}[0]) / $ncpa_data{"${YEAR}102"}[0])*100;
    $ncpa_total_gp = sprintf "%.1f", (
      (($ncpa_data{"${YEAR}101"}[0] + $ncpa_data{"${YEAR}102"}[0]) - $ncpa_data{"${YEAR}201"}[0] - $ncpa_data{"${YEAR}202"}[0]) 
      /
      ($ncpa_data{"${YEAR}101"}[0] + $ncpa_data{"${YEAR}102"}[0])
    )*100;
    
    ### [1] = NCPA Top 25 Average Data
    $ncpa_top25_rx_gp    = sprintf "%.1f", (($ncpa_data{"${YEAR}101"}[1] - $ncpa_data{"${YEAR}201"}[1]) / $ncpa_data{"${YEAR}101"}[1])*100;
    $ncpa_top25_other_gp = sprintf "%.1f", (($ncpa_data{"${YEAR}102"}[1] - $ncpa_data{"${YEAR}202"}[1]) / $ncpa_data{"${YEAR}102"}[1])*100;
    $ncpa_top25_total_gp = sprintf "%.1f", (
      (($ncpa_data{"${YEAR}101"}[1] + $ncpa_data{"${YEAR}102"}[1]) - $ncpa_data{"${YEAR}201"}[1] - $ncpa_data{"${YEAR}202"}[1]) 
      /
      ($ncpa_data{"${YEAR}101"}[1] + $ncpa_data{"${YEAR}102"}[1])
    )*100;
    
    ### [2] = Sales Category Data
    $ncpa_sales_rx_gp    = sprintf "%.1f", (($ncpa_data{"${YEAR}101"}[2] - $ncpa_data{"${YEAR}201"}[2]) / $ncpa_data{"${YEAR}101"}[2])*100;
    $ncpa_sales_other_gp = sprintf "%.1f", (($ncpa_data{"${YEAR}102"}[2] - $ncpa_data{"${YEAR}202"}[2]) / $ncpa_data{"${YEAR}102"}[2])*100;
    $ncpa_sales_total_gp = sprintf "%.1f", (
      (($ncpa_data{"${YEAR}101"}[2] + $ncpa_data{"${YEAR}102"}[2]) - $ncpa_data{"${YEAR}201"}[2] - $ncpa_data{"${YEAR}202"}[2]) 
      /
      ($ncpa_data{"${YEAR}101"}[2] + $ncpa_data{"${YEAR}102"}[2])
    )*100;
    
    ### [3] = Location Data
    $ncpa_location_rx_gp    = sprintf "%.1f", (($ncpa_data{"${YEAR}101"}[3] - $ncpa_data{"${YEAR}201"}[3]) / $ncpa_data{"${YEAR}101"}[3])*100;
    $ncpa_location_other_gp = sprintf "%.1f", (($ncpa_data{"${YEAR}102"}[3] - $ncpa_data{"${YEAR}202"}[3]) / $ncpa_data{"${YEAR}102"}[3])*100;
    $ncpa_location_total_gp = sprintf "%.1f", (
      (($ncpa_data{"${YEAR}101"}[3] + $ncpa_data{"${YEAR}102"}[3]) - $ncpa_data{"${YEAR}201"}[3] - $ncpa_data{"${YEAR}202"}[3]) 
      /
      ($ncpa_data{"${YEAR}101"}[3] + $ncpa_data{"${YEAR}102"}[3])
    )*100;
    
    ###Row 6, Rx GP
    if ( $Jay_LTCs{$inNCPDP} ) {
       # ltc LTC Pharmacy Found
#      print "<tr><td>Rx GP</td><td>\$$rx_gp_disp</td><td>$rx_gp_percent_disp%</td><td>$rbsavg_rx_gp_percent_disp%</td><td>-</td><td>-</td><td>-</td><td>-</td></tr>\n";
       print "<tr><td>Rx GP</td><td>\$$rx_gp_disp</td><td>$rx_gp_percent_disp%</td><td>$rbsavg_rx_gp_percent_disp%</td><td>-</td><td>-</td><td>-</td></tr>\n";
    } else {
#      print "<tr><td>Rx GP</td><td>\$$rx_gp_disp</td><td>$rx_gp_percent_disp%</td><td>$rbsavg_rx_gp_percent_disp%</td><td>$ncpa_rx_gp%</td><td>$ncpa_top25_rx_gp%</td><td>$ncpa_sales_rx_gp%</td><td>$ncpa_location_rx_gp%</td></tr>\n";
       
       if ( $ReportMonth != '2015-12-01' ) { 
     ##    print "<tr><td>Rx GP</td><td>\$$rx_gp_disp</td><td>$rx_gp_percent_disp%</td><td>$rbsavg_rx_gp_percent_disp%</td><td>$ncpa_rx_gp%</td><td>$ncpa_sales_rx_gp%</td><td>$ncpa_location_rx_gp%</td></tr>\n";
         print "<tr><td>Rx GP</td><td>\$$rx_gp_disp</td><td>$rx_gp_percent_disp%</td><td>$rbsavg_rx_gp_percent_disp%</td><td>$ncpa_rx_gp%</td><td>$ncpa_top25_rx_gp%</td><td>$ncpa_sales_rx_gp%</td><td>$ncpa_location_rx_gp%</td></tr>\n";
       } else {
         print "<tr><td>Rx GP</td><td>\$$rx_gp_disp</td><td>$rx_gp_percent_disp%</td><td>22.8%</td><td>$ncpa_rx_gp%</td><td>$ncpa_sales_rx_gp%</td><td>$ncpa_location_rx_gp%</td></tr>\n";
       }
    }
 
    ###Row 7, Other GP
    if ( $Jay_LTCs{$inNCPDP} ) {
       # ltc LTC Pharmacy Found
#      print "<tr><td>Other GP</td><td>\$$other_gp_disp</td><td>$other_gp_percent_disp%</td><td>$rbsavg_other_gp_percent_disp%</td><td>-</td><td>-</td><td>-</td><td>-</td></tr>\n";
       print "<tr><td>Other GP</td><td>\$$other_gp_disp</td><td>$other_gp_percent_disp%</td><td>$rbsavg_other_gp_percent_disp%</td><td>-</td><td>-</td><td>-</td></tr>\n";
    } else {
      print "<tr><td>Other GP</td><td>\$$other_gp_disp</td><td>$other_gp_percent_disp%</td><td>$rbsavg_other_gp_percent_disp%</td><td>$ncpa_other_gp%</td><td>$ncpa_top25_other_gp%</td><td>$ncpa_sales_other_gp%</td><td>$ncpa_location_other_gp%</td></tr>\n";
#       print "<tr><td>Other GP</td><td>\$$other_gp_disp</td><td>$other_gp_percent_disp%</td><td>$rbsavg_other_gp_percent_disp%</td><td>$ncpa_other_gp%</td><td>$ncpa_sales_other_gp%</td><td>$ncpa_location_other_gp%</td></tr>\n";
    }

    ###Row 8, Total GP
    if ( $Jay_LTCs{$inNCPDP} ) {
       # ltc LTC Pharmacy Found
#      print "<tr><td>Total GP</td><td>\$$total_gp_disp</td><td>$total_gp_percent_disp%</td><td>$rbsavg_total_gp_percent_disp%</td><td>-</td><td>-</td><td>-</td><td>-</td></tr>\n";
       print "<tr><td>Total GP</td><td>\$$total_gp_disp</td><td>$total_gp_percent_disp%</td><td>$rbsavg_total_gp_percent_disp%</td><td>-</td><td>-</td><td>-</td></tr>\n";
    } else {
      print "<tr><td>Total GP</td><td>\$$total_gp_disp</td><td>$total_gp_percent_disp%</td><td>$rbsavg_total_gp_percent_disp%</td><td>$ncpa_total_gp%</td><td>$ncpa_top25_total_gp%</td><td>$ncpa_sales_total_gp%</td><td>$ncpa_location_total_gp%</td></tr>\n";
#       print "<tr><td>Total GP</td><td>\$$total_gp_disp</td><td>$total_gp_percent_disp%</td><td>$rbsavg_total_gp_percent_disp%</td><td>$ncpa_total_gp%</td><td>$ncpa_sales_total_gp%</td><td>$ncpa_location_total_gp%</td></tr>\n";
    }
  
    ###Blank Row
    print "<tr><td colspan=8>$nbsp</td></tr>\n";
  
    
    ###Dynamically Generate Expense Rows, all ID's over YEAR202
  
    $sql = "
    SELECT f.ncpa_category, f.ncpa_category_number, IFNULL(storeinfo.amount, 0) amount
    FROM rbsreporting.financials f 

    LEFT JOIN (
      SELECT ncpdp, ncpa_category_number, sum(net_income) as amount 
      FROM rbsreporting.financials 
      WHERE 
      ncpdp = $NCPDP && 
      year = ${YEAR}
      GROUP BY ncpa_category_number
    ) storeinfo
    ON f.ncpa_category_number = storeinfo.ncpa_category_number 

    WHERE 
    f.year = ${YEAR} 
    && f.ncpa_category_number NOT IN (${YEAR}101, ${YEAR}102, ${YEAR}201, ${YEAR}202)
    && f.ncpa_category_number < ${YEAR}500 
    GROUP BY f.ncpa_category_number
    ";
  
    $NumOfRows = 0;
    $getExpenses  = $dbx->prepare("$sql");
    $getExpenses->execute;
    $NumOfRows = $getExpenses->rows;
    if ($NumOfRows > 0) {
      while ( my @row = $getExpenses->fetchrow_array() ) {
        ($category, $id, $amount) = @row;
        $amount = $amount * -1;
        $rbsavg = $id;
        ncpa_row($all_sales, $amount, "$rbsavg", $YEAR, "$category", "$id");
      }
      $rbsavg = 0;
    }
    $getExpenses->finish;
    
    ###Blank Row
    print "<tr><th colspan=8>$nbsp</th></tr>\n";
    
    ###Total Operating Expense Row
    $pharm_expense_exp_disp = commify(sprintf "%.0f" , $pharm_expense_exp);
    $pharm_expense_percent_disp = sprintf "%.1f", ($pharm_expense_percent);
    $ncpa_average_exp    = sprintf "%.1f", ($ncpa_average_exp);
    $ncpa_top25_exp      = sprintf "%.1f", ($ncpa_top25_exp);
    $ncpa_sales_exp      = sprintf "%.1f", ($ncpa_sales_exp);
    $ncpa_location_exp   = sprintf "%.1f", ($ncpa_location_exp);
  
    $rbsavg_expense_percent_disp = sprintf "%.1f", ($rbsavg_expense_percent);
  
    if ( $Jay_LTCs{$inNCPDP} ) {
       # ltc LTC Pharmacy Found
#      print "<tr><td>Total Operating Exp.</td><td>\$$pharm_expense_exp_disp</td><td>$pharm_expense_percent_disp%</td><td>$rbsavg_expense_percent_disp%</td><td>-</td><td>-</td><td>-</td><td>-</td></tr>\n";
       print "<tr><td>Total Operating Exp.</td><td>\$$pharm_expense_exp_disp</td><td>$pharm_expense_percent_disp%</td><td>$rbsavg_expense_percent_disp%</td><td>-</td><td>-</td><td>-</td></tr>\n";
    } else {
      print "<tr><td>Total Operating Exp.</td><td>\$$pharm_expense_exp_disp</td><td>$pharm_expense_percent_disp%</td><td>$rbsavg_expense_percent_disp%</td><td>$ncpa_average_exp%</td><td>$ncpa_top25_exp%</td><td>$ncpa_sales_exp%</td><td>$ncpa_location_exp%</td></tr>\n";
#       print "<tr><td>Total Operating Exp.</td><td>\$$pharm_expense_exp_disp</td><td>$pharm_expense_percent_disp%</td><td>$rbsavg_expense_percent_disp%</td><td>$ncpa_average_exp%</td><td>$ncpa_sales_exp%</td><td>$ncpa_location_exp%</td></tr>\n";
    }
    
    ###Blank Row
    print "<tr><th colspan=8>$nbsp</th></tr>\n";
    
    ###Operating Income Row
    $pharm_net_income = sprintf "%.0f", ($total_gp - $pharm_expense_exp);
    $pharm_net_income = commify($pharm_net_income);
    $pharm_net_percent = sprintf "%.1f", ($total_gp_percent - $pharm_expense_percent);
    $ncpa_average_net  = sprintf "%.1f", ($ncpa_total_gp - $ncpa_average_exp);
    $ncpa_top25_net    = sprintf "%.1f", ($ncpa_top25_total_gp - $ncpa_top25_exp);
    $ncpa_sales_net    = sprintf "%.1f", ($ncpa_sales_total_gp - $ncpa_sales_exp);
    $ncpa_location_net = sprintf "%.1f", ($ncpa_location_total_gp - $ncpa_location_exp);
  
    $rbsavg_net_percent = 0;
    $rbsavg_net_percent = sprintf "%.1f", ($rbsavg_total_gp_percent - $rbsavg_expense_percent);
    
    
    
    if ( $Jay_LTCs{$inNCPDP} ) {
       if ( $ReportMonth != '2015-12-01' ) {
           # ltc LTC Pharmacy Found
    #      print "<tr><td><strong>Operating Income</strong></td><td>\$$pharm_net_income</td><td>$pharm_net_percent%</td><td>$rbsavg_net_percent%</td><td>-</td><td>-</td><td>-</td><td>-</td></tr>\n";
           print "<tr><td><strong>Operating Income</strong></td><td>\$$pharm_net_income</td><td>$pharm_net_percent%</td><td>$rbsavg_net_percent%</td><td>-</td><td>-</td><td>-</td></tr>\n";

       } else {
           print "<tr><td><strong>Operating Income</strong></td><td>\$$pharm_net_income</td><td>$pharm_net_percent%</td><td>4.5%</td><td>-</td><td>-</td><td>-</td></tr>\n";
       }
    } else {
#      print "<tr><td><strong>Operating Income</strong></td><td>\$$pharm_net_income</td><td>$pharm_net_percent%</td><td>$rbsavg_net_percent%</td><td>$ncpa_average_net%</td><td>$ncpa_top25_net%</td><td>$ncpa_sales_net%</td><td>$ncpa_location_net%</td></tr>\n";
       
       if ( $ReportMonth != '2015-12-01' ) {
#           print "<tr><td><strong>Operating Income</strong></td><td>\$$pharm_net_income</td><td>$pharm_net_percent%</td><td>$rbsavg_net_percent%</td><td>$ncpa_average_net%</td><td>$ncpa_sales_net%</td><td>$ncpa_location_net%</td></tr>\n";
            print "<tr><td><strong>Operating Income</strong></td><td>\$$pharm_net_income</td><td>$pharm_net_percent%</td><td>$rbsavg_net_percent%</td><td>$ncpa_average_net%</td><td>$ncpa_top25_net%</td><td>$ncpa_sales_net%</td><td>$ncpa_location_net%</td></tr>\n";
       } else {
            print "<tr><td><strong>Operating Income</strong></td><td>\$$pharm_net_income</td><td>$pharm_net_percent%</td><td>4.5%</td><td>$ncpa_average_net%</td><td>$ncpa_sales_net%</td><td>$ncpa_location_net%</td></tr>\n";
       }
    
    }
    
    $sql = "
    SELECT amount 
    FROM rbsreporting.financials 
    WHERE 
    ncpa_category_number = ${YEAR}501 
    && ncpdp = $NCPDP
    ";
    $checkInventoryData  = $dbx->prepare("$sql");
    $checkInventoryData->execute;
    $countInventoryRows = $checkInventoryData->rows;
    if ($countInventoryRows =~ /0E0/i) { $countInventoryRows = 0; }
    $checkInventoryData->finish;
  
    if ($countInventoryRows > 0) {
    
      ###Blank Row
      print "<tr><td colspan=8>$nbsp</td></tr>\n";
    
      print "<tr><th>$nbsp</th><th>&nbsp;</th><th>Store</th><th>RBS Average</th><th>NCPA<br />Average</th><th>NCPA Top<br />25 Average</th><th>$sales_category</th><th>$region</th></tr>\n";
      ncpa_row_inventory($NCPDP, $YEAR, "Inventory Turnover (Annual)", "${YEAR}501");
      ncpa_row_inventory($NCPDP, $YEAR, "Inventory Turnover (Days)", "${YEAR}502");
    
    }
  
    print "</table>";
    print "</div>";
  
  } else {
  
    ### NO Financial data found, let's show em' a static table!
  
    print qq#<div class="page">#;
    print qq#<div class="page_header"><h3>$YEAR NCPA Comparison - $Pharmacy_Name</h3></div><br />#;  
  
    print qq#<p>To complete this section, please provide Pharm AssessRBS with pharmacy financial information.</p>#;
  
    $sql = "
    SELECT amount 
    FROM rbsreporting.financials 
    WHERE 
    ncpa_category_number = ${YEAR}501 
    && ncpdp = $NCPDP
    ";
    $checkInventoryData  = $dbx->prepare("$sql");
    $checkInventoryData->execute;
    $countInventoryRows = $checkInventoryData->rows;
    if ($countInventoryRows =~ /0E0/i) { $countInventoryRows = 0; }
    $checkInventoryData->finish;
  
    if ($countInventoryRows > 0) {
  
      print qq#<table class="tableizer-table">\n#;
      print "<tr><th>$nbsp</th><th>&nbsp;</th><th>Store</th><th>RBS Average</th><th>NCPA<br />Average</th><th>NCPA Top<br />25 Average</th><th>$sales_category</th><th>$region</th></tr>\n";
      ncpa_row_inventory($NCPDP, $YEAR, "Inventory Turnover (Annual)", "${YEAR}501");
      ncpa_row_inventory($NCPDP, $YEAR, "Inventory Turnover (Days)", "${YEAR}502");
      print qq#</table>\n#;
  
    }
    
    print qq#</div>#;
  
  }
  
}

#______________________________________________________________________________

sub ncpa_row {

  ### For use in the ncpa sub to generate table rows and save data to hash

  my ($total, $row, $rbsavg, $year, $name, $id) = @_;
  
  my $pharmpercent = 0;
  if ($total > 0) {
    $pharmpercent = ($row/$total)*100;
  }
  $pharmpercent_disp = sprintf "%.1f", $pharmpercent;
  $row = sprintf "%.0f", $row;
  $row_disp = commify($row);
  
  $ncpa_average         = 0;
  $ncpa_top25           = 0;
  $sales_category_value = 0;
  $location             = 0;
  
  my $sql = qq#
SELECT category, ncpa_amount FROM rbsreporting.ncpa 
WHERE (1=1)
&& ncpa_category_number = $id
&& year = $year
#;
  
  my $NumOfRows = 0;
  $getncpadata  = $dbx->prepare("$sql");
  $getncpadata->execute;
  $NumOfRows = $getncpadata->rows;
  if ($NumOfRows > 0) {
    while ( my @row = $getncpadata->fetchrow_array() ) {
      ($category, $percent) = @row;
      $percent = ($percent)*100;
      if ($category =~ /NCPA Average/) {
        $ncpa_average = $percent;
      } elsif ($category =~ /NCPA Top 25 Average/) {
        $ncpa_top25 = $percent;
      } elsif ($category =~ /\Q$sales_category\E/) {
        $sales_category_value = $percent;
      } elsif ($category =~ /$region/) {
        $location = $percent;
      }
    }
    $ncpa_average         = sprintf "%.1f", $ncpa_average;
    $ncpa_top25           = sprintf "%.1f", $ncpa_top25;
    $sales_category_value = sprintf "%.1f", $sales_category_value;
    $location             = sprintf "%.1f", $location;
  }
  $getncpadata->finish;
  
  ### [0] = NCPA Average, [1] = Top 25 Average, [2] = Sales Category, [3] = Location / Geo
  push @{ $ncpa_data{"$id"} }, $ncpa_average, $ncpa_top25, $sales_category_value, $location;
  
  if ($total != -20000) {
  
    ### RBS Average Calculations Per Row
    if ($rbsavg > 2000299) {
      #&& $rbsavg !~ /${YEAR}501/ && $rbsavg !~ /${YEAR}502/
    
      $sql = "
      SELECT ncpa_category, ncpa_category_number, 
      sum(net_income)/($rbsavg_count) as amount 
      FROM rbsreporting.financials 
      WHERE 
      year = $year 
      && ncpa_category_number = $rbsavg 
      && ncpdp IN ($ncpdps_for_rbs_avg)
      ";
      $NumOfRows = 0;
      $getRBSAVGExpenses  = $dbx->prepare("$sql");
      $getRBSAVGExpenses->execute;
      $NumOfRows = $getRBSAVGExpenses->rows;
      if ($NumOfRows > 0) {
        while ( my @row = $getRBSAVGExpenses->fetchrow_array() ) {
          ($category, $id, $amount) = @row;
          $rbsavg = ($amount/$rbsavg_all_sales)*100;
          $rbsavg = $rbsavg * -1 if ($rbsavg < 0);
          $rbsavg_expense_percent += $rbsavg;
          $rbsavg = sprintf "%.1f", $rbsavg;
        }
      } else {
        $rbsavg = 0;
      }
      $getRBSAVGExpenses->finish;
    }
    
    ### Save Expense data totals
    my $min = "${year}299";
    $min = $min+0;
    $id = $id+0;
    if ($id > $min) {
      $pharm_expense_exp   += $row;
      $pharm_expense_percent += $pharmpercent;
      $ncpa_average_exp    += $ncpa_average;
      $ncpa_top25_exp      += $ncpa_top25;
      $ncpa_sales_exp      += $sales_category_value;
      $ncpa_location_exp   += $location;
    }
  
  }
  
  if ($pharmpercent == 0) { $pharmpercent_disp = 'N/A'; } else { $pharmpercent_disp = "$pharmpercent_disp%"; }
  if ($rbsavg == 0) { $rbsavg = 'N/A'; } else { $rbsavg = "$rbsavg%"; }
  if ($ncpa_average == 0) { $ncpa_average = 'N/A'; } else { $ncpa_average = "$ncpa_average%"; }
  if ($ncpa_top25 == 0) { $ncpa_top25 = 'N/A'; } else { $ncpa_top25 = "$ncpa_top25%"; }
  if ($sales_category_value == 0) { $sales_category_value = 'N/A'; } else { $sales_category_value = "$sales_category_value%"; }
  if ($location == 0) { $location = 'N/A'; } else { $location = "$location%"; }
  
# jlh. 01/08/2016. For Amy. Remove the #N/A line from the NCPA Comparison. It used to be Bonus/Owner Compensation.

  if ($total != -20000 && $name ne "#N/A") {
    if ( $Jay_LTCs{$inNCPDP} ) {
       # ltc LTC Pharmacy Found
       $ncpa_average         = "-";
       $ncpa_top25           = "-";
       $sales_category_value = "-";
       $location             = "-";
    }
   print "<tr><td>$name</td><td>\$$row_disp</td><td>$pharmpercent_disp</td><td>$rbsavg</td><td>$ncpa_average</td><td>$ncpa_top25</td><td>$sales_category_value</td><td>$location</td>\n";
#    print "<tr><td>$name</td><td>\$$row_disp</td><td>$pharmpercent_disp</td><td>$rbsavg</td><td>$ncpa_average</td><td>$sales_category_value</td><td>$location</td>\n";
  }

}

#______________________________________________________________________________

sub ncpa_row_inventory {

  my ($ncpdp, $year, $name, $id) = @_;
  
  $store_turnover  = 'N/A';
  $rbsavg_turnover = 'N/A';
  
  #Original query, the RBS Average section was apparently not giving the correct value.
  #We decided to instead tie to a pre-calculated 'weighted' average stored in the ncpa table (sql below).
  
  # my $sql = "
  # SELECT amount, 
  # (
    # SELECT AVG(amount)
    # FROM rbsreporting.financials 
    # LEFT JOIN officedb.pharmacy 
      # ON financials.ncpdp = pharmacy.NCPDP
    # WHERE 
    # ncpa_category_number = $id && year = $year 
    # && Status_RBS = 'Active' && RBSReporting = 'Yes'
  # ) rbsavg_amount
  # FROM rbsreporting.financials 
  # WHERE 
  # ncpa_category_number = $id && year = $year 
  # && ncpdp = $ncpdp
  # ";
  
  my $sql = "
  SELECT amount, 
  (
    SELECT ncpa_amount 
    FROM rbsreporting.ncpa 
    WHERE 
    category = 'RBS Average' && ncpa_category_number = $id
  ) rbsavg_amount
  FROM rbsreporting.financials 
  WHERE 
  ncpa_category_number = $id && year = $year 
  && ncpdp = $ncpdp
  ";
  
  my $NumOfRows = 0;
  $getinvdata  = $dbx->prepare("$sql");
  $getinvdata->execute;
  $NumOfRows = $getinvdata->rows;
  if ($NumOfRows > 0) {
    while ( my @row = $getinvdata->fetchrow_array() ) {
      ($store_turnover, $rbsavg_turnover) = @row;
    }
    $store_turnover  = sprintf "%.1f", $store_turnover;
    $rbsavg_turnover = sprintf "%.1f", $rbsavg_turnover;
  }
  $getinvdata->finish;
  
  
  
  $ncpa_average         = "N/A";
  $ncpa_top25           = "N/A";
  $sales_category_value = "N/A";
  $location             = "N/A";
  
  my $sql = "
  SELECT category, ncpa_amount FROM rbsreporting.ncpa 
  WHERE 
  ncpa_category_number = $id && year = $year
  ";
  
  my $NumOfRows = 0;
  $getncpadata  = $dbx->prepare("$sql");
  $getncpadata->execute;
  $NumOfRows = $getncpadata->rows;
  if ($NumOfRows > 0) {
    while ( my @row = $getncpadata->fetchrow_array() ) {
      ($category, $amount) = @row;
      if ($category =~ /NCPA Average/) {
        $ncpa_average = $amount;
      } elsif ($category =~ /NCPA Top 25 Average/) {
        $ncpa_top25 = $amount;
      } elsif ($category =~ /\Q$sales_category\E/) {
        $sales_category_value = $amount;
      } elsif ($category =~ /$region/) {
        $location = $amount;
      }
    }
    $ncpa_average         = sprintf "%.1f", $ncpa_average;
    $ncpa_top25           = sprintf "%.1f", $ncpa_top25;
    $sales_category_value = sprintf "%.1f", $sales_category_value;
    $location             = sprintf "%.1f", $location;
  }
  $getncpadata->finish;
  
  print "<tr><td>$name</td><td>&nbsp;</td><td>$store_turnover</td><td>$rbsavg_turnover</td><td>$ncpa_average</td><td>$ncpa_top25</td><td>$sales_category_value</td><td>$location</td>\n";
  
}

#______________________________________________________________________________

sub displayPatientInfo {

  my $section_title = "Patient Information - $Pharmacy_Name";
  print qq#<div class="page">\n#;
  print qq#<div class="page_header"><h3>$section_title</h3></div>\n#;
  
  ### Build Data Hashes ### -------------------------------------------------------------
  my %Data_Unique_Patient_Count = ();
  my %Data_Scripts_Per_Unique_Patient = ();
  
  my %Data_Sales_Per_Unique_Patient_Brand = ();
  my %Data_Sales_Per_Unique_Patient_Generic = ();
  my %Data_Sales_Per_Unique_Patient_Total = ();
  
  my %Data_GM_Per_Unique_Patient_Brand = ();
  my %Data_GM_Per_Unique_Patient_Generic = ();
  my %Data_GM_Per_Unique_Patient_Total = ();
  
  
  for (my $lyear=$yearm2; $lyear<=$yearcur; $lyear++) {
    for (my $lmonth=1; $lmonth<=12; $lmonth++) {
      $lmonth = sprintf("%02d", $lmonth);
      
      my $RepKey = "$inNCPDP##$lyear-$lmonth-01"; #Build key to retrieve data
      my $DataLoadKey = "$lyear##$lmonth";        #Build key to send data to graph
    
      my $Unique_Patients = $Rep_Unique_Patients{$RepKey} || 0;
      my $Total_Scripts = ($Rep_Total_Brand{$RepKey} + $Rep_Total_Generic{$RepKey}) || 0;
      
      my $Brand_Sales   = $Rep_Total_Brand_Revenue{$RepKey} || 0;
      my $Generic_Sales = $Rep_Total_Generic_Revenue{$RepKey} || 0;
      my $Total_Sales   = ($Brand_Sales + $Generic_Sales) || 0;
      
      my $Brand_GM   = $Rep_Total_Brand_Revenue{$RepKey} - $Rep_Total_Brand_Cost{$RepKey};
      my $Generic_GM = $Rep_Total_Generic_Revenue{$RepKey} - $Rep_Total_Generic_Cost{$RepKey};
      my $Total_GM   = ( 
                         $Rep_Total_Brand_Revenue{$RepKey} + $Rep_Total_Generic_Revenue{$RepKey} 
                         - $Rep_Total_Brand_Cost{$RepKey}    - $Rep_Total_Generic_Cost{$RepKey}
                       );
      
      ### Calculations ### ----------------------------------------------------
      my $ScriptsPerPatient = 0;

      my $Sales_Per_Unique_Patient_Brand = 0;
      my $Sales_Per_Unique_Patient_Generic = 0;
      my $Sales_Per_Unique_Patient_Total = 0;
      
      my $GM_Per_Unique_Patient_Brand = 0;
      my $GM_Per_Unique_Patient_Generic = 0;
      my $GM_Per_Unique_Patient_Total = 0;
      
      if ($Unique_Patients > 0) {
        $ScriptsPerPatient = $Total_Scripts / $Unique_Patients;
        
        $Sales_Per_Unique_Patient_Brand = $Brand_Sales / $Unique_Patients;
        $Sales_Per_Unique_Patient_Generic = $Generic_Sales / $Unique_Patients;
        $Sales_Per_Unique_Patient_Total = $Total_Sales / $Unique_Patients;
        
        $GM_Per_Unique_Patient_Brand = $Brand_GM / $Unique_Patients;
        $GM_Per_Unique_Patient_Generic = $Generic_GM / $Unique_Patients;
        $GM_Per_Unique_Patient_Total = $Total_GM / $Unique_Patients;
      } else {
        $Unique_Patients = "null";
        $ScriptsPerPatient = "null";
        
        $Sales_Per_Unique_Patient_Brand = 'null';
        $Sales_Per_Unique_Patient_Generic = 'null';
        $Sales_Per_Unique_Patient_Total = 'null';
        
        $GM_Per_Unique_Patient_Brand = 'null';
        $GM_Per_Unique_Patient_Generic = 'null';
        $GM_Per_Unique_Patient_Total = 'null';
      }
      
      
      ### End Calculations ### ------------------------------------------------
      
      #Load data to hashes with appropriate key for graph display
      $Data_Unique_Patient_Count{$DataLoadKey} = $Unique_Patients;
      $Data_Scripts_Per_Unique_Patient{$DataLoadKey} = $ScriptsPerPatient;
      
      $Data_Sales_Per_Unique_Patient_Brand{$DataLoadKey} = $Sales_Per_Unique_Patient_Brand;
      $Data_Sales_Per_Unique_Patient_Generic{$DataLoadKey} = $Sales_Per_Unique_Patient_Generic;
      $Data_Sales_Per_Unique_Patient_Total{$DataLoadKey} = $Sales_Per_Unique_Patient_Total;

      $Data_GM_Per_Unique_Patient_Brand{$DataLoadKey} = $GM_Per_Unique_Patient_Brand;
      $Data_GM_Per_Unique_Patient_Generic{$DataLoadKey} = $GM_Per_Unique_Patient_Generic;
      $Data_GM_Per_Unique_Patient_Total{$DataLoadKey} = $GM_Per_Unique_Patient_Total;
    }
  }
  ### End Data Hashes ### ---------------------------------------------------------------

  
  ### Start New Graph ### ---------------------------------------------------------------
  #Set &build_mainchart parameters
  $decimalplaces = 0;
  $rotation      = 0;
  $container     = "Unique_Patient_Count";
  $type          = 'Unique Patient Count';
  $yaxistitle    = "Count Per Month";
  $class         = "mainchart";
  $marginright   = "110";
  $legend        = "true";
  $charttype     = "Linear";
  %data = %Data_Unique_Patient_Count;
  &build_mainchart;
  print qq#<div id="$container" class="$class"></div>\n#;
  print qq#<div style="clear:both"></div>\n#;
  ### End Graph ### ---------------------------------------------------------------------
  
  
  ### Start New Graph ### ---------------------------------------------------------------
  #Set &build_mainchart parameters
  $decimalplaces = 2;
  $rotation      = 0;
  $container     = "Scripts_Per_Unique_Patient";
  $type          = 'Scripts per Unique Patient';
  $yaxistitle    = "Count Per Month";
  $class         = "mainchart";
  $marginright   = "110";
  $legend        = "true";
  $charttype     = "Linear";
  %data = %Data_Scripts_Per_Unique_Patient;
  &build_mainchart;
  print qq#<div id="$container" class="$class"></div>\n#;
  print qq#<div style="clear:both"></div>\n#;
  ### End Graph ### ---------------------------------------------------------------------
  
#  print qq#</div> <!-- end page -->\n#;

  
#  $section_title = "Patient Information (continued) - $Pharmacy_Name";
#  print qq#<div class="page">\n#;
#  print qq#<div class="page_header"><h3>$section_title</h3></div>\n#;
  
  ### Start Main Graph ### ---------------------------------------------------------------
  #Set &build_mainchart parameters
  $decimalplaces = 2;
  $rotation      = 0;
  $container     = "ID_Sales_Per_Unique_Patient_Total";
  $type          = "Sales Per Unique Patient";
  $yaxistitle    = "Dollars Per Month";
  $class         = "mainchart";
  $marginright   = "110";
  $legend        = "true";
  %data = %Data_Sales_Per_Unique_Patient_Total;
  &build_mainchart;
  print qq#<div id="$container" class="$class"></div>\n#;
  print qq#<div style="clear:both"></div>\n#;
  ### End Graph ### ---------------------------------------------------------------------
  
  ### Start Main Graph ### ---------------------------------------------------------------
  #Set &build_mainchart parameters
#  $decimalplaces = 2;
#  $rotation      = 0;
#  $container     = "ID_Total_Gross_Margin_Per_Unique_Patient";
#  $type          = "Gross Margin Per Unique Patient";
#  $yaxistitle    = "Dollars Per Month";
#  $class         = "mainchart";
#  $marginright   = "110";
#  $legend        = "true";
#  %data = %Data_GM_Per_Unique_Patient_Total;
#  &build_mainchart;
#  print qq#<div id="$container" class="$class"></div>\n#;
#  print qq#<div style="clear:both"></div>\n#;
  ### End Graph ### ---------------------------------------------------------------------
  
  ### Summary / Graph Comments ### ------------------------------------------------------
  my $summary = $Rep_sPatient_Info{$ThisReportRepKey};
  if ( $summary !~ /^\s*$/ ) {
    print qq#<div class="summary">$summary</div>\n#;
  }
  ### End Summary ### -------------------------------------------------------------------
  
  print qq#</div> <!-- end page -->\n#;

}

#______________________________________________________________________________

sub displayClaimInfo {

  my $title = "New vs. Refill Claims - $Pharmacy_Name";
  my $id = "claiminfo";
  
  my $New_Claim_Count_yearcur    = 0;
  my $New_Claim_Sales_yearcur    = 0;
  my $Refill_Claim_Count_yearcur = 0;
  my $Refill_Claim_Sales_yearcur = 0;
  
  my $New_Claim_Count_yearm1    = 0;
  my $New_Claim_Sales_yearm1    = 0;
  my $Refill_Claim_Count_yearm1 = 0;
  my $Refill_Claim_Sales_yearm1 = 0;
  
  my $New_Claim_Count_yearm2    = 0;
  my $New_Claim_Sales_yearm2    = 0;
  my $Refill_Claim_Count_yearm2 = 0;
  my $Refill_Claim_Sales_yearm2 = 0;

  foreach $RepKey ( sort {$Rep_Date{$a} cmp $Rep_Date{$b} } keys %Rep_Date) {
  
    next if ($RepKey =~ /Q/i);  
    
    my @pcs = split('##', $RepKey);
    my $tempdate = $pcs[1];
    @pcs = split('-', $tempdate);
    my $year = $pcs[0];
    my $month = $pcs[1];
    
    if      ($year == $yearm2) {
    
      $New_Claim_Count_yearm2    += $Rep_New_Claim_Count{$RepKey};
      $New_Claim_Sales_yearm2     += $Rep_New_Claim_Sales{$RepKey};
      $Refill_Claim_Count_yearm2  += $Rep_Refill_Claim_Count{$RepKey};
      $Refill_Claim_Sales_yearm2  += $Rep_Refill_Claim_Sales{$RepKey};
    
    } elsif ($year == $yearm1) {
    
      $New_Claim_Count_yearm1    += $Rep_New_Claim_Count{$RepKey};
      $New_Claim_Sales_yearm1     += $Rep_New_Claim_Sales{$RepKey};
      $Refill_Claim_Count_yearm1  += $Rep_Refill_Claim_Count{$RepKey};
      $Refill_Claim_Sales_yearm1  += $Rep_Refill_Claim_Sales{$RepKey};
    
    } elsif ($year == $yearcur) {
    
      next if ($month > $jmonth);
    
      $New_Claim_Count_yearcur    += $Rep_New_Claim_Count{$RepKey};
      $New_Claim_Sales_yearcur    += $Rep_New_Claim_Sales{$RepKey};
      $Refill_Claim_Count_yearcur += $Rep_Refill_Claim_Count{$RepKey};
      $Refill_Claim_Sales_yearcur += $Rep_Refill_Claim_Sales{$RepKey};
    
    }
  
  }
  
  my $New_Avg_Sale_Per_Script_yearcur = 0;
  my $New_Avg_Sale_Per_Script_yearm1 = 0;
  my $New_Avg_Sale_Per_Script_yearm2 = 0;
  if ($New_Claim_Count_yearcur > 0) {
    $New_Avg_Sale_Per_Script_yearcur = $New_Claim_Sales_yearcur / $New_Claim_Count_yearcur;
  $New_Avg_Sale_Per_Script_yearcur = sprintf("%.2f", $New_Avg_Sale_Per_Script_yearcur);
  }
  if ($New_Claim_Count_yearm1 > 0) {
    $New_Avg_Sale_Per_Script_yearm1 = $New_Claim_Sales_yearm1 / $New_Claim_Count_yearm1;
    $New_Avg_Sale_Per_Script_yearm1 = sprintf("%.2f", $New_Avg_Sale_Per_Script_yearm1);
  }
  if ($New_Claim_Count_yearm2 > 0) {
    $New_Avg_Sale_Per_Script_yearm2 = $New_Claim_Sales_yearm2 / $New_Claim_Count_yearm2;
    $New_Avg_Sale_Per_Script_yearm2 = sprintf("%.2f", $New_Avg_Sale_Per_Script_yearm2);
  }
  
  my $Refill_Avg_Sale_Per_Script_yearcur = 0;
  my $Refill_Avg_Sale_Per_Script_yearm1 = 0;
  my $Refill_Avg_Sale_Per_Script_yearm2 = 0;
  if ($Refill_Claim_Count_yearcur > 0) {
    $Refill_Avg_Sale_Per_Script_yearcur = $Refill_Claim_Sales_yearcur / $Refill_Claim_Count_yearcur;
    $Refill_Avg_Sale_Per_Script_yearcur = sprintf("%.2f", $Refill_Avg_Sale_Per_Script_yearcur);
  }
  if ($Refill_Claim_Count_yearm1 > 0) {
    $Refill_Avg_Sale_Per_Script_yearm1 = $Refill_Claim_Sales_yearm1 / $Refill_Claim_Count_yearm1;
    $Refill_Avg_Sale_Per_Script_yearm1 = sprintf("%.2f", $Refill_Avg_Sale_Per_Script_yearm1);
  }
  if ($Refill_Claim_Count_yearm2 > 0) {
    $Refill_Avg_Sale_Per_Script_yearm2 = $Refill_Claim_Sales_yearm2 / $Refill_Claim_Count_yearm2;
    $Refill_Avg_Sale_Per_Script_yearm2 = sprintf("%.2f", $Refill_Avg_Sale_Per_Script_yearm2);
  }
  
  print qq#
  <div class="page">
  <div class="page_header"><h3>$title</h3></div>
  <div id="$id" class="mainchart"></div>
  <div style="width: 600px; margin: 0 auto 0;">
  
    <div class="databox_container">
      <div class="databox">
        <div><strong>New Avg. Sale Per Script</strong></div>
        <div class="databox_value">\$$New_Avg_Sale_Per_Script_yearm2</div>
    </div>
      <div class="databox">
      <div><strong>Refill Avg. Sale Per Script</strong></div>
      <div class="databox_value">\$$Refill_Avg_Sale_Per_Script_yearm2</div>
    </div>
    <span>$yearm2</span>
  </div>
  
    <div class="databox_container">
      <div class="databox">
        <div><strong>New Avg. Sale Per Script</strong></div>
        <div class="databox_value">\$$New_Avg_Sale_Per_Script_yearm1</div>
    </div>
      <div class="databox">
      <div><strong>Refill Avg. Sale Per Script</strong></div>
      <div class="databox_value">\$$Refill_Avg_Sale_Per_Script_yearm1</div>
    </div>
    <span>$yearm1</span>
  </div>
  
    <div class="databox_container">
      <div class="databox">
        <div><strong>New Avg. Sale Per Script</strong></div>
        <div class="databox_value">\$$New_Avg_Sale_Per_Script_yearcur</div>
    </div>
      <div class="databox">
      <div><strong>Refill Avg. Sale Per Script</strong></div>
      <div class="databox_value">\$$Refill_Avg_Sale_Per_Script_yearcur</div>
    </div>
    <span>$yearcur</span>
  </div>
  
  <div style="clear: both;"></div>
  
  </div>
  </div> <!-- end page -->
  #;
  
  print qq@
<script>
\$(function () {
  \$('#$id').highcharts({
    chart: {
      type: 'column',
      zoomType: "y"
    },
    title: {
      text: null
    },
    credits: {
      enabled: false
    },
    xAxis: {
      categories: ['$yearm2', '$yearm1', '$yearcur']
    },
    yAxis: {
      min: 0,
      //max: 60,
      title: {
        text: 'New vs. Refill Comparison'
      }
    },
    legend: {
      enabled: false
    },
    tooltip: {
      pointFormat: '<span style="color:#000;">{series.name}</span>: <b>{point.y}</b> ({point.percentage:.1f}%)<br/>',
      shared: true
    },
    plotOptions: {
      column: {
        stacking: 'percent',
        dataLabels: {
          enabled: true,
          color: 'black',
          formatter: function () {
            return Highcharts.numberFormat(this.percentage, 1) + '% <br />' + this.series.name;
          }
        }
      }
    },
    series: [{
        name: '   New Claims',
        data: [$New_Claim_Count_yearm2, $New_Claim_Count_yearm1, $New_Claim_Count_yearcur],
        color: '#FFF',
        borderWidth: 2,
        borderColor: '#2f7ed8'
    }, {
        name: 'Refill Claims',
        data: [$Refill_Claim_Count_yearm2, $Refill_Claim_Count_yearm1, $Refill_Claim_Count_yearcur],
        color: '#FFF',
        borderWidth: 2,
        borderColor: '#0d233a'
    }]
  });
});
</script>
  @;
}

#______________________________________________________________________________

sub displayBGUtilization {

  my $title = "Brand/Generic Utilization - $Pharmacy_Name";
  my $id = "BGUtilization";
  
  my $brandCount_yearcur   = $Rep_Total_Brand{$yearcur} || 0;
  my $genericCount_yearcur = $Rep_Total_Generic{$yearcur} || 0;
  
  my $brandCount_yearm1    = $Rep_Total_Brand{$yearm1} || 0;
  my $genericCount_yearm1  = $Rep_Total_Generic{$yearm1} || 0;
  
  my $brandCount_yearm2    = $Rep_Total_Brand{$yearm2} || 0;
  my $genericCount_yearm2  = $Rep_Total_Generic{$yearm2} || 0;


  print qq#
  <div class="page">
    <div class="page_header"><h3>$title</h3></div>
    <div id="$id" class="mainchart"></div>
  </div> <!-- end page -->
  #;
  
  print qq@
<script>
\$(function () {
  \$('#$id').highcharts({
    chart: {
      type: 'column',
      zoomType: "y"
    },
    title: {
      text: null
    },
    credits: {
      enabled: false
    },
    xAxis: {
      categories: ['$yearm2', '$yearm1', '$yearcur']
    },
    yAxis: {
      min: 0,
      //max: 60,
      title: {
        text: 'Percentage (%) of Utilization'
      }
    },
    legend: {
      enabled: false
    },
    tooltip: {
        pointFormat: '<span style="color:#000;">{series.name}</span>: <b>{point.y}</b> ({point.percentage:.1f}%)<br/>',
        shared: true
    },
    plotOptions: {
      column: {
        stacking: 'percent',
        dataLabels: {
          enabled: true,
          color: 'black',
          formatter: function () {
            return Highcharts.numberFormat(this.percentage, 1) + '% ' + this.series.name;
          }
        }
      }
    },
    series: [{
        name: 'Brand',
        data: [$brandCount_yearm2, $brandCount_yearm1, $brandCount_yearcur],
        color: '#FFF',
        borderWidth: 2,
        borderColor: '#2f7ed8'
    }, {
        name: 'Generic',
        data: [$genericCount_yearm2, $genericCount_yearm1, $genericCount_yearcur],
        color: '#FFF',
        borderWidth: 2,
        borderColor: '#0d233a'
    }]
  });
});
</script>
  @;

}

#______________________________________________________________________________

sub inventoryTurns_CALC {

  my $title = "Inventory Turns - $Pharmacy_Name";
  my $id    = "inventoryTurns";

  my $count = 1;
  my $Total_Cost_NR = 0;
  my $Total_Cost_LY_NR = 0;
  my $Total_Cost_LYE_NR = 0;
  
  foreach $RepKey ( sort {$Rep_Date{$b} cmp $Rep_Date{$a} } keys %Rep_Date) {
  
    next if ($count  > 12 ); 
    next if ($RepKey =~ /Q/i);  
    
    my @pcs = split('##', $RepKey);
    my $ncpdp = $pcs[0];
    my $tempdate = $pcs[1];
    @pcs = split('-', $tempdate);
    my $year = $pcs[0];
    my $month = $pcs[1];
    
    my $lyear = $year - 1;
    ($RepKeyLY = $RepKey) =~ s/$year/$lyear/;
    
    my $scount = sprintf("%02d", $count);
    my $RepKeyLYE = "$ncpdp##$yearm1-$scount-01";
    
    $Total_Monthly_Cost_NR = $Rep_Total_Brand_Cost_NR{$RepKey} + $Rep_Total_Generic_Cost_NR{$RepKey};
    $Total_Cost_NR += $Total_Monthly_Cost_NR;
    
    $Total_Monthly_Cost_LY_NR = $Rep_Total_Brand_Cost_NR{$RepKeyLY} + $Rep_Total_Generic_Cost_NR{$RepKeyLY};
    $Total_Cost_LY_NR += $Total_Monthly_Cost_LY_NR;
    
    $Total_Monthly_Cost_LYE_NR = $Rep_Total_Brand_Cost_NR{$RepKeyLYE} + $Rep_Total_Generic_Cost_NR{$RepKeyLYE};
    $Total_Cost_LYE_NR += $Total_Monthly_Cost_LYE_NR;
    
    #print "<p>RepKey: $RepKey | Total_Monthly_Cost_NR: $Total_Monthly_Cost_NR</p>\n";
    #print "<p>RepKeyLY: $RepKeyLY | Total_Monthly_Cost_LY_NR: $Total_Monthly_Cost_LY_NR</p>\n";
    #print "<p>RepKeyLYE: $RepKeyLYE | Total_Monthly_Cost_LYE_NR: $Total_Monthly_Cost_LYE_NR</p>\n";
    #print "<hr />";
    
    $count++;
  
  }
  
  $sjmonth = sprintf("%02d", $jmonth);
  
  $InvKey    = "$inNCPDP##$yearcur-$sjmonth-01";
  $InvKeyLY  = "$inNCPDP##$yearm1-$sjmonth-01";
  $InvKeyLYE = "$inNCPDP##$yearm1-12-01";
  
  #$Rep_Inventory_Value{$RepKey};
  
  if ($Rep_Inventory_Value{$InvKey} !~ /^\s*$/) {
    $Inventory_Turns = sprintf("%0.1f", $Total_Cost_NR / $Rep_Inventory_Value{$InvKey});
    print "<p>Inventory Turns = $Inventory_Turns ($Total_Cost_NR / $Rep_Inventory_Value{$InvKey})</p>\n";
  } else {
    $Inventory_Turns = "N/A";
    print "<p>Inventory Turns = NO VALUE ENTRY FOUND!</p>";
  }
  
  if ($Rep_Inventory_Value{$InvKeyLY} !~ /^\s*$/) {
    $Inventory_TurnsLY = sprintf("%0.1f", $Total_Cost_LY_NR / $Rep_Inventory_Value{$InvKeyLY});
    print "<p>Inventory Turns Last Year = $Inventory_TurnsLY ($Total_Cost_LY_NR / $Rep_Inventory_Value{$InvKeyLY})</p>\n";
  } else {
    $Inventory_TurnsLY = "N/A";
    print "<p>Inventory Turns Last Year = NO VALUE ENTRY FOUND!</p>";
  }
  
  if ($Rep_Inventory_Value{$InvKeyLYE} !~ /^\s*$/) {
    $Inventory_TurnsLYE = sprintf("%0.1f", $Total_Cost_LYE_NR / $Rep_Inventory_Value{$InvKeyLYE});
    print "<p>Inventory Turns Last Year END = $Inventory_TurnsLYE ($Total_Cost_LYE_NR / $Rep_Inventory_Value{$InvKeyLYE})</p>\n";
  } else {
    $Inventory_TurnsLYE = "N/A";
    print "<p>Inventory Turns Last Year END = NO VALUE ENTRY FOUND!</p>";
  }
  
  
  print qq#
  <div class="page">
    <div class="page_header"><h3>$title</h3></div><br />
    
    <table class="tableizer-table">
    <tr><th>Q${jqtr} $yearcur</th><th>Q${jqtr} $yearm1</th><th>YE $yearm1</th></tr>
    <tr><td style="text-align: center;">$Inventory_Turns</td><td style="text-align: center;">$Inventory_TurnsLY</td><td style="text-align: center;">$Inventory_TurnsLYE</td></tr>
    </table>
    
  </div> <!-- end page -->
  #;

}

#______________________________________________________________________________

sub inventoryTurns {

  my $title = "Inventory Turns - $Pharmacy_Name";
  my $id    = "inventoryTurns";
  
  %Inventory_Turns = ();  

  my $sql = "
SELECT 
NCPDP, Date, Inventory_Value, Inventory_Turns
FROM $DBNAMERM.inventory_values
WHERE 1=1 
&& (NCPDP = $inNCPDP || NCPDP = -1)
";

  $sthit  = $dbx->prepare("$sql");
  $sthit->execute;

  my $NumOfRows = $sthit->rows;

  if ($NumOfRows > 0) {
    while ( my @row = $sthit->fetchrow_array() ) {
      my ( $NCPDP, $Date, $Inventory_Value, $Inventory_Turns) = @row;
      $NCPDP = sprintf("%07d", $NCPDP) if ($NCPDP != '-1');
      $InvKey = "$NCPDP##$Date";
      $Inventory_Turns{$InvKey} = $Inventory_Turns;
      $Inventory_Value{$InvKey} = $Inventory_Value;
    }
  }
  
  $sthit->finish;
  
  $sjmonth = sprintf("%02d", $jmonth);
  
  ### Pharmacy Inv Turns ### --------------------------------------------- ### 
  
  $InvKey    = "$inNCPDP##$yearcur-$sjmonth-01";
  $InvKeyLY  = "$inNCPDP##$yearm1-$sjmonth-01";
  $InvKeyLYE = "$inNCPDP##$yearm1-12-01";
  
  if ($Inventory_Turns{$InvKey} !~ /^\s*$/) {
    $Inventory_Turns = sprintf("%0.1f", $Inventory_Turns{$InvKey});
    $Inventory_Value = commify(round($Inventory_Value{$InvKey}));
  } else {
    $Inventory_Turns    = "N/A";
  }
  
  if ($Inventory_Turns{$InvKeyLY} !~ /^\s*$/) {
    $Inventory_TurnsLY = sprintf("%0.1f", $Inventory_Turns{$InvKeyLY});
    $Inventory_ValueLY = commify(round($Inventory_Value{$InvKeyLY}));
  } else {
    $Inventory_TurnsLY  = "N/A";
  }
  
  if ($Inventory_Turns{$InvKeyLYE} !~ /^\s*$/) {
    $Inventory_TurnsLYE  = sprintf("%0.1f", $Inventory_Turns{$InvKeyLYE});
    $Inventory_ValueLYE = commify(round($Inventory_Value{$InvKeyLYE}));
  } else {
    $Inventory_TurnsLYE  = "N/A";
  }
  ### -------------------------------------------------------------------- ### 
  
  
  ### RBS Avg Inv Turns ### ---------------------------------------------- ### 
  
  $AvgInvKey    = "-1##$yearcur-$sjmonth-01";
  $AvgInvKeyLY  = "-1##$yearm1-$sjmonth-01";
  $AvgInvKeyLYE = "-1##$yearm1-12-01";
  
  if ($Inventory_Turns{$AvgInvKey} !~ /^\s*$/) {
    $AvgInventory_Turns = sprintf("%0.1f", $Inventory_Turns{$AvgInvKey});
  } else {
    $AvgInventory_Turns    = "N/A";
  }
  
  if ($Inventory_Turns{$AvgInvKeyLY} !~ /^\s*$/) {
    $AvgInventory_TurnsLY = sprintf("%0.1f", $Inventory_Turns{$AvgInvKeyLY});
  } else {
    $AvgInventory_TurnsLY  = "N/A";
  }
  
  if ($Inventory_Turns{$AvgInvKeyLYE} !~ /^\s*$/) {
    $AvgInventory_TurnsLYE = sprintf("%0.1f", $Inventory_Turns{$AvgInvKeyLYE});
  } else {
    $AvgInventory_TurnsLYE  = "N/A";
  }
  ### -------------------------------------------------------------------- ### 
  
  
  print qq#
  <div class="page">
    <div class="page_header"><h3>$title</h3></div><br />
    
    <table class="tableizer-table">
      <tr>
        <th>$nbsp</th>
        <th>Q${jqtr} $yearcur</th>
        <th>Q${jqtr} $yearm1</th>
        <th>YE $yearm1</th>
      </tr><tr>
        <td style="text-align: right;">Pharmacy</td>
        <td style="text-align: center;">$Inventory_Turns</td>
        <td style="text-align: center;">$Inventory_TurnsLY</td>
        <td style="text-align: center;">$Inventory_TurnsLYE</td>
      </tr><tr>
      </tr><tr>
        <td style="text-align: right;">Pharmacy \$</td>
        <td style="text-align: center;">$Inventory_Value</td>
        <td style="text-align: center;">$Inventory_ValueLY</td>
        <td style="text-align: center;">$Inventory_ValueLYE</td>
      </tr><tr>
        <td style="text-align: right;">RBS Average</td>
        <td style="text-align: center;">$AvgInventory_Turns</td>
        <td style="text-align: center;">$AvgInventory_TurnsLY</td>
        <td style="text-align: center;">$AvgInventory_TurnsLYE</td>
      </tr>
    </table>
    
  </div> <!-- end page -->
  #;

}
 
sub get_GPI {

  my ($NDC_Number) = @_;
  my $DRUGNAME = "";
  my $GPI      = "";
  my $NDC      = 0;

  if ($GPIs{$NDC} ) {

     $GPI = $GPIs{$NDC};
     $DRUGNAME = $DRUGNAMEs{$NDC};
     $CONTROLLED_SUBSTANCE_CODE = $CONTROLLED_SUBSTANCE_CODEs{$NDC};

  } else {

    my $DBNAME  = "Medispan";
    my $TABLE   = "mf2ndc";
  
    my %attr = ( PrintWarn=>1, RaiseError=>1, PrintError=>1, AutoCommit=>1, InactiveDestroy=>0, HandleError => \&handle_error_batch );
  
    my $dbm = DBI->connect("DBI:mysql:$DBNAME:$DBHOST", $dbuser,$dbpwd, \%attr) || &handle_error_batch;
  
  #ndc_upc_hri, CONCAT(drug_name," ",strength," ",strength_unit_of_measure," - ",dosage_form), generic_product_identifier
    my $sql = "";
    $sql = qq#
  SELECT 
  ndc_upc_hri, tcgpi_name, generic_product_identifier, controlled_substance_code
  FROM $DBNAME.$TABLE
    LEFT JOIN mf2name 
      ON mf2ndc.drug_descriptor_id = mf2name.drug_descriptor_id
    LEFT JOIN mf2tcgpi 
      ON mf2name.generic_product_identifier = mf2tcgpi.tcgpi_id
  WHERE 
  ndc_upc_hri = $NDC_Number
  #;
   
    $sthLM = $dbm->prepare($sql);
    $sthLM->execute();
      
    my $NumOfRows = $sthLM->rows;
  
    if ( $NumOfRows > 0 ) {
       while ( my @row = $sthLM->fetchrow_array() ) {
          ($NDC, $DRUGNAME, $GPI, $CONTROLLED_SUBSTANCE_CODE) = @row;
       }
    }
    $sthLM->finish;
    $dbm->disconnect;

    $GPIs{$NDC}                       = $GPI;
    $DRUGNAMEs{$NDC}                  = $DRUGNAME;
    $CONTROLLED_SUBSTANCE_CODEs{$NDC} = $CONTROLLED_SUBSTANCE_CODE;
  }
  
  return($GPI, $DRUGNAME, $CONTROLLED_SUBSTANCE_CODE);

}

#______________________________________________________________________________

sub doCSClaimsgraph {

  my ($TYPE, $title) = @_;

  $pass++;
  $container = "${TYPE}_containerClaims_$pass";
  $title = "\Q$title\E";	# jlh. 02/18/2016. This fixed the "disappearing" graph problem...

print qq#

  <center>

    <script>
    \$(function () {
    
      \$( ".${container}, .${TYPE}" )
      .mouseover(function() {
        padRight = \$( this ).css('padding-right');
        \$( this ).animate({ paddingRight: '10px' }, 200);
      })
      .mouseout(function() {
        \$( this ).animate({ paddingRight: padRight }, 200);
      });
      
      //\$( ".${title}, .${TYPE}" )
      //.mouseover(function() {
      //  \$( this ).effect( "bounce", {times:2}, 300 );
      //})
    
      Highcharts.setOptions({
        colors: [
          '\#FF0000', 
          '\#00B0B0', 
          '\#880088',
          '\#FFFF00', 
          '\#005C1F'
        ]
      });
    });

    \$(function () {

      \$('\#${container}').highcharts({
        chart: {
          plotBackgroundColor: null,
          plotBorderWidth: null,
          plotShadow: false,
          margin: [50, 0, 0, 0]
        },
        title: {
          text: '$title'
        },
        tooltip: {
          pointFormat: '<b>{point.y:,.1f}</b> ({point.percentage:.1f}%)'
        },
        credits: {
          enabled: false
        }, 
        plotOptions: {
          pie: {
            size: 200,
            allowPointSelect: true,
            cursor: 'pointer',
            dataLabels: {
              enabled: true,
              color: '\#000000',
              connectorColor: '\#000000',
              format: '<b>{point.name}</b>: {point.percentage:.1f}%'
            }
          }
        },
        series: [{
          type: 'pie',
          name: 'data',
          data: [ $ClaimsString ]
        }]
      });
    });
    
    </script>
    
    <div id="$container"  style="position: relative; float: left; width: 600px; height: 450px; margin: 0 auto;"></div>

  </center>
#;

}

#______________________________________________________________________________

sub doCSDollarsgraph {

  my ($TYPE, $title) = @_;

  $container = "${TYPE}_containerDollars";
  $title = "\Q$title\E";	# jlh. 02/18/2016. This fixed the "disappearing" graph problem...

print qq#

  <center>

    <script>
    \$(function () {
    
      \$( ".${container}, .${TYPE}" )
      .mouseover(function() {
        padRight = \$( this ).css('padding-right');
        \$( this ).animate({ paddingRight: '10px' }, 200);
      })
      .mouseout(function() {
        \$( this ).animate({ paddingRight: padRight }, 200);
      });
      
      //\$( ".${title}, .${TYPE}" )
      //.mouseover(function() {
      //  \$( this ).effect( "bounce", {times:2}, 300 );
      //})

      Highcharts.setOptions({
        colors: [
          '\#FF0000', 
          '\#00B0B0', 
          '\#880088',
          '\#FFFF00', 
          '\#005C1F'
        ]
      });
    });

    \$(function () {

      \$('\#${container}').highcharts({
        chart: {
          plotBackgroundColor: null,
          plotBorderWidth: null,
          plotShadow: false,
          margin: [50, 0, 0, 0]
        },
        title: {
          text: '$title'
        },
        tooltip: {
          pointFormat: '<b>{point.y:,.1f}</b> ({point.percentage:.1f}%)'
        },
        credits: {
          enabled: false
        }, 
        plotOptions: {
          pie: {
            size: 200,
            allowPointSelect: true,
            cursor: 'pointer',
            dataLabels: {
              enabled: true,
              color: '\#000000',
              connectorColor: '\#000000',
              format: '<b>{point.name}</b>: {point.percentage:.1f}%'
            }
          }
        },
        series: [{
          type: 'pie',
          name: 'data',
          data: [ $DollarsString ]
        }]
      });
    });
    
    </script>
    
    <div id="$container"  style="position: relative; float: left; width: 600px; height: 450px; margin: 0 auto;"></div>

  </center>
#;

}

#______________________________________________________________________________

sub getdatafrom_rbsreportingfinancials {

  my ($NCPDP) = @_;
  my ($sales, $costs, $financials_sales, $other_sales, $financials_costs, $other_costs);

  my $sql = qq#
SELECT  FS.ncpdp,
 "" as "sales",
 "" as "costs",
 financials_sales, 
 other_sales,
 financials_costs,
 other_costs
FROM
(SELECT ncpdp, ncpa_category_number, format(sum(net_income),2) as "financials_sales" FROM rbsreporting.financials WHERE ncpdp=$NCPDP && ncpa_category_number=2014101) FS,
(SELECT ncpdp, ncpa_category_number, format(sum(net_income),2) as "other_sales"      FROM rbsreporting.financials WHERE ncpdp=$NCPDP && ncpa_category_number=2014102) OS,
(SELECT ncpdp, ncpa_category_number, format(sum(net_income),2) as "financials_costs" FROM rbsreporting.financials WHERE ncpdp=$NCPDP && ncpa_category_number=2014201) FC,
(SELECT ncpdp, ncpa_category_number, format(sum(net_income),2) as "other_costs"      FROM rbsreporting.financials WHERE ncpdp=$NCPDP && ncpa_category_number=2014202) OC
#;

  $sthgetdata  = $dbx->prepare("$sql");
  $sthgetdata->execute;

  my $NumOfRows = $sthgetdata->rows;

  if ( $NumOfRows > 0 ) {
    while ( my @row = $sthgetdata->fetchrow_array() ) {
       ($inncpdp, $sales, $costs, $financials_sales, $other_sales, $financials_costs, $other_costs) = @row;
    }
  }
  $sthgetdata->finish;

  $sales            =~ s/,//g;
  $costs            =~ s/,//g;
  $financials_sales =~ s/,//g;
  $other_sales      =~ s/,//g;
  $financials_costs =~ s/,//g;
  $other_costs      =~ s/,//g;

  return ($sales, $costs, $financials_sales, $other_sales, $financials_costs, $other_costs);

}
 
#______________________________________________________________________________
 
sub loadSummaries {

  my ($NCPDP, $Pharmacy_Type, $Location) = @_;

  my $sql  = "
SELECT
RowType, Pharmacy_Name, NCPDP, Pharmacy_Type, Location, Size, format(Total_Count,0), Brand_Count, Generic_Count, concat('\$', format(Total_Sale,0)), Brand_Sale, Generic_Sale, concat('\$', format(Total_GM,0)), Brand_GM, Generic_GM, Total_GM_Percent, Brand_GM_Percent, Generic_GM_Percent, Total_Sale_Per_Script, Brand_Sale_Per_Script, Generic_Sale_Per_Script, Total_GM_Per_Script, Brand_GM_Per_Script, Generic_GM_Per_Script, Unique_Patients, Average_Unique_Patients, Average_Scripts_Per_Unique_Patient, Average_Sale_Per_Unique_Patient, Average_GM_Per_Unique_Patient, New_Claim_Count, New_Claim_Sales, Refill_Claim_Count, Refill_Claim_Sales, Controlled_Count_ALL, Controlled_Count_ALL_Percent, Controlled_Sale_ALL, Controlled_Sale_ALL_Percent, Legent_Count_ALL, Legent_Count_ALL_Percent, Legend_Sale_ALL, Legend_Sale_ALL_Percent, Controlled_Count_CASH, Controlled_Count_CASH_Percent, Controlled_Sale_CASH, Controlled_Sale_CASH_Percent, Legent_Count_CASH, Legent_Count_CASH_Percent, Legend_Sale_CASH, Legend_Sale_CASH_Percent
FROM rbsreporting.rbs_averages
WHERE 1=1
&& RowType       = 'S'
&& Pharmacy_Type = '$Pharmacy_Type'
&& Location      = 'ALL'
&& Size          = 'ALL'
&& YYYYMM        = '$doMonth'
";

  $sumData  = $dbx->prepare("$sql");
  $sumData->execute;
  $rowsfound = $sumData->rows;
  
  if ($rowsfound > 0) {
  
     while ( my @row = $sumData->fetchrow_array() ) {
    
       my (
$SUM_RowType,$SUM_Pharmacy_Name,$SUM_NCPDP,$SUM_Pharmacy_Type,$SUM_Location,$SUM_Size,$SUM_Total_Count,$SUM_Brand_Count,$SUM_Generic_Count,$SUM_Total_Sale,$SUM_Brand_Sale,$SUM_Generic_Sale,$SUM_Total_GM,$SUM_Brand_GM,$SUM_Generic_GM,$SUM_Total_GM_Percent,$SUM_Brand_GM_Percent,$SUM_Generic_GM_Percent,$SUM_Total_Sale_Per_Script,$SUM_Brand_Sale_Per_Script,$SUM_Generic_Sale_Per_Script,$SUM_Total_GM_Per_Script,$SUM_Brand_GM_Per_Script,$SUM_Generic_GM_Per_Script,$SUM_Unique_Patients,$SUM_Average_Unique_Patients,$SUM_Average_Scripts_Per_Unique_Patient,$SUM_Average_Sale_Per_Unique_Patient,$SUM_Average_GM_Per_Unique_Patient,$SUM_New_Claim_Count,$SUM_New_Claim_Sales,$SUM_Refill_Claim_Count,$SUM_Refill_Claim_Sales,$SUM_Controlled_Count_ALL,$SUM_Controlled_Count_ALL_Percent,$SUM_Controlled_Sale_ALL,$SUM_Controlled_Sale_ALL_Percent,$SUM_Legent_Count_ALL,$SUM_Legent_Count_ALL_Percent,$SUM_Legend_Sale_ALL,$SUM_Legend_Sale_ALL_Percent,$SUM_Controlled_Count_CASH,$SUM_Controlled_Count_CASH_Percent,$SUM_Controlled_Sale_CASH,$SUM_Controlled_Sale_CASH_Percent,$SUM_Legent_Count_CASH,$SUM_Legent_Count_CASH_Percent,$SUM_Legend_Sale_CASH,$SUM_Legend_Sale_CASH_Percent
) = @row;

       $key = $NCPDP;
       $SUM_RowTypes{$key}                            = $SUM_RowType;
       $SUM_Pharmacy_Names{$key}                      = $SUM_Pharmacy_Name;
       $SUM_NCPDPs{$key}                              = $SUM_NCPDP;
       $SUM_Pharmacy_Types{$key}                      = $SUM_Pharmacy_Type;
       $SUM_Locations{$key}                           = $SUM_Location;
       $SUM_Sizes{$key}                               = $SUM_Size;
       $SUM_Total_Counts{$key}                        = $SUM_Total_Count;
       $SUM_Brand_Counts{$key}                        = $SUM_Brand_Count;
       $SUM_Generic_Counts{$key}                      = $SUM_Generic_Count;
       $SUM_Total_Sales{$key}                         = $SUM_Total_Sale;
       $SUM_Brand_Sales{$key}                         = $SUM_Brand_Sale;
       $SUM_Generic_Sales{$key}                       = $SUM_Generic_Sale;
       $SUM_Total_GMs{$key}                           = $SUM_Total_GM;
       $SUM_Brand_GMs{$key}                           = $SUM_Brand_GM;
       $SUM_Generic_GMs{$key}                         = $SUM_Generic_GM;
       $SUM_Total_GM_Percents{$key}                   = $SUM_Total_GM_Percent;
       $SUM_Brand_GM_Percents{$key}                   = $SUM_Brand_GM_Percent;
       $SUM_Generic_GM_Percents{$key}                 = $SUM_Generic_GM_Percent;
       $SUM_Total_Sale_Per_Scripts{$key}              = $SUM_Total_Sale_Per_Script;
       $SUM_Brand_Sale_Per_Scripts{$key}              = $SUM_Brand_Sale_Per_Script;
       $SUM_Generic_Sale_Per_Scripts{$key}            = $SUM_Generic_Sale_Per_Script;
       $SUM_Total_GM_Per_Scripts{$key}                = $SUM_Total_GM_Per_Script;
       $SUM_Brand_GM_Per_Scripts{$key}                = $SUM_Brand_GM_Per_Script;
       $SUM_Generic_GM_Per_Scripts{$key}              = $SUM_Generic_GM_Per_Script;
       $SUM_Unique_Patients{$key}                     = $SUM_Unique_Patients;
       $SUM_Average_Unique_Patientss{$key}            = $SUM_Average_Unique_Patients;
       $SUM_Average_Scripts_Per_Unique_Patients{$key} = $SUM_Average_Scripts_Per_Unique_Patient;
       $SUM_Average_Sale_Per_Unique_Patients{$key}    = $SUM_Average_Sale_Per_Unique_Patient;
       $SUM_Average_GM_Per_Unique_Patients{$key}      = $SUM_Average_GM_Per_Unique_Patient;
       $SUM_New_Claim_Counts{$key}                    = $SUM_New_Claim_Count;
       $SUM_New_Claim_Saless{$key}                    = $SUM_New_Claim_Sales;
       $SUM_Refill_Claim_Counts{$key}                 = $SUM_Refill_Claim_Count;
       $SUM_Refill_Claim_Saless{$key}                 = $SUM_Refill_Claim_Sales;
       $SUM_Controlled_Count_ALLs{$key}               = $SUM_Controlled_Count_ALL;
       $SUM_Controlled_Count_ALL_Percents{$key}       = $SUM_Controlled_Count_ALL_Percent;
       $SUM_Controlled_Sale_ALLs{$key}                = $SUM_Controlled_Sale_ALL;
       $SUM_Controlled_Sale_ALL_Percents{$key}        = $SUM_Controlled_Sale_ALL_Percent;
       $SUM_Legent_Count_ALLs{$key}                   = $SUM_Legent_Count_ALL;
       $SUM_Legent_Count_ALL_Percents{$key}           = $SUM_Legent_Count_ALL_Percent;
       $SUM_Legend_Sale_ALLs{$key}                    = $SUM_Legend_Sale_ALL;
       $SUM_Legend_Sale_ALL_Percents{$key}            = $SUM_Legend_Sale_ALL_Percent;
       $SUM_Controlled_Count_CASHs{$key}              = $SUM_Controlled_Count_CASH;
       $SUM_Controlled_Count_CASH_Percents{$key}      = $SUM_Controlled_Count_CASH_Percent;
       $SUM_Controlled_Sale_CASHs{$key}               = $SUM_Controlled_Sale_CASH;
       $SUM_Controlled_Sale_CASH_Percents{$key}       = $SUM_Controlled_Sale_CASH_Percent;
       $SUM_Legent_Count_CASHs{$key}                  = $SUM_Legent_Count_CASH;
       $SUM_Legent_Count_CASH_Percents{$key}          = $SUM_Legent_Count_CASH_Percent;
       $SUM_Legend_Sale_CASHs{$key}                   = $SUM_Legend_Sale_CASH;
       $SUM_Legend_Sale_CASH_Percent{$key}            = $SUM_Legend_Sale_CASH_Percent;

     }
  } else {
 ##   print "No SUM Summary data found!!!!<br><br>\n";
  }
  $sumData->finish;
}

#______________________________________________________________________________
 
sub loadRegions {

  my ($NCPDP, $Pharmacy_Type, $Location, $Size) = @_;

  my $sql  = "
SELECT
RowType, Pharmacy_Name, NCPDP, Pharmacy_Type, Location, Size, format(Total_Count,0), Brand_Count, Generic_Count, concat('\$', format(Total_Sale,0)), Brand_Sale, Generic_Sale, concat('\$', format(Total_GM,0)), Brand_GM, Generic_GM, Total_GM_Percent, Brand_GM_Percent, Generic_GM_Percent, Total_Sale_Per_Script, Brand_Sale_Per_Script, Generic_Sale_Per_Script, Total_GM_Per_Script, Brand_GM_Per_Script, Generic_GM_Per_Script, Unique_Patients, Average_Unique_Patients, Average_Scripts_Per_Unique_Patient, Average_Sale_Per_Unique_Patient, Average_GM_Per_Unique_Patient, New_Claim_Count, New_Claim_Sales, Refill_Claim_Count, Refill_Claim_Sales, Controlled_Count_ALL, Controlled_Count_ALL_Percent, Controlled_Sale_ALL, Controlled_Sale_ALL_Percent, Legent_Count_ALL, Legent_Count_ALL_Percent, Legend_Sale_ALL, Legend_Sale_ALL_Percent, Controlled_Count_CASH, Controlled_Count_CASH_Percent, Controlled_Sale_CASH, Controlled_Sale_CASH_Percent, Legent_Count_CASH, Legent_Count_CASH_Percent, Legend_Sale_CASH, Legend_Sale_CASH_Percent
FROM rbsreporting.rbs_averages
WHERE 1=1
&& RowType       = 'S'
&& Pharmacy_Type = '$Pharmacy_Type'
&& Location      = '$Location'
&& YYYYMM        = '$doMonth'
";

  $regionData  = $dbx->prepare("$sql");
  $regionData->execute;
  $rowsfound = $regionData->rows;
  
  if ($rowsfound > 0) {
  
     while ( my @row = $regionData->fetchrow_array() ) {
    
       my (
$REG_RowType,$REG_Pharmacy_Name,$REG_NCPDP,$REG_Pharmacy_Type,$REG_Location,$REG_Size,$REG_Total_Count,$REG_Brand_Count,$REG_Generic_Count,$REG_Total_Sale,$REG_Brand_Sale,$REG_Generic_Sale,$REG_Total_GM,$REG_Brand_GM,$REG_Generic_GM,$REG_Total_GM_Percent,$REG_Brand_GM_Percent,$REG_Generic_GM_Percent,$REG_Total_Sale_Per_Script,$REG_Brand_Sale_Per_Script,$REG_Generic_Sale_Per_Script,$REG_Total_GM_Per_Script,$REG_Brand_GM_Per_Script,$REG_Generic_GM_Per_Script,$REG_Unique_Patients,$REG_Average_Unique_Patients,$REG_Average_Scripts_Per_Unique_Patient,$REG_Average_Sale_Per_Unique_Patient,$REG_Average_GM_Per_Unique_Patient,$REG_New_Claim_Count,$REG_New_Claim_Sales,$REG_Refill_Claim_Count,$REG_Refill_Claim_Sales,$REG_Controlled_Count_ALL,$REG_Controlled_Count_ALL_Percent,$REG_Controlled_Sale_ALL,$REG_Controlled_Sale_ALL_Percent,$REG_Legent_Count_ALL,$REG_Legent_Count_ALL_Percent,$REG_Legend_Sale_ALL,$REG_Legend_Sale_ALL_Percent,$REG_Controlled_Count_CASH,$REG_Controlled_Count_CASH_Percent,$REG_Controlled_Sale_CASH,$REG_Controlled_Sale_CASH_Percent,$REG_Legent_Count_CASH,$REG_Legent_Count_CASH_Percent,$REG_Legend_Sale_CASH,$REG_Legend_Sale_CASH_Percent
) = @row;

       $key = $NCPDP;
       $REG_RowTypes{$key}                            = $REG_RowType;
       $REG_Pharmacy_Names{$key}                      = $REG_Pharmacy_Name;
       $REG_NCPDPs{$key}                              = $REG_NCPDP;
       $REG_Pharmacy_Types{$key}                      = $REG_Pharmacy_Type;
       $REG_Locations{$key}                           = $REG_Location;
       $REG_Sizes{$key}                               = $REG_Size;
       $REG_Total_Counts{$key}                        = $REG_Total_Count;
       $REG_Brand_Counts{$key}                        = $REG_Brand_Count;
       $REG_Generic_Counts{$key}                      = $REG_Generic_Count;
       $REG_Total_Sales{$key}                         = $REG_Total_Sale;
       $REG_Brand_Sales{$key}                         = $REG_Brand_Sale;
       $REG_Generic_Sales{$key}                       = $REG_Generic_Sale;
       $REG_Total_GMs{$key}                           = $REG_Total_GM;
       $REG_Brand_GMs{$key}                           = $REG_Brand_GM;
       $REG_Generic_GMs{$key}                         = $REG_Generic_GM;
       $REG_Total_GM_Percents{$key}                   = $REG_Total_GM_Percent;
       $REG_Brand_GM_Percents{$key}                   = $REG_Brand_GM_Percent;
       $REG_Generic_GM_Percents{$key}                 = $REG_Generic_GM_Percent;
       $REG_Total_Sale_Per_Scripts{$key}              = $REG_Total_Sale_Per_Script;
       $REG_Brand_Sale_Per_Scripts{$key}              = $REG_Brand_Sale_Per_Script;
       $REG_Generic_Sale_Per_Scripts{$key}            = $REG_Generic_Sale_Per_Script;
       $REG_Total_GM_Per_Scripts{$key}                = $REG_Total_GM_Per_Script;
       $REG_Brand_GM_Per_Scripts{$key}                = $REG_Brand_GM_Per_Script;
       $REG_Generic_GM_Per_Scripts{$key}              = $REG_Generic_GM_Per_Script;
       $REG_Unique_Patients{$key}                     = $REG_Unique_Patients;
       $REG_Average_Unique_Patientss{$key}            = $REG_Average_Unique_Patients;
       $REG_Average_Scripts_Per_Unique_Patients{$key} = $REG_Average_Scripts_Per_Unique_Patient;
       $REG_Average_Sale_Per_Unique_Patients{$key}    = $REG_Average_Sale_Per_Unique_Patient;
       $REG_Average_GM_Per_Unique_Patients{$key}      = $REG_Average_GM_Per_Unique_Patient;
       $REG_New_Claim_Counts{$key}                    = $REG_New_Claim_Count;
       $REG_New_Claim_Saless{$key}                    = $REG_New_Claim_Sales;
       $REG_Refill_Claim_Counts{$key}                 = $REG_Refill_Claim_Count;
       $REG_Refill_Claim_Saless{$key}                 = $REG_Refill_Claim_Sales;
       $REG_Controlled_Count_ALLs{$key}               = $REG_Controlled_Count_ALL;
       $REG_Controlled_Count_ALL_Percents{$key}       = $REG_Controlled_Count_ALL_Percent;
       $REG_Controlled_Sale_ALLs{$key}                = $REG_Controlled_Sale_ALL;
       $REG_Controlled_Sale_ALL_Percents{$key}        = $REG_Controlled_Sale_ALL_Percent;
       $REG_Legent_Count_ALLs{$key}                   = $REG_Legent_Count_ALL;
       $REG_Legent_Count_ALL_Percents{$key}           = $REG_Legent_Count_ALL_Percent;
       $REG_Legend_Sale_ALLs{$key}                    = $REG_Legend_Sale_ALL;
       $REG_Legend_Sale_ALL_Percents{$key}            = $REG_Legend_Sale_ALL_Percent;
       $REG_Controlled_Count_CASHs{$key}              = $REG_Controlled_Count_CASH;
       $REG_Controlled_Count_CASH_Percents{$key}      = $REG_Controlled_Count_CASH_Percent;
       $REG_Controlled_Sale_CASHs{$key}               = $REG_Controlled_Sale_CASH;
       $REG_Controlled_Sale_CASH_Percents{$key}       = $REG_Controlled_Sale_CASH_Percent;
       $REG_Legent_Count_CASHs{$key}                  = $REG_Legent_Count_CASH;
       $REG_Legent_Count_CASH_Percents{$key}          = $REG_Legent_Count_CASH_Percent;
       $REG_Legend_Sale_CASHs{$key}                   = $REG_Legend_Sale_CASH;
       $REG_Legend_Sale_CASH_Percent{$key}            = $REG_Legend_Sale_CASH_Percent;

     }
  } else {
   ## print "No REG Summary data found!!!!<br><br>\n";
  }
  $regionData->finish;
}

#______________________________________________________________________________
 
sub loadSizes {

  my ($NCPDP, $Pharmacy_Type, $Location, $Size) = @_;

  my $sql  = "
SELECT
RowType, Pharmacy_Name, NCPDP, Pharmacy_Type, Location, Size, format(Total_Count,0), Brand_Count, Generic_Count, concat('\$', format(Total_Sale,0)), Brand_Sale, Generic_Sale, concat('\$', format(Total_GM,0)), Brand_GM, Generic_GM, Total_GM_Percent, Brand_GM_Percent, Generic_GM_Percent, Total_Sale_Per_Script, Brand_Sale_Per_Script, Generic_Sale_Per_Script, Total_GM_Per_Script, Brand_GM_Per_Script, Generic_GM_Per_Script, Unique_Patients, Average_Unique_Patients, Average_Scripts_Per_Unique_Patient, Average_Sale_Per_Unique_Patient, Average_GM_Per_Unique_Patient, New_Claim_Count, New_Claim_Sales, Refill_Claim_Count, Refill_Claim_Sales, Controlled_Count_ALL, Controlled_Count_ALL_Percent, Controlled_Sale_ALL, Controlled_Sale_ALL_Percent, Legent_Count_ALL, Legent_Count_ALL_Percent, Legend_Sale_ALL, Legend_Sale_ALL_Percent, Controlled_Count_CASH, Controlled_Count_CASH_Percent, Controlled_Sale_CASH, Controlled_Sale_CASH_Percent, Legent_Count_CASH, Legent_Count_CASH_Percent, Legend_Sale_CASH, Legend_Sale_CASH_Percent
FROM rbsreporting.rbs_averages
WHERE 1=1
&& RowType       = 'S'
&& Pharmacy_Type = '$Pharmacy_Type'
&& Location      = 'ALL'
&& Size          = '$Size'
&& YYYYMM        = '$doMonth'

";

  $sizeData  = $dbx->prepare("$sql");
  $sizeData->execute;
  $rowsfound = $sizeData->rows;
  
  if ($rowsfound > 0) {
  
     while ( my @row = $sizeData->fetchrow_array() ) {
    
       my (
$SIZ_RowType,$SIZ_Pharmacy_Name,$SIZ_NCPDP,$SIZ_Pharmacy_Type,$SIZ_Location,$SIZ_Size,$SIZ_Total_Count,$SIZ_Brand_Count,$SIZ_Generic_Count,$SIZ_Total_Sale,$SIZ_Brand_Sale,$SIZ_Generic_Sale,$SIZ_Total_GM,$SIZ_Brand_GM,$SIZ_Generic_GM,$SIZ_Total_GM_Percent,$SIZ_Brand_GM_Percent,$SIZ_Generic_GM_Percent,$SIZ_Total_Sale_Per_Script,$SIZ_Brand_Sale_Per_Script,$SIZ_Generic_Sale_Per_Script,$SIZ_Total_GM_Per_Script,$SIZ_Brand_GM_Per_Script,$SIZ_Generic_GM_Per_Script,$SIZ_Unique_Patients,$SIZ_Average_Unique_Patients,$SIZ_Average_Scripts_Per_Unique_Patient,$SIZ_Average_Sale_Per_Unique_Patient,$SIZ_Average_GM_Per_Unique_Patient,$SIZ_New_Claim_Count,$SIZ_New_Claim_Sales,$SIZ_Refill_Claim_Count,$SIZ_Refill_Claim_Sales,$SIZ_Controlled_Count_ALL,$SIZ_Controlled_Count_ALL_Percent,$SIZ_Controlled_Sale_ALL,$SIZ_Controlled_Sale_ALL_Percent,$SIZ_Legent_Count_ALL,$SIZ_Legent_Count_ALL_Percent,$SIZ_Legend_Sale_ALL,$SIZ_Legend_Sale_ALL_Percent,$SIZ_Controlled_Count_CASH,$SIZ_Controlled_Count_CASH_Percent,$SIZ_Controlled_Sale_CASH,$SIZ_Controlled_Sale_CASH_Percent,$SIZ_Legent_Count_CASH,$SIZ_Legent_Count_CASH_Percent,$SIZ_Legend_Sale_CASH,$SIZ_Legend_Sale_CASH_Percent
) = @row;

       $key = $NCPDP;
       $SIZ_RowTypes{$key}                            = $SIZ_RowType;
       $SIZ_Pharmacy_Names{$key}                      = $SIZ_Pharmacy_Name;
       $SIZ_NCPDPs{$key}                              = $SIZ_NCPDP;
       $SIZ_Pharmacy_Types{$key}                      = $SIZ_Pharmacy_Type;
       $SIZ_Locations{$key}                           = $SIZ_Location;
       $SIZ_Sizes{$key}                               = $SIZ_Size;
       $SIZ_Total_Counts{$key}                        = $SIZ_Total_Count;
       $SIZ_Brand_Counts{$key}                        = $SIZ_Brand_Count;
       $SIZ_Generic_Counts{$key}                      = $SIZ_Generic_Count;
       $SIZ_Total_Sales{$key}                         = $SIZ_Total_Sale;
       $SIZ_Brand_Sales{$key}                         = $SIZ_Brand_Sale;
       $SIZ_Generic_Sales{$key}                       = $SIZ_Generic_Sale;
       $SIZ_Total_GMs{$key}                           = $SIZ_Total_GM;
       $SIZ_Brand_GMs{$key}                           = $SIZ_Brand_GM;
       $SIZ_Generic_GMs{$key}                         = $SIZ_Generic_GM;
       $SIZ_Total_GM_Percents{$key}                   = $SIZ_Total_GM_Percent;
       $SIZ_Brand_GM_Percents{$key}                   = $SIZ_Brand_GM_Percent;
       $SIZ_Generic_GM_Percents{$key}                 = $SIZ_Generic_GM_Percent;
       $SIZ_Total_Sale_Per_Scripts{$key}              = $SIZ_Total_Sale_Per_Script;
       $SIZ_Brand_Sale_Per_Scripts{$key}              = $SIZ_Brand_Sale_Per_Script;
       $SIZ_Generic_Sale_Per_Scripts{$key}            = $SIZ_Generic_Sale_Per_Script;
       $SIZ_Total_GM_Per_Scripts{$key}                = $SIZ_Total_GM_Per_Script;
       $SIZ_Brand_GM_Per_Scripts{$key}                = $SIZ_Brand_GM_Per_Script;
       $SIZ_Generic_GM_Per_Scripts{$key}              = $SIZ_Generic_GM_Per_Script;
       $SIZ_Unique_Patients{$key}                     = $SIZ_Unique_Patients;
       $SIZ_Average_Unique_Patientss{$key}            = $SIZ_Average_Unique_Patients;
       $SIZ_Average_Scripts_Per_Unique_Patients{$key} = $SIZ_Average_Scripts_Per_Unique_Patient;
       $SIZ_Average_Sale_Per_Unique_Patients{$key}    = $SIZ_Average_Sale_Per_Unique_Patient;
       $SIZ_Average_GM_Per_Unique_Patients{$key}      = $SIZ_Average_GM_Per_Unique_Patient;
       $SIZ_New_Claim_Counts{$key}                    = $SIZ_New_Claim_Count;
       $SIZ_New_Claim_Saless{$key}                    = $SIZ_New_Claim_Sales;
       $SIZ_Refill_Claim_Counts{$key}                 = $SIZ_Refill_Claim_Count;
       $SIZ_Refill_Claim_Saless{$key}                 = $SIZ_Refill_Claim_Sales;
       $SIZ_Controlled_Count_ALLs{$key}               = $SIZ_Controlled_Count_ALL;
       $SIZ_Controlled_Count_ALL_Percents{$key}       = $SIZ_Controlled_Count_ALL_Percent;
       $SIZ_Controlled_Sale_ALLs{$key}                = $SIZ_Controlled_Sale_ALL;
       $SIZ_Controlled_Sale_ALL_Percents{$key}        = $SIZ_Controlled_Sale_ALL_Percent;
       $SIZ_Legent_Count_ALLs{$key}                   = $SIZ_Legent_Count_ALL;
       $SIZ_Legent_Count_ALL_Percents{$key}           = $SIZ_Legent_Count_ALL_Percent;
       $SIZ_Legend_Sale_ALLs{$key}                    = $SIZ_Legend_Sale_ALL;
       $SIZ_Legend_Sale_ALL_Percents{$key}            = $SIZ_Legend_Sale_ALL_Percent;
       $SIZ_Controlled_Count_CASHs{$key}              = $SIZ_Controlled_Count_CASH;
       $SIZ_Controlled_Count_CASH_Percents{$key}      = $SIZ_Controlled_Count_CASH_Percent;
       $SIZ_Controlled_Sale_CASHs{$key}               = $SIZ_Controlled_Sale_CASH;
       $SIZ_Controlled_Sale_CASH_Percents{$key}       = $SIZ_Controlled_Sale_CASH_Percent;
       $SIZ_Legent_Count_CASHs{$key}                  = $SIZ_Legent_Count_CASH;
       $SIZ_Legent_Count_CASH_Percents{$key}          = $SIZ_Legent_Count_CASH_Percent;
       $SIZ_Legend_Sale_CASHs{$key}                   = $SIZ_Legend_Sale_CASH;
       $SIZ_Legend_Sale_CASH_Percent{$key}            = $SIZ_Legend_Sale_CASH_Percent;

     }
  } else {
   ## print "No SIZ Summary data found!!!!<br><br>\n";
  }
  $sizeData->finish;
}

#______________________________________________________________________________

sub build_cs_chart {
  $data1     = shift;
  $data2     = shift;
  $data3     = shift;
  $container = shift;

  $charttype =~ s/^\s*(.*?)\s*$/$1/;    # trim leading and trailing white spaces

  $rotation      = -30;
  $decimalplaces = 1;
  $yaxistitle    = "Percentage %";
  $count         = 'Count';
  $count         = 'Dollars' if($charttype =~ 'Dollars');

print <<BM;

<!-- Line Chart Generation -->

<script type="text/javascript">
\$(function () {
  var chart;
  \$(document).ready(function() {
    chart = new Highcharts.Chart({
      chart: {
        renderTo: '$container',
        type: 'line',
        marginBottom: 80 
      },
      credits: {
        enabled: false
      },
      title: {
        text: 'Controlled Substance - $charttype',
        x: -20 //center
      },
      xAxis: {
        categories: [$month_str],
        labels: {
          rotation: $rotation
        }
      },
      yAxis: {
        gridLineWidth: 2,
        title: {
          text: '$yaxistitle'
        },
        min:0,
        plotLines: [{
          value: 0,
          width: 1,
          color: '#808080'
        }],
        minPadding: 0.5,
        maxPadding: 0.5
      },
      tooltip: {
        formatter: function() {
          var s = 'Year/Month: '+ this.x;

          \$.each(this.points, function(i, point) {
            s += '<br/>'+'<b>'+ point.series.name +'</b>: '+
            Highcharts.numberFormat(this.y,$decimalplaces);
          });

          return s;
        },
        shared: true,
        borderColor: '#000000',
        crosshairs: true
      },
      legend: {
        borderWidth: 0,
        itemDistance:50
      },
      plotOptions: {
        series: {
          animation: false
        }
      },
      series: [{
        name: 'Controlled $count %',
        color: '#c0504d',
        data: [$data1]
      }, {
        name: 'CII $count %',
        color: '#9bbb59',
        data: [$data2]
      }, {
      name: 'CIII - CV $count %',
        color: '#4f81bd',
        data: [$data3]
      }]
    });
  });
});
</script>

BM
print qq# <br><br><br> #;
}

sub displayControlledSubstanceClaims_ALL {
  $charttype  = "ALL Claims";
  $container     = "Controlled Substances";
  &build_cs_chart($all_cs_cnt, $cash_c2_cnt, $all_c35_cnt, $container);


  print qq#<div id="$container" class="mainchart"></div>\n#;
}

sub displayControlledSubstanceClaims_CASH {
  $charttype  = "CASH Claims";
  $container     = "Controlled Substances3";
  &build_cs_chart($cash_cnt, $all_c2_cash_cnt, $c35_cash_cnt, $container);

  print qq#<div id="$container" class="mainchart"></div>\n#;
}

sub displayControlledSubstanceDollars_ALL {
  $charttype  = "ALL Dollars";
  $container     = "Controlled Substances2";
  &build_cs_chart($all_cs_dollar, $all_c2_dollar, $all_c35_dollar, $container);

  print qq#<div id="$container" class="mainchart"></div>\n#;
}

sub displayControlledSubstanceDollars_CASH {
  $charttype  = "CASH Dollars";
  $container     = "Controlled Substances4";
  &build_cs_chart($cash_cs_dollar, $c2_cash_dollar, $c35_cash_dollar, $container);

  print qq#<div id="$container" class="mainchart"></div>\n#;
}

sub displayControlledSubstanceUnits_ALL {
  $charttype  = "ALL Units";
  $container     = "Controlled Substances5";
  &build_cs_chart($all_cs_unit, $all_c2_unit, $all_c35_unit, $container);

  print qq#<div id="$container" class="mainchart"></div>\n#;
}

sub displayControlledSubstanceUnits_CASH {
  $charttype  = "CASH Units";
  $container     = "Controlled Substances6";
  &build_cs_chart($cash_cs_unit, $cash_c2_unit, $c35_cash_unit, $container);

  print qq#<div id="$container" class="mainchart"></div>\n#;
}

sub getControlledSubstanceTotals {
  $doCS = 0;
  my $DBNAME = "RBSReporting";
  my $TABLE  = "controlled_substances_tds";

  my $sql = qq# 
    SELECT NCPDP,Month,Pharmacy_Name,Legend_Cash_Count,Legend_Cash_Dollars,Legend_NonCash_Count,Legend_NonCash_Dollars,CII_Cash_Count,CII_Cash_Dollars,CII_NonCash_Count,CII_NonCash_Dollars,CIII_Cash_Count,
           CIII_Cash_Dollars,CIII_NonCash_Count,CIII_NonCash_Dollars,CIV_Cash_Count,CIV_Cash_Dollars,CIV_NonCash_Count,CIV_NonCash_Dollars,CV_Cash_Count,CV_Cash_Dollars,CV_NonCash_Count,CV_NonCash_Dollars,
           Legend_Cash_Unit,Legend_NonCash_Unit,CII_Cash_Unit,CII_NonCash_Unit,CIII_Cash_Unit,CIII_NonCash_Unit,CIV_Cash_Unit,CIV_NonCash_Unit,CV_Cash_Unit,CV_NonCash_Unit
      FROM $DBNAME.`$TABLE`
     WHERE 1=1
        && Pharmacy_ID = $PH_ID
        && Month >= $year2
  #;

  $sthx  = $dbx->prepare("$sql");
  $sthx->execute;

  my $totalCSCfound = $sthx->rows;

  if ( $totalCSCfound > 0 ) {
    while ( my @row = $sthx->fetchrow_array() ) {
       ($NCPDP,$Month,$pharmacy_name,$Legend_Cash_Count,$Legend_Cash_Dollars,$Legend_NonCash_Count,$Legend_NonCash_Dollars,$CII_Cash_Count,$CII_Cash_Dollars,$CII_NonCash_Count,
        $CII_NonCash_Dollars,$CIII_Cash_Count,$CIII_Cash_Dollars,$CIII_NonCash_Count,$CIII_NonCash_Dollars,$CIV_Cash_Count,$CIV_Cash_Dollars,$CIV_NonCash_Count,$CIV_NonCash_Dollars,
        $CV_Cash_Count,$CV_Cash_Dollars,$CV_NonCash_Count,$CV_NonCash_Dollars,$Legend_Cash_Unit,$Legend_NonCash_Unit,$CII_Cash_Unit,$CII_NonCash_Unit,$CIII_Cash_Unit,$CIII_NonCash_Unit,
        $CIV_Cash_Unit,$CIV_NonCash_Unit,$CV_Cash_Unit,$CV_NonCash_Unit) = @row;

       $Pharmacy_Name = $pharmacy_name;

       #### COUNT        
       $CII_Cash_Count_ALL      = $CII_Cash_Count    + $CII_NonCash_Count;
       $CIII_Cash_Count_ALL     = $CIII_Cash_Count   + $CIII_NonCash_Count;
       $CIV_Cash_Count_ALL      = $CIV_Cash_Count    + $CIV_NonCash_Count;
       $CV_Cash_Count_ALL       = $CV_Cash_Count     + $CV_NonCash_Count;
       $Legend_Cash_Count_ALL   = $Legend_Cash_Count + $Legend_NonCash_Count;

       $Cash_Count_Total = $CII_Cash_Count + $CIII_Cash_Count + $CIV_Cash_Count + $CV_Cash_Count + $Legend_Cash_Count;
       $Cash_Count_ALL   = $CII_Cash_Count_ALL + $CIII_Cash_Count_ALL + $CIV_Cash_Count_ALL + $CV_Cash_Count_ALL + $Legend_Cash_Count_ALL;

       if(!$CII_Cash_Count_ALL||!$Cash_Count_ALL) {
         $CII_Cash_Count_ALL_PCT  = sprintf("%.01f",0);
       }
       else {
         $CII_Cash_Count_ALL_PCT  = sprintf("%.01f", ($CII_Cash_Count_ALL    / $Cash_Count_ALL) * 100);
       }
       if (!$CII_Cash_Count ||!$Cash_Count_Total) {
         $CII_Cash_Count_PCT = sprintf("%.01f",0);
       }
       else {
         $CII_Cash_Count_PCT   = sprintf("%.01f", ($CII_Cash_Count    / $Cash_Count_Total) * 100);
       }

       $C35_Cash_Count_ALL     = $CIII_Cash_Count_ALL + $CIV_Cash_Count_ALL + $CV_Cash_Count_ALL;
       $C35_Cash_Count         = $CIII_Cash_Count + $CIV_Cash_Count + $CV_Cash_Count;

       if (!$Cash_Count_ALL) {
         $C35_Cash_Count_ALL_PCT = sprintf("%.01f", 0);
       }
       else {
         $C35_Cash_Count_ALL_PCT = sprintf("%.01f", ($C35_Cash_Count_ALL  / $Cash_Count_ALL) * 100);
       }

       if (!$Cash_Count_Total) {
         $C35_Cash_Count_PCT = sprintf("%.01f", 0);
       }
       else {
         $C35_Cash_Count_PCT = sprintf("%.01f", ($C35_Cash_Count / $Cash_Count_Total) * 100);
       }
  
       #### DOLLARS
       $CII_Cash_Dollars_ALL    = $CII_Cash_Dollars    + $CII_NonCash_Dollars;
       $CIII_Cash_Dollars_ALL   = $CIII_Cash_Dollars   + $CIII_NonCash_Dollars;
       $CIV_Cash_Dollars_ALL    = $CIV_Cash_Dollars    + $CIV_NonCash_Dollars;
       $CV_Cash_Dollars_ALL     = $CV_Cash_Dollars     + $CV_NonCash_Dollars;
       $Legend_Cash_Dollars_ALL = $Legend_Cash_Dollars + $Legend_NonCash_Dollars;

       $Cash_Dollars_Total = $CII_Cash_Dollars + $CIII_Cash_Dollars + $CIV_Cash_Dollars + $CV_Cash_Dollars + $Legend_Cash_Dollars;
       $Cash_Dollars_ALL   =$Legend_Cash_Dollars_ALL+$CII_Cash_Dollars_ALL+$CIII_Cash_Dollars_ALL+$CIV_Cash_Dollars_ALL+$CV_Cash_Dollars_ALL;
  
       if (!$Cash_Dollars_Total) {
         $CII_Cash_Dollars_PCT    = sprintf("%.01f", 0);
       }
       else {
         $CII_Cash_Dollars_PCT    = sprintf("%.01f",  ($CII_Cash_Dollars    / $Cash_Dollars_Total) * 100);
       }
       if (!$Cash_Dollars_ALL) {
         $CII_Cash_Dollars_ALL_PCT = sprintf("%.01f", 0);
       }
       else {
         $CII_Cash_Dollars_ALL_PCT = sprintf("%.01f",  ($CII_Cash_Dollars_ALL/ $Cash_Dollars_ALL) * 100);
       }

       $C35_Cash_Dollar_ALL     = $CIII_Cash_Dollars_ALL + $CIV_Cash_Dollars_ALL + $CV_Cash_Dollars_ALL;
       $C35_Cash_Dollar         = $CIII_Cash_Dollars + $CIV_Cash_Dollars + $CV_Cash_Dollars;

       if (!$Cash_Dollars_ALL) {
         $C35_Cash_Dollars_ALL_PCT = sprintf("%.01f", 0);
       }
       else {
         $C35_Cash_Dollars_ALL_PCT = sprintf("%.01f", ($C35_Cash_Dollar_ALL / $Cash_Dollars_ALL) * 100);
       }

       if (!$Cash_Dollars_Total) {
         $C35_Cash_Dollars_PCT = sprintf("%.01f", 0);
       }
       else {
         $C35_Cash_Dollars_PCT = sprintf("%.01f", ($C35_Cash_Dollar / $Cash_Dollars_Total) * 100);
       }

       #### UNITS
       $CII_Cash_Unit_ALL      = $CII_Cash_Unit    + $CII_NonCash_Unit;
       $CIII_Cash_Unit_ALL     = $CIII_Cash_Unit   + $CIII_NonCash_Unit;
       $CIV_Cash_Unit_ALL      = $CIV_Cash_Unit    + $CIV_NonCash_Unit;
       $CV_Cash_Unit_ALL       = $CV_Cash_Unit     + $CV_NonCash_Unit;
       $Legend_Cash_Unit_ALL   = $Legend_Cash_Unit + $Legend_NonCash_Unit;
  
       $Cash_Unit_Total = $CII_Cash_Unit + $CIII_Cash_Unit + $CIV_Cash_Unit + $CV_Cash_Unit + $Legend_Cash_Unit;
       $Cash_Unit_ALL   = $CII_Cash_Unit_ALL + $CIII_Cash_Unit_ALL + $CIV_Cash_Unit_ALL + $CV_Cash_Unit_ALL + $Legend_Cash_Unit_ALL;

       if(!$CII_Cash_Unit_ALL||!$Cash_Unit_ALL) {
         $CII_Cash_Unit_ALL_PCT  = sprintf("%.01f",0);
       }
       else {
         $CII_Cash_Unit_ALL_PCT  = sprintf("%.01f", ($CII_Cash_Unit_ALL    / $Cash_Unit_ALL) * 100);
       }
       if (!$CII_Cash_Unit ||!$Cash_Unit_Total) {
         $CII_Cash_Unit_PCT = sprintf("%.01f",0);
       }
       else {
         $CII_Cash_Unit_PCT      = sprintf("%.01f", ($CII_Cash_Unit    / $Cash_Unit_Total) * 100);
       }

       $C35_Cash_Unit_ALL     = $CIII_Cash_Unit_ALL + $CIV_Cash_Unit_ALL + $CV_Cash_Unit_ALL;
       $C35_Cash_Unit         = $CIII_Cash_Unit + $CIV_Cash_Unit + $CV_Cash_Unit;

       if (!$Cash_Unit_ALL) {
         $C35_Cash_Unit_ALL_PCT = sprintf("%.01f", 0);
       }
       else {
         $C35_Cash_Unit_ALL_PCT = sprintf("%.01f", ($C35_Cash_Unit_ALL / $Cash_Unit_ALL) * 100);
       }

       if (!$Cash_Unit_Total) {
         $C35_Cash_Unit_PCT = sprintf("%.01f", 0);
       }
       else {
         $C35_Cash_Unit_PCT = sprintf("%.01f", ($C35_Cash_Unit / $Cash_Unit_Total) * 100);
       }

       #### Do "ALL" Calculations
       $All_Controlled_Substance_Count        = $Cash_Count_ALL - $Legend_Cash_Count_ALL;
       $All_Controlled_Substance_Dollars      = $CII_Cash_Dollars_ALL+$CIII_Cash_Dollars_ALL+$CIV_Cash_Dollars_ALL+$CV_Cash_Dollars_ALL;
       $All_Controlled_Substance_Unit         = $Cash_Unit_ALL - $Legend_Cash_Unit_ALL;
       $All_Controlled_Substance_Cash_Dollars = $CII_Cash_Dollars +$CIII_Cash_Dollars +$CIV_Cash_Dollars +$CV_Cash_Dollars;
       $All_Controlled_Substance_Cash_Count   = $Cash_Count_Total - $Legend_Cash_Count;
       $All_Controlled_Substance_Cash_Unit    = $Cash_Unit_Total - $Legend_Cash_Unit;

       #### Do Percentage Calculations
       ### CASH BY COUNT
       if (!$Cash_Count_Total) {
         $Claims_Count_PCT = sprintf("%.01f", 0);
       }
       else {
         $Claims_Count_PCT                     = sprintf("%.01f", ($All_Controlled_Substance_Cash_Count / $Cash_Count_Total) * 100);
       }

       ### ALL BY COUNT
       if (!$Cash_Count_ALL) {
         $All_Controlled_Substance_Count_PCT = sprintf("%.01f", 0);
       }
       else {
         $All_Controlled_Substance_Count_PCT   = sprintf("%.01f", ($All_Controlled_Substance_Count / $Cash_Count_ALL) * 100);
       }

       ### ALL BY DOLLAR
       if (!$Cash_Dollars_ALL) {
         $All_Controlled_Substance_Dollars_PCT = sprintf("%.01f", 0);
       }
       else {
         $All_Controlled_Substance_Dollars_PCT = sprintf("%.01f", ($All_Controlled_Substance_Dollars / $Cash_Dollars_ALL) * 100);
       }

       ### ALL BY UNIT
       if (!$Cash_Unit_ALL) {
         $All_Controlled_Substance_Unit_PCT = sprintf("%.01f", 0);
       }
       else {
         $All_Controlled_Substance_Unit_PCT    = sprintf("%.01f", ($All_Controlled_Substance_Unit / $Cash_Unit_ALL) * 100);
       }

       ### CASH BY DOLLAR
       if (!$Cash_Dollars_Total) {
         $Cash_PCT = sprintf("%.01f", 0);
       }
       else {
         $Cash_PCT = sprintf("%.01f", ($All_Controlled_Substance_Cash_Dollars / $Cash_Dollars_Total) * 100);
       }

       ### CASH BY UNIT
       if (!$Cash_Unit_Total) {
         $Claims_Unit_PCT = sprintf("%.01f", 0);
       }
       else {
         $Claims_Unit_PCT    = sprintf("%.01f", ($All_Controlled_Substance_Cash_Unit / $Cash_Unit_Total) * 100);
       }


       #### Add to chart variables
       $month_str     .= "'$Month',"; 

       $all_cs_cnt      .= "$All_Controlled_Substance_Count_PCT,";
       $all_c2_cash_cnt .= "$CII_Cash_Count_PCT,";
       $all_c35_cnt     .= "$C35_Cash_Count_ALL_PCT,"; 

       $all_cs_dollar  .= "$All_Controlled_Substance_Dollars_PCT,"; 
       $all_c2_dollar  .= "$CII_Cash_Dollars_ALL_PCT,"; 
       $all_c35_dollar .= "$C35_Cash_Dollars_ALL_PCT,"; 

       $all_cs_unit  .= "$All_Controlled_Substance_Unit_PCT,"; 
       $all_c2_unit  .= "$CII_Cash_Unit_ALL_PCT,"; 
       $all_c35_unit .= "$C35_Cash_Unit_ALL_PCT,"; 

       $cash_cnt      .= "$Claims_Count_PCT,"; 
       $cash_c2_cnt   .= "$CII_Cash_Count_ALL_PCT,"; 
       $c35_cash_cnt  .= "$C35_Cash_Count_PCT,"; 

       $cash_cs_dollar  .= "$Cash_PCT,";
       $c2_cash_dollar  .= "$CII_Cash_Dollars_PCT,"; 
       $c35_cash_dollar .= "$C35_Cash_Dollars_PCT,"; 
  
       $cash_cs_unit   .= "$Claims_Unit_PCT,"; 
       $cash_c2_unit   .= "$CII_Cash_Unit_PCT,"; 
       $c35_cash_unit  .= "$C35_Cash_Unit_PCT,"; 

    }

    $doCS = 1;
  } 

  $sthx->finish;
}

#______________________________________________________________________________

sub displayMedSync {

  my $section_title = "Medsync Information - $Pharmacy_Name";
  print qq#<div class="page">\n#;
  print qq#<div class="page_header"><h3>$section_title</h3></div>\n#;
  
  ### Build Data Hashes ### -------------------------------------------------------------
  my %Data_Unique_Patient_Count = ();
  my %Data_Scripts_Per_Unique_Patient = ();
  
  my %Data_Sales_Per_Unique_Patient_Brand = ();
  my %Data_Sales_Per_Unique_Patient_Generic = ();
  my %Data_Sales_Per_Unique_Patient_Total = ();
  
  my %Data_GM_Per_Unique_Patient_Brand = ();
  my %Data_GM_Per_Unique_Patient_Generic = ();
  my %Data_GM_Per_Unique_Patient_Total = ();
  
  
  for (my $lyear=$yearm2; $lyear<=$yearcur; $lyear++) {
    for (my $lmonth=1; $lmonth<=12; $lmonth++) {
      $lmonth = sprintf("%02d", $lmonth);
      
      my $RepKey = "$inNCPDP##$lyear-$lmonth-01"; #Build key to retrieve data
      my $DataLoadKey = "$lyear##$lmonth";        #Build key to send data to graph
    
      my $Unique_Synced_Patients = $Rep_Synced_Patients{$RepKey} || 0;
      my $Unique_Maintenance_Patients = $Rep_Maintenance_Med_Patients{$RepKey} || 0;
      
      my $Synced_Script_Count = $Rep_Synced_Claim_Count{$RepKey} || 0;
      my $Maintenance_Script_Count = $Rep_Maintenance_Med_Claim_Count{$RepKey} || 0;
      
      ### Calculations ### ----------------------------------------------------
      my $Percent_Synced_Patients    = 0;
      my $Percent_Synced_Scripts     = 0;
      my $Average_Synced_Scripts_Per = 0;

      if ($Unique_Synced_Patients > 0) {
        $Percent_Synced_Patients = ($Unique_Synced_Patients / $Unique_Maintenance_Patients) * 100;
        $Percent_Synced_Scripts = ($Synced_Script_Count / $Maintenance_Script_Count) * 100;
        $Average_Synced_Scripts_Per = $Synced_Script_Count / $Unique_Synced_Patients;
      } else {
        $Percent_Synced_Patients = 'null';
        $Percent_Synced_Scripts = 'null';
        $Average_Synced_Scripts_Per = 'null';
      }
      
      ### End Calculations ### ------------------------------------------------
      
      #Load data to hashes with appropriate key for graph display
      $Data_Synced_Patient_Percent{$DataLoadKey} = $Percent_Synced_Patients;
      $Data_Synced_Script_Count{$DataLoadKey} = $Percent_Synced_Scripts;
      $Data_Synced_Script_Average{$DataLoadKey} = $Average_Synced_Scripts_Per;
    }
  }
  ### End Data Hashes ### ---------------------------------------------------------------

  ### Start New Graph ### ---------------------------------------------------------------
  #Set &build_mainchart parameters
  $decimalplaces = 1;
  $rotation      = 0;
  $container     = "Synced_Script_Percent";
  $type          = 'Med Sync Claims';
  $yaxistitle    = "% of Synced Claims";
  $class         = "mainchart";
  $marginright   = "110";
  $legend        = "true";
  $charttype     = "Linear";
  %data = %Data_Synced_Script_Count;
  &build_mainchart;
  print qq#<div id="$container" class="$class"></div>\n#;
  print qq#<div style="clear:both"></div>\n#;
  ### End Graph ### ---------------------------------------------------------------------
  
  ### Start New Graph ### ---------------------------------------------------------------
  #Set &build_mainchart parameters
  $decimalplaces = 1;
  $rotation      = 0;
  $container     = "Synced_Patient_Percent";
  $type          = 'Med Sync Patients';
  $yaxistitle    = "% of Synced Patients";
  $class         = "mainchart";
  $marginright   = "110";
  $legend        = "true";
  $charttype     = "Linear";
  %data = %Data_Synced_Patient_Percent;
  &build_mainchart;
  print qq#<div id="$container" class="$class"></div>\n#;
  print qq#<div style="clear:both"></div>\n#;
  ### End Graph ### ---------------------------------------------------------------------
  
  ### Start Main Graph ### ---------------------------------------------------------------
  #Set &build_mainchart parameters
  $decimalplaces = 1;
  $rotation      = 0;
  $container     = "Synced_Script_Average";
  $type          = "Average Claims Per Synced Patient";
  $yaxistitle    = "# of Claims";
  $class         = "mainchart";
  $marginright   = "110";
  $legend        = "true";
  %data = %Data_Synced_Script_Average;
  &build_mainchart;
  print qq#<div id="$container" class="$class"></div>\n#;
  print qq#<div style="clear:both"></div>\n#;
  ### End Graph ### ---------------------------------------------------------------------
  
  print qq#</div> <!-- end page -->\n#;

}
