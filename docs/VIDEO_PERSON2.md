# Person 2 video: portable build, testing, and results

Target: approximately four minutes of recording, in one continuous take.
Initial setup is separate and must be completed first. Replace only your name;
never replace genuine output with memorized counter values.

## Complete prerequisites before recording

### Windows PowerShell

Check WSL, and install Ubuntu if needed. Installation may need an Administrator
PowerShell and a restart:

```powershell
wsl --status
wsl --list --verbose
wsl --install -d Ubuntu-24.04
```

After a requested restart, launch Ubuntu from Start or:

```powershell
wsl --distribution Ubuntu-24.04
```

Use the exact installed name shown by `wsl --list --verbose`. If its VERSION is
1, convert it in PowerShell with `wsl --set-version Ubuntu-24.04 2`. First launch
asks for a Linux username and password; password typing is invisible. These
Windows-side instructions follow [Microsoft's WSL command guide](https://learn.microsoft.com/en-us/windows/wsl/basic-commands).

### Inside Ubuntu, not PowerShell

```bash
cat /etc/os-release
uname -m
sudo apt update
sudo apt install git build-essential binutils gcc-multilib perl python3 qemu-system-x86
mkdir -p ~/os-projects
cd ~/os-projects
git clone https://github.com/hst257/Pintos-Kernel-Monitor.git
cd Pintos-Kernel-Monitor
bash setup_person2.sh
bash demo_person2.sh
```

The author must have committed/pushed Phase 3 first. If you cloned earlier,
check `git status`, then use `git pull --ff-only` only when local changes are
safe to preserve; ask your teammate if Git refuses the update. Rerun setup
after an update. Do not reset files or copy the author's kernel binary.

Expect `SETUP PASS`, followed by a live five-test supported-suite PASS. Setup
builds using the known `-m32`, non-PIE/non-PIC flags and records the toolchain,
compiler output, and smoke checker. It never installs packages automatically.
All generated preparation/run files live under `generated/person2/`. A missing
legacy evidence archive is not a problem. See `PERSON2_SETUP.md` for detailed
troubleshooting. The authoring agent did not test your physical laptop; these
prerequisites must succeed here before you describe this laptop as verified.

### Terminal and recording preparation

Practice the full narration with your actual output. Keep Ubuntu in the project
root, maximize it, use a readable font, check microphone/screen capture, and
close unrelated notifications. After a successful rehearsal, clear the terminal
before starting the recording if useful. Do not clear or hide failures during
the live demonstration. Keep enough terminal rows visible for the short table
and five summary lines. No source edits, installation, update, or rebuild should
be needed during your recording.

## Recording: 0:00-0:40 — role and reproduced environment

Screen: prepared Ubuntu terminal at the repository root.

> Hello, I am [Person 2 name], and I handled testing and interpretation of the results. Before this recording, I cloned our project and ran the setup script on this laptop. It compiled the modified kernel from source, checked the generated binary, prepared the boot images, and passed a live smoke test. The setup uses the documented compatibility flags and records its environment. I am not using a kernel copied from my teammate's machine. During this demonstration, we only execute the prepared build, so no rebuild or source edit is needed.

Say the laptop-specific claims only after setup and rehearsal actually pass.

## 0:40-1:10 — start the real tests

Execute exactly one recording command:

```bash
bash demo_person2.sh
```

Screen: source revision/hash, LIVE CPU-monitor table, then checker/regression
summaries. Let the command finish. It normally takes only a few seconds; the
remaining presentation explains the visible results.

> This one command runs the modified kernel and the test checkers. The source revision and manifest identify the build prepared here. The labels say LIVE because QEMU is executing these tests now. Every run also saves full console output, commands, exit status, timeout information, and checker results. A success message requires normal initialization, test completion, shutdown, and the checker. Simply getting a process exit code is not enough.

## 1:10-2:05 — explain workload and real table

Screen: keep or scroll back to the actual three worker rows. Do not edit code.

> The monitoring workload creates three workers with different amounts of calibrated CPU work. The second worker also yields repeatedly. Each initially waits on a semaphore while the controller runs, allowing the test to check that a blocked thread is not charged CPU samples. Here each row belongs to the actual created thread ID, and DONE means its completed statistics were copied before its thread page was freed. The test checks exactly one matching final record for each worker. The CPU column counts timer samples, while dispatches count scheduler selections. A selection can return to the same thread, so dispatches are not the same as context switches. The yielding worker can have more selections while using fewer CPU samples. These values are from this run; they are not fixed expected numbers.

## 2:05-2:55 — verification and bounded storage

Screen: monitoring PASS, monitor-overflow output, and remaining PASS summaries.

> The first checker matches the created IDs to the completed rows and requires the kernel's invariant checks to finish. Those checks cover initialization, monotonic counters, blocked-thread accounting, and dispatch growth after yielding. The separate overflow test creates nineteen short-lived threads. It verifies that the newest sixteen records remain, the oldest three were overwritten, and bounded snapshots work. That demonstrates the history limit instead of assuming storage grows forever. The existing alarm-single, alarm-simultaneous, and alarm-zero checkers also pass. They exercise timer and scheduling behavior after instrumentation, including multiple threads waking together. This is a selected regression suite, not a claim that every Pintos assignment test passes.

## 2:55-3:35 — honest limitations

Screen: supported-suite summary and known upstream limitation message.

> There is one important known failure: priority-fifo fails on both the original and modified kernels because this distribution does not finish priority scheduling. We preserved both results and did not change the scheduling algorithm to make that unrelated test pass. Our supported tests passed, but we do not label that known failure as a pass. The monitor also has limits: ticks are coarse samples, short jobs may get zero samples, only sixteen completed records are retained, and interrupt-based protection assumes a single CPU. We have not measured an exact overhead percentage.

## 3:35-4:00 — evidence and conclusion

Screen: final PASS and printed local log directory.

> The final summary confirms the supported live checks passed, and the printed directory contains the complete evidence from this run. The result shows that we can observe individual CPU usage and scheduler activity inside the kernel, preserve completed results safely, and reproduce the demonstration from source. Together with the original baseline, this completes our implementation and verification. Thank you.

## Troubleshooting and final checklist

If the script says setup is missing or source changed, stop recording and run
setup again before a new take. For a real failure, preserve the printed logs
and diagnose it; do not change expected values. Use `bash demo_person2.sh --full`
only for diagnosis or rehearsal, since it prints the complete console output.
Status 99 is the configured normal QEMU exit; status alone never overrides a
panic, timeout, or failed checker. If QEMU is missing, install its Ubuntu package
before recording. All detailed cases are in `PERSON2_SETUP.md`.

Final checklist: setup succeeded on this laptop; approximately four minutes;
real table and checker summaries visible; no hardcoded counters; known failure
acknowledged; no live package install/build/edit/Git operation; one continuous
take; narration and terminal readable.
