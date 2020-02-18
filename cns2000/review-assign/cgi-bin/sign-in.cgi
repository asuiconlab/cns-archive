#! /usr/bin/perl

use Mysql;
use CGI;

require 'utils.pl';
require 'rev_utils.pl';

$cgi = new CGI();

$dbname = "cns2000";
$reviewer_n = $cgi->param(-name=>'id');

if (length($reviewer_n) < 5) {
    print "Location: ../\n\n";
}

$sql_reviewer_n = &sqlescape($reviewer_n);
$cgi_reviewer_n = $cgi->escape($reviewer_n);

&process_reviewer_set($cgi);

# Check to see if we want to view a particular paper first:
@keys = $cgi->param();
foreach $k (@keys) {
    if ($k =~ /view-(\d+)/) {
	$sid = $1;
	$range = $cgi->param(-name=>'range');
	print "Location: view.cgi?sid=$sid&reviewer_n=$cgi_reviewer_n&range=$range\n\n";
	exit 0;
    }
}

if ($reviewer_n eq "- none selected -") {
    print <<EOF;
Content-type: text/html

<html>
<head>
<title>Oops!</title>
</head>
<body bgcolor=white>
<h2>You need to select a reviewer name!</h2>
Please <a href="../">go back</a> to the entry page!
<hr>
<font size=2>
<i>Please contact
<a href="mailto:support\@cns.numedeon.com">support\@cns.numedeon.com</a>
if you have any questions regarding this Web page.</i>
</body>
</html>
EOF
    exit 0;
}

$qs = "select sid from tsub where locked='n' and cmdsuccess='y' order by sid";
$sth = &query($dbname, $qs) || &printerr("15a");

@sids=();
while($sid = $sth->fetchrow()) {
    @sids = (@sids, $sid);
}

$qs = "select paper_id, reviewer_id, reviewer_id_2 from review_assign where committee_member='$sql_reviewer_n' order by paper_id";
$sth = &query($dbname, $qs) || &printerr("13.5");

# initialize the unassigned counters:

foreach $j (1..9) {
    eval("\$unassigned_$j = 0");
}

# run thru and check to see which of the papers
#        (a) are missing from the list
#        (b) if not on the list, have no reviewers

$sid_i = 0;
while(($id, $rid, $rid2) = $sth->fetchrow()) {
    #
    # First, catch up the $sids[$sid_i] to the $id:
    #
    while ($sids[$sid_i] < $id && $sids[$sid_i] ne '') {
	print STDERR "ID: '$id' '$sids[$sid_i]'\n";
	$j = int($sid_i / 25) + 1;
	eval("\$unassigned_$j += 1");
	$sid_i++;
    }

    #
    # Now $sids[$sid_i] == $id:
    #
    if ($rid == -2 || $rid2 == -2) {
	$j = int($sid_i / 25) + 1;
	eval("\$unassigned_$j += 1");
    }
    $sid_i++;
}

# If they're not on the list and there are no more to be fetched from the
# database of papers assigned reviewers, make sure they're still counted.

while ($sid_i <= $#sids) {
    $j = int($sid_i / 25) + 1;
    eval("\$unassigned_$j += 1");
    $sid_i++;
}

$sth = &query($dbname, $qs) || &printerr("12");

print <<EOF;
Content-type: text/html

<html>
<head>
<title>
CNS*2000 Reviewer Assignment - Paper Ranges
</title>
</head>
<body bgcolor=white>
Welcome, <b>$reviewer_n</b>!<p>
For convenience - and so as not to overwhelm you! - we've broken down the
over 200 papers into subgroups of 25.  The number on the right is the
number of papers that have yet to be assigned reviewers.
<p>
You should <b>select one of the ranges</b> and then hit the "Assign Reviewers"
button.  Be sure to read the text at the bottom of this page before you
continue!

<form method=POST action="assign.cgi">
<input type=hidden name="reviewer_n" value="$reviewer_n">
<blockquote>
<table>
<tr>
    <th></th>
    <th>&nbsp;&nbsp;&nbsp;&nbsp;Range&nbsp;&nbsp;&nbsp;&nbsp;</th>
    <th>(Number Still to be Assigned Reviewers)</th>
</tr>
<tr>
    <td><input type=radio name=range value=1 checked></td>
    <td align=center> 1 - 25 </td>
    <td align=center> $unassigned_1 </td>
</tr>
<tr>
    <td><input type=radio name=range value=2></td>
    <td align=center> 26-50 </td>
    <td align=center> $unassigned_2 </td>
</tr>
<tr>
    <td><input type=radio name=range value=3></td>
    <td align=center> 51-75 </td>
    <td align=center> $unassigned_3 </td>
</tr>
<tr>
    <td><input type=radio name=range value=4></td>
    <td align=center> 76-100 </td>
    <td align=center> $unassigned_4 </td>
</tr>
<tr>
    <td><input type=radio name=range value=5></td>
    <td align=center> 101-125 </td>
    <td align=center> $unassigned_5 </td>
</tr>
<tr>
    <td><input type=radio name=range value=6></td>
    <td align=center> 126-150 </td>
    <td align=center> $unassigned_6 </td>
</tr>
<tr>
    <td><input type=radio name=range value=7></td>
    <td align=center> 151-175 </td>
    <td align=center> $unassigned_7 </td>
</tr>
<tr>
    <td><input type=radio name=range value=8></td>
    <td align=center> 176-200 </td>
    <td align=center> $unassigned_8 </td>
</tr>
<tr>
    <td><input type=radio name=range value=9></td>
    <td align=center> 201 on up </td>
    <td align=center> $unassigned_9 </td>
</tr>
<tr><td colspan=3><p></td></tr>
<tr><td colspan=3 align=center><input type=submit value="Assign Reviewers"></td></tr>
</table>
</blockquote>
</form>
<dl>
<dt><b>A few notes:</b></dt>
<dd><p>
If you have a JavaScript capable browser with JavaScript enabled,
then when you select a reviewer for a paper, a window will pop
up with the list of reviewer keywords for that reviewer.  If
you put this window behind the main browser window, it won't come to
the front again, so you can get rid of it if you need to do so.
<p>
If you <b>don't</b> have a JavaScript capable browser, then you
should print out a copy of the reviewer list, which is available
<a href="../reviewers.html">here</a>.
<p>
Some reviewers have been "turned off" as selections for some papers,
if they are from the same institution as the authors of the paper.
<p>
Note also that because of the several different submission formats this
year, the paper itself is only available in bitmap form.  Printouts
of the paper(s) can be FAXed to you as necessary.
</dd>
</dl>
<hr>
<font size=2>
<i>Please contact
<a href="mailto:support\@cns.numedeon.com">support\@cns.numedeon.com</a>
if you have any questions regarding this Web page.</i>
</body>
</html>

EOF
