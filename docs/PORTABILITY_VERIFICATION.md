# Portability verification

## What was actually verified

On 2026-10-22, the authoring environment was Ubuntu 24.04.1 WSL2 on x86_64,
GCC 13.3, binutils 2.42, Make 4.3, Perl 5.38.2, Python 3.12.3, QEMU 8.2.2,
and Git 2.43.0. No package was installed during finalization.

Phase 2 is committed at `476d3e1` (the original kernel remains tagged at
`ab699959f0d3eae8e59d8507ae2474a638c3d1d3`). Phase 3 scripts and documents
were uncommitted during testing. A genuine clone of the final Phase 3 revision
cannot be tested until the user commits/pushes those files. No commit or push
was made by the agent, and no second physical laptop was used.

## Source-only isolation method

An isolated directory beneath `/tmp`, with the project folder named
`Pintos Kernel Monitor`, received `git archive HEAD src` and only the three
new portable files: `setup_person2.sh`, `demo_person2.sh`, and
`tools/pintos_workflow.py`. This deliberately omitted `.git`, both evidence
archives, `generated/`, and `src/threads/build/`. Initial absence checks
confirmed no kernel binaries or previous setup outputs were available.
The source export is stronger evidence of archive independence than a normal
working-tree test, but it is not a genuine final-revision clone or a second
machine test. It shares this host's installed toolchain.

The actual command forms, executed with caller working directory `/tmp`, were:

```bash
bash "$isolated_project/setup_person2.sh"
bash "$isolated_project/demo_person2.sh"
bash "$isolated_project/setup_person2.sh"
```

The variable denotes the isolated project path recorded in the evidence JSON;
it is not a command that depends on Person 1's username. The original checkout's
branch, index, remotes, and history were not changed.

| Check | Actual result |
| --- | --- |
| Fresh source build with known flags | PASS, exit 0 |
| ELF32 kernel / 512-byte loader validation | PASS |
| Images created without local archives | PASS |
| CPU-monitor smoke workload and checker | PASS |
| Person 2 live five-test demonstration | PASS, exit 0 |
| Source path containing spaces | PASS |
| Invocation from a different current directory | PASS |
| Setup rerun, separate preserved run directories | PASS, exit 0 |
| Original evidence folder absent throughout isolated workflow | PASS |
| Genuine final Git clone after Phase 3 push | NOT YET TESTED |
| Person 2's physical laptop | NOT TESTED |

Setup logs are `evidence/finalization/isolated-setup.log` and
`isolated-setup-rerun.log`; the demo log is `isolated-demo.log`.
`portability-results.json` records exact expanded commands, paths, commit,
statuses, and the method. Source-derived artifacts and test outputs remain
in the isolated directory, whose actual location is recorded there.
These audit logs are retained locally and excluded from normal Git staging.

## Original-laptop checks

The current checkout independently ran source setup, `demo_person2.sh`,
`demo_modified.sh`, and both default/video baseline modes successfully.
The portable scripts and shared runner contain no literal original-machine
path. All paths derive from the script location. Artifact manifests use
relative file names. Logs may record absolute paths from the machine on
which a command actually ran; those generated files are local outputs.

## Reproducible publication gate

The author must review, commit, and push the Phase 3 source/scripts/docs
listed in the final handoff. Person 2 can then run:

```bash
git clone https://github.com/hst257/Pintos-Kernel-Monitor.git
cd Pintos-Kernel-Monitor
bash setup_person2.sh
bash demo_person2.sh
```

Record that laptop's actual environment and results before claiming cross-laptop
verification. If a script is missing, check publication/update state rather
than copying binaries from Person 1. Ubuntu on ARM, other compiler versions,
restricted package/network access, and other distributions remain unverified.
The setup checks architecture, tools, a 32-bit compile, actual boot/shutdown,
and checker success; passing compilation alone is not accepted.
