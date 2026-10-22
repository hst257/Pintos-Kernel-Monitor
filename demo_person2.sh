#!/usr/bin/env bash
set -euo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
if ! command -v python3 >/dev/null 2>&1; then
  printf 'Python 3 is missing. Inside Ubuntu run: sudo apt update && sudo apt install python3\n' >&2
  exit 1
fi
exec python3 "$root/tools/pintos_workflow.py" demo "$@"
