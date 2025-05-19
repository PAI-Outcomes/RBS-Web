require "D:/RedeemRx/MyData/RBSDesktop_routines.pl";
require "D:/RedeemRx/cgi-bin/cgi-lib.pl";

use File::Basename;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use Env qw(PATH REMOTE_ADDR PERL5LIB PERLLIB);
use DateTime;

$| = 1;

my $start = time();
($prog, $dir, $ext) = fileparse($0, '\..*');
$PROG = "$prog" . "$ext";
$nbsp = "&nbsp;";
$blank = "&lt; blank &gt;";

$ret = &ReadParse(*in);
&CgiDie("Error in reading and parsing of CGI input") if !defined $ret;

&readsetCookies;
&MyPharmassessMembersHeader;

$status = $in{'status'};

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

$dbin     = "R8DBNAME";
$DBNAME   = $DBNAMES{"$dbin"};
$TABLE    = $DBTABN{"$dbin"};
$FIELDS   = $DBFLDS{"$dbin"};
$FIELDS2  = $DBFLDS{"$dbin"} . "2";
$fieldcnt = $#${FIELDS2} + 2;

$dbx = DBI->connect("DBI:mysql:$DBNAME:$DBHOST",$dbuser,$dbpwd,
       { PrintError => 1, RaiseError => 1, InactiveDestroy => 0 } ) || die "$DBI::errstr";
DBI->trace(1) if ($dbitrace);

&displayWebPage;

$dbx->disconnect;

#______________________________________________________________________________

&MyReconRxTrailer;

exit(0);

#______________________________________________________________________________

sub displayWebPage {
   my $complete_checked = '';
   my $pending_checked = '';

   print qq#<script>
              \$(document).ready(function() {
                 \$('input[name=status]').change(function(){
                    \$('form[name=radio_form]').submit();
                 });
              });
            </script>#;

   print qq#<!-- displayWebPage -->\n#;
 
   my @abbr = qw( Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec );
   my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($TS);
   $year += 1900;
   $date = qq#$abbr[$mon] $mday, $year#; 
   $DATE    = sprintf("%02d/%02d/%04d", $mon+1, $mday, $year);
   $SFDATE  = sprintf("%04d-%02d-%02d", $year, $mon+1, $mday);
   $SFDATE2 = sprintf("%04d%02d%02d",   $year, $mon+1, $mday);
 
   ($PROG = $prog) =~ s/_/ /g;

   if ($status =~ /complete/i) {
     $complete_checked = 'checked';
   } elsif ($status =~ /archived/i) {
     $archived_checked = 'checked';
   } else {
     $pending_checked = 'checked';
   }

   print qq#<h2>Completed Enrollments</h2>\n#;
   print qq#<p>All completed enrollments in the system, waiting to be put into PAI Desktop.</p>\n#;
   print qq#<form name="radio_form" action="Enrollments.cgi" method="post">
               <INPUT TYPE="radio" NAME="status" VALUE="pending" $pending_checked> Pending
               <INPUT TYPE="radio" NAME="status" VALUE="complete" $complete_checked> Completed
               <INPUT TYPE="radio" NAME="status" VALUE="archived" $archived_checked> Archived
             </form><br>#;
   
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
   print "<tr><th>Completed</th><th>Status</th><th>Pharmacy</th><th>NCPDP</th><th>Details</th></tr>\n";
   print "</thead>\n";
   print "<tbody>\n";

   if ($status =~ /complete/i) {
     $status = "'complete','pending_coo'";
   }
   elsif ($status =~ /archive/i) {
     $status = "'archive'";
   }
   elsif ($status =~ /pending/i) {
     $status = "'pending'";
   }
   else {
     $status = "'none'";
   }

   my $numrowsc = 0;
   my $sql = "";

   $sql = "SELECT rbs_status, rbs_enrollment_start, rbs_enrollment_complete, rbs_pharmname, rbs_ncpdp, rbs_npi, coo, id
             FROM pharmassess.enrollment 
            WHERE (rbs_status IN ($status)) 
         ORDER BY rbs_enrollment_start DESC";

   ($sqlout = $sql) =~ s/\n/<br>\n/g;

   $sthrp = $dbx->prepare($sql);
   $sthrp->execute();
   my $numofrows = $sthrp->rows;

   while ( my ( $status, $enrollment_start, $enrollment_complete, $Pharmacy_Name, $NCPDP, $NPI, $coo, $ID ) = $sthrp->fetchrow_array()) {
     my $coo_ext = '';
     $coo_ext = ' (COO)' if ($coo > 0); 
     print "<tr>";
     print qq#<td>$enrollment_start</td>#;
     print qq#<td>$status</td>#;
     print qq#<td>${Pharmacy_Name}$coo_ext</td>#;
     print qq#<td>$NCPDP</td>#;
     print qq#<td><form action="../rbs_enroll_review.php" method="post">
                    <INPUT class="button-form-xsmall" TYPE="submit" VALUE="View Details">
                    <input type="hidden" name="admin_ncpdp" value="$NCPDP">
                    <input type="hidden" name="admin_npi" value="$NPI">
                    <input type="hidden" name="admin_id" value="$ID">
                  </form>
		</td>#;
     print qq#</tr>\n#;
   }

   $sthrp->finish;
 
   print qq#</tbody>\n#;
   print qq#<tr>#;
   print qq#</table>\n#;

   print qq#<div style="clear: both;"></div>#;
   print qq#<br>\n#;
}

#______________________________________________________________________________

