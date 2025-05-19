require "D:/RedeemRx/MyData/RBSDesktop_routines.pl";
require "D:/RedeemRx/cgi-bin/cgi-lib.pl";

use File::Basename;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use Env qw(PATH REMOTE_ADDR PERL5LIB PERLLIB);

$| = 1;
my $start = time();
my ($prog, $dir, $ext) = fileparse($0, '\..*');
my $members = 'members';
$nbsp = "&nbsp\;";

$title = "$prog";
$title = qq#${COMPANY} - $title# if ( $COMPANY );

$ret = &ReadParse(*in);

&CgiDie("Error in reading and parsing of CGI input") if !defined $ret;

$SORT    = $in{'SORT'};

#______________________________________________________________________________

&readsetCookies;

&read_canned_header($RBSHeader);
$members = 'www' if ($ENV{'SERVER_NAME'} =~ /^dev./);

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

&readPharmacies();
&readLogins;

$FirstName = $LFirstNames{$USER};
$LastName  = $LLastNames{$USER};
$Pharmacy_Name = $Pharmacy_Names{$PH_ID};

$ntitle = "Generate EFT Paperwork";

print qq#<h1>$ntitle</h1>\n#;

&displayEFT;

#______________________________________________________________________________

&MyPharmassessMembersTrailer;

exit(0);

#______________________________________________________________________________

sub displayEFT {

  print qq#<!-- displayEFT -->\n#;
  print "sub displayEFT: Entry.<br>\n" if ($debug);

  $pdfSaveDir = "D:/PharmAssess/Reports"; #no trailing slash
  $pdfDownloadDir = "/Reports"; #no trailing slash

  &eftForm($PH_ID, $pdfSaveDir, $pdfDownloadDir);

  print "sub displayEFT: Exit.<br>\n" if ($debug);

}

#______________________________________________________________________________
