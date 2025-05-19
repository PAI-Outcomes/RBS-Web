require "D:/RedeemRx/MyData/RBSDesktop_routines.pl";
require "D:/RedeemRx/MyData/Common_routines.pl";
require "D:/RedeemRx/MyData/RBSReporting_routines.pl";
require "D:/RedeemRx/cgi-bin/cgi-lib.pl";

use File::Basename;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use Env qw(PATH REMOTE_ADDR PERL5LIB PERLLIB);
use POSIX 'ceil';

$| = 1; # don't buffer output
#______________________________________________________________________________
#
my $cnt = 0;
my $start = time();
my ($prog, $dir, $ext) = fileparse($0, '\..*');

my $start;
my $end;
my $end_month;
my $end_year;
my $dir_fee;
my $profit_share;

$ret = &ReadParse(*in);

&CgiDie("Error in reading and parsing of CGI input") if !defined $ret;

$PayerType   = "PAI_Payer_Name";

$SORT    = $in{'SORT'};
$dir_fee = $in{'DIRFEE'};
$profit_share = $in{'Bonus'};

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

$dbx = DBI->connect("DBI:mysql:$DBNAME:$DBHOST",$dbuser,$dbpwd,
        { PrintError => 1, RaiseError => 1, InactiveDestroy => 0 } ) || die "$DBI::errstr";
   
DBI->trace(1) if ($dbitrace);

&get_startend_month();

($isMember, $VALID) = &isMember($USER, $PASS);

print qq#USER: $USER, VALID: $VALID, isMember: $isMember\n# if ($debug);

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

&readLogins;
&readPharmacies;
$NCPDP = $Pharmacy_NCPDPs{$PH_ID};
&loadRebateLookup($NCPDP);


$progext = "${prog}${ext}";

$ntitle = "Med Sync Patient Incentive Graph for $Pharmacy_Names{$PH_ID}";
print qq#<h1 class="rbsreporting">$ntitle</h1>\n#;
print qq#<script src="js/highcharts8.2.js"> </script>#;
print qq#<link type="text/css" rel="stylesheet" href="../css/highcharts.css"/>#;

             
#Additional Includes

print qq#
<form name="sbtc" action="$progext" method="post">

<div id="submitdiv">
  <table >
    <tr><td class="tdNoBorder">DIR Fee/Script Estimate (\$)</td><td class="tdNoBorder"><input type="text" name="DIRFEE" id="NDC"  value="$dir_fee" style="width: 120px" onchange='';></td></tr> 
    <tr><td class="tdNoBorder">Increased Profit Share (Employee Bonus %)<td class="tdNoBorder"><input type="text" id="Bonus" name="Bonus" value="$profit_share" style="width: 120px";></td></tr>
    <tr><td class="tdNoBorder"></td><td class="tdNoBorder"><input type="Submit" NAME="Generate" VALUE="Generate" class="";></td></tr>
    <tr><td class="tdNoBorder">Based on claim data from $styr-$stmo to $endyr-$endmo</td></tr> 
  </table>
</div>

<figure class="highcharts-figure">
    <div id="container"></div>
</figure>
<div style="text-align:center">    
  <a style="font-size:15px;" href="https://members.pharmassess.com/members/RBSReportingMedSync.cgi">Take me to the Med Sync Patient Report</a>
</div>
</form>
<hr />
#;
print qq#</div>#;

&getData;
&build_chart;

$dbx->disconnect;
 
&MyPharmassessMembersTrailer;

exit(0);

sub get_startend_month {

  my $start_month;
  my $start_year = $year;
  my $end_month;
  my $end_year   = $year;
  my $lastday;
  

  my $sql = " 
              SELECT max(date) from rbsreporting.monthly
              WHERE pharmacy_id = $PH_ID 
                AND display = 'Y'
            ";
  $sthx  = $dbx->prepare("$sql");
  $sthx->execute;
  my($maxdate)  = $sthx->fetchrow_array();
  ($YYYY,$MM,$DD) = split('-',$maxdate); 
  $endyr  =  $YYYY;
  $styr   =  $YYYY - 1;

  if ($MM <= 3) {
    $endyr -=  1;
    $endmo = 12;
    $stmo  = '01';
  }
  else {
    $endmo = '03' if($MM > 3 && $MM <= 6);
    $endmo = '06' if($MM > 6 && $MM <= 9);
    $endmo = '09' if($MM > 9 && $MM <= 12);
    $stmo  = '04' if($MM > 3 && $MM <= 6);
    $stmo  = '07' if($MM > 6 && $MM <= 9);
    $stmo  = '10' if($MM > 9 && $MM <= 12);
  }

  $start = "$styr-$stmo-01";
  $end   = "$endyr-$endmo-01";
  $st    = "$styr$stmo";
  $endd  = "$endyr$endmo";
}

sub getData {

  my $db_rbsreporting = 'rbsreporting';
  my $tbl_monthly    = 'monthly';
  my $tbl_rebates    = 'rebates';
  my ($DateRangeStart, $DateRangeEnd) = @_;
  $db_rbsreporting = 'webinar' if($PH_ID < 12);

  print "sub getData: Entry.<br>\n" if ($debug);
  
  $starttime = time;
  $tth = time - $starttime;
  print "<p><hr />Time at entry of getData: $tth second(s)<hr /></p>\n" if ($showTTH);
  
  my $sql   = "";

  $sql  = "
    SELECT  YYYYMM, Brand_Rebate, Generic_Rebate,Rebate_Type
            From $db_rbsreporting.$tbl_rebates
       WHERE Pharmacy_ID in ($PH_ID) 
          && YYYYMM >= '$st'  
          && YYYYMM <= '$endd' 
  ";

  print "sql:<br>$sql<br>\n" if ($debug);

  $sthx  = $dbx->prepare("$sql");
  $sthx->execute;

  my $NumOfMonths = $sthx->rows;
  print "Number of rows affected: $NumOfMonths<br>\n" if ($debug);

  while ( my($YYYYMM, $B_Rebate, $G_Rebate,$type)  = $sthx->fetchrow_array() ) {
     $Rebate{B}{$YYYYMM} = $B_Rebate;
     $Rebate{G}{$YYYYMM} = $G_Rebate;
     $Rebatetype{$YYYYMM} = $type;
  }

  $sql  = "
    SELECT  Date, Total_Brand, Total_Generic, Total_Brand_Revenue, Total_Generic_Revenue, Total_Brand_Cost, Total_Generic_Cost, Unique_Patients
      From $db_rbsreporting.$tbl_monthly
     WHERE Pharmacy_ID in ($PH_ID) 
          && Date >= '$start'  
          && Date <= '$end' 
  ";

  print "sql:<br>$sql<br>\n" if ($debug);

  $sthx  = $dbx->prepare("$sql");
  $sthx->execute;

  my $NumOfRows = $sthx->rows;
  print "Number of rows affected: $NumOfRows<br>\n" if ($debug);

  while ( my @row = $sthx->fetchrow_array() ) {
     $cnt++;
     my ($Date, $Total_Brand, $Total_Generic, $Total_Brand_Revenue, $Total_Generic_Revenue, $Total_Brand_Cost, $Total_Generic_Cost, $Unique_Patients) = @row;
     $rdate = $Date;
     $rdate =~ s/-//g; 
     $rdate =~ s/01$//g;
     if ($Rebatetype{$rdate} ne 'D') {
       $GM_val = $Total_Brand_Revenue + $Total_Generic_Revenue - $Total_Brand_Cost * (1-$Rebate{B}{$rdate}) - $Total_Generic_Cost * (1-$Rebate{G}{$rdate}) ;
     }
     else {
       ##$GM_val = $Total_Brand_Revenue + $Total_Generic_Revenue - $Total_Brand_Cost * ($Rebate{B}{$rdate}/$Total_Brand_Cost)  - $Total_Generic_Cost * ($Rebate{G}{$rdate}/$Total_Generic_Cost) ;
       $GM_val = $Total_Brand_Revenue + $Total_Generic_Revenue - $Total_Brand_Cost * (1-$rebateBrandDB{$rdate}) - $Total_Generic_Cost * (1-$rebateGenericDB{$rdate}) ;
     }

     $GM{$rdate} = $GM_val;
     $T_GM += $GM_val; 
     $Avg_PPM += $Unique_Patients;
     $Avg_CPM += $Total_Brand + $Total_Generic;
  }

  $Avg_CPM = $Avg_CPM/$NumOfMonths;
  $Avg_PPM = $Avg_PPM/$NumOfMonths;
  $Avg_GM  = $T_GM/$NumOfMonths; 
  $Avg_GMScript = $Avg_GM/$Avg_CPM; 
  $Avg_SPP = $Avg_CPM/$Avg_PPM; 

  $pspy = $Avg_SPP*$Avg_PPM*12;
  $GMB = $pspy * $Avg_GMScript;
  $ldir = $pspy * $dir_fee;
  $Base_GMBP = $GMB - $ldir; 

  $rounded = ceil($Avg_SPP*10)/10;
  $ps = $profit_share;
  $ps = $profit_share/100 if($profit_share && $profit_share >= 1);

  for (my $i = 0; $i<11; $i++) {
    $pspy = 0;
    $GMB = 0;
    $GMBP = 0;
    $ldir=0;
    $IGMBP = 0;
    $IIPS  = 0;
    $GMAPS = 0;
    push(@Avg_SPP,$rounded);
    $pspy = $rounded*$Avg_PPM*12;
    $GMB = $pspy * $Avg_GMScript;
    $ldir =$pspy * $dir_fee;
    $GMBP = $GMB - $ldir; 
    $IGMBP =  $GMBP - $Base_GMBP;
    $IIPS  = $IGMBP * $ps;
    $GMAPS = $IGMBP - $IIPS;
    $IIPS = sprintf("%.0f",$IIPS);
    push(@IIPS,$IIPS);
    $GMAPS = sprintf("%.0f",$GMAPS);
    push(@GMAPS,$GMAPS);
    $rounded+=.1;
  }
  $str_avgspp = join(',',@Avg_SPP);
  $str_IIPS = join(',',@IIPS);
  $str_GMAPS = join(',',@GMAPS);

  if ( $NumOfRows > 0 ) {
    #Build string of unique NDCs and get data from MediSpan
  }
  print "sub getData: Exit.<br>\n" if ($debug);
}

sub build_chart {

print <<BM;

<script type="text/javascript">
\$(function () {
  var chart;
  \$(document).ready(function() {
    Highcharts.setOptions({
    lang: {
      thousandsSep: ','
    }
  });
    chart = new Highcharts.Chart({
      chart: {
        renderTo: 'container',
        type: 'area',
      },
      title: {
        text: 'Med Sync Incentive'
      },
      subtitle: {
      },
      xAxis: {
        categories: [$str_avgspp],
        tickmarkPlacement: 'on',
        title: {
            text: 'Avg Scripts Per Patient'
        }
      },
      yAxis: {
        title: {
            text: 'Increase in GM per Year \$'
        },
        labels: {
          formatter: function () {
            return this.value / 1000 + 'k';
          }
        }
      },
      tooltip: {
        split: true
      
      },
      plotOptions: {
        series: {
          dataLabels: {
                enabled: true
          }
        },
        area: {
            stacking: 'normal',
            lineColor: '#666666',
            lineWidth: 1,
            marker: {
              lineWidth: 1,
              lineColor: '#666666'
            }
        }
      },
       series: [{
          dataLabels: {
            y:80,
          },
           name: 'Increase GM after Profit Share',
           data: [$str_GMAPS] ,color: '#74C666',
       }, {
          dataLabels: {
                y:20
          },
           name: 'Increase Profit Share',
           data: [$str_IIPS], color :'#22A5DA'
       }]
  });  
  });  
});
</script>

BM
print qq# <br><br><br> #;
}



