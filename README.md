# Pintos Kernel — Per-Thread CPU Monitoring and Scheduling Analytics

A university OS project that instruments the **existing JHU/Stanford Pintos
kernel**. The team added per-thread monitoring; it did not create Pintos or
replace its scheduler. See [upstream](https://github.com/jhu-cs318/pintos),
[src/LICENSE](src/LICENSE), and retained attribution below.

## Features and architecture

- 64-bit lifetime CPU timer samples per thread, recorded by `thread_tick()`.
- 64-bit scheduler selections per thread, including same-thread reselection.
- Latest 16 copied completed-thread records, retained after thread destruction.
- Interrupt-safe snapshots and a completed-thread table printed in safe context.
- Three-worker workload, a history-overflow test, and selected existing regressions.

```text
Timer -> thread_tick -> per-thread CPU samples
Scheduler -> selected thread's dispatch counter
Thread exit -> bounded copied history -> safe snapshot/report -> QEMU console
```

Round-robin selection, priorities, timer frequency, and context-switch assembly
are unchanged. Original baseline: `baseline-unmodified` at
`ab699959f0d3eae8e59d8507ae2474a638c3d1d3`. Phase 2 source commit: `476d3e1`.

## Person 2: clone, build from source, demonstrate

Validated target: x86_64 Ubuntu 24.04 under WSL2. Windows/first-launch details
are in [PERSON2_SETUP.md](docs/PERSON2_SETUP.md). Inside Ubuntu:

```bash
sudo apt update
sudo apt install git build-essential binutils gcc-multilib perl python3 qemu-system-x86
git clone https://github.com/hst257/Pintos-Kernel-Monitor.git
cd Pintos-Kernel-Monitor
bash setup_person2.sh
bash demo_person2.sh
```

Phase 3 must be committed/pushed before a clone contains its new scripts.
Setup never installs packages automatically. It compiles current source,
validates ELF32 output, prepares images, and smoke-tests the real guest.
It needs **neither evidence folder nor the developer's archived binaries**.
Run setup after source updates. Logs/artifacts are generated locally under
`generated/person2/` and are not committed. Setup reruns preserve prior runs.

The verified build command is:

```bash
make -C src/threads -B -j2 \
  CFLAGS='-m32 -g -msoft-float -O0 -fno-stack-protector -fno-pie -fno-pic'
```

Use the setup wrapper to prepare the demo images as well as build the kernel.
A recording requires no rebuild:

```bash
bash demo_person2.sh          # concise, five supported tests LIVE
bash demo_person2.sh --full   # full console output for diagnosis
```

## Person 1: preserved original baseline and source walkthrough

On the original development checkout with intact baseline evidence:

```bash
bash demo_baseline.sh --video
bash demo_modified.sh
```

The baseline labels its archived build evidence, then boots the original disk
LIVE. Default `bash demo_baseline.sh` and `--archive` remain available.
The modified demo reuses the common runner and uses source-built local artifacts
when setup exists; otherwise it can use the original laptop's Phase 2 archive.
A missing archive is resolved with source setup, not a manual binary transfer.

## Tests and results

The portable demo runs cpu-monitor, monitor-overflow, alarm-single,
alarm-simultaneous, and alarm-zero, requiring real normal shutdown and checker
PASS. Example final live samples were 22/10/3 ticks and 7/42/2 dispatches;
these values vary and are not test constants. Complete output and command/status
records are saved for every invocation.

**Known failure:** priority-fifo fails with “No iterations found in output”
on both the original and modified kernels. Priority scheduling is unfinished
upstream. We do not claim that all Pintos priority/MLFQS tests pass.
See [final testing summary](docs/FINAL_TESTING_SUMMARY.md).

## Limitations and portability status

CPU ticks are coarse samples, not exact wall time or instructions. History is
bounded to 16 completed records; counters reset at boot; synchronization assumes
one CPU. No overhead percentage is claimed. The source-only workflow passed in
an isolated same-host directory without evidence or binaries, including a path
with spaces. A second physical laptop and a final post-publication clone remain
to be verified: [portability verification](docs/PORTABILITY_VERIFICATION.md).

## Documentation and recording

- [Person 2 prerequisites/setup](docs/PERSON2_SETUP.md)
- [Baseline setup/evidence](docs/BASELINE_SETUP.md)
- [Kernel implementation](docs/KERNEL_MODIFICATION.md)
- [Final report draft](docs/FINAL_PROJECT_REPORT.md)
- [Person 1 four-minute script](docs/VIDEO_PERSON1.md)
- [Person 2 setup and four-minute script](docs/VIDEO_PERSON2.md)
- [Final testing summary](docs/FINAL_TESTING_SUMMARY.md)
- [Portability verification](docs/PORTABILITY_VERIFICATION.md)

Team member 1: [Name / register number]. Team member 2: [Name / register number].
Fill in the report's course/university/faculty/submission fields before submission.

## Repository organization

Commit source, tests, portable scripts/shared runner, documentation, and small
report images. Keep `generated/` and local modified/demo/finalization evidence
out of normal staging; `.gitignore` preserves those files locally. Existing
tracked baseline evidence is intentionally left untouched: ignoring a path does
not untrack it. No automatic cleanup or Git-history operation is performed.
The final handoff must be reviewed/committed/pushed manually by the author.

<details>
<summary>Original upstream README and attribution, retained</summary>

# Pintos
Labs for undergraduate OS class (600.318) at Johns Hopkins. [Pintos](http://pintos-os.org) 
is a teaching operating system for x86, challenging but not overwhelming, small
but realistic enough to understand OS in depth (it can run x86 machine and simulators 
including QEMU, Bochs and VMWare Player!). The main source code, documentation and assignments 
are developed by Ben Pfaff and others from Stanford (refer to its [LICENSE](src/LICENSE)).

The course instructor ([Ryan Huang](mailto:huang@cs.jhu.edu)) made some changes to the original
Pintos labs to tailor for his class. The upstream for this branch comes from 
[https://github.com/ryanphuang/PintosM](https://github.com/ryanphuang/PintosM). For students in the class, please
download the release version for this branch at https://github.com/jhu-cs318/pintos.git

</details>
