require "D:/RedeemRx/MyData/RBSDesktop_routines.pl";
require "D:/RedeemRx/MyData/Common_routines.pl";
require "D:/RedeemRx/MyData/RBSReporting_routines.pl";
require "D:/RedeemRx/cgi-bin/cgi-lib.pl";

use File::Basename;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use Env qw(PATH REMOTE_ADDR PERL5LIB PERLLIB);

use Excel::Writer::XLSX;  

$| = 1; # don't buffer output
#______________________________________________________________________________
#
my $cnt = 0;
my $start = time();
my ($prog, $dir, $ext) = fileparse($0, '\..*');
my $help = qq|\n\nExecute as "$prog " without debug, or add " -d" for debug|;

$nbsp = "&nbsp\;";
my $start_month;
my $start_year;
my $start;
my $end;
my $end_month;
my $end_year;
my $lastday;

$ret = &ReadParse(*in);

&CgiDie("Error in reading and parsing of CGI input") if !defined $ret;

$PH_ID = 146;

#______________________________________________________________________________

&readsetCookies;

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
$ttime  = sprintf("%02d:%02d", $hour, $min);

($start_month, $start_year, $end_month, $end_year, $lastday) = &get_startend_month($month,$year,$sday);

$date_start = sprintf("%04d%02d%02d", $start_year, $start_month, 1);
$date_end   = sprintf("%04d%02d%02d", $end_year, $end_month, $lastday);
#______________________________________________________________________________

($isMember, $VALID) = &isMember($USER, $PASS);

print qq#USER: $USER, VALID: $VALID, isMember: $isMember\n# if ($debug);

#if ( $USER ) {
   &MembersHeaderBlock;
#} else {

#   &MembersLogin;
#   &MyPharmassessMembersTrailer;

#   print qq#</BODY>\n#;
#   print qq#</HTML>\n#;
#   exit(0);
#}

#______________________________________________________________________________

$progext = "${prog}${ext}";

$ntitle = "Landing Page for $Pharmacy_Names{$PH_ID}";

print qq#<h1 class="rbsreporting">$ntitle</h1>\n#;

print "<a href='https://members.pharmassess.com/members/RBSReportingReport_Basic.cgi'><img src='images/report-xxl.png' style='width: 80px; height: 80px;' border='0' alt='Pharm Assess RBS - Reports'  class='logographic'/><span style='display: inline; font-size: 32px; color: #000'>Monthly Reports</span></a><br>";
print "<a href='https://members.pharmassess.com/members/RBSReportingInventory_Basic.cgi'><img src='images/Inventory.png' style='width: 80px; height: 80px;' border='0' alt='Pharm Assess RBS - Inventory'  class='logographic'/><span style='display: inline; font-size: 32px; color: #000'>Inventory Management Report</span></a><br>";
print "<a href='https://members.pharmassess.com/members/RBSReportingMedSync_Basic.cgi'><img src='images/people2.png' style='width: 80px; height: 80px;' border='0' alt='Pharm Assess RBS - Medsync'  class='logographic'/><span style='display: inline; font-size: 32px; color: #000'>MedSync Patient Report</span></a>";

print qq#</div>#;

#______________________________________________________________________________

&MyPharmassessMembersTrailer;

exit(0);

#______________________________________________________________________________

sub get_startend_month {
  $month = shift;
  $year  = shift;
  $day   = shift;

  my $start_month;
  my $start_year = $year;
  my $end_month;
  my $end_year   = $year;
  my $lastday;

  $start_month = $month -4;
  $end_month   = $month -1;
#  if ($day < 15) {
#    $start_month--;
#    $end_month--;
#  }

  if ($start_month < 1) {
    $start_month = 12 if ($start_month ==  0); 
    $start_month = 11 if ($start_month == -1); 
    $start_month = 10 if ($start_month == -2); 
    $start_month = 9  if ($start_month == -3); 
    $start_month = 8  if ($start_month == -4); 
    $start_year--;
  }

  if ($end_month < 1) {
    $end_month = 12 if ($end_month == 0); 
    $end_month = 11 if ($end_month < 0); 
    $end_year--;
  }

  my $wrk_month = $end_month;
  my $wrk_year = $end_year;
  for ( $x = 1; $x <= 4; $x++ ) {
    if ( $wrk_month < 1 ) {
      $wrk_month = 12;
      $wrk_year--;
    }

    $column = $wrk_year . sprintf("%02d", $wrk_month);

    push(@display_month, $column);
    $wrk_month--;
  }

  $lastday = &LastDayOfMonth($end_year,$end_month);
  return ($start_month, $start_year, $end_month, $end_year, $lastday);

}

sub getData {
  my $db_rbsreporting = 'rbsreporting';
  my $tbl_medsync     = 'basic_medsync';
  my ($DateRangeStart, $DateRangeEnd) = @_;
  $db_rbsreporting = 'webinar' if($PH_ID < 12);

  print "sub getData: Entry.<br>\n" if ($debug);
  
  $starttime = time;
  $tth = time - $starttime;
  print "<p><hr />Time at entry of getData: $tth second(s)<hr /></p>\n" if ($showTTH);
  
  my $sql   = "";
  $start_month  = sprintf("%02d", $start_month);
  $end_month    = sprintf("%02d", $end_month);
  $lastday      = sprintf("%02d", $lastday);
  $start = "${start_year}${start_month}01";
  $end   = "$end_year$end_month$lastday";

  $sql  = "
    SELECT fname, lname, yob, synced, month1, month2, month3, month4, (month1+month2+month3+month4) AS Total
      FROM $db_rbsreporting.$tbl_medsync
     WHERE pharmacy_ID = $PH_ID
  ORDER BY Total DESC
  ";

  print "sql:<br>$sql<br>\n" if ($debug);
#  print "sql:<br>$sql<br>\n";

  $sthx  = $dbx->prepare("$sql");
  $sthx->execute;

  my $NumOfRows = $sthx->rows;
  print "Number of rows affected: $NumOfRows<br>\n" if ($debug);
  my $RepKeyLast = '';

  $grid = '[';

  while ( my @row = $sthx->fetchrow_array() ) {
    my ($fname, $lname, $yob, $synced, $month1, $month2, $month3, $month4, $total) = @row;
    if ( $NumOfRows > 0 ) {
      $grid .= "{
        'FName':'$fname',
        'LName':'$lname',
        'YOB':'$yob',
        'Synced':'$synced',
        'Cnt1':'$month1',
        'Cnt2':'$month2',
        'Cnt3':'$month3',
        'Cnt4':'$month4',
        'Total': '$total'
      },";
    }
  }

  $sthx->finish();

  $grid .= "]";

  print qq# <script>#;
  print qq^
\$(document).ready(function () {

// prepare the data

var month1 = $display_month[3];
var month2 = $display_month[2];
var month3 = $display_month[1];
var month4 = $display_month[0];

var source = {
    datatype: "json",
    datafields: [
        { name: 'FName', type:'string'},
        { name: 'LName', type:'string'},
        { name: 'YOB', type:'number'},
        { name: 'Synced', type:'string'},
        { name: 'Cnt1', type:'number'},
        { name: 'Cnt2', type:'number'},
        { name: 'Cnt3', type:'number'},
        { name: 'Cnt4', type:'number'},
        { name: 'Total', type:'number'}
    ],
    localdata: $grid,
    sortcolumn: 'Total',
    sortdirection: 'Desc',
};

var dataAdapter = new \$.jqx.dataAdapter(source);

         \$("#jqxgrid").jqxGrid(
            {
                width: 1000,
                height: 700,
                columnsheight: 40,
                source: dataAdapter,
                selectionmode: 'singlerow',
                editable:true,
    theme: 'classic',
    altrows: true,
    sortable: true,
    columns: [
        { text: 'First Name', datafield: 'FName', width: 100},
        { text: 'Last Name', datafield: 'LName', width: 100},
        { text: 'Year Of Birth', datafield: 'YOB', width: 100 },
        { text: 'Synced', datafield: 'Synced', width: 80 },
        { text: month1, datafield: 'Cnt1', width: 120},
        { text: month2, datafield: 'Cnt2', width: 120 },
        { text: month3, datafield: 'Cnt3', width: 120 },
        { text: month4, datafield: 'Cnt4', width: 120 },
        { text: 'Grand Total', datafield: 'Total', width: 120 }
    ]
            });

});

\$("#excelExport").jqxButton({
    theme: 'classic'
});

\$("#excelExport").click(function() {
    \$("#jqxgrid").jqxGrid('exportdata', 'xls', "$ntitle",true,null,null,'http://dev.pharmassess.com/js/jqwidgets/PHPExport/save-file.php'); 
});

  ^;
  print qq#</script>#;
}
