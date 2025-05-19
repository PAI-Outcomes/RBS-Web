require "D:/RedeemRx/MyData/RBSDesktop_routines.pl";
require "D:/RedeemRx/MyData/Common_routines.pl";
require "D:/RedeemRx/MyData/RBSReporting_routines.pl";
require "D:/RedeemRx/cgi-bin/cgi-lib.pl";

use File::Basename;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use Env qw(PATH REMOTE_ADDR PERL5LIB PERLLIB);

use Excel::Writer::XLSX;  

$| = 1;
my $start = time();
my ($prog, $dir, $ext) = fileparse($0, '\..*');
$nbsp = "&nbsp\;";

$ret = &ReadParse(*in);
&CgiDie("Error in reading and parsing of CGI input") if !defined $ret;

#______________________________________________________________________________

$inNCPDP = $in{'ncpdp'};

&readsetCookies;

#______________________________________________________________________________

&MyPharmassessMembersHeader;

#$Pharmacy_ID = 146 if (!$Pharmacy_ID);

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
$lyear  = $syear-1;

$smonth = '08';
$sday   = '01';

print "\nProg: $prog &nbsp; &nbsp;<br>Date: $tdate &nbsp; Time: $ttime<P>\n" if ($debug);
#______________________________________________________________________________

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

$ntitle = "Inventory Management for $Pharmacy_Names{$Pharmacy_ID}";
print qq#<h1 class="rbsreporting">$ntitle</h1>\n#;

my $DBNAME = "officedb";

$dbhost = '10.255.65.50';
#$dbhost = '192.168.2.5';

$dbx = DBI->connect("DBI:mysql:$DBNAME:$dbhost",$dbuser,$dbpwd,
        { PrintError => 1, RaiseError => 1, InactiveDestroy => 0 } ) || die "$DBI::errstr";
   
DBI->trace(1) if ($dbitrace);

&displayInventory;

$dbx->disconnect;
 
#______________________________________________________________________________

&MyPharmassessMembersTrailer;

exit(0);

#______________________________________________________________________________

sub displayInventory {

  print "<p>Based on data from $smonth/$sday/$lyear to $smonth/$sday/$syear, showing top $show_lines NDC groups.</p>\n";


  print qq#<form id="selectForm" action="RBSReportingInventory_Basic.cgi" method="post">#;

  print qq#<p><label for="ncpdp">Pharmacy:</label>#;
#  print qq#<select name="ph_id onChange="document.selectForm.submit()">#;
  print qq#<select name="ncpdp" onChange="submit_form();">#;

  print qq#<option value="">Select...</option>\n#;

  my $TABLE  = "pharmacy";

#  my $sql = "SELECT Pharmacy_ID, NCPDP, Pharmacy_Name
#               FROM officedb.pharmacy 
#              WHERE 
#                 && NCPDP NOT IN (1111111,2222222,3333333,5555555)
#           ORDER BY Pharmacy_Name";

  my $sql = "SELECT *
             FROM ( SELECT a.NCPDP, b.Pharmacy_Name, count(*) AS cnt
                      FROM rbsreporting.basic_inventory a
                      JOIN officedb.ncpdp_list b ON (a.ncpdp = b.providerid)
                  GROUP BY a.NCPDP, b.Pharmacy_Name
                  ) x
            WHERE cnt >= 300
            ORDER BY Pharmacy_Name, NCPDP";

  my $sthx  = $dbx->prepare("$sql");
  $sthx->execute;

  while ( my ($NCPDP, $Pharmacy_Name) = $sthx->fetchrow_array() ) {
    if ( $NCPDP == $inNCPDP ) {
      $sel = 'SELECTED';
    }
    else {
      $sel = '';
    }
    print qq#<option value="$NCPDP" $sel>$NCPDP - $Pharmacy_Name</option>\n#;
  }

  $sthx->finish;

  print qq#</select>#;

  print qq#<script type="text/javascript" charset="utf-8">
          function submit_form() {
             \$("\#selectForm").submit();
          }

  </script>#;



  print qq#<link type="text/css" media="screen" rel="stylesheet" href="/includes/datatables/css/jquery.dataTables.css" /> \n#;
  print qq#<script type="text/javascript" charset="utf-8" src="/includes/datatables/js/jquery.dataTables.min.js"></script> \n#;
  print qq#<script type="text/javascript" charset="utf-8"> \n#;
  print qq#\$(document).ready(function() { \n#;
  print qq#  \$('\#tablef').dataTable( { \n#;
  print qq#    "aaSorting": [[ 4, "desc" ]], \n#;
  #print qq#    "sScrollX": "100%", \n#;
  print qq#    "bScrollCollapse": true,  \n#;
  print qq#    "sScrollY": "350px", \n#;
  print qq#    "bPaginate": false \n#;
  print qq#  } ); \n#;
  print qq#} ); \n#;
  print qq#</script> \n#;
  
  print qq#<br />#;
  print qq#<table id="tablef">\n#;
  print "
  <thead><tr>
  <th>NDC</th>
  <th>Rx Count</th>
  <th>B/G</th>
  <th>Drug Name</th>
  <!-- <th>Total Sale</th> -->
  <th>Total Cost</th>
  <th>Total Qty</th>
  <th>Pack. Size</th>
  <th>Daily Avg Qty</th>
  <th>Max Daily Qty</th>
  <th>MIN</th>
  <th>MAX</th>
  </tr></thead>
  \n";
  
  print "<tbody>\n";

  #Use the MSBorG Lookup Table
  $sql = "SELECT timeframe, ndc, rx_count, borg, drug_name, total_cost, total_qty, pack_size, daily_avg_qty, max_daily_qty, minimum, maximum
            FROM rbsreporting.basic_inventory
           WHERE NCPDP = '$inNCPDP'";

  my $sthx  = $dbx->prepare($sql);
  $sthx->execute;
  my $NumOfRows = $sthx->rows;

  if ( $NumOfRows > 0 ) {
    while ( my @row = $sthx->fetchrow_array() ) {
      my ($timeframe, $ndc, $rx_count, $borg, $drug_name, $total_cost, $total_qty, $pack_size, $daily_avg_qty, $max_daily_qty, $min, $max) = @row;
  
      print "
        <tr>
          <td>$ndc</td>
          <td class=\"align_right\">$rx_count</td>
          <td>$borg</td>
          <td>$drug_name</td>
          <!-- <td class=\"align_right\">$sumSALE</td> -->
          <td class=\"align_right\">$total_cost</td>
          <td class=\"align_right\">$total_qty</td>
          <td>$pack_size</td>
          <td class=\"align_right\">$daily_avg_qty</td>
          <td class=\"align_right\">$max_daily_qty</td>
          <td class=\"align_center\">$min</td>
          <td class=\"align_center\">$max</td>
        </tr>
      \n";
    }
  }

  $sthx->finish;

  print "</tbody>\n";
  print "</table>\n"; #End HTML Table
  
  print qq#<br style="clear: both;" /><br />\n#;
  print qq#<p><i>Please use your own judgement in addition to data provided in this report. Seasonal quantities may vary.</i></p>\n#;
  
  $tth = time - $starttime;
}

#____________________________________________________________________________
