#!/usr/bin/env bash
set -euo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
mode=${1:---monitor}
if [[ $# -gt 1 || ( "$mode" != --monitor && "$mode" != --regressions ) ]]; then
  printf 'Usage: bash demo_modified.sh [--regressions]\n' >&2
  exit 2
fi
archive="$root/evidence/modified/artifacts"
printf 'MODIFIED PINTOS KERNEL: ARCHIVED BUILD IDENTITY\n'
cat "$archive/version.txt"
(cd "$archive" && sha256sum --check --quiet SHA256SUMS)
printf '\nLIVE QEMU EXECUTION; kernel counters are produced by the guest.\n'
python3 - "$root" "$mode" <<'PYDEMO'
from pathlib import Path
import json, shlex, subprocess, sys, tempfile, time
root=Path(sys.argv[1]); archive=root/'evidence/modified/artifacts'
logdir=root/'evidence/demo-runs'; logdir.mkdir(parents=True,exist_ok=True)
run=Path(tempfile.mkdtemp(prefix='modified-',dir=logdir))
names=['cpu-monitor']
if sys.argv[2]=='--regressions':
    names+=['monitor-overflow','alarm-single','alarm-simultaneous','alarm-zero']
results=[]
for name in names:
    args=['timeout','--signal=TERM','--kill-after=5s','20s',
          'qemu-system-i386','-device','isa-debug-exit',
          '-drive','format=raw,media=disk,index=0,file='+str(archive/(name+'.dsk')),
          '-snapshot','-m','4','-net','none','-display','none',
          '-serial','stdio','-monitor','none','-no-reboot']
    print('\n$ '+shlex.join(args),flush=True)
    start=time.monotonic()
    try:
        p=subprocess.run(args,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT,timeout=30)
        raw=p.stdout; status=p.returncode
    except subprocess.TimeoutExpired as error:
        raw=error.stdout or b''; status=124
    (run/(name+'.output')).write_bytes(raw)
    sys.stdout.buffer.write(raw); sys.stdout.flush()
    text=raw.decode(errors='replace')
    normal=(status in (0,99) and all(marker in text for marker in [
        'Boot complete.', '('+name+') begin', '('+name+') end',
        "Execution of '"+name+"' complete.", 'Powering off...'])
        and not any(marker in text for marker in ['PANIC','TIMEOUT','FAIL','still running...']))
    check=['perl','-I',str(archive/'checker-lib'),
           str(archive/'checkers'/(name+'.ck')),str(run/name),str(archive/'checker-lib')]
    result='NOT RUN: boot/shutdown failure'
    if normal:
        checker=subprocess.run(check,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        (run/(name+'.checker.log')).write_text('$ '+shlex.join(check)+'\n'+checker.stdout+'exit_status='+str(checker.returncode)+'\n')
        result=(run/(name+'.result')).read_text().strip() if (run/(name+'.result')).exists() else 'MISSING RESULT'
        normal=checker.returncode==0 and result=='PASS'
    results.append({'test':name,'command':args,'raw_exit_status':status,
                    'elapsed_seconds':time.monotonic()-start,'result':result,'passed':normal})
    (run/'results.json').write_text(json.dumps(results,indent=2)+'\n')
    print(('PASS' if normal else 'FAIL')+': '+name+'; raw QEMU/timeout status='+str(status))
    if not normal:
        print('Evidence: '+str(run),file=sys.stderr)
        raise SystemExit(1)
print('\nPASS: All requested live demonstrations and their checkers passed.')
print('Full output, checker results, and exact commands: '+str(run))
print('Status 99 is normal isa-debug-exit shutdown; timeouts are failures.')
PYDEMO
