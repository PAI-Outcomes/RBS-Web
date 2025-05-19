require "D:/RedeemRx/MyData/RBSDesktop_routines.pl";
require "D:/RedeemRx/cgi-bin/cgi-lib.pl";

use File::Basename;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use Env qw(PATH REMOTE_ADDR PERL5LIB PERLLIB);

$| = 1;
my $start = time();
($prog, $dir, $ext) = fileparse($0, '\..*');
$PROG = "$prog" . "$ext";
$nbsp = "&nbsp;";

#______________________________________________________________________________

&readsetCookies;

#______________________________________________________________________________
  
&MyPharmassessMembersHeader;

# Create the inputfile format name
my ($min, $hour, $day, $month, $year) = (localtime)[1,2,3,4,5];
$year  += 1900;	# reported as "years since 1900".
$month += 1;	# reported ast 0-11, 0==January
$syear  = sprintf("%4d", $year);
$smonth = sprintf("%02d", $month);
$sday   = sprintf("%02d", $day);
$tdate  = sprintf("%04d/%02d/%02d", $year, $month, $day);
$ttime  = sprintf("%02d:%02d", $hour, $min);

$amDate  = $syear . $smonth;
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

&displayWebPage;

#______________________________________________________________________________

&MyPharmassessMembersTrailer;

exit(0);

#______________________________________________________________________________

sub displayWebPage {
   print qq#<!-- displayWebPage -->\n#;

   ($PROG = $prog) =~ s/_/ /g;
 
   print qq#<h1>Broadcast Communications to RBS Clients</h1>\n#;
 
   print qq#<div id="textarea2" style="padding-bottom:40px;" class="notices">\n#;
 
   @broadcasts = ("Broadcasts");
 
   print qq#<table>\n#;
#   print qq#<tr><td colspan=2><h2>Broadcast Communications</h2></td></tr>\n#;
   print qq#<tr><th width="100px" class="align_left lj_blue_bb">Date</th> <th class="align_left lj_blue_bb"><span style="padding-left: 15px;">Document</span></th></tr>\n#;
 
   foreach $BC (sort @broadcasts) {
     $webpath = qq#/members/WebShare/$BC#;
     $dskpath = "D:/WWW/members.pharmassess.com/members/WebShare/$BC";
     my ($prog, $dir, $ext);
 
     my $cnt2 = 0;
     (@files) = &readfiles($dskpath);
     foreach $filename (reverse sort {"\L$a" cmp "\L$b"} @files) {
        next if ( $filename =~ /Thumbs.db|.swp$|\~$/i );
        my ($jdate, $rest) = split("_", $filename, 2);
  
        $jdate =~ s/\./-/g;
        if ( $rest ) {
           ($prog, $dir, $ext) = fileparse($rest, qr/\.[^.]*/ );
           $prog =~ s/BIN_PCN/BIN\/PCN/g;
        } else {
           $prog  = $jdate;
           $jdate = $nbsp;
        }
		
	$jdate2 = $jdate;
        $jdate2 =~ s/-//;
		
	if($amDate - $jdate2 < 100) {
          print qq#<tr>\n#;
          
          print qq#<td nowrap><span style="color:\#5FC8ED;">$jdate</span></td> #;
          print qq#<td nowrap><span style="padding-left: 0px;"><a href="$webpath/$filename" target="_blank"><strong>$prog</strong> ($ext)</span></a></td>#;
         
          print qq#</tr>\n#;
        }
        $cnt2++;
     }

     if ( !$cnt2 && $debug ) {
        print qq#<tr><td>$nbsp</td> <td><p>No $BC found</p></td></tr>\n#;
     }
   }
 
   print qq#</table>\n#;
 
   print qq#</div>\n#;
   print qq#<!-- end  textarea2 --> \n#;
}

#______________________________________________________________________________
