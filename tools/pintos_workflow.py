#!/usr/bin/env python3
"""Source-built Pintos setup and checked live demos. Python standard library only."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shlex
import shutil
import signal
import struct
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
FLAGS = "-m32 -g -msoft-float -O0 -fno-stack-protector -fno-pie -fno-pic"
TESTS = ["cpu-monitor", "monitor-overflow", "alarm-single", "alarm-simultaneous", "alarm-zero"]
INSTALL = "sudo apt update && sudo apt install git build-essential binutils gcc-multilib perl python3 qemu-system-x86"

class Failure(Exception):
    pass

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def source_state():
    files = []
    for path in (ROOT / "src").rglob("*"):
        if not path.is_file() or "build" in path.relative_to(ROOT / "src").parts:
            continue
        if path.suffix in (".c", ".h", ".S", ".ck", ".pm") or path.name.startswith("Make"):
            files.append(path)
    return {p.relative_to(ROOT).as_posix(): digest(p) for p in sorted(files)}

def tools(build=False):
    if platform.system() != "Linux" or platform.machine() not in ("x86_64", "i386", "i686"):
        raise Failure("Use x86/x86_64 Linux (validated on Ubuntu 24.04 WSL2). ARM/cross-toolchain setup is not covered.")
    names = ["perl", "qemu-system-i386"]
    if build:
        names += ["git", "gcc", "make", "ld", "objdump", "objcopy", "nm", "ar"]
    missing = [name for name in names if not shutil.which(name)]
    if missing:
        raise Failure("Missing tools: " + ", ".join(missing) + "\nRun inside Ubuntu yourself:\n" + INSTALL)

def execute(args, cwd, output, timeout=30, input_data=None):
    start = time.monotonic()
    p = subprocess.Popen(args, cwd=cwd, stdin=subprocess.PIPE if input_data is not None else subprocess.DEVNULL,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, start_new_session=True)
    timed_out = False
    try:
        raw, _ = p.communicate(input_data, timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        os.killpg(p.pid, signal.SIGTERM)
        try:
            raw, _ = p.communicate(timeout=3)
        except subprocess.TimeoutExpired:
            os.killpg(p.pid, signal.SIGKILL)
            raw, _ = p.communicate()
    output.write_bytes(raw)
    record = {"command": args, "cwd": str(cwd), "exit_status": p.returncode,
              "timeout": timed_out, "elapsed_seconds": round(time.monotonic()-start, 3),
              "output": str(output)}
    with (output.parent / "commands.jsonl").open("a") as log:
        log.write(json.dumps(record) + "\n")
    return record, raw

def checked(args, cwd, output, timeout=30, input_data=None):
    record, raw = execute(args, cwd, output, timeout, input_data)
    if record["timeout"] or record["exit_status"] != 0:
        sys.stderr.write(raw.decode(errors="replace")[-6000:])
        raise Failure("Command failed: " + shlex.join(args) + "\nFull log: " + str(output))
    return raw

def verify_pack(pack):
    sums = pack / "SHA256SUMS"
    if not sums.is_file():
        raise Failure("Artifacts missing. Run: bash setup_person2.sh")
    for line in sums.read_text().splitlines():
        expected, name = line.split("  ", 1)
        path = (pack / name).resolve()
        if not path.is_relative_to(pack.resolve()) or not path.is_file() or digest(path) != expected:
            raise Failure("Artifact integrity failure: " + name + "; rerun setup_person2.sh")

def run_tests(pack, names, run, full=False):
    tools()
    verify_pack(pack)
    print((pack / "version.txt").read_text().strip(), flush=True)
    results = []
    for name in names:
        if name not in TESTS:
            raise Failure("Unsupported demo test: " + name)
        print("\nLIVE: " + name, flush=True)
        args = ["qemu-system-i386", "-device", "isa-debug-exit", "-drive",
                "format=raw,media=disk,index=0,file=" + str(pack / (name + ".dsk")),
                "-snapshot", "-m", "4", "-net", "none", "-display", "none",
                "-serial", "stdio", "-monitor", "none", "-no-reboot"]
        record, raw = execute(args, ROOT, run / (name + ".output"), timeout=20)
        text = raw.decode(errors="replace")
        markers = ["Boot complete.", "(" + name + ") begin", "(" + name + ") end",
                   "Execution of '" + name + "' complete.", "Powering off..."]
        normal = (not record["timeout"] and record["exit_status"] in (0, 99)
                  and all(s in text for s in markers)
                  and not any(s in text for s in ("PANIC", "FAIL", "TIMEOUT", "still running...")))
        check = ["perl", "-I", str(pack / "checker-lib"), str(pack / "checkers" / (name + ".ck")),
                 str(run / name), str(pack / "checker-lib")]
        checker_result = "NOT RUN: boot/shutdown failure"
        checker_status = None
        if normal:
            check_record, _ = execute(check, ROOT, run / (name + ".checker.log"))
            checker_status = check_record["exit_status"]
            result_file = run / (name + ".result")
            checker_result = result_file.read_text().strip() if result_file.exists() else "MISSING RESULT"
            normal = not check_record["timeout"] and checker_status == 0 and checker_result == "PASS"
        results.append(dict(record, test=name, checker_status=checker_status,
                            result=checker_result, passed=normal))
        (run / "results.json").write_text(json.dumps(results, indent=2) + "\n")
        if full or not normal:
            print(text, flush=True)
        elif name == "cpu-monitor":
            first = text.find("========== PINTOS THREAD MONITOR")
            last = text.find("(cpu-monitor) PASS:", first)
            print(text[first:last].strip(), flush=True)
        elif name == "monitor-overflow":
            print("\n".join(line for line in text.splitlines() if "(monitor-overflow) PASS:" in line))
        print(("PASS" if normal else "FAIL") + ": " + name + "; checker=" + checker_result +
              "; guest exit=" + str(record["exit_status"]), flush=True)
        if not normal:
            raise Failure("Live test failed; complete evidence: " + str(run))
    print("\nPASS: " + str(len(results)) + "/" + str(len(names)) + " supported live tests; normal guest shutdown.")
    print("Known upstream limitation: priority-fifo fails on original and modified kernels; excluded from this supported suite.")
    print("Full output, exact commands, and results: " + str(run))
    return results

def setup():
    tools(build=True)
    parent = ROOT / "generated/person2/runs"
    parent.mkdir(parents=True, exist_ok=True)
    run = Path(tempfile.mkdtemp(prefix="setup-", dir=parent))
    print("Setup logs: " + str(run), flush=True)
    print("No packages are installed automatically. Building current source.", flush=True)
    state = source_state()
    try:
        environment = {"platform": platform.platform(), "machine": platform.machine()}
        for name in ("gcc", "make", "ld", "perl", "python3", "qemu-system-i386", "git"):
            raw = checked([name, "--version"], ROOT, run / (name + "-version.log"))
            environment[name] = raw.decode(errors="replace").splitlines()[:2]
        (run / "environment.json").write_text(json.dumps(environment, indent=2) + "\n")
        checked(["gcc", "-m32", "-x", "c", "-c", "-o", str(run / "probe.o"), "-"], ROOT,
                run / "32-bit-probe.log", input_data=b"int probe;\n")
        checked(["make", "-C", "src/threads", "-B", "-j2", "CFLAGS=" + FLAGS], ROOT,
                run / "build.log", timeout=180)
        kernel = ROOT / "src/threads/build/kernel.bin"
        raw = kernel.read_bytes()
        if raw[:5] != b"\x7fELF\x01" or struct.unpack_from("<H", raw, 18)[0] != 3:
            raise Failure("Generated kernel is not an ELF32 Intel 80386 executable")
        pack = run / "artifacts"
        pack.mkdir()
        for name in ("kernel.bin", "loader.bin"):
            shutil.copy2(ROOT / "src/threads/build" / name, pack / name)
        if (pack / "loader.bin").stat().st_size != 512:
            raise Failure("Unexpected loader size")
        try:
            revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, stderr=subprocess.DEVNULL, text=True).strip()
        except subprocess.CalledProcessError:
            revision = "source export (no Git metadata)"
        manifest = json.dumps(state, sort_keys=True).encode()
        version = "Pintos Thread Monitor v1, SOURCE-BUILT HERE\nSource base revision: " + revision + "\nSource manifest SHA-256: " + hashlib.sha256(manifest).hexdigest() + "\n"
        (pack / "version.txt").write_text(version)
        (pack / "source_sha256.json").write_text(json.dumps(state, indent=2) + "\n")
        for name in ("tests/tests.pm", "tests/Algorithm/Diff.pm", "tests/threads/alarm.pm"):
            dst = pack / "checker-lib" / name
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / "src" / name, dst)
        (pack / "checkers").mkdir()
        for name in TESTS:
            shutil.copy2(ROOT / "src/tests/threads" / (name + ".ck"), pack / "checkers" / (name + ".ck"))
            checked(["perl", str(ROOT / "src/utils/pintos"), "--make-disk=" + str(pack / (name + ".dsk")),
                     "--kernel=" + str(pack / "kernel.bin"), "--loader=" + str(pack / "loader.bin")],
                    ROOT, run / (name + "-disk.log"))
            checked(["perl", str(ROOT / "src/utils/pintos-set-cmdline"), str(pack / (name + ".dsk")),
                     "--", "-q", "run", name], ROOT, run / (name + "-cmdline.log"))
        (pack / "SHA256SUMS").write_text("".join(digest(p) + "  " + p.relative_to(pack).as_posix() + "\n"
            for p in sorted(pack.rglob("*")) if p.is_file()))
        smoke = run / "smoke"
        smoke.mkdir()
        run_tests(pack, ["cpu-monitor"], smoke)
        if source_state() != state:
            raise Failure("Source changed during setup; rerun after source edits finish")
        current = ROOT / "generated/person2/current.json"
        ready = {"setup_run": run.relative_to(ROOT).as_posix(), "source": state, "revision": revision}
        temporary = current.with_suffix(".tmp")
        temporary.write_text(json.dumps(ready, indent=2) + "\n")
        temporary.replace(current)
        (run / "setup-status.json").write_text(json.dumps({"passed": True, "build_flags": FLAGS}, indent=2) + "\n")
        print("\nSETUP PASS: built from source, verified ELF32, prepared images, and passed the live monitoring checker.")
        print("Ready for recording: bash demo_person2.sh")
    except Exception:
        (run / "setup-status.json").write_text(json.dumps({"passed": False}) + "\n")
        print("SETUP FAIL. Logs retained: " + str(run), file=sys.stderr)
        raise

def demo(full):
    current = ROOT / "generated/person2/current.json"
    if not current.exists():
        raise Failure("Setup has not completed. Run: bash setup_person2.sh")
    ready = json.loads(current.read_text())
    if ready["source"] != source_state():
        raise Failure("Source changed since setup. Rebuild before recording: bash setup_person2.sh")
    run = ROOT / ready["setup_run"]
    if not run.resolve().is_relative_to((ROOT / "generated/person2/runs").resolve()):
        raise Failure("Invalid setup artifact path")
    logs = ROOT / "generated/person2/demo-runs"
    logs.mkdir(parents=True, exist_ok=True)
    output = Path(tempfile.mkdtemp(prefix="live-", dir=logs))
    print("PINTOS KERNEL MONITOR - PERSON 2\nFeatures: per-thread CPU samples, dispatches, copied completed history, safe reporting.")
    run_tests(run / "artifacts", TESTS, output, full)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("setup")
    p = sub.add_parser("demo")
    p.add_argument("--full", action="store_true")
    p = sub.add_parser("run")
    p.add_argument("--artifacts", type=Path, required=True)
    p.add_argument("--regressions", action="store_true")
    p.add_argument("--full", action="store_true")
    args = parser.parse_args()
    if args.action == "setup":
        setup()
    elif args.action == "demo":
        demo(args.full)
    else:
        logs = ROOT / "evidence/demo-runs"
        logs.mkdir(parents=True, exist_ok=True)
        run_tests(args.artifacts.resolve(), TESTS if args.regressions else ["cpu-monitor"],
                  Path(tempfile.mkdtemp(prefix="modified-", dir=logs)), args.full)

if __name__ == "__main__":
    try:
        main()
    except (Failure, OSError, ValueError, KeyError) as error:
        print("FAIL: " + str(error), file=sys.stderr)
        sys.exit(1)
