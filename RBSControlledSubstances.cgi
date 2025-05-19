require "D:/RedeemRx/MyData/RBSDesktop_routines.pl";
require "D:/RedeemRx/cgi-bin/cgi-lib.pl";
require "D:/RedeemRx/MyData/RBSReporting_routines.pl";

use File::Basename;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use Env qw(PATH REMOTE_ADDR PERL5LIB PERLLIB);

$| = 1;
my $start = time();
my ($prog, $dir, $ext) = fileparse($0, '\..*');

my $help = qq|\n\nExecute as "$prog " without debug, or add " -d" for debug|;
my $doCS;
my $charttype;
my $inNCPDP;
my $Pharmacy_Name;
my $DBNAME = "RBSReporting";
my $TABLE  = "controlled_substances";

$ret = &ReadParse(*in);
&CgiDie("Error in reading and parsing of CGI input") if !defined $ret;

#______________________________________________________________________________

&readsetCookies;

&MyPharmassessReportingMonthlyHeader;

# Create the inputfile format name
my ($min, $hour, $day, $month, $year) = (localtime)[1,2,3,4,5];
$year  += 1900;	# reported as "years since 1900".
$month += 1;	# reported ast 0-11, 0==January
$tdate  = sprintf("%02d/%02d/%04d", $month, $day,$year);
$year2   = $year - 2 ."01";

if ( $USER ) {
   &MembersHeaderBlock;
} else {
   &MembersLogin;
   print qq#</BODY>\n#;
   print qq#</HTML>\n#;
   exit(0);
}

# connect to the RBS Reporting Database (with two tables, monthly & weekly)

%attr = ( PrintWarn=>1, RaiseError=>1, PrintError=>1, AutoCommit=>1, InactiveDestroy=>0, HandleError => \&handle_error );
$dbx = DBI->connect("DBI:mysql:$DBNAME:$DBHOST",$dbuser,$dbpwd, \%attr) || &handle_error;

print qq#<script src="js/highcharts.js"></script>\n#; #MOVE TO CANNED FILE

&getControlledSubstanceTotals;
&displayReportHeaderNEW;

if ( $doCS ) {
   &displayControlledSubstanceClaims_ALL;
   &displayControlledSubstanceDollars_ALL;
   &displayControlledSubstanceUnits_ALL;
   &displayControlledSubstanceClaims_CASH;
   &displayControlledSubstanceDollars_CASH;
   &displayControlledSubstanceUnits_CASH;
} else {
   print qq#<h3>No Controlled Substances data found for this pharmacy.</h3>\n#;
}
 
# Close the Database
$dbx->disconnect;

&MyPharmassessReportingTrailerPrint;

exit(0);

#______________________________________________________________________________

sub displayReportHeader {
  print qq#<div id="wrapper">\n#;
  print qq#<table class="header">\n#;
  print qq#<tr>\n#;
  print qq#<td class="logo"><img src="/images/pa_rbs_logo.png" style="width: 100%; max-width: 400px;"></td>\n#;
  print qq#<td>Controlled Substances Report</td>\n#;
  print qq#<td>$Pharmacy_Name</td>\n#;
  print qq#<td style="border-right: 0px">$tdate</td>\n#;
  print qq#</tr>\n#;
  print qq#</table>\n#;
  
  if ( $disclaimer ) {
     ####### ENTER DISCLAIMRS #####
     print qq#<div class="summary" style="text-align: center;">$disclaimer</div>\n#;
     ##############################
  }
  print qq#</div><!-- end wrapper -->\n#;
}

sub displayReportHeaderNEW {
  print "<h1 class='rbsreporting'>Controlled Substances Report for $Pharmacy_Name - $tdate</h1>\n";
  
  if ( $disclaimer ) {
     ####### ENTER DISCLAIMRS #####
     print qq#<div class="summary" style="text-align: center;">$disclaimer</div>\n#;
     ##############################
  }
}

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

  print qq#<div id="$container" style="width: 1125px;"></div>\n#;
}

sub displayControlledSubstanceClaims_CASH {
  $charttype  = "CASH Claims";
  $container     = "Controlled Substances3";
  &build_cs_chart($cash_cnt, $all_c2_cash_cnt, $c35_cash_cnt, $container);

  print qq#<div id="$container" style="width: 1125px;"></div>\n#;
}

sub displayControlledSubstanceDollars_ALL {
  $charttype  = "ALL Dollars";
  $container     = "Controlled Substances2";
  &build_cs_chart($all_cs_dollar, $all_c2_dollar, $all_c35_dollar, $container);

  print qq#<div id="$container" style="width: 1125px;"></div>\n#;
}

sub displayControlledSubstanceDollars_CASH {
  $charttype  = "CASH Dollars";
  $container     = "Controlled Substances4";
  &build_cs_chart($cash_cs_dollar, $c2_cash_dollar, $c35_cash_dollar, $container);

  print qq#<div id="$container" style="width: 1125px;"></div>\n#;
}

sub displayControlledSubstanceUnits_ALL {
  $charttype  = "ALL Units";
  $container     = "Controlled Substances5";
  &build_cs_chart($all_cs_unit, $all_c2_unit, $all_c35_unit, $container);

  print qq#<div id="$container" style="width: 1125px;"></div>\n#;
}

sub displayControlledSubstanceUnits_CASH {
  $charttype  = "CASH Units";
  $container     = "Controlled Substances6";
  &build_cs_chart($cash_cs_unit, $cash_c2_unit, $c35_cash_unit, $container);

  print qq#<div id="$container" style="width: 1125px;"></div>\n#;
}

sub getControlledSubstanceTotals {
  $doCS = 0;
  $DBNAME = 'Webinar' if($PH_ID < 11);
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
