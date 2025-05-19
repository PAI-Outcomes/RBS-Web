#______________________________________________________________________________
#
# Jay Herder
# Date: 10/03/2012
# Mods: 07/17/2015. Renamed "ANDA" to "MAC_Busters"
##
#______________________________________________________________________________
#
require "D:/RedeemRx/MyData/RBSDesktop_routines.pl";
require "D:/RedeemRx/cgi-bin/cgi-lib.pl";

use File::Basename;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use Env qw(PATH REMOTE_ADDR PERL5LIB PERLLIB);

$| = 1; # don't buffer output
#______________________________________________________________________________
#
my $start = time();
my ($prog, $dir, $ext) = fileparse($0, '\..*');
#####print "dol0: $0\nprog: $prog, dir: $dir, ext: $ext\n";
my $help = qq|\n\nExecute as "$prog " without debug, or add " -d" for debug|;
my $debug;
my $verbose;
$nbsp = "&nbsp\;";
my %HoH = (); 	# "Hash of Hashes"...

#$uberdebug++;
if ( $uberdebug ) {
  $incdebug++;
  $debug++;
  $verbose++;
}
#####$dbitrace++;

$title = "$prog";
$title = qq#${COMPANY} - $title# if ( $COMPANY );

#_____________________________________________________________________________________
#
# Create HTML to display results to browser.
#______________________________________________________________________________
#
$ret = &ReadParse(*in);

# A bit of error checking never hurt anyone
&CgiDie("Error in reading and parsing of CGI input") if !defined $ret;


$debug   = $in{'debug'}   if (!$debug);
$verbose = $in{'verbose'} if (!$verbose);

$USER       = $in{'USER'};
$PASS       = $in{'PASS'};
$VALID      = $in{'VALID'};
$isAdmin    = $in{'isAdmin'};
$CUSTOMERID = $in{'CUSTOMERID'};

($CUSTOMERID) = &StripJunk($CUSTOMERID);
($USER)     = &StripJunk($USER);
($PASS)     = &StripJunk($PASS);
 
($inNPI)      = &StripJunk($inNPI);
($inNCPDP)    = &StripJunk($inNCPDP);
($dispNPI)    = &StripJunk($dispNPI);
($dispNCPDP)  = &StripJunk($dispNCPDP);
($inNCPDP)    = &StripJunk($inNCPDP);

$SORT    = $in{'SORT'};

$inNPI   = $dispNPI   if ( $dispNPI && !$inNPI );
$inNCPDP = $dispNCPDP if ( $dispNCPDP && !$inNCPDP );

$dispNPI   = $inNPI   if ( $inNPI && !$dispNPI );
$dispNCPDP = $inNCPDP if ( $inNCPDP && !$dispNCPDP );

$debug++ if ( $verbose );
$dbin     = "TPDBNAME";
$db       = $dbin;
$DBNAME   = $DBNAMES{"$dbin"};
$TABLE    = $DBTABN{"$dbin"};
$FIELDS   = $DBFLDS{"$dbin"};
$FIELDS2  = $DBFLDS{"$dbin"} . "2";
$fieldcnt = $#${FIELDS2} + 2;

my $HASH   = $HASHNAMES{$dbin};

#______________________________________________________________________________

&readsetCookies;

if ( $USER ) {
   $inNCPDP   = $USER;
   $dispNCPDP = $USER;
} else {
   $inNCPDP   = $in{'inNCPDP'};
   $dispNCPDP = $in{'dispNCPDP'};
}
if ( $PASS ) {
   $inNPI   = $PASS;
   $dispNPI = $PASS;
} else {
   $inNPI   = $in{'inNPI'};
   $dispNPI = $in{'dispNPI'};
}

#______________________________________________________________________________

&MyPharmassessMembersHeader;

print "In DEBUG   mode<br>\n" if ($debug);
print "In VERBOSE mode<br>\n" if ($verbose);

if ( $debug ) {
  print "dbin: $dbin, db: $db, DBNAME: $DBNAME, TABLE: $TABLE<br>\n";
  print "FIELDS : $FIELDS, FIELDS2: $FIELDS2, fieldcnt: $fieldcnt<br>\n";

# print "<hr size=4 noshade color=blue>\n";
# print "JJJ:<br>\n";
  my $key;
  foreach $key (sort keys %in) {
     next if ( $key =~ /^PASS\s*$/ );	# skip printing out the password...
#    print "key: $key, val: $in{$key}<br>\n" if ($debug);
  }
  print "<hr size=4 noshade color=blue>\n";
}
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

print "\nProg: $prog &nbsp; &nbsp;<br>Date: $tdate &nbsp; Time: $ttime<P>\n" if ($debug);
#______________________________________________________________________________

($isMember, $VALID) = &isMember($USER, $PASS);

print qq#USER: $USER, PASS: $PASS, VALID: $VALID, isMember: $isMember\n# if ($debug);

if ( $VALID && $isMember ) {

   &MembersHeaderBlock;

} else {

   &MembersLogin;

   &MyPharmassessMembersTrailer;

   print qq#</BODY>\n#;
   print qq#</HTML>\n#;
   exit(0);
}

#______________________________________________________________________________

print "<P>SORT: $SORT, dbin: $dbin<br>\n" if ($debug);

$HEADPREFIX = "VN";
#______________________________________________________________________________

&readPharmacies;
&readLogins;

$FirstName = $LFirstNames{$USER};
$LastName  = $LLastNames{$USER};

$Pharmacy_Name = $Pharmacy_Names{$inNCPDP};
$ntitle = "MAC Buster Specials for $Pharmacy_Name";

print qq#<h1>$ntitle</h1>\n#;

&displayMB;

#______________________________________________________________________________

&MyPharmassessMembersTrailer;

exit(0);

#______________________________________________________________________________

sub displayMB {

  print qq#<!-- displayMB -->\n#;
  print "sub displayMB: Entry.<br>\n" if ($debug);

  print qq#  <div id="textarea2" style="padding-bottom:40px;" class="notices">\n#;

  @MAC_Busters = ("MAC_Busters_RBS");

  print qq#<table cellspacing=1 cellpadding=9>\n#;

  foreach $NL (sort @MAC_Busters) {

    # Read in all $NL items for this Pharmacy
    $webpath = qq#/members/WebShare/$NL#;
    $dskpath = "D:/WWW/www.pharmassess.com/members/WebShare/$NL";

    print "dskpath: $dskpath<br>\n" if ($debug);
 
    my $cnt = 0;
    (@files) = &readfiles("$dskpath");
    foreach $filename ( reverse sort { "\L$a" cmp "\L$b" } @files) {
       print "filename: $filename<br>\n" if ($debug);

       if ( $filename =~ /^[0-9][0-9][0-9][0-9]/ ) {
          print "Numeric! - $filename<br>\n" if ($debug);
          ($jdate, $rest) = split("_", $filename, 2);
          $jdate =~ s/\./-/g;
       } else {
          print "Normal! - $filename<br>\n" if ($debug);
          $jdate = "&lt;BLANK&gt;";
          $rest  = "$filename";
       }
       print "filename: $filename, prog: $prog, dir: $dir, ext: $ext<br>\n" if ($debug);
       my ($prog, $dir, $ext) = fileparse($rest, qr/\.[^.]*/ );
       if ( $cnt == 0 ) {
         print qq#<tr><td colspan=2><h2>$NL</h2></td></tr>\n#;
       }
       print qq#<tr>\n#;
       print qq#<td nowrap align=left><p><span class="notice-date">$jdate</span></p></td> #;
       print qq#<td nowrap><p><a href="$webpath/$filename" target="_blank"><strong>$prog</strong> ($ext)</a></p></td>#;
       print qq#</tr>\n#;
  
       $cnt++;
    }
    if ( !$cnt  ) {
       print qq#<tr><td>$nbsp</td> <td><p>No MAC Buster Specials found.</p></td></tr>\n#;
    }
    print qq#<tr><th colspan=2 align=left>$nbsp</th></tr>\n#;
  }

  print qq#</table>\n#;

  print qq#  </div>\n#;
  print qq#  <!-- end  textarea2 --> \n#;

  print "sub displayMB: Exit.<br>\n" if ($debug);

}

#______________________________________________________________________________
