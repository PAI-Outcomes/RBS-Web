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

($ENV) = &What_Env_am_I_in;

#______________________________________________________________________________

$ntitle = "Controlled Substance Patient Monitoring Program";

print qq#<h1>$ntitle</h1>\n#;

#----------------------------------------------------------------#

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


  print qq#



<h2 id="expanderHead3" class="expander" style="cursor:pointer;"><span id="expanderSign3" class="sign">></span>Controlled Substance Patient Monitoring Program</h2>




<div class="content expander_area">


<p style="text-align:justify;  width:95%;">
Drug abuse is a growing problem in the U.S., but even more so is the increasing incidence of prescription drug misuse. As the last line of defense for prescription drug diversion, it is imperative that pharmacists exercise due diligence when filling prescriptions for controlled substances to ensure every prescription is written for a legitimate medical purpose. Having a policy and procedure in place founded on established programs can help your pharmacy defend itself against DEA suspicion and avoid hefty fines or registration revocation.
</p>


<p style="text-align:justify; width:95%;">
Pharm AssessRBS has implemented a couple of tools to assist our customers in managing your patients utilizing controlled substances.  First is the new section within our RBS reporting that assists in monitoring controlled substance utilization; including brand and generic script counts and dollars for all scripts and cash scripts.  We encourage all of our customers to implement some type of controlled substance monitoring program for your pharmacy.  Our second tool can assist in actually monitoring your patients seeking controlled substance prescriptions from your pharmacy.  This program provides specific detail on how to implement a nationally established monitoring program called VIGIL (Verification, Identification, Generalization, Interpretation, Legalization). 
</p>

<p style="text-align:justify;  width:95%;">
For more information on how to implement the VIGIL program, please view the Pharm AssessRBS Controlled Substance Patient Monitoring presentation below. We have also provided a link to the VIGIL program for your convenience. If you would like to implement this program, please contact Pharm AssessRBS at <a href="mailto:cs\@pharmassess.com">cs\@pharmassess.com</a> or (888) 255-6526 for the complete program.
</p>
</div>

<h2 class="expander" style="cursor:pointer;"><span id="expanderSign2" class="sign">+</span>Program Presentation</h2>
<div class="content" hidden>
<ul><li><a target=\"_blank\" href="http\://${ENV}.pharmassess.com/members/WebShare/Controlled_Substance_Monitoring_Program/Controlled_Substance_Patient_Monitoring_Program_Presentation.pptx">Program PowerPoint Presentation</a></li></ul>
</div>

<h2 class="expander" style="cursor:pointer;"><span id="expanderSign5" class="sign">+</span>Program Documents</h2>
<div class="content" hidden>
<ul>
<li>
    <a target=\"_blank\" href="http\://${ENV}.pharmassess.com/members/WebShare/Controlled_Substance_Monitoring_Program/Patient_Medication_Use_Agreement.pdf">Patient Medication Use Agreement</a>
</li>
<li>
    <a target=\"_blank\" href="http\://${ENV}.pharmassess.com/members/WebShare/Controlled_Substance_Monitoring_Program/VIGIL_Documents.pdf">VIGIL Program Documents</a>
</li>

<li>
    <a target=\"_blank\" href="http\://${ENV}.pharmassess.com/members/WebShare/Controlled_Substance_Monitoring_Program/Vigil_Stickers.pdf">VIGIL Stickers</a>
</li>

</ul>
</div>
</div>



#;


#______________________________________________________________________________

&MyPharmassessMembersTrailer;

exit(0);
