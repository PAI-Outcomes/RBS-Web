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

&readPharmacysTPPs;
&readThirdPartyPayers;

$DIRECT{700044} = "BCBS Mississippi";
$DIRECT{700002} = "Caremark";
#$DIRECT{700006} = "Express Script, Inc.";
$DIRECT{700003} = "Humana";
$DIRECT{700170} = "Catamaran";
$DIRECT{700150} = "OptumRx";

$ntitle = "Third Party Direct Payers\n";

print qq#<h1 class="thirdparty">$ntitle</h1>\n#;

&displayTPP;

#______________________________________________________________________________

&MyPharmassessMembersTrailer;

exit(0);

#______________________________________________________________________________

sub displayTPP {
  print qq#<!-- displayTPP -->\n#;

  $processedcount = 0;

  print qq#<table class="thirdparty-table">\n#;
  print qq#<tr valign=bottom>\n#;
  print qq#<th class="lj_blue_bb">Payer</th>\n#;
  print qq#<th class="lj_blue_bb">BIN \#</th>\n#;
  print qq#<th class="lj_blue_bb">Phone</th>\n#;
  print qq#<th class="lj_blue_bb">Manual</th>\n#;
  print qq#<th class="lj_blue_bb">MAC Appeal Form</th>\n#;
  print qq#<th class="lj_blue_bb">MAC Appeal Turn-Around</th>\n#;
  print qq#</tr>\n#;

  foreach $TPP_ID (sort { $DIRECT{$a} cmp $DIRECT{$b} } keys %DIRECT ) {
     my $TPP_Name        = $TPP_Names{$TPP_ID};
     my $TPP_Phone       = $TPP_Business_Phones{$TPP_ID};
     my $TPP_Website     = $TPP_Websites{$TPP_ID};
     my $BIN             = $TPP_BINs{$TPP_ID};
     my $SBINs           = $TPP_Secondary_BINs{$TPP_ID};
     my $Pharmacy_ID     = $PTPharmacy_IDs{$TPP_ID};
     my $Pharmacy_Name   = $Pharmacy_Names{$Pharmacy_ID};
     my $Pharmacy_Status = $Pharmacy_Statuses{$PTPharmacy_IDs{$TPP_ID}};
     my $MAC_Appeal_Turn_Around = $TPP_MAC_Appeal_Turn_Arounds{$TPP_ID};

     ($jdays, $MAC_Appeal_Turn_Around) = split("-", $MAC_Appeal_Turn_Around, 2);
     $MAC_Appeal_Turn_Around =~ s/^\s*(.*?)\s*$/$1/;    # trim leading and trailing white spaces

     if ( $TPP_Website && $TPP_Website !~ /^http/i ) {
        $TPP_Website = "http://" . $TPP_Website;
     }

     $processedcount++;
     print qq#<tr>\n#;
     print qq#<td valign=top nowrap>#;
     if ( $TPP_Website !~ /^\s*$/ ) {
        print qq#<a href="$TPP_Website" target="_blank">$TPP_Name</a>#;
     } else {
        print qq#$TPP_Name#;
     }
     print qq#</td>\n#;
     print qq#<td nowrap>$BIN#;
     if ( $SBINs !~ /^\s*$/ ) {
       $jBIN = "$BIN";
       print qq# (<a href="javascript:ReverseDisplay('$jBIN')">more</a>)\n#;
       print qq#   <div id="$jBIN" style="display:none\;">\n#;
       @array = split(":", $SBINs);
       foreach $pc (@array) {
         my $TPP_Sec_ID = $Reverse_TPP_BINs{$pc};
          my $TPP_Secondary_Name = $TPP_Names{$TPP_Sec_ID};
          $TPP_Secondary_Name = "<i>Not in DB</i>" if ( !$TPP_Secondary_Name );
          print qq#$pc - $TPP_Secondary_Name<br>\n#;
       }
       print qq#   </div>\n#;
     }
     print qq#</td>\n#;

     print qq#<td nowrap>$TPP_Phone</td>\n#;

     print qq#<td align=center valign=middle>#;
     &print_TPP_Manual($TPP_Name);
     print qq#</td>#;

     print qq#<td align=center valign=middle>#;
     &print_MAC_Appeal_Form($TPP_Name);
     print qq#</td>#;

     print qq#<td nowrap>$MAC_Appeal_Turn_Around</td>\n#;
     print qq#</tr>\n#;

   }
   if ( !$processedcount ) {
      print qq#<tr><th align=left colspan=4>No Third Party Direct Payers defined</th></tr>\n#;
   }
   print qq#</table>\n#;
}

#______________________________________________________________________________
 
sub print_TPP_Manual {
  my ($TPP_Name) = @_;

  $webpath = qq#/members/WebShare/TPP_Manuals/$TPP_Name#;
  $dskpath = "D:/WWW/www.pharmassess.com/members/WebShare/TPP_Manuals/$TPP_Name";

  (@files) = &readfiles($dskpath);
  foreach $filename (sort {"\L$a" cmp "\L$b"} @files) {
     next if ( $filename =~ /Thumbs.db|\~$|.swp$/i );
     my ($jdate, $rest) = split("_", $filename, 2);
   
     print qq#<a href="$webpath/$filename" target="_blank"><img src="/images/open_file.png" width="14" height="14" ></a> $nbsp#;
  }
}

#______________________________________________________________________________

sub print_MAC_Appeal_Form {
  my ($TPP_Name) = @_;

  $webpath = qq#/members/WebShare/MAC_Appeal_Forms/$TPP_Name#;
  $dskpath = "D:/WWW/www.pharmassess.com/members/WebShare/MAC_Appeal_Forms/$TPP_Name";

  (@files) = &readfiles($dskpath);
  foreach $filename (sort {"\L$a" cmp "\L$b"} @files) {

     next if ( $filename =~ /Thumbs.db|\~$|.swp$/i );
     my ($jdate, $rest) = split("_", $filename, 2);
   
     print qq#<a href="$webpath/$filename" target="_blank"><img src="/images/open_file.png" width="14" height="14" ></a> $nbsp#;
  }
}

#______________________________________________________________________________
#
