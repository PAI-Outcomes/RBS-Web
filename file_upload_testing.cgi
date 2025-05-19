#!/usr/bin/perl

#use warnings;
##use strict;
use CGI;
use File::Basename;
require "D:/RedeemRx/cgi-bin/cgi-lib.pl";
require "D:/RedeemRx/MyData/RBSDesktop_routines.pl";
my %in;
my $ret;
my $date;
my $www = 'members';
$www = 'www' if ($ENV{'SERVER_NAME'} =~ /^dev./);
my ($sec,$min, $hour, $day, $month, $year) = (localtime)[0,1,2,3,4,5];
$year  += 1900;	# reported as "years since 1900".
$month += 1;	# reported ast 0-11, 0==January
$date  = sprintf("%04d%02d%02d%02d%02d%02d", $year, $month, $day, $hour, $min, $sec);

##$ret = &ReadParse(*in);
&readsetCookies;
&readPharmacies();

my $q = CGI->new;


##$CGI::POST_MAX = 1024 * 5000;
my $safe_filename_characters = "a-zA-Z0-9_.-";
my $filename = $q->param("upfile");
my $TPP_ID      = $q->url_param('TPP_ID');
my $type        = $q->url_param('document_type');
my $cred        = $q->url_param('Cred');
my $fname       = $q->url_param('FName');
my $lname       = $q->url_param('LName');
my $expdate     = $q->url_param('ExpDate');
my $license     = $q->url_param('LicNumber');

  print $q->header ( );
  if ( !$filename ) {
    print "No filename:$filename";
    print "<script>parent.callback('There was a problem uploading your file (try a smaller file).')</script>";
    exit;
  }

  my ( $name, $path, $extension ) = fileparse ( $filename, '..*' );
  $filename = $name . $extension;
  $filename =~ tr/ /_/;
  $filename =~ s/[^$safe_filename_characters]//g;
  
  if ( $filename =~ /^([$safe_filename_characters]+)$/ ) {
    $filename = $1;
  }
  else {
    die "Filename contains invalid characters";
    print "<script>parent.callback('Filename issues')</script>";
  }

my $UPLOAD_FH = $q->upload("upfile");

if ( $cred =~ /Y/i ) {
  $newfilename = "$Pharmacy_NCPDPs{$PH_ID}";
  $newfilename .= "_${fname} ${lname}" if ($fname);
  $newfilename .= "_$type";
  $newfilename .= "_$expdate" if ($expdate);
  $newfilename .= "_$license" if ($license);
  $newfilename .= ".pdf";  ##Has to stay at the end

  $upload_dir = "D:\\WWW\\${www}.pharmassess.com\\members\\WebShare\\Credentialing\\Licenses";
}
else {
  $newfilename = "${PH_ID}_${TPP_ID}_${date}_${type}_${filename}";
  $upload_dir = "D:\\WWW\\${www}.pharmassess.com\\members\\WebShare\\UploadedContracts\\$PH_ID";
}

umask 0000; #This is needed to ensure permission in new file

if (!-d $upload_dir) {
  mkdir "$upload_dir" or die "Unable to create $upload_dir\n";
}

open $NEWFILE_FH, ">$upload_dir/$newfilename"; 

if ($filename =~ /\.zip|.doc|.pdf|.xls/) {
 binmode $NEWFILE_FH;
}

while ( <$UPLOAD_FH> ) {
    print $NEWFILE_FH "$_";
}

close $NEWFILE_FH or die "I cannot close filehandle: $!";

##this is the only way to send msg back to the client
print "<script>parent.callback('File Upload: $filename--> Success!')</script>";

exit;


