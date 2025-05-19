require "D:/RedeemRx/MyData/RBSDesktop_routines.pl";
require "D:/RedeemRx/cgi-bin/cgi-lib.pl";

use File::Basename;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use Env qw(PATH REMOTE_ADDR PERL5LIB PERLLIB);

$| = 1;
my $start = time();
my ($prog, $dir, $ext) = fileparse($0, '\..*');
my $email   = 'RBS@TDSClinical.com';
my $program = 'Pharm AssessRBS';

#______________________________________________________________________________

&readsetCookies;

&read_canned_header($RBSHeader);
 $email   = 'RBSDirect@TDSClinical.com' if ($RBSHeader =~ /Direct/);
 $program = 'RBS Direct'                if ($RBSHeader =~ /Direct/);
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

$Pharmacy_Name = $Pharmacy_Names{$PH_ID};
$ntitle = "<i>Let Us Know</i> Assistance for $Pharmacy_Name";

print qq#<h1>$ntitle</h1>\n#;

&displayLetUsKnow;

#______________________________________________________________________________

&MyPharmassessMembersTrailer;

exit(0);

#______________________________________________________________________________

sub displayLetUsKnow {
  print qq#<!-- displayLetUsKnow -->\n#;

  print qq#Thank you for choosing $program. We are here to assist you.<br><br>\n#;

  print qq#If you have questions, comments, or changes required to the information in the Members section of this website, please let us know so we can provide the requested assistance for your Pharmacy.<br><br>\n#;

  print qq#<table cellpadding=4 cellspacing=4 border=0>\n#;
  $URL = qq#mailto:$email\?subject=$program Members pages - Let Us Know email from $Pharmacy_Name#;
  print qq#<tr><th align=left>Email:</th>     <td><a href="$URL">$email</a></td></tr>\n#;
  print qq#<tr><th align=left>Phone:</th>     <td>(913) 897-4343</td></tr>\n#;
  print qq#<tr><th align=left>Fax:</th>       <td>(888) 825-6670</td></tr>\n#;
  print qq#<tr><th align=left>Toll Free:</th> <td>(888) 255-6526</td></tr>\n#;
  print qq#</table>\n#;
  
  print qq#<br />\n#;
  print qq#<table width="600px">\n#;
  print qq#<tr><td colspan=2><h2>Regular Business Hours</h2></td></tr>\n#;
  print qq#<tr><td>Mon-Fri</td><td>8:30am - 5:30pm CST</td></tr>\n#;
  print qq#<tr><td>Sat-Sun</td><td>Closed</td></tr>\n#;
  print qq#<tr><td colspan=2><h2>Closed on the following holidays:</h2></td><tr>\n#;
  print qq#<tr><td colspan=2><i>Memorial Day, Independence Day, Labor Day, Thanksgiving Day, Day After Thanksgiving, Christmas Eve, Christmas Day, New Year's Eve, and New Year's Day</i></td></tr>\n#;
  print qq#</table>\n#;
}

#______________________________________________________________________________
