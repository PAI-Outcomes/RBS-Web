require "D:/RedeemRx/MyData/RBSDesktop_routines.pl";
require "D:/RedeemRx/cgi-bin/cgi-lib.pl";

use File::Basename;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use Env qw(PATH REMOTE_ADDR PERL5LIB PERLLIB);
use DateTime;

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

$ntitle = "Synchronization Assistance Program";
print qq#<h1>$ntitle</h1>\n\n#;

&printMenu;

print qq#\n#;

#______________________________________________________________________________

&MyPharmassessMembersTrailer;

exit(0);

#______________________________________________________________________________


#_______________________________________________________________________________

sub printMenu {

  my ($NCPDP, $PROGRAM) = @_;

  #Master source for document links ($dochost)
  #The master will be on pharmassess.com
  $HTTP_HOST = $ENV{'HTTP_HOST'};
  if ($HTTP_HOST =~ /^dev/i) {
    $dochost = "http://dev.pharmassess.com";
  } else {
    $dochost = "http://members.pharmassess.com";
  }
  #------------------------------------------#

  print qq#
  <script>
  \$(function() {
    \$( ".expander" ).click(function() {
    
  	var wasOpen = 0;
  	
  	if ( \$(this).next('.content').is(":visible") ) {
        wasOpen = 1;
  	}
  	
  	\$('.content').slideUp();
  	\$('.sign').html('+');
  	
  	if ( wasOpen > 0 ) {
  	  //Do Nothing
  	} else { 
  	  \$(this).next('.content').slideDown();
  	  \$(this).find('.sign').html('>');
  	}
  	
    });
  });
  </script>
  #;

  print qq#<div id="expander_area">\n\n#;
  print qq#<p>Expand categories below for more information.</p>\n#;
  print qq#<hr />\n#;
  
  #----------------------------------------------------------------------------------------------------#
  print qq#<h2 id="expanderHead3" class="expander" style="cursor:pointer;"><span id="expanderSign3" class="sign">></span>Introduction</h2>\n#;
  print qq#<div class="content credentialing_category" >\n#;

  print qq#<UL>\n#;
  print qq#<LI>Medication Synchronization is an adaptable service that allows patients to pick up all chronic medications on the same day each month</LI>\n#;
  print qq#<LI>Benefits</LI>\n#;
     print qq#<UL>\n#;
     print qq#<LI>Average of \$230 Gross Margin Per Patient, Per Year</LI>\n#;
     print qq#<LI>Increase Productivity Through Even Workflow</LI>\n#;
     print qq#<LI>Better Inventory Control</LI>\n#;
     print qq#<LI>Increase Medication Adherance</LI>\n#;
     print qq#</UL>\n#;
  print qq#<LI>Click on Links Below for Complete Program Details!</LI>\n#;
  print qq#</UL>\n#;
  
  print qq#<hr />#;
  print qq#</div>\n#;
  #----------------------------------------------------------------------------------------------------#
  
  #----------------------------------------------------------------------------------------------------#
  print qq#<h2 class="expander" style="cursor:pointer;"><span id="expanderSign4" class="sign">+</span> Synchronization Assistance Program</h2>\n#;
  print qq#<div class="content credentialing_category" style="display:none">\n#;

  print qq#\n#;
  print qq#<UL>\n#;
  print qq#<LI><a href="https://www.youtube.com/watch?v=ty1EjcXVqcA" target="_blank">Webinar</a></LI>\n#;
  print qq#<LI><a href="${dochost}/members/WebShare/Synchronization_Assistance_Program/SynchronizationAssistanceProgramPresentation.pdf" target="_blank">Presentation</a></LI>\n#;
  print qq#<LI><a href="${dochost}/members/WebShare/Synchronization_Assistance_Program/SynchronizationAssistanceProgramManual.pdf" target="_blank">Synchronization Assistance Program Manual</a></LI>\n#;
  print qq#</UL>\n#;

  print qq#<hr />#;
  print qq#</div>\n#;
  #----------------------------------------------------------------------------------------------------#
  
  #----------------------------------------------------------------------------------------------------#
  print qq#<h2 class="expander" style="cursor:pointer;"><span id="expanderSign1" class="sign">+</span> NCPA Simplify My Meds</h2>\n#;
  print qq#<div class="content credentialing_category" style="display:none">\n#;
  
  print qq#<UL>\n#;
  print qq#<LI><a href="http://www.ncpanet.org/solutions/adherence-simplify-my-meds" target="SMM">Main Page</a></LI>\n#;
  print qq#<LI><a href="http://www.ncpanet.org/solutions/adherence-simplify-my-meds/simplify-my-meds/simplify-my-meds-participation-agreement" target="SMM">Enrollment</a></LI>\n#;
  print qq#<LI><a href="http://www.ncpafulfillment.com/" target="SMM">Free Marketing Materials</a></LI>\n#;
  print qq#</UL>\n#;

  print qq#<hr />#;
  print qq#</div>\n#;
  #----------------------------------------------------------------------------------------------------#
  
  #----------------------------------------------------------------------------------------------------#
  print qq#<h2 class="expander" style="cursor:pointer;"><span id="expanderSign2" class="sign">+</span> Program Manager Daily Task Sheet </h2>\n#;
  print qq#<div class="content credentialing_category" style="display:none">\n#;
  
  print qq#<UL>\n#;
  print qq#<LI><a href="${dochost}/members/WebShare/Synchronization_Assistance_Program/ProgramManagerDailyTaskSheet.pdf" target="_new">Program Manager Daily Task Sheet</a></LI>\n#;


  print qq#</UL>\n#;
  
  print qq#<hr />#;
  print qq#</div>\n#;
  #----------------------------------------------------------------------------------------------------#
 
  #----------------------------------------------------------------------------------------------------#
  
  print qq#</div>\n#;
  
}

#_______________________________________________________________________________
