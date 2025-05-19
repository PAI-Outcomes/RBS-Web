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
my $do_graph;
my $charttype;
my $container;
my $inNCPDP;
my $Pharmacy_Name;
my $DBNAME = "RBSReporting";
my $TABLE  = "inventory_values";
my %all_turns;
my $max = 0;
my $turn_min = 0;
my $turn_max = 0;

$ret = &ReadParse(*in);
&CgiDie("Error in reading and parsing of CGI input") if !defined $ret;

#______________________________________________________________________________

&readsetCookies;
&readPharmacies;

$Pharmacy_Name = $Pharmacy_Names{$PH_ID};

&MyPharmassessReportingMonthlyHeader;

# Create the inputfile format name
my ($min, $hour, $day, $month, $year) = (localtime)[1,2,3,4,5];
$year  += 1900;	# reported as "years since 1900".
$month += 1;	# reported ast 0-11, 0==January
$tdate  = sprintf("%02d/%02d/%04d", $month, $day,$year);
$year2   = $year - 2 ."-03-01";

if ( $USER ) {
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

&getInventoryTotals;
&displayReportHeader;

if ( $do_graph ) {
   &displayInventoryTurns;
} else {
   print qq#<h3>No Inventory Turn data found for this pharmacy.</h3>\n#;
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
  print qq#<td>Inventory Turn Graph</td>\n#;
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

sub build_cs_chart {
  my $cnt = 0;
  foreach $num (sort { $order_dates{$b} cmp $order_dates{$a} } keys %order_dates) {
    $dte = $order_dates{$num};
    print $dte;
    $cnt++;
    $data  = "data${cnt}";
    $dates = "dte${cnt}";
    $$data = $all_turns{$dte};
    $newdate = $dte;
    $newdate =~ s/-01//g;
    $newdate =~ s/-/\//g;
    $$dates  = $newdate;
  }
 
  $rotation      = -30;
  $decimalplaces = 0;
  $yaxistitle    = "Inventory \$\$\$";

print <<BM;

<!-- Line Chart Generation -->

<script type="text/javascript">
\$(function () {
  var chart;
  \$(document).ready(function() {
    chart = new Highcharts.Chart({
      chart: {
        renderTo: '$container',
        type: '$charttype',
        marginBottom: 80 
      },
      credits: {
        enabled: false
      },
      title: {
        text: 'Inventory Turns',
        x: -20 //center
      },
      xAxis: {
        tickIntervals: 2,
        min: $turn_min, 
        max: $turn_max, 
        title: {
          text: 'Inventory Turns'
        },
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
        max:$max,
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
          var s = 'Inventory Turn: '+ this.x;

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
          animation: false,
          marker: { 
            enabled: false
          }
        }
      },
      series: [
        {
          name: 'Inventory as of $dte1 ',
          color: 'red',
          data: [$data1]
        }, 
        {
          name: 'Inventory as of $dte2 ',
          color: 'blue',
          data: [$data2]
        }, 
        {
          name: 'Inventory as of $dte3 ',
          color: 'yellow',
          data: [$data3]
        }, 
        {
          name: 'Inventory as of $dte4 ',
          color: 'black',
          data: [$data4]
        }
      ]
    });
  });
});
</script>

BM
print qq# <br><br><br> #;
}

sub displayInventoryTurns {
  $charttype = "spline";
  $container = "Inventory Turns";
  &build_cs_chart();

  print qq#<div id="$container" style="width: 1125px;"></div>\n#;
}

sub getInventoryTotals {
  $do_graph = 0;
  $DBNAME = 'rbsreporting';
  $TABLE  = 'inventory_values';
  my $sql = qq# 
    SELECT min(Inventory_Turns) - 10, max(Inventory_Turns) + 10
      FROM $DBNAME.`$TABLE`
     WHERE 1=1
        && Pharmacy_ID = $PH_ID
        && Date >= '$year2'
  #;
  $sthx  = $dbx->prepare("$sql");
  $sthx->execute;

  ($turn_min,$turn_max) = $sthx->fetchrow_array();
  $turn_min = 2 if($turn_min < 0);

  my $sql = qq# 
    SELECT Date, Inventory_Value, Inventory_Turns 
      FROM $DBNAME.`$TABLE`
     WHERE 1=1
        && Pharmacy_ID = $PH_ID
        && Date >= '$year2'
     ORDER BY Date
  #;

  $sthx  = $dbx->prepare("$sql");
  $sthx->execute;

  my $countfound = $sthx->rows;
  $skip = 1 if($countfount > 8);

  if ( $countfound > 0 ) {
    $do_graph = 1;
    $order = 1;
    while ( my @row = $sthx->fetchrow_array() ) {
      next if($skip);
      $skip;
      ($dte, $value, $turn) = @row;
      $COGS = $value * $turn;
      next if($dte !~ /-06-|-12-/);
      $order_dates{$order} = $dte;
      $order++;
      for (my $i=$turn_min; $i <= $turn_max; $i+=2) {
        $turns = $COGS/$i;
        $all_turns{$dte} .= "[$i,$turns],";
        if($turn > $i && $turn < $i + 2) {
          $all_turns{$dte} .= "{x:$turn, y:$value, marker: { enabled: true, radius: 15, symbol: 'diamond'},}," ;
        }
        $max = $turns if($max < $turns);
      }
    } 
  } 
  $sthx->finish;
}
