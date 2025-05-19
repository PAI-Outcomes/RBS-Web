require "D:/RedeemRx/MyData/RBSDesktop_routines.pl";
require "D:/RedeemRx/cgi-bin/cgi-lib.pl";

use File::Basename;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use Env qw(PATH REMOTE_ADDR PERL5LIB PERLLIB);
use DateTime;

$| = 1; 
my $start = time();
my ($prog, $dir, $ext) = fileparse($0, '\..*');
$PROG = "$prog" . "$ext";

$ret = &ReadParse(*in);
&CgiDie("Error in reading and parsing of CGI input") if !defined $ret;

$WHICHDB    = $in{'WHICHDB'};

$USER       = $in{'USER'};
$PASS       = $in{'PASS'};

($WHICHDB)  = &StripJunk($WHICHDB);
if ($USER =~ /demorbsdirect/i) {
  $WHICHDB = 'Webinar';
}

$PROGRAM = 'RBS|Cred|VacOnly|Special Programs|RBSDirect';

($isMember, $USER_ID, $TYPE, $PH_ID, $LEVEL, $PharmacyCount) = &isAuthorizedMember($USER, $PASS, $PROGRAM);
if ($isMember) {
&readPharmacies;



  print "Set-Cookie:USER=$USER_ID;           path=/; domain=$cookie_server;\n";
  print "Set-Cookie:LOGIN=$USER;             path=/; domain=$cookie_server;\n";
  print "Set-Cookie:TYPE=$TYPE;              path=/; domain=$cookie_server;\n";
  print "Set-Cookie:PROGRAM=$PROGRAM;        path=/; domain=$cookie_server;\n";
  print "Set-Cookie:PH_ID=$PH_ID;            path=/; domain=$cookie_server;\n" if ($TYPE =~ /User/i);
  print "Set-Cookie:PH_COUNT=$PharmacyCount; path=/; domain=$cookie_server;\n";
  print "Set-Cookie:WHICHDB=$WHICHDB;        path=/; domain=$cookie_server;\n";
  print "Set-Cookie:RBSHeader='';            path=/; domain=$cookie_server;\n";

  if(($Pharmacy_Types{$PH_ID} =~ /RBS Direct/) && $Pharmacy_Types{$PH_ID} !~ /RBS$/ && $Pharmacy_Types{$PH_ID} !~ /RBS:/) {
    print "Set-Cookie:RBSHeader=RBSDirectHeader.html;  path=/; domain=$cookie_server;\n" if ($TYPE =~ /User/i);
  }
  else {
    print "Set-Cookie:RBSHeader=PharmassessMembersHeader.html; path=/; domain=$cookie_server;\n" if ($TYPE =~ /User/i);
  }
}
else {
   print "Location: ../Login.html\n\n";
   exit(0);
}

#if ( $TYPE =~ /Admin/i || ($TYPE =~ /SuperUser/i && $PharmacyCount > 1) ) {
if ( $TYPE =~ /Admin/i || $PharmacyCount > 1 ) {
  &logActivity($USER, "SuperUser Logged in to Pharmassess", NULL);
  print "Location: home_super.cgi\n\n";
} else {
  &logActivity($USER, "Logged in to Pharmassess", $PH_ID);
  print "Location: home.cgi\n\n";
}

exit(0);

