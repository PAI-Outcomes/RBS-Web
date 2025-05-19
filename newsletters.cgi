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

$Pharmacy_Name = $Pharmacy_Names{$PH_ID};
$ntitle = "Newsletters for $Pharmacy_Name";

print qq#<h1>$ntitle</h1>\n#;

$amDate  = $syear . $smonth;

&displayNL;

#______________________________________________________________________________

&MyPharmassessMembersTrailer;

exit(0);

#______________________________________________________________________________

sub displayNL {
  print qq#<!-- displayNL -->\n#;

#  print qq#  <div id="textarea2" style="padding-bottom:40px;" class="notices">\n#;

  @newsletters = ("Newsletters");

  print qq#<table cellspacing=1 cellpadding=9>\n#;
  print qq#<tr><th width="100px" class="align_left lj_blue_bb">Date</th> <th class="align_left lj_blue_bb"><span style="padding-left: 15px;">Document</span></th></tr>\n#;

  foreach $NL (sort @newsletters) {
    $webpath = qq#/members/WebShare/$NL#;
    $dskpath = "D:/WWW/members.pharmassess.com/members/WebShare/$NL";

    my $cnt = 0;
    (@files) = &readfiles("$dskpath");
    foreach $filename ( reverse sort { "\L$a" cmp "\L$b" } @files) {
       if ( $filename =~ /^[0-9][0-9][0-9][0-9]/ ) {
          ($jdate, $rest) = split("_", $filename, 2);
          $jdate =~ s/\./-/g;
       } else {
          $jdate = "&lt;BLANK&gt;";
          $rest  = "$filename";
       }
       my ($prog, $dir, $ext) = fileparse($rest, qr/\.[^.]*/ );

       $jdate2 = $jdate;
       $jdate2 =~ s/-//;
	   
       if($amDate - $jdate2 < 100){
           print qq#<tr>\n#;
           print qq#<td nowrap align=left><span class="notice-date">$jdate</span></td> #;
           print qq#<td nowrap><a href="$webpath/$filename" target="_blank"><strong>$prog</strong> ($ext)</a></td>#;
           print qq#</tr>\n#;
       }
       $cnt++;
    }
  }

  print qq#</table>\n#;

  print qq#  </div>\n#;
  print qq#  <!-- end  textarea2 --> \n#;
}

#______________________________________________________________________________
