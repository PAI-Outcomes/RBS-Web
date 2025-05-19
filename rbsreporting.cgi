require "D:/RedeemRx/MyData/RBSDesktop_routines.pl";
require "D:/RedeemRx/cgi-bin/cgi-lib.pl";

use File::Basename;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use Env qw(PATH REMOTE_ADDR PERL5LIB PERLLIB);

($ENV) = &What_Env_am_I_in;

$WHICHDB    = $in{'WHICHDB'};
$WHICHDB = 'Webinar' if($USER == 2182);

($WHICHDB)  = &StripJunk($WHICHDB);


$| = 1;
my $start = time();
($prog, $dir, $ext) = fileparse($0, '\..*');
$nbsp = "&nbsp\;";
my %color;

$ret = &ReadParse(*in);
&CgiDie("Error in reading and parsing of CGI input") if !defined $ret;

$RTYPE      = $in{'RTYPE'};
$RADIO      = $in{'RADIO'};
$OWNER      = $in{'OWNER'};
($RTYPE)    = &StripJunk($RTYPE);

$RTYPE = "Weekly" if ( !$RTYPE );
$Server_Name = $ENV{'SERVER_NAME'};

&readsetCookies;
&read_canned_header($RBSHeader);


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
} else {
  &MembersLogin;
  &MyPharmassessMembersTrailer;

  print qq#</BODY>\n#;
  print qq#</HTML>\n#;
  exit(0);
}
#______________________________________________________________________________

$inNCPDP = $Pharmacy_NCPDPs{$PH_ID};

$progext = "${prog}${ext}";

$dbin      = "RWDBNAME";	# RBS Reporting Weekly data
$DBNAMERW  = $DBNAMES{"$dbin"};
$TABLERW   = $DBTABN{"$dbin"};
$FIELDSRW  = $DBFLDS{"$dbin"};
$FIELDS2RW = $DBFLDS{"$dbin"} . "2";

$dbin      = "RMDBNAME";	# RBS Reporting Monthly data
$DBNAMERM  = $DBNAMES{"$dbin"};
$TABLERM   = $DBTABN{"$dbin"};
$FIELDSRM  = $DBFLDS{"$dbin"};
$FIELDS2RM = $DBFLDS{"$dbin"} . "2";

$DBNAMERW  = 'Webinar' if($USER == 2182);
$DBNAMERM  = 'Webinar' if($USER == 2182);

$MAX_WEEKS_TO_DISPLAY  = 56;
if ( $PH_ID == 445 ) {
$MAX_MONTHS_TO_DISPLAY = 42;
} else {
$MAX_MONTHS_TO_DISPLAY = 16;
}

$ntitle = "RBS Reports for $Pharmacy_Names{$PH_ID}";
  
print qq#<h1 class="rbsreporting">$ntitle</h1>\n#;

##print qq#RBS Reporting? : $Pharmacy_RBSReporting{$PH_ID}..$TYPE<br>\n# ;

if (($Pharmacy_Types{$PH_ID} =~ /RBS:/i ||  $Pharmacy_Types{$PH_ID} =~ /RBS$/i) && $Pharmacy_RBSReporting{$PH_ID} =~ /Y/i && $TYPE =~ /^SuperUser|^Admin$/i  ) {
  print qq#<div>#; #column container

  print qq#<div class="column">#;
  
  # Weekly section
  &readWeeklyData;
  &displayReportingWeekly;

  # Monthly section
  &readMonthlyData;
  &displayReportingMonthly;
  &displayControlledSubstances;

  # Special section
  &displayReportingSpecial;
  print qq#</div>#; #end column

  print qq#<div class="column">#;
#  print qq#<h2 class="report_header">Interactive Reports</h2>\n#;
 
  &displayReportingInventory;
  &displaySalesByTC;
  &displayTopBottom;
  &displaySalesByPayerYearOverYear;
  #&displayMedSyncPatients;
  #&displayMedSyncIncentive;

  print qq#</div>#; #end column


  print qq#<div class="column">#;

  &displayMostProfitableProduct;
  &displayProfitablePhysician;
  &displayTherapeuticConversions;
 ## &displayDIRReport;
 ## &displayInvTurnGraph;

  print qq#</div>#; #end column

  print qq#<div style="clear: both;"></div>#; 
  print qq#</div>#; #end column container
   
  print qq#			 
  <div id="loading_notification" class="overlay" style="display: none;">
    <div>
      <p class="$bgcolor"><strong>We're building your report...</strong></p>
      <p>Your report could take several minutes to generate. Please do not leave this page while your report is being created.</p>
    <p style="text-align: center;"><img src="/images/loader_large.gif" /></p>
    </div>
  </div>

  <script>
   document.getElementById("Therapeutic").disabled = true;
   document.getElementById('Therapeutic').style.visibility = 'hidden';
   document.getElementById('gif').style.visibility = 'hidden';

    \$(function () {
    
      \$(".overlay").delay(1000).hide();
      \$( '.showload' ).click(function() {
        \$(".overlay").show();
      });  
      
    });

    function overlay_loading() {
      //el = document.getElementById("loading_notification");
      //el.style.visibility = (el.style.visibility == "visible") ? "hidden" : "visible";
    }

    function getDrugName(NDC) {
      document.getElementById("Drug").value = '';
      document.getElementById("Therapeutic").disabled = true;
      document.getElementById('Therapeutic').style.visibility = 'hidden';
      document.getElementById('gif').style.visibility = 'visible';
      var xhttp = new XMLHttpRequest();
      xhttp.onreadystatechange=function() {
      if (this.readyState == 4 && this.status == 200) {
       document.getElementById("Drug").value = this.responseText;
       if (this.responseText!= 'NDC Not Found') {
         document.getElementById("Therapeutic").disabled = false;
         document.getElementById('Therapeutic').style.visibility = 'visible';
       }
       document.getElementById('gif').style.visibility = 'hidden';
      }
    };
    var url ="includes/ndclookup.pl?NDC="+NDC ;
       xhttp.open("POST", url, true);
       xhttp.send();
    }

  </script>
  #;
} elsif(($Pharmacy_Types{$PH_ID} =~ /RBS Direct/) && $Pharmacy_Types{$PH_ID} !~ /RBS$/ && $Pharmacy_Types{$PH_ID} !~ /RBS:/) {


  print qq#<div class="column">#;
  
  # Weekly section
  &readWeeklyData;
  &displayReportingWeekly;

  # Monthly section
  &readMonthlyData;
  &displayReportingMonthly;
  print qq#</div>#; #end column

  print qq#<div class="column">#;
 
  &displaySalesByPayerYearOverYear;
  &displayDIRReport;

  print qq#</div>#; #end column

  print qq#<div style="clear: both;"></div>#; 
  print qq#</div>#; #end column container
   
  print qq#			 
  <div id="loading_notification" class="overlay" style="display: none;">
    <div>
      <p class="$bgcolor"><strong>We're building your report...</strong></p>
      <p>Your report could take several minutes to generate. Please do not leave this page while your report is being created.</p>
    <p style="text-align: center;"><img src="/images/loader_large.gif" /></p>
    </div>
  </div>

  <script>
   document.getElementById("Therapeutic").disabled = true;
   document.getElementById('Therapeutic').style.visibility = 'hidden';
   document.getElementById('gif').style.visibility = 'hidden';

    \$(function () {
    
      \$(".overlay").delay(1000).hide();
      \$( '.showload' ).click(function() {
        \$(".overlay").show();
      });  
      
    });

    function overlay_loading() {
      //el = document.getElementById("loading_notification");
      //el.style.visibility = (el.style.visibility == "visible") ? "hidden" : "visible";
    }

    function getDrugName(NDC) {
      document.getElementById("Drug").value = '';
      document.getElementById("Therapeutic").disabled = true;
      document.getElementById('Therapeutic').style.visibility = 'hidden';
      document.getElementById('gif').style.visibility = 'visible';
      var xhttp = new XMLHttpRequest();
      xhttp.onreadystatechange=function() {
      if (this.readyState == 4 && this.status == 200) {
       document.getElementById("Drug").value = this.responseText;
       if (this.responseText!= 'NDC Not Found') {
         document.getElementById("Therapeutic").disabled = false;
         document.getElementById('Therapeutic').style.visibility = 'visible';
       }
       document.getElementById('gif').style.visibility = 'hidden';
      }
    };
    var url ="includes/ndclookup.pl?NDC="+NDC ;
       xhttp.open("POST", url, true);
       xhttp.send();
    }

  </script>
  #;
} else {

  if($Pharmacy_RBSReporting{$PH_ID} =~ /Y/i) {
    print qq#<div class="column">#;
      &displayReportingInventory;
      &displayMedSyncPatients;
    print qq#</div>#; #end column container
  }
  else {
   &displayAdvertising;
  }
}
 
#______________________________________________________________________________

&MyPharmassessMembersTrailer;

exit(0);

#______________________________________________________________________________

sub displayReporting {
  print qq#<!-- displayReporting -->\n#;

  my $URL = "$progext";
  print qq#<FORM ACTION="$URL" METHOD="POST">\n#;
  print qq#<INPUT TYPE="hidden" NAME="debug"    VALUE="$debug">\n#;
  print qq#<INPUT TYPE="hidden" NAME="verbose"  VALUE="$verbose">\n#;
  print qq#<INPUT TYPE="hidden" NAME="RTYPE"     VALUE="$RTYPE">\n#;

  print qq#<table>\n#;
  # Now display the page of RBS Reports
   
  $Pharmacy_Name = $Pharmacy_Names{$PH_ID};

  $webpath = qq#/members/WebShare/Reports/$Pharmacy_Name/$RTYPE#;
  $dskpath = "D:/WWW/www.pharmassess.com/members/WebShare/Reports/$Pharmacy_Name/$RTYPE";

  my $cnt = 0;
  (@files) = &readfiles($dskpath);
  print qq#<tr><td><hr size=4 noshade></td></tr>\n#;
  if ( $RTYPE =~ /Monthly/i ) {
     print qq#<tr><th class="timeframe">Monthly Archives</th></tr>\n#;
  } else {
     print qq#<tr><th class="timeframe">$RTYPE</th></tr>\n#;
  }
  foreach $filename (@files) {
     print qq#<tr>#;

     if ( $#files == 0 || $cnt == 0) {
        $CHECKED = "CHECKED";
     } else {
        $CHECKED = "";
     }
     print qq#<td>$nbsp <INPUT TYPE="radio" NAME="RADIO" VALUE="$filename" $CHECKED> $filename</td>#;
     print qq#</tr>\n#;
     $cnt++;
  }
  if ( !$cnt ) {
     print qq#<tr><td>No $RTYPE files found</td></tr>\n#;
  } else {
     print qq#<tr><td><hr size=4 noshade></td></tr>\n#;
     $submitvalue = "See File";
     print qq#<tr><th><INPUT TYPE="Submit" NAME="REPORT" VALUE="$submitvalue"></th></tr>\n#;

  }
  print qq#</table>\n#;
  print qq#</FORM>\n#;
  print "sub displayReporting: Exit.<br>\n" if ($debug);

}

sub displayControlledSubstances {
  print qq#<div class="block">\n#;

  print qq#<!-- displayControlledSubstances -->\n#;

  my $URL = "RBSControlledSubstances.cgi";

  print qq#<FORM ACTION="$URL" METHOD="POST">\n#;
  print qq#<INPUT TYPE="hidden" NAME="RTYPE"     VALUE=$TYPE>\n#;

  $Pharmacy_Name = $Pharmacy_Names{$PH_ID};
  my $cnt = 0;
  print qq#<h2 class="report_block_header">Controlled Substances</h2>\n#;
  $submitvalue = "Run Report";
  print qq#<INPUT TYPE="Submit" NAME="REPORT" VALUE="$submitvalue" class="button report_button">\n#;
  print qq#</FORM>\n#;

  print qq#</div>\n#; #end block
}

sub displayReportingWeekly {
  print qq#<div class="block">\n#;

  print qq#<!-- displayReportingWeekly -->\n#;

  my $URL = "RBSReportingWeekly.cgi";
  $RTYPE   = "Weekly";
  print qq#<FORM ACTION="$URL" METHOD="POST">\n#;
  print qq#<INPUT TYPE="hidden" NAME="TYPE"     VALUE=$RTYPE>\n#;

  # Now display the page of RBS Reports
   
  $Pharmacy_Name = $Pharmacy_Names{$PH_ID};

  #print "<hr>\n";

  my $cnt = 0;
  print qq#<h2 class="report_block_header">Reports By Week</h2>\n#;

  $submitvalue = "Run Report";
  print qq#<p>for week ending on #;
  print qq#<SELECT NAME="ReportWeek">\n#;

  foreach $weeklydate (sort { $Rep_Date{$b} cmp $Rep_Date{$a} } keys %Rep_Date) {
    if ( $cnt == 0) {
       $SEL = "SELECTED";
    } else {
       $SEL = "";
    }
    print qq#<OPTION $SEL VALUE="$weeklydate">$weeklydate</OPTION>\n#;
    $cnt++;
  }
  print qq#</SELECT>\n#;
  print qq#</p>\n#;
  if ( !$cnt ) {
     print qq#No Weekly files found\n#;
  }
  
  print qq#<INPUT TYPE="Submit" NAME="REPORT" VALUE="$submitvalue" class="button report_button">\n#;
  
  print qq#</FORM>\n#;

  print qq#</div>\n#; #end block
}

#______________________________________________________________________________

sub displayReportingMonthly {
  print qq#<div class="block">\n#;

  print qq#<!-- displayReportingMonthly -->\n#;

  # Now display the page of RBS Reports
   
  $Pharmacy_Name = $Pharmacy_Names{$PH_ID};

  print qq#<h2 class="report_block_header">Reports By Month</h2>\n#;

  foreach $monthlydate (sort { $Rep_Date{$b} cmp $Rep_Date{$a} } keys %Rep_Date) {
    my $output = $monthlydate;
    $output =~ s/-01$//g;
    my ($jyear, $jmonth) = split("-", $output, 2);
    $jmonth += 0;   
    $output = "$jyear " . $FMONTHS{$jmonth};
    
    my $jfmonth = $FMONTHS{$jmonth};

    $RTYPE = "Monthly";
    $timeframe = "";
    if ( $jmonth == 3 || $jmonth == 9 ) {
       $timeframe = "Quarterly";
       $RTYPE      = $timeframe;
       $timeframe = "<strong>$timeframe</strong>";
    } elsif ( $jmonth == 6 ) {
       #$timeframe = "Semi-Annual"; #6/22/2015 : Monty said to remove term 'Semi-Annual' and instead simply call 'Quarterly'
       $timeframe = "Quarterly";
       $RTYPE      = $timeframe;
       $timeframe = "<strong>$timeframe</strong>";
    } elsif ( $jmonth == 12 ) {
       $timeframe = "Annual";
       $RTYPE      = $timeframe;
       $timeframe = "<strong style=\"font-size: 16px;\">$timeframe</strong>";
    } else {
       $timeframe = "Monthly";
       $RTYPE      = $timeframe;
    }

    my $URL = "RBSReportingReport.cgi";
    # print qq#<span class="less_margin"><FORM ACTION="$URL" METHOD="POST">\n#;
    # print qq#<INPUT TYPE="hidden" NAME="TYPE"     VALUE="$RTYPE">\n#;

    # $submitvalue = "View Report";
    # print qq#<INPUT TYPE="Submit" NAME="REPORT" VALUE="$submitvalue" class="button" >\n#;
    # print qq#<INPUT TYPE="hidden" NAME="ReportMonth" VALUE="$monthlydate"> for $output ($timeframe)<br>\n#;
    # print qq#</FORM></span>\n#;
    
#   <a href="${URL}?debug=$debug&verbose=$verbose&TYPE=$RTYPE&ReportMonth=$monthlydate">
    print qq#
    <a href="${URL}?RTYPE=$RTYPE&ReportMonth=$monthlydate">
    <div class="monthly_report" style="$color{$monthlydate}">
      <div >
        <div style="float: left;">
          <img src="/images/icons/cal${jmonth}.png" style="vertical-align: middle;" /> 
          $jfmonth <span class="monthly_report_year">($jyear)</span>
        </div>
        <div class="timeframe" style="float: right;">$timeframe</div>
        <div style="clear: both;"></div>
      </div>
    </div>
    </a>
    #;

  }

  print qq#</div>\n#; #end block
}

#______________________________________________________________________________

sub displayReportingSpecial {
  print qq#<!-- displayReportingMonthly -->\n#;
  my $inNCPDP = $Pharmacy_NCPDPs{$PH_ID};
   
#-----------------------------
# jlh. 01/03/2017. Brent had me add this Quick & Dirty code to make Hometown's work...
#
  if      ( $inNCPDP == 2605357 ) {
    $Pharmacy_Name = "Hometown Pharmacy - Carrollton";
  } elsif ( $inNCPDP == 2634435 ) {
    $Pharmacy_Name = "Hometown Pharmacy - Chillicothe";
  } elsif ( $inNCPDP == 2641721 ) {
    $Pharmacy_Name = "Hometown Pharmacy - Peculiar";
  } elsif ( $inNCPDP == 2639043 ) {
    $Pharmacy_Name = "Hometown Pharmacy - Trenton";
  } else {
    $Pharmacy_Name = $Pharmacy_Names{$PH_ID};
  }
#-----------------------------
#  $path_DIR   = qq#members/WebShare/Reports/$Pharmacy_Name/Special/DIR#;
  $path_340B  = qq#members/WebShare/Reports/$Pharmacy_Name/Special/340B#;
  $path_Other = qq#members/WebShare/Reports/$Pharmacy_Name/Special/Other#;

}

#______________________________________________________________________________

sub dropdown7 {
  my ($dbvar, $label, @OPTS) = @_;

  $dbvarval = $$dbvar;
  $formname = "$dbvar";

  my $foundmatch = 0;

  print qq#  <th>$label</th>\n#;
  print qq#  <td>\n#;
  print qq#    <SELECT NAME="$formname">\n#;

  foreach $OPT (@OPTS) {
    if ( $dbvarval =~ /^$OPT/i ) {
       $SEL = "SELECTED";
       $foundmatch++;
    } else {
       $SEL = "";
    }
    print qq#      <OPTION $SEL VALUE="$OPT">$OPT</OPTION>\n#;
  }

  print qq#    </SELECT>\n#;
  print qq#  </td>\n#;
 
  # print qq#</tr>\n#;

  # print "sub dropdown7: dbvar: exit.<br>\n" if ($verbose);
}
 
#______________________________________________________________________________

sub docmd_local {
  ($cmd) = @_;
  my $out = "";

  chomp($out = `$cmd`);
  $cmd = "";
  $out =~ s///g;

  return($cmd, $out);
}
#______________________________________________________________________________
 
sub readWeeklyData {
  # open RBSReporting DB, read Weekly data
   
  %attr = ( PrintWarn=>1, RaiseError=>1, PrintError=>1, AutoCommit=>1, InactiveDestroy=>0, HandleError => \&handle_error );
  $dbRW = DBI->connect("DBI:mysql:$DBNAMERW:$DBHOST",$dbuser,$dbpwd, \%attr) || &handle_error;
   
  my $sql = "";

  $sql  = "SELECT Date
             FROM $DBNAMERW.$TABLERW 
            WHERE Pharmacy_ID = $PH_ID
               && Total_Scripts > 0 
         ORDER BY Date DESC ";

  $sthx  = $dbRW->prepare("$sql");
  $sthx->execute;

  my $NumOfRows = $sthx->rows;

  $ptr = 0;
  while ( my @row = $sthx->fetchrow_array() ) {

     my ( $Date) = @row;
     # print "Date: $Date<br>\n";

     $ptr++;
     next if ( $ptr > $MAX_WEEKS_TO_DISPLAY );

     $RepKey            = "$Date";
     $Rep_Date{$RepKey} = $Date;
  }
  $sthx->finish;
 
  # Close the Database
  $dbRW->disconnect; 
}

#______________________________________________________________________________
 
sub readMonthlyData {
  $RepKey   = "";
  %Rep_Date = ();

  # open RBSReporting DB, read Monthly data
   
  %attr = ( PrintWarn=>1, RaiseError=>1, PrintError=>1, AutoCommit=>1, InactiveDestroy=>0, HandleError => \&handle_error );
  $dbRM = DBI->connect("DBI:mysql:$DBNAMERM:$DBHOST",$dbuser,$dbpwd, \%attr) || &handle_error;
   
  my $sql = "";
  $DBNAMERM = 'Webinar' if($PH_ID < 11);

  $sql  = " SELECT Date, Display 
              FROM $DBNAMERM.$TABLERM
             WHERE Pharmacy_ID= $PH_ID 
                && Date >= DATE_SUB(curdate(), INTERVAL $MAX_MONTHS_TO_DISPLAY MONTH) 
                && ( Total_Brand>0 || Total_Generic>0 ) ";

  if ( $TYPE =~ /Admin/i) {
     $sql .= "&& Display IN('D', 'Y') ";
  } else {
     $sql .= "&& Display='Y' ";
  }

  $sql .= " ORDER BY Date DESC ";

#                && Display IN('D', 'Y')
#          ORDER BY Date DESC";

  $sthx  = $dbRM->prepare("$sql");
  $sthx->execute;

  my $NumOfRows = $sthx->rows;

  my $ptr = 0;
  while ( my @row = $sthx->fetchrow_array() ) {
     my ($Date,$Display) = @row;
#    print "Date: $Date<br>\n";

     $ptr++;
     next if ( $ptr > $MAX_MONTHS_TO_DISPLAY );
     $RepKey               = "$Date";
     $Rep_Date{$RepKey}    = $Date;
     $color{$Date} = ''    if ($Display ne 'D'); 
     $color{$Date} = 'background-color:red; color:#ffffff' if ($Display eq 'D'); 
  }
  $sthx->finish;
 
  # Close the Database
  $dbRM->disconnect; 
}

#______________________________________________________________________________

sub is_folder_empty {
    my ($dirname) = @_;
    opendir(my $dh, $dirname);
    return scalar(grep { $_ ne "." && $_ ne ".." } readdir($dh)) == 0;
}

#______________________________________________________________________________

sub displayAdvertising {
  print qq#RBS Reporting has not been set up for your pharmacy.<br><br>\n#;

  print qq#To have this set up, please contact us using the information on the #;
  print qq#<a href="/members/LetUsKnow.cgi">"Let Us Know"</a> page.<br><br>\n#;
  print qq#Thank you!<br>\n#;
}

#______________________________________________________________________________

sub displayReportingInventory {
#  <img src="/images/icons/play44.png" style="vertical-align: middle;" /> 
  print qq#<div class="block">\n#;

  #print "<hr>\n";
  print qq#
  <h2 class="report_block_header">
  Inventory Management Report
  </h2>#;
  my $URL = "RBSReportingInventory.cgi";
  print qq#<FORM ACTION="$URL" METHOD="POST">\n#;
  print qq#<INPUT TYPE="hidden" NAME="TYPE"     VALUE="$TYPE">\n#;

  print qq#<p>Show top <input type="text" name="lines" value="900" style="width: 35px;"> NDC groups by total cost.</p><br>#;

  $submitvalue = "Run Report";
  print qq#<INPUT TYPE="Submit" NAME="Generate" VALUE="$submitvalue" class="button showload report_button" onclick='overlay_loading()'>\n#;
  print qq#</FORM>\n#;

  print qq#</div>\n#; #end block
  
}

#______________________________________________________________________________

sub displayPlanLookupTest {
  if ($ENV =~ /dev/i) {

    print qq#<div class="block">\n#;

    #print "<hr>\n";
    print "<h2>Test Plan Lookup</h2>";
    my $URL = "RBSReporting_Test.cgi";
    print qq#<FORM ACTION="$URL" METHOD="POST">\n#;
    print qq#<INPUT TYPE="hidden" NAME="TYPE"     VALUE="$TYPE">\n#;
	
	print qq#<p>Run a test matching of plan name to BIN/PCN/GROUP combos from real pharmacy data.</p>#;
	
    $submitvalue = "Show Test";
    print qq#<INPUT TYPE="Submit" NAME="Generate" VALUE="$submitvalue" class="button showload report_button" onclick='overlay_loading()'>\n#;
    print qq#</FORM>\n#;
	
	print qq#</div>\n#; #end block
  }
}

#______________________________________________________________________________

sub displaySalesByPayerYearOverYear {
  print qq#<div class="block">\n#;

  #print "<hr>\n";
  print qq#
  <h2 class="report_block_header">
  Sales By Payer Year-Over-Year
  </h2>#;
  my $URL = "RBSReportingSBPYOY.cgi";
  print qq#<FORM ACTION="$URL" METHOD="POST">\n#;
  print qq#<INPUT TYPE="hidden" NAME="TYPE"     VALUE="$TYPE">\n#;

  print qq#<p>Year over year comparison of Sales by Payer data.</p>#;

  $submitvalue = "Run Report";
  print qq#<INPUT TYPE="Submit" NAME="Generate" VALUE="$submitvalue" class="button report_button">\n#;
  #showload
  print qq#</FORM>\n#;
	
	print qq#</div>\n#; #end block
}

#______________________________________________________________________________

sub displaySalesByTC {
  print qq#<div class="block">\n#;

  #print "<hr>\n";
  print qq#
  <h2 class="report_block_header">
  Sales By Therapeutic Class
  </h2>#;
  my $URL = "RBSReportingSBTC.cgi";
  print qq#<FORM ACTION="$URL" METHOD="POST">\n#;
  print qq#<INPUT TYPE="hidden" NAME="debug"    VALUE="$debug">\n#;
  print qq#<INPUT TYPE="hidden" NAME="verbose"  VALUE="$verbose">\n#;
  print qq#<INPUT TYPE="hidden" NAME="TYPE"     VALUE="$TYPE">\n#;

  print qq#<p>Detailed summary of drugs by therapeutic class, further broken out by third party payer.</p>#;

  $submitvalue = "Run Report";
  print qq#<INPUT TYPE="Submit" NAME="Generate" VALUE="$submitvalue" class="button report_button">\n#;
  #showload
  print qq#</FORM>\n#;
	
	print qq#</div>\n#; #end block
}

sub displayMostProfitableProduct {
  print qq#<div class="block">\n#;

  print qq#
  <h2 class="report_block_header">
    Most Profitable Product Report 
  </h2>#;
  my $URL = "RBSReportingMostProfitableProduct.cgi";
  print qq#<FORM ACTION="$URL" METHOD="POST">\n#;
  print qq#<INPUT TYPE="hidden" NAME="TYPE"     VALUE="$TYPE">\n#;

  print qq#<p>Products sorted by gross margin, and further <br />broken down into individual prescriptions.</p>#;

  $submitvalue = "Run Report";
  print qq#<INPUT TYPE="Submit" NAME="Generate" VALUE="$submitvalue" class="button report_button">\n#;
  print qq#</FORM>\n#;
	
  print qq#</div>\n#; #end block
}

sub displayTherapeuticConversions {
  print qq#<div class="block">\n#;

  print qq#
  <h2 class="report_block_header">
   Therapeutic Conversions 
  </h2>#;
  my $URL = "RBSReportingTherapeuticConversion.cgi";
  print qq#<FORM ACTION="$URL" METHOD="POST">\n#;
  print qq#<INPUT TYPE="hidden" NAME="debug"    VALUE="$debug">\n#;
  print qq#<INPUT TYPE="hidden" NAME="verbose"  VALUE="$verbose">\n#;
  print qq#<INPUT TYPE="hidden" NAME="TYPE"     VALUE="$TYPE">\n#;

  print qq#<p>Search for a drug and compare the gross margin of alternatives within its therapeutic class. </p>#;
  print qq#<input type="text" name="NDC" id="NDC" placeholder="NDC" value="" style="width: 120px" onchange='getDrugName(this.value)';> <img src="/images/loader_small.gif" id='gif' /><br></p>#;
  print qq#<input type="text" id="Drug" name="Drug" placeholder="Drug" value="" readonly style="width: 240px"; ">#;

  $submitvalue = "Run Report";
  print qq#<INPUT TYPE="Submit" id="Therapeutic" NAME="Generate" VALUE="$submitvalue" class="button report_button">\n#;
  print qq#</FORM>\n#;
  print qq#</div>\n#; #end block
}


sub displayProfitablePhysician {
  print qq#<div class="block">\n#;

  print qq#
  <h2 class="report_block_header">
    Most Profitable Physician Report
  </h2>#;
  my $URL = "RBSReportingMostProfitablePhysician.cgi";
  print qq#<FORM ACTION="$URL" METHOD="POST">\n#;
  print qq#<INPUT TYPE="hidden" NAME="debug"    VALUE="$debug">\n#;
  print qq#<INPUT TYPE="hidden" NAME="verbose"  VALUE="$verbose">\n#;
  print qq#<INPUT TYPE="hidden" NAME="TYPE"     VALUE="$TYPE">\n#;

  print qq#<p>Physicians sorted by profit and prescription volume.</p>#;

  $submitvalue = "Run Report";
  print qq#<INPUT TYPE="Submit" NAME="Generate" VALUE="$submitvalue" class="button report_button">\n#;
  print qq#</FORM>\n#;
  print qq#</div>\n#; #end block
}

#______________________________________________________________________________

sub displayTopBottom {
  print qq#<div class="block">\n#;

  #print "<hr>\n";
  print qq#
  <h2 class="report_block_header">
  Top / Bottom Payers
  </h2>#;
  my $URL = "RBSReportingTB.cgi";
  print qq#<FORM ACTION="$URL" METHOD="POST">\n#;
  print qq#<INPUT TYPE="hidden" NAME="TYPE"     VALUE="$TYPE">\n#;

  print qq#<p>Top and Bottom Payers listed in order of GM/Script.</p>#;

  $submitvalue = "Run Report";
  print qq#<INPUT TYPE="Submit" NAME="Generate" VALUE="$submitvalue" class="button report_button">\n#;
  #showload
  print qq#</FORM>\n#;
	
  print qq#</div>\n#; #end block
}

sub displayMedSyncIncentive {
  print qq#<div class="block">\n#;

  #print "<hr>\n";
  print qq#
  <h2 class="report_block_header">
  Med Sync Incentive Graph
  </h2>#;

  my $URL = "RBSReportingMedSyncIncentive.cgi";
  print qq#<FORM ACTION="$URL" METHOD="POST">\n#;
  print qq#<INPUT TYPE="hidden" NAME="TYPE"     VALUE="$TYPE">\n#;
 
  $submitvalue = "Run Report";
  print qq#<INPUT TYPE="Submit" NAME="Generate" VALUE="$submitvalue" class="button showload report_button" onclick='overlay_loading()'>\n#;
  print qq#</FORM>\n#;

  print qq#</div>\n#; #end block
}

sub displayMedSyncPatients {
  print qq#<div class="block">\n#;

  #print "<hr>\n";
  print qq#
  <h2 class="report_block_header">
  Med Sync Patient Report
  </h2>#;

  my $URL = "RBSReportingMedSync.cgi";
  print qq#<FORM ACTION="$URL" METHOD="POST">\n#;
  print qq#<INPUT TYPE="hidden" NAME="debug"    VALUE="$debug">\n#;
  print qq#<INPUT TYPE="hidden" NAME="verbose"  VALUE="$verbose">\n#;
  print qq#<INPUT TYPE="hidden" NAME="TYPE"     VALUE="$TYPE">\n#;

  $submitvalue = "Run Report";
  print qq#<INPUT TYPE="Submit" NAME="Generate" VALUE="$submitvalue" class="button showload report_button" onclick='overlay_loading()'>\n#;
  print qq#</FORM>\n#;

  print qq#</div>\n#; #end block
}

sub displayDIRReport {
  print qq#<div class="block">\n#;

  #print "<hr>\n";
  print qq#
  <h2 class="report_block_header">
  DIR Fee Report
  </h2>#;
  my $URL = "RBSReporting_DIR_Fees.cgi";
  print qq#<FORM ACTION="$URL" METHOD="POST">\n#;
  print qq#<INPUT TYPE="hidden" NAME="debug"    VALUE="$debug">\n#;
  print qq#<INPUT TYPE="hidden" NAME="verbose"  VALUE="$verbose">\n#;
  print qq#<INPUT TYPE="hidden" NAME="TYPE"     VALUE="$TYPE">\n#;

  print qq#<p>Summary of DIR Fees, by Quarter.</p>#;

  $submitvalue = "Run Report";
#  print qq#<INPUT TYPE="Submit" NAME="Generate" VALUE="$submitvalue" class="button showload report_button" onclick='overlay_loading()'>\n#;
  print qq#<INPUT TYPE="Submit" NAME="Generate" VALUE="$submitvalue" class="button report_button">\n#;
  print qq#</FORM>\n#;

  print qq#</div>\n#; #end block
}

sub displayInvTurnGraph {
  print qq#<div class="block">\n#;

  #print "<hr>\n";
  print qq#
  <h2 class="report_block_header">
  Inventory Turn Graph
  </h2>#;
  my $URL = "RBSInventory_Turn.cgi";
  print qq#<FORM ACTION="$URL" METHOD="POST">\n#;
  print qq#<INPUT TYPE="hidden" NAME="debug"    VALUE="$debug">\n#;
  print qq#<INPUT TYPE="hidden" NAME="verbose"  VALUE="$verbose">\n#;
  print qq#<INPUT TYPE="hidden" NAME="TYPE"     VALUE="$TYPE">\n#;

  $submitvalue = "Run Report";
  print qq#<INPUT TYPE="Submit" NAME="Generate" VALUE="$submitvalue" class="button report_button">\n#;
  print qq#</FORM>\n#;

  print qq#</div>\n#; #end block
}

#______________________________________________________________________________
