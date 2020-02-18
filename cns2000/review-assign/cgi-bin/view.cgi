#! /usr/bin/perl

use CGI;
use Mysql;
$dbname = "cns2000";

require 'utils.pl';
require 'rev_utils.pl';

$cgi = new CGI();
$reviewer_n = $cgi->param(-name=>'reviewer_n');
$sid_view = $cgi->param(-name=>'sid');
$range = $cgi->param(-name=>'range');
$page = $cgi->param(-name=>'page');

$fullpage = 0;
$fullpage = 1 if (defined($cgi->param(-name=>'fullpage')));

if (length($reviewer_n) < 5) {
    print "Location: ../\n\n";
}

if (!defined($page)) { $page = 1; }

$cgi_reviewer_n = $cgi->escape($reviewer_n);
$sql_reviewer_n = &sqlescape($reviewer_n);

&process_reviewer_set($cgi);

if (defined($cgi->param(-name=>'go_next'))) {
    $sid_view = $cgi->param(-name=>'next');
    $page = 1;
}
if (defined($cgi->param(-name=>'go_prev'))) {
    $sid_view = $cgi->param(-name=>'prev');
    $page = 1;
}
if (defined($cgi->param(-name=>'return'))) {
    print "Location: assign.cgi?reviewer_n=$cgi_reviewer_n&range=$range\n\n";
}
if (defined($cgi->param(-name=>'prev_page'))) {
    $page--;
}
if (defined($cgi->param(-name=>'next_page'))) {
    $page++;
}

$qs = "SELECT uid,sid,title,cmdsuccess,lname1,fname1,email1,lname2,fname2,email2,lname3,fname3,email3,lname4,fname4,email4,lname5,fname5,email5,lname6,fname6,email6,lname7,fname7,email7,lname8,fname8,email8,abstract,lastMod FROM tsub WHERE sid=$sid_view";

$sth = &query($dbname, $qs) || &printerr("18.2c");

($uid,$sid,$title,$cmdsuccess,$lname1,$fname1,$email1,$lname2,$fname2,$email2,$lname3,$fname3,$email3,$lname4,$fname4,$email4,$lname5,$fname5,$email5,$lname6,$fname6,$email6,$lname7,$fname7,$email7,$lname8,$fname8,$email8,$abstract,$last_mod) = $sth->fetchrow();

$last=1;
while (eval("\$lname$last") ne "") {
    $last = $last+1;
}
$lastp = $last;
$last = $last - 1;

# Get the number of pages:

$qs = "SELECT page FROM pages WHERE sid=$sid_view ORDER BY page";
$sth = &query($dbname, $qs) || &printerr("18.5c");

$min_page = $sth->fetchrow();

$max_page = $min_page;		# only one page?
while($x = $sth->fetchrow()) {
    $max_page = $x;
}

if (!$fullpage) {

# Get the list of valid papers so that we can present "next" and "previous"
# buttons where appropriate.

    $qs = "SELECT sid FROM tsub WHERE locked='y' AND cmdsuccess='y' ORDER BY sid";
    $sth = &query($dbname, $qs) || &printerr("18.3c");

    while(($s) = $sth->fetchrow()) {
	@sid_list = (@sid_list, $s);
    }
    if ($sid_view == $sid_list[0]) {
	$prev_sid = -1;
	$next_sid = $sid_list[1];
    }
    if ($sid_view == $sid_list[$#sid_list]) {
	$prev_sid = $sid_list[$#sid_list - 1];
	$next_sid = -1;
    }
    foreach $i (1..($#sid_list-1)) {
	if ($sid_view == $sid_list[$i]) {
	    $prev_sid = $sid_list[$i - 1];
	    $next_sid = $sid_list[$i + 1];
	}
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
	
	if ($paper_id == $sid_view) {
	    @rev_assigns = (@rev_assigns, @rev_assign);
	}
	
	$n_papers[$rid]++ if ($rid >= 0);
	$n_papers[$rid2]++ if ($rid2 >= 0);
    }
}


$fullpage_title = "";
$fullpage_tag = "";
if ($fullpage) {
    $fullpage_tag = "<input type=hidden name=fullpage value=yes>";
    $fullpage_title = "(Full page view)";
    
}

print <<EOF;
Content-type: text/html

<html>
<head>
<title>CNS*2000 Reviewer Assignment - Paper View $fullpage_title</title>
</head>
<body bgcolor=white>
<form method=POST action="view.cgi">
<input type=hidden name=sid value=$sid_view>
<input type=hidden name=range value=$range>
<input type=hidden name=reviewer_n value="$reviewer_n">
<input type=hidden name=page value="$page">
$fullpage_tag
EOF

if (!$fullpage) {
    print <<EOF;

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
<table width=100%>
<tr><td colspan=4><hr></td></tr>
<tr>
<td align=center colspan=3>
<a name="paper$id">
&nbsp;&nbsp;&nbsp;&nbsp;
<font size=+1><b>$title</b></font></td>
</tr>
<tr>
<td></td>
<td><font size=-2>(1)</font> $lname1, $fname1 $corresponding_author</td>
<td></td><td></td>
</tr>
EOF

    foreach $i (2..$last) {
	$lname_tmp = eval("\$lname$i");
	$fname_tmp = eval("\$fname$i");
	print "<tr><td></td><td><font size=-2>($i)</font> $lname_tmp, $fname_tmp</td><td></td><td></td></tr>\n";
    }

    print "<tr><td></td><td colspan=3>
<blockquote>
$abstract
</blockquote>
</td></tr>";

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
	    $ok = 0 if ($sid == int($excludes_list[$i]));
	    $i++;
	}
	if ($ok) {
	    $reviewer_2_select_list .="<option value=$rid $op_ck>$name ($n)\n";
	}
    }

    print <<EOF;
<tr><td colspan=4><hr>
<tr><td></td><td colspan=3>
<b>Reviewer 1: <select name=reviewer1-$sid onChange="gotoInWin(this)"> $reviewer_1_select_list </select>
</td></tr>
<tr><td></td><td colspan=3>
<b>Reviewer 2: <select name=reviewer2-$sid onChange="gotoInWin(this)"> $reviewer_2_select_list </select>
</td></tr>
<tr><td colspan=4><hr></td></tr>
EOF

    $go_prev = "";
    if ($prev_sid != -1) {
	$go_prev = "<input type=submit name=go_prev value=\"<-- View Previous Paper --\">";
	$go_prev .= "<input type=hidden name=prev value=$prev_sid>";
    }
    $go_next = "";
    if ($next_sid != -1) {
	$go_next = "<input type=submit name=go_next value=\"-- View Next Paper -->\">";
	$go_next .= "<input type=hidden name=next value=$next_sid>";
    }

print <<EOF;
</table>
<table width=100%><tr><td align=center>
    $go_prev &nbsp;&nbsp;&nbsp;&nbsp;
<input type=submit name=return value="-> Return to List <-">
 &nbsp;&nbsp;&nbsp;&nbsp;
$go_next
</td></tr>
<!--<tr><td align=center>
<input type=reset value="Reset to Initial Reviewers">
</td></tr>-->
</table>
Save changes to reviewers: <input type=checkbox name="save_reviewers" checked>
<hr>
EOF
}
$next_page = $prev_page = "&nbsp;";
if ($page != $min_page) {
    $prev_page = "<input type=submit name=prev_page value=\"<-- Previous Page --\">";
}
if ($page != $max_page) {
    $next_page = "<input type=submit name=next_page value=\"-- Next Page -->\">";
}

if ($fullpage) {
    $fullpage_width="";
    $fullpage_switch="";
    $fullpage_doc = "(Click on image to return to reviewer assignment)";
} else {
    $fullpage_width = "width=95%";
    $fullpage_switch = "&fullpage=yes";
    $fullpage_doc = "(Click on image to view expanded version)";
}

print <<EOF;
<table width=100%>
<tr>
    <td align=right>
$prev_page
    </td>
    <td align=center>
<center>
<i><b>Page $page of $max_page.</b></i><br>
<font size=-1>$fullpage_doc</font>
</center>
    </td>
    <td align=left>
$next_page
    </td>
</tr>
</table>

<hr>
<A href="view.cgi?$fullpage_switch&sid=${sid}&page=$page&range=$range&reviewer_n=$cgi_reviewer_n">
<img border=2 hspace=20 $fullpage_width
src="getPage.cgi?sid=${sid}&page=$page&lastMod=$last_mod" alt="Page 1"></a>
<table width=100%>
<tr>
    <td align=right>
$prev_page
    </td>
    <td align=center>
<center>
<i><b>Page $page of $max_page.</b></i><br>
<font size=-1>$fullpage_doc</font>
</center>
    </td>
    <td align=left>
$next_page
    </td>
</tr>
</table>
</form>
<hr width=100%>
<font size=2>
<i>Please contact
<a href="mailto:support\@cns.numedeon.com">support\@cns.numedeon.com</a>
if you have any questions regarding this Web page.</i>
</body>
</html>
EOF

exit 0;
