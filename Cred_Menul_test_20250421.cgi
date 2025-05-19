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
$fileyear  = $year-1;
$tmpmonth  = $month;
$tmpmonth  = 12 if ($tmpmonth == 0);
$tmpmonth2 = $tmpmonth -1;

$dispmonth  = $FMONTHS{$tmpmonth};
$dispmonth2 = $FMONTHS{$tmpmonth-1};
$month += 1;	# reported ast 0-11, 0==January
$syear  = sprintf("%4d", $year);
$smonth = sprintf("%02d", $month);
$sday   = sprintf("%02d", $day);
$tdate  = sprintf("%04d/%02d/%02d", $year, $month, $day);
$ttime  = sprintf("%02d:%02d", $hour, $min);
$areteBT = 0;
my $webpathAC;
&readPharmacies;

$NCPDP = $Pharmacy_NCPDPs{$PH_ID};
$EOYACFName = "ReconRx_End_of_Fiscal_Year_Accounts_Receivable_${NCPDP}_${PH_ID}_$fileyear.xlsx";
$ReimTrkng  = "ReimbursementTracking_${NCPDP}_${PH_ID}_$dispmonth.xlsx";
$ReimTrkng2 = "ReimbursementTracking_${NCPDP}_${PH_ID}_$dispmonth2.xlsx";
$EOYFName   = "ReconRx_End_of_Fiscal_Year_Reconciled_Claims_Summary_${NCPDP}_${PH_ID}_$fileyear.xlsx";

if ($PH_ID ne "Aggregated") {
	$webpathRec = "$outdir\\End_of_Fiscal_Year_Reconciled_Claims\\$EOYFName";
	$webpathAC  = "$outdir\\End_of_Fiscal_Year$testing\\$EOYACFName";
	$webpathRT  = "$outdir\\ReimbursementTracking\\$ReimTrkng";
	$webpathRT2 = "$outdir\\ReimbursementTracking\\$ReimTrkng2";
} 
#______________________________________________________________________________

$Pharmacy_Name = $Pharmacy_Names{$PH_ID};
$ntitle = " All Reports Menu";

print qq#<h3>$ntitle ( $LOGIN )</h3>\n#;

&displayAdminPage;

#______________________________________________________________________________

&MyPharmassessMembersTrailer;

exit(0);

#______________________________________________________________________________

sub displayAdminPage {
  print qq#<!-- displayAdminPage -->\n#;
  print "sub displayAdminPage: Entry.<br>\n" if ($debug);
  print qq# <link rel="stylesheet" type="text/css" href="/css/testing.css"/>#;

  my $Target = qq#target="_Blank"#;
  print qq#<table class='tblCredReports' cellpadding=3 cellspacing=3 >\n#;
    print qq#<tr><td>#;	
        print qq#<div class='ReportMenuDivs' >\n#;
        print qq# <div class='ReportDivHeader'>HIPPA</div>#;
        print qq# <ul class='ReportUL'>#;
        print qq# <li>test</li>#; 
        print qq# <li>test</li>#; 
        print qq# <li>test</li>#; 
        print qq# <li>test</li>#; 
        print qq# <li>test</li>#; 
        print qq# <li>test</li>#; 
        print qq# <li>test</li>#; 
        print qq# <li>test</li>#; 
        print qq# <li>test</li>#; 
        print qq# <li>test</li>#; 
        print qq# <li>test</li>#; 
        print qq# <li>test</li>#; 
        print qq# <li>test</li>#; 
        print qq#</ul></div>\n#;	  
      print qq#</td>#;
      print qq#<td>#;	
	print qq#<div class='ReportMenuDivs' >\n#;
        print qq# <div class='ReportDivHeader'>FWAC</div>#;
        print qq# <ul class='ReportUL'>#;
        print qq#</ul></div>\n#; 
    print qq#</td></tr>#;
    print qq#<tr><td>#;   		
      print qq#<div class='ReportMenuDivs' >\n#;
      print qq# <div class='ReportDivHeader'>FWAM</div>#;
      print qq# <ul class='ReportUL'>#;
      print qq#</ul></div>\n#;	  
    print qq#</td>#;	  
    print qq#<td>#;
      print qq#<div class='ReportMenuDivs' >\n#;
        print qq# <div class='ReportDivHeader'>Employee Handbook</div>#;
        print qq# <ul class='ReportUL'>#;
        print qq#</ul></div>\n#;
	print qq#</td></tr>#;
        print qq# <ul class='ReportUL'>#;
        print qq#</ul></div>\n#;
        print qq#</td></tr>#;

  print qq#</table>\n#;

  print "sub displayAdminPage: Exit.<br>\n" if ($debug);

}

#______________________________________________________________________________
