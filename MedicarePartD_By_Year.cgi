require "D:/RedeemRx/MyData/RBSDesktop_routines.pl";
require "D:/RedeemRx/cgi-bin/cgi-lib.pl";

use File::Basename;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use Env qw(PATH REMOTE_ADDR PERL5LIB PERLLIB);

$| = 1;
my $start = time();
my ($prog, $dir, $ext) = fileparse($0, '\..*');
$nbsp = "&nbsp\;";

$ret = &ReadParse(*in);
&CgiDie("Error in reading and parsing of CGI input") if !defined $ret;

$dbin     = "TPDBNAME";
$db       = $dbin;
$DBNAME   = $DBNAMES{"$dbin"};
$TABLE    = $DBTABN{"$dbin"};
$FIELDS   = $DBFLDS{"$dbin"};
$FIELDS2  = $DBFLDS{"$dbin"} . "2";
$fieldcnt = $#${FIELDS2} + 2;
$YEAR = $in{year};
my ($ENV) = &What_Env_am_I_in;

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

$ntitle = "CIPN Medicare Part D Information";

#print qq#<h1>$ntitle</h1>\n#;

&displayMPD;

#______________________________________________________________________________

&MyPharmassessMembersTrailer;

exit(0);

#______________________________________________________________________________

sub displayMPD {
  print qq#<!-- displayMPD -->\n#;

  print qq#<div id="textarea2" style="padding-bottom:40px;" class="notices">\n#;
  
  &process_notifications;
  
  print qq#<br /><p style="font-size: 16px;"><strong><a href="PrefNetSU.cgi" >Medicare - Preferred Network Letter Template</a></strong></p>\n#;
  ##$planfile = sprintf("%04d_Plan_Information", $YEAR);
  @medicaredocs = ("$YEAR");

  #print qq#<hr>\n#;
  print qq#<table cellspacing=1 cellpadding=9>\n#;

  foreach $MPD (sort @medicaredocs) {

    # Read in all $MPD items for this Pharmacy
    $webpath = qq#/members/WebShare/MedicarePartD/Plan Information/$MPD#;
    $dskpath = "D:/WWW/members.pharmassess.com/members/Webshare/MedicarePartD/Plan Information/$MPD";

    my $cnt = 0;
    (@files) = &readfiles("$dskpath");

    foreach $file (@files) {
       my ($year, $name) = split("_", $file, 2);
       $name = lc($name);
       $fhash{$file} = $name;
       $yhash{$file} = $year;
    }

#   foreach $filename ( sort { $yhash{$b} <=> $yhash{$a} || $fhash{$a} cmp $fhash{$b} } keys %fhash ) 

    foreach $filename ( sort { $yhash{$a} cmp $yhash{$b} || $fhash{$a} cmp $fhash{$b} } keys %fhash ) {
       if ( $filename =~ /^[0-9][0-9][0-9][0-9]_/ ) {
          ($jdate, $rest) = split("_", $filename, 2);
          $jdate =~ s/\./-/g;
       } else {
          $jdate = "$nbsp";		#	"&lt;BLANK&gt;";
          $rest  = "$filename";
       }
       my ($prog, $dir, $ext) = fileparse($rest, qr/\.[^.]*/ );
       if ( $cnt == 0 ) {
         print qq#<tr><td colspan=2><h2>$YEAR Documents</h2></td></tr>\n#;
       }
       print qq#<tr>\n#;
       print qq#<td nowrap align=left><p><span class="notice-date">$jdate</span></p></td> #;
       print qq#<td nowrap><p><a href="${webpath}/${filename}?v=${today}"><strong>$prog</strong> ($ext)</a></p></td>#;
       print qq#</tr>\n#;
  
       $cnt++;
    }
    if ( $cnt ) {
    } else {
       print qq#<tr><td colspan=2><h2>Documents</h2></td></tr>\n#;
       print qq#<tr><td>$nbsp</td> <td><p>No $MPD found</p></td></tr>\n#;
    }
    print qq#<tr><th colspan=2 align=left>$nbsp</th></tr>\n#;
  }
  print qq#</table>\n#;
  
  print qq#<hr /><br /><strong>Helpful Links:</strong><br />\n#;
  print qq#<ul>\n#;
  print qq#<li><a href="https://www.medicare.gov/find-a-plan/questions/home.aspx" target="_BLANK">Medicare Part D Plan Finder Tool</a></li>\n#;
  print qq#<li><a href="http://www.cms.gov" target="_BLANK">www.cms.gov</a></li>\n#;
  print qq#<li><a href="http://www.medicare.gov" target="_BLANK">www.medicare.gov</a></li>\n#;
  print qq#</ul>\n#;
  
  print qq#<br /><br /><a href="javascript:history.go(-1)"> Go Back </a><br>\n#;

  print qq#  </div>\n#;
  print qq#  <!-- end  textarea2 --> \n#;
}

#______________________________________________________________________________

sub process_notifications {
   
   print "
   <style>
   .notification p {
     margin-bottom: 15px !important;
   }
   </style>
   ";

   my $filename = "D:/WWW/www.CIPNetwork.com/Webshare/MedicarePartD/notification/MedD_Notification.txt";

   if ( -e "$filename" ) {	 
     print qq#<div class="notification white">\n#;
     open (FILE, "< $filename") || warn "Couldn't open file.<br>\n$!<br>\n";
     while (<FILE>) {
       chomp;
       my $line = $_;
       #$line = $nbsp if ( $line =~ /^\s*$/ );
       #print qq#$line<br />\n#;
	   print qq#$line\n#;
     }
     print qq#</div>\n#;
     close(FILE);
   }
}

#______________________________________________________________________________
