#!/usr/bin/perl

use Mysql;
require 'utils.pl';
use CGI;

$cgi = new CGI();

$mid = $cgi->param(-name=>'mid');
$password = $cgi->param(-name=>'password');

if (!defined($mid)) {
    print "Location: ../\n\n";
    exit 0;
}

if ($password ne "memanager") {
    print "Location: ../\n\n";
    exit 0;
}

$qs = "select rid,name,email,pwd from reviewers order by name";
$sth = &query($CNS_DB, $qs);

print <<EOF;
Content-type: text/html\n\n
<html>
<body bgcolor=white>
<form action=setup-review.cgi>
<input type=hidden name=rid value=$rid>
<input type=hidden name=password value="$password">
<table>
<tr>
<th>Name</th><th>Email</th><th>Password</th>
<th>Total Papers</th><th>Reviewed Papers</th><th>Incomplete Papers</th>
<tr><th colspan=6><hr></th></tr>
EOF

@rev=();
while(($y,$u,$v,$w)=$sth->fetchrow())
	{
	@rev=(@rev,$y,$u,$v,$w);
	}

while (($rid,$name,$email,$pwd,@rev) = @rev)
  {
  $qs = "SELECT count(rid) from po_form where rid=$rid AND ((q1>0) OR (q2>0) OR (q3>0) OR ((q4a='y') AND (q4b = NULL)) OR ((q5a='y') AND (q5b >0)))";
  $sth = &query($CNS_DB, $qs);

  ($n_started) = $sth->fetchrow();

  $qs = "SELECT count(rid) FROM po_form WHERE rid=$rid AND ((q1>0) AND (q2>0) AND (q3>0) AND (((q4a='y') AND (length(q4b) > 10)) OR q4a='n') AND (((q5a='y') AND (length(q5b) > 10)) OR q5a='n'))";
  $sth = &query($CNS_DB, $qs);

  ($n_done) = $sth->fetchrow();

  $qs = "SELECT paper_id FROM prog_review WHERE (reviewer1 = $rid OR reviewer2= $rid) order by paper_id";
  $sth = &query($CNS_DB, $qs);



  $n_todo = 0;
  $temp=-1;
  @papers=();
  while($x=$sth->fetchrow())
      {
      if ($x ne $temp)
      {$n_todo++;$temp=$x;@papers=(@papers,$x);}
      }

  $incomplete = $n_started - $n_done;

print <<EOF;
<tr>
<td>$name</td><td>$email</td><td>$pwd</td></td><td>$n_todo</td>
<td>$n_done</td><td>$incomplete</td>
EOF
}

print <<EOF;
</table>
</form>
</body>
</html>
EOF

exit 0;
