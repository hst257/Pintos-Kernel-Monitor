# Person 1 baseline video preparation

This is the baseline portion only. It is not the final eight-minute script.
Plan approximately 60-90 seconds for this portion within Person 1's four
minutes. Record only after Phase 2 implementation and tests are complete.

## What to show and execute

1. Introduce Pintos as a small educational x86 OS with C kernel code,
   accessible scheduler/timer routines, and built-in QEMU tests. Explain
   that the project adds per-thread monitoring later, while this section
   establishes the unmodified starting point.
2. In the Ubuntu WSL terminal:

   ```bash
   cd /home/harshit/OSGroup/OS-Pintos/pintos
   bash demo_baseline.sh
   ```

3. Point out the archived source revision
   `ab699959f0d3eae8e59d8507ae2474a638c3d1d3` and integrity check. The script
   labels the build and historical boot excerpts as ARCHIVED. Do not claim
   those displayed logs are a build executed during the recording.
4. When LIVE EXECUTION appears, explain that QEMU is now executing the
   preserved original kernel disk. It remains the original baseline even
   when the current working tree contains Phase 2 code.
5. Show `Boot complete.`, the five `alarm-single` wakeup products
   10/20/30/40/50, test completion, `Powering off...`, and the script PASS.
   Explain that raw QEMU exit 99 is its debug-exit success convention and
   that the run was not killed by a timeout.

The script does not edit source, change branches, install tools, or rebuild
anything. The preserved original disk is booted with temporary snapshot
writes, and new live output is saved separately in `evidence/demo-runs/`.

## Evidence files available on screen

- `evidence/baseline/build.log`: complete initial and compatibility builds.
- `boot.log`: complete successful original-kernel boot/test output.
- `git_info.txt`, `revision.txt`: revision, tag, remotes, and initial status.
- `environment.txt`, `commands.txt`: actual tool versions and executed commands.
- `artifact-verification.txt`, `alarm-single.result`, `SHA256SUMS`: binary,
  upstream checker, and archived-evidence verification.
- `boot_screenshot.png`: genuine QEMU VGA capture showing initialization and
  `Boot complete`; no manual screenshot is needed.
- `boot-default-attempt.log`: failed default-compiler boot retained for the
  report's challenges section. The resolved build uses command-line
  `-fno-pie -fno-pic`; source remains unmodified.

Full paths for the relative names above start with `evidence/baseline/`.
Only open detailed evidence if needed; the prepared script keeps this portion
short. Timing values may vary, so recognize completion and correct wakeup
order rather than reading a fixed tick total from a script.

## Kernel files to explain after Phase 2

Use the actual final diff and verified output when these sections are ready:

- `src/threads/thread.h`: per-thread metadata and future monitoring fields.
- `src/threads/thread.c`: accounting, dispatch, reporting, and lifetime handling.
- `src/devices/timer.c`: existing timer interrupt calls `thread_tick()`.
- `src/threads/switch.S`: context-switch background; no change is currently planned.
- `src/tests/threads/`: future workload, registry, and test checker.

## Reserved final sections

Person 1 modified-kernel demonstration: to be written after Phase 2 is
implemented and verified. Show the actual new features and output; do not
substitute the baseline's aggregate counters for the proposed functionality.

Person 2 testing demonstration: to be written after completed tests exist.
Prepare one continuous-take command sequence with no code edits, installation,
branch changes, or environment changes during recording. Allocate roughly
four minutes for methodology, workload results, challenges, and conclusions.
No Phase 2 demonstration script or final narration has been created yet.


# Phase 2 verified update

The earlier reserved sections can now use the completed Thread Monitor v1
implementation. This update is a demonstration plan, not final narration or
the Phase 3 report/script. Keep the total target near eight minutes, with
approximately four minutes for each presenter.

## Person 1: setup and implementation

Use `bash demo_baseline.sh` for the original kernel, then explain the actual
changes in `src/threads/thread.h` and `thread.c`: two 64-bit counters,
`thread_tick()` accounting, one dispatch increment per `schedule()` selection,
and the 16-entry copied completion ring in `thread_exit()`. Explain the
bootstrap main count, same-thread reselection, and reporting after safe
snapshots. `timer.c` and `switch.S` are background context and were not edited.
Show the genuine table with:

```bash
cd /home/harshit/OSGroup/OS-Pintos/pintos
bash demo_modified.sh
```

No build, installation, branch change, or code edit is needed during the
recording. State that ticks are samples, rather than exact execution time.
The initial verified run showed worker ticks 21/9/3 and dispatches 7/42/2;
recognize the real live values rather than expecting those exact numbers.

## Person 2: one continuous-take testing sequence

Run this single prepared command from the project root:

```bash
bash demo_modified.sh --regressions
```

It runs the real CPU-monitor workload, bounded-history test, alarm-single,
alarm-simultaneous scheduling regression, and alarm-zero. Each run checks its
actual Perl result, saves output under `evidence/demo-runs/`, and prints PASS
only after normal completion. The prepared sequence was executed successfully.

Explain what each invariant establishes: workers have unique created IDs,
per-thread dispatches, no charged ticks while semaphore-blocked, monotonic
counters, and exactly one completion row after each worker exits. The overflow
test retains the newest 16 of 19 records and checks bounded snapshots.

Mention the honest limitation: priority-fifo fails identically on both the
original and modified kernel because priority scheduling is unfinished in
the supplied distribution. It is excluded from the supported PASS sequence;
both actual outputs are in `evidence/modified/tests/`. Do not claim that all
Pintos priority/MLFQS assignment tests pass.

Conclude the testing portion with timer sampling limits, the fixed 16-record
capacity, and unchanged round-robin policy. Full implementation details,
results, and genuine screenshots are in `docs/KERNEL_MODIFICATION.md` and
`evidence/modified/`. The final narration and report remain for Phase 3.


# Phase 3 final recording update

Use the completed scripts in `VIDEO_PERSON1.md` and `VIDEO_PERSON2.md` for the
balanced four-minute sections. Person 1 runs `bash demo_baseline.sh --video`
and uses the listed source locations. Person 2 prepares his own clone with
`bash setup_person2.sh` before recording, then runs `bash demo_person2.sh`.
The portable demo uses the same live runner as the modified demo and needs no
legacy evidence archives. All five supported tests execute live; the known
priority-fifo failure remains explicitly documented. No kernel changes were
made during finalization. Publication and the second laptop's actual setup
verification remain manual prerequisites, not completed cross-laptop evidence.
