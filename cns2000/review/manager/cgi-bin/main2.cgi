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

$qs = "select paper_id from prog_review where approved ='y' AND user<>'Judy Macias' AND reviewer1<>(-2) AND reviewer2<>(-2) order by paper_id";
$sth = &query($CNS_DB, $qs);

print <<EOF;
Content-type: text/html\n\n
<html>
<body bgcolor=white>
<table>
<tr>
<th>Paper ID</th><th>Finished Reviews</th>
<tr><th colspan=2><hr></th></tr>
EOF
@rev=();
while(($id)=$sth->fetchrow())
	{
	@rev=(@rev,$id);
	}
$tid=0;

while (($id,@rev) = @rev)
  {
  if ($tid != $id) {
  $qs = "SELECT count(pid) from po_form where pid=$id AND ((q1>0) OR (q2>0) OR (q3>0) OR ((q4a='y') AND (q4b = NULL)) OR ((q5a='y') AND (q5b >0)))";
  $sth = &query($CNS_DB, $qs);

  ($nfin) = $sth->fetchrow();

 if ($nfin != 0) {
    print "<tr><td>$id</td><td>$nfin</td>";
   }
  else {print "<tr><th>$id</th><th>$nfin</th>";
     }
  $tid=$id;
  }
}

print <<EOF;
</table>
</body>
</html>
EOF

exit 0;
