#!/usr/bin/env bash
# sync-payload.sh — Regenerate the skill payload directory from source.
#
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MANIFEST="$ROOT/scripts/payload-manifest.json"
PAYLOAD_DIR="$ROOT/skills/python-project-workflow"
CI_MODE=false

[ "${1:-}" = "--ci" ] && CI_MODE=true

[ -f "$MANIFEST" ] || { echo "FAIL: manifest not found"; exit 1; }

echo "Syncing skill payload..."
DRIFT=false
CHANGED=false
SYNC_ERROR=false

sync_file() {
    local source="$1"
    local target="$2"
    local label="$3"
    local mode="${4:-644}"

    if [ ! -f "$source" ]; then
        echo "  MISSING source: $label"
        DRIFT=true
        SYNC_ERROR=true
        return
    fi

    if $CI_MODE; then
        if [ ! -f "$target" ] || ! cmp -s "$source" "$target"; then
            echo "  DRIFTED: $label"
            DRIFT=true
        fi
        return
    fi

    if [ ! -f "$target" ] || ! cmp -s "$source" "$target"; then
        CHANGED=true
    fi
    mkdir -p "$(dirname "$target")"
    install -m "$mode" "$source" "$target"
}

is_covered() {
    local rel="$1"
    # Authored-in-place files (written directly in payload, not copied)
    case "$rel" in
        SKILL.md) return 0 ;;
    esac
    for f in $(python3 -c "import json; d=json.load(open('$MANIFEST')); print('\n'.join(str(x) for x in d.get('files',[])))" 2>/dev/null); do
        [ "$rel" = "$f" ] && return 0
    done
    for s in $(python3 -c "import json; d=json.load(open('$MANIFEST')); print('\n'.join(str(x) for x in d.get('scripts',[])))" 2>/dev/null); do
        [ "$rel" = "scripts/$s" ] && return 0
    done
    local ref_mode
    ref_mode=$(python3 -c "import json; d=json.load(open('$MANIFEST')); r=d.get('references',''); print(r if isinstance(r,str) else '')" 2>/dev/null)
    if [ "$ref_mode" = "*" ]; then
        case "$rel" in
            references/*) [ -f "$ROOT/$rel" ] && return 0 ;;
        esac
    fi
    return 1
}

# Files
for f in $(python3 -c "import json; d=json.load(open('$MANIFEST')); print('\n'.join(str(x) for x in d.get('files',[])))" 2>/dev/null); do
    source="$ROOT/$f"
    target="$PAYLOAD_DIR/$f"
    sync_file "$source" "$target" "$f"
done

# Scripts
for s in $(python3 -c "import json; d=json.load(open('$MANIFEST')); print('\n'.join(str(x) for x in d.get('scripts',[])))" 2>/dev/null); do
    source="$ROOT/scripts/$s"
    target="$PAYLOAD_DIR/scripts/$s"
    mode=644
    [ -x "$source" ] && mode=755
    sync_file "$source" "$target" "scripts/$s" "$mode"
done

# References (mirror)
ref_mode=$(python3 -c "import json; d=json.load(open('$MANIFEST')); r=d.get('references',''); print(r if isinstance(r,str) else '')" 2>/dev/null)
if [ "$ref_mode" = "*" ]; then
    for source in "$ROOT/references/"*.md; do
        if [ ! -f "$source" ]; then
            echo "  MISSING source: references/*.md"
            DRIFT=true
            SYNC_ERROR=true
            break
        fi
        name="$(basename "$source")"
        sync_file "$source" "$PAYLOAD_DIR/references/$name" "references/$name"
    done
fi

# Orphan cleanup
while IFS= read -r -d '' f; do
    relpath="$f"
    # shellcheck disable=SC2295
    rel="${relpath#$PAYLOAD_DIR/}"
    if ! is_covered "$rel"; then
        echo "  ORPHANED: $rel"
        if ! $CI_MODE; then
            rm -f "$f"
            CHANGED=true
        else
            DRIFT=true
        fi
    fi
done < <(find "$PAYLOAD_DIR" -type f -print0)
if ! $CI_MODE; then
    find "$PAYLOAD_DIR" -type d -empty -delete 2>/dev/null || true
fi

if $SYNC_ERROR; then
    echo ""
    echo "SYNC FAILED"
    exit 1
elif $DRIFT; then
    echo ""
    echo "DRIFT DETECTED"
    exit 1
elif $CHANGED; then
    echo "Payload synchronized"
else
    echo "Payload in sync"
fi
