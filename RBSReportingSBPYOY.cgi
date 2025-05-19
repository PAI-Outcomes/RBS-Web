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

$DBNAME = 'RBSReporting';
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

$Pharmacy_Name = $Pharmacy_Names{$PH_ID};

$progext = "${prog}${ext}";

$ntitle = "Sales by Payer (Year-Over-Year) for $Pharmacy_Names{$inNCPDP}";
print qq#<h1 class="rbsreporting">$ntitle</h1>\n#;
$DBNAME = 'Webinar' if($USER == 2182);

$dbx = DBI->connect("DBI:mysql:$DBNAME:$DBHOST",$dbuser,$dbpwd,
        { PrintError => 1, RaiseError => 1, InactiveDestroy => 0 } ) || die "$DBI::errstr";
   
DBI->trace(1) if ($dbitrace);

### ---------------------------------------------------------------------------

($inyear, $inqtr) = split( '-', $in{'inTimeframe'} );
$inqtr =~ s/Q//gi; #NOT TESTED

print qq#<FORM ACTION="$progext" METHOD="POST">\n#;
print qq#<SELECT NAME="inTimeframe" onchange="this.form.submit()">\n#;
print qq#<OPTION VALUE="">Select a timeframe</OPTION>\n#;

my $SEL = '';

if ( $PH_ID == 445 ) {
  $minus = 3;
}
else {
  $minus = 1;
}


for ($y=$syear; $y >= $syear-$minus; $y--) {
  for ($q=4; $q >= 1; $q--) {
  
    if ($y == $syear) {
      if      ($month =~ /^1$|^2$|^3$/ && $q >= 1) {
        next();
      } elsif ($month =~ /^4$|^5$|^6$/ && $q >= 2) {
        next();
      } elsif ($month =~ /^7$|^8$|^9$/ && $q >= 3) {
        next();
      } 
    }
    
    my $year  = $y;
    my $lyear = $y-1;
    my $qtr   = $q;
    
    if ($y == $inyear && $q == $inqtr) {
      $SEL = "SELECTED";
    } else {
      $SEL = '';
    }
    
    #print "<p>Compare $year-Q$qtr to $lyear-Q$qtr</p>\n";
    print qq#<OPTION $SEL VALUE="$year-Q$qtr">Compare $year-Q$qtr to $lyear-Q$qtr</OPTION>\n#;
    
  }
}

print qq#</SELECT>\n#;
print qq#</FORM>\n#;


if ($inyear > 0 && $inqtr > 0) {
  &displaySBPYOY;
}

### ---------------------------------------------------------------------------

$dbx->disconnect;
 
#______________________________________________________________________________

&MyPharmassessMembersTrailer;

exit(0);

#______________________________________________________________________________

sub displaySBPYOY {
  my $lyear = $inyear - 1;
  
  &loadSBPData();
  
  $data_present = keys %sbpRxCount;
  
  if ($data_present <= 0) {
    print qq#<p>No Sales by Payer data found for $Pharmacy_Name to build report.</p>\n#;
  } else { 
    ### START EXCEL FILE AND SET VARS ### -------------------------------------------------
    my $save_location = "D:\\RBSDesktop\\Reports\\";
    my $filename      = $Pharmacy_NCPDPs{$PH_ID} . "_sales_by_payer_${inyear}-Q${inqtr}_to_${lyear}-Q${inqtr}_report.xlsx";
    my $SAVELOC       = "${save_location}\\${filename}";
    
    print qq#<hr /><br />\n#;
    
    print "<p><strong>Comparing $inyear-Q$inqtr to $lyear-Q$inqtr</strong></p>\n";
    
    print qq#<p><img src="/images/icons/xlsx1.png" style="vertical-align: middle"><a href="/Reports/$filename">Download Spreadsheet (XLSX)</a></p>\n#;
    
    print qq#<hr />\n#;
    
#   $workbook = Excel::Writer::XLSX->new( $save_location.$filename );
    $workbook = Excel::Writer::XLSX->new( $SAVELOC );

    $worksheet = $workbook->add_worksheet();
    $worksheet->set_landscape();
    $worksheet->fit_to_pages( 1, 0 ); #Fit all columns on a single page
    $worksheet->hide_gridlines(0); #0 = Show gridlines
    
    $worksheet->freeze_panes( 1, 0 ); #Freeze first row
    $worksheet->repeat_rows( 0 );    #Print on each page
    
    $worksheet->set_header("&L$Pharmacy_Name - Comparing $inyear-Q$inqtr to $lyear-Q$inqtr");
    #$worksheet->set_footer("&CPage &P of &N &RName: ___________________________  ");
    
    $format_bold = $workbook->add_format();
    $format_bold->set_bold();
    $format_bold->set_text_wrap();
    
    my $format_left = $workbook->add_format();
    $format_left->set_align( 'left' );
    my $format_center = $workbook->add_format();
    $format_center->set_align( 'center' );
    my $format_right = $workbook->add_format();
    $format_right->set_align( 'right' );
    my $format_number = $workbook->add_format();
    $format_number->set_num_format( '#,##0' );
    my $format_money = $workbook->add_format();
    $format_money->set_num_format( '$#,##0.00' );
    my $format_1dec = $workbook->add_format();
    $format_1dec->set_num_format( '0.0' );
    my $format_2dec = $workbook->add_format();
    $format_2dec->set_num_format( '0.00' );
    
    $worksheet->keep_leading_zeros();
    
    ### -----------------------------------------------------------------------------------
    
    if ( $print_to_screen ) {
      print qq#
      <style>
      .sbpyoy th {
        vertical-align: top;
      }
      .sbpyoy td {
        border: 1px solid \#000;
      }
      .alt_td {
        background: \#EEE;
      }
      </style>
      #;
    
      print "<table class=\"sbpyoy\">\n";
      
      print qq#<tr>#;
      print qq#<th>Plan</th>\n#;
      
      print qq#<th>$inyear<br />Rx Count</th>\n#;
      print qq#<th>$inyear<br />GDR</th>\n#;
      print qq#<th>$inyear<br />GER</th>\n#;
      print qq#<th>$inyear<br />Sales</th>\n#;
      print qq#<th>$inyear<br />% of Sales</th>\n#;
      print qq#<th>$inyear<br />Gross Margin</th>\n#;
      print qq#<th>$inyear<br />GM %</th>\n#;
      print qq#<th>$inyear<br />Sale/ Script</th>\n#;
      print qq#<th>$inyear<br />GM/ Script</th>\n#;
      print qq#<th>$inyear<br />Avg. Days Supply</th>\n#;
      
      #print qq#<th>&nbsp; &nbsp;</th>\n#;
      
      print qq#<th class="">$lyear<br />Rx Count</th>\n#;
      print qq#<th class="">$lyear<br />GDR</th>\n#;
      print qq#<th class="">$lyear<br />GER</th>\n#;
      print qq#<th class="">$lyear<br />Sales</th>\n#;
      print qq#<th class="">$lyear<br />% of Sales</th>\n#;
      print qq#<th class="">$lyear<br />Gross Margin</th>\n#;
      print qq#<th class="">$lyear<br />GM %</th>\n#;
      print qq#<th class="">$lyear<br />Sale/ Script</th>\n#;
      print qq#<th class="">$lyear<br />GM/ Script</th>\n#;
      print qq#<th class="">$lyear<br />Avg. Days Supply</th>\n#;
      
      print qq#</tr>#;
    }
    
    $wrow = 1;
    
    #$worksheet->set_column( 0, 0, 11.3 ); #Col Addd
    $worksheet->set_column( 0, 17, 12 );
    
    $worksheet->write( "A$wrow", "Plan", $format_bold);
      $worksheet->set_column( 0, 0, 32 );
    
    $worksheet->write( "B$wrow", "$inyear Rx Count", $format_bold);
      $worksheet->set_column( 1, 1, 9 );
    $worksheet->write( "C$wrow", "$inyear GDR", $format_bold );
    $worksheet->write( "D$wrow", "$inyear GER", $format_bold );
    $worksheet->write( "E$wrow", "$inyear Sales", $format_bold );
    $worksheet->write( "F$wrow", "$inyear % of Sales", $format_bold );
      $worksheet->set_column( 5, 5, 7 );
    $worksheet->write( "G$wrow", "$inyear Gross Margin", $format_bold );
    $worksheet->write( "H$wrow", "$inyear GM %", $format_bold );
      $worksheet->set_column( 7, 7, 7 );
    $worksheet->write( "I$wrow", "$inyear Sale/ Script", $format_bold );
    $worksheet->write( "J$wrow", "$inyear GM/ Script", $format_bold );
    $worksheet->write( "K$wrow", "$inyear Avg. Days Supply", $format_bold );
    
    $worksheet->write( "L$wrow", "      "); #Col 9
    
    $worksheet->write( "M$wrow", "$lyear Rx Count", $format_bold);
      $worksheet->set_column( 12, 12, 9 );
    $worksheet->write( "N$wrow", "$lyear GDR", $format_bold );
    $worksheet->write( "O$wrow", "$lyear GER", $format_bold );
    $worksheet->write( "P$wrow", "$lyear Sales", $format_bold );
    $worksheet->write( "Q$wrow", "$lyear % of Sales", $format_bold );
      $worksheet->set_column( 16, 16, 7 );
    $worksheet->write( "R$wrow", "$lyear Gross Margin", $format_bold );
    $worksheet->write( "S$wrow", "$lyear GM %", $format_bold );
      $worksheet->set_column( 18, 18, 7 );
    $worksheet->write( "T$wrow", "$lyear Sale/ Script", $format_bold );
    $worksheet->write( "U$wrow", "$lyear GM/ Script", $format_bold );
    $worksheet->write( "V$wrow", "$lyear Avg. Days Supply", $format_bold );
    
    
    foreach my $key (sort { $sbpSales{$b} <=> $sbpSales{$a} } keys %sbpSales) {
      next if ($key !~ /plan/i);
      next if ($key !~ /$inyear/i);
      
      $wrow++;
      
      if ( $print_to_screen ) {
        print "<tr>\n";
      }
      
      my $plan            = $sbpPlan{$key};
      my $count           = $sbpRxCount{$key} || 0;
      my $sales           = sprintf "%.2f", $sbpSales{$key};
      my $percent         = sprintf "%.1f", $sbpPercentSales{$key};
      my $gm              = sprintf "%.2f", $sbpGrossMargin{$key};
      my $gm_percent      = sprintf "%.1f", $sbpGrossMarginPercent{$key};
      my $sale_per_script = sprintf "%.2f", $sbpSalesPerScript{$key};
      my $gm_per_script   = sprintf "%.2f", $sbpGrossMarginPerScript{$key};
      my $avg_day_supply  = sprintf "%.1f", $sbpAvgDaysSupply{$key};
      my $gdr_percent     = sprintf "%.1f", $sbpGDRPercent{$key};
      my $ger_percent     = sprintf "%.1f", $sbpGERPercent{$key};
      
      $shown_count   += $count;
      $shown_sales   += $sales;
      $shown_percent += $percent;
      $shown_gm      += $gm;
      
      
      if ( $print_to_screen ) {
        print qq#<td>$plan</td>\n#;
        
        print qq#<td class="align_right">$count</td>\n#;
        print qq#<td class="align_right">$gdr_percent</td>\n#;
        print qq#<td class="align_right">$ger_percent</td>\n#;
        print qq#<td class="align_right">$sales</td>\n#;
        print qq#<td class="align_right">$percent</td>\n#;
        print qq#<td class="align_right">$gm</td>\n#;
        print qq#<td class="align_right">$gm_percent</td>\n#;
        print qq#<td class="align_right">$sale_per_script</td>\n#;
        print qq#<td class="align_right">$gm_per_script</td>\n#;
        print qq#<td class="align_right">$avg_day_supply</td>\n#;
      }
      
      $worksheet->write( "A$wrow", "$plan", $format_left);
      
      $worksheet->write( "B$wrow", "$count", $format_number);
      $worksheet->write( "C$wrow", "$gdr_percent", $format_1dec );
      $worksheet->write( "D$wrow", "$ger_percent", $format_1dec );
      $worksheet->write( "E$wrow", "$sales", $format_money );
      $worksheet->write( "F$wrow", "$percent", $format_1dec );
      $worksheet->write( "G$wrow", "$gm", $format_money );
      $worksheet->write( "H$wrow", "$gm_percent", $format_1dec );
      $worksheet->write( "I$wrow", "$sale_per_script", $format_money );
      $worksheet->write( "J$wrow", "$gm_per_script", $format_right );
      $worksheet->write( "K$wrow", "$avg_day_supply", $format_1dec );
      
      # --- # --- #
      #print qq#<td>&nbsp; &nbsp;</td>\n#;
      $worksheet->write( "L$wrow", "      ");
      # --- # --- #
      
      my ($kyear, $kplan) = split('##', $key);
      my $lkey = "$lyear##$kplan";
      
      my $lplan            = $sbpPlan{$lkey};
      my $lcount           = $sbpRxCount{$lkey} || 0;
      my $lsales           = sprintf "%.2f", $sbpSales{$lkey};
      my $lpercent         = sprintf "%.1f", $sbpPercentSales{$lkey};
      my $lgm              = sprintf "%.2f", $sbpGrossMargin{$lkey};
      my $lgm_percent      = sprintf "%.1f", $sbpGrossMarginPercent{$lkey};
      my $lgdr_percent     = sprintf "%.1f", $sbpGDRPercent{$lkey};
      my $lger_percent     = sprintf "%.1f", $sbpGERPercent{$lkey};
      my $lsale_per_script = sprintf "%.2f", $sbpSalesPerScript{$lkey};
      my $lgm_per_script   = sprintf "%.2f", $sbpGrossMarginPerScript{$lkey};
      my $lavg_day_supply  = sprintf "%.1f", $sbpAvgDaysSupply{$lkey};
      
      $shown_lcount   += $lcount;
      $shown_lsales   += $lsales;
      $shown_lpercent += $lpercent;
      $shown_lgm      += $lgm;
      
      if ( $print_to_screen ) {
        print qq#<td class="align_right alt_td">$lcount</td>\n#;
        print qq#<td class="align_right alt_td">$lgdr_percent</td>\n#;
        print qq#<td class="align_right alt_td">$lger_percent</td>\n#;
        print qq#<td class="align_right alt_td">$lsales</td>\n#;
        print qq#<td class="align_right alt_td">$lpercent</td>\n#;
        print qq#<td class="align_right alt_td">$lgm</td>\n#;
        print qq#<td class="align_right alt_td">$lgm_percent</td>\n#;
        print qq#<td class="align_right alt_td">$lsale_per_script</td>\n#;
        print qq#<td class="align_right alt_td">$lgm_per_script</td>\n#;
        print qq#<td class="align_right alt_td">$lavg_day_supply</td>\n#;
      }
      
      $worksheet->write( "M$wrow", "$lcount", $format_number);
      $worksheet->write( "N$wrow", "$lgdr_percent", $format_1dec );
      $worksheet->write( "O$wrow", "$lger_percent", $format_1dec );
      $worksheet->write( "P$wrow", "$lsales", $format_money );
      $worksheet->write( "Q$wrow", "$lpercent", $format_1dec );
      $worksheet->write( "R$wrow", "$lgm", $format_money );
      $worksheet->write( "S$wrow", "$lgm_percent", $format_1dec );
      $worksheet->write( "T$wrow", "$lsale_per_script", $format_money );
      $worksheet->write( "U$wrow", "$lgm_per_script", $format_right );
      $worksheet->write( "V$wrow", "$lavg_day_supply", $format_1dec );
      
      if ( $print_to_screen ) {
        print "<tr>\n";
      }
      
    }
    
    
    my $tkey = "$inyear##TOTAL";
    my $tcount           = $sbpRxCount{$tkey} || 0;
    my $tsales           = sprintf "%.2f", $sbpSales{$tkey};
    my $tpercent         = sprintf "%.1f", $sbpPercentSales{$tkey};
    my $tgm              = sprintf "%.2f", $sbpGrossMargin{$tkey};
    my $tgm_percent      = sprintf "%.1f", $sbpGrossMarginPercent{$tkey};
    my $tgdr_percent     = sprintf "%.1f", $sbpGDRPercent{$tkey};
    my $tger_percent     = sprintf "%.1f", $sbpGERPercent{$tkey};
    my $tsale_per_script = sprintf "%.2f", $sbpSalesPerScript{$tkey};
    my $tgm_per_script   = sprintf "%.2f", $sbpGrossMarginPerScript{$tkey};
    my $tavg_day_supply  = sprintf "%.1f", $sbpAvgDaysSupply{$tkey};
    
    
    my $tlkey = "$lyear##TOTAL";
    my $tlcount           = $sbpRxCount{$tlkey} || 0;
    my $tlsales           = sprintf "%.2f", $sbpSales{$tlkey};
    my $tlpercent         = sprintf "%.1f", $sbpPercentSales{$tlkey};
    my $tlgm              = sprintf "%.2f", $sbpGrossMargin{$tlkey};
    my $tlgm_percent      = sprintf "%.1f", $sbpGrossMarginPercent{$tlkey};
    my $tlgdr_percent     = sprintf "%.1f", $sbpGDRPercent{$tlkey};
    my $tlger_percent     = sprintf "%.1f", $sbpGERPercent{$tlkey};
    my $tlsale_per_script = sprintf "%.2f", $sbpSalesPerScript{$tlkey};
    my $tlgm_per_script   = sprintf "%.2f", $sbpGrossMarginPerScript{$tlkey};
    my $tlavg_day_supply  = sprintf "%.1f", $sbpAvgDaysSupply{$tlkey};
    
    
    my $total_count_LESS_shown_count = ($tcount - $shown_count) || 1;
    my $total_sales_LESS_shown_sales = ($tsales - $shown_sales) || 1;
    my $other_sale_per_script = sprintf "%.2f", (($tsales - $shown_sales)/$total_count_LESS_shown_count);
    my $other_gm_per_script   = sprintf "%.2f", (($tgm - $shown_gm)/$total_count_LESS_shown_count);
    my $other_count           = $tcount - $shown_count;
    my $other_gm_percent      = sprintf "%.1f", ((($tgm - $shown_gm)/($total_sales_LESS_shown_sales))*100);
    my $other_sales           = sprintf "%.0f", ($tsales - $shown_sales);
    my $other_percent         = sprintf "%.1f", (100 - $shown_percent);
    my $other_gm              = sprintf "%.0f", ($tgm - $shown_gm);
    
    
    my $ltotal_count_LESS_shown_count = ($tlcount - $shown_lcount) || 1;
    my $ltotal_sales_LESS_shown_sales = ($tlsales - $shown_lsales) || 1;
    my $otherl_sale_per_script = sprintf "%.2f", (($tlsales - $shown_lsales)/$ltotal_count_LESS_shown_count);
    my $otherl_gm_per_script   = sprintf "%.2f", (($tlgm - $shown_lgm)/$ltotal_count_LESS_shown_count);
    my $otherl_count           = $tlcount - $shown_lcount;
    my $otherl_gm_percent      = sprintf "%.1f", ((($tlgm - $shown_lgm)/($ltotal_sales_LESS_shown_sales))*100);
    my $otherl_sales           = sprintf "%.0f", ($tlsales - $shown_lsales);
    my $otherl_percent         = sprintf "%.1f", (100 - $shown_lpercent);
    my $otherl_gm              = sprintf "%.0f", ($tlgm - $shown_lgm);
    
    $wrow++;
    
    if ( $print_to_screen ) {
      print "<tr>\n";
      print qq#<td>Other</td>\n#;

      print qq#<td class="align_right">$other_count</td>\n#;
      print qq#<td class="align_right">$other_gdr_percent</td>\n#;
      print qq#<td class="align_right">$other_ger_percent</td>\n#;
      print qq#<td class="align_right">$other_sales</td>\n#;
      print qq#<td class="align_right">$other_percent</td>\n#;
      print qq#<td class="align_right">$other_gm</td>\n#;
      print qq#<td class="align_right">$other_gm_percent</td>\n#;
      print qq#<td class="align_right">$other_sale_per_script</td>\n#;
      print qq#<td class="align_right">$other_gm_per_script</td>\n#;
      print qq#<td class="align_right">&nbsp;</td>\n#;

      print qq#<td class="align_right alt_td">$otherl_count</td>\n#;
      print qq#<td class="align_right alt_td">$otherl_gdr_percent</td>\n#;
      print qq#<td class="align_right alt_td">$otherl_ger_percent</td>\n#;
      print qq#<td class="align_right alt_td">$otherl_sales</td>\n#;
      print qq#<td class="align_right alt_td">$otherl_percent</td>\n#;
      print qq#<td class="align_right alt_td">$otherl_gm</td>\n#;
      print qq#<td class="align_right alt_td">$otherl_gm_percent</td>\n#;
      print qq#<td class="align_right alt_td">$otherl_sale_per_script</td>\n#;
      print qq#<td class="align_right alt_td">$otherl_gm_per_script</td>\n#;
      print qq#<td class="align_right alt_td">&nbsp;</td>\n#;
      
      print "</tr>\n";
    }
    
    $worksheet->write( "A$wrow", "OTHER", $format_left);

    $worksheet->write( "B$wrow", "$other_count", $format_number);
    $worksheet->write( "C$wrow", "$other_gdr_percent", $format_1dec );
    $worksheet->write( "D$wrow", "$other_ger_percent", $format_1dec );
    $worksheet->write( "E$wrow", "$other_sales", $format_money );
    $worksheet->write( "F$wrow", "$other_percent", $format_1dec );
    $worksheet->write( "G$wrow", "$other_gm", $format_money );
    $worksheet->write( "H$wrow", "$other_gm_percent", $format_1dec );
    $worksheet->write( "I$wrow", "$other_sale_per_script", $format_money );
    $worksheet->write( "J$wrow", "$other_gm_per_script", $format_right );
    $worksheet->write( "K$wrow", "", $format_1dec );

    $worksheet->write( "L$wrow", "      ");
    
    $worksheet->write( "M$wrow", "$otherl_count", $format_number);
    $worksheet->write( "N$wrow", "$otherl_gdr_percent", $format_1dec );
    $worksheet->write( "O$wrow", "$otherl_ger_percent", $format_1dec );
    $worksheet->write( "P$wrow", "$otherl_sales", $format_money );
    $worksheet->write( "Q$wrow", "$otherl_percent", $format_1dec );
    $worksheet->write( "R$wrow", "$otherl_gm", $format_money );
    $worksheet->write( "S$wrow", "$otherl_gm_percent", $format_1dec );
    $worksheet->write( "T$wrow", "$otherl_sale_per_script", $format_money );
    $worksheet->write( "U$wrow", "$otherl_gm_per_script", $format_right );
    $worksheet->write( "V$wrow", "", $format_1dec );
      
    ### -----------------------------------------------------------------------------------
    
    
    ### TOTAL ROW -------------------------------------------------------------------------
    
    $wrow++;
    
    if ( $print_to_screen ) {
      print "<tr>\n";
      print qq#<td>Total</td>\n#;

      print qq#<td class="align_right">$tsales</td>\n#;
      print qq#<td class="align_right">$tgdr</td>\n#;
      print qq#<td class="align_right">$tger</td>\n#;
      print qq#<td class="align_right">$tcount</td>\n#;
      print qq#<td class="align_right">$tsales</td>\n#;
      print qq#<td class="align_right">$tpercent</td>\n#;
      print qq#<td class="align_right">$tgm</td>\n#;
      print qq#<td class="align_right">$tgm_percent</td>\n#;
      print qq#<td class="align_right">$tsale_per_script</td>\n#;
      print qq#<td class="align_right">$tgm_per_script</td>\n#;
      print qq#<td class="align_right">&nbsp;</td>\n#;

      print qq#<td class="align_right alt_td">$tlcount</td>\n#;
      print qq#<td class="align_right alt_td">$tlgdr</td>\n#;
      print qq#<td class="align_right alt_td">$tlger</td>\n#;
      print qq#<td class="align_right alt_td">$tlsales</td>\n#;
      print qq#<td class="align_right alt_td">$tlpercent</td>\n#;
      print qq#<td class="align_right alt_td">$tlgm</td>\n#;
      print qq#<td class="align_right alt_td">$tlgm_percent</td>\n#;
      print qq#<td class="align_right alt_td">$tlsale_per_script</td>\n#;
      print qq#<td class="align_right alt_td">$tlgm_per_script</td>\n#;
      print qq#<td class="align_right alt_td">&nbsp;</td>\n#;
      
      print "</tr>\n";
    }
    
    $worksheet->write( "A$wrow", "TOTAL", $format_left);

    $worksheet->write( "B$wrow", "$tcount", $format_number);
    $worksheet->write( "C$wrow", "$tgdr", $format_number);
    $worksheet->write( "D$wrow", "$tger", $format_number);
    $worksheet->write( "E$wrow", "$tsales", $format_money );
    $worksheet->write( "F$wrow", "$tpercent", $format_1dec );
    $worksheet->write( "G$wrow", "$tgm", $format_money );
    $worksheet->write( "H$wrow", "$tgm_percent", $format_1dec );
    $worksheet->write( "I$wrow", "$tsale_per_script", $format_money );
    $worksheet->write( "J$wrow", "$tgm_per_script", $format_right );
    $worksheet->write( "K$wrow", "", $format_1dec );

    $worksheet->write( "L$wrow", "      ");
    
    $worksheet->write( "M$wrow", "$tlcount", $format_number);
    $worksheet->write( "N$wrow", "$tlgdr", $format_money );
    $worksheet->write( "O$wrow", "$tlger", $format_money );
    $worksheet->write( "P$wrow", "$tlsales", $format_money );
    $worksheet->write( "Q$wrow", "$tlpercent", $format_1dec );
    $worksheet->write( "R$wrow", "$tlgm", $format_money );
    $worksheet->write( "S$wrow", "$tlgm_percent", $format_1dec );
    $worksheet->write( "T$wrow", "$tlsale_per_script", $format_money );
    $worksheet->write( "U$wrow", "$tlgm_per_script", $format_right );
    $worksheet->write( "V$wrow", "", $format_1dec );
      
    ### -----------------------------------------------------------------------------------
    
    if ( $print_to_screen ) {
      print "</table>\n";
    }
    
    $workbook->close(); #End XLSX
    
  }
}

#____________________________________________________________________________

sub loadSBPData {
  $showPlansMAX = 25;

  my $Pharmacy_ID = $PH_ID;
  
  my $key = '';
  %sbpPlan = ();
  %sbpRxCount = ();
  %sbpSales = ();
  %sbpPercentSales = ();
  %sbpGrossMargin = ();
  %sbpGrossMarginPercent = ();
  %sbpSalesPerScript = ();
  %sbpGrossMarginPerScript = ();
  %sbpAvgDaysSupply = ();
  %sbpGDRPercent = ();
  %sbpGERPercent = ();
  
  @years = ($inyear, $inyear - 1);
  
  foreach (@years) {
    my $jyear = $_;
    my $jqtr  = $inqtr;
    
    my $sbp_data_present = 0;
    my $sql  = "SELECT ncpdp 
                  FROM ${DBNAME}.sales_by_payer_new 
                 WHERE Pharmacy_ID = $Pharmacy_ID
                    && Year = $jyear 
                    && Qtr_YTD = $jqtr";

    $checkData  = $dbx->prepare("$sql");
    $checkData->execute;
    $sbp_data_present = $checkData->rows;
    $checkData->finish;
    
    if ($sbp_data_present > 0) {
      if      ( $jqtr == 1 ) {
        $timeframe     = "date >= '${jyear}-01-01' && date <= '${jyear}-03-31' ";
      } elsif ( $jqtr == 2 ) {
        $timeframe     = "date >= '${jyear}-01-01' && date <= '${jyear}-06-30' ";
      } elsif ( $jqtr == 3 ) {
        $timeframe     = "date >= '${jyear}-01-01' && date <= '${jyear}-09-30' ";
      } elsif ( $jqtr == 4 ) {
        $timeframe     = "date >= '${jyear}-01-01' && date <= '${jyear}-12-31' ";
      }  
      
      $sql = "
      SELECT Plan, 

      #Select Count
      (Brand_Count + Generic_Count) Count, 

      #Select Sales
      (Brand_Sale + Generic_Sale) Sales, 

      #Select Percent, inject total sales number
      (((Brand_Sale + Generic_Sale) / 
        (SELECT sum(Total_Brand_Revenue + Total_Generic_Revenue) 
         FROM $DBNAME.monthly 
         WHERE Pharmacy_ID = $Pharmacy_ID
            && $timeframe
        )
      )*100) Percent, 

      #Select Gross Margin
      ((Brand_Sale + Generic_Sale) - ((Brand_Cost) + (Generic_Cost))) GM, 

      #Select Gross Margin Percent
      ((((Brand_Sale + Generic_Sale) - ((Brand_Cost) + (Generic_Cost)))/(Brand_Sale + Generic_Sale))*100) GM_Percent, 

      #Select Sale Per Script
      ((Brand_Sale + Generic_Sale) / (Brand_Count + Generic_Count)) Sale_Per_Script, 

      #Select Gross Margin Per Script
      (((Brand_Sale + Generic_Sale) - ((Brand_Cost) + (Generic_Cost))) / (Brand_Count + Generic_Count)) GM_Per_Script, 

      #Select Average Day Supply 
      (Days_Supply / (Days_Supply_Count)) Avg_Days_Supply,

      #Select GDR
      (( Generic_Count /(Generic_Count + Brand_Count))*100) GDR_Percent,

      #Select GER
      (((Generic_AWP - Generic_Sale) / Generic_AWP)*100) as GER_Perent

      FROM $DBNAME.sales_by_payer_new 
      WHERE Pharmacy_ID = $Pharmacy_ID
         && Year = $jyear 
         && Qtr_YTD = $jqtr
      ORDER BY (Brand_Sale + Generic_Sale) DESC 
      LIMIT $showPlansMAX";
    
      $getSBPdata = $dbx->prepare("$sql");
      $getSBPdata->execute;
      $SBPNumOfRows = $getSBPdata->rows;
      if ($SBPNumOfRows > 0) {
        my $shown_count = 0;
        my $shown_total = 0;
        my $shown_percent = 0;
        my $shown_gm = 0;
        #print "<table class=\"tableizer-table\">";
        #print "<tr><th>Plan</th><th>Rx Count</th><th>Sales</th><th>% of Sales</th><th>Gross Margin</th><th>GM %</th><th>Sale/ Script</th><th>GM/ Script</th><th>Avg. Days Supply</th></tr>";
        while ( my @row = $getSBPdata->fetchrow_array() ) {
          my ($plan, $count, $sales, $percent, $gm, $gm_percent, $sale_per_script, $gm_per_script, $avg_day_supply, $gdr_percent, $ger_percent) = @row;
          my $count_disp = commify($count);
      
          #Exception to blank out GM values for stores with BAD DATA
          if ($jyear <= 2014 && $NCPDP =~ /1912751|2601993|2586521|2638053|2601917/) {
            $gm = 0;
            $gm_percent = 0;
            $gm_per_script = 0;
          }
      
          #print "<tr><td style=\"text-align: left;\">$plan</td><td>$count_disp</td><td>\$$sales</td><td>$percent%</td><td>\$$gm</td><td>$gm_percent%</td><td>\$$sale_per_script</td><td>\$$gm_per_script</td><td>$avg_day_supply</td></tr>";
          $shown_count   += $count;
          $shown_total   += $sales;
          $shown_percent += $percent;
          $shown_gm      += $gm;
          
          $key = "$jyear##PLAN|$plan";
          $sbpPlan{$key}                 = $plan;
          $sbpRxCount{$key}              = $count;
          $sbpSales{$key}                = $sales;
          $sbpPercentSales{$key}         = $percent;
          $sbpGrossMargin{$key}          = $gm;
          $sbpGrossMarginPercent{$key}   = $gm_percent;
          $sbpSalesPerScript{$key}       = $sale_per_script;
          $sbpGrossMarginPerScript{$key} = $gm_per_script;
          $sbpAvgDaysSupply{$key}        = $avg_day_supply;
          $sbpGDRPercent{$key}           = $gdr_percent;
          $sbpGERPercent{$key}           = $ger_percent;
        }
        
        ### Sales, Rebated Cost, Count by year as reported by us.
        $sql = "SELECT SUM( Total_Brand_Revenue + Total_Generic_Revenue) as Sales, 
                       SUM( (CASE 
                               WHEN Rebate_Type = 'P'
                               THEN (Total_Brand_Cost * (1 - Brand_Rebate))
                               ELSE (Total_Brand_Cost * (1 - (Brand_Rebate/Total_Brand_Cost)))
                             END) + (CASE 
                                       WHEN Rebate_Type = 'P'
                                       THEN (Total_Generic_Cost * (1 - Generic_Rebate)) 
                                       ELSE (Total_Generic_Cost * (1 - (Generic_Rebate/Total_Generic_Cost)))
                                     END)
                          ) as Rebated_Cost,
                       SUM( Total_Brand + Total_Generic) as Count,
                       SUM( Total_Generic) as Gen_Count
                  FROM ( SELECT NCPDP, date, date_format(date, '%Y%m') as datef, Total_Brand_Revenue, Total_Generic_Revenue, Total_Brand_Cost, Total_Generic_Cost, Total_Brand, Total_Generic
                           FROM $DBNAME.monthly 
                          WHERE Pharmacy_ID = $Pharmacy_ID
                             && $timeframe 
                       ) pharm 
             LEFT JOIN $DBNAME.rebates rebates 
                    ON ( pharm.NCPDP = rebates.NCPDP && BINARY pharm.datef = BINARY YYYYMM )";
        $getTotalSales = $dbx->prepare("$sql");
        $getTotalSales->execute;
        $NumOfRows = $getTotalSales->rows;
        if ($NumOfRows > 0) {
          while ( my @row = $getTotalSales->fetchrow_array() ) {
            ($total_rx_sales, $total_rx_cost, $total_rx_count, $total_gen_count) = @row;
          }
        }
        $getTotalSales->finish;
      
        ### Use OUR reported numbers for totals, not Sales By Payer actual totals
        $reported_total_gm = $total_rx_sales - $total_rx_cost;
        $total_count = $total_rx_count;
        $total_gm = $reported_total_gm;
      
      
        $total_sale_per_script = sprintf "%.2f", ($total_rx_sales/$total_count);
        $total_gm_per_script   = sprintf "%.2f", ($total_gm/$total_count);
        $total_count           = $total_count;
        $total_gm_percent      = sprintf "%.1f", (($total_gm/$total_rx_sales)*100);
        $ymc_annual_total_rx_sales = $total_rx_sales;
        $total_rx_sales        = sprintf "%.0f", $total_rx_sales;
        $total_gm              = sprintf "%.0f", $total_gm;

        $total_percent         = sprintf "%.1f", (100); #Always 100.0%
        $total_gdr_percent     = sprintf "%.1f", (($total_gen_count/$total_rx_count)*100);
        $total_ger_percent     = ''; #sprintf "%.1f", (($total_gen_count/$total_rx_count)*100);
      
        #Exception to blank out GM values for stores with BAD DATA
        if ($yearcur <= 2014 && $NCPDP =~ /1912751|2601993|2586521|2638053|2601917/) {
          $total_gm = 0;
          $total_gm_percent = 0;
          $total_gm_per_script = 0;
        }
        
        $key = "$jyear##TOTAL";
        $sbpPlan{$key}                 = "TOTAL";
        $sbpRxCount{$key}              = $total_count;
        $sbpSales{$key}                = $total_rx_sales;
        $sbpPercentSales{$key}         = $total_percent;
        $sbpGrossMargin{$key}          = $total_gm;
        $sbpGrossMarginPercent{$key}   = $total_gm_percent;
        $sbpSalesPerScript{$key}       = $total_sale_per_script;
        $sbpGrossMarginPerScript{$key} = $total_gm_per_script;
        #$sbpAvgDaysSupply{$key}        = $xyz;
        $sbpGDRPercent{$key}            = $total_gdr_percent;
        $sbpGERPercent{$key}            = $total_ger_percent;
      
        #Total Row
        #print "<tr><td style=\"text-align: left;\">Totals ($jyear YTD Q$jqtr)</td><td>$total_count</td><td>\$$total_rx_sales</td><td>$total_percent%</td><td>\$$total_gm</td><td>$total_gm_percent%</td><td>\$$total_sale_per_script</td><td>\$$total_gm_per_script</td><td>---</td></tr>";
      
        #print "</table>";
      }
      $getSBPdata->finish;
    }
  }
}

#____________________________________________________________________________

