# -*- perl -*-
use strict;
use warnings;
use tests::tests;
our ($test);
my @output = read_text_file ("$test.output");
common_checks ("run", @output);
my %created;
my %rows;
foreach (@output) {
    if (/Created (worker-[abc]) tid=(\d+)/) {
        fail "Duplicate worker creation" if exists $created{$1};
        $created{$1} = $2;
    }
    if (/^\s*(\d+)\s+(worker-[abc])\s+(\d+)\s+(\d+)\s+(\d+)\s+DONE\s*$/) {
        my ($tid, $name, $priority, $ticks, $dispatches) = ($1,$2,$3,$4,$5);
        fail "Duplicate completed row" if exists $rows{$name};
        fail "Invalid completed counters" if $tid <= 0 || $priority != 31 || $dispatches < 1;
        $rows{$name} = $tid;
    }
}
fail "Expected three workers and three final rows" if keys(%created) != 3 || keys(%rows) != 3;
my %ids;
for my $name (qw(worker-a worker-b worker-c)) {
    fail "Created/completed worker mismatch" if !exists $created{$name} || !exists $rows{$name} || $created{$name} != $rows{$name};
    fail "Duplicate thread ID" if $ids{$created{$name}}++;
}
fail "Missing invariants or normal test completion" if !grep (/^\(cpu-monitor\) PASS$/, @output);
fail "Missing completion history accounting" if !grep (/Records: 3\/16; overwritten: 0/, @output);
pass;
