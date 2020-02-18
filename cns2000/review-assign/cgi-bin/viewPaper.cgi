#!/usr/bin/perl

use CGI;
require "utils.pl";
$CNS_DB="cns2000";

$cgi = new CGI();

$sid = $cgi->param(-name=>'sid');
$page = $cgi->param(-name=>'page');

local (@row, @rows);

$qs = "SELECT page FROM pages WHERE sid = $sid ORDER BY page";
$sth = &query($CNS_DB, $qs) || &printerr("SQL err: 9215");
 
while (@row = $sth->fetchrow()) {
    @rows = (@rows, @row);
}

$MINPAGE = $rows[0];

if (length($page) > 0) { $CURRENTPAGE = $page; }
else { $CURRENTPAGE = $MINPAGE; }

$MAXPAGE = $rows[$#rows];

$output = <<EOF;
Content-type: text/html
Cache-Control: max-age=0

<html>
<head><title>Page view: page $CURRENTPAGE</title></head>
<body bgcolor="ffffff" fgcolor="000000">
(You may have to hit 'Reload' to get your browser to acknowledge changes,
if you've loaded this page before.)
<p>
This is a <b>low-resolution</b> bitmap version of your paper; the actual
printed out copy will be of 600 dpi quality.
<hr>
<a href=${CGI_ROOT}getPage.cgi?sid=${sid}&page=$CURRENTPAGE&uid=$uid&pwd=$pwd>
<img align=left width=80% border hspace=20
src="${CGI_ROOT}getPage.cgi?sid=${sid}&page=$CURRENTPAGE&uid=$uid&pwd=$pwd" alt="Page $CURRENTPAGE"></a>
<table>
EOF

foreach $row (@rows) {
    $output .= <<EOF;
<tr><td><form action=viewPage.cgi method=POST>
<input type=hidden name=sid value=$sid>
<input type=hidden name=page value=$row>
<input type=hidden name=uid value=$uid>
<input type=hidden name=pwd value=$pwd>
<input type=submit value="Page $row">
</form></td></tr>
EOF
}

$output .= <<EOF;
</table>
<form action="mainMenu.cgi" method="POST">
<input type=hidden name="uid" value=$uid>
<input type=hidden name="pwd" value=$pwd>
<table>
<tr><td><input type=submit value="Return to main menu"></tr></td>
</table>
</form>
EOF

print $output;
print "<hr>";

# &printFooter();

1;
