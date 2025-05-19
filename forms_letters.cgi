require "D:/RedeemRx/MyData/RBSDesktop_routines.pl";
require "D:/RedeemRx/cgi-bin/cgi-lib.pl";

use File::Basename;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use Env qw(PATH REMOTE_ADDR PERL5LIB PERLLIB);

$| = 1; 
my $start = time();
my ($prog, $dir, $ext) = fileparse($0, '\..*');
$nbsp = "&nbsp\;";

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

$Pharmacy_Name = $Pharmacy_Names{$PH_ID};
$ntitle = "Forms and Letters for $Pharmacy_Name";

print qq#<h1>$ntitle</h1>\n#;

&displayFL;

#______________________________________________________________________________

&MyPharmassessMembersTrailer;

exit(0);

#______________________________________________________________________________

sub displayFL {
  print qq#<!-- displayFL -->\n#;

  print qq#  <div id="textarea2" style="padding-bottom:40px;" class="notices">\n#;

  @formletters = ("Forms", "Letters");

  print qq#<table cellspacing=1 cellpadding=9>\n#;
  print qq#<tr><th class="align_left lj_blue_bb"><span style="padding-left: 15px;">Document</span></th></tr>\n#;

  foreach $FL (sort @formletters) {
    $webpath = qq#/members/WebShare/$FL#;
    $dskpath = "D:/WWW/members.pharmassess.com/members/WebShare/$FL";

    my $cnt = 0;
    (@files) = &readfiles("$dskpath");
    foreach $filename (sort { "\L$a" cmp "\L$b" } @files) {
       my ($prog, $dir, $ext) = fileparse($filename, qr/\.[^.]*/ );
       print qq#<tr>\n#;
       print qq#<td nowrap><a href="$webpath/$filename" target="_blank"><strong>$prog</strong> ($ext)</a></td>#;
       print qq#</tr>\n#;
  
       $cnt++;
    }
  }

  print qq#</table>\n#;

  print qq#  </div>\n#;
  print qq#  <!-- end  textarea2 --> \n#;
}

#______________________________________________________________________________
