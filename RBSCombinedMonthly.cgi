require "D:/RedeemRx/MyData/RBSDesktop_routines.pl";
require "D:/RedeemRx/cgi-bin/cgi-lib.pl";

use File::Basename;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use Env qw(PATH REMOTE_ADDR PERL5LIB PERLLIB);

($ENV) = &What_Env_am_I_in;

$| = 1;
my $start = time();
my ($prog, $dir, $ext) = fileparse($0, '\..*');
$nbsp = "&nbsp\;";

$ret = &ReadParse(*in);
&CgiDie("Error in reading and parsing of CGI input") if !defined $ret;

$RADIO      = $in{'RADIO'};

$Server_Name = $ENV{'SERVER_NAME'};

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

$lyear = sprintf("%4d", $syear-1);

$dbDate_m1y = "${lyear}${smonth}${sday}";

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
$DBNAMERM = 'Webinar' if($USER == 2182);

$MAX_MONTHS_TO_DISPLAY = 15;

$ntitle = "RBS Reports for $Pharmacy_Names{$PH_ID}";
  
print qq#<h1 class="rbsreporting">$ntitle</h1>\n#;

if ($TYPE =~ /^SuperUser|^Admin$/i  ) {
  print qq#<div >#; #column container
    print qq#<div style="width:300px;">#;
      print qq#<h2 class="report_header">RBS Reports</h2>\n#;
  
      # Monthly section
#      ($suNCPDPs) = &getsuperuserncpdps($USER);
      ($suIDs, $ptype) = &get_user_pharmacyids($USER);

      &readMonthlyData;
      &displayReportingMonthly;
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
#;
} else {
 &displayAdvertising;
}
 
#______________________________________________________________________________

&MyPharmassessMembersTrailer;

exit(0);

#______________________________________________________________________________

sub displayReportingMonthly {
  my $background;

  print qq#<div class="block">\n#;

  print qq#<!-- displayReportingMonthly -->\n#;

  print qq#<h2 class="report_block_header">Reports By Month</h2>\n#;

  foreach $monthlydate (sort { $Rep_Date{$b} cmp $Rep_Date{$a} } keys %Rep_Date) {
    my $output  = $monthlydate;
    my $display = $Display_Date{$output};

    $output =~ s/-01$//g;
    my ($jyear, $jmonth) = split("-", $output, 2);
    $jmonth += 0;   
    $output = "$jyear " . $FMONTHS{$jmonth};
    
    my $jfmonth = $FMONTHS{$jmonth};

    $rpttype = "Monthly";
    $timeframe = "";
    if ( $jmonth == 3 || $jmonth == 9 ) {
       $timeframe = "Quarterly";
       $rpttype   = $timeframe;
       $timeframe = "<strong>$timeframe</strong>";
    } elsif ( $jmonth == 6 ) {
       $timeframe = "Quarterly";
       $rpttype   = $timeframe;
       $timeframe = "<strong>$timeframe</strong>";
    } elsif ( $jmonth == 12 ) {
       $timeframe = "Annual";
       $rpttype   = $timeframe;
       $timeframe = "<strong style=\"font-size: 16px;\">$timeframe</strong>";
    } else {
       $timeframe = "Monthly";
       $rpttype   = $timeframe;
    }

    my $URL = "RBSCombinedReport.cgi";

    print qq#
    <a href="${URL}?RptType=$rpttype&ReportMonth=$monthlydate">
    <div class="monthly_report" style="" >
      <div>
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
 
sub readMonthlyData {
  %attr = ( PrintWarn=>1, RaiseError=>1, PrintError=>1, AutoCommit=>1, InactiveDestroy=>0, HandleError => \&handle_error );
  $dbRM = DBI->connect("DBI:mysql:$DBNAMERM:$DBHOST",$dbuser,$dbpwd, \%attr) || &handle_error;

  $RepKey   = "";
  %Rep_Date = ();

  my $display = "&& Display IN('D', 'Y')";
   
  my $sql = "";

  $sql = "
    SELECT * FROM (
      SELECT Date, Display FROM $DBNAMERM.$TABLERM
       WHERE Pharmacy_ID IN ($suIDs) && Date >= DATE_SUB(curdate(), INTERVAL 16 MONTH) 
          && ( Total_Brand>0 || Total_Generic>0 ) 
           $display
       GROUP BY DATE, display order by display 
      ) a
    GROUP BY DATE ORDER BY Date DESC
  ";
  $sthx  = $dbRM->prepare("$sql");
  $sthx->execute;

  my $NumOfRows = $sthx->rows;
 
  my $ptr = 0;
  while ( my @row = $sthx->fetchrow_array() ) {
     my ( $Date, $Disp) = @row;

     $ptr++;
     next if ( $ptr > $MAX_MONTHS_TO_DISPLAY );
     next if ($Disp eq 'D'&& $TYPE !~ /Admin/i); 
     $RepKey                = "$Date";
     $Rep_Date{$RepKey}     = $Date;
     $Display_Date{$RepKey} = $Disp;
  }
  $sthx->finish;
 
  # Close the Database
  $dbRM->disconnect; 
}

#______________________________________________________________________________


sub displayAdvertising {
  print qq#RBS Reporting has not been set up for your pharmacy.<br><br>\n#;

  print qq#To have this set up, please contact us using the information on the #;
  print qq#<a href="/members/LetUsKnow.cgi">"Let Us Know"</a> page.<br><br>\n#;
  print qq#Thank you!<br>\n#;
}

