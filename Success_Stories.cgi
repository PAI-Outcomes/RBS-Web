require "D:/RedeemRx/MyData/RBSDesktop_routines.pl";
require "D:/RedeemRx/cgi-bin/cgi-lib.pl";

use File::Basename;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use Env qw(PATH REMOTE_ADDR PERL5LIB PERLLIB);

$| = 1;
my $start = time();
($prog, $dir, $ext) = fileparse($0, '\..*');
$nbsp = "&nbsp\;";

$title = "$prog";

$DBNAME   = 'RBSReporting';
$TABLE    = 'roi_stories';

#______________________________________________________________________________

&readsetCookies;

&MyPharmassessMembersHeader;

#______________________________________________________________________________
# Create the inputfile format name
my ($min, $hour, $day, $month, $year) = (localtime)[1,2,3,4,5];
$year  += 1900;	# reported as "years since 1900".
$month += 1;	# reported ast 0-11, 0==January

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

$dbx = DBI->connect("DBI:mysql:$DBNAME:$DBHOST",$dbuser,$dbpwd,
        { PrintError => 1, RaiseError => 1, InactiveDestroy => 0 } ) || die "$DBI::errstr";
   
DBI->trace(1) if ($dbitrace);
 
#______________________________________________________________________________

$ntitle = "Success Stories";

#print qq#<h1>$ntitle</h1>\n#;

&displaySuccessStories($PH_ID);

&displaySuccessStories('ALL');

#______________________________________________________________________________

# Close the Database
$dbx->disconnect;

&MyPharmassessMembersTrailer;

exit(0);

#______________________________________________________________________________

sub displaySuccessStories {
  my ($for) = @_;

  my $rpt_dte = "";
  my $FMT = "%0.02f";
  my $PharmacyName;
  my $WHERE = '';

  if ($month <= 3) {
    $rpt_dte = --$year . '-01-01';
  }
  else {
    $rpt_dte = $year . '-01-01';
  }

  if ($for !~ /ALL/i) {
    $WHERE = "AND Pharmacy_ID = $for";
    $PharmacyName = $Pharmacy_Names{$for};
  }
  else {
    $PharmacyName = $for;
  }

  print qq#<table class="main">\n#;

  print "<tr>\n";

  print "<th colspan=1 align=left><h1>$PharmacyName Success Stories</h1></th>\n";
  print "<th colspan=2 align=right><font size=-2><i>* Current year to date and, if first quarter, previous year too</i></font></th>\n";

  print "</tr>\n";
  print "<tr>\n";
  print qq#<th class="align_left"  width=50%>Category</th> \n#;
  print qq#<th class="align_right" width=25%>Amount</th> \n#;
  print qq#<th class="align_left">Recovered</th> \n#;
  print qq#</tr>\n#;

  my @sortit = sort { $Int_Closed_Date{$b} cmp $Int_Closed_Date{$a} } keys %Intervention_IDs;
  my $where = "";

  $processedcount = 0;
  $Total_Success_Story = 0;

  my $sql = "SELECT Category, Date_Realized, SUM(Amt_Realized) AS Total
                FROM $DBNAME.$TABLE
               WHERE Date_Realized > '$rpt_dte'
              $WHERE
            GROUP BY Category, Date_Realized
            ORDER BY Category, Date_Realized DESC";

  $sth = $dbx->prepare($sql);
  $sth->execute();

  while (my @row = $sth->fetchrow_array()) {
    ($Category, $Date, $Total) =  @row;

     $Date_Year = substr($Date, 0, 4);
     $Date_Mon  = substr($Date, 5, 2);
     $Date_Day  = substr($Date, 8, 2);

     $Date_Realized = $Date_Mon ."/" . $Date_Day . "/" . $Date_Year;
 
     $processedcount++;
     $Total_Success_Story += $Total;

     print "<tr>";
     print qq#<td>$Category</td>#;
     $SSamt = "\$" . &commify(sprintf("$FMT", $Total));
     print qq#<td nowrap class="align_right lj_blue">$SSamt</td>#;
     print qq#<td>$Date_Realized</td>#;
     print qq#</tr>\n#;
  }

  $sth->finish();

  if ( $processedcount) {
     if ( $dorep =~ /^ALL$/i ) {
        $msg = "$processedcount Success Stories found";
     } else {
        $msg = "$processedcount $PharmacyName Success Stories found";
     } 
  } else {
     $msg = "No $PharmacyName Success Stories found yet";
  }
  print qq#<tr>#;
  print qq#<th class="align_left navy">Total Success Stories</th>\n#;

  $SSamt = "\$" . &commify(sprintf("$FMT", $Total_Success_Story));
  print qq#<th class="align_right navy">$SSamt</th>#;
  print qq#<th class="align_right navy">$nbsp</th>#;
  print qq#</tr>\n#;
  print qq#<tr><th colspan=3 class="align_left">$msg</th></tr>#;
  print "</table>\n";

  print "<br>\n";
}

#______________________________________________________________________________

