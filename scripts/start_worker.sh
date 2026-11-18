#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
    cat <<USAGE
Usage: $0 BACKEND [celery worker options]

Start an ewoksjob worker in the foreground.
The Python environment must have ewokssoleildemo[job] installed.

BACKEND stores the jobs, the results and the Ewoks events:
  redis   Redis server (scripts/config_redis.py)
  sqlite  SQLite files (scripts/config_sqlite.py)

Environment variables:
  EWOKS_REDIS_URL   Redis URL (default: redis://localhost:6379)
  EWOKS_SQLITE_DIR  Directory of the SQLite files (default: sqlite/ in the repository)
USAGE
}

backend="$1"
case "$backend" in
    redis | sqlite)
        shift
        ;;
    -h | --help)
        usage
        exit 0
        ;;
    *)
        usage >&2
        exit 1
        ;;
esac

export EWOKS_CONFIG_URI="$SCRIPT_DIR/config_$backend.py"

# ewoksfluo starts sub-processes: the "process" pool allows it, "prefork" does not
exec python -m ewoksjob worker \
    --pool=process \
    --concurrency=2 \
    "$@"
