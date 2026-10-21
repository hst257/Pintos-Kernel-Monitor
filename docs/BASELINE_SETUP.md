# Pintos baseline setup and Phase 2 assessment

## Scope and source revision

Phase 1 only: environment inspection, original-kernel build/boot evidence,
architecture review, and baseline video preparation. No monitoring feature
or kernel/build-source edit was made.

- Repository: `/home/harshit/OSGroup/OS-Pintos/pintos`, branch `main`.
- Source: JHU CS318 Pintos, derived from Stanford Pintos via PintosM, as
  described by the repository README and license.
- Exact revision: `ab699959f0d3eae8e59d8507ae2474a638c3d1d3`.
- `baseline-unmodified`, local `upstream/master`, and the upstream GitHub
  master ref all matched that revision when inspected.
- Remotes remain `origin=https://github.com/hst257/Pintos-Kernel-Monitor.git`
  and `upstream=https://github.com/jhu-cs318/pintos.git`.
- Initial working tree was clean. No tag, branch, commit, remote, staging,
  or history change was performed.

## OS selection

Pintos provides a small educational x86 kernel written mainly in C, with
short assembly routines for boot and context switching. Its scheduler,
timer interrupt handler, and thread structure are accessible enough for a
focused monitoring change. Built-in thread tests and QEMU support provide
repeatable demonstrations. It meets the requirement to use an OS other than
xv6 while keeping the project small enough for the available time.

## Environment and requirements

Verified on 2026-10-22 in Ubuntu 24.04.1 LTS, WSL2 on Windows, x86_64 host:

| Tool | Installed version used |
| --- | --- |
| GCC | 13.3.0 |
| GNU binutils / ld | 2.42 |
| GNU Make | 4.3 |
| Perl | 5.38.2 |
| Python | 3.12.3 |
| QEMU | 8.2.2, `qemu-system-i386` |

All dependencies, including `gcc-multilib` and `libc6-dev-i386`, were already
installed; no packages or administrative configuration were changed.
For another Ubuntu machine missing them, the package-manager commands are:

```bash
sudo apt update
sudo apt install build-essential gcc-multilib libc6-dev-i386 binutils perl python3 qemu-system-x86
```

These installation commands are setup instructions, not commands executed
in this run. Actual package versions are in `environment.txt`.

`src/Make.config` supports either an `i386-elf-` cross toolchain or native
GCC/binutils with 32-bit output. Its default C options include `-m32`,
`-msoft-float`, `-O0`, and automatic stack-protector disabling. The kernel
uses its own headers with `-nostdinc` and direct `ld -melf_i386` linking;
it does not link a hosted 32-bit libc. The multilib packages are already
present and simplify native 32-bit development, but a libc-linked user
program is not required for this threads-kernel baseline.

The bundled historical cross-toolchain script targets GCC 6.2.0 and
binutils 2.27. Those exact versions are not enforced by the Makefiles and
were not needed here. Make/Perl version minima are not specified locally;
the installed versions were verified. Perl core modules used by the launcher
and checker were sufficient. Python is used for evidence and demo helpers,
rather than to compile the kernel. Bochs-only helpers were not built because
this demonstration uses QEMU. The threads test defaults mention Bochs,
so select QEMU explicitly when using the launcher/test rules.

Keep the source on WSL's Linux filesystem and use Linux tools. Headless
QEMU uses software emulation here; Windows GUI integration and KVM are not
required. The explicit display settings avoid reliance on `DISPLAY`/WSLg.

## Build, failure, and compatibility adjustment

The first command was the supplied procedure:

```bash
cd /home/harshit/OSGroup/OS-Pintos/pintos
make -C src/threads -j2
```

It compiled successfully, but boot repeatedly reset during the first
formatted startup message and reached a 35-second safety timeout (status
124). This was a failed baseline run. Its complete output is retained in
`evidence/baseline/boot-default-attempt.log`, with status metadata and the
default-build binaries under `artifacts/default-build/`.

Compiler inspection showed that Ubuntu GCC enables PIE/PIC by default;
the generated objects contained position-independent code and GOT sections.
A full rebuild with only PIE/PIC disabled resolved the boot resets:

```bash
make -C src/threads -B -j2 \
  CFLAGS='-m32 -g -msoft-float -O0 -fno-stack-protector -fno-pie -fno-pic'
```

`-B` forces all objects to use the same flags without a destructive clean.
This command changed no Makefile or source. The final build status was 0.
Use these flags again for future clean/reproducible builds; Make does not
normally detect changes in command-line compiler flags by itself.

The complete initial and compatibility build outputs are in `build.log`.
`artifact-verification.txt` records `file` and `readelf` checks: `kernel.bin`
is a static ELF32 Intel 80386 executable, and `loader.bin` is a 512-byte
boot sector. The verified kernel entry point is recorded in that file.

Warnings included nonzero frame-address use in debug backtraces,
nonnull-argument comparisons, possible test-name truncation, loader RWX
metadata, and missing GNU-stack assembly metadata. They were not errors;
the chosen baseline test and shutdown completed successfully. That result
does not certify all unimplemented Pintos assignment tests.

## Baseline boot and evidence

The successful launcher command, run from `src/threads/build`, was:

```bash
timeout --signal=TERM --kill-after=5s 20s \
  /home/harshit/OSGroup/OS-Pintos/pintos/src/utils/pintos \
  --qemu --no-vga -- -q run alarm-single
```

The original launcher generated the QEMU command recorded at the beginning
of `boot.log`, including `-device isa-debug-exit`, 4 MB RAM, no network,
and headless output. It returned 0 after normal shutdown. Internally,
Pintos writes `0x31` to the debug-exit port, producing raw QEMU status 99;
the original launcher recognizes that status as success. A timeout is never
accepted as success. The launcher itself can return 0 for some timeouts,
so output completion checks are necessary as well as status checks.

Actual observed output excerpt:

```text
Pintos booting with 3,968 kB RAM...
Boot complete.
(alarm-single) thread 0: duration=10, iteration=1, product=10
(alarm-single) thread 1: duration=20, iteration=1, product=20
(alarm-single) thread 2: duration=30, iteration=1, product=30
(alarm-single) thread 3: duration=40, iteration=1, product=40
(alarm-single) thread 4: duration=50, iteration=1, product=50
(alarm-single) end
Execution of 'alarm-single' complete.
Timer: 271 ticks
Thread: 0 idle ticks, 271 kernel ticks, 0 user ticks
Powering off...
```

The upstream `alarm-single.ck` checker also returned PASS. Timing and
calibration values can vary between runs. The test exercises five kernel
threads and timer-driven scheduling; it is not evidence of new monitoring.

Preserved under `evidence/baseline/`:

- Required files: `build.log`, `boot.log`, `git_info.txt`, `environment.txt`,
  and `commands.txt` (actual primary build/boot/artifact/check commands and
  exit statuses).
- Original revision and source hashes: `revision.txt`, `source_sha256.json`.
- Artifact checks and successful boot metadata: `artifact-verification.txt`,
  `boot_status.json`, `alarm-single.output`, `alarm-single.result`,
  `test-check.log`.
- Failed first-run evidence: `boot-default-attempt.log`,
  `boot-default-status.json`, and `artifacts/default-build/`.
- Verified preserved artifacts: `artifacts/kernel.bin`, `kernel.o`,
  `kernel.sym`, `loader.bin`, and `baseline-alarm-single.dsk`.
- Genuine screenshot: `boot_screenshot.png`, captured through QEMU's VGA
  framebuffer after `Boot complete`, with its own complete run log.
- `SHA256SUMS`: integrity checks for the archived evidence/artifacts.

The screenshot is a lossless conversion of QEMU's screendump, with no
reconstructed text or compositing. No manual screenshot is required.

One disk-preparation command initially omitted the required `--` separator
for `pintos-set-cmdline`; it printed usage and returned 1. The corrected
command is recorded, and the final disk was verified by live execution.
This was a command syntax correction, not a source compatibility patch.

## Repeatable original-kernel demonstration

From the project root:

```bash
bash demo_baseline.sh --archive   # display archived evidence only
bash demo_baseline.sh            # archived evidence, then a real live boot
```

The script labels archived output, verifies SHA-256 hashes, and runs the
preserved baseline disk using QEMU's `-snapshot` option. It never rebuilds
or boots the working-tree kernel, changes branches, or overwrites baseline
logs. Fresh live output goes to `evidence/demo-runs/`. It requires both
normal shutdown status and expected test output, and fails on panic,
missing markers, unexpected wakeups, or timeout.

This frozen disk is the simplest baseline demonstration after Phase 2:
no separate checkout is needed. For a later source rebuild, use a separate
checkout/worktree at the recorded revision through a deliberate manual
Git operation, or first verify the current `src` hashes match the manifest.
Do not rebuild a modified working tree and call it the original baseline.

## Kernel architecture and existing functionality

| File | Functions/structures and role |
| --- | --- |
| `src/threads/thread.h` | `struct thread`, TID, name, priority, state, saved stack, and list links. A thread shares its 4 KB page with its kernel stack; keep additions small and leave `magic` as the stack-overflow sentinel. |
| `src/threads/thread.c` | `thread_create()` allocates the page and stack frames; `init_thread()` initializes metadata; `thread_unblock()` enqueues ready threads. |
| Same file | `schedule()` selects a thread through `next_thread_to_run()`; FIFO ready-list selection implements round robin. `thread_schedule_tail()` marks running, resets the slice counter, and frees the previous dying thread. |
| `src/threads/switch.S`, `switch.h` | `switch_threads()` saves registers/stack and restores the next stack; `switch_entry()` starts a new thread. `thread_stack_ofs` is calculated from the C structure. No assembly modification is needed for monitoring fields. |
| `src/devices/timer.c`, `timer.h` | `timer_init()` registers IRQ vector 0x20 at 100 Hz; `timer_interrupt()` increments global ticks and calls `thread_tick()`. `timer_ticks()` reads a 64-bit value with interrupts disabled. |
| `src/threads/interrupt.c` | Dispatches interrupts and handles `intr_yield_on_return()`, allowing preemption after an interrupt rather than an unsafe direct scheduler call from the timer handler. |
| `src/threads/thread.c` | `thread_tick()` already increments global idle/kernel/user tick totals and requests preemption after four ticks. `thread_ticks` is only the current time-slice counter, reset on scheduling. |
| Same file | `thread_exit()` removes the thread from `all_list` and marks it dying; its page is freed later in `thread_schedule_tail()`. `thread_foreach()` visits only live threads with interrupts off. |
| `src/lib/kernel/console.c`, `src/lib/stdio.c` | Kernel `printf()` formatting and synchronized console output. Print reports in a safe thread context. |
| `src/devices/shutdown.c` | Calls `timer_print_stats()` and `thread_print_stats()` before power-off; current reports contain aggregate totals only. |
| `src/threads/init.c`, `src/tests/threads/tests.c` | Startup, command-line actions, and built-in test dispatch. A new workload can use this test registration path in Phase 2. |

Priorities are stored but actual priority scheduling is not implemented in
this distribution. Nice/recent-CPU/load-average/MLFQS interfaces are stubs.
`timer_sleep()` repeatedly yields rather than truly blocking, so it must not
be described as an I/O-blocked workload. There are no per-thread lifetime
tick counters, dispatch counts, completed-thread records, or statistics table.

## Phase 2 recommendation, not implemented

Keep the round-robin scheduling policy unchanged and add:

1. Per-thread 64-bit lifetime tick and dispatch counters. Initialize them
   in `init_thread()`; count each timer sample in `thread_tick()`. Define a
   dispatch as each scheduler selection, including selecting the same thread
   again; count the bootstrapped main thread's first dispatch explicitly.
2. A report with TID, copied name, priority, state, sampled CPU ticks, and
   dispatch count. Snapshot counters with interrupts disabled briefly, then
   restore interrupts before formatting/printing. Label idle separately.
3. A small bounded completed-thread record buffer, filled in `thread_exit()`
   before removal/freeing, with an explicit overflow indication. This avoids
   stale pointers and lets the demo report workers after they finish.
4. One registered kernel test with CPU-heavy, yield-heavy, and genuinely
   semaphore-blocked workers. Use gates/completion semaphores for repeatable
   reporting and enough work to span many 10 ms timer samples.

Expected files: `src/threads/thread.h`, `thread.c`, new
`src/tests/threads/cpu-monitor.c`, its checker, and the existing test registry
`tests.c`, `tests.h`, and `Make.tests`. The existing timer-to-thread hook is
sufficient; `timer.c`, `switch.S`, scheduler policy, and user syscalls need
not change. Estimated scope: a few hours, including tests and explanation.

Tests should cover initialization, monotonic counters, increasing dispatch
counts on yielding, no tick growth while a worker is semaphore-blocked,
completed-record retention, output bounds, and the original baseline test.
Compare qualitative workload differences over repeated runs rather than
requiring exact tick counts or ratios under QEMU.

Risks: 64-bit reads can tear on 32-bit x86; interrupt context cannot block;
large reports can overflow the shared kernel stack; dying thread pages are
freed; short jobs can receive zero timer samples; and sampling attributes
interrupt overhead to the interrupted thread. Define tick-derived CPU time
as an approximation, not exact nanoseconds. Do not print or allocate from
`thread_tick()` or the middle of `schedule()`. A bounded static report buffer
or caller-provided storage avoids large local arrays. Exposing the existing
global statistics alone would not constitute this proposed new feature.

## Learning outcomes and integrity

The baseline demonstrates the boot-loader/kernel boundary, 32-bit build
requirements, interrupt initialization, time-slice preemption, thread life
cycles, test oracles, and evidence integrity. It also shows why successful
compilation alone does not establish a working OS.

Every tracked file under `src/` was hashed before building and compared
afterward. Tracked kernel, test, utility, and build files remain unchanged.
Only documentation, evidence, the baseline demonstration script, and normal
ignored build outputs were created. Phase 1 ends here; Phase 2 requires
explicit approval.

Validation of the prepared demonstration: `bash -n demo_baseline.sh`,
`bash demo_baseline.sh --archive`, and `bash demo_baseline.sh` all returned 0.
The live run completed the expected test with raw QEMU status 99. Validation
transcripts are `evidence/demo-archive-validation.log` and
`evidence/demo-live-validation.log`; original baseline evidence was unchanged.
