require "D:/RedeemRx/MyData/RBSDesktop_routines.pl";
require "D:/RedeemRx/cgi-bin/cgi-lib.pl";

use File::Basename;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use Env qw(PATH REMOTE_ADDR PERL5LIB PERLLIB);

$| = 1; 

my $start = time();
my ($prog, $dir, $ext) = fileparse($0, '\..*');

$title = "$prog";
$title = qq#${COMPANY} - $title# if ( $COMPANY );

$ret = &ReadParse(*in);
&CgiDie("Error in reading and parsing of CGI input") if !defined $ret;

$PH_ID = $in{'PH_ID'};
&readsetCookies;

if ($RBSHeader !~ /html$/) {
  &readPharmacies;
  if(($Pharmacy_Types{$PH_ID} =~ /RBS Direct/) && ($Pharmacy_Types{$PH_ID} !~ /RBS$/ && $Pharmacy_Types{$PH_ID} !~ /RBS:/)) {
    $RBSHeader = 'RBSDirectHeader.html';
  }
  else {
    $RBSHeader = 'PharmassessMembersHeader.html';
  }
   print "Set-Cookie:RBSHeader=$RBSHeader; path=/; domain=$cookie_server;\n" ;
}

&read_canned_header($RBSHeader);

#______________________________________________________________________________


if ( $USER ) {
   &MembersHeaderBlock;

   my $Licenses_Okay   = 0;
   my $Licenses_Broken = "";
   ($Licenses_Okay, $Licenses_Broken) = &Validate_No_Expired_Licenses($PH_ID);

   if ( !$Licenses_Okay ) {
      &display_Expired_Page($Licenses_Broken);
   }
} else {
   &MembersLogin;
   &MyPharmassessMembersTrailer;

   print qq#</BODY>\n#;
   print qq#</HTML>\n#;
   exit(0);
}

#______________________________________________________________________________

$dbin     = "WLDBNAME";
$DBNAME   = $DBNAMES{"$dbin"};
$TABLE    = $DBTABN{"$dbin"};
$FIELDS   = $DBFLDS{"$dbin"};
$FIELDS2  = $DBFLDS{"$dbin"} . "2";
$fieldcnt = $#${FIELDS2} + 2;

$dbx = DBI->connect("DBI:mysql:$DBNAME:$DBHOST",$dbuser,$dbpwd,
       { PrintError => 1, RaiseError => 1, InactiveDestroy => 0 } ) || die "$DBI::errstr";
DBI->trace(1) if ($dbitrace);

$inNCPDP = $Pharmacy_NCPDPs{$PH_ID};

if ( $TYPE !~ /Admin/i ) {
   my ($lockoutCIPN, $lockoutRBS, $lockoutQCPN) = &MEV_Check($inNCPDP,"CRED");
}

&displayPharmacyRight($PH_ID);

&MyPharmassessMembersTrailer;

$dbx->disconnect;

exit(0);

sub displayPharmacyRight {
   my ($Pharmacy_ID) = @_;
   print qq#<!-- displayPharmacyRight -->\n#;

   if ( $Pharmacy_ID ) {
      $HELPURL = "/members/LetUsKnow.cgi";
      if ($Login_Auth{$USER} =~ /COMPANY/i ) {
         &displayProfileInfoCompany($Pharmacy_ID, $HELPURL);
      } else {
         &displayProfileInfo($Pharmacy_ID, $HELPURL);
      }
      if(($Pharmacy_Types{$PH_ID} =~ /RBS Direct/) && ($Pharmacy_Types{$PH_ID} !~ /RBS$/ && $Pharmacy_Types{$PH_ID} !~ /RBS:/)) {
         print "<br><div>It is important to note that we are not providing legal services with the RBS Direct service. Any advice or guidance provided <br> is based solely on our experience as consultants in this industry. Any documentation populated on behalf of the pharmacy must<br> be reviewed/ verified by the pharmacy prior to submission to an outside party. The pharmacy is solely responsible for the<br> accuracy of this documentation.
                  </div>";
      }
      
   }
}

