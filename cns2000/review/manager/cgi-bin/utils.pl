#! /usr/bin/perl

$CNS_DB = "cns2000";

sub printFile
{
	local($fn) = @_;
	open(INF,$fn) || die "Cannot open $fn\n";
	print "Content-type: text/html\n\n";

	while (<INF>) {
	    s/,,([^\s,]+),,/eval "$1"/eg;
	    print;
	}
	close(INF);
}

sub query
{
	local($dbname,$qs) = @_;
	# print STDERR "query -------- $dbname $qs\n" if (length($qs) < 1000);
	$dbh = Mysql->Connect("",$dbname) || die $Mysql::db_errstr;
	unless($sth = $dbh->Query($qs)) {
		$errStr = $Mysql::db_errstr;
		print STDERR "SQL Error: $errStr\n";
		return 0;
	}
	return $sth;
}

sub sqlescape()
{
	local($s) = @_;
	$s =~ s/\\/\\\\/g;
	$s =~ s/'/\\'/g;
	$s =~ s/"/\\"/g;
	$s =~ s/\x0/\\0/g;
	return $s;
}

sub printerr()
{
    local($errname) = @_;

    print <<EOF;
Content-type: text/html

<html>
<head>
</head>
<body bgcolor=white>
Error $errname - contact
<a href="mailto:judy\@bbb.caltech.edu">judy\@bbb.caltech.edu</a>
and report this!
</body>
</html>
EOF
    exit -1;
}

1;
