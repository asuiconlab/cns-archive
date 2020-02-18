#! /usr/bin/perl

use CGI;
use Mysql;

require 'utils.pl';

$dbname = "cns2000";

$qs = "SELECT rid,name,comments,keywords FROM reviewers";
$sth = &query($dbname, $qs) || &printerr("18");

@reviewers = ();
while (@reviewer_query = $sth->fetchrow()) {
    @reviewers = (@reviewers,@reviewer_query);
}

print <<EOF;
<html>
<head>
<title>CNS*2000 Reviewer List</title>
</head>
<body bgcolor=white>

<dl>
EOF

while(($rid,$name,$comments,$keywords,@reviewers) = @reviewers) {
	$comments = "(" . "$comments" . ")" if (length($comments) > 2);
	print <<EOF;

<dt><a name="$rid"><p><hr>
<font size=+1><b>$name</b></font>
<dd><i>$comments</i>
<p>
$keywords
<p>
</dd>
EOF
}

print <<EOF;
</dl>
</body>
</html>
EOF

exit 0;
