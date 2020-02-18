#!/usr/bin/perl

package Query;

use Mysql;

my $SDB = '';
$DEF_DB = 'cns2000';

sub query
{
	my ($db,$qs) = @_;

	# print STDERR "query -------- $db $qs\n";
	$dbh ||= Mysql->Connect($SDB,$db); # ,$UNAME,$UPASS));
	unless ($dbh) {
		print STDERR "ERR Mysql Connect: $qs : $Mysql::db_errstr ";
		die "DB Error: $qs : $Mysql::db_errstr\n";
	}

	my $sth = $dbh->Query($qs);
	unless ($sth) {
		print STDERR "ERR Mysql Query: $qs : $Mysql::db_errstr ";
		die "DB Error: $qs : $Mysql::db_errstr\n";
	}
	return $sth;
}

sub q
{
	my ($qs,$db) = @_;
	$db ||= $DEF_DB;
	return query($db,$qs);
}

sub queryLine
{
	my ($db,$qs) = @_;
	my $sth = &query($db,$qs);
	return $sth->fetchrow;
}

sub qLine
{
	my ($qs,$db) = @_;
	$db ||= $DEF_DB;
	return queryLine($db,$qs);
}


sub sqlescape
{
	my ($s) = @_;
	$s =~ s/\\/\\\\/g;
	$s =~ s/'/\\'/g;
	$s =~ s/"/\\"/g;
	$s =~ s/\x0/\\0/g;
	return $s;
}

1;

