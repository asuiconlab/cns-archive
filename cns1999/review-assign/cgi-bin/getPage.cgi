#!/usr/bin/perl

# Used to display an image stored in a database blob.

use CGI;
use Mysql;
$cgi = new CGI();

require "utils.pl";

$db = "cns99";
$sid = $cgi->param(-name=>'sid');
$page = $cgi->param(-name=>'page');

$qs = "SELECT jpeg FROM pages WHERE sid='$sid' AND page=$page";
$sth = &query($db,$qs);
@row = $sth->fetchrow();

print "Content-type: image/jpeg\n\n";

print $row[0];
