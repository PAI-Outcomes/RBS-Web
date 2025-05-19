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
my $Detail           = 'YRBS';   #Claim Detail Data - RBS Database
my $RebateBrand      = 0;	    #Rebate factored later.
my $RebateGeneric    = 0;	    #Rebate factored later
my  $NPIstring       = '';	    #No NPI string.
my  $ExcBINstring    = '';     #No BIN exclusion string.
my $start_month;
my $start_year;
my $start;
my $end;
my $end_month;
my $end_year;
my $lastday;
my @columns = qw(PrescriberNPI PrescriberName AverageRebatedGMperRx TotalRxCount TotalRebatedGM TotalSales);
my %detailstring;
my %test;

$ret = &ReadParse(*in);

&CgiDie("Error in reading and parsing of CGI input") if !defined $ret;

$PayerType   = "PAI_Payer_Name";

$SORT    = $in{'SORT'};

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

if ( $USER ) {
   &MembersHeaderBlock;
  print qq#
    <link rel="stylesheet" href="../js/jqwidgets/jqwidgets/styles/jqx.base.css" type="text/css" />
    <script type="text/javascript" src="../js/jqwidgets/scripts/jquery-1.11.1.min.js"></script>
    <script type="text/javascript" src="../js/jqwidgets/jqwidgets/jqxcore.js"></script>
    <script type="text/javascript" src="../js/jqwidgets/jqwidgets/jqxbuttons.js"></script>
    <script type="text/javascript" src="../js/jqwidgets/jqwidgets/jqxscrollbar.js"></script>
    <script type="text/javascript" src="../js/jqwidgets/jqwidgets/jqxmenu.js"></script>
    <script type="text/javascript" src="../js/jqwidgets/jqwidgets/jqxdata.js"></script>
    <script type="text/javascript" src="../js/jqwidgets/jqwidgets/jqxgrid.js"></script>
    <script type="text/javascript" src="../js/jqwidgets/jqwidgets/jqxgrid.selection.js"></script>
    <script type="text/javascript" src="../js/jqwidgets/jqwidgets/jqxgrid.sort.js"></script>
    <script type="text/javascript" src="../js/jqwidgets/jqwidgets/jqxdata.export.js"></script> 
    <script type="text/javascript" src="../js/jqwidgets/jqwidgets/jqxgrid.export.js"></script>
 
    <script type="text/javascript" src="../js/jqwidgets/jqwidgets/jqxdropdownlist.js"></script>
    <script type="text/javascript" src="../js/jqwidgets/jqwidgets/jqxgrid.edit.js"></script>
    <script type="text/javascript" src="../js/jqwidgets/jqwidgets/jqxdropdownbutton.js"></script>
    <script type="text/javascript" src="../js/jqwidgets/jqwidgets/jqxgrid.columnsresize.js"></script>
    <script type="text/javascript" src="../js/jqwidgets/jqwidgets/jqxlistbox.js"></script>
    <script type="text/javascript" src="../js/jqwidgets/jqwidgets/jqxgrid.pager.js"></script>
   
  #;
} else {

   &MembersLogin;
   &MyPharmassessMembersTrailer;

   print qq#</BODY>\n#;
   print qq#</HTML>\n#;
   exit(0);
}

#______________________________________________________________________________

&readLogins;

$progext = "${prog}${ext}";

$ntitle = "Med Sync Patient Report for $Pharmacy_Names{$PH_ID}";
print qq#<h1 class="rbsreporting">$ntitle</h1>\n#;
print qq#<div id="jqxWidget">#;
print qq#<div id="jqxgrid"></div>#;
print qq#</div>#;
print qq#<input style='margin-top: 10px;' type="button" value="Export to Excel" id='excelExport' /> #;
             
$dbx = DBI->connect("DBI:mysql:$DBNAME:$DBHOST",$dbuser,$dbpwd,
        { PrintError => 1, RaiseError => 1, InactiveDestroy => 0 } ) || die "$DBI::errstr";
   
DBI->trace(1) if ($dbitrace);

#Additional Includes

print qq#
<form name="sbtc" action="$progext" method="post">

</form>

<hr />
#;

&getData($date_start, $date_end);

$dbx->disconnect;
 
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
  if ($day < 15) {
    $start_month--;
    $end_month--;
  }

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

  $lastday = &LastDayOfMonth($end_year,$end_month);
  return ($start_month, $start_year, $end_month, $end_year, $lastday);
}

sub getData {
  my $db_rbsreporting = 'rbsreporting';
  my $tbl_incoming    = 'incomingtb_rbsdata';
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
    SELECT dbPatientFirstName, dbPatientLastName,YearofBirth, monthofservice, dbSyncPatient, dbNDC, count(*) from (
      SELECT dbpatientfirstname, dbpatientlastname, SUBSTR(dbdateofbirth,1,4) as YearOfBirth, dbrxnumber, dbSyncPatient, dbNDC, SUBSTR(dbdateofservice,1,6) AS monthofservice
        FROM $db_rbsreporting.incomingtb_rbsdata a
        JOIN officedb.`msborg_lookup_table_new` b ON a.dbNDC = b.NDC
#        JOIN medispan.mf2ndc b ON a.dbNDC = b.ndc_upc_hri
#        JOIN medispan.mf2name c ON b.drug_descriptor_id = c.drug_descriptor_id
       WHERE (1=1)
#          && dbDateofService >= '20201101'
#         && dbDateofService <= '20210229'
          && dbDateofService >= '$start'  
          && dbDateofService <= '$end' 
          && Pharmacy_ID in ($PH_ID) 
          && maintenance_drug_code = 2
          && dbTcode = '' 
    ##      && (dbSyncPatient IS NULL or dbSyncPatient = '')
       GROUP BY dbrxnumber,monthofservice
    ) a
    GROUP BY dbPatientFirstName,dbPatientLastName, YearofBirth, monthofservice, dbSyncPatient, dbNDC
    #HAVING COUNT(*) > 1
    ORDER BY dbPatientFirstName, dbPatientLastName, YearofBirth, monthofService, dbNDC
  ";

  print "sql:<br>$sql<br>\n" if ($debug);
#  print "sql:<br>$sql<br>\n";

  $sthx  = $dbx->prepare("$sql");
  $sthx->execute;

  my $NumOfRows = $sthx->rows;
  print "Number of rows affected: $NumOfRows<br>\n" if ($debug);
  my $RepKeyLast = '';

  while ( my @row = $sthx->fetchrow_array() ) {
     $cnt++;
     my ($fname,$lname,$yob,$mos, $synced, $ndc, $count) = @row;
     $fname =~ s/'/\\'/g;
     $lname =~ s/'/\\'/g;
     $RepKey = "$fname##$lname##$yob";

     if ( $RepKey ne $RepKeyLast ) {
       $ndcs{$RepKeyLast} = $ndc_counter;
       %ndc_hash = ();
       $ndc_counter = 0;
     }

     if (! $ndc_hash{$ndc} ) {
       $ndc_counter++;
     }

     $ndc_hash{$ndc} += 1;
     $record{$RepKey} += 1;
#     push @{ $record{"$RepKey"} }, $count;
     $synced{$RepKey}++ if ( $synced =~ /Y/i );
#     $counts{$RepKey}++;
     $counts{$RepKey}{$mos} += $count;
     $Tcount{$RepKey}+= $count;
     $month{$mos} = 1;
     $RepKeyLast = $RepKey;
  }
  if ( $NumOfRows > 0 ) {
    #Build string of unique NDCs and get data from MediSpan
    &buildJQW();
  }
  print "sub getData: Exit.<br>\n" if ($debug);
}

sub buildJQW {
my @array = (sort keys %month );
my $cnt = 0;
my @vals;

  $grid = '[';
  foreach $key (sort keys %record) {
    ($fname,$lname,$yob) = split('##',$key);
    $cfname = substr($fname,0,1);
    $cfname .= '.';
    $clname = substr($lname,0,3);
    $clname .= '.';
    @vals = ();
    foreach my $mos (@array) {
      my $val = 0;
      if ( $counts{$key}{$mos} ) {
        $val = $counts{$key}{$mos};
      }
      push(@vals, $val);
    }

#    @vals =  @{$record{$key}};
#    next if ( scalar @vals != 4);
    next if ( $ndcs{$key} < 3 );

    if ( $synced{$key} ) {
      $synced_patient = 'Yes';
    }
    else {
      $synced_patient = '';
    }

    $grid .= "{
      'FName':'$cfname',
      'LName':'$clname',
      'YOB':'$yob',
      'Synced':'$synced_patient',
      'Cnt1':'$vals[0]',
      'Cnt2':'$vals[1]',
      'Cnt3':'$vals[2]',
      'Cnt4':'$vals[3]',
      'Total': '$Tcount{$key}'
    },";
    $cnt++;
  }

  $grid .= "]";
#  print "<h2>$cnt</h2>";
  print qq# <script>#;
  print qq^
\$(document).ready(function () {

// prepare the data

var month1 = $array[0];
var month2 = $array[1];
var month3 = $array[2];
var month4 = $array[3];

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
    \$("#jqxgrid").jqxGrid('exportdata', 'csv', "$ntitle",true,null,null,'/js/jqwidgets/PHPExport/save-file.php'); 

});

  ^;
  print qq#</script>#;
}

