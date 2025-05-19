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

#&readPharmacies;
&readLogins;

$FirstName = $LFirstNames{$USER};
$LastName  = $LLastNames{$USER};

#$Pharmacy_Name = $Pharmacy_Names{$inNCPDP};
$ntitle = "Vaccinations";

print qq#<h1>Vaccination Program</h1>\n#;

#&vaccinations;

&vaccinationProgram();

#______________________________________________________________________________

&MyPharmassessMembersTrailer;

exit(0);

#______________________________________________________________________________

sub vaccinationProgram {

  print qq#<!-- vaccination program -->\n#;
  print "sub vaccinationProgram: Entry.<br>\n" if ($debug);
  
  my $vax_program_intro_canned_file = 'D:\\RedeemRx\\CannedFiles\\vaccination_program_intro.html';
  if (open(my $fh, '<', $vax_program_intro_canned_file)) {
    while (my $row = <$fh>) {
      chomp $row;
      print "$row\n";
    }
  } else {
    warn "Could not open file '$filename' $!";
  }
  
  my $vax_program_canned_file = 'D:\\RedeemRx\\CannedFiles\\vaccination_program.html';
  if (open(my $fh, '<', $vax_program_canned_file)) {
    while (my $row = <$fh>) {
      chomp $row;
      print "$row\n";
    }
  } else {
    warn "Could not open file '$filename' $!";
  }
  
  print "sub vaccinationProgram: Exit.<br>\n" if ($debug);

}

#______________________________________________________________________________

sub vaccinations {

  print qq#<!-- vaccinations -->\n#;
  print "sub vaccinations: Entry.<br>\n" if ($debug);
  
  print qq#<img src="/images/packet_web.jpg" style="width: 250px; float: right;" />\n#;

  print qq#<p>Pharm AssessRBS is here to help you with providing flu vaccinations! Below, you will find our <strong>Vaccinations Materials Packet</strong> documents. Download the sample packet, or download individual documents from the list below!</p>\n#;
  
  print qq#<p><a href="/downloads/vax/vaccinations_sample_packet.pdf" target="_blank" style="margin: 4px 0px 0px 10px;">Download Sample Packet (pdf)</a></p>\n#;
  
  print qq#<hr /><br /><h1>Individual Forms</h1>\n#;
  
  print qq#<p>Employer Group Notification Letter (<i>Customizable</i>)
  <br /><a href="/downloads/vax/notification_letter_custom.pdf" target="_blank" style="margin: 4px 0px 0px 10px;">Download (pdf)</a></p>\n#;
  
  print qq#<p>Patient Demographic Form
  <br /><a href="/downloads/vax/patient_demographic_form.pdf" target="_blank" style="margin: 4px 0px 0px 10px;">Download (pdf)</a></p>\n#;
  
  print qq#<p>Employer Group Flu Vaccine Administration Cards
  <br /><a href="/downloads/vax/flu_vaccination_cards.pdf" target="_blank" style="margin: 4px 0px 0px 10px;">Download (pdf)</a></p>\n#;
  
  print qq#<p>Employer Group Flu Vaccine Summary Log
  <br /><a href="/downloads/vax/summary_log.pdf" target="_blank" style="margin: 4px 0px 0px 10px;">Download (pdf)</a></p>\n#;
  
  print qq#<p>Newspaper Ad Samples
  <br /><a href="/downloads/vax/newspaper_sample_ads.pdf" target="_blank" style="margin: 4px 0px 0px 10px;">Download (pdf)</a></p>\n#;
  
  print qq#<p>In Store Display Material (<i>Customizable</i>)
  <br /><a href="/downloads/vax/display_instore.docx" target="_blank" style="margin: 4px 0px 0px 10px;">Download (docx)</a></p>\n#;
  
  print qq#<hr /><br /><h1>Vaccine Networks</h1>\n#;
  
  print qq#<p>For vaccine network information, login to your CIPN Member's section and select "Special Network Rates" from the sidebar. Then choose "Vaccine Networks" to view the CIPN contracted vaccine networks information.</p>\n#;

# print qq#</div>\n#;
# print qq#<!-- end  textarea2 --> \n#;

  print "sub vaccinations: Exit.<br>\n" if ($debug);

}

#______________________________________________________________________________
