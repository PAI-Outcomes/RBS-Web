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

#______________________________________________________________________________

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

print "\nProg: $prog &nbsp; &nbsp;<br>Date: $tdate &nbsp; Time: $ttime<P>\n" if ($debug);
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

$ntitle = "Inventory Management for $Pharmacy_Names{$PH_ID}";
print qq#<h1 class="rbsreporting">$ntitle</h1>\n#;

$DBNAME = 'Webinar' if($USER==2182);

$dbx = DBI->connect("DBI:mysql:$DBNAME:$DBHOST",$dbuser,$dbpwd,
        { PrintError => 1, RaiseError => 1, InactiveDestroy => 0 } ) || die "$DBI::errstr";
   
DBI->trace(1) if ($dbitrace);

&displayInventory;

$dbx->disconnect;
 
#______________________________________________________________________________

&MyPharmassessMembersTrailer;

exit(0);

#______________________________________________________________________________

sub displayInventory {
  $starttime = time;
  $tth = time - $starttime;
  
  $lyear = sprintf("%4d", $year-1);
  $DateRangeStart = "${lyear}${smonth}${sday}";
##  $DateRangeStart = "20200101";
  my @startDate = ($lyear, $smonth, $sday);
##  my @startDate = ('2020', '01', '01');
  
  $DateRangeEnd = "${syear}${smonth}${sday}";
##  $DateRangeEnd = "20201231";
  my @endDate = ($syear, $smonth, $sday);
##  my @endDate = ('2020', '12', '31');

  $show_lines = $in{'lines'};
  $timeframe = "$smonth/$sday/$lyear to $smonth/$sday/$syear";
  
  use Date::Calc qw/Delta_Days/;
  $TotalDays = Delta_Days( @startDate, @endDate );

  print "<p>Based on data from $smonth/$sday/$lyear to $smonth/$sday/$syear, showing top $show_lines NDC groups.</p>\n";

  $PharmacyWanted   = $Pharmacy_NCPDPs{$PH_ID};
  
  $Detail           = 'YRBS';   #Claim Detail Data - RBS Database
  $RebateBrand      = 0;	    #Rebate factored later.
  $RebateGeneric    = 0;	    #Rebate factored later.
  $NPIstring        = '';	    #No NPI string.
  $ExcBINstring     = '';       #No BIN exclusion string.

  #Get RBS Reporting data via subroutine
  ( $RxNumbersref, $FillNumbersref, $BGsref, $SALEsref, $COSTsref, $BinNumbersref,
    $DBsref, $CASHorTPPsref, $GMsref, $salecalcsref, $costcalcsref, $DOSsref, $DateTransmittedsref,
    $PCNsref, $Groupsref, $NDCsref, $TCodesref, $Quantitysref, $DaySupplyref, 
    $RCOSTsref, $RGMsref, $PBMsref, $PAI_Payer_Namesref, $Comm_MedD_Medicaidref, 
    $PrescriberIDsref ) =
    &Get_RBSReporting_Data($PharmacyWanted, $DateRangeStart, $DateRangeEnd, $Detail, 
    $RebateBrand, $RebateGeneric, "$NPIstring", "$ExcBINstring" );
  
  $tth = time - $starttime;
  
  #Create hashes for NDC summaries
  %sumSALE = ();
  %sumCOST = ();
  %sumCOUNT = ();
  %sumQUANTITY = ();
  
  %maxDailyQUANTITY = ();
  %maxQUANTITY = ();
  
  %sumDailyAvg = ();
  %sumMAX = ();
  %sumMIN = ();
  %sumBG  = ();
  
  foreach $key (sort keys %$RxNumbersref) {
    $RxNumber   = $RxNumbersref->{$key};
    $FillNumber = $FillNumbersref->{$key};
    $BG         = $BGsref->{$key};
    $SALE       = $SALEsref->{$key};
    $COST       = $COSTsref->{$key};
    $BinNumber  = $BinNumbersref->{$key};
    $DB         = $DBsref->{$key};
    $CASHorTPP  = $CASHorTPPsref->{$key};
    $GM         = $GMsref->{$key};
    $salecalc   = $salecalcsref->{$key};
    $costcalc   = $costcalcsref->{$key};
    $DOS        = $DOSsref->{$key};
    $DateTransmitted = $DateTransmittedsref->{$key};
    $PCN        = $PCNsref->{$key};
    $Group      = $Groupsref->{$key};
    $NDC        = $NDCsref->{$key};
    $TCode      = $TCodesref->{$key};
    $Quantity   = $Quantitysref->{$key};
    $DaySupply  = $DaySupplyref->{$key};
    $RCOST      = $RCOSTsref->{$key}; 
    $RGM        = $RGMsref->{$key};
    $PBM        = $PBMsref->{$key};
    $PAI_Payer_Name = $PAI_Payer_Namesref->{$key};
    $Comm_MedD_Medicaid = $Comm_MedD_Medicaidref->{$key};
    $dbPrescriberID = $PrescriberIDsref->{$key};
		
    $salecalc =~ s/<u>//;
    $salecalc =~ s/<\/u>//;
    $salecalc =~ s/<br \/>/ - /;
	
    #Sum up per NDC values
    if ($NDC > 0 && $NDC =~ /^[0-9]+$/) {
      my $sumKEY = $NDC;
         $sumSALE{$sumKEY} += $SALE;
         $sumCOST{$sumKEY} += $COST;
         $sumQUANTITY{$sumKEY} += $Quantity;
         $sumCOUNT{$sumKEY}++;

      my $j9NDC = substr($sumKEY, 0, 9);
      $sumj9NDC{$sumKEY} = $j9NDC;
    }
	
    my $dailyKEY = "$NDC##$DOS";
    $maxDailyQUANTITY{$dailyKEY} += $Quantity;
  }
  
  $tth = time - $starttime;
  
  #Build string of unique NDCs and get data from MediSpan
  my $NDCstring = '';
  foreach my $sumKEY (keys %sumSALE) {
    $NDCstring .= "$sumKEY,";
  }
  $NDCstring =~ s/,+$//;  
  
  &getMediSpanData($NDCstring);

#  $sql = "DELETE
#            FROM rbsreporting.basic_inventory
#           WHERE pharmacy_id = $PH_ID";
#  $dbx->do($sql) or die $DBI::errstr;
  
  $tth = time - $starttime;
  #print "<p>Time after getMediSpanData: $tth</p>\n";
  #------------------------------------------------------
  
  foreach my $dailyKEY (keys %maxDailyQUANTITY) {
    my ($ndc, $dos) = split ('##', $dailyKEY, 2);
    my $DailyQuantity = $maxDailyQUANTITY{$dailyKEY};
    if ($DailyQuantity > $maxQUANTITY{$ndc}) {
      $maxQUANTITY{$ndc} = $DailyQuantity;
    }
  }
  
  my $save_location = "D:\\RBSDesktop\\Reports\\";
  my $filename = $Pharmacy_NCPDPs{$PH_ID} . "_inventory_report.xlsx";
  
  print qq#<p><img src="/images/icons/xlsx1.png" style="vertical-align: middle"><a href="/Reports/$filename">Download Spreadsheet (XLSX)</a></p>\n#;
  
  $workbook = Excel::Writer::XLSX->new( $save_location.$filename );
  $worksheet = $workbook->add_worksheet();
  $worksheet->set_landscape();
  $worksheet->fit_to_pages( 1, 0 ); #Fit all columns on a single page
  $worksheet->hide_gridlines(0); #0 = Show gridlines
  
  $worksheet->freeze_panes( 1, 0 ); #Freeze first row
  $worksheet->repeat_rows( 0 );    #Print on each page
  
  $pharmacy_name = $Pharmacy_Names{$PH_ID};
  $worksheet->set_header("&L$pharmacy_name - Top $show_lines \nData from $smonth/$sday/$lyear to $smonth/$sday/$syear");
  $worksheet->set_footer("&CPage &P of &N &RName: ___________________________  ");
  
  $format_bold = $workbook->add_format();
  $format_bold->set_bold();
  
  $wrow = 1;
  $worksheet->write( "A$wrow", 'NDC', $format_bold);  
    $worksheet->set_column( 0, 0, 11.3 ); #Col A
  $worksheet->write( "B$wrow", 'Rx Count', $format_bold );  
  $worksheet->write( "C$wrow", 'B/G', $format_bold );  
    $worksheet->set_column( 2, 2, 3.6 ); #Col C
  $worksheet->write( "D$wrow", 'Drug Name', $format_bold ); 
    $worksheet->set_column( 3, 3, 46.6 ); #Col D
  $worksheet->write( "E$wrow", 'Total Cost', $format_bold ); 
    $worksheet->set_column( 4, 4, 12 ); #Col E
  $worksheet->write( "F$wrow", 'Total Qty', $format_bold ); 
  $worksheet->write( "G$wrow", 'Pack. Size', $format_bold ); 
    $worksheet->set_column( 6, 6, 12 ); #Col G  
  $worksheet->write( "H$wrow", 'Daily Avg Qty', $format_bold );  
    $worksheet->set_column( 7, 7, 12 ); #Col H
  $worksheet->write( "I$wrow", 'Max Daily Qty', $format_bold );  
    $worksheet->set_column( 8, 8, 12.3 ); #Col I
  $worksheet->write( "J$wrow", 'MIN', $format_bold ); 
    $worksheet->set_column( 9, 9, 4 ); #Col J  
  $worksheet->write( "K$wrow", 'MAX', $format_bold );  
    $worksheet->set_column( 10, 10, 4 ); #Col K 
  $wrow++;
  
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
  
  $line = 1;
  #Per summed NDC
  foreach $sumKEY (sort { $sumCOST{$b} <=> $sumCOST{$a} } keys %sumCOST) {
  
    last if ($line > $show_lines);
    next if ($seen{$sumKEY});

    &printline($sumKEY, "primary");

    $j9NDC = $sumj9NDC{$sumKEY};
    foreach $KEY (sort { $sumCOST{$b} <=> $sumCOST{$a} } keys %sumCOST) {
       next if ($seen{$KEY});
       if ( $j9NDC == $sumj9NDC{$KEY} ) {
          print "sumKEY: $sumKEY, j9NDC: $j9NDC<br>\n" if ($debug);
          &printline($KEY, "secondary");
       }
    }
	
    $line++;
  }
  
  print "</tbody>\n";
  print "</table>\n"; #End HTML Table
  $workbook->close(); #End XLSX
  
  print qq#<br style="clear: both;" /><br />\n#;
  print qq#<p><i>Please use your own judgement in addition to data provided in this report. Seasonal quantities may vary.</i></p>\n#;
  
  $tth = time - $starttime;
}

#____________________________________________________________________________

sub getMediSpanData {
  my ($NDCstring) = @_;

  %sumDRUG_NAME = ();
  %sumSTRENGTH = ();
  %sumSTRENGTH_UOM = ();
  %sumPACKAGE_SIZE = ();
  %sumPACKAGE_SIZE_UOM = ();
  %sumDOSAGE_FORM = ();
  %sumMSBorG = ();

  # $sql = qq#
  # SELECT ndc_upc_hri, drug_name, strength, strength_unit_of_measure, package_size, package_size_uom, dosage_form
  # FROM medispan.mf2ndc 
  # LEFT JOIN medispan.mf2name 
  # ON mf2ndc.drug_descriptor_id = mf2name.drug_descriptor_id
  # LEFT JOIN medispan.mf2gppc 
  # ON mf2ndc.generic_product_pack_code = mf2gppc.generic_product_pack_code
  # WHERE 
  # ndc_upc_hri IN ($NDCstring)
  # #;
  
  #Use the MSBorG Lookup Table
  $sql = qq#
  SELECT NDC, drug_name, strength, strength_unit_of_measure, package_size, package_size_uom, dosage_form, MSBorG
  FROM officedb.msborg_lookup_table
  WHERE 
  NDC IN ($NDCstring)
  #;

  my $sthx  = $dbx->prepare("$sql");
  $sthx->execute if($NDCstring != '');
  my $NumOfRows = $sthx->rows;

  if ( $NumOfRows > 0 ) {
    while ( my @row = $sthx->fetchrow_array() ) {
      my ($ndc, $drug_name, $strength, $strength_unit_of_measure, $package_size, $package_size_uom, $dosage_form, $MSBorG) = @row;
      $sumDRUG_NAME{$ndc}    = $drug_name;
      $sumSTRENGTH{$ndc}     = $strength;
      $sumSTRENGTH_UOM{$ndc} = $strength_unit_of_measure;
      $sumPACKAGE_SIZE{$ndc} = $package_size;
      $sumPACKAGE_SIZE_UOM{$ndc} = $package_size_uom;
      $sumDOSAGE_FORM{$ndc} = $dosage_form;
      $sumMSBorG{$ndc} = $MSBorG;
    }
  }
}

#____________________________________________________________________________

sub printline {
  my ($sumKEY, $status) = @_;

  $seen{$sumKEY}++;

  #Summary Data
  my $sumSALE = $sumSALE{$sumKEY};
     $sumSALE = sprintf("%.2f", $sumSALE);
  my $sumCOST = $sumCOST{$sumKEY}; 
     $sumCOST = sprintf("%.2f", $sumCOST);
  my $sumQUANTITY = $sumQUANTITY{$sumKEY};
     #$sumQUANTITY = sprintf("%.0f", $sumQUANTITY);
  my $sumCOUNT = $sumCOUNT{$sumKEY};
  my $maxQUANTITY = $maxQUANTITY{$sumKEY};
  
  #MediSpan Data
  my $sumDRUG_NAME = $sumDRUG_NAME{$sumKEY};
  my $sumSTRENGTH = $sumSTRENGTH{$sumKEY};
  my $sumSTRENGTH_UOM = $sumSTRENGTH_UOM{$sumKEY};
  my $sumPACKAGE_SIZE = $sumPACKAGE_SIZE{$sumKEY};
  my $sumPACKAGE_SIZE_UOM = $sumPACKAGE_SIZE_UOM{$sumKEY};
  my $sumDOSAGE_FORM = $sumDOSAGE_FORM{$sumKEY};
  my $sumMSBorG = $sumMSBorG{$sumKEY};
  
  #Calculated Data
  $sumDailyAvg{$sumKEY} = $sumQUANTITY / $TotalDays;
  my $sumDailyAvg = $sumDailyAvg{$sumKEY};
  $sumDailyAvg = sprintf("%.1f", $sumDailyAvg);
  
  #MIN
  my $min = 0;
  my $min_mult = 1.3;
  if ($sumPACKAGE_SIZE >= 500) {
    $min = ( ((($sumQUANTITY/$TotalDays)/$sumPACKAGE_SIZE)+0.25)*2 );
    $min = (int($min + 0.5))/2; #Round to int, then divide by 2
    $min = sprintf("%.1f", $min);
  } else {
    if ($sumPACKAGE_SIZE =~ /^\s*$/) { $sumPACKAGE_SIZE = 1; }
    #print "<p>sumQuantity: $sumQUANTITY || TotalDays: $TotalDays || sumPACKAGE_SIZE: $sumPACKAGE_SIZE</p>\n";
    $min = int( (($sumQUANTITY/$TotalDays)/$sumPACKAGE_SIZE)*$min_mult + 1 );
  }
  $sumMIN{$sumKEY} = $min;
  
  #MAX
  my $max = 0;
  my $max_mult = 4.0;	# jlh. 11/13/2014. Was 3.5

  #$max = int ( ($maxQUANTITY/$sumPACKAGE_SIZE) + .99 );
  
  $max = int( (($sumQUANTITY/$TotalDays)/$sumPACKAGE_SIZE)*$max_mult + 1 );
  $sumMAX{$sumKEY} = $max;
  
  $primary_class = '';
  if ($status =~ /primary/i) {
    #$primary_class = qq#style="background: \#CCC;"#;
  }
  
  $drug_name_concat = $sumDRUG_NAME.' '.$sumSTRENGTH.' '.$sumSTRENGTH_UOM;
  
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
  
  $worksheet->keep_leading_zeros();
  
  $worksheet->write( "A$wrow", $sumKEY, $format_left );  
  $worksheet->write( "B$wrow", $sumCOUNT, $format_number );  
  $worksheet->write( "C$wrow", $sumMSBorG, $format_center );  
  $worksheet->write( "D$wrow", $drug_name_concat ); 
  $worksheet->write( "E$wrow", $sumCOST, $format_money ); 
  $worksheet->write( "F$wrow", $sumQUANTITY, $format_number ); 
  $worksheet->write( "G$wrow", "$sumPACKAGE_SIZE $sumPACKAGE_SIZE_UOM", $format_right );  
  $worksheet->write( "H$wrow", $sumDailyAvg, $format_right );  
  $worksheet->write( "I$wrow", $maxQUANTITY, $format_right );  
  $worksheet->write( "J$wrow", $min, $format_center );  
  $worksheet->write( "K$wrow", $max, $format_center );  
  $wrow++;
  
  print "
  <tr>
  <td $primary_class>$sumKEY</td>
  <td class=\"align_right\">$sumCOUNT</td>
  <td>$sumMSBorG</td>
  <td>$drug_name_concat</td>
  <!-- <td class=\"align_right\">$sumSALE</td> -->
  <td class=\"align_right\">$sumCOST</td>
  <td class=\"align_right\">$sumQUANTITY</td>
  <td>$sumPACKAGE_SIZE $sumPACKAGE_SIZE_UOM</td>
  <td class=\"align_right\">$sumDailyAvg</td>
  <td class=\"align_right\">$maxQUANTITY</td>
  <td class=\"align_center\">$min</td>
  <td class=\"align_center\">$max</td>
  </tr>
  \n";

#  $sql = "INSERT INTO rbsreporting.basic_inventory
#                 (pharmacy_id, timeframe, ndc, rx_count, borg, drug_name, total_cost, total_qty, pack_size, daily_avg_qty, max_daily_qty, minimum, maximum)
#          VALUES ($PH_ID, '$timeframe', '$sumKEY', $sumCOUNT, '$sumMSBorG', '$drug_name_concat', '$sumCOST', '$sumQUANTITY', '$sumPACKAGE_SIZE $sumPACKAGE_SIZE_UOM',
#                  '$sumDailyAvg', '$maxQUANTITY', '$min', '$max')";
#  $dbx->do($sql) or die $DBI::errstr;
}

#____________________________________________________________________________
