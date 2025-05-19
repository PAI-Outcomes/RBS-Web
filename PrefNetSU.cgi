require "D:/RedeemRx/MyData/RBSDesktop_routines.pl";
require "D:/RedeemRx/cgi-bin/cgi-lib.pl";

use File::Basename;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use Env qw(PATH REMOTE_ADDR PERL5LIB PERLLIB);

$| = 1;
my $start = time();
my ($prog, $dir, $ext) = fileparse($0, '\..*');
my $members = 'members';
$nbsp = "&nbsp\;";

$ret = &ReadParse(*in);
&CgiDie("Error in reading and parsing of CGI input") if !defined $ret;

$PrefPayer  = $in{'PrefPayer'};
$UserNotes  = $in{'UserNotes'};
$Payer      = $in{'Payer'};
$buildLetter= $in{'buildLetter'};

($PrefPayer)  = &StripJunk($PrefPayer);
#($UserNotes) = &StripJunk($UserNotes);
($Payer)      = &StripJunk($Payer);
($buildLetter)= &StripJunk($buildLetter);

$dbin     = "PHDBNAME";
$db       = $dbin;
$DBNAME   = $DBNAMES{"$dbin"};
$TABLE    = $DBTABN{"$dbin"};
$FIELDS   = $DBFLDS{"$dbin"};
$FIELDS2  = $DBFLDS{"$dbin"} . "2";
$fieldcnt = $#${FIELDS2} + 2;

#______________________________________________________________________________

&readsetCookies;

&read_canned_header($RBSHeader);
$members = 'www' if ($ENV{'SERVER_NAME'} =~ /^dev./);


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

# Create the inputfile format name
my ($min, $hour, $day, $month, $year) = (localtime)[1,2,3,4,5];
$year  += 1900;	# reported as "years since 1900".
$month += 1;	# reported ast 0-11, 0==January
$syear  = sprintf("%4d", $year);
$smonth = sprintf("%02d", $month);
$sday   = sprintf("%02d", $day);
$tdate  = sprintf("%04d/%02d/%02d", $year, $month, $day);
$ttime  = sprintf("%02d:%02d", $hour, $min);
$CURYEAR  = sprintf("%4d", $year);
$NEXTYEAR = $CURYEAR + 1;

$mdatetime = sprintf("%02d/%02d/%04d", $month, $day, $year);

#______________________________________________________________________________

$dbx = DBI->connect("DBI:mysql:$DBNAME:$DBHOST",$dbuser,$dbpwd,
       { PrintError => 1, RaiseError => 1, InactiveDestroy => 0 } ) || die "$DBI::errstr";
   
DBI->trace(1) if ($dbitrace);
 
#______________________________________________________________________________

&readThirdPartyPayers;

my $whocalledme = $ENV{'SERVER_NAME'};

my $URL = "${prog}${ext}";

$PrefPayers{"700002"}++;	# Caremark
$PrefPayers{"700336"}++;	# Catamaran
#	$PrefPayers{"700004"}++;	# CIGNA
$PrefPayers{"700006"}++;	# Express Script, Inc
$PrefPayers{"700003"}++;	# Humana
$PrefPayers{"700150"}++;	# OptumRx
$PrefPayers{"700009"}++;	# Prime Therapeutics
if ( $whocalledme =~ /dev\./ ) {
   $PrefPayers{"700407"}++;	# TESTING
}

# Display Pharmacy demographics
$Pharmacy_Name           = $Pharmacy_Names{$PH_ID};
$Pharmacy_Address        = $Pharmacy_Addresses{$PH_ID};
$Pharmacy_City           = $Pharmacy_Citys{$PH_ID};
$Pharmacy_State          = $Pharmacy_States{$PH_ID};
$Pharmacy_Zip            = $Pharmacy_Zips{$PH_ID};
$Pharmacy_Business_Phone = $Pharmacy_Business_Phones{$PH_ID};
#
#$Pharmacy_Contact        = $Pharmacy_Primary_Contact_Name{$PH_ID};
$Pharmacy_Contact        = $Pharmacy_Owner_Contact_Names{$PH_ID};

$Pharmacy_NCPDP          = $Pharmacy_NCPDPs{$PH_ID};
$Pharmacy_NPI            = $Pharmacy_NPIs{$PH_ID};

$Pharmacy_Owner_Name     = $Pharmacy_Owner_Contact_Names{$PH_ID};
$Pharmacy_Owner_Phone    = $Pharmacy_Owner_Contact_Phones{$PH_ID};
$Pharmacy_Owner_Email    = $Pharmacy_Owner_Contact_Emails{$PH_ID};
$Pharmacy_Owner_Fax      = $Pharmacy_Owner_Contact_Faxes{$PH_ID};

$ntitle = "Medicare - Preferred Network Letter";
print qq#<h2>$ntitle</h2>\n#;

$Payer_Name              = $TPP_Names{$PrefPayer};
$Payer_Contact_Name      = $TPP_PreferredNetwork_Contact_Names{$PrefPayer};
$Payer_Address           = $TPP_PreferredNetwork_Contact_Addresses{$PrefPayer};
$Payer_City              = $TPP_PreferredNetwork_Contact_Citys{$PrefPayer};
$Payer_State             = $TPP_PreferredNetwork_Contact_States{$PrefPayer};
$Payer_Zip               = $TPP_PreferredNetwork_Contact_Zips{$PrefPayer};
$Payer_Business_Phone    = $TPP_Business_Phones{$PrefPayer};
$Payer_Contact           = $TPP_PreferredNetwork_Contact_Names{$PrefPayer};
$Payer_Email             = $TPP_PreferredNetwork_Contact_Emails{$PrefPayer};

if ( $PrefPayer && ($PrefPayer !~ /700006|700150/) ) {

   if ( $Payer_Email ) {
      $Payer_Info = qq#<strong>$Payer_Name</strong><br>$Payer_Contact_Name<br>$Payer_Email<br><br>#;
   } else {
      $Payer_Info = qq#<strong>$Payer_Name</strong><br>$Payer_Contact_Name<br>$Payer_Address<br>$Payer_City, $Payer_State $Payer_Zip<br><br>#;
   }
   #print "Payer_Info: $Payer_Info<br>\n";

} else {
  $Payer_Name= $TPP_Names{$PrefPayer};
  $Payer_Info = qq#<strong>$Payer_Name</strong><br>$Payer_Contact<br><br>#;
}

if ( !$PrefPayer ) {
   &askForPayer;

} elsif ( $UserNotes || ($buildLetter =~ /Build Letter/i && $UserNotes =~ /^\s*$/) ) {
   &createLetter;

} else {
   &buildLetter;
}

#______________________________________________________________________________

# Close the Database
$dbx->disconnect;

&MyPharmassessMembersTrailer;

exit(0);

#______________________________________________________________________________

sub askForPayer {
  print qq#<FORM ACTION=$URL METHOD="POST">\n#;

  print "Select a Preferred Payer:<br><br>\n";
  print qq#<SELECT NAME="PrefPayer">\n#;

  foreach $key (sort {$TPP_Names{$a} cmp $TPP_Names{$b} } keys %PrefPayers) {
     print qq#<OPTION VALUE="$key">$TPP_Names{$key}</OPTION>\n#;
  }
  print qq#</SELECT>\n#;
  print qq#<INPUT TYPE="Submit" NAME="askForPayer" VALUE="Select">\n#;
  print qq#</FORM>\n#;

}
#______________________________________________________________________________

sub buildLetter {
  print qq#<!-- buildLetter -->\n#;
# Read in canned file, use variables to fill in "<%var%>" values

  print qq#<FORM ACTION=$URL METHOD="POST">\n#;
  print qq#<INPUT TYPE="hidden" NAME="PrefPayer"  VALUE="$PrefPayer">\n#;
  print qq#<INPUT TYPE="hidden" NAME="Payer"      VALUE="$Payer">\n#;

  my $FILE = "CIPN_Medicare-Pref_Net_SU";
  my ($message, @array) = &read_canned_file($FILE);
  foreach $line (@array) {
     print "$line\n";
  }

  print qq#<INPUT TYPE="Submit" NAME="buildLetter" VALUE="Build Letter">\n#;
  print qq#</FORM>\n#;
}

#______________________________________________________________________________

sub createLetter {
  $folder = "D:/WWW/www.CIPNetwork.com/WebShare/PrefNetworksLetters";
  $name   = "${inNCPDP}_CIPN_CIPN Assists with Letters Requesting Participation into $NEXTYEAR Medicare Part D Preferred Networks_${Payer_Name}.doc";
  $LETTER = "$folder/$name";
  $WEBLET = "/WebShare/PrefNetworksLetters/$name";

#	  my $PHPCreateWord = qq#D:\\WWW\\www.CIPNetwork.com\\includes\\CreateWord.php#;
#	  $UserNotes =~ s/\n/<w:br\/>/g;
#	
#	  $cmd = qq#php "$PHPCreateWord" "$inNCPDP" "$PrefPayer" "$Payer" "$Pharmacy_Name" "$Pharmacy_Address" "$Pharmacy_City" "$Pharmacy_State" "$Pharmacy_Zip" "$Pharmacy_Business_Phone" "$Pharmacy_Contact" "$UserNotes" #;

  open(OFILE, "> $LETTER") || die "Couldn't open output file '$LETTER'\n$!\n\n";
  print OFILE "<html>\n";
  print OFILE "<body>\n";
  my $FILE = "CIPN_Medicare-Pref_Net_SU";
  my ($message, @array) = &read_canned_file($FILE);
  foreach $line (@array) {
     if ( $line =~ /Enter text to be|Examples of what you may state/i ) {
        # don't include this line
     } elsif ( $line =~ /TEXTAREA/i ) {
        if ( $UserNotes !~ /^\s*$/ ) {
           $UserNotes =~ s/\n/<br>/g;
           print OFILE "$UserNotes<br><br>\n";
        }
     } else {
        print OFILE "$line\n";
     }
  }
  print OFILE "</body>\n";
  print OFILE "</html>\n";
  close(OFILE);

  print qq#<h1>Download your generated CIPN Medicare - Preferred Network Letter</h1>\n#;

  print qq#<p>Your CIPN Document has been created. Please download it by clicking on the link below.</p>\n#;

  if ( -e "$LETTER" ) {
	print qq#<p class="download"><a href="$WEBLET"><img src="/images/clip.png">Click Here to Download letter</a>\n#;
  } else {
	print qq#<p style="color: \#F00;"><strong>There was a problem generating your letter, please call or email CIPN for assistance.</strong></p>#;
  }
}

#______________________________________________________________________________

sub Error {
  print "Content-type: text/html\n\n";
  print "The server can't $_[0] the $_[1]: $! \n";
  exit;
}  

#______________________________________________________________________________

sub docmd_local {
  ($cmd) = @_;
  my $out = "";

  chomp($out = `$cmd`);
  $cmd = "";
  $out =~ s///g;
  $out =~ s/\n/<br>\n/g;

  return($cmd, $out);
}

#______________________________________________________________________________
