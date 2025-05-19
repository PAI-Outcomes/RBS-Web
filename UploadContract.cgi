#______________________________________________________________________________
#
# Steve Downing 
# Date: 03/23/2020
# UploadContract.cgi
#______________________________________________________________________________
#
require "D:/RedeemRx/MyData/RBSDesktop_routines.pl";
require "D:/RedeemRx/cgi-bin/cgi-lib.pl";

use File::Basename;
use CGI;
use Env qw(PATH REMOTE_ADDR PERL5LIB PERLLIB);

$| = 1; # don't buffer output
#______________________________________________________________________________
#
my $start = time();
my ($prog, $dir, $ext) = fileparse($0, '\..*');
$PROG = "$prog" . "$ext";

$ret = &ReadParse(*in);
$tpp_id = $in{'TPP_ID'};

&CgiDie("Error in reading and parsing of CGI input") if !defined $ret;

&readsetCookies;

&read_canned_header($RBSHeader);

if ( $USER) {
  &MembersHeaderBlock;
} else {
   &MembersLogin;
   &MyPharmassessMembersTrailer;

   print qq#</BODY>\n#;
   print qq#</HTML>\n#;
   exit(0);
}

&DisplayForm;

&MyPharmassessMembersTrailer;

exit(0);

##############################################
# Subroutines
##############################################
##<script type="text/javascript" language="javascript" src="/members/js/jquery-1.2.6.js"></script>

sub DisplayForm {
print <<"HTML";
<html>
<script type="text/javascript" language="javascript" src="/members/js/uploadcontract.js"></script>
<script>
function showdiv(t) {
  document.getElementById("upload").style.display = "";
  document.getElementById("contracttype").value = t;
}
function submitform(t) {
   document.uploaddoc.action= "/members/file_upload.cgi?TPP_ID=$tpp_id&type=" + document.getElementById("contracttype").value; 
}

</script>
<head>
<title>Upload Contract</title>
<body>
<h2>Upload Contract</h2>
<hr>
<br>
<input type="hidden" id="contracttype" value="test">
<input type="radio" id="Base" name="contract" value="base" onclick=showdiv('Base')>
  <label for="Base">Base Agreement</label><br>
<input type="radio" id="Addendum" name="contract" value="Addendum" onclick=showdiv('Addendum')>
  <label for="Addendum">Addendum</label><br>
<div id="upload" style="display:none">
  <form method="post" id='form1' name="uploaddoc" onSubmit="return submitform();" enctype="multipart/form-data" target="hidden_frame">
  <p>Enter a file to upload: <input type="file" id='file' name="upfile" style="border: solid .25px" onclick="clear_msg()"/></p><br>
  <input type="submit" name="Submit" value="Upload File">
</div>
<span id="msg"></span>
</form>
<iframe name='hidden_frame' id="hidden_frame" style='display:none'></iframe>

HTML
}
