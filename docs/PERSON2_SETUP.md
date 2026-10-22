# Person 2 setup: Windows, Ubuntu, build, and recording

Complete setup before recording. This workflow compiles the modified kernel
on your laptop; no evidence folder or binary needs to be copied from Person 1.
The project targets x86/x86_64 Ubuntu Linux. Ubuntu 24.04 on WSL2 is verified;
ARM Windows/Ubuntu needs a separate cross-toolchain procedure and is not covered.

## 1. Windows PowerShell: prepare WSL

Open PowerShell and check:

```powershell
wsl --status
wsl --list --verbose
```

If WSL/Ubuntu is absent, open PowerShell as Administrator:

```powershell
wsl --install -d Ubuntu-24.04
```

Restart Windows when requested. If that distribution name is unavailable,
use `wsl --list --online` and choose the Ubuntu 24.04 entry shown. Existing
Ubuntu installations can be used without reinstalling. If Ubuntu is listed
with VERSION 1, convert it, using its exact listed name:

```powershell
wsl --set-version Ubuntu-24.04 2
wsl --distribution Ubuntu-24.04
```

On first launch, finish decompression and create a Linux username/password.
The password prompt displays no characters while you type; this is normal.
If installation requests virtualization, enable it in the computer's firmware
and follow the displayed WSL error instructions before continuing.
The commands above are Windows commands. Microsoft documents installation,
restarts, first launch, and version checks in its [WSL installation guide](https://learn.microsoft.com/en-us/windows/wsl/install).

## 2. Ubuntu terminal: verify and install dependencies

All remaining commands run inside Ubuntu, not PowerShell:

```bash
cat /etc/os-release
uname -m
pwd
sudo apt update
sudo apt install git build-essential binutils gcc-multilib perl python3 qemu-system-x86
```

Expect Ubuntu and `x86_64` on the validated configuration. `build-essential`
provides GCC/Make and native build support; binutils provides assembler,
linker, and binary tools; Perl runs Pintos utilities/checkers; Python 3 runs
our workflow; QEMU runs the emulated x86 kernel. `gcc-multilib` provides the
supported native 32-bit compiler environment on x86_64 Ubuntu. The kernel
itself uses its own headers and does not link a hosted libc. No GUI, GDB,
Bochs, Windows compiler, Python package, or KVM configuration is needed.

```bash
command -v git gcc make ld objdump objcopy nm ar perl python3 qemu-system-i386
gcc --version
qemu-system-i386 --version
```

The setup script never invokes sudo or installs packages. If a tool is
missing, it prints installation instructions and exits nonzero.

## 3. Clone the project into Linux storage

```bash
mkdir -p ~/os-projects
cd ~/os-projects
git clone https://github.com/hst257/Pintos-Kernel-Monitor.git
cd Pintos-Kernel-Monitor
pwd
git status --short --branch
```

Check that `setup_person2.sh`, `demo_person2.sh`, and
`tools/pintos_workflow.py` exist. The author must commit and push the Phase 3
files first; a clone made before that cannot contain these scripts.
Use your Ubuntu home directory, rather than a Windows mounted directory,
for consistent Linux permissions and build behavior.

If you cloned earlier and have no changes to preserve, update before setup:

```bash
git status
git pull --ff-only
```

If Git reports local changes or refuses the update, stop and ask your teammate;
do not reset or discard files. After any source update, rerun setup.

## 4. Build and smoke-test from source

```bash
bash setup_person2.sh
```

The script resolves its own location, so it also works when invoked by its
full path from another directory. It checks Linux/architecture/tools, tests
32-bit object generation, forces a consistent rebuild, validates the actual
ELF32 kernel and loader, creates five boot images, and runs the real monitoring
workload and its Perl checker. The build command is:

```bash
make -C src/threads -B -j2 \
  CFLAGS='-m32 -g -msoft-float -O0 -fno-stack-protector -fno-pie -fno-pic'
```

The flags matter: an earlier default build compiled but reset during boot.
Disabling PIE/PIC resolved it. No kernel source patch was used for that fix.
The script always compiles source and never substitutes an archived kernel.

Success ends with `SETUP PASS` and instructions to run the demo. Full logs
are in a new `generated/person2/runs/setup-*` directory, including `build.log`,
`environment.json`, exact commands/statuses, smoke output, and checker result.
`generated/person2/current.json` identifies the last successful setup using
relative paths. Repeating setup preserves old runs and publishes new artifacts
only after another successful smoke test; failure retains logs and leaves the
last successful setup available. The demo rejects a source mismatch.

## 5. Verify the complete recording command

```bash
bash demo_person2.sh
```

This runs five tests LIVE: CPU monitor, 19-thread history overflow,
alarm-single, alarm-simultaneous, and alarm-zero. Expect an actual three-row
statistics table, copied DONE records, an overflow check, each checker PASS,
and a supported-suite PASS summary. Values can vary; do not memorize ticks.
No kernel rebuild happens during the demo. Use `--full` for full console output:

```bash
bash demo_person2.sh --full
```

Live logs, checker results, commands, exit status, and timeout flags go to
`generated/person2/demo-runs/live-*`. This workflow uses no baseline or modified
archives. A concise message distinguishes the known priority-fifo failure
from the supported suite; this unrelated test is not falsely counted as PASS.

Raw QEMU status 99 is expected for this kernel's `isa-debug-exit` shutdown.
The script also requires startup, test completion, normal shutdown, no panic,
and a passing checker. Status alone is insufficient. A timeout always fails.

## 6. Prepare the terminal and record

Run the full demo once before recording. Then maximize Ubuntu Terminal,
choose a readable font around 18-22 points, disable unrelated notifications,
and keep the project directory ready. Have `docs/VIDEO_PERSON2.md` open for
practice. Start screen/audio recording, run `bash demo_person2.sh`, and
explain the real results in one continuous take. Do not install packages,
update Git, edit source, or rebuild while recording. Save the recording
locally and send it to your teammate for joining with Person 1's section.

## Troubleshooting

| Symptom | Action inside Ubuntu unless stated otherwise |
| --- | --- |
| qemu-system-i386 not found | Install `qemu-system-x86`, then rerun setup. |
| GCC/Make missing | Install `build-essential`; recheck `command -v gcc make`. |
| 32-bit object failure | Install `gcc-multilib` on x86_64 Ubuntu; read `32-bit-probe.log`. ARM needs a different toolchain. |
| Repeated boot reset/PIE problem | Rerun setup with its complete known flags; do not patch kernel code. |
| Permission denied | Invoke wrappers with `bash`; keep the checkout in your Linux home and owned by your Linux account. Do not run setup as root or chmod the whole tree. |
| File/script missing | Check `pwd`, `ls`, and whether Phase 3 was pushed; use the correct repository. |
| Missing archived binaries | Person 2 does not need them. Run `setup_person2.sh`, then `demo_person2.sh`, rather than the legacy archive path. |
| Setup failed | Read the printed setup directory's build/probe/environment logs; do not proceed to recording until SETUP PASS. |
| Demo says source changed | Rerun setup before recording. Source hashes prevent a stale build being described as current. |
| Integrity failure | Rerun setup to generate a new bundle; preserve the failing logs. |
| Timeout/unexpected exit | Read the full `.output` and `results.json`; do not call timeout a successful boot. Close competing heavy tasks and retry before recording. Persistent failures need diagnosis. |
| Test checker FAIL | Keep the actual output/checker log and ask your teammate; do not edit expected tick counts or hide the failure. |

The second physical laptop has not been tested by the authoring agent.
See `PORTABILITY_VERIFICATION.md` for the actual isolated-source verification
and its environment limits.
