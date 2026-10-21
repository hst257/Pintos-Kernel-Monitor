#!/usr/bin/env bash
set -euo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
evidence="$root/evidence/baseline"
mode=${1:---live}
if [[ $# -gt 1 || ( "$mode" != --live && "$mode" != --archive ) ]]; then
  printf 'Usage: bash demo_baseline.sh [--live|--archive]\n' >&2
  exit 2
fi
cd "$evidence"
printf 'PINTOS ORIGINAL BASELINE\nArchived source revision: '
cat revision.txt
printf '\nChecking archived evidence and artifact hashes...\n'
sha256sum --check --quiet SHA256SUMS
printf '\nARCHIVED BUILD EVIDENCE (this is not a live rebuild)\n'
tail -n 10 build.log
file artifacts/kernel.bin artifacts/loader.bin
printf '\nARCHIVED BOOT EVIDENCE (this is not a live boot)\n'
grep -E 'Pintos booting|Boot complete|product=|Execution of|Powering off' boot.log
printf 'Upstream alarm-single checker: '
cat alarm-single.result
if [[ "$mode" == --archive ]]; then
  printf '\nArchive display complete; no kernel was executed.\n'
  exit 0
fi
printf '\nLIVE EXECUTION OF THE ARCHIVED ORIGINAL KERNEL\n'
printf 'The working-tree kernel is not rebuilt or executed.\n'
python3 - "$root" <<'PYDEMO'
from pathlib import Path
import hashlib, re, shlex, subprocess, sys, tempfile
root=Path(sys.argv[1]); evidence=root/'evidence/baseline'
disk=evidence/'artifacts/baseline-alarm-single.dsk'
logdir=root/'evidence/demo-runs'; logdir.mkdir(parents=True,exist_ok=True)
before=hashlib.sha256(disk.read_bytes()).hexdigest()
args=['timeout','--signal=TERM','--kill-after=5s','20s',
      'qemu-system-i386','-device','isa-debug-exit',
      '-drive','format=raw,media=disk,index=0,file='+str(disk),
      '-snapshot','-m','4','-net','none','-display','none',
      '-serial','stdio','-monitor','none','-no-reboot']
print('$ '+shlex.join(args),flush=True)
try:
    result=subprocess.run(args,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT,timeout=30)
except subprocess.TimeoutExpired as error:
    print('FAIL: Outer safety timeout; this is not successful boot evidence.',file=sys.stderr)
    if error.stdout:
        with tempfile.NamedTemporaryFile(prefix='failed-',suffix='.log',dir=logdir,delete=False) as log:
            log.write(error.stdout)
            print('Partial live output saved to '+log.name,file=sys.stderr)
    raise SystemExit(1)
with tempfile.NamedTemporaryFile(prefix='baseline-',suffix='.log',dir=logdir,delete=False) as log:
    log.write(result.stdout); logname=log.name
sys.stdout.buffer.write(result.stdout); sys.stdout.flush()
text=result.stdout.decode(errors='replace')
required=['Pintos booting with','Boot complete.','(alarm-single) begin',
          '(alarm-single) end',"Execution of 'alarm-single' complete.",'Powering off...']
valid=(result.returncode in (0,99) and all(s in text for s in required)
       and not any(s in text for s in ['PANIC','FAILED','TIMEOUT','still running...'])
       and re.findall(r'product=(\d+)\r?$',text,re.M)==['10','20','30','40','50']
       and hashlib.sha256(disk.read_bytes()).hexdigest()==before)
print('Raw QEMU/timeout exit status:',result.returncode)
print('Live output saved to:',logname)
if not valid:
    print('FAIL: Baseline completion or integrity check failed.',file=sys.stderr)
    raise SystemExit(1)
print('PASS: Original kernel initialized, completed alarm-single, and powered off normally.')
print('Status 99 is the expected isa-debug-exit shutdown status; no timeout occurred.')
PYDEMO
