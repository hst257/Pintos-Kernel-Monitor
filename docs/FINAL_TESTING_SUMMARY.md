# Final testing summary

Finalization reruns occurred on 2026-10-22 in Ubuntu 24.04.1 WSL2.
PASS requires normal boot/test/shutdown and the relevant checker, not merely
a zero process status. No timeout or kernel panic occurred in these reruns.

| Test | Purpose | Expected result | Actual result / status | Evidence |
| --- | --- | --- | --- | --- |
| Baseline default demo | Original-kernel preservation | Normal alarm-single completion | PASS | `evidence/finalization/baseline-default.log` |
| Baseline --video | Concise real baseline boot | Same checks as default | PASS | `evidence/finalization/baseline-video.log` |
| Portable source setup | Compile, ELF/image checks, smoke test | Setup exit 0 and checker PASS | PASS | `evidence/finalization/setup-main.log`; `generated/person2/runs/setup-*/` |
| cpu-monitor | Independent CPU/dispatch counters and completed workers | Invariants and checker PASS | PASS; latest live samples 22/10/3 ticks, 7/42/2 dispatches | `evidence/finalization/person2-live.log` |
| monitor-overflow | Bounded retention | Newest 16 of 19, overwrite count 3 | PASS | Same live suite; full raw outputs under its printed generated run path |
| alarm-single | Original timer/thread behavior | Official checker PASS | PASS | Same live suite |
| alarm-simultaneous | Multiple-thread wakeup scheduling | Official checker PASS | PASS | Same live suite |
| alarm-zero | Zero-duration alarm behavior | Official checker PASS | PASS | Same live suite |
| Modified demo, default and --regressions | Reused runner and real modified boot | Checker PASS | PASS; final regression mode 5/5 | `evidence/finalization/modified-live.log`, `modified-regressions-final.log` |
| priority-fifo, original | Known upstream priority limitation | Known FAIL, recorded honestly | FAIL: No iterations found in output. | `evidence/finalization/priority-comparison/original.output`, `.result`, `.checker.log` |
| priority-fifo, modified | Detect a changed failure | Same known failure as original | Identical FAIL: No iterations found in output. | Corresponding `modified.*` files |
| Isolated source setup/demo/rerun | Archive-free reproduction | Build and supported suite PASS | PASS on the same WSL host | `evidence/finalization/isolated-*.log`, `portability-results.json` |

The supported five-test suite passed; the complete table does NOT say every
test passed. `priority-fifo` requires an unfinished upstream priority scheduler.
The project preserves that algorithm and documents the matched original failure.

## Reproduce supported tests live

```bash
bash setup_person2.sh
bash demo_person2.sh           # concise, all five supported tests LIVE
bash demo_person2.sh --full    # same tests, complete console output
bash demo_modified.sh --regressions
```

The setup force-builds with the verified flags. Demos do not rebuild.
For baseline verification on Person 1's preserved checkout:

```bash
bash demo_baseline.sh --video
```

Every portable live run saves `.output`, `.result`, `.checker.log`,
`commands.jsonl`, and `results.json` in the printed generated directory.
The priority comparison's exact commands/statuses are in
`evidence/finalization/priority-comparison/results.json`.
CPU values vary between runs; none is an expected constant or pass threshold.

## Preservation audit

Final SHA-256 checks found all 635 pre-existing source files and all 86 baseline/Phase 2 evidence files unchanged, with identical file sets. The baseline tag and `main` HEAD remained at their original revisions. Shell syntax, Python compilation, relative Markdown links, and `git diff --check` passed. The original README text is retained in full. Audit details are in `evidence/finalization/integrity-final.json`; generated outputs and local evidence are ignored, not deleted.
