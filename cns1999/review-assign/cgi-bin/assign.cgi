#! /usr/bin/perl

use CGI;
use Mysql;

require 'utils.pl';
require 'rev_utils.pl';

$cgi = new CGI();

$dbname = "cns99";

$reviewer_n = $cgi->param(-name=>'reviewer_n');
$range = int($cgi->param(-name=>'range'));

if (length($reviewer_n) < 5) {
    print "Location: ../\n\n";
}

$cgi_reviewer_n = $cgi->escape($reviewer_n);
$sql_reviewer_n = &sqlescape($reviewer_n);

&process_reviewer_set($cgi);

$min = ($range - 1) * 25;
$max = $range * 25;

$qs = "select sid from tsub where locked='y' and cmdsuccess='y' order by sid";
$sth = &query($dbname, $qs) || &printerr("15a");

while($sid = $sth->fetchrow()) {
    @sids = (@sids, $sid);
}

$min_sid = $sids[$min];

if ($max <= $#sids) {
    $max_sid = $sids[$max];
} else {
    $max_sid = $sids[$#sids];
}

$qs = "SELECT uid,sid,title,cmdsuccess,lname1,fname1,email1,lname2,fname2,email2,lname3,fname3,email3,lname4,fname4,email4,lname5,fname5,email5,lname6,fname6,email6,lname7,fname7,email7,lname8,fname8,email8 FROM tsub WHERE cmdsuccess='y' and locked='y' AND sid BETWEEN $min_sid AND $max_sid ORDER BY sid";

$sth = &query($dbname, $qs) || &printerr("15b");

@list_query = $sth->fetchrow();
while(@list = $sth->fetchrow()) {
    @list_query = (@list_query, @list);
}

$qs = "SELECT rid,name,comments,keywords,exclude_list FROM reviewers";
$sth = &query($dbname, $qs) || &printerr("18");

@reviewers = ();
while (@reviewer_query = $sth->fetchrow()) {
    local($rid,@tmp_list) = @reviewer_query;
    $n_papers[$rid] = 0;
    @reviewers = (@reviewers, @reviewer_query);
}

$qs = "SELECT paper_id, reviewer_id, reviewer_id_2 FROM review_assign WHERE committee_member='$sql_reviewer_n' ORDER BY paper_id";

$sth = &query($dbname, $qs) || &printerr("19");

@rev_assigns = ();
while (@rev_assign = $sth->fetchrow()) {
    local($paper_id,$rid,$rid2) = @rev_assign;
    if ($paper_id >= $min_sid && $paper_id <= $max_sid) {
	@rev_assigns = (@rev_assigns, @rev_assign);
    }
    $n_papers[$rid]++ if ($rid >= 0);
    $n_papers[$rid2]++ if ($rid2 >= 0);
}

print <<EOF;
Content-type: text/html

<html>
<head>
<title>CNS*99 Reviewer Assignment - Papers $min-$max</title>
</head>
<body bgcolor=white>

<SCRIPT>
  <!--
  function gotoInWin(selector)
  {
      if (selector.options[selector.options.selectedIndex].value >= 0)  {
	  var myWin=window.open("../reviewers.html#" + selector.options[selector.options.selectedIndex].value,"reviewWindow","height=400,width=510,scrollbars=yes,dependent=yes");
      }
  }
  //-->
</SCRIPT>

<form method=POST action="sign-in.cgi">
<input type=hidden name=id value="$reviewer_n">
<input type=hidden name=range value="$range">
<table width=100%><tr><td align=center>
<input type=submit value="-> Save Assignments <-">
</td></tr></table>
<table width=100%>
<tr>
<td colspan=4><hr></td></tr>
<th align=left>ID</th>
<th align=left>Name(s) of author(s)</th>
<th align=center>Title</th>
</tr>
<tr><td colspan=4><hr></td></tr>
EOF

$index = 0;
while (($uid,$sid,$title,$cmdsuccess,$lname1,$fname1,$email1,$lname2,$fname2,$email2,$lname3,$fname3,$email3,$lname4,$fname4,$email4,$lname5,$fname5,$email5,$lname6,$fname6,$email6,$lname7,$fname7,$email7,$lname8,$fname8,$email8,@list_query) = @list_query) {
    $id = $min + $index;
    $qs = "select email,pwd from tuser where uid=$uid";
    $account_sth = &query($dbname, $qs) || &printerr("SQL error B.\n");
    ($email,$pwd) = $account_sth->fetchrow();

    $last = 1;
    while (eval("\$lname$last") ne "") {
	$last = $last+1;
    }
    $lastp = $last;
    $last = $last - 1;

    if ($email1 eq $email) {
	$corresponding_author = "<b>(*)</b>";
    } else {
	$corresponding_author = "";
    }

    print <<EOF;
<tr>
<td valign=center rowspan=$last>
<a name="paper$id">
-$id-&nbsp;&nbsp;&nbsp;&nbsp;</td>
<td><font size=-2>(1)</font> $lname1, $fname1 $corresponding_author</td>
<td valign=top align=center rowspan=$last><font size=+1>$title</font></td>
<td valign=middle align=center rowspan=$lastp>

<input type=submit value="View Paper" name="view-$sid">
<!-- <a href="view.cgi?sid=$sid&reviewer_n=$cgi_reviewer_n&range=$range">VIEW<br>PAPER</a> -->

</td>
</tr>
EOF
    foreach $i (2..$last) {
	if (eval("\$email$i") eq $email) {
	    $corresponding_author = "<b>(*)</b>";
	} else {
	    $corresponding_author = "";
	}

	$lname_tmp = eval("\$lname$i");
	$fname_tmp = eval("\$fname$i");
	print "<tr><td><font size=-2>($i)</font> $lname_tmp, $fname_tmp $corresponding_author</td><td></td><td></td></tr>\n";
    }

    # Set up the first reviewer list.

    @rev_assigns_tmp = @rev_assigns;

    $finished = 0;

    $op_ck_neg1 = "";
    $op_ck_neg2 = "";

    if (! (($pid, $rid, $rid2, @rev_assigns_tmp) = @rev_assigns_tmp)) {
	$finished = 1;
    }
    while(!$finished) {
	if ($pid == $sid && $rid > -2) {
	    if ($rid == -1) {
		$op_ck_neg1 = "selected";
	    } else {
		eval("\$op_ck_$rid = \"selected\"");
	    }
	    $finished = 1;
	}
	if (! (($pid, $rid, $rid2, @rev_assigns_tmp) = @rev_assigns_tmp)) {
	    $finished = 1;
	}
    }
    if (!$finished) {
	$op_ck_neg2 = "selected";
    }

    $reviewer_1_select_list ="<option value=-2 $op_ck_neg2> - unassigned -" .
	"<option value=-1 $op_ck_neg1> - decline to assign -";

    @reviewers_tmp = @reviewers;
    while(($rid,$name,$comments,$keywords,$excludes,@reviewers_tmp) = @reviewers_tmp) {
	if ($rid >= 0) {
	    $op_ck = eval("\$op_ck_$rid");
	    eval("\$op_ck_$rid = \"\"");
	}
	# Get number of papers already assigned to this reviewer:
	$n = $n_papers[$rid];

	# Check to make sure that this paper isn't on his excludes list;
	$i = 0; $ok = 1;
	@excludes_list = split(/,/,$excludes);
	while($i <= $#excludes_list && $ok) {
	    print STDERR $sid, " --> ", int($excludes_list[$i]), "\n";
	    $ok = 0 if ($sid == int($excludes_list[$i]));
	    $i++;
	}
	if ($ok) {
	    $reviewer_1_select_list .="<option value=$rid $op_ck>$name ($n)\n";
	}
    }
    # Set up the second reviewer list.

    @rev_assigns_tmp = @rev_assigns;

    $finished = 0;

    $op_ck_neg1 = "";
    $op_ck_neg2 = "";

    if (! (($pid, $rid, $rid2, @rev_assigns_tmp) = @rev_assigns_tmp)) {
	$finished = 1;
    }
    while(!$finished) {
	if ($rid2 >= 0) {	# Clear reviewer autoselect
	    eval("\$op_ck_$rid2 = \"\"");
	}

	if ($pid == $sid && $rid2 > -2) {
	    if ($rid2 == -1) {
		$op_ck_neg1 = "selected";
	    } else {
		eval("\$op_ck_$rid2 = \"selected\"");
	    }
	    $finished = 1;
	}
	if (! (($pid, $rid, $rid2, @rev_assigns_tmp) = @rev_assigns_tmp)) {
	    $finished = 1;
	}
    }
    if (!$finished) {
	$op_ck_neg2 = "selected";
    }

    $reviewer_2_select_list ="<option value=-2 $op_ck_neg2> - unassigned -" .
	"<option value=-1 $op_ck_neg1> - decline to assign -";

    @reviewers_tmp = @reviewers;
    while(($rid,$name,$comments,$keywords,$excludes,@reviewers_tmp) = @reviewers_tmp) {
	if ($rid >= 0) {
	    $op_ck = eval("\$op_ck_$rid");
	    eval("\$op_ck_$rid = \"\"");
	}
	# Get number of papers already assigned to this reviewer:
	$n = $n_papers[$rid];

	# Check to make sure that this paper isn't on his excludes list;
	$i = 0; $ok = 1;
	@excludes_list = split(/,/,$excludes);
	while($i <= $#excludes_list && $ok) {
	    print STDERR $sid, " --> ", int($excludes_list[$i]), "\n";
	    $ok = 0 if ($sid == int($excludes_list[$i]));
	    $i++;
	}
	if ($ok) {
	    $reviewer_2_select_list .="<option value=$rid $op_ck>$name ($n)\n";
	}
    }

    print <<EOF;
<tr><td></td><td colspan=3>
<b>Reviewer 1: <select name=reviewer1-$sid onChange="gotoInWin(this)"> $reviewer_1_select_list </select>
</td></tr>
<tr><td></td><td colspan=3>
<b>Reviewer 2: <select name=reviewer2-$sid onChange="gotoInWin(this)"> $reviewer_2_select_list </select>
</td></tr>
EOF

    print "<tr><td colspan=4><hr></td></tr>";
    $index += 1;
}
print <<EOF;
</table>
<table width=100%><tr><td align=center>
<input type=submit value="-> Save Assignments <-">
</td></tr></table>
</form>
<hr>
<font size=2>
<i>Please contact
<a href="mailto:support\@cns.numedeon.com">support\@cns.numedeon.com</a>
if you have any questions regarding this Web page.</i>
</body>
</html>
EOF

exit 0;
