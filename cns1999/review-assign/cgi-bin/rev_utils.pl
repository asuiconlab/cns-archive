#! /usr/bin/perl

sub process_reviewer_set {
    local($cgi) = @_;
    @keys = $cgi->param();
    foreach $k (@keys) {
	if ($k =~ /reviewer1-(\d+)/) {
	    $id = $1;

	    print STDERR "found reviewer1-$id\n";

	    # they come in pairs...
	    $val1 = $cgi->param(-name=>"reviewer1-$id");
	    $val2 = $cgi->param(-name=>"reviewer2-$id");

	    $qs = "SELECT reviewer_id FROM review_assign WHERE committee_member='$sql_reviewer_n' AND paper_id=$id";
	    $sth = &query($dbname, $qs) || &printerr("25");

	    # is there a record already there to change?
	    if ($sth->fetchrow()) { # yep!
		$qs = "UPDATE review_assign SET reviewer_id=$val1,reviewer_id_2=$val2 WHERE paper_id=$id AND committee_member='$sql_reviewer_n'";
		&query($dbname, $qs) || &printerr("26a");
	    } else {		# nope.
		$qs = "INSERT INTO review_assign (paper_id,reviewer_id, committee_member, reviewer_id_2) VALUES ($id, $val1, '$sql_reviewer_n', $val2)";
		&query($dbname, $qs) || &printerr("26a");
	    }
	}
    }
}

1;
