#______________________________________________________________________________
#
# Jay Herder
# Date: 11/17/2014
#______________________________________________________________________________
#
require "D:/RedeemRx/MyData/RBSDesktop_routines.pl";
require "D:/RedeemRx/MyData/Common_routines.pl";
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
$isMember   = $in{'isMember'};
$TYPE       = $in{'TYPE'};
$RADIO      = $in{'RADIO'};

($CUSTOMERID) = &StripJunk($CUSTOMERID);
($USER)       = &StripJunk($USER);
($PASS)       = &StripJunk($PASS);
 
($inNPI)      = &StripJunk($inNPI);
($inNCPDP)    = &StripJunk($inNCPDP);
($dispNPI)    = &StripJunk($dispNPI);
($dispNCPDP)  = &StripJunk($dispNCPDP);
($inNCPDP)    = &StripJunk($inNCPDP);
($TYPE)       = &StripJunk($TYPE);

$SORT    = $in{'SORT'};

$inNPI   = $dispNPI   if ( $dispNPI && !$inNPI );
$inNCPDP = $dispNCPDP if ( $dispNCPDP && !$inNCPDP );

$dispNPI   = $inNPI   if ( $inNPI && !$dispNPI );
$dispNCPDP = $inNCPDP if ( $inNCPDP && !$dispNCPDP );

$TYPE = "Weekly" if ( !$TYPE );
$Server_Name = $ENV{'SERVER_NAME'};

$debug++ if ( $verbose );

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

  print "<hr size=4 noshade color=blue>\n";
  my $key;
  foreach $key (sort keys %in) {
     next if ( $key =~ /^PASS\s*$/ );	# skip printing out the password...
     print "key: $key, val: $in{$key}<br>\n";
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

print qq#USER: $USER, VALID: $VALID, isMember: $isMember\n# if ($debug);

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

&readPharmacies;
&readLogins;
# print "dol0: $0<br>prog: $prog<br>dir: $dir<br>ext: $ext<br>\n";
$progext = "${prog}${ext}";

$dbin      = "RWDBNAME";	# RBS Reporting Weekly data
$DBNAMERW  = $DBNAMES{"$dbin"};
$TABLERW   = $DBTABN{"$dbin"};
$FIELDSRW  = $DBFLDS{"$dbin"};
$FIELDS2RW = $DBFLDS{"$dbin"} . "2";

$dbin      = "RMDBNAME";	# RBS Reporting Monthly data
$DBNAMERM  = $DBNAMES{"$dbin"};
$TABLERM   = $DBTABN{"$dbin"};
$FIELDSRM  = $DBFLDS{"$dbin"};
$FIELDS2RM = $DBFLDS{"$dbin"} . "2";

if ( $debug ) {
  print "radio: $radio<br>\n";
  print "RADIO: $RADIO<br>\n";
}

$TIMEFRAME{0} = "Day";
$TIMEFRAME{1} = "Week";
$TIMEFRAME{2} = "Month";
$TIMEFRAME{3} = "Year";

$ntitle = "Upcoming Events";
print qq#<h1 class="rbsreporting">$ntitle</h1>\n#;

%attr = ( PrintWarn=>1, RaiseError=>1, PrintError=>1, AutoCommit=>1, InactiveDestroy=>0, HandleError => \&handle_error );
$dbx = DBI->connect("DBI:mysql:$DBNAME:$DBHOST",$dbuser,$dbpwd, \%attr) || &handle_error;
   
DBI->trace(1) if ($dbitrace);

&Read_in_cal_users;
&Read_Calendar_Events;
&Display_Calendar_Events;

$dbx->disconnect;
 
#______________________________________________________________________________

&MyPharmassessMembersTrailer;

exit(0);

#______________________________________________________________________________

sub Read_in_cal_users {

  print "sub Read_in_cal_users. Entry.<br>\n" if ($debug);

  $DBNAME = "pharm_wp";
  $TABLE  = "cals_users";

  $sql = qq#SELECT ID, user_login, user_pass, user_nicename, user_email, user_url, user_registered, user_activation_key, user_status, display_name FROM $DBNAME.$TABLE#;

  print "sql:<br>\n$sql<hr>\n" if ($debug);

  my $sthx = $dbx->prepare("$sql");
  $sthx->execute;

  my $NumOfRows = $sthx->rows;
  print "Number of rows found: $NumOfRows<br>\n" if ($debug);

  while ( my @row = $sthx->fetchrow_array() ) {
     my ($ID,$user_login,$user_pass,$user_nicename,$user_email,$user_url,$user_registered,$user_activation_key,$user_status,$display_name) = @row;

     $key = $ID;
     $user_logins{$key} = $user_login;
     $user_emails{$key} = $user_email;
     $display_names{$key} = $display_name;

     if ( $debug ) {
        print qq#ID: $ID<br>\n#;
        print qq#user_login: $user_login<br>\n#;
#       print qq#user_pass: $user_pass<br>\n#;
#       print qq#user_nicename: $user_nicename<br>\n#;
        print qq#user_email: $user_email<br>\n#;
#       print qq#user_url: $user_url<br>\n#;
#       print qq#user_registered: $user_registered<br>\n#;
#       print qq#user_activation_key: $user_activation_key<br>\n#;
#       print qq#user_status: $user_status<br>\n#;
        print qq#display_name: $display_name<br>\n#;
        print "<hr>\n";
     }
  }

  print "<br>\nsub Read_in_cal_users. Exit.<br>\n" if ($debug);
}

#______________________________________________________________________________

sub Read_Calendar_Events {

# my $debug++;

  $DBNAME = "pharm_wp";
  $TABLE  = "cals_aec_event";

  $sql  = qq#SELECT id, user_id, title, start, end, repeat_freq, repeat_int, repeat_end, allDay, category_id, description, link, venue, address, city, state, zip, country, contact, contact_info, access, rsvp FROM $DBNAME.$TABLE ORDER BY start#;

  print "sql:<br>\n$sql<hr>\n" if ($debug);

  my $sthx = $dbx->prepare("$sql");
  $sthx->execute;
  my $NumOfRows = $sthx->rows;
  print "Number of rows found: $NumOfRows<br>\n" if ($debug);
  if ( $NumOfRows > 0 ) {

     while ( my @row = $sthx->fetchrow_array() ) {
  
       my ($id,$user_id,$title,$start,$end,$repeat_freq,$repeat_int,$repeat_end,$allDay,$category_id,$description,$link,$venue,$address,$city,$state,$zip,$country,$contact,$contact_info,$access,$rsvp) = @row;
  
       next if ( $user_id == 0 );

       $link = "http://" . $link if ( $link !~ /^\s*$/ && $link !~ /^http/i );
       $key = $id;
       $ids{$key}           = $id;
       $user_ids{$key}      = $user_id;
       $titles{$key}        = $title;
       $starts{$key}        = $start;
       $ends{$key}          = $end;
       $repeat_freqs{$key}  = $repeat_freq;
       $repeat_ints{$key}   = $repeat_int;
       $repeat_ends{$key}   = $repeat_end;
       $allDays{$key}       = $allDay;
       $category_ids{$key}  = $category_id;
       $descriptions{$key}  = $description;
       $links{$key}         = $link;
       $venues{$key}        = $venue;
       $addresss{$key}      = $address;
       $citys{$key}         = $city;
       $states{$key}        = $state;
       $zips{$key}          = $zip;
       $countrys{$key}      = $country;
       $contacts{$key}      = $contact;
       $contact_infos{$key} = $contact_info;
       $accesss{$key}       = $access;
       $rsvps{$key}         = $rsvp;
       print "title: $title, description: $description<br>\n" if ($debug);
    }
  }
  $sthx->finish;
  if ( $debug ) {
     print "sub Read_Calendar_Events. Exit.\n";
     print "<hr>\n";
  }

}

#______________________________________________________________________________

sub Display_Calendar_Events {

# my $debug++;

  print "sub Read_and_Display_Calendar_Events. Entry.<br>\n" if ($debug);


  $found = 0;
  foreach $key (sort { $starts{$a} cmp $starts{$b} } keys %starts) {
     $found++;
     if ( $found == 1 ) {
        print qq#<table class="secondary">\n#;
        print "<tr>";
        print "<th align=left>Date</th> ";
        print "<th align=left>Title</th> ";
        print "<th align=left>Description</th> ";
        print "</tr>";
     }
     $id           = $ids{$key};
     $user_id      = $user_ids{$key};
     $title        = $titles{$key};
     $start        = $starts{$key};
     $end          = $ends{$key};
     $repeat_freq  = $repeat_freqs{$key};
     $repeat_int   = $repeat_ints{$key};
     $repeat_end   = $repeat_ends{$key};
     $allDay       = $allDays{$key};
     $category_id  = $category_ids{$key};
     $description  = $descriptions{$key};
     $link         = $links{$key};
     $venue        = $venues{$key};
     $address      = $addresss{$key};
     $city         = $citys{$key};
     $state        = $states{$key};
     $zip          = $zips{$key};
     $country      = $countrys{$key};
     $contact      = $contacts{$key};
     $contact_info = $contact_infos{$key};
     $access       = $accesss{$key};
     $rsvp         = $rsvps{$key};

     $start =~ s/ 00:00:00//g;
     $end   =~ s/ 00:00:00//g;
     $start =~ s/:00$//;
     $end   =~ s/:00$//;
     my $ADDRESS = qq#$address, $city, $state $zip $country#;
     my $ACHK = $ADDRESS;
     $ACHK =~ s/\s*|,//g; 
     (my $chkend = $end) =~ s/-//g;
     (my $chkrepeatend = $repeat_end) =~ s/-//g;

     if ( $chkrepeatend > $chkend ) {
        my @pcs = split(/\s+/, $chkend, 2);
        $lastday = "$repeat_end $pcs[1]";
     } else {
        $lastday = $end;
     }
     print "<strong>chkend: $chkend, chkrepeatend: $chkrepeatend. Set lastday: $lastday</strong><br>\n" if ($debug);

     $FREQ = "";
     if ( $repeat_freq > 0 ) {
        $FREQ  = "<br>Every ";
        $FREQ .= "$repeat_freq " if ( $repeat_freq > 1 );
        $FREQ .= "$TIMEFRAME{$repeat_int}";
        $FREQ .= "s" if ($repeat_freq > 1);
     }

     if ( $debug ) {
        print qq#id: $id<br>\n#;
        print qq#user_id: $user_id ($user_emails{$user_id})<br>\n#;
        print qq#title: $title<br>\n#;
        print qq#start: $start, end: $end<br>\n#;
        print qq#repeat_freq: $repeat_freq, repeat_int: $repeat_int, repeat_end: $repeat_end<br>\n#;
        print qq#allDay: $allDay<br>\n#;
        print qq#category_id: $category_id<br>\n#;
        print qq#description: $description<br>\n#;
        print qq#link: $link<br>\n#;
        print qq#venue: $venue<br>\n#;
        print qq#Address: $Address<br>\n# if ( $ACHK !~ /^\s*$/ );
        print qq#city: $city<br>\n#;
        print qq#state: $state<br>\n#;
        print qq#zip: $zip<br>\n#;
        print qq#country: $country<br>\n#;
        print qq#Contact: $contact # if ( $contact !~ /^\s*$/ );
        print qq#$contact_info<br>\n# if ( $contact_info !~ /^\s*$/ );
        print qq#access: $access<br>\n#;
        print qq#rsvp: $rsvp<br>\n#;
        print "<hr>\n";
     }
     print qq#<tr>#;
     print qq#<td>$start #;
     print qq#thru $lastday $FREQ # if ( $lastday ne $start );
     print qq#</td>#;
     if ( $link =~ /^\s*$/ ) {
        print qq#<td>$title</td>#;
     } else {
        print qq#<td><a href="$link" target=_Blank>$title</a></td>#;
     }
     print qq#<td>$description</td>#;
     print qq#</tr>\n#;
  }

  if ( $found > 0 ) {
     print "</table>\n";
  } else {
     print "No Events found.\n";
  }

  print "<br>\nsub Display_Calendar_Events. Exit.<br>\n" if ($debug);
}

#______________________________________________________________________________
