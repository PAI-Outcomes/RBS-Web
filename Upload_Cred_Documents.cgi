#______________________________________________________________________________
#
# Steve Downing 
# Date: 03/28/2025
#______________________________________________________________________________
#
require "D:/RedeemRx/MyData/RBSDesktop_routines.pl";
require "D:/RedeemRx/cgi-bin/cgi-lib.pl";
require "D:/RedeemRx/MyData/Testing_routines.pl";

use File::Basename;
use CGI;
use Env qw(PATH REMOTE_ADDR PERL5LIB PERLLIB);

$| = 1; # don't buffer output
my $q = CGI->new;
my $infname   = $q->param('fname');
my $inlname   = $q->param('lname');
my $inlnumber = $q->param('lnumber');
my $inltype   = $q->param('ltype');

$type{'Pharmacist'}            = 'Pharm';  
$type{'PIC'}                   = 'PIC';  
$type{'Intern'}                = 'Intern';  
$type{'Technician'}            = 'Tech';  
$type{'Technician Candidate'}  = 'Cand';  

$tmp = "$type{$inltype}";

$$tmp = 'selected';


#______________________________________________________________________________
#
my $start = time();
($prog, $dir, $ext) = fileparse($0, '\..*');
$PROG = "$prog" . "$ext";

$ret = &ReadParse(*in);

&CgiDie("Error in reading and parsing of CGI input") if !defined $ret;

#______________________________________________________________________________

&readsetCookies;
$ret = &ReadParse(*in);

&CgiDie("Error in reading and parsing of CGI input") if !defined $ret;

&read_canned_header($RBSHeader);



if ( $USER ) {
   &MembersHeaderBlock;
} else {
   &MembersLogin;
   &MyPharmassessMembersTrailer;

   print qq#</BODY>\n#;
   print qq#</HTML>\n#;
   exit(0);
}

&DisplayForm;

#______________________________________________________________________________

##&MyReconRxTrailer;

exit(0);

##############################################
# Subroutines
##############################################

sub DisplayForm {


print <<"HTML";
<html>
<script type="text/javascript" language="javascript" src="/js/upload835.js"></script>

<script>

function callback(data) {  
  \$("#alert").html('<br>Upload Complete.');
  document.getElementById("document_type").value = '';
  document.getElementById("DIV_FileUpload").style.display = "none";
  document.getElementById("DIV_ExpDate").style.display = "none";
  document.getElementById("DIV_Name").style.display = "none";
}

function checkingdata(dta) {
  document.getElementById("DIV_FileUpload").style.display = "none";
  document.getElementById("DIV_ExpDate").style.display = "none";
  document.getElementById("DIV_Name").style.display = "none";
  document.getElementById("alert").innerHTML = '';

  if (dta.match(/SP|DEA|CSC|PIC|LI|Pharm|Tech|Intern|Cand/)) {
    document.getElementById("ExpDate").value = '';
    document.getElementById("upfile").value = '';
    document.getElementById("alert").innerHTML = '*Only PDF File Formats Accepted*';
    document.getElementById("DIV_ExpDate").style.display = "block";

    if(dta.match(/PIC|Pharm|Tech|Intern|Cand/)) {
      document.getElementById("DIV_Name").style.display = "block";
    }
  }
  else if(dta.match(/[0-9][0-9[0-9][0-9]-/)) {
    doc = document.getElementById("document_type").value;
    if(doc.match(/PIC|Pharm|Tech|Intern|Cand/)) {
      document.getElementById("DIV_Name").style.display = "block";
    }
    document.getElementById("DIV_ExpDate").style.display = "block";
    document.getElementById("DIV_FileUpload").style.display = "block";
    document.getElementById("alert").innerHTML = '*Only PDF File Formats Accepted*';
  }
  else if (dta.match(/COI/)) {
    document.getElementById("DIV_FileUpload").style.display = "block";
    document.getElementById("alert").innerHTML = '*Only PDF File Formats Accepted*';
  }
}

function checkInput() {
   doc    = document.getElementById("document_type").value;
   fname  = document.getElementById("FName").value;
   lname  = document.getElementById("LName").value;
   lic    = document.getElementById("LicNumber").value;
   tmp    = document.getElementById("ExpDate").value;
   upfile = document.getElementById("upfile").value;
   exp = tmp.replace(/-/g,"");

  if ( document.getElementById("document_type").value == '' ) {
    alert("Please Select a type of document");
    return false;
  }
  if(doc.match(/PIC|Pharm|Tech|Intern|Cand/)) {
  
    if ( document.getElementById("FName").value == '' ) {
      alert("Very Important: Please add First Name ");
      return false;
    }
    if ( document.getElementById("LName").value == '' ) {
      alert("Very Important: Please add Last Name ");
      return false;
    }
    if ( lic == '' ) {
      alert("Very Important: Please add License Number ");
      return false;
    }
  }
  if ( document.getElementById("upfile").value == '' ) {
    alert("Please Select a File to Upload");
    return false;
  }
  if (!upfile.match(/.pdf/)) {
    alert("PDF Only Please");
    return false;
  }

  document.uploaddoc.action= "file_upload_testing.cgi?document_type=" + doc + "&Cred=Y" + "&FName=" + fname + "&LName=" + lname + "&ExpDate=" + exp + "&LicNumber=" + lic  ;
  return true;
}
</script>
<head>
<title>Credentialing Document Upload</title>
<body onload="checkingdata(document.getElementById('document_type').value)">
<h2>Credentialing Document Upload</h2>
<hr>
<br>

<form method="post" name="uploaddoc" action="file_upload_testing.cgi"  enctype="multipart/form-data" target="hidden_frame">

<div style="display: inline-block; width:200px">
Document Type: 
</div>

<SELECT NAME="document_type" ID="document_type" onChange="checkingdata(this.value)">
<OPTION VALUE="">Select a Document Type</OPTION>
<OPTION VALUE="SP" $SP>State Permit</OPTION>
<OPTION VALUE="DEA" $DEA>DEA License</OPTION>
<OPTION VALUE="CSC" $CSS>State Controlled License</OPTION>
<OPTION VALUE="LI" $LI>Liability Insurance</OPTION>
<OPTION VALUE="PIC" $PIC>Pharmacist In Charge License</OPTION>
<OPTION VALUE="Pharm" $Pharm>Staff Pharmacist License</OPTION>
<OPTION VALUE="Tech" $Tech>Pharmacy Tech License</OPTION>
<OPTION VALUE="Intern" $Intern>Pharmacy Intern License</OPTION>
<OPTION VALUE="Cand" $Cand>Pharmacy Technician Candidate License</OPTION>
<OPTION VALUE="COI"  $COI>Conflict Of Interest Form</OPTION>
</SELECT><br><br>


<div id="DIV_ExpDate" style="display: none">
 <div style="display: inline-block; width:200px">
 <label for="LicNumber">License</label>
 </div>
  <input type="text" id="LicNumber" name="LicNumber" value=$inlnumber><br><br>
 <div style="display: inline-block; width:200px">
 <label for="ExpDate">Expiration Date Of Document</label>
 </div>
  <input type="date" id="ExpDate" name="ExpDate" onChange="checkingdata(this.value)"><br><br>
</div>

<div id="DIV_Name" style="display: none">
 <div style="display: inline-block; width:200px">
 <label for="FName">First Name:</label>
 </div>
  <input type="txt" id="FName" name="FName" value=$infname><br><br>
 <div style="display: inline-block; width:200px">
 <label for="LName">Last Name:</label>
 </div>
  <input type="txt" id="LName" name="LName" value=$inlname>><br><br>
</div>


<div id="DIV_FileUpload" style="display: none">
  <div style="display: inline-block; width:200px">
    <p>Enter a file to upload: 
  </div>
  <input type="file" id='upfile' name="upfile"  style="border: solid .25px"/></p>
  <input type="submit" name="Submit" value="Upload File" onClick="return checkInput()">&nbsp
  <span id="msg"></span>
</div>
<br>
<div id="alert" style="font-weight:bold;"></div>
<iframe name='hidden_frame' id="hidden_frame" style='display:none'></iframe>
</form><br>

HTML
}
