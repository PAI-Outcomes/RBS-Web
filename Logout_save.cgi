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

&MyPharmassessMembersHeaderLO;

#______________________________________________________________________________

if ( !$USER && !$PASS && !$VALID ) {
} else {
  $USER        = "";
  $PASS        = "";
  $RUSER       = "";
  $RPASS       = "";
  $VALID       =  0;
  $NEWPASS     = "";
  $CUSTOMERID  = "";
  $LTYPE       = "";
  $LDATEADDED  = "";
  $LFIRSTLOGIN = "";
  $LPERMISSIONLEVEL = "";
  $WHICHDB     = "";
  $OWNER       = "";
  $OWNERPASS   = "";
  
  $submitvalue = "Log Out";
  my $URL = "Logout.cgi";
  print qq#<FORM ACTION="$URL" METHOD="POST">\n#;
  print qq#<INPUT TYPE="hidden" NAME="debug"      VALUE="$debug">\n#;
  print qq#<INPUT TYPE="hidden" NAME="verbose"    VALUE="$verbose">\n#;
  print qq#<INPUT TYPE="hidden" NAME="USER"       VALUE="$USER">\n#;
  print qq#<INPUT TYPE="hidden" NAME="PASS"       VALUE="$PASS">\n#;
  print qq#<INPUT TYPE="hidden" NAME="RUSER"      VALUE="$RUSER">\n#;
  print qq#<INPUT TYPE="hidden" NAME="RPASS"      VALUE="$RPASS">\n#;
  print qq#<INPUT TYPE="hidden" NAME="VALID"      VALUE="$VALID">\n#;
  print qq#<INPUT TYPE="hidden" NAME="NEWPASS"    VALUE="$NEWPASS">\n#;
  print qq#<INPUT TYPE="hidden" NAME="CUSTOMERID" VALUE="$CUSTOMERID">\n#;
  print qq#<INPUT TYPE="hidden" NAME="LTYPE"      VALUE="$LTYPE">\n#;
  print qq#<INPUT TYPE="hidden" NAME="LDATEADDED" VALUE="$LDATEADDED">\n#;
  print qq#<INPUT TYPE="hidden" NAME="isAdmin"    VALUE="$isAdmin">\n#;
  print qq#<INPUT TYPE="hidden" NAME="isMember"   VALUE="$isMember">\n#;
  print qq#<INPUT TYPE="hidden" NAME="CUSTOMERID" VALUE="$CUSTOMERID">\n#;
  print qq#<INPUT TYPE="hidden" NAME="LPERMISSIONLEVEL" VALUE="$LPERMISSIONLEVEL">\n#;
  print qq#<INPUT TYPE="hidden" NAME="WHICHDB"    VALUE="$WHICHDB">\n#;
  print qq#<INPUT TYPE="hidden" NAME="OWNER"      VALUE="$OWNER">\n#;
  print qq#<INPUT TYPE="hidden" NAME="OWNERPASS"  VALUE="$OWNERPASS">\n#;
  print qq#<H3><INPUT TYPE="Submit" VALUE="$submitvalue"></H3>\n#;
  
  print "</FORM>\n";

  &trailer;
}
#
#______________________________________________________________________________

print qq#</BODY>\n#;
print qq#</HTML>\n#;

exit(0);
