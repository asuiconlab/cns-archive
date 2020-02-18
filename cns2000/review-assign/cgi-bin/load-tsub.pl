#! /usr/bin/perl

use CGI;
use Mysql;

require 'utils.pl';

$dbname = "cns2000";

$header = <>;
chop $header;

@header_list = split(/\t/, $header);
print "header_list $#header_list\n";
$n = 0;
foreach $i (@header_list) {
#    print "$n \"$i\"\n";
    $n++;
}

#print @header_list;

$qs_1 = "insert into tsub (" . join(",", @header_list) . ") VALUES ";

while(<>) {
    chop;
    my @sqld = ();
    @ds = split(/\t/, $_, $#header_list + 1);

#    print "DS: $#ds\n";

    $n = 0;
    foreach $d (@ds) {
#	if (length($d) > 0) {
	    @sqld = (@sqld, &sqlescape($d));
	    $n++;
#	}
#	print "$n \"$d\"\n";
    }

    $line = join("','", @sqld);
    $qs = $qs_1 . "('$line')";
    print $qs, "\n";

    &query("cns2000", $qs);
}

exit 0;
