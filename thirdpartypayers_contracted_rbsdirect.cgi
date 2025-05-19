require "D:/RedeemRx/MyData/RBSDesktop_routines.pl";
require "D:/RedeemRx/cgi-bin/cgi-lib.pl";

use File::Basename;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use Env qw(PATH REMOTE_ADDR PERL5LIB PERLLIB);

$| = 1;
my $start = time();
my ($prog, $dir, $ext) = fileparse($0, '\..*');
my %contracts = ();
$nbsp = "&nbsp\;";
my $tpps = '';
my $ACH;
my $MAC;
my $manual;
my $cont;
my %children = ();
my $children = 0;
my $cm;
my $cm2;
my $online;
my $upload;

$ret = &ReadParse(*in);
&CgiDie("Error in reading and parsing of CGI input") if !defined $ret;

$dbin     = "TPDBNAME";
$db       = $dbin;
$DBNAME   = $DBNAMES{"$dbin"};
$TABLE    = $DBTABN{"$dbin"};
$FIELDS   = $DBFLDS{"$dbin"};
$FIELDS2  = $DBFLDS{"$dbin"} . "2";
$fieldcnt = $#${FIELDS2} + 2;
##my $HASH   = $HASHNAMES{$dbin};

&readsetCookies;

&read_canned_header($RBSHeader);

if ( $USER ) {
    &MembersHeaderBlock
} else {
  &MembersLogin;
  &MyPharmassessMembersTrailer;

   print qq#</BODY>\n#;
   print qq#</HTML>\n#;
   exit(0);
}

# Connect to the Pharmacy database

$dbx = DBI->connect("DBI:mysql:$DBNAME:$DBHOST",$dbuser,$dbpwd,
        { PrintError => 1, RaiseError => 1, InactiveDestroy => 0 } ) || die "$DBI::errstr";
   
DBI->trace(1) if ($dbitrace);
 
#______________________________________________________________________________

##&readPharmacysTPPs;
&readThirdPartyPayers;
&readTPPPriSec;

$printcount = 0;
my %printed = ();

$ntitle = "Third Party Payers - Contracted\n";

print qq#<h1 class="thirdparty">$ntitle</h1>\n#;

&readContracts;
&displayTPP;

#______________________________________________________________________________

# Close the Database
$dbx->disconnect;

print "<hr>printcount: $printcount<hr>\n" if ($debug);

&MyPharmassessMembersTrailer;

exit(0);

#______________________________________________________________________________

sub displayTPP {
  print qq#<div id="treeGrid">\n#;
  print qq#</div>\n#;

#------------------------------------------
my $ADD_ID = 999999;

foreach $TPP_ID (sort {$a <=> $b} keys %TPP_BINs) {
  next if ( $TPP_PriSecs{$TPP_ID} =~ /Sec/i );

  $checkPriID = $Reverse_TPPPS_Pri_IDs{$TPP_ID};
  $checkSecID = $Reverse_TPPPS_Sec_IDs{$TPP_ID};
  $PayerType  = $TPP_Direct_Payers{$TPP_ID};

##  next if ( $PayerType  !~ /Contract/i );
  next if ( $checkPriID !~ /^\s*$/i );
  next if ( $checkSecID !~ /^\s*$/i );

  $TPPPS_Pri_IDs{$ADD_ID} = $TPP_ID;
  $TPPPS_Sec_IDs{$ADD_ID} = $TPP_ID;

  $ADD_ID--;
}
#------------------------------------------

@sorted = sort {
  $TPP_Names{$TPPPS_Pri_IDs{$a}} cmp $TPP_Names{$TPPPS_Pri_IDs{$b}}
} keys %TPPPS_Pri_IDs;

  foreach $key (@sorted) {
     $TPP_Pri_ID = $TPPPS_Pri_IDs{$key};
     ##next if($TPP_Pri_ID != 700020 && $TPP_Pri_ID != 700120);
     $children = 0;
     next if ( $TPP_Pri_ID <= 0 );

     $TPP_Sec_ID   = $TPPPS_Sec_IDs{$key};
     $TPP_Name     = $TPP_Names{$TPP_Pri_ID};
     $TPP_DirPayer = $TPP_Direct_Payers{$TPP_Pri_ID};

     next if ( $TPP_DirPayer !~ /Contract/i );

     next if ( $TPP_BINs{$TPP_Pri_ID} > 999990 || $TPP_BINs{$TPP_Sec_ID} > 999990 );

     if ( $TPP_BINs{$TPP_Sec_ID} =~ /^\s*$/ ) {
        if ( $debug ) {
           print "FIX! TPP_Sec_ID: $TPP_Sec_ID<br>\n";
           print "TPP_Pri_ID: $TPP_Pri_ID, key: $key, TPP_Sec_ID: $TPP_Sec_ID<br>\n";
           print "$nbsp TPP_BINs(TPPPS_Sec_IDs($key): $TPPPS_Sec_IDs{$key}, TPP_BINs(): $TPP_BINs{$TPP_Sec_ID}<br>\n";
        }
     } else {
        my $which = 0;
        if ( !$printed{$TPP_Pri_ID} ) {
           $which = 1;
           &printline($which, $TPP_Pri_ID, $TPP_Sec_ID);# if($TPP_Pri_ID == 700020 || $TPP_Pri_ID == 700120);
        }
        if ( $key < 999900 ) {
           $which = 2;
           $children = 1;
           &printline($which, $TPP_Pri_ID, $TPP_Sec_ID);# if($TPP_Pri_ID == 700020 || $TPP_Pri_ID == 700120);
        }

     }
  }
     $tpps .= qq#$cm } # if($tpps);

  print qq#
    <script type="text/javascript" src="/js/jqwidgets/scripts/jquery-1.11.1.min.js"></script>
    <link rel="stylesheet" href="../js/jqwidgets/jqwidgets/styles/jqx.base.css" type="text/css" />
    <script type="text/javascript" src="/js/jqwidgets/jqwidgets/jqx-all.js"></script>
    <script type="text/javascript" src="/js/jqwidgets/jqwidgets/globalization/globalize.js"></script>
    <link rel="stylesheet" href="../js/jqwidgets/jqwidgets/styles/jqx.arctic.css" type="text/css" />
    
  #;

print qq#<script>
\$(document).ready(function () {
   var tpps = [$tpps
        ];
    // prepare the data
    var source =
    {
        dataType: "json",
        dataFields: [
            { name: 'TPP_ID', type: 'number' },
            { name: 'PBM', type: 'string' },
            { name: 'Plan', type: 'string' },
            { name: 'BIN', type: 'string' },
            { name: 'HelpDesk', type: 'string' },
            { name: 'ACH', type: 'string' },
            { name: 'Manual', type: 'string' },
            { name: 'children', type: 'array' },
            { name: 'expanded', type: 'bool' },
            { name: 'Mac', type: 'string' },
            { name: 'Enrollment', type: 'string' },
            { name: 'Contract', type: 'string' },
            { name: 'Upload', type: 'string' }
        ],
        hierarchy:
        {
            root: 'children'
        },
        id: 'EmployeeID',
        localData:  tpps 
    };
    var dataAdapter = new \$.jqx.dataAdapter(source);
    // create Tree Grid
    \$("\#treeGrid").jqxTreeGrid(
    {
        width: 1330,
        theme: "arctic",
        source: dataAdapter,
        columnsHeight: 45,
        sortable: true,
        columns: [
          { text: 'PBM', dataField: 'PBM', width: 250 },
          { text: 'Plan', dataField: 'Plan', width: 250 },
          { text: 'BIN', dataField: 'BIN', width: 100 },
          { text: 'Help Desk', dataField: 'HelpDesk', cellsFormat: 'd', width: 120 },
          { text: 'ACH Setup Form', dataField: 'ACH', width: 120 },
          { text: 'Manual', dataField: 'Manual', width: 75 },
          { text: 'Mac Appeal<br>Turn-Around', dataField: 'Mac', width: 150 },
          { text: 'Online<br>Enrollment', dataField: 'Enrollment', width: 100 },
          { text: 'Executed<br>Contract', dataField: 'Contract', width: 100 },
          { text: '   ', dataField: 'Upload' },
        ]
    });
});
</script>
#;

}

# ______________________________________________________________________________

sub printline {
  my ($which, $TPP_Pri_ID, $TPP_Sec_ID) = @_;
  $cont = '';
  $contract = '';
  $online = '';
  $upload = '';

  my $TPP_ID_1 = "";

  if ( $which == 1 ) {
     $TPP_ID_1 = $TPP_Pri_ID;
  } else {
     $TPP_ID_1 = $TPP_Sec_ID;
  }

  $Website = $TPP_Websites{$TPP_Pri_ID};
  $OEnroll = $TPP_OnlineEnrollment{$TPP_Pri_ID};

  if ( $Website !~ /^\s*$/ && $Website !~ /^http:\/\//i ) {
     $Website =~ s/^/http:\/\//;
  }

  if ( $Website !~ /^\s*$/ ) {
    $PBM = qq#<a href='$Website'>$TPP_Names{$TPP_Pri_ID}</a>#;
  } else {
    $PBM = "$TPP_Names{$TPP_Pri_ID}";
  }

  $plan = "$TPP_Names{$TPP_ID_1}"; 
  $bins = "$TPP_BINs{$TPP_ID_1}";
  $hd = "$TPP_HelpDesks{$TPP_ID_1}";

  &print_ACH_Setup_Form($TPP_Name);
  &print_TPP_Manual($TPP_Name);

  $MAC_Appeal_Turn_Around = $TPP_MAC_Appeal_Turn_Arounds{$TPP_Pri_ID};
  ($jdays, $MAC_Appeal_Turn_Around) = split("-", $MAC_Appeal_Turn_Around, 2);
  $MAC_Appeal_Turn_Around =~ s/^\s*(.*?)\s*$/$1/;    # trim leading and trailing white spaces

  $MAC = "$MAC_Appeal_Turn_Around";

  if ( $OEnroll !~ /^\s*$/ ) {
    $online = qq#<a href='$OEnroll'><img src='/members/images/document.jpg'width='32' height='32' alt='Online Enrollment' title='Online Enrollment'></a>#;
  }

  if($which == 1) {
    $contract = $contracts{$PH_ID}{$TPP_Pri_ID};
    $upload  = qq# <a href='/members/UploadContract.cgi?TPP_ID=$TPP_Pri_ID'>Upload Contract</a>#;
  }

  if ($contract) {
  $cont =  qq#<a href='$contract'><img src='/members/images/document.jpg'width='32' height='32' alt='Uploaded Contract' title='Uploaded Contract'></a>#;
  }

  $displaycount++;

  $printed{$TPP_Pri_ID}++ if ( $which == 1 );

  $printcount++;
  if($tpps eq '') {
  $tpps = qq#
            {
                "TPPID": $TPP_ID_1, "PBM": "$PBM", "Plan": "$plan", "BIN": "$bins", "HelpDesk": "$hd", "ACH": "$ACH", "Manual": "$manual", "Mac": "$MAC", "Enrollment": "$online","Contract": "$cont", "Upload": "$upload", "expanded": "false",
            #;    
  }
  else {
  if ($which == 2) {
    if (!$children{$PBM}) {
    $cm2 = "],";   
    $tpps .= qq#
                 children: [
            #;    
      $children{$PBM}++;
    }
    $tpps .= qq# {"TPPID": $TPP_ID_1, "PBM": "$PBM", "Plan": "$plan", "BIN": "$bins", "HelpDesk": "$hd",  "ACH": "$ACH", "Manual": "$manual", "Mac": "$MAC","Enrollment": "", "Contract": "", "expanded": "false"},#;
  }
  else {
  $tpps .= qq#$cm2 }, #;
  $tpps .= qq#
            {
                "TPPID": $TPP_ID_1, "PBM": "$PBM", "Plan": "$plan", "BIN": "$bins", "HelpDesk": "$hd", "ACH": "$ACH", "Manual": "$manual", "Mac": "$MAC","Enrollment": "$online", "Contract": "$cont", "Upload": "$upload", "expanded": "false",
            #;    
   $cm2 = "";   
  }
  }

}

#______________________________________________________________________________
 
sub print_TPP_Manual {
  my ($TPP_Name) = @_;
  my $printed = 0;

  $webpath = qq#/WebShare/TPP_Manuals/$TPP_Name#;
  $dskpath = "D:/WWW/www.CIPNetwork.com/Webshare/TPP_Manuals/$TPP_Name";

  (@files) = &readfiles($dskpath);
  foreach $filename (sort {"\L$a" cmp "\L$b"} @files) {

     next if ( $filename =~ /Thumbs.db|\~$|.swp$/i );

     if ( $filename =~ /_/ ) {
        ($jdate, $rest) = split("_", $filename, 2);
     } else {
        $jdate = "";
        $rest  = $filename;
     }
   
     ##print qq#<a href="$webpath/$filename"><img src="/members/images/btn-download.gif" width="12" height="12" ></a> $nbsp#;
     $manual =  qq#<a href='$webpath/$filename'><img src='/members/images/btn-download.gif' width='12' height='12' ></a> $nbsp#;
     $printed++;
  }
  if ( !$printed ) {
    $manual =  '';
  }
}

sub readContracts {

  $webpath = qq#/members/WebShare/UploadedContracts#;
  $dskpath = "D:/WWW/www.pharmassess.com/members/Webshare/UploadedContracts";

  (@files) = &readfiles($dskpath);
  foreach $filename (sort {"\L$a" cmp "\L$b"} @files) {

     next if ( $filename =~ /Thumbs.db|\~$|.swp$/i );
     next if ( $filename !~ /_/ );

     if ( $filename =~ /_/ ) {
        ($PID, $tpp_id, $rest) = split("_", $filename, 3);
        $contracts{$PID}{$tpp_id} = "$webpath/$filename";
     } else {
     }
   
     ##print qq#<a href="$webpath/$filename"><img src="/members/images/btn-download.gif" width="12" height="12" ></a> $nbsp#;
  }
}

#______________________________________________________________________________

sub print_ACH_Setup_Form {
  my ($TPP_Name) = @_;

  $webpath = qq#/members/WebShare/ACH_Setup_Forms/$TPP_Name#;
  $dskpath = "D:/WWW/www.pharmassess.com/members/Webshare/ACH_Setup_Forms/$TPP_Name";

  my $printed = 0;

  (@files) = &readfiles($dskpath);
  foreach $filename (sort {"\L$a" cmp "\L$b"} @files) {

     next if ( $filename =~ /Thumbs.db|\~$|.swp$/i );

     if ( $filename =~ /_/ ) {
        ($jdate, $rest) = split("_", $filename, 2);
     } else {
        $jdate = "";
        $rest  = $filename;
     }

     $ACH =  qq#<a href='$webpath/$filename'><img src='/members/images/btn-download.gif' width='12' height='12' ></a> $nbsp#;
     $printed++;
  }
  if ( !$printed ) {
     $ACH =  qq#N/A#;
  }

  print "sub print_ACH_Setup_Form: Exit.<br>\n" if ($debug);

}

#______________________________________________________________________________

sub print_MAC_Appeal_Form {
  my ($TPP_Name) = @_;

  $webpath = qq#/WebShare/MAC_Appeal_Forms/$TPP_Name#;
  $dskpath = "D:/WWW/www.CIPNetwork.com/WebShare/MAC_Appeal_Forms/$TPP_Name";
# print "webpath: $webpath, dskpath: $dskpath<br>\n";

  (@files) = &readfiles($dskpath);
  foreach $filename (sort {"\L$a" cmp "\L$b"} @files) {

     next if ( $filename =~ /Thumbs.db|\~$|.swp$/i );
     my ($jdate, $rest) = split("_", $filename, 2);
   
     print qq#<a href="$webpath/$filename"><img src="/images/btn-download.gif" width="12" height="12" ></a> $nbsp#;
  }
}

#______________________________________________________________________________
#
sub Error {
  print "Content-type: text/html\n\n";
  print "The server can't $_[0] the $_[1]: $! \n";
  exit;
}  

#______________________________________________________________________________
