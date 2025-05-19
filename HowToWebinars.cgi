require "D:/RedeemRx/MyData/RBSDesktop_routines.pl";
require "D:/RedeemRx/cgi-bin/cgi-lib.pl";

use File::Basename;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use Env qw(PATH REMOTE_ADDR PERL5LIB PERLLIB);
use DateTime;

$| = 1; 
my $start = time();
($prog, $dir, $ext) = fileparse($0, '\..*');

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

$ntitle = "\"How To\" Webinars";
print qq#<h1>$ntitle</h1>\n\n#;

&printMenu;

print qq#\n#;

#______________________________________________________________________________

&MyPharmassessMembersTrailer;

exit(0);

#_______________________________________________________________________________

sub printMenu {
  #Master source for document links ($dochost)
  #The master will be on pharmassess.com
  $HTTP_HOST = $ENV{'HTTP_HOST'};
  if ($HTTP_HOST =~ /^dev/i) {
    $dochost = "http://dev.pharmassess.com";
  } else {
    $dochost = "http://www.pharmassess.com";
  }
  #------------------------------------------#

  print qq#
  
  <script>
   \$(document).ready(function(){
    \$(\".expander1\").click(function(){
        \$(\".content1\").slideToggle(\"slow\");
    });
  });
   \$(document).ready(function(){
    \$(\".expander2\").click(function(){
        \$(\".content2\").slideToggle(\"slow\");
    });
  });
   \$(document).ready(function(){
    \$(\".expander3\").click(function(){
        \$(\".content3\").slideToggle(\"slow\");
    });
  });  
   \$(document).ready(function(){
    \$(\".expander4\").click(function(){
        \$(\".content4\").slideToggle(\"slow\");
    });
  });  
   \$(document).ready(function(){
    \$(\".expander5\").click(function(){
        \$(\".content5\").slideToggle(\"slow\");
    });
  });  
   \$(document).ready(function(){
    \$(\".expander6\").click(function(){
        \$(\".content6\").slideToggle(\"slow\");
    });
  });  
   \$(document).ready(function(){
    \$(\".expander7\").click(function(){
        \$(\".content7\").slideToggle(\"slow\");
    });
  });  
   \$(document).ready(function(){
    \$(\".expander8\").click(function(){
        \$(\".content8\").slideToggle(\"slow\");
    });
  });  
   \$(document).ready(function(){
    \$(\".expander9\").click(function(){
        \$(\".content9\").slideToggle(\"slow\");
    });
  });  
  </script>
  #;
  
  print qq#
  <ul>
      <li>
	      <a class=\"expander3\" style=\"cursor: pointer; font-size:145%;\"><strong>Inventory Management Report</strong></a>
	      <div class=\"content3\" hidden>
	          <iframe width=\"640\" height=\"360\" src=\"https://www.youtube.com/embed/NY080ASWke8\" frameborder=\"0\" allowfullscreen></iframe>
		  </div>
	  </li>
	  <li>
          <a class=\"expander4\" style=\"cursor: pointer; font-size:145%;\"><strong>Prescription Savings Program</strong></a>
	      <div class=\"content4\" hidden>
	          <iframe width=\"640\" height=\"360\" src=\"https://www.youtube.com/embed/todpOj5JE8s\" frameborder=\"0\" allowfullscreen></iframe>
		  </div>
	  </li>
	  
	  <li>
          <a class=\"expander5\" style=\"cursor: pointer; font-size:145%;\"><strong>Synchronization Assistance Program</strong></a>
	      <div class=\"content5\" hidden>
	          <iframe width=\"640\" height=\"360\" src=\"https://www.youtube.com/embed/ty1EjcXVqcA\" frameborder=\"0\" allowfullscreen></iframe>
		  </div>
	  </li>	 

	  <li>
          <a class=\"expander6\" style=\"cursor: pointer; font-size:145%;\"><strong>Controlled Substance Patient Monitoring Program</strong></a>
	      <div class=\"content6\" hidden>
	          <iframe width=\"640\" height=\"360\" src=\"https://www.youtube.com/embed/quglD3uD608\" frameborder=\"0\" allowfullscreen></iframe>
		  </div>
	  </li>
	  <li>
          <a class=\"expander7\" style=\"cursor: pointer; font-size:145%;\"><strong>Travel Health Services Vaccination Program</strong></a>
              <div class=\"content7\" hidden>
                  <iframe width=\"640\" height=\"360\" src=\"https://www.youtube.com/embed/9M6AH0tzUJE\" frameborder=\"0\"  allowfullscreen></iframe>
                  </div>
	  </li>
	  <li>
          <a class=\"expander8\" style=\"cursor: pointer; font-size:145%;\"><strong>Amplicare Platform Overview</strong></a>
              <div class=\"content8\" hidden>
                  <iframe width=\"640\" height=\"360\" src=\"https://www.youtube.com/embed/4jXpDDJ_zcE\" frameborder=\"0\"  allowfullscreen></iframe>
                  </div>
	  </li>
	  <li>
          <a class=\"expander9\" style=\"cursor: pointer; font-size:145%;\"><strong>Amplicare Match 2021 Overview</strong></a>
              <div class=\"content9\" hidden>
                  <iframe width=\"640\" height=\"360\" src=\"https://www.youtube.com/embed/5GsRyWwV5Fc\" frameborder=\"0\"  allowfullscreen></iframe>
                  </div>
	  </li>
  </ul>
  #;

}

#_______________________________________________________________________________
