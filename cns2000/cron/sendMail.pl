#!/usr/bin/perl

# For all mail in the queue not already sent, send it here.
# This serves two purposes:  we get a record of every mail sent,
# and we let the cgi script run and finish with no danger of
# timeouts.

use Query;

open(LOG,">>sendMail.log");
print LOG "---- starting at " , scalar(localtime) , "\n";

my $tm = time();

$sth = Query::q("SELECT id FROM mailq WHERE sent=0");
print LOG $sth->numrows , " mails to send\n";
while (@row = $sth->fetchrow) {
	my ($id) = @row;

	my $qs = "SELECT fromAddr,body FROM mailq WHERE id=$id";
	my ($fromAddr,$body) = Query::qLine($qs);

	if (open (MAIL,"| /var/qmail/bin/qmail-inject -f${fromAddr}")) {
		print MAIL $body;
		print LOG "($id) sent\n";
		Query::q("UPDATE mailq SET sent=$tm WHERE id=$id");
	} else {
		print LOG "($id) Cannot pipe to mail: $!\n";
	}

}

close(LOG);
