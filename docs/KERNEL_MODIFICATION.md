# Pintos per-thread CPU monitoring and scheduling analytics

## Scope and architecture

Phase 2 adds instrumentation to the real Pintos kernel, with no change to
round-robin selection, priorities, timer frequency, context-switch assembly,
or the existing aggregate counters. Source changes are uncommitted on `main`.
The build starts from Phase 1 commit `3da490e8f5f85f37a8b44422b6ec13e0b7c0f89b`;
the original baseline tag remains at
`ab699959f0d3eae8e59d8507ae2474a638c3d1d3`.

```text
timer_interrupt() -> thread_tick() -> current thread's cpu_ticks++
schedule()       -> selected thread's dispatches++
thread_exit()    -> copy final record into bounded history
                    -> original removal/switch/free path
controlled test  -> interrupt-safe copied snapshot
                    -> sort and print with interrupts enabled
```

## Data structures and counter initialization

`struct thread` gains two `uint64_t` fields: `cpu_ticks` counts lifetime
timer samples; `dispatches` counts scheduler selections. `init_thread()`
sets both to zero before the thread becomes runnable. `thread_init()` sets
the already executing main thread's bootstrap dispatch count to one.
The idle thread has the same counters and accounting rule as every other
thread, although it normally never exits and therefore has no completed row.

The threads-only build's structure grows from 52 to 68 bytes. `magic` remains
the final member, and an assertion enforces a size below 1 KB. The saved-stack
field is unchanged; `thread_stack_ofs` is still computed by C. Each thread
still uses one 4 KB page for its structure and kernel stack.

A `thread_monitor_record` contains a TID, copied 16-byte name, final priority,
64-bit tick and dispatch values, and status. Records contain no thread-page
pointers. Each is 44 bytes; the 16-record static ring occupies 704 bytes.
The ring tracks its next slot, retained count, and overwrite count.

## CPU accounting and scheduling analytics

The existing 100 Hz timer handler already calls `thread_tick()`. Incrementing
the interrupted thread's counter there attributes one sample to that thread
and preserves the existing idle/kernel/user totals and four-tick preemption.
No new interrupt handler or timer configuration was introduced.

A dispatch means one selection by `schedule()`, including selecting the
currently running thread again. The selected thread is incremented once
before the existing `cur != next` switch check. Thus dispatches count more
than actual context switches and are distinct from ticks, creations, and
yields. The bootstrap main-thread count handles execution before the first
scheduler selection.

Ticks approximate CPU consumption at 10 ms intervals. They are not exact
instruction counts, nanoseconds, or wall time; interrupt overhead can be
attributed to the interrupted thread. Short jobs can have zero samples.
The tests never require fixed tick counts or different counts for every job.

## Completion history and reporting

`thread_exit()` disables interrupts and calls `monitor_complete()` before
removing the thread from `all_list`, marking it dying, and following the
original switch/free path. The helper copies metadata and counters, marking
the copied status `THREAD_DYING` (displayed as DONE). It neither allocates,
blocks, nor prints. After 16 completions the oldest record is replaced and
the overwrite count increases. Live threads are not part of this history.

`thread_monitor_current()` snapshots the caller. `thread_monitor_snapshot()`
copies the newest records that fit the caller's capacity, in completion
order, and can return the overwrite count. Capacity zero is valid. Both
briefly exclude interrupts, making multiword reads safe on this single-CPU,
32-bit Pintos configuration. Snapshot storage belongs to the caller.

`thread_monitor_report()` requires ordinary thread context with interrupts
on. It allocates a fixed maximum of 704 bytes, copies the history, restores
interrupts, sorts by TID, prints a table, and frees the buffer. It returns
false on allocation failure. This avoids a large stack array, shared static
report scratch space, and printing during scheduler/interrupt critical paths.
Normal Pintos execution emits no extra monitoring table unless explicitly
requested. Existing shutdown statistics remain unchanged.

## Controlled workloads and invariants

The registered `cpu-monitor` test creates three default-priority threads:

| Thread | Calibrated busy work | Explicit yields |
| --- | --- | --- |
| worker-a | 8 units of 25 ms | 0 |
| worker-b | 4 units of 25 ms | 10 per unit |
| worker-c | 1 unit of 25 ms | 0 |

All initially block on semaphore gates while the controller performs work.
Snapshots immediately before blocking and after resumption, with interrupts
disabled on that thread around the boundary, verify that no CPU ticks were
charged while blocked. This uses genuine semaphore blocking, rather than
the original `timer_sleep()` yield loop.

Workers verify initialized identity/dispatches and monotonic counters.
The yield-heavy worker checks dispatch growth across every yield return,
including reselection after other workers finish. The controller checks
unique IDs, matching copied names/priorities, DONE status, final counters
at least as large as the worker's last sample, and exactly one record per
created worker.

A completion semaphore alone does not prove `thread_exit()` has run, so the
controller also waits for each completion record with a bounded deadline.
When it resumes after that exit, the original scheduler tail has freed the
worker page. Static test arrays avoid oversized kernel-stack allocations.

A separate `monitor-overflow` test creates 19 short-lived workers and checks
that only the newest 16 remain, exactly three were overwritten, no TID is
duplicated, and one-entry/zero-capacity snapshots work. Both new tests have
Perl checkers integrated through Pintos's existing test framework.

## Exact source changes

| File | Changes |
| --- | --- |
| `src/threads/thread.h` | Adds counters, copied record type, capacity, and three monitoring API declarations. |
| `src/threads/thread.c` | Updates `thread_init()`, `init_thread()`, `thread_tick()`, `schedule()`, and `thread_exit()`; adds `monitor_copy()`, `monitor_complete()`, snapshot APIs, and reporting. |
| `src/tests/threads/cpu-monitor.c` (new) | Implements `test_cpu_monitor()` and `test_monitor_overflow()`, workers, and lifecycle checks. |
| `src/tests/threads/cpu-monitor.ck` (new) | Validates actual creation IDs against the three completed report rows and test success. |
| `src/tests/threads/monitor-overflow.ck` (new) | Checks normal completion and the bounded-history test result. |
| `src/tests/threads/tests.c`, `tests.h`, `Make.tests` | Register and compile the two tests. |

Non-kernel additions are `demo_modified.sh`, this document, and
`evidence/modified/`. The video plan gains a Phase 2 update. Earlier source,
Phase 1 setup notes, the baseline demo script, tag, and baseline evidence
remain preserved. No new dependency was installed.

## Build and actual results

Run from `/home/harshit/OSGroup/OS-Pintos/pintos`:

```bash
make -C src/threads -B -j2 \
  CFLAGS='-m32 -g -msoft-float -O0 -fno-stack-protector -fno-pie -fno-pic'
```

The build returned 0 and generated `src/threads/build/kernel.bin`, verified
as a static ELF32 Intel 80386 executable. Existing compiler/linker warnings
remain recorded in `build.log` and `build-info.txt`; no new monitoring-source
warnings or build errors were observed.

Actual first monitoring run:

```text
TID   THREAD NAME      PRIORITY CPU TICKS    DISPATCHES   STATUS
3     worker-a         31       21           7            DONE
4     worker-b         31       9            42           DONE
5     worker-c         31       3            2            DONE
Records: 3/16; overwritten: 0
(cpu-monitor) PASS
```

The debugger-assisted screenshot run showed 20/10/3 ticks with the same
7/42/2 dispatch counts. These are different genuine runs; sampling variation
is expected and is not treated as failure. The guest resumed after capture,
passed its checks, and shut down normally.

| Test | Actual checker result |
| --- | --- |
| cpu-monitor | PASS |
| monitor-overflow | PASS |
| alarm-single | PASS |
| alarm-simultaneous (multiple-thread scheduling/wakeup regression) | PASS |
| alarm-zero | PASS |
| priority-fifo, modified kernel | FAIL: No iterations found in output. |
| priority-fifo, archived original kernel | Identical FAIL: No iterations found in output. |

All these runs booted and shut down without timeout or panic. `priority-fifo`
is an existing unsupported priority-scheduler case, not a monitoring
regression: the original kernel only stores priority values and does not
implement priority scheduling. It was tested and preserved rather than
silently fixed or reported as passing. The supported scheduling regression,
`alarm-simultaneous`, passed its official output checker.

The modified demonstration and regression mode were both executed and
passed. The original `demo_baseline.sh` was rerun and still passed, booting
its unchanged original disk. New monitoring runs take roughly a second;
the prepared supported regression sequence completes within a few seconds
plus the original alarm test's sleep interval. Calibration/host load varies.

## Demonstration and preserved evidence

```bash
cd /home/harshit/OSGroup/OS-Pintos/pintos
bash demo_baseline.sh
bash demo_modified.sh
# Person 2 can run this single continuous-take command:
bash demo_modified.sh --regressions
```

`demo_modified.sh` verifies archived modified artifacts/checkers, prints the
build identity and source-manifest hash, then performs real QEMU execution.
It uses prepared test disks and snapshot writes, with no build, source edit,
branch change, or installation. It checks normal shutdown and the test's
actual Perl result. Raw QEMU status 99 is the expected debug-exit convention;
status 124 or missing completion markers fail the script. Every invocation
saves complete outputs, check results, exact QEMU commands, and statuses in
a new `evidence/demo-runs/modified-*` directory.

The modified build is identified as Thread Monitor v1 plus the Phase 1 base
commit and SHA-256 source manifest, rather than falsely claiming that the
uncommitted implementation has its own Git revision.

`evidence/modified/` contains:

- `build.log`, `build-info.txt`, `commands.txt`, `source_sha256.json`.
- `tests/*.output`, `*.result`, `*.checker.log`, and `test-results.json`,
  including the original/modified priority-fifo comparison.
- `artifacts/`: matching kernel/loader, debug symbols, prepared disks,
  copied checkers and their support modules, version metadata, and checksums.
- `demo-default-validation.log`, `demo-validation.log`, and
  `baseline-demo-recheck.log`.
- `monitor_screenshot.png` and the original PPM framebuffer dump, with guest
  and debugger transcripts. No screenshot content was reconstructed.
- `baseline-before.json` and final integrity records proving that no Phase 1
  baseline file changed.

## Challenges and safety review

The initial build and monitoring tests passed. A priority regression probe
failed and was confirmed identical on the original kernel; no scheduling
policy change was made to satisfy an unrelated unfinished assignment.

The first screenshot attempt used Python `splitlines()` to compute a GDB
line number. Form-feed separators in the original source caused a mismatch,
so no breakpoint was set and no screenshot was captured. That attempt's
logs remain available. Counting newline bytes fixed the capture without
changing source; the successful screenshot pauses after the table prints,
then resumes to normal completion. GDB reports the remote connection closing
when QEMU exits; the guest's raw status was the expected 99.

Instrumentation updates and snapshots exclude interrupts under Pintos's
uniprocessor model. There is no allocation, console output, blocking lock,
or recursive scheduler call in the timer, dispatch, or completion path.
The reporting allocation is fixed-size and outside those paths. Existing
timer, context-switch, synchronization, priority, and aggregate-statistic
source code is unchanged.

Limitations: only 16 completed records are retained, active-thread tables
are omitted, names are limited to the existing 15 visible characters, and
counters reset each boot. No SMP safety is claimed. The 64-bit counters
assume no wraparound during a run (at 100 Hz, tick wrap would take billions
of years). Timer sampling and the extra counter/copy instructions introduce
small overhead; this project makes no benchmark claim about its magnitude.
A full priority/MLFQS implementation and the complete Pintos assignment suite
are outside scope.

## Learning outcomes

The implementation demonstrates how timer interrupts account for execution,
how scheduler decisions differ from actual switches, why thread destruction
requires copied diagnostic data, how to read multiword counters safely on
32-bit hardware, and how bounded reporting can preserve kernel behavior.
Phase 2 stops here; the final report and final video script belong to Phase 3.
