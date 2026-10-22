#!/usr/bin/env bash
set -euo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
mode=${1:---monitor}
if [[ $# -gt 1 || ( "$mode" != --monitor && "$mode" != --regressions ) ]]; then
  printf 'Usage: bash demo_modified.sh [--regressions]\n' >&2
  exit 2
fi
archive="$root/evidence/modified/artifacts"
if [[ -f "$root/generated/person2/current.json" ]]; then
  prepared=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["setup_run"])' "$root/generated/person2/current.json")
  archive="$root/$prepared/artifacts"
fi
if [[ ! -f "$archive/SHA256SUMS" ]]; then
  printf 'Local archives are absent. First run: bash setup_person2.sh\n' >&2
  exit 1
fi
args=(run --artifacts "$archive" --full)
if [[ "$mode" == --regressions ]]; then args+=(--regressions); fi
exec python3 "$root/tools/pintos_workflow.py" "${args[@]}"
