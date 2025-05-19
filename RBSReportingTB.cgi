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

$showRows    = $in{'showRows'};

$PayerType   = "PAI_Payer_Name";

($showRows)  = &StripJunk($showRows);

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

$showRows = 10 if (!$showRows);
  
$ntitle = "Top $showRows / Bottom $showRows Payers by GM/Script for $Pharmacy_Names{$inNCPDP}";
print qq#<h1 class="rbsreporting">$ntitle</h1>\n#;
print qq#<p>* This report only considers payers this year YTD with over 1% of sales.</p>\n#;

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
<form name="sbtc" action="$progext" method="post">
<div>

<!-- 
<p>Rows <INPUT TYPE="text" NAME="showRows" SIZE=10 MAXLENGTH=10 VALUE="$showRows">
Payer Type
<SELECT NAME="PayerType">
<OPTION VALUE="PBM">PBM</OPTION>
<OPTION VALUE="PAI_Payer_Name">PAI Payer Name</OPTION>
</SELECT></p>

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
-->

</div>
</form>

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
    
    &buildTable("Top");
    &buildTable("Bot");
  }
}

#____________________________________________________________________________

sub buildTable {
  ($which) = @_;

  %sortPayer    = ();
  
  %tcCount   = ();
  %tcSale    = ();
  %tcGM      = ();
  %tcGMPct   = ();
  %tcDS      = ();
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
    
    $PayerKey     = $$PayerType;

    #Sorting Hashes -------------------------------
    $sortPayer{$PayerKey}     += $SALE;
    
    #Data Hashes ----------------------------------
    $tcCount{$PayerKey}++;
    
    #----------------------------------------------

    $tcSale{$PayerKey} += sprintf("%.2f", $SALE);
    $tcGM{$PayerKey}   += sprintf("%.2f", $RGM);
    
    if ($DaySupply > 0) {
      $tcDS{$PayerKey} += $DaySupply;
      
      $tcDSCount{$PayerKey}++;
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
    font-weight: 500;
    color: \#133562;
  }
  .lvl1:hover td {
    background: \#5FC8ED;
  }
  .lvl1 .tcname {
    padding-left: 3px;
    font-weight: 700;
  }
  
  .lvl2 td {
    background: \#EEE;
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
    color: \#444;
  }
  .lvl3:hover td {
    background: \#c1e7a8;
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
    
    \$("\#myTable_Top").freezeHeader();
    \$("\#myTable_Bot").freezeHeader();
    
  });
  </script>
  #;
  
  my $payer_rowCount   = 0;
  
  #Sort these hashes only ONCE and save to arrays, saves a ton of time in foreach's below.

  my @sortPayer_arr = ();

# my @sortPayer_arr    = sort {$sortPayer{$b}    <=> $sortPayer{$a}    } keys %sortPayer;
  if ( $which =~ /Top/i ) {
     @sortPayer_arr = sort {
       ( $tcGM{$b}/$tcCount{$b}) <=> ($tcGM{$a}/$tcCount{$a} )
       } keys %sortPayer;
       $id = "myTable_Top";
  } else {
     @sortPayer_arr = sort {
       ( $tcGM{$a}/$tcCount{$a}) <=> ($tcGM{$b}/$tcCount{$b} )
       } keys %sortPayer;
       $id = "myTable_Bot";
  }
  
  print qq#<table class="gridView" id="$id">\n#;

  print qq#<thead>\n#;
  print qq#<tr valign=top>#;
  print qq#<th>$which $showRows Payers</th>\n#;
  print qq#<th>Rx Count</th>\n#;
  print qq#<th>Sales</th>\n#;
  print qq#<th>% of Sales</th>\n#;
  print qq#<th>Gross Margin</th>\n#;
  print qq#<th>GM %</th>\n#;
  print qq#<th>Sale/ Script</th>\n#;
  print qq#<th>GM/ Script</th>\n#;
  print qq#<th>Avg Days Supply</th>\n#;
  print qq#</tr>#;
  print qq#</thead>\n#;
  
  print qq#<tbody>\n#;
  
  foreach $sortPayerKey (@sortPayer_arr)  {
    
    my $name            = $sortPayerKey;
    my $count           = $tcCount{$sortPayerKey};
    my $sales           = sprintf("%.2f", $tcSale{$sortPayerKey});
    my $sales_percent   = sprintf("%.2f", ($sales / $totalSales)*100);
    next if ( $sales_percent < 1 );

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
#     $payer_rowCount++;
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
#     print qq#<td class="align_right">BOB 1</td>\n#;
      print qq#</tr>#;
      
    } else {
#     $payer_rowCount++;
      $payer_count_other           += $count;
      $payer_sales_other           += $sales;
      $payer_sales_percent_other   += $sales_percent;
      $payer_gm_other              += $gm;
    }
    
    $payer_rowCount++;
    $payer_count_total           += $count;
    $payer_sales_total           += $sales;
    $payer_sales_percent_total   += $sales_percent;
    $payer_gm_total              += $gm;
    
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
    print qq#<td class="align_left tcname">Other</td>\n#;
    print qq#<td class="align_right">$payer_count_other</td>\n#;
    print qq#<td class="align_right">$payer_sales_other</td>\n#;
    print qq#<td class="align_right">$payer_sales_percent_other</td>\n#;
    print qq#<td class="align_right">$payer_gm_other</td>\n#;
    print qq#<td class="align_right">$payer_gm_percent_other</td>\n#;
    print qq#<td class="align_right">$payer_sale_per_script_other</td>\n#;
    print qq#<td class="align_right">$payer_gm_per_script_other</td>\n#;
    print qq#<td class="align_right">&nbsp;</td>\n#;
#   print qq#<td class="align_right">BOB 6</td>\n#;
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
#	  
#	  #TOTAL line for PAYER level
#	  print qq#<tr class="lvl1 other">#;
#	  print qq#<td class="align_left tcname">Total</td>\n#;
#	  print qq#<td class="align_right">$payer_count_total</td>\n#;
#	  print qq#<td class="align_right">$payer_sales_total</td>\n#;
#	  print qq#<td class="align_right">$payer_sales_percent_total</td>\n#;
#	  print qq#<td class="align_right">$payer_gm_total</td>\n#;
#	  print qq#<td class="align_right">$payer_gm_percent_total</td>\n#;
#	  print qq#<td class="align_right">$payer_sale_per_script_total</td>\n#;
#	  print qq#<td class="align_right">$payer_gm_per_script_total</td>\n#;
#	  print qq#<td class="align_right">&nbsp;</td>\n#;
#	# print qq#<td class="align_right">BOB 7</td>\n#;
#	  print qq#</tr>#;
#	  
  print qq#</tbody>\n#;
  
  print "</table>\n";

  $tth = time - $starttime;
  print "<p><hr />Time after buildTable: $tth second(s)<hr /></p>\n" if ($showTTH);
}

#____________________________________________________________________________
