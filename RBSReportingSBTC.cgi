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

$DSTART = sprintf("%04d%02d%02d", $year, 1, 1);
$DEND   = sprintf("%04d%02d%02d", $year, $month, $day);

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

$progext = "${prog}${ext}";

$ntitle = "Sales By Therapeutic Class for $Pharmacy_Names{$inNCPDP}";
print qq#<h1 class="rbsreporting">$ntitle</h1>\n#;
print qq#<p>* This report uses data from this year YTD.</p>\n#;

$dbx = DBI->connect("DBI:mysql:$DBNAME:$DBHOST",$dbuser,$dbpwd,
        { PrintError => 1, RaiseError => 1, InactiveDestroy => 0 } ) || die "$DBI::errstr";
   
DBI->trace(1) if ($dbitrace);

#Additional Includes
print qq#
<link rel="stylesheet" href="https://code.jquery.com/ui/1.10.3/themes/smoothness/jquery-ui.css" />
<script src="https://code.jquery.com/ui/1.10.3/jquery-ui.js"></script>
#;

print qq#
<script>
\$(function(){ 
  \$( ".datepicker" ).datepicker({maxDate: '0'});
});
</script>
#;

print qq#
<!--
<form name="sbtc" action="$progext" method="post">
<div>

<div style="float: left; margin: 0 15px 10px 0;">
<p>Date Start</p>
<INPUT class="cipn-input-text-form required datepicker" TYPE="text" NAME="inDateRangeStart" VALUE="$in{'inDateRangeStart'}" readonly="readonly">
</div>

<div style="float: left; margin: 0 15px 10px 0;">
<p>Date End</p>
<INPUT class="cipn-input-text-form required datepicker" TYPE="text" NAME="inDateRangeEnd" VALUE="$in{'inDateRangeEnd'}" readonly="readonly">
</div>

<div style="clear: both;"></div>

<INPUT TYPE="submit" VALUE="Submit" />

</div>
</form>
-->

<hr />
#;

$DateRangeStart = $DSTART;
$DateRangeEnd   = $DEND;

if ($DateRangeStart > 0 && $DateRangeEnd > 0) {
  &getData($DateRangeStart, $DateRangeEnd);
}

$dbx->disconnect;
 
#______________________________________________________________________________

&MyPharmassessMembersTrailer;

exit(0);

#______________________________________________________________________________

sub getData {
  my ($DateRangeStart, $DateRangeEnd) = @_;

  $starttime = time;
  $tth = time - $starttime;
  print "<p><hr />Time at entry of getData: $tth second(s)<hr /></p>\n" if ($showTTH);
  
  $PharmacyWanted   = $Pharmacy_NCPDPs{$PH_ID};
  
  $Detail           = 'YRBS'; #Claim Detail Data - RBS Database
  $RebateBrand      = 0;	    #Rebate factored later.
  $RebateGeneric    = 0;	    #Rebate factored later.
  $NPIstring        = '';	    #No NPI string.
  $ExcBINstring     = '';     #No BIN exclusion string.

  #Get RBS Reporting data via subroutine
  ( $RxNumbersref, $FillNumbersref, $BGsref, $SALEsref, $COSTsref, $BinNumbersref,
    $DBsref, $CASHorTPPsref, $GMsref, $salecalcsref, $costcalcsref, $DOSsref, $DateTransmittedsref,
    $PCNsref, $Groupsref, $NDCsref, $TCodesref, $Quantitysref, $DaySupplyref, 
    $RCOSTsref, $RGMsref, $PBMsref, $PAI_Payer_Namesref, $Comm_MedD_Medicaidref, 
    $PrescriberIDsref ) =
    &Get_RBSReporting_Data($PharmacyWanted, $DateRangeStart, $DateRangeEnd, $Detail, 
    $RebateBrand, $RebateGeneric, "$NPIstring", "$ExcBINstring" );
  
  @NDCs = ();
  
  $totalSales = 0;
  
  my $rows = 0;
  
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
    
    $totalSales += $SALE;
    
    push(@NDCs, $NDC); 
		
    $rows++;
  }
  
  $tth = time - $starttime;
  print "<p><hr />Time after RBS data pull foreach: $tth second(s)<hr /></p>\n" if ($showTTH);
  
  if ( $rows > 0 && $PH_ID > 0 ) {
    #Build string of unique NDCs and get data from MediSpan
    $NDCstring = '';
    my @uniqueNDCs = do { my %seen; grep { !$seen{$_}++ } @NDCs };
    foreach my $NDC (@uniqueNDCs) {
      $NDCstring .= "$NDC,";
    }
    $NDCstring =~ s/,+$//;  
    &getMediSpanTCData($NDCstring);
    
    &buildTable();
  }
}

#____________________________________________________________________________

sub getMediSpanTCData {
  my ($NDCstring) = @_;

  %msDRUG_NAME = ();
  %msSTRENGTH = ();
  %msSTRENGTH_UOM = ();
  %msDOSAGE_FORM = ();
  %msTCLVL01 = ();
  %msTCLVL02 = ();

  $sql = qq#
  SELECT ndc_upc_hri, drug_name, strength, strength_unit_of_measure, dosage_form, gpi02.tcgpi_name, gpi10.tcgpi_name
  FROM medispan.mf2ndc 
  LEFT JOIN medispan.mf2name 
    ON mf2ndc.drug_descriptor_id = mf2name.drug_descriptor_id
  LEFT JOIN medispan.mf2tcgpi gpi02
    ON SUBSTR(mf2name.generic_product_identifier,1,2) = gpi02.tcgpi_id
    && gpi02.tc_level_code = 02
  LEFT JOIN medispan.mf2tcgpi gpi10
    ON SUBSTR(mf2name.generic_product_identifier,1,10) = gpi10.tcgpi_id
    && gpi10.tc_level_code = 10
  WHERE 
  ndc_upc_hri IN ($NDCstring)
  #;
  
  #Use the MSBorG Lookup Table
  # $sql = qq#
  # SELECT NDC, drug_name, strength, strength_unit_of_measure, package_size, package_size_uom, dosage_form, MSBorG
  # FROM officedb.msborg_lookup_table
  # WHERE 
  # NDC IN ($NDCstring)
  ;

  my $sthx  = $dbx->prepare("$sql");
  $sthx->execute;
  my $NumOfRows = $sthx->rows;

  if ( $NumOfRows > 0 ) {
    while ( my @row = $sthx->fetchrow_array() ) {
      my ($ndc, $drug_name, $strength, $strength_unit_of_measure, $dosage_form, $TClvl01, $TClvl02) = @row;
      $msDRUG_NAME{$ndc}    = $drug_name;
      $msSTRENGTH{$ndc}     = $strength;
      $msSTRENGTH_UOM{$ndc} = $strength_unit_of_measure;
      $msDOSAGE_FORM{$ndc}  = $dosage_form;
      
      $TClvl01 =~ s/\*|\.//g;  
      $TClvl02 =~ s/\*|\.//g;  
      
      $msTCLVL01{$ndc}      = $TClvl01;
      $msTCLVL02{$ndc}      = $TClvl02;

      #print "<p>$ndc | $TClvl01 | $TClvl02</p>\n";
    }
  }
  
  $tth = time - $starttime;
  print "<p><hr />Time after getMediSpanTCData: $tth second(s)<hr /></p>\n" if ($showTTH);
}

#____________________________________________________________________________

sub buildTable {
  %sortPayer   = ();
  %sortTClvl01   = ();
  %sortTClvl02   = ();
  
  %tcCount = ();
  %tcSale  = ();
  %tcGM    = ();
  %tcGMPct = ();
  %tcDS = ();
  %tcDSCount = ();

  foreach $key (sort keys %$SALEsref) {
    $BG         = $BGsref->{$key};
    $SALE       = $SALEsref->{$key};
    $COST       = $COSTsref->{$key};
    $BinNumber  = $BinNumbersref->{$key};
    $GM         = $GMsref->{$key};
    $NDC        = $NDCsref->{$key};
    $Quantity   = $Quantitysref->{$key};
    $DaySupply  = $DaySupplyref->{$key};
    $RCOST      = $RCOSTsref->{$key}; 
    $RGM        = $RGMsref->{$key};
    $PBM        = $PBMsref->{$key};
    $PAI_Payer_Name = $PAI_Payer_Namesref->{$key};
    
    #$PBM =~ /^\Q$PBM\E/;
    #print "<p>PBM: $PBM</p>\n";
    
    #Tied in via &getMediSpanTCData
    my $TClvl01 = $msTCLVL01{$NDC};
    my $TClvl02 = $msTCLVL02{$NDC};
    
    my $PayerKey     = $PBM;
    my $TClvl01Key   = "$PayerKey##$TClvl01";
    my $TClvl02Key   = "$PayerKey##$TClvl01##$TClvl02";
    
    #Sorting Hashes -------------------------------
    $sortPayer{$PayerKey}     += $SALE;
    $sortTClvl01{$TClvl01Key} += $SALE;
    $sortTClvl02{$TClvl02Key} += $SALE;
    
    #Data Hashes ----------------------------------
    $tcCount{$PayerKey}++;
    $tcCount{$TClvl01Key}++;
    $tcCount{$TClvl02Key}++;
    
    $tcSale{$PayerKey}   += sprintf("%.2f", $SALE);
    $tcSale{$TClvl01Key} += sprintf("%.2f", $SALE);
    $tcSale{$TClvl02Key} += sprintf("%.2f", $SALE);
    
    $tcGM{$PayerKey}   += sprintf("%.2f", $RGM);
    $tcGM{$TClvl01Key} += sprintf("%.2f", $RGM);
    $tcGM{$TClvl02Key} += sprintf("%.2f", $RGM);
    
    if ($DaySupply > 0) {
      $tcDS{$PayerKey}   += $DaySupply;
      $tcDS{$TClvl01Key} += $DaySupply;
      $tcDS{$TClvl02Key} += $DaySupply;
      
      $tcDSCount{$PayerKey}++;
      $tcDSCount{$TClvl01Key}++;
      $tcDSCount{$TClvl02Key}++;
    }
  }
  
  print qq#
  <style>
  
  .gridView {
    clear: both;
    margin: 10px 0;
    border: medium none !important;
    border-collapse: collapse;
  }
  .gridView thead tr {
    background: \#fff url(../images/bg-header-grid.png) bottom repeat-x;
    /* background: \#fff; */
    opacity: 0.92;
  }
  .gridView thead tr th {
    z-index: 999;
  }
  
  .lvl1 td {
    background: \#5FC8ED;
    font-weight: 500;
    color: \#FFF;
    border-right: 1px solid \#CCC;
  }
  .lvl1:hover td {
    background: \#30b7e8;
  }
  .lvl1 .tcname {
    padding-left: 3px;
    font-weight: 700;
  }
  
  .lvl2 td {
    background: \#f2f2f2;
    cursor: pointer;
    border-right: 1px solid \#CCC;
  }
  .lvl2 .tcname {
    padding-left: 5px;
  }
  .lvl2.other .tcname {
    padding-left: 27px;
  }
  .lvl2:hover td {
    background: \#dbdbdb;
  }
  
  .lvl3 td {
    background: \#FFF;
    border-right: 1px solid \#CCC;
  }
  .lvl3:hover td {
    background: \#5FC8ED;
  }
  .lvl3 .tcname {
    padding-left: 27px;
  }
  .lvl3.other .tcname {
    padding-left: 47px;
  }
  
  .other td {
    font-style: italic;
  }
  
  </style>
  #;
  
  #Additional Includes
  print qq#
  <link rel="stylesheet" href="https://code.jquery.com/ui/1.10.3/themes/smoothness/jquery-ui.css" />
  <script src="https://code.jquery.com/ui/1.10.3/jquery-ui.js"></script>
  <script src="/includes/jquery.freezeheader.js"></script>
  #;
  
  print qq#
  <script>
  \$(function(){
  
    \$(".lvl3").hide();
    
    \$(".lvl2_toggle").click(function (e) {
      e.stopPropagation();
      \$(this).nextUntil('.lvl2').toggle();
    });
    
    \$("\#mytable").freezeHeader();
    
  });
  </script>
  #;
  
  my $showRows         = 5;
  
  my $payer_rowCount   = 0;
  my $tclvl01_rowCount = 0;
  my $tclvl02_rowCount = 0;
  
  #Sort these hashes only ONCE and save to arrays, saves a ton of time in foreach's below.
  my @sortPayer_arr   = sort {$sortPayer{$b}   <=> $sortPayer{$a}  } keys %sortPayer;
  my @sortTClvl01_arr = sort {$sortTClvl01{$b} <=> $sortTClvl01{$a}} keys %sortTClvl01;
  my @sortTClvl02_arr = sort {$sortTClvl02{$b} <=> $sortTClvl02{$a}} keys %sortTClvl02;
  
  print qq#<table class="gridView" id="mytable">\n#;

  print qq#<thead>\n#;
  print qq#<tr>#;
  print qq#<th>&nbsp;</th>\n#;
  print qq#<th>Rx Count</th>\n#;
  print qq#<th>Sales</th>\n#;
  print qq#<th>% of Sales</th>\n#;
  print qq#<th>Gross Margin</th>\n#;
  print qq#<th>GM %</th>\n#;
  print qq#<th>Sale/ Script</th>\n#;
  print qq#<th>GM/ Script</th>\n#;
  print qq#<th>Avg. Days Supply</th>\n#;
  print qq#</tr>#;
  print qq#</thead>\n#;
  
  print qq#<tbody>\n#;
  
  foreach $sortPayerKey (@sortPayer_arr) {
    #print "<p>$sortPayerKey | $sortPayer{$sortPayerKey}</p>\n";
    
    my $name            = $sortPayerKey;
    my $count           = $tcCount{$sortPayerKey};
    my $sales           = sprintf("%.2f", $tcSale{$sortPayerKey});
    my $sales_percent   = sprintf("%.2f", ($sales / $totalSales)*100);
    my $gm              = sprintf("%.2f", $tcGM{$sortPayerKey});
    my $gm_percent = 0;
    if ($sales != 0) {
      $gm_percent      = sprintf("%.2f", ($gm / $sales)*100);
    }
    my $sale_per_script = sprintf("%.2f", ($sales / $count));
    my $gm_per_script   = sprintf("%.2f", ($gm / $count));
    my $avg_days_supply = 0;
    if ( $tcDSCount{$sortPayerKey} != 0 ) {
      $avg_days_supply = sprintf("%.2f", ($tcDS{$sortPayerKey} / $tcDSCount{$sortPayerKey}));
    }
    
    $count_disp = commify($count);
    $sales_disp = commify($sales);
    $gm_disp    = commify($gm);
    $sale_per_script_disp = commify($sale_per_script);
    $gm_per_script_disp   = commify($gm_per_script);
    
    if ( $payer_rowCount < $showRows && $sortPayerKey !~ /^\s*$/) {
      $payer_rowCount++;
      print qq#<tr class="lvl1">#;
      print qq#<td class="align_left tcname">$name</td>\n#;
      print qq#<td class="align_right">$count_disp</td>\n#;
      print qq#<td class="align_right">$sales_disp</td>\n#;
      print qq#<td class="align_right">$sales_percent</td>\n#;
      print qq#<td class="align_right">$gm_disp</td>\n#;
      print qq#<td class="align_right">$gm_percent</td>\n#;
      print qq#<td class="align_right">$sale_per_script_disp</td>\n#;
      print qq#<td class="align_right">$gm_per_script_disp</td>\n#;
      print qq#<td class="align_right">$avg_days_supply</td>\n#;
      print qq#</tr>#;
      
      $tclvl01_rowCount = 0;
      
    } else {
      $payer_rowCount++;
      $payer_count_other           += $count;
      $payer_sales_other           += $sales;
      $payer_sales_percent_other   += $sales_percent;
      $payer_gm_other              += $gm;
    }
    
    #$payer_rowCount++;
    $payer_count_total           += $count;
    $payer_sales_total           += $sales;
    $payer_sales_percent_total   += $sales_percent;
    $payer_gm_total              += $gm;
    
    
    foreach $sortTClvl01Key (@sortTClvl01_arr) {
      next if ( $sortTClvl01Key !~ /^\Q$sortPayerKey\E/);

      my $rowCount++;
      #print "<p>&nbsp; &nbsp; &nbsp; $sortTClvl01Key | $sortTClvl01{$sortTClvl01Key}</p>\n";
      
      my @pcs = split('##', $sortTClvl01Key);

      my $name            = pop(@pcs);
      my $count           = $tcCount{$sortTClvl01Key};
      my $sales           = sprintf("%.2f", $tcSale{$sortTClvl01Key});
      my $sales_percent   = sprintf("%.2f", ($sales / $totalSales)*100);
      my $gm              = sprintf("%.2f", $tcGM{$sortTClvl01Key});
      my $gm_percent = 0;
      if ($sales != 0) {
        $gm_percent       = sprintf("%.2f", ($gm / $sales)*100);
      }
      my $sale_per_script = sprintf("%.2f", ($sales / $count));
      my $gm_per_script   = sprintf("%.2f", ($gm / $count));
      my $avg_days_supply = 0;
      if ( $tcDSCount{$sortTClvl01Key} != 0 ) {
        $avg_days_supply = sprintf("%.2f", ($tcDS{$sortTClvl01Key} / $tcDSCount{$sortTClvl01Key}));
      }
      
      $count_disp = commify($count);
      $sales_disp = commify($sales);
      $gm_disp    = commify($gm);
      $sale_per_script_disp = commify($sale_per_script);
      $gm_per_script_disp   = commify($gm_per_script);
      
      if ( $tclvl01_rowCount < $showRows && $sortTClvl01Key !~ /##$/) {
        $tclvl01_rowCount++;
        print qq#<tr class="lvl2 lvl2_toggle">#;
        print qq#
        <td class="align_left tcname ">
          <div style="float: left;">
            <img src="/images/icons/arrow_right_from_top.png" style="max-width: 16px;" />
          </div>
          <div style="margin-left: 22px;">$name</div>
          <div style="clear: both;"></div>
          </td>
        \n#;
        print qq#<td class="align_right">$count_disp</td>\n#;
        print qq#<td class="align_right">$sales_disp</td>\n#;
        print qq#<td class="align_right">$sales_percent</td>\n#;
        print qq#<td class="align_right">$gm_disp</td>\n#;
        print qq#<td class="align_right">$gm_percent</td>\n#;
        print qq#<td class="align_right">$sale_per_script_disp</td>\n#;
        print qq#<td class="align_right">$gm_per_script_disp</td>\n#;
        print qq#<td class="align_right">$avg_days_supply</td>\n#;
        print qq#</tr>#;
        
        $tclvl02_rowCount = 0;
        
      } else {
        $tclvl01_rowCount++;
        $tclvl01_count_other           += $count;
        $tclvl01_sales_other           += $sales;
        $tclvl01_sales_percent_other   += $sales_percent;
        $tclvl01_gm_other              += $gm;
      }
      

      foreach $sortTClvl02Key (@sortTClvl02_arr) {
        next if ( $sortTClvl02Key !~ /^\Q$sortTClvl01Key\E/);

        #print "<p>&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; $sortTClvl02Key | $sortTClvl02{$sortTClvl02Key}</p>\n";
        
        my @pcs = split('##', $sortTClvl02Key);
        
        my $name            = pop(@pcs);
        my $count           = $tcCount{$sortTClvl02Key};
        my $sales           = sprintf("%.2f", $tcSale{$sortTClvl02Key});
        my $sales_percent   = sprintf("%.2f", ($sales / $totalSales)*100);
        my $gm              = sprintf("%.2f", $tcGM{$sortTClvl02Key});
        my $gm_percent = 0;
        if ($sales != 0) {
          $gm_percent       = sprintf("%.2f", ($gm / $sales)*100);
        }
        my $sale_per_script = sprintf("%.2f", ($sales / $count));
        my $gm_per_script   = sprintf("%.2f", ($gm / $count));
        my $avg_days_supply = 0;
        if ( $tcDSCount{$sortTClvl02Key} != 0 ) {
          $avg_days_supply = sprintf("%.2f", ($tcDS{$sortTClvl02Key} / $tcDSCount{$sortTClvl02Key}));
        }
        
        $count_disp = commify($count);
        $sales_disp = commify($sales);
        $gm_disp    = commify($gm);
        $sale_per_script_disp = commify($sale_per_script);
        $gm_per_script_disp   = commify($gm_per_script);
        
        if ( $tclvl02_rowCount < $showRows && $sortTClvl02Key !~ /##$/
          && $tclvl01_rowCount <= $showRows
        ) {
          $tclvl02_rowCount++;
          print qq#<tr class="lvl3">#;
          #print qq#<td class="align_left tcname">$name</td>\n#;
          
          #opacity: 0.5;
          print qq#
          <td class="align_left tcname ">
            <div style="float: left;">
              <img src="/images/icons/arrow_right_from_top.png" style="max-width: 16px;" />
            </div>
            <div style="margin-left: 22px;">$name</div>
            <div style="clear: both;"></div>
            </td>
          \n#;
          
          print qq#<td class="align_right">$count_disp</td>\n#;
          print qq#<td class="align_right">$sales_disp</td>\n#;
          print qq#<td class="align_right">$sales_percent</td>\n#;
          print qq#<td class="align_right">$gm_disp</td>\n#;
          print qq#<td class="align_right">$gm_percent</td>\n#;
          print qq#<td class="align_right">$sale_per_script_disp</td>\n#;
          print qq#<td class="align_right">$gm_per_script_disp</td>\n#;
          print qq#<td class="align_right">$avg_days_supply</td>\n#;
          print qq#</tr>#;
        } else {
          $tclvl02_rowCount++;
          $tclvl02_count_other           += $count;
          $tclvl02_sales_other           += $sales;
          $tclvl02_sales_percent_other   += $sales_percent;
          $tclvl02_gm_other              += $gm;
        }
          

        
      } #End @sortTClvl02_arr foreach
      
      if ($tclvl01_rowCount <= $showRows && $tclvl02_count_other > 0) {
      
        $tclvl02_sales_percent_other = sprintf("%.2f", $tclvl02_sales_percent_other);
        $tclvl02_gm_other = sprintf("%.2f", $tclvl02_gm_other);
        if ( $tclvl02_sales_other != 0 ) {
          $tclvl02_gm_percent_other = sprintf("%.2f", ($tclvl02_gm_other / $tclvl02_sales_other)*100);
        }
        if ( $tclvl02_count_other != 0 ) {
          $tclvl02_sale_per_script_other = sprintf("%.2f", ($tclvl02_sales_other / $tclvl02_count_other));
          $tclvl02_gm_per_script_other = sprintf("%.2f", ($tclvl02_gm_other / $tclvl02_count_other));
        }
        
        $tclvl02_count_other = commify($tclvl02_count_other);
        $tclvl02_sales_other = commify(sprintf("%.2f",$tclvl02_sales_other));
        $tclvl02_gm_other    = commify($tclvl02_gm_other);
        $tclvl02_sale_per_script_other = commify($tclvl02_sale_per_script_other);
        $tclvl02_gm_per_script_other   = commify($tclvl02_gm_per_script_other);
      
        #OTHER line for TClvl02 level
        print qq#<tr class="lvl3 other">#;
        print qq#<td class="align_left tcname">Other ($name)</td>\n#;
        print qq#<td class="align_right">$tclvl02_count_other</td>\n#;
        print qq#<td class="align_right">$tclvl02_sales_other</td>\n#;
        print qq#<td class="align_right">$tclvl02_sales_percent_other</td>\n#;
        print qq#<td class="align_right">$tclvl02_gm_other</td>\n#;
        print qq#<td class="align_right">$tclvl02_gm_percent_other</td>\n#;
        print qq#<td class="align_right">$tclvl02_sale_per_script_other</td>\n#;
        print qq#<td class="align_right">$tclvl02_gm_per_script_other</td>\n#;
        print qq#<td class="align_right">&nbsp;</td>\n#;
        print qq#</tr>#;
      }
      
      $tclvl02_count_other           = 0;
      $tclvl02_sales_other           = 0;
      $tclvl02_sales_percent_other   = 0;
      $tclvl02_gm_other              = 0;
    
    } #End @sortTClvl01_arr foreach
    

    if ($payer_rowCount <= $showRows && $tclvl01_count_other > 0) {
    
      $tclvl01_sales_percent_other = sprintf("%.2f", $tclvl01_sales_percent_other);
      $tclvl01_gm_other = sprintf("%.2f", $tclvl01_gm_other);
      if ( $tclvl01_sales_other != 0 ) {
        $tclvl01_gm_percent_other = sprintf("%.2f", ($tclvl01_gm_other / $tclvl01_sales_other)*100);
      }
      if ( $tclvl01_count_other != 0 ) {
        $tclvl01_sale_per_script_other = sprintf("%.2f", ($tclvl01_sales_other / $tclvl01_count_other));
        $tclvl01_gm_per_script_other = sprintf("%.2f", ($tclvl01_gm_other / $tclvl01_count_other));
      }
      
      $tclvl01_count_other = commify($tclvl01_count_other);
      $tclvl01_sales_other = commify(sprintf("%.2f",$tclvl01_sales_other));
      $tclvl01_gm_other    = commify($tclvl01_gm_other);
      $tclvl01_sale_per_script_other = commify($tclvl01_sale_per_script_other);
      $tclvl01_gm_per_script_other   = commify($tclvl01_gm_per_script_other);
    
      #OTHER line for TClvl01 level
      print qq#<tr class="lvl2 other">#;
      print qq#<td class="align_left tcname">Other ($name)</td>\n#;
      print qq#<td class="align_right">$tclvl01_count_other</td>\n#;
      print qq#<td class="align_right">$tclvl01_sales_other</td>\n#;
      print qq#<td class="align_right">$tclvl01_sales_percent_other</td>\n#;
      print qq#<td class="align_right">$tclvl01_gm_other</td>\n#;
      print qq#<td class="align_right">$tclvl01_gm_percent_other</td>\n#;
      print qq#<td class="align_right">$tclvl01_sale_per_script_other</td>\n#;
      print qq#<td class="align_right">$tclvl01_gm_per_script_other</td>\n#;
      print qq#<td class="align_right">&nbsp;</td>\n#;
      print qq#</tr>#;
    }
    
    $tclvl01_count_other           = 0;
    $tclvl01_sales_other           = 0;
    $tclvl01_sales_percent_other   = 0;
    $tclvl01_gm_other              = 0;
    
  } #End @sortPayer_arr foreach
  
  
  if ($payer_count_other > 0) {
  
    $payer_sales_percent_other = sprintf("%.2f", $payer_sales_percent_other);
    $payer_gm_other = sprintf("%.2f", $payer_gm_other);
    if ( $payer_sales_other != 0 ) {
      $payer_gm_percent_other = sprintf("%.2f", ($payer_gm_other / $payer_sales_other)*100);
    }
    if ( $payer_count_other != 0 ) {
      $payer_sale_per_script_other = sprintf("%.2f", ($payer_sales_other / $payer_count_other));
      $payer_gm_per_script_other = sprintf("%.2f", ($payer_gm_other / $payer_count_other));
    }
    
    $payer_count_other = commify($payer_count_other);
    $payer_sales_other = commify(sprintf("%.2f",$payer_sales_other));
    $payer_gm_other    = commify($payer_gm_other);
    $payer_sale_per_script_other = commify($payer_sale_per_script_other);
    $payer_gm_per_script_other   = commify($payer_gm_per_script_other);
  
    #OTHER line for PAYER level
    print qq#<tr class="lvl1 other">#;
    print qq#<td class="align_left tcname">Other (Overall)</td>\n#;
    print qq#<td class="align_right">$payer_count_other</td>\n#;
    print qq#<td class="align_right">$payer_sales_other</td>\n#;
    print qq#<td class="align_right">$payer_sales_percent_other</td>\n#;
    print qq#<td class="align_right">$payer_gm_other</td>\n#;
    print qq#<td class="align_right">$payer_gm_percent_other</td>\n#;
    print qq#<td class="align_right">$payer_sale_per_script_other</td>\n#;
    print qq#<td class="align_right">$payer_gm_per_script_other</td>\n#;
    print qq#<td class="align_right">&nbsp;</td>\n#;
    print qq#</tr>#;
    
  }
  
  #$payer_sales_percent_total = sprintf("%.2f", $payer_sales_percent_total);
  $payer_sales_percent_total = sprintf("%.2f", 100);
  $payer_gm_total = sprintf("%.2f", $payer_gm_total);
  if ( $payer_sales_total > 0 ) {
    $payer_gm_percent_total = sprintf("%.2f", ($payer_gm_total / $payer_sales_total)*100);
  }
  if ( $payer_count_total > 0 ) {
    $payer_sale_per_script_total = sprintf("%.2f", ($payer_sales_total / $payer_count_total));
    $payer_gm_per_script_total = sprintf("%.2f", ($payer_gm_total / $payer_count_total));
  }
  
  $payer_count_total = commify($payer_count_total);
  $payer_sales_total = commify($payer_sales_total);
  $payer_gm_total    = commify($payer_gm_total);
  $payer_sale_per_script_total = commify($payer_sale_per_script_total);
  $payer_gm_per_script_total   = commify($payer_gm_per_script_total);
  
  print qq#<tr class=""><td colspan=9>&nbsp;</td></tr>#;
  
  #TOTAL line for PAYER level
  print qq#<tr class="lvl1 other">#;
  print qq#<td class="align_left tcname">Total (Overall)</td>\n#;
  print qq#<td class="align_right">$payer_count_total</td>\n#;
  print qq#<td class="align_right">$payer_sales_total</td>\n#;
  print qq#<td class="align_right">$payer_sales_percent_total</td>\n#;
  print qq#<td class="align_right">$payer_gm_total</td>\n#;
  print qq#<td class="align_right">$payer_gm_percent_total</td>\n#;
  print qq#<td class="align_right">$payer_sale_per_script_total</td>\n#;
  print qq#<td class="align_right">$payer_gm_per_script_total</td>\n#;
  print qq#<td class="align_right">&nbsp;</td>\n#;
  print qq#</tr>#;
  
  print qq#</tbody>\n#;
  
  print "</table>\n";
  
  
  $tth = time - $starttime;
  print "<p><hr />Time after buildTable: $tth second(s)<hr /></p>\n" if ($showTTH);
}

#____________________________________________________________________________


