# -*- perl -*-
use strict;
use warnings;
use tests::tests;
check_expected ([<<'EOF']);
(monitor-overflow) begin
(monitor-overflow) PASS: newest 16 records retained, 3 oldest overwritten
(monitor-overflow) PASS: bounded and zero-capacity snapshots
(monitor-overflow) PASS
(monitor-overflow) end
EOF
pass;
