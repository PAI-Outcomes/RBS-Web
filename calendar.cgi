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
$FIELDS   = $DBFLDS{"$dbin"};
$FIELDS2  = $DBFLDS{"$dbin"} . "2";
$fieldcnt = $#${FIELDS2} + 2;

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

$date_start = sprintf("%04d%02d%02d", $year, $month, $day);
$date_end   = sprintf("%04d%02d%02d", $year, $month, "31");
$DisplayLines = 0;

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

$dbx = DBI->connect("DBI:mysql:$DBNAME:$DBHOST",$dbuser,$dbpwd,
       { PrintError => 1, RaiseError => 1, InactiveDestroy => 0 } ) || die "$DBI::errstr";
DBI->trace(1) if ($dbitrace);

$ntitle = "Pharmacy Planning Calendar";

print qq#<h1>$ntitle</h1>\n#;

&display_Upcoming_Events;

#______________________________________________________________________________

&MyPharmassessMembersTrailer;

exit(0);

$dbx->disconnect;


#______________________________________________________________________________

sub display_Upcoming_Events {

  $TIMEFRAME{0} = "Day";
  $TIMEFRAME{1} = "Week";
  $TIMEFRAME{2} = "Month";
  $TIMEFRAME{3} = "Year";

  &Read_in_cal_users;
  &Read_Calendar_Events;
  
  #print "DisplayLines: $DisplayLines<br />";
  
  &Display_Calendar_Events;

}

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
        print qq#user_email: $user_email<br>\n#;
        print qq#display_name: $display_name<br>\n#;
        print "<hr>\n";
     }
  }

  print "<br>\nsub Read_in_cal_users. Exit.<br>\n" if ($debug);
}

#______________________________________________________________________________

sub Read_Calendar_Events {
  $DBNAME = "pharm_wp";
  $TABLE  = "cals_aec_event";

  $sql  = qq#
  SELECT id, user_id, title, start, end, repeat_freq, repeat_int, repeat_end, allDay, category_id, description, link, venue, address, city, state, zip, country, contact, contact_info, access, rsvp 
  FROM $DBNAME.$TABLE 
  WHERE end >= CURDATE() 
  ORDER BY start#;

  print "sql:<br>\n$sql<hr>\n" if ($debug);

  my $sthx = $dbx->prepare("$sql");
  $sthx->execute;
  my $NumOfRows = $sthx->rows;
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
	   
	   @pcs = split(' ', $end);
	   (my $date_check = $pcs[0]) =~ s/-//g;
	   
	   if ($date_check >= $date_start && $date_check <= $date_end ) {
	     $DisplayLines++;
	   }
	   
    }
  }
  $sthx->finish;
}

#______________________________________________________________________________

sub Display_Calendar_Events {
  print qq#
  <script type="text/javascript">
    \$(document).ready(function () {
      \$("\#events table tr:gt($DisplayLines)").hide();
      var openorclosed = 1;
      \$('\#moreorless').click(function() {
        if (openorclosed % 2 !== 0) {
          \$("\#events table tr:gt($DisplayLines)").show();
          \$('\#moreorless').html('show less...');
          openorclosed++;
        } else {
          \$("\#events table tr:gt($DisplayLines)").hide();
          \$('\#moreorless').html('show all upcoming events...');
          openorclosed++;
        }
      });
    });
  </script>
  #;

  $found = 0;
  foreach $key (sort { $starts{$a} cmp $starts{$b} } keys %starts) {
     $found++;
     if ( $found == 1 ) {
	    print qq#<div id="events">\n#;
		print qq#<h2>Upcoming Events</h2>\n#;
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
	 
	 $title =~ s/\\\'/\'/g;
	 $description =~ s/\\\'/\'/g;

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
	 print qq#<p style="font-size: 18px;">#;
     print qq#<a id="moreorless" href="\#" onclick="return false;">show all upcoming events...</a>#;
	 print qq#</p>\n#;
	 print "</div>\n"; #events
  } else {
     print "No Events found.\n";
  }
}

#______________________________________________________________________________
