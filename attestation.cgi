require "D:/RedeemRx/MyData/RBSDesktop_routines.pl";
require "D:/RedeemRx/cgi-bin/cgi-lib.pl";

use File::Basename;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use Env qw(PATH REMOTE_ADDR PERL5LIB PERLLIB);
use DateTime;

$| = 1; # don't buffer output
my $start = time();
my ($prog, $dir, $ext) = fileparse($0, '\..*');
$nbsp = "&nbsp\;";

$title = "$prog";
$title = qq#${COMPANY} - $title# if ( $COMPANY );

$ret = &ReadParse(*in);

&CgiDie("Error in reading and parsing of CGI input") if !defined $ret;

$dbin     = "TPDBNAME";
$db       = $dbin;
$DBNAME   = $DBNAMES{"$dbin"};
$TABLE    = $DBTABN{"$dbin"};
$FIELDS   = $DBFLDS{"$dbin"};
$FIELDS2  = $DBFLDS{"$dbin"} . "2";
$fieldcnt = $#${FIELDS2} + 2;

my $HASH   = $HASHNAMES{$dbin};

#______________________________________________________________________________

&readsetCookies;

&readPharmacies;

#______________________________________________________________________________

&printCredAttestationHeader;

#______________________________________________________________________________

if ( $USER ) {
   $Entity_Type = $Login_Auth{$USER};
   if ($Entity_Type =~ /company/i) {
	 $PROGRAM = "RBS Company";
   } else {
	 $PROGRAM = "RBS";
   }

   &printCredAttestation($PH_ID, $PROGRAM);

   exit(0);

} else {
   &MembersLogin;
   &MyPharmassessMembersTrailer;

   print qq#</BODY>\n#;
   print qq#</HTML>\n#;
   exit(0);
}
