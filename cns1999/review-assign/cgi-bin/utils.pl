#! /usr/bin/perl

sub query
{
	local($dbname,$qs) = @_;
	print STDERR "query -------- $dbname $qs\n" if (length($qs) < 300);
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
<a href="mailto:support\@cns.numedeon.com">support\@cns.numedeon.com</a>
and report this!
</body>
</html>
EOF
    exit -1;
}

1;
