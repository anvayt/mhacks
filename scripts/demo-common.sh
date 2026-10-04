#!/usr/bin/env bash
# Shared shell helpers. No dependency installation, secret echoing, or global pkill.
set -euo pipefail
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

# Literal dotenv assignments only: inherited environment wins, then root .env,
# then agent/.env. Never source/eval a credentials file or expand shell expressions.
load_env() {
    local file=$1 line key value
    [[ -f "$file" ]] || return 0
    while IFS= read -r line || [[ -n "$line" ]]; do
        line=${line%$'\r'}
        if [[ "$line" =~ ^[[:space:]]*(export[[:space:]]+)?([A-Z_][A-Z0-9_]*)[[:space:]]*=[[:space:]]*(.*)$ ]]; then
            key=${BASH_REMATCH[2]}; value=${BASH_REMATCH[3]}
            declare -p "$key" >/dev/null 2>&1 && continue
            if [[ "$value" == \"*\" ]]; then value=${value:1:${#value}-2}
            elif [[ "$value" == \'*\' ]]; then value=${value:1:${#value}-2}
            else value=${value%% #*}; value="${value%"${value##*[![:space:]]}"}"
            fi
            export "$key=$value"
        fi
    done < "$file"
}
load_env "$ROOT/.env"
load_env "$ROOT/agent/.env"
MODEL_DIR=${MODEL_DIR:-$ROOT}
API_BASE_URL=${API_BASE_URL:-http://localhost:8000}
MODEL_BASE_URL=${MODEL_BASE_URL:-http://localhost:8001}
DEMO_LOG_DIR=${DEMO_LOG_DIR:-$ROOT/data/demo/$(date +%Y%m%d-%H%M%S)-$$}
mkdir -p "$DEMO_LOG_DIR"
export MODEL_DIR API_BASE_URL MODEL_BASE_URL DEMO_LOG_DIR
API_PY="$ROOT/api/.venv/bin/python"

fail() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
need() { command -v "$1" >/dev/null 2>&1 || fail "Install prerequisite: $1"; }
healthy() { curl --noproxy '*' -fsS --connect-timeout 1 --max-time 3 "$1" >/dev/null 2>&1; }
port_used() { lsof -nP -iTCP:"$1" -sTCP:LISTEN -t >/dev/null 2>&1; }

# Job control creates a separate process group for each background service, so
# npm/tsx/Next descendants are cleaned up with their own parent. IDs are kept in
# memory; a stale PID file is never used as authority to kill a process.
OWNED_PIDS=()
OWNED_GROUPS=()
LAST_PID=
process_tracking() {
    need ps; need lsof
    set -m
    SELF_GROUP=$(ps -o pgid= -p $$ | tr -d ' ')
    trap cleanup EXIT
    trap 'exit 130' INT
    trap 'exit 143' TERM
}
track_owned() {
    local pid=$1 name=$2 group
    OWNED_PIDS+=("$pid")
    group=$(ps -o pgid= -p "$pid" | tr -d ' ') || group=
    [[ "$group" =~ ^[0-9]+$ && "$group" == "$pid" && "$group" != "$SELF_GROUP" && "$group" -gt 1 ]] || fail "Could not isolate $name process group"
    OWNED_GROUPS+=("$group")
    printf '%s\t%s\t%s\n' "$name" "$pid" "$group" >> "$DEMO_LOG_DIR/owned.tsv"
    LAST_PID=$pid
}
start_owned() {
    local name=$1 dir=$2
    shift 2
    (cd "$dir" && exec "$@") > "$DEMO_LOG_DIR/$name.log" 2>&1 &
    track_owned "$!" "$name"
}
cleanup_before() { :; }
cleanup_extra() { :; }

# Explicitly release one group this process started; never read PID files here.
stop_owned() {
    local target=$1 group index round
    for ((index=0; index<${#OWNED_GROUPS[@]}; index++)); do
        group=${OWNED_GROUPS[$index]}
        [[ "$group" == "$target" ]] || continue
        kill -TERM -- "-$group" 2>/dev/null || true
        for round in 1 2 3 4 5; do
            kill -0 -- "-$group" 2>/dev/null || break
            sleep 1
        done
        kill -KILL -- "-$group" 2>/dev/null || true
        wait "${OWNED_PIDS[$index]}" 2>/dev/null || true
        unset 'OWNED_GROUPS[index]' 'OWNED_PIDS[index]'
        set +u
        OWNED_GROUPS=("${OWNED_GROUPS[@]}"); OWNED_PIDS=("${OWNED_PIDS[@]}")
        set -u
        return
    done
    fail "Refusing to stop an unowned process group"
}

cleanup() {
    local status=$? group pid round alive
    trap - EXIT INT TERM
    cleanup_before
    set +eu  # Bash 3.2 treats an empty array expansion as unbound under nounset.
    for group in "${OWNED_GROUPS[@]}"; do
        [[ "$group" != "$SELF_GROUP" && "$group" -gt 1 ]] && kill -TERM -- "-$group" 2>/dev/null
    done
    # A group can outlive npm/make; wait on group existence, not only its leader.
    for round in 1 2 3 4 5 6 7 8 9 10; do
        alive=0
        for group in "${OWNED_GROUPS[@]}"; do kill -0 -- "-$group" 2>/dev/null && alive=1; done
        [[ "$alive" == 0 ]] && break
        sleep 1
    done
    for group in "${OWNED_GROUPS[@]}"; do
        [[ "$group" != "$SELF_GROUP" && "$group" -gt 1 ]] && kill -KILL -- "-$group" 2>/dev/null
    done
    for pid in "${OWNED_PIDS[@]}"; do wait "$pid" 2>/dev/null; done
    cleanup_extra
    printf 'Stopped only processes started by this run. Logs: %s\n' "$DEMO_LOG_DIR"
    exit "$status"
}
wait_healthy() {
    local name=$1 url=$2 pid=$3 limit=${4:-90} n
    for ((n=0; n<limit; n++)); do
        if healthy "$url"; then printf '%s ready: %s\n' "$name" "$url"; return; fi
        kill -0 "$pid" 2>/dev/null || fail "$name exited; see $DEMO_LOG_DIR/$name.log"
        sleep 1
    done
    fail "$name did not become healthy in ${limit}s; see $DEMO_LOG_DIR/$name.log"
}
