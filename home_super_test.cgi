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
$nbsp = "&nbsp\;";

$title = "$prog";
$title = qq#${COMPANY} - $title# if ( $COMPANY );

$ret = &ReadParse(*in);

&CgiDie("Error in reading and parsing of CGI input") if !defined $ret;

$WHICHDB    = $in{'WHICHDB'};

#______________________________________________________________________________

&readPharmacies;
 
&readsetCookies;
  
if ( $PH_ID ) {
  $PH_ID = 0;
  print "Set-Cookie: PH_ID=$PH_ID;             path=/; domain=$cookie_server;\n";
}
  print "Set-Cookie:RBSHeader= ;             path=/; domain=$cookie_server;\n";

&MyPharmassessMembersHeader;

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

$dbin     = "WLDBNAME";	# WAS "PYDBNAME"
$DBNAME   = $DBNAMES{"$dbin"};
$TABLE    = $DBTABN{"$dbin"};
$FIELDS   = $DBFLDS{"$dbin"};
$FIELDS2  = $DBFLDS{"$dbin"} . "2";
$fieldcnt = $#${FIELDS2} + 2;

$dbx = DBI->connect("DBI:mysql:$DBNAME:$DBHOST",$dbuser,$dbpwd,
       { PrintError => 1, RaiseError => 1, InactiveDestroy => 0 } ) || die "$DBI::errstr";
DBI->trace(1) if ($dbitrace);

&read_this_Owners_Pharmacies($USER, $TYPE);

&displayWebPage;

$dbx->disconnect;

#______________________________________________________________________________

&MyPharmassessMembersTrailer;

exit(0);

#______________________________________________________________________________

sub displayWebPage {
   print qq#<!-- displayWebPage -->\n#;
 
   my @abbr = qw( Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec );
   my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($TS);
   $year += 1900;
   $date = qq#$abbr[$mon] $mday, $year#; 
   $DATE    = sprintf("%02d/%02d/%04d", $mon+1, $mday, $year);
   $SFDATE  = sprintf("%04d-%02d-%02d", $year, $mon+1, $mday);
   $SFDATE2 = sprintf("%04d%02d%02d",   $year, $mon+1, $mday);
 
   ($PROG = $prog) =~ s/_/ /g;

   print qq#<h2>Pharmacy Selection</h2>\n#;
   print qq#<p>Please select the pharmacy you wish to view from the list below:</p>\n#;
    
   #jQuery now loaded on all pages via header include.
   print qq#<link type="text/css" media="screen" rel="stylesheet" href="/includes/datatables/css/jquery.dataTables.css" /> \n#;
   print qq#<script type="text/javascript" charset="utf-8" src="/includes/datatables/js/jquery.dataTables.min.js"></script> \n#;
   print qq#<script type="text/javascript" charset="utf-8"> \n#;
   print qq#\$(document).ready(function() { \n#;
   print qq#                \$('\#tablef').dataTable( { \n#;
   print qq#                                "sScrollX": "100%", \n#;
   print qq#                                "bScrollCollapse": true,  \n#;
   print qq#                                "sScrollY": "370px", \n#;
   print qq#                                "bPaginate": false \n#;
   print qq#                } ); \n#;
   print qq#} ); \n#;
   print qq#</script> \n#;

   print qq#<table id="tablef">\n#;
   print "<thead>\n";
   print "<tr><th>$nbsp</th><th>Pharmacy Name</th><th>NCPDP</th><th>NPI</th><th>Phone</th><th>Address</th></tr>\n";
   print "</thead>\n";
   print "<tbody>\n";

   foreach $Pharmacy_ID (sort { $Pharmacy_Names{$a} cmp $Pharmacy_Names{$b} } keys %Pharmacies) {
    
      $Pharmacy_Names{146} = 'RBS' if($Pharmacy_ID == 146 && $LOGIN eq 'rbsdirectdemo');
      next if($TYPE eq 'Admin' && $Pharmacy_RBSReporting{$Pharmacy_ID} ne 'Yes');
      print "<tr>";
      print qq#<td>#;
      $URLH = "home.cgi";
      print qq#<FORM ACTION="$URLH" METHOD="POST">\n#;
      print qq#<INPUT TYPE="hidden" NAME="PH_ID" VALUE="$Pharmacy_ID">\n#;
      print qq#<INPUT TYPE="Submit" NAME="Submit" VALUE="Select ">\n#;
      print qq#</FORM>\n#;
      print qq#</td>#;
      print "<td width=150>$Pharmacy_Names{$Pharmacy_ID}</td>\n";
      print "<td>$Pharmacy_NCPDPs{$Pharmacy_ID}</td>\n";
      print "<td>$Pharmacy_NPIs{$Pharmacy_ID}</td>\n";
      print "<td>$Pharmacy_Business_Phones{$Pharmacy_ID}</td>\n";
      print "<td>$Pharmacy_Addresses{$Pharmacy_ID}<br>$Pharmacy_Citys{$Pharmacy_ID}, $Pharmacy_States{$Pharmacy_ID} $Pharmacy_Zips{$Pharmacy_ID}</td>\n";
      print "</tr>\n";
      print qq#<!--end pharmacy to select-->\n#;
   }

   print "</tbody>";
   print "</table>\n";
}

#______________________________________________________________________________

