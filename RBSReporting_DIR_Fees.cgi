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

$inyear     = $in{'inyear'};

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

#______________________________________________________________________________

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
    <script type="text/javascript" src="../js/jqwidgets/jqwidgets/jqxgrid.aggregates.js"></script> 
   
  #;
} else {
   &MembersLogin;
   &MyPharmassessMembersTrailer;

   print qq#</BODY>\n#;
   print qq#</HTML>\n#;
   exit(0);
}

#______________________________________________________________________________

$Pharmacy_Name = $Pharmacy_Names{$PH_ID};

$progext = "${prog}${ext}";

$ntitle = "DIR Fees for $Pharmacy_Names{$PH_ID}";
print qq#<h1 class="rbsreporting">$ntitle</h1>\n#;

$dbx = DBI->connect("DBI:mysql:$DBNAME:$DBHOST",$dbuser,$dbpwd,
        { PrintError => 1, RaiseError => 1, InactiveDestroy => 0 } ) || die "$DBI::errstr";
   
DBI->trace(1) if ($dbitrace);

### ---------------------------------------------------------------------------

print qq#<FORM ACTION="$progext" METHOD="POST">\n#;
print qq#<SELECT NAME="inyear" onchange="this.form.submit()">\n#;
print qq#<OPTION VALUE="">Select a timeframe</OPTION>\n#;

my $SEL = '';

for ($y=$syear; $y >= $syear-1; $y--) {
  if ($y == $inyear) {
    $SEL = "SELECTED";
  } else {
    $SEL = '';
  }
    
  print qq#<OPTION $SEL VALUE="$y">$y</OPTION>\n#;
}

print qq#</SELECT>\n#;
print qq#</FORM>\n#;


if ($inyear > 0) {
  &display_DIR_Fee;
}

### ---------------------------------------------------------------------------

$dbx->disconnect;
 
#______________________________________________________________________________

&MyPharmassessMembersTrailer;

exit(0);

#______________________________________________________________________________

sub display_DIR_Fee {
  my $tbl_dirfee = 'rbsreporting.dirfee_rpt_new';
  $tbl_dirfee = 'webinar.dirfee_rpt' if($PH_ID < 12);
  my $tbl_tpp = 'officedb.third_party_payers';
  my $lyear = $inyear - 1;
  
  my $sql  = "SELECT b.Third_Party_Payer_Name, a.year, a.qtr, a.fee_amount
                FROM $tbl_dirfee a,
                     $tbl_tpp b
               WHERE a.TPP_id = b.Third_Party_Payer_ID
                  && a.Pharmacy_ID = $PH_ID
                  && a.Year = '$inyear'
            ORDER BY a.year, a.qtr, b.Third_Party_Payer_Name";

  $data = $dbx->prepare("$sql");
  $data->execute;
  $data_present = $data->rows;
    
  if ($data_present <= 0) {
    if ( $Pharmacy_Status_ReconRxs{$PH_ID} !~ /Active/ && $Pharmacy_Status_ReconRx_Clinics{$PH_ID} !~ /Active/) {
      print '<br><p>We currently do not receive 835 remits for your pharmacy. Please contact Pharm AssessRBS via e-mail at RBS@TDSClinical.com or call (888) 255-6526.</p>';
    }
    else {
      print "<br><p>No DIR Fee data found for $Pharmacy_Name to build report.</p>\n";
    }
  }
  else { 
    print qq#<hr /><br />\n#;
    print qq#<div id="jqxWidget">#;
    print qq#<div id="jqxgrid"></div>#;
    print qq#</div>#;
    print qq#<input style='margin-top: 10px;' type="button" value="Export to Excel" id='excelExport' /> #;
    print qq#<style>.bold { font-weight: bold; }</style> #;
    
    while ( my $rec = $data->fetchrow_hashref() ) {
      $key = $rec->{'qtr'} . '##' . $rec->{'Third_Party_Payer_Name'};
      $periods{$rec->{'qtr'}}++;
      $payers{$rec->{'Third_Party_Payer_Name'}} += $rec->{'fee_amount'};
      $amt{$key} = $rec->{'fee_amount'};
      $mtotal{$rec->{'qtr'}} += $rec->{'fee_amount'};
    }
  }

  $data->finish;

  &buildJQW();
}

#____________________________________________________________________________

sub buildJQW {
  my @array = (sort keys %payers );
  my $cnt = 0;
  my $grid;
  my $payer_num = 1;
  my @vals;
  my $fields = "{ name: 'Period', type:'string'},";
  my $cols = "{ text: 'Period', datafield: 'Period', width: 100, aggregates: [{ 'Totals':
                            function (aggregatedValue, currentValue, column, record) {
                                return '';
                            } } ] },";
  my $tbl_width = 100;

  ### Build Grid Data Definition
  foreach my $payer (@array) {
    $fields  .= "{ name: 'Pay${payer_num}', type:'number'},";
    $cols    .= "{ text: '$payer', datafield: 'Pay${payer_num}', width: 120, cellsformat: 'C2', cellsalign: 'right', align: 'right', aggregates: [{ 'Total':
                            function (aggregatedValue, currentValue, column, record) {
                                return aggregatedValue + currentValue;
                            } } ],
                          aggregatesrenderer: function(aggregates) {
                            var renderstring = aggregates[\"Total\"];
                            return '<span style=\"margin-top: 4px; float: right;\">' + renderstring + '</span>';
                          } },";
    $payer_num++;
    $tbl_width += 120;
  }

  $fields .= "{ name: 'Total', type:'number'}";
  $cols   .= "{ text: 'Grand Total', datafield: 'Total', width: 120, cellsformat: 'C2', cellsalign: 'right', align: 'right', aggregates: [{ 'Total':
                            function (aggregatedValue, currentValue, column, record) {
                                return aggregatedValue + currentValue;
                            } } ],
                          aggregatesrenderer: function(aggregates) {
                            var renderstring = aggregates[\"Total\"];
                            return '<span style=\"margin-top: 4px; float: right;\">' + renderstring + '</span>';
                          }
              }";
  $tbl_width += 120;

  ### Build Grid Data
  $grid = '[';
  foreach $period (sort keys %periods) {
    @vals = ();
    $payer_num = 1;
    $grid_dtl = '';
    foreach my $payer (@array) {
      my $key = $period . '##' . $payer;
      my $val = 0;
      if ( $amt{$key} ) {
        $val = $amt{$key};
      }
      $grid_dtl .= "'Pay${payer_num}':'$val',";
      $payer_num++;
    }

    $data_period = $inyear . $period;

    $grid .= "{'Period':'$data_period'," . $grid_dtl . "'Total': '$mtotal{$period}'},";
    $cnt++;
  }


  $grid .= "]";
#  print "<h2>$cnt</h2>";
  print qq# <script>#;
  print qq^
\$(document).ready(function () {

// prepare the data

var source = {
    datatype: "json",
    datafields: [ $fields ],
    localdata: $grid,
    sortcolumn: 'Period',
};

var dataAdapter = new \$.jqx.dataAdapter(source);

         \$("#jqxgrid").jqxGrid(
            {
                width: $tbl_width,
                autoheight: true,
                columnsheight: 40,
                showstatusbar: true,
                source: dataAdapter,
                selectionmode: 'singlerow',
                showaggregates: true,
                editable:false,
    theme: 'classic',
    altrows: true,
    sortable: true,
    columns: [ $cols ]
            });

var cellsrenderer = function (row, column, value) {
	return '<div style="text-align: right; margin-top: 5px;">' + value + '</div>';
}
var columnrenderer = function (value) {
	return '<div style="text-align: right; margin-top: 5px;">' + value + '</div>';       
}

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

#                height: 480,

#____________________________________________________________________________

sub display_DIR_Fee_old {
  my $tbl_dirfee = 'rbsreporting.dirfee_rpt';
  $tbl_dirfee = 'webinar.dirfee_rpt' if($PH_ID < 12);
  my $tbl_tpp = 'officedb.third_party_payers';
  my $lyear = $inyear - 1;
  
  my $sql  = "SELECT b.Third_Party_Payer_Name, a.notes, a.year, a.qtr, a.claim_count, a.fee_amount
                FROM $tbl_dirfee a,
                     $tbl_tpp b
               WHERE a.TPP_id = b.Third_Party_Payer_ID
                  && a.Pharmacy_ID = $PH_ID
                  && a.Year = '$inyear'
            ORDER BY a.year, a.qtr, b.Third_Party_Payer_Name";

  $data = $dbx->prepare("$sql");
  $data->execute;
  $data_present = $data->rows;
    
  if ($data_present <= 0) {
    if ( $Pharmacy_Status_ReconRxs{$PH_ID} !~ /Active/ && $Pharmacy_Status_ReconRx_Clinics{$PH_ID} !~ /Active/) {
      print '<br><p>We currently do not receive 835 remits for your pharmacy. Please contact Pharm AssessRBS via e-mail at RBS@TDSClinical.com or call (888) 255-6526.</p>';
    }
    else {
      print "<br><p>No DIR Fee data found for $Pharmacy_Name to build report.</p>\n";
    }
  }
  else { 
    my $save_location = "D:\\PharmAssess\\Reports\\";
    my $filename      = "${PH_ID}_dir_fees_${inyear}_report.xlsx";
    my $SAVELOC       = "${save_location}\\${filename}";
    
    print qq#<hr /><br />\n#;
    
    print "<p><strong>DIR Fees $inyear</strong></p>\n";
    
    print qq#<p><img src="/images/icons/xlsx1.png" style="vertical-align: middle"><a href="/Reports/$filename">Download Spreadsheet (XLSX)</a></p>\n#;
    
    print qq#<hr />\n#;
    
    $workbook = Excel::Writer::XLSX->new( $SAVELOC );

    $worksheet = $workbook->add_worksheet();
    $worksheet->set_portrait();
    $worksheet->fit_to_pages( 1, 0 ); #Fit all columns on a single page
    $worksheet->hide_gridlines(0); #0 = Show gridlines
    
    $worksheet->repeat_rows( 0 );    #Print on each page
    
    $worksheet->set_header("&L$Pharmacy_Name - $inyear DIR Fees");
    
    $format_bold = $workbook->add_format( bold => 1 );
    $format_bold->set_text_wrap();
    $format_boldh = $workbook->add_format( bg_color => '#b3b3b3', bold => 1, border => 1 );
    $format_boldh->set_text_wrap();
    $format_boldch = $workbook->add_format( bg_color => '#b3b3b3', align => 'center', bold => 1, border => 1 );
    $format_boldch->set_text_wrap();
    
    my $format_left = $workbook->add_format( align => 'left', border => 1 );
    my $format_right = $workbook->add_format( align => 'right' );
    my $format_number = $workbook->add_format( num_format => '#,##0', border => 1 );
    my $format_money = $workbook->add_format( num_format => '$#,##0.00', border => 1 );
    my $format_numberbh = $workbook->add_format( bg_color => '#b3b3b3', bold => 1, num_format => '#,##0', border => 1 );
    my $format_moneybh = $workbook->add_format( bg_color => '#b3b3b3', bold => 1, num_format => '$#,##0.00', border => 1 );
    
    $worksheet->keep_leading_zeros();
    
    ### -----------------------------------------------------------------------------------
    
    my $row = 0;
    my $col = 0;
    my $qtr_sav = '';
    my $first = 1;
    my $claim_total = 0;
    my $fee_total = 0;
    
    $worksheet->set_column( 0, 0, 35 );
    $worksheet->set_column( 1, 0, 40 );
    $worksheet->set_column( 2, 5, 12 );

    $worksheet->merge_range( 'A1:B1', $Pharmacy_Name, $format_bold ); $row++; $row++;

    while ( my $rec = $data->fetchrow_hashref() ) {
      $col = 0;

      if ($rec->{qtr} ne $qtr_sav) {
        if (!$first) {
          $row++;
          if ($cliam_total > 0) {
            $avg_total = $fee_total/$claim_total;
          }
          else {
            $avg_total = 0;
          }
          $worksheet->write_blank($row, $col, $format_number); $col++;
          $worksheet->write_blank($row, $col, $format_number); $col++;
          $worksheet->write_blank($row, $col, $format_number); $col++;
          $worksheet->write_blank($row, $col, $format_number); $col++;
          $worksheet->write_blank($row, $col, $format_number); $row++;
          $col = 0;
          $worksheet->write($row, $col, "Pharmacy Total", $format_boldh); $col++;
          $worksheet->write($row, $col, " ", $format_boldh); $col++;
          $worksheet->write($row, $col, $claim_total, $format_numberbh); $col++;
          $worksheet->write($row, $col, $fee_total, $format_moneybh); $col++;
          $worksheet->write($row, $col, $avg_total, $format_moneybh);
          $row++;
          $row++;
          $row++;
        }

        $claim_total = 0;
        $fee_total = 0;

        $col = 0;
        $worksheet->write($row, $col, "Q$rec->{qtr} $rec->{year} DIR Fee Report", $format_bold); $row++;
        $worksheet->write($row, $col, "Payer", $format_boldh); $col++;
        $worksheet->write($row, $col, "Notes", $format_boldh); $col++;
        $worksheet->write($row, $col, "DIR Claim Count", $format_boldch); $col++;
        $worksheet->write($row, $col, "DIR Fee Amount", $format_boldch); $col++;
        $worksheet->write($row, $col, "Average DIR/Script", $format_boldch);
      }

      $row++;
      $col = 0;

      if ($rec->{'claim_count'} && $rec->{'claim_count'} > 0) {
        $fee_avg = $rec->{'fee_amount'} / $rec->{'claim_count'};
      }
      else {
        $fee_avg = '0';
      }

      $worksheet->write($row, $col, $rec->{'Third_Party_Payer_Name'}, $format_left); $col++;
      $worksheet->write($row, $col, $rec->{'notes'}, $format_left); $col++;
      $worksheet->write($row, $col, $rec->{'claim_count'}, $format_number); $col++;
      $worksheet->write($row, $col, $rec->{'fee_amount'}, $format_money ); $col++;
      $worksheet->write($row, $col, $fee_avg, $format_money );

      $qtr_sav = $rec->{qtr};
      $claim_total += $rec->{'claim_count'};
      $fee_total += $rec->{'fee_amount'};
      $first = 0;
    }
    
    $col = 0;
    $row++;
    $worksheet->write_blank($row, $col, $format_number); $col++;
    $worksheet->write_blank($row, $col, $format_number); $col++;
    $worksheet->write_blank($row, $col, $format_number); $col++;
    $worksheet->write_blank($row, $col, $format_number); $col++;
    $worksheet->write_blank($row, $col, $format_number); $row++;
    $col = 0;
    $worksheet->write($row, $col, "Pharmacy Total", $format_boldh); $col++;
    $worksheet->write($row, $col, " ", $format_boldh); $col++;
    $worksheet->write($row, $col, $claim_total, $format_numberbh); $col++;
    $worksheet->write($row, $col, $fee_total, $format_moneybh); $col++;
    $worksheet->write($row, $col, $avg_total, $format_moneybh);

    $workbook->close(); #End XLSX
  }

  $data->finish;
}
