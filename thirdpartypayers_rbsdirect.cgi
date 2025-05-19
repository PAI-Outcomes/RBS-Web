require "D:/RedeemRx/MyData/RBSDesktop_routines.pl";
require "D:/RedeemRx/cgi-bin/cgi-lib.pl";

use File::Basename;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use Env qw(PATH REMOTE_ADDR PERL5LIB PERLLIB);

$| = 1;
my $start = time();
my ($prog, $dir, $ext) = fileparse($0, '\..*');
$nbsp = "&nbsp\;";
$title = "$prog";
$title = qq#${COMPANY} - $title# if ( $COMPANY );

#______________________________________________________________________________

&readsetCookies;

&read_canned_header($RBSHeader);

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

$ntitle = "Third Party Payer Information";

print qq#<h1>$ntitle</h1>\n#;

print qq#<ul>\n#;

print qq#  <li><a href="thirdpartypayers_contracted.cgi">Third Party Payers</a></li>\n#;
print qq#  <li><a href="MedicarePartD.cgi"              >Medicare Part D</a></li>\n#;
print qq#  <li><a href="EFT.cgi"                        >Submit request for ALL available EFT's</a></li>\n#;
print qq#</ul>\n#;

#______________________________________________________________________________

&MyPharmassessMembersTrailer;

exit(0);
