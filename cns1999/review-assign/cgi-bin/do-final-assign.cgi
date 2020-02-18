#! /usr/bin/perl

$CNS_DB = "cns99";

$qs = "SELECT sid FROM tsub WHERE cmdsuccess='y' AND locked='y'";
$sth = &query($CNS_DB, $qs) || die("DB error.");

@sids = ();
while($sid=$sth->fetchrow()) {
	@sids = (@sids, $sid);
}

$qs = "DELETE FROM review_assign WHERE committee_member='actual'";
&query($CNS_DB, $qs);

$qs = "SELECT paper_id, reviewer_id, committee_member, reviewer_id_2 FROM review_assign";

exit 0;
