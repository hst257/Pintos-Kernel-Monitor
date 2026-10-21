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
