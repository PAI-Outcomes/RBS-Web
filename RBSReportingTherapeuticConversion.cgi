require "D:/RedeemRx/MyData/RBSDesktop_routines.pl";
require "D:/RedeemRx/MyData/Common_routines.pl";
require "D:/RedeemRx/MyData/RBSReporting_routines.pl";
require "D:/RedeemRx/cgi-bin/cgi-lib.pl";

use File::Basename;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use Env qw(PATH REMOTE_ADDR PERL5LIB PERLLIB);

$| = 1;
my $start = time();
my ($prog, $dir, $ext) = fileparse($0, '\..*');
$nbsp = "&nbsp\;";
my $Detail           = 'YRBS';   #Claim Detail Data - RBS Database
my $RebateBrand      = 0;	    #Rebate factored later.
my $RebateGeneric    = 0;	    #Rebate factored later
my $NPIstring        = '';	    #No NPI string.
my $ExcBINstring     = '';     #No BIN exclusion string.
my $start_month;
my $start_year;
my $end_month;
my $end_year;
my $lastday;
my @columns = qw(PrescriberNPI PrescriberName AverageRebatedGMperRx TotalRxCount TotalRebatedGM TotalSales);
my %TC;
my %GPI;
my %Minor_SC;

$ret = &ReadParse(*in);
&CgiDie("Error in reading and parsing of CGI input") if !defined $ret;


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

($start_month, $start_year, $end_month, $end_year, $lastday) = &get_startend_month($month,$year);

$date_start = sprintf("%04d%02d%02d", $start_year, $start_month, 1);
$date_end   = sprintf("%04d%02d%02d", $end_year, $end_month, $lastday);

#______________________________________________________________________________

if ( $USER ) {
   &MembersHeaderBlock;
  print qq#
    <link rel="stylesheet" type="text/css" href="/css/profitable_physician.css"  />
    <link rel="stylesheet" href="/js/jqwidgets/jqwidgets/styles/jqx.base.css" type="text/css" />
    <script type="text/javascript" src="/js/jqwidgets/scripts/jquery-1.11.1.min.js"></script>
    <script type="text/javascript" src="/js/jqwidgets/jqwidgets/jqxcore.js"></script>
    <script type="text/javascript" src="/js/jqwidgets/jqwidgets/jqxbuttons.js"></script>
    <script type="text/javascript" src="/js/jqwidgets/jqwidgets/jqxscrollbar.js"></script>
    <script type="text/javascript" src="/js/jqwidgets/jqwidgets/jqxmenu.js"></script>
    <script type="text/javascript" src="/js/jqwidgets/jqwidgets/jqxdata.js"></script>
    <script type="text/javascript" src="/js/jqwidgets/jqwidgets/jqxgrid.js"></script>
    <script type="text/javascript" src="/js/jqwidgets/jqwidgets/jqxgrid.selection.js"></script>
    <script type="text/javascript" src="/js/jqwidgets/jqwidgets/jqxgrid.sort.js"></script>
    <script type="text/javascript" src="/js/jqwidgets/jqwidgets/jqxdata.export.js"></script> 
    <script type="text/javascript" src="/js/jqwidgets/jqwidgets/jqxgrid.export.js"></script> 
  #;
} else {
   &MembersLogin;
   &MyPharmassessMembersTrailer;

   print qq#</BODY>\n#;
   print qq#</HTML>\n#;
   exit(0);
}

#______________________________________________________________________________

$progext = "${prog}${ext}";

$ntitle = "Therapeutic Conversion Opportunities Report for $Pharmacy_Names{$PH_ID}";
print qq#<h1 class="rbsreporting">$ntitle</h1>\n#;
print qq#<div><table>#;
print qq#<tr>#;
print qq#<td class="noborder">#;
print qq#</td>#;
print qq#<td class="noborder">#;
print qq#</td>#;
print qq#</tr>#;
print qq#</table></div>#;
print qq#<div id="example" class='container'></div>#;
print qq#<div id="jqxgrid"></div>#;
print qq#<input style='margin-top: 10px;' type="button" value="Export to CSV" id='excelExport' /> #;
print qq#<input style='margin-top: 10px;' type="button" value="Export Detail to CSV" id='excelDetailExport' /> #;
             
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

  my $start_month;
  my $start_year = $year;
  my $end_month;
  my $end_year   = $year;
  my $lastday;

  $start_month = $month -4;
  $end_month   = $month -2;

  if ($start_month < 1) {
    $start_month = 12 if ($start_month ==  0); 
    $start_month = 11 if ($start_month == -1); 
    $start_month = 10 if ($start_month == -2); 
    $start_month = 9  if ($start_month == -3); 
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
  my ($DateRangeStart, $DateRangeEnd) = @_;

  $starttime = time;
  $tth = time - $starttime;
  print "<p><hr />Time at entry of getData: $tth second(s)<hr /></p>\n" if ($showTTH);
  
  $PharmacyWanted   = $Pharmacy_NCPDPs{$PH_ID};
  ($Minor_SCref, $GPIref, $DrugNamesref) = &Get_DrugNames;
  %DrugNames = %$DrugNamesref;
  %GPI       = %$GPIref;
  %Minor_SC  = %$Minor_SCref;
  
  #Get RBS Reporting data via subroutine
  ( $RxNumbersref, $FillNumbersref, $BGsref, $SALEsref, $COSTsref, $BinNumbersref,
    $DBsref, $CASHorTPPsref, $GMsref, $salecalcsref, $costcalcsref, $DOSsref, $DateTransmittedsref,
    $PCNsref, $Groupsref, $NDCsref, $TCodesref, $Quantitysref, $DaySupplyref, 
    $RCOSTsref, $RGMsref, $PBMsref, $PAI_Payer_Namesref, $Comm_MedD_Medicaidref, 
    $PrescriberIDsref, $CashFlagref, $PrescriberLastNameref ) =
    &Get_RBSReporting_Data($PharmacyWanted, $DateRangeStart, $DateRangeEnd, $Detail, 
    $RebateBrand, $RebateGeneric, "$NPIstring", "$ExcBINstring" );
  
  @NDCs = ();
  
  $totalSales = 0;
  
  my $rows = 0;
  &create_NDC;
  
  foreach $key (sort keys %$RxNumbersref) {
    $RxNumber   =         $RxNumbersref->{$key};
    $FillNumber         = $FillNumbersref->{$key};
    $BG                 = $BGsref->{$key};
    $SALE               = $SALEsref->{$key};
    $COST               = $COSTsref->{$key};
    $BinNumber          = $BinNumbersref->{$key};
    $DB                 = $DBsref->{$key};
    $CASHorTPP          = $CASHorTPPsref->{$key};
    $GM                 = $GMsref->{$key};
    $salecalc           = $salecalcsref->{$key};
    $costcalc           = $costcalcsref->{$key};
    $DOS                = $DOSsref->{$key};
    $DateTransmitted    = $DateTransmittedsref->{$key};
    $PCN                = $PCNsref->{$key};
    $Group              = $Groupsref->{$key};
    $NDC                = $NDCsref->{$key};
    $TCode              = $TCodesref->{$key};
    $Quantity           = $Quantitysref->{$key};
    $DaySupply          = $DaySupplyref->{$key};
    $RCOST              = $RCOSTsref->{$key}; 
    $RGM                = $RGMsref->{$key};
    $PBM                = $PBMsref->{$key};
    $PAI_Payer_Name     = $PAI_Payer_Namesref->{$key};
    $Comm_MedD_Medicaid = $Comm_MedD_Medicaidref->{$key};
    $PrescriberID       = $PrescriberIDsref->{$key};

    if ($TC{$NDC}) {
#      print "$RxNumber - $DOS - $NDC<br>";
      $TotalSales{$NDC}  += $SALE;
      $TotalRGM{$NDC}    += $RGM;
      $TotalDS{$NDC}     += $DaySupply;
      $TotalClaims{$NDC}++;
      $AverageRGM{$NDC}   = $TotalRGM{$NDC}/$TotalClaims{$NDC};
      $AverageRGMDS{$NDC} = $TotalRGM{$NDC}/$TotalDS{$NDC};
      $LastName{$NDC}     = $PrescriberLastNameref->{$key};
      $LastName{$NDC}     =~ s/\'/\\'/g;
      $DrugName           = $DrugNames{$NDC};
      $RCOST              = sprintf("%.2f", $RCOST);
      $RGM                = sprintf("%.2f", $RGM);
      $Quantity           = sprintf("%.0f", $Quantity);

      $detailJsonData{$NDC} .= 
        "{
          'RxNumber'         :'$RxNumber',
          'DateFilled'       :'$DOS',
          'SalePrice'        :'$SALE',
          'RebatedCost'      :'$RCOST',
          'RebatedGM'        :'$RGM',
          'Quantity'         :'$Quantity',
          'DaySupply'        :'$DaySupply',
          'ThirdPartyPayer'  :'$PAI_Payer_Name',
          'PrescriberNPI'    :'$PrescriberID',
          'PrescriberName'   :'$LastName{$NDC}',
          'DrugName/Strength':'$DrugName',
          'NDC'              :'$NDC'
        },";
		
      $totalSales += $SALE;
		
      $rows++;
    }
  
  }
  
  $tth = time - $starttime;
  print "<p><hr />Time after RBS data pull foreach: $tth second(s)<hr /></p>\n" if ($showTTH);
  
  if ( $rows > 0 && $PH_ID > 0 ) {
    #Build string of unique NDCs and get data from MediSpan
    &buildJQW;
  }
  else{
   print "No Rows Available\n";
  }
}
#____________________________________________________________________________

sub create_NDC {
 $ndc = sprintf( "%011d", $in{NDC}); 
 $gpi = substr($GPI{$ndc},0,6);
 %TC = ();

 foreach $key (sort keys %GPI) {
   if($Minor_SC{$key} == $gpi) {
     $TC{$key} = 1; 
   }
 }
}

sub buildJQW {
  $grid = '[';
  $cnt = 0;
  foreach my $NDC (sort { $AverageRGM{$b} <=> $AverageRGM{$a} or $a cmp $b } keys %AverageRGM) {
    $id++;
    $averageRGM   = sprintf("%.2f", $AverageRGM{$NDC});
    $averageRGMDS = sprintf("%.2f", $AverageRGMDS{$NDC});
    $totalRGM = sprintf("%.2f", $TotalRGM{$NDC});
       $grid .= "{
      'id':$id,
      'DName':'$DrugNames{$NDC}',
      'ARGM':'$averageRGM',
      'TRX':'$TotalClaims{$NDC}',
      'RGM':'$totalRGM',
      'ARGMDS': '$averageRGMDS',
      //'TS':'$TotalSales{$NDC}',
      'children': [$detailJsonData{$NDC}]
    },"
  }

  $grid .= "]";

  print qq# <script>#;
  print qq^
  \$(document).ready(function () {

  // prepare the data

  var data = new Array();
  var nestedRows;

  var source = {
      datatype: "json",
      localdata: $grid,
      datafields: [
        { name: 'DName', type:'string'},
        { name: 'ARGM', type:'number'},
        { name: 'TRX', type:'number'},
        { name: 'RGM', type:'number'},
        { name: 'ARGMDS', type:'number'},
      //  { name: 'TS', type:'number'},
        { name: "children", type: "array" },
      ],
      hierarchy:
        {
            root: 'children'
        },
    id: 'id',
  };

  var dataAdapter = new \$.jqx.dataAdapter(source);
                    console.log(dataAdapter);

         \$("#jqxgrid").jqxGrid(
            {
              width: 1180,
              height: 700,
              columnsheight: 40,
              source: dataAdapter,
              theme: 'classic',
              altrows: true,
              sortable: true,
              rowdetails: true,
              rowdetailstemplate: { rowdetails: "<div id='jqxgrid' style='margin: 10px;'></div>", rowdetailsheight: 400, rowdetailshidden: true },
              initrowdetails: function (index, parentElement, gridElement, record)
            {
            var container = \$('#jqxgrid' + index);

            if (record.records.length != 0) {
              var secondSource = {
                  dataType: "json",
                  dataFields: [
                      { name: "RxNumber", type: "number" },
                      { name: "DateFilled", type: "string" },
                      { name: "SalePrice", type: "number" },
                      { name: "RebatedCost", type: "string" },
                      { name: "RebatedGM", type: "string" },
                      { name: "Quantity", type: "number" },
                      { name: "DaySupply", type: "number" },
                      { name: "ThirdPartyPayer", type: "string" },
                      { name: "PrescriberNPI", type: "number" },
                      { name: "PrescriberName", type: "string" },
                      { name: "DrugName/Strength", type: "string"},
                      { name: "NDC", type: "string"}
                  ],
                  id: "ID",
                  localdata: record.records
                };
                var secondLevel = new \$.jqx.dataAdapter(secondSource);

                if (container != null) {
                  container.jqxGrid({
                  source: secondLevel, width: 1100, height: 300,
                  columnsheight: 40,
                  columns: [
                      { text: "RxNumber", dataField: "RxNumber", width: 80 },
                      { text: "Date Filled", dataField: "DateFilled" , width: 80},
                      { text: "Sale Price", dataField: "SalePrice", width: 100 },
                      { text: "Rebated Cost", dataField: "RebatedCost", width: 100 },
                      { text: "Rebated GM", dataField: "RebatedGM", width: 90 },
                      { text: "Quantity", dataField: "Quantity", width: 75 },
                      { text: "Day  Supply", dataField: "DaySupply",
                               renderer: function (text, align, columnsheight) {
                                 var textWithLineBreak = text.replace('  ', '<br />');
                                 return '<div style="margin-top: 5px; margin-left: 5px;">' + textWithLineBreak + '</div>';
                               }, 
                               width: 75 
                      },
                      { text: "Third Party Payer", dataField: "ThirdPartyPayer", width: 250 },
                      { text: "Prescriber NPI", dataField: "PrescriberNPI", width: 100 },
                      { text: "Prescriber", dataField: "PrescriberName", width: 150 },
                      { text: "DrugName/Strength", dataField: "DrugName/Strength", width: 500 },
                      { text: "NDC", dataField: "NDC", width: 100 }
                  ]
                  });
                }
                nestedRows = container.jqxGrid('getrows');
                \$.each(nestedRows, function () {
                    data.push(this);
                });
                nestedGrid = container;
            } 
            else {
              container.html("<p>No Data</p>");
            }
        },
        columns: [
           { text: 'Drug Name/Strength', datafield: 'DName', width: 500},
           { text: 'Average Rebated  GM per Rx', datafield: 'ARGM',    
                    renderer: function (text, align, columnsheight) {
                      var textWithLineBreak = text.replace('  ', '<br />');
                     return '<div style="margin-top: 5px; margin-left: 5px;">' + textWithLineBreak + '</div>';
                    }, 
                    width: 145 
           },
           { text: 'Total Rx Count', datafield: 'TRX', 
                    renderer: function (text, align, columnsheight) {
                      var textWithLineBreak = text.replace(' ', '<br />');
                      return '<div style="margin-top: 5px; margin-left: 5px;">' + textWithLineBreak + '</div>';
                    }, 
                    width: 80 
           },
           { text: 'Total Rebated GM', datafield: 'RGM', width: 155 },
           { text: 'Average Rebated  GM per Day Supply', datafield: 'ARGMDS', 
                    renderer: function (text, align, columnsheight) {
                      var textWithLineBreak = text.replace('  ', '<br />');
                      return '<div style="margin-top: 5px; margin-left: 5px;">' + textWithLineBreak + '</div>';
                    }, 
                    width: 150 
          },
   //     { text: 'Total Sales', datafield: 'TS', width: 120 }
        ]
     });
  });

  \$("#excelExport").jqxButton({
     theme: 'classic'
  });

  \$("#excelDetailExport").jqxButton({
     theme: 'classic'
  });

  \$("#excelDetailExport").click(function() {
     if (nestedGrid) {
       nestedGrid.jqxGrid('exportdata', 'csv', 'Theraputic Conversion Detail Report', true, null, null, '../js/jqwidgets/PHPExport/save-file.php');
     }
  });

  \$("#excelExport").click(function() {
    \$("#jqxgrid").jqxGrid('exportdata', 'csv', 'Theraputic Conversion Report', true, null, null, '../js/jqwidgets/PHPExport/save-file.php'); 
  });

  ^;
  print qq#</script>#;
}

#____________________________________________________________________________
