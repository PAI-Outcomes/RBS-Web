#______________________________________________________________________________
#
# Jay & Josh Herder
# Date: 10/23/2012
# Mods: 08/27/2013. Major changes
# Mods: 10/31/2013. Changed SuperUser Select Routines
# Mods: 11/20/2014. Added Upcoming Events (student Grant's project)
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
  $debug++;
  $verbose++;
# $incdebug++;
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
$OLTYPE     = $in{'OLTYPE'};
$LDATEADDED = $in{'LDATEADDED'};
$RUSER      = $in{'RUSER'};
$RPASS      = $in{'RPASS'};
$WHICHDB    = $in{'WHICHDB'};
$OWNER      = $in{'OWNER'};
$OWNERPASS  = $in{'OWNERPASS'};

$inPharmacy = $in{'inPharmacy'};
$inNPI      = $in{'inNPI'};
$inNCPDP    = $in{'inNCPDP'};
$dispNPI    = $in{'dispNPI'};
$dispNCPDP  = $in{'dispNCPDP'};

$SAVEVALID  = $VALID;

($CUSTOMERID) = &StripJunk($CUSTOMERID);
($USER)     = &StripJunk($USER);
#($PASS)     = &StripJunk($PASS);
($RUSER)    = &StripJunk($RUSER);
#($RPASS)    = &StripJunk($RPASS);
($WHICHDB)  = &StripJunk($WHICHDB);

($inNPI)    = &StripJunk($inNPI);
($inNCPDP)  = &StripJunk($inNCPDP);
($dispNPI)  = &StripJunk($dispNPI);
($dispNCPDP)= &StripJunk($dispNCPDP);
($inNCPDP)  = &StripJunk($inNCPDP);


$inNPI   = $dispNPI   if ( $dispNPI && !$inNPI );
$inNCPDP = $dispNCPDP if ( $dispNCPDP && !$inNCPDP );

$dispNPI   = $inNPI   if ( $inNPI && !$dispNPI );
$dispNCPDP = $inNCPDP if ( $inNCPDP && !$dispNCPDP );

$debug++ if ( $verbose );

$dbin     = "PHDBNAME";
$db       = $dbin;
$DBNAME   = $DBNAMES{"$dbin"};
$TABLE    = $DBTABN{"$dbin"};
$FIELDS   = $DBFLDS{"$dbin"};
$FIELDS2  = $DBFLDS{"$dbin"} . "2";
$fieldcnt = $#${FIELDS2} + 2;

my $HASH   = $HASHNAMES{$dbin};

$USER = $RUSER if ( !$USER && $RUSER );
$PASS = $RPASS if ( !$PASS && $RPASS );


my @NCPDParray = ();

#______________________________________________________________________________

&readPharmacies;
 
# $UpDB_NCPDP = $in{"UpDB_NCPDP"};
# $UpDB_NPI   = $in{"UpDB_NPI"};
# if ( $UpDB_NCPDP && $UpDB_NCPDP !~ /^\s*$/ ) {
   # $RUSER = $UpDB_NCPDP;
   # $RPASS = $Pharmacy_NPIs{$RUSER};
   # $USER  = $RUSER;
   # $PASS  = $RPASS;
# }
# if ( $UpDB_NPI && $UpDB_NPI !~ /^\s*$/ ) {
   # $RUSER = $Reverse_Pharmacy_NPIs{$UpDB_NPI};
   # $RPASS = $UpDB_NPI;
   # $USER  = $RUSER;
   # $PASS  = $RPASS;
# }

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

&readsetCookies;

($isMember, $VALID) = &isMember($USER, $PASS);
if ( $isMember && $VALID ) {
  # Great!
} else {
  # Check to see if they are in the "VacOnly" program
  ($isMemberVac, $VALIDVac) = &isVacMember($USER, $PASS);
  $isMember  = $isMemberVac;
  $VALID     = $VALIDVac;
  unless ( $isMember && $VALID ) {
    # Check to see if they are in the "Special Programs" program
    ($isMemberSP, $VALIDsp) = &isSPMember($USER, $PASS);
    $isMember  = $isMemberSP;
    $VALID     = $VALIDsp;
  }
}

$SAVEUSER = $USER;

if ($isMember && $VALID && $Login_Auth{$USER} =~ /SuperUser/i ) {
  $RUSER     = $USER;
  $RPASS     = $PASS;
  $inNCPDP   = $in{'inNCPDP'}   || '';
  $dispNCPDP = $in{'dispNCPDP'} || '';
  $inNPI     = $in{'inNPI'}     || '';
  $dispNPI   = $in{'dispNPI'}   || '';
  $OWNER      = "";
  $OWNERPASS  = "";
  
  print qq#Set-Cookie:RUSER=$RUSER;           path=/; domain=$cookie_server;\n#;
  print qq#Set-Cookie:RPASS=$RPASS;           path=/; domain=$cookie_server;\n#;
  print qq#Set-Cookie:OWNER=$OWNER;           path=/; domain=$cookie_server;\n#;
  print qq#Set-Cookie:OWNERPASS=$OWNERPASS;   path=/; domain=$cookie_server;\n#;
  
} elsif ($isMember && $VALID) {
  $RUSER     = $Login_NCPDP{$USER} || '';
  $RPASS     = $Login_NPI{$USER}   || '';
  $inNCPDP   = $Login_NCPDP{$USER} || '';
  $dispNCPDP = $Login_NCPDP{$USER} || '';
  $inNPI     = $Login_NPI{$USER}   || '';
  $dispNPI   = $Login_NPI{$USER}   || '';
  
  $USER      = $Login_NCPDP{$USER} || '';
  $PASS      = $inNPI              || '';
  
  print qq#Set-Cookie:USER=$USER;              path=/; domain=$cookie_server;\n#;
  print qq#Set-Cookie:PASS=$PASS;              path=/; domain=$cookie_server;\n#;
  print qq#Set-Cookie:RUSER=$inNCPDP;          path=/; domain=$cookie_server;\n#;
  print qq#Set-Cookie:RPASS=$inNPI;            path=/; domain=$cookie_server;\n#;
}

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

if ( $debug ) {
  print qq#<hr>\n#;
  print qq#PROGRAM: $PROGRAM<br>\n#;
  print qq#Login_Auth($USER): $Login_Auth{$USER}<br>\n#;
  print qq#USER: $USER, PASS: $PASS, OWNER: $OWNER<br>\n#;
  print qq#isMember: $isMember, VALID: $VALID<br>\n#;
  print qq#isMemberVac: $isMemberVac, VALIDVac: $VALIDVac<br>\n#;
  print qq#<hr>\n#;
}

if ( $isMember && $VALID ) {

   &MembersHeaderBlock;

   my $Licenses_Okay   = 0;
   my $Licenses_Broken = "";
   ($Licenses_Okay, $Licenses_Broken) = &Validate_No_Expired_Licenses($RUSER, $inNPI);
   print "Licenses_Okay: $Licenses_Okay<br>Licenses_Broken: $Licenses_Broken<hr>\n" if ($debug);

   if ( !$Licenses_Okay ) {
      &display_Expired_Page($Licenses_Broken);
   }

} else {

#print qq#<hr>\n#;
#print qq#PROGRAM: $PROGRAM<br>\n#;
#print qq#USER: $USER, PASS: $PASS, OWNER: $OWNER<br>\n#;
#print qq#isMember: $isMember, VALID: $VALID<br>\n#;
#print qq#isMemberVac: $isMemberVac, VALIDVac: $VALIDVac<br>\n#;
#print qq#<hr>\n#;

   &MembersLogin;
   &MyPharmassessMembersTrailer;

   print qq#</BODY>\n#;
   print qq#</HTML>\n#;
   exit(0);
}

#______________________________________________________________________________

if ( $debug ) {
   print "<hr>\n";
   print "Pharmacy Type: $Pharmacy_Types{$inNCPDP}<br>\n";
   print "VacOnly Start: $Pharmacy_Active_Date_VacOnlys{$inNCPDP}<br>\n";
   print "Difference in days: $dd\n";
   print "<hr>\n";
}

if ( $Pharmacy_Types{$inNCPDP} =~ /VacOnly/i ) {
   use Date::Calc qw/Delta_Days/;
   my ($y1, $m1, $d1) = split("-", $Pharmacy_Active_Date_VacOnlys{$inNCPDP});
   my @first = ($y1, $m1, $d1);
   my @second = ($syear, $smonth, $sday);
   my $dd = Delta_Days( @first, @second );
   if ( $dd > 365 ) {
      $Header  = "Annual Vaccination Program Membership has Expired!";
      $H1      = "Your Annual Vaccination Program Membership has Expired!";
      @message = ("Your annual vaccination program membership has expired.",
                  "Please contact our office to re-enroll!",
                  "Your enrollment date was $m1/$d1/$y1.");
      &display_Nag_Page($Header, $H1, @message);
      print join("<br>", @message), "<br>\n";
      &MyPharmassessMembersTrailer;
      exit(0);
   }
}

#______________________________________________________________________________

print "SAVEVALID: $SAVEVALID, USER: $USER, OWNER: $OWNER<br>\n" if ($debug);
if ( $SAVEVALID =~ /^\s*$/ ) {
   print "USER: $USER, OWNER: $OWNER<br>\n" if ($debug);
   if ( $USER !~ m/[^0-9.]/ && $USER > 0 && $OWNER !~ /pharmassess/i) {
      $Pharmacy_Name = $Pharmacy_Names{$USER};
      &logActivity($Pharmacy_Name, "Logged in to RBS", $USER);
   } else {
      if ( $USER eq $OWNER ) {
         &logActivity($RUSER, "SuperUser Logged in to RBS", NULL);
      }
   }
}

#______________________________________________________________________________
$HEADPREFIX = "PH";

# print "SAVEUSER: $SAVEUSER, Login_Auth($USER): $Login_Auth{$USER}<br>\n";
# print "isMemberVac: $isMemberVac, VALIDVac: $VALIDVac<hr>\n";

print "In DEBUG   mode<br>\n" if ($debug);
print "In VERBOSE mode<br>\n" if ($verbose);
print "\nProg: $prog &nbsp; &nbsp;<br>Date: $tdate &nbsp; Time: $ttime<P>\n" if ($debug);

if ( $debug ) {
  print "RUSER: $RUSER, USER: $USER<hr>\n";
  print "dbin: $dbin, db: $db, DBNAME: $DBNAME, TABLE: $TABLE<br>\n";
  print "FIELDS : $FIELDS, FIELDS2: $FIELDS2, fieldcnt: $fieldcnt<br>\n";

  print "<hr size=4 noshade color=blue>\n";
  print "JJJ:<br>\n";
  my $key;
  foreach $key (sort keys %in) {
     next if ( $key =~ /^PASS\s*$/ );	# skip printing out the password...
     print "key: $key, val: $in{$key}<br>\n" if ($debug);
  }
  print "<hr size=4 noshade color=blue>\n";
}
# print "Login_Auth($USER): $Login_Auth{$USER}<hr>\n";
#______________________________________________________________________________

$dbin     = "WLDBNAME";	# WAS "PYDBNAME"
$DBNAME   = $DBNAMES{"$dbin"};
$TABLE    = $DBTABN{"$dbin"};
$FIELDS   = $DBFLDS{"$dbin"};
$FIELDS2  = $DBFLDS{"$dbin"} . "2";
$fieldcnt = $#${FIELDS2} + 2;

$dbx = DBI->connect("DBI:mysql:$DBNAME:$DBHOST",$dbuser,$dbpwd,
       { PrintError => 1, RaiseError => 1, InactiveDestroy => 0 } ) || die "$DBI::errstr";
DBI->trace(1) if ($dbitrace);

$Pharmacy_Name = $Pharmacy_Names{$USER};
$Pharmacy_Type = $Pharmacy_Types{$USER};

if ( !$USER && $RUSER ) {
   $USER = $RUSER;
   $PASS = $RPASS;
}
if ( !$RUSER && $USER ) {
   $RUSER = $USER;
   $RPASS = $PASS;
}

# print "RUSER: $RUSER, OLTYPE: $OLTYPE<hr>\n";

&read_this_Owners_Pharmacies($RUSER, $OLTYPE);

# print "VALID: $VALID<br>USER: $USER<BR>RUSER: $RUSER<BR>OLTYPE: $OLTYPE<br>\n" if ($debug);


if ( $VALID && $RUSER =~ /\@/ && $OLTYPE =~ /^SuperUser|^Owner$|^Admin$/i ) {

#  $URLH = "${prog}.cgi";

   print qq#<h2>Pharmacy Selection</h2>\n#;
   print qq#<p>Please select the pharmacy you wish to view from the list below:</p>\n#;
    
   print "2. USER: $USER<br>RUSER: $RUSER<br>OWNER: $OWNER<br>OLTYPE: $OLTYPE<br>\n" if ($debug);
   if ( $OWNER =~ /\@/ ) {
        # okay
   } elsif ( $RUSER =~ /\@/ ) {
        $OWNER     = $RUSER;
        $OWNERPASS = $RPASS;
   } elsif ( $USER =~ /\@/ ) {
        $OWNER     = $USER;
        $OWNERPASS = $PASS;
   }

   if ( $OLTYPE =~ /^Admin$|^SuperUser$/i ) {

      #NOW LOADED IN HEADER CANNED FILE 
      #print qq#<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>\n#;
      print qq#<link type="text/css" media="screen" rel="stylesheet" href="/includes/datatables/css/jquery.dataTables.css" /> \n#;
      print qq#<script type="text/javascript" charset="utf-8" src="/includes/datatables/js/jquery.dataTables.min.js"></script> \n#;
      print qq#<script type="text/javascript" charset="utf-8"> \n#;
      print qq#\$(document).ready(function() { \n#;
      print qq#                \$('\#tablef').dataTable( { \n#;
      print qq#                                "sScrollX": "100%", \n#;
      print qq#                                "bScrollCollapse": true,  \n#;
      print qq#                                "sScrollY": "350px", \n#;
      print qq#                                "bPaginate": false \n#;
      print qq#                } ); \n#;
      print qq#} ); \n#;
      print qq#</script> \n#;

      print qq#<table id="tablef">\n#;
      print "<thead>";
      print "<tr><th>$nbsp</th><th>Pharmacy Name</th><th>NCPDP</th><th>NPI</th><th>Phone</th><th>Address</th></tr>";
      print "</thead>";
      print "<tbody>";

      foreach $ONCPDP (sort { $OPharmacy_Names{$a} cmp $OPharmacy_Names{$b} } keys %ONCPDPs) {

         $OPharmacy_Name = $OPharmacy_Names{$ONCPDP};

         print "<tr>";
         print qq#<td>#;
         $URLH = "index.cgi";
         print qq#<FORM ACTION="$URLH" METHOD="POST">\n#;
         print qq#<INPUT TYPE="hidden" NAME="debug"   VALUE="$debug">\n#;
         print qq#<INPUT TYPE="hidden" NAME="verbose" VALUE="$verbose">\n#;
         print qq#<INPUT TYPE="hidden" NAME="isOWNER" VALUE="$isOWNER">\n#;
         print qq#<INPUT TYPE="hidden" NAME="OWNER"   VALUE="$OWNER">\n#;
         print qq#<INPUT TYPE="hidden" NAME="OWNERPASS" VALUE="$OWNERPASS">\n#;
         print qq#<INPUT TYPE="hidden" NAME="USER"    VALUE="$ONCPDP">\n#;
         print qq#<INPUT TYPE="hidden" NAME="PASS"    VALUE="$ONPIs{$ONCPDP}">\n#;
         print qq#<INPUT TYPE="hidden" NAME="RUSER"   VALUE="$ONCPDP">\n#;
         print qq#<INPUT TYPE="hidden" NAME="RPASS"   VALUE="$ONPIs{$ONCPDP}">\n#;

         print qq#<INPUT TYPE="Submit" NAME="Submit" VALUE="Select">\n#;
         print qq#</FORM>\n#;
         print qq#</td>#;
         print "<td>$OPharmacy_Name</td>\n";
         print "<td>$ONCPDP</td>\n";
         print "<td>$ONPIs{$ONCPDP}</td>\n";
         print "<td>$Pharmacy_Business_Phones{$ONCPDP}</td>\n";
         print "<td>$Pharmacy_Addresses{$ONCPDP}<br>$Pharmacy_Citys{$ONCPDP}, $Pharmacy_States{$ONCPDP} $Pharmacy_Zips{$ONCPDP}</td>\n";
         print "</tr>\n";
         print qq#<!--end pharmacy to select-->\n#;
      }
      print "</tbody>";
      print "</table>\n";

   }
} else {

   #print qq#<h1 class="acctprofile">$ntitle</h1>\n#;
   
   &displayNewLoginInfo;
   
   if ( $OLTYPE !~ /Admin/i ) {
       my ($lockoutCIPN, $lockoutRBS, $lockoutQCPN) = &MEV_Check($inNCPDP,"CRED");
   }
   &displayPharmacyRight($dispNCPDP, $dispNPI);

}

#______________________________________________________________________________

&MyPharmassessMembersTrailer;

$dbx->disconnect;


exit(0);

#______________________________________________________________________________

sub viewfield {
#
# if MODE = "View", just display field name and value
# if MODE = "Update", display field name and open up for edit

  my ($MODE, $screenval, $name, $color, @OPTS) = @_;
  my $NAME  = "UpDB_" . $name;
  my $value = $$name;

  $sizeopts = $#OPTS;

  if ( $MODE =~ /View/i ) {
     # View
     if ( $screenval =~ /website/i && $value !~ /^\s*NA\s*$/i ) {
        if ( $value =~ /^http/i ) {
           $URL = $value;
        } else {
           $URL = "http://" . $value;
        }
        # print "<tr><th>$value</th><td>$URL</td></tr>\n";
        print qq#<tr><th class="$color" align=left>${screenval}:</th><td><a href="$URL" target=new>$value</a></td></tr>\n#;
     } else {
         print qq#<tr><th class="$color" align=left>${screenval}:</th><td>$value</td></tr>\n#;
     }
  } else {
     # Update
     if ( $sizeopts <= 0 ) {
       if ( $NAME =~ /Comments/i ) {
          print qq#<tr><th class="$color" align=left>${screenval}:</th><td><TEXTAREA NAME="$NAME" COLS=30 ROWS=8 WRAP="soft">$value</TEXTAREA></td></tr>\n#;
       } else {
          print qq#<tr><th class="$color" align=left>${screenval}:</th><td><INPUT TYPE="text" SIZE=20 NAME="$NAME" VALUE="$value"</td></tr>\n#;
       }
     } else {
       &dropdown( "$name", "$screenval", @OPTS);
     }
  }
}

#______________________________________________________________________________

sub displayPharmacyRight {

   my ($jNCPDP, $jNPI) = @_;
   print qq#<!-- displayPharmacyRight -->\n#;
   print "sub displayPharmacyRight: Entry. jNCPDP: $jNCPDP, jNPI: $jNPI, LPERMISSIONLEVEL: $LPERMISSIONLEVEL<br>\n" if ($debug);


#	   my $dbin     = "PHDBNAME";
#	   my $db       = $dbin;
#	   my $DBNAME   = $DBNAMES{"$dbin"};
#	   my $TABLE    = $DBTABN{"$dbin"};
#	   my $FIELDS   = $DBFLDS{"$dbin"};
#	   my $FIELDS2  = $DBFLDS{"$dbin"} . "2";
#	   my $fieldcnt = $#${FIELDS2} + 2;
#	
#	#  connect to the pharmacy MySQL database
#	#  print "PHDBNAME: $PHDBNAME, dbuser: $dbuser\n" if ($debug);
#	
#	   $dbp = DBI->connect("DBI:mysql:$PHDBNAME:$DBHOST",$dbuser,$dbpwd,
#		        { RaiseError => 1, InactiveDestroy => 0 } ) || die "$DBI::errstr";
#	
#	   DBI->trace(1) if ($dbitrace);
#	
#	   my $sql = "SELECT $PHFIELDS FROM $PHTABLE WHERE NPI = $jNPI";
#	# print "sql:<br>$sql<hr>\n";
#	
#	   $sthp = $dbp->prepare($sql);
#	   $sthp->execute();
#	   my $numofrows = $sthp->rows;
#	   print "Number of rows found: " . $sthp->rows . "<br>\n" if ($debug);
#	
#	   @$FIELDS3 = @$FIELDS2;
#	   while (my @row = $sthp->fetchrow_array()) {
#	     (@$FIELDS3) =  @row;
#	     $ptr = -1;
#	     foreach $pc (@$FIELDS3) {
#	        $ptr++;
#		    my $name = @$FIELDS2[$ptr];
#	        ${$name} = $pc || $nbsp;
#	#       ${$name} = $pc || "Unknown";
#	#       print "name: $name, value: $$name<br>\n" ;# if ($verbose);
#	     }
#	   }
#	
#	   $sthp->finish();
#	
#	   # Close the Databases
#	   $dbp->disconnect;

#  print "inNCPDP: $inNCPDP<br>\n";
#  print "dispNCPDP: $dispNCPDP<br>\n";
#  print "dispNPI: $dispNPI<br>\n";
   if ( $dispNCPDP || $dispNPI ) {
      $HELPURL = "/members/LetUsKnow.cgi";
      if ($Login_Auth{$USER} =~ /COMPANY/i ) {
#        print "dispNCPDP: $dispNCPDP, dispNPI: $dispNPI, HELPURL: $HELPURL<br>\n";
         &displayProfileInfoCompany($dispNCPDP, $HELPURL);
      } else {
         &displayProfileInfo($dispNCPDP, $dispNPI, $HELPURL);
      }
   }

   print "sub displayPharmacyRight: Exit.<br>\n" if ($debug);
}

#______________________________________________________________________________


