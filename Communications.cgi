require "D:/RedeemRx/MyData/RBSDesktop_routines.pl";
require "D:/RedeemRx/cgi-bin/cgi-lib.pl";

use File::Basename;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use Env qw(PATH REMOTE_ADDR PERL5LIB PERLLIB);

$| = 1;
my $start = time();
my ($prog, $dir, $ext) = fileparse($0, '\..*');

$title = "$prog";
$title = qq#${COMPANY} - $title# if ( $COMPANY );

#______________________________________________________________________________

&readsetCookies;

&MyPharmassessMembersHeader;

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

$ntitle = "Communications Information";

print qq#<h1>$ntitle</h1>\n#;

print qq#<ul>\n#;

print qq# <li><a href="/members/Broadcast_Communications.cgi">Broadcast Communications</a></li>\n#;
print qq# <li><a href="/members/newsletters.cgi"             >Newsletters</a></li>\n#;
# print qq# <li><a href="/members/thirdpartynotices.cgi"       >Third Party Notices</a></li>\n#;

print qq#</ul>\n#;

#______________________________________________________________________________

&MyPharmassessMembersTrailer;

exit(0);
