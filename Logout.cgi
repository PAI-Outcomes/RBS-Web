require "D:/RedeemRx/MyData/RBSDesktop_routines.pl";
require "D:/RedeemRx/cgi-bin/cgi-lib.pl";

use File::Basename;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use Env qw(PATH REMOTE_ADDR PERL5LIB PERLLIB);

$| = 1;
my $start = time();
my ($prog, $dir, $ext) = fileparse($0, '\..*');
$PROG = "$prog" . "$ext";

$USER    = "";
$PASS    = "";
$RUSER   = "";
$RPASS   = "";
$VALID   = 0;
$isAdmin = 0;
$isMember= 0;
$CUSTOMERID = "";
$LTYPE      = "";
$JPHNPI     =  0;
$JPHLoginID =  0;
$LPERMISSIONLEVEL = "";
$WHICHDB    = "";
$OWNER      = "";
$OWNERPASS  = "";

$PATH = "/";

print qq#Set-Cookie:USER=$USER;             path=$PATH; domain=$cookie_server;\n#;
print qq#Set-Cookie:PASS=$PASS;             path=$PATH; domain=$cookie_server;\n#;
print qq#Set-Cookie:RUSER=$RUSER;           path=$PATH; domain=$cookie_server;\n#;
print qq#Set-Cookie:RPASS=$RPASS;           path=$PATH; domain=$cookie_server;\n#;
print qq#Set-Cookie:VALID=$VALID;           path=$PATH; domain=$cookie_server;\n#;
print qq#Set-Cookie:isAdmin=$isAdmin;       path=$PATH; domain=$cookie_server;\n#;
print qq#Set-Cookie:isMember=$isMember;     path=$PATH; domain=$cookie_server;\n#;
print qq#Set-Cookie:CUSTOMERID=$CUSTOMERID; path=$PATH; domain=$cookie_server;\n#;
print qq#Set-Cookie:JPHNPI=$JPHNPI;         path=$PATH; domain=$cookie_server;\n#;
print qq#Set-Cookie:JPHLoginID=$JPHLoginID; path=$PATH; domain=$cookie_server;\n#;
print qq#Set-Cookie:LPERMISSIONLEVEL=$LPERMISSIONLEVEL; path=$PATH; domain=$cookie_server;\n#;
print qq#Set-Cookie:WHICHDB=$WHICHDB;       path=$PATH; domain=$cookie_server;\n#;
print qq#Set-Cookie:OWNER=$OWNER;           path=$PATH; domain=$cookie_server;\n#;
print qq#Set-Cookie:OWNERPASS=$OWNERPASS;   path=$PATH; domain=$cookie_server;\n#;

print "Location: ../Login.html\n\n";

exit(0);
