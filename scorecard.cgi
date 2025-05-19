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

$ret = &ReadParse(*in);

&CgiDie("Error in reading and parsing of CGI input") if !defined $ret;

$dbin     = "TPDBNAME";
$db       = $dbin;
$DBNAME   = $DBNAMES{"$dbin"};
$TABLE    = $DBTABN{"$dbin"};
$FIELDS   = $DBTPNDS{"$dbin"};
$FIELDS2  = $DBTPNDS{"$dbin"} . "2";
$fieldcnt = $#${FIELDS2} + 2;

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

&readPharmacies;
&readLogins;

$Pharmacy_Name = $Pharmacy_Names{$inNCPDP};
$inNCPDP = $Pharmacy_NCPDPs{$PH_ID};
$ntitle = "RBS Scorecard";

print qq#<h1>$ntitle</h1>\n#;

&displayScorecard;

#______________________________________________________________________________

&MyPharmassessMembersTrailer;

exit(0);

#______________________________________________________________________________

sub displayScorecard {
  my $webpath = '';
  my $dskpath = '';
  my $newest = 0;
  my $newest_file = '';
  my $newest_file_disp_date = '';
  my $newest_file_ext = '';
  
#  for my $dir (grep -d, glob "D:/WWW/www.pharmassess.com/members/WebShare/RBS_Scorecard/$PH_ID*") {
  for my $dir (grep -d, glob "D:/WWW/members.pharmassess.com/members/WebShare/RBS_Scorecard/$inNCPDP*") {
    $dskpath = $dir;
  }
  
  my @pcs = split('/', $dskpath);
  my $store_dir = pop(@pcs);
  $webpath = qq#/members/WebShare/RBS_Scorecard/$store_dir#;
  
  if (-e $dskpath) {
    (@files) = &readfiles($dskpath);
    foreach $filename (reverse sort {"\L$a" cmp "\L$b"} @files) {
 
      next if ( $filename =~ /Thumbs.db|.swp$|\~$/i );
	  my (@pcs_ext) = split('\.', $filename);
      my (@pcs) = split("_", $filename);
      (my $jdate     = $pcs[1]) =~ s/\.//;
      (my $disp_date = $pcs[1]) =~ s/\./\//;
      if ($jdate > $newest) {
	    $newest = $jdate;
	    $newest_file = $filename;
	    $newest_file_disp_date = $disp_date;
		$newest_file_ext = pop(@pcs_ext);
	  }
  
    }  
  
    print qq#
    <div class="special_program" style="width: 332px;">
    <img src="/images/icons/verified7.png" style="vertical-align: top;" />
    <span class="special_program_text"><a href="$webpath/$newest_file" target="_new">View Your RBS Scorecard - Click Here</a>
    <p style="text-align: right; color: \#BBB;">($newest_file_ext) - posted $newest_file_disp_date</p>
    </span>
    </div>
    #;
	
#	print qq#<p><a href="/members/WebShare/RBS_Scorecard/Documents/RBS Scorecard Outline - Client.pdf"  target="_new">RBS Scorecard Outline - Client</a></p>\n#;
  
    print qq#<p>This scorecard is designed specifically by our staff at Pharm Assess to ensure that your pharmacy is receiving the most value out of your Retail Business Solution (RBS) membership. These scores do not reflect how well your pharmacy is doing as a business, but whether you are taking advantage of all the available services that we offer to our RBS clients.</p>\n#;
  
    print qq#<p>Note: Each program’s score is weighted by the value it can provide your pharmacy.</p>\n#;
  
  } else {
    print qq#<p>No RBS Scorecard was found for your pharmacy.</p>\n#;
  }

  print "sub displayScorecard: Exit.<br>\n" if ($debug);

}

#______________________________________________________________________________
