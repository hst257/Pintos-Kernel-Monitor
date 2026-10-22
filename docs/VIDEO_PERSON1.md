# Person 1 video: setup, original kernel, and implementation

Target: approximately four minutes, about half the combined video. Bracketed
names are placeholders. Practice at a natural pace; pause briefly for the real
boot and source navigation. This is final narration based on completed work.

## Before recording

- Fill in your actual name; read the final report and implementation notes.
- In the original Ubuntu checkout, practice `bash demo_baseline.sh --video`.
- Confirm preserved baseline checksums and the demo PASS. Do not record a failed
  rehearsal as successful execution.
- Open the two kernel files in VS Code if already available, or use terminal
  `sed` commands below. No extension/IDE installation is required.
- Maximize the terminal, choose a readable font, test microphone/audio, and
  close distracting windows. Build/debug beforehand, not during recording.
- Keep the original baseline revision visible and distinguish archived build
  evidence from the live boot.

Recommended initial terminal location:

```bash
cd ~/OSGroup/OS-Pintos/pintos
```

That is the original laptop's existing project location. If your checkout is
elsewhere, change to its actual root; the script itself has no fixed path.

Optional VS Code navigation, before recording:

```bash
code -g src/threads/thread.h:101
code -g src/threads/thread.c:135
```

Without VS Code, use these short source views when indicated:

```bash
sed -n '101,133p' src/threads/thread.h
sed -n '132,155p' src/threads/thread.c
sed -n '571,585p' src/threads/thread.c
sed -n '304,312p' src/threads/thread.c
sed -n '619,662p' src/threads/thread.c
```

## Recording: 0:00-0:40 — introduction and scope

Screen: project README title and features, then terminal.

> Hello, I am [Person 1 name]. Our project is Pintos Kernel: Per-Thread CPU Monitoring and Scheduling Analytics. We used Pintos, an educational operating system, and added instrumentation inside its actual kernel. We did not create Pintos itself. Our work records CPU samples and scheduler selections for individual threads, preserves completed results, and prints a checked statistics table. I will explain the original baseline and implementation. My teammate will demonstrate the workload, verification, and limitations on his own prepared laptop.

## 0:40-1:10 — selection and environment

Screen: README environment/build section. Do not execute a rebuild.

> We chose Pintos because its C kernel is small enough to study, while still providing real threads, timer interrupts, synchronization, and context switching. Our development environment is Ubuntu 24.04 under WSL2 with GCC and QEMU. This older kernel needed explicit non-PIE compiler flags on our Ubuntu toolchain. We kept that environment adjustment in the build command rather than changing the original kernel source to make it boot.

## 1:10-1:50 — genuine original baseline

Execute:

```bash
bash demo_baseline.sh --video
```

Screen: original revision, archived compatibility-build success, then LIVE boot,
`Boot complete.`, five wakeup products, normal shutdown, final PASS.

> Before adding features, we compiled and booted the unmodified kernel at the baseline revision shown here. The build information at the top is archived evidence, not a rebuild happening now. The QEMU execution below it is live and uses the preserved original disk. It initializes the kernel, runs alarm-single, and shuts down normally. The script checks the expected wakeups and completion messages. Raw status 99 is the configured QEMU debug-exit convention; a timeout would fail, even if some boot text had appeared.

## 1:50-2:35 — fields and CPU accounting

Screen: `thread.h` around lines 101-133, then `thread_tick()` around 135.

> The first kernel change adds two 64-bit fields to the thread structure. One stores lifetime CPU ticks, and the other stores dispatches. New threads start at zero, while the already running main thread gets one bootstrap dispatch. The structure is now 68 bytes in this build and still shares a four-kilobyte page with its stack. For CPU accounting, we extend the existing thread_tick function. Every timer interrupt adds one sample to the thread that was interrupted. We preserve the original global statistics and timer frequency. These are sampled execution observations, not exact instruction counts or wall-clock timings.

## 2:35-3:05 — dispatch definition

Screen: `schedule()` around lines 571-584.

> Here, the scheduler has already chosen the next thread. We increment its dispatch counter once before the existing switch condition. A dispatch means a scheduler selection, including selecting the same thread again. That is different from an actual switch between two threads. A yielding worker can therefore have many dispatches without consuming the most CPU samples. We have not changed which ready thread is selected, its priority, or the round-robin scheduling policy.

## 3:05-3:50 — completion history and safe reporting

Screen: `thread_exit()` and `monitor_complete()`/snapshot functions. Point to the
16-record capacity and copied fields; do not edit code.

> Completed thread pages are eventually freed, so keeping a pointer to them would be unsafe. Our exit hook first copies the final identity, name, priority, counters, and completed status into a fixed ring. It retains the latest sixteen records and counts overwrites. The snapshot routines briefly disable interrupts so a 64-bit value cannot be read halfway through an update on this 32-bit target. Reporting then sorts and prints copied data with interrupts enabled. There is no printing, allocation, or blocking added to the timer and scheduler instrumentation. The completed table can remain visible after the worker itself has been destroyed.

## 3:50-4:00 — transition

Screen: README demo commands or the implementation architecture diagram.

> That is the kernel instrumentation. My teammate will now show how we build the modified system from source, run different workloads, and check both the statistics and existing behavior.

## Output highlights and troubleshooting

The baseline must show actual initialization, completed alarm-single execution,
and normal shutdown. Never replace a failed run with narration claiming PASS.
If an archive is missing or an integrity check fails, stop recording and resolve
it from the preserved evidence before retrying. Do not alter checksums to bypass
an unexplained mismatch. If `code` is unavailable, use the prepared `sed` views.
The report's code locations are exact for the Phase 2 source preserved in Phase 3.

Final checklist: approximately four minutes; clear attribution; archived/live
labels explained; no live install/build/edit; both counters defined; lifecycle
and snapshot safety covered; clear handoff to Person 2.
