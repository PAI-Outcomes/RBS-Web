require "D:/RedeemRx/MyData/RBSDesktop_routines.pl";
require "D:/RedeemRx/cgi-bin/cgi-lib.pl";

use File::Basename;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use Env qw(PATH REMOTE_ADDR PERL5LIB PERLLIB);

$| = 1;
my $start = time();
($prog, $dir, $ext) = fileparse($0, '\..*');
$nbsp = "&nbsp\;";

$title = "$prog";
$title = qq#${COMPANY} - $title# if ( $COMPANY );

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

($ENV) = &What_Env_am_I_in;

#______________________________________________________________________________

if ( $Pharmacy_Types{$PH_ID} =~ /VacOnly/i ) {
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

$VACPROGONLY = 0;
if ( $Pharmacy_Types{$PH_ID} =~ /VacOnly/i ) {
   $VACPROGONLY++;
}

$RBSCREDPLUS = 0;
if ( $Pharmacy_Types{$PH_ID} =~ /Cred/i && $Pharmacy_Types{$PH_ID} =~ /Default Cash/i ) {
   $RBSCREDPLUS++;
}

$SPECIALPROGS = 0;
if ( $Pharmacy_Types{$PH_ID} =~ /Special Programs/i ) {
   $SPECIALPROGS++;
}

$ntitle = "Special Programs";

print qq#<h1>$ntitle</h1>\n#;

#----------------------------------------------------------------#

print qq#<div>\n#;

if ( $VACPROGONLY ) {
  print qq#
  <div class="special_program">
  <img src="/images/icons/drug2.png" style="vertical-align: top;" />
  <span class="special_program_text">
  <a href="/members/vaccinations.cgi">Vaccination Program</a>
  </span>
  </div>
  #;
} elsif ( $RBSCREDPLUS || $SPECIALPROGS ) {
  print qq#
  <div class="special_program">
  <img src="/images/icons/pill.png" style="vertical-align: middle;" />
  <span class="special_program_text"><a href="/members/psp.cgi">Prescription Savings Program</a></span>
  </div>
  #;

  print qq#
  <div class="special_program">
  <img src="/images/icons/drug2.png" style="vertical-align: top;" />
  <span class="special_program_text">
  <a href="/members/vaccinations.cgi">Vaccination Program</a>
  </span>
  </div>
  #;
} else {
  print qq#
  <div class="special_program">
  <img src="/images/icons/pill.png" style="vertical-align: middle;" />
  <span class="special_program_text"><a href="/members/psp.cgi">Prescription Savings Program</a></span>
  </div>
  #;
  
  print qq#
  <!--
  <div class="special_program">
  <img width="32" height="32" src="/images/icons/syncfill.png" style="vertical-align: middle;" />
  <span class="special_program_text"><a href="/members/SynchronizedAssistance.cgi">Synchronization Assistance Program</a></span>
  </div>
  -->
  #;
  
  
  print qq#
  <div class="special_program">
  <img src="/images/icons/drug2.png" style="vertical-align: top;" />
  <span class="special_program_text">
  <a href="/members/vaccinations.cgi">Vaccination Program</a>
  </span>
  </div>
  #;
  
}

print qq#</div>\n#;

#______________________________________________________________________________

&MyPharmassessMembersTrailer;

exit(0);
