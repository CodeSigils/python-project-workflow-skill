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
        case "$rel" in references/*) return 0 ;; esac
    fi
    return 1
}

# Files
for f in $(python3 -c "import json; d=json.load(open('$MANIFEST')); print('\n'.join(str(x) for x in d.get('files',[])))" 2>/dev/null); do
    source="$ROOT/$f"
    target="$PAYLOAD_DIR/$f"
    if [ ! -f "$source" ]; then echo "  MISSING source: $f"; DRIFT=true; continue; fi
    mkdir -p "$(dirname "$target")"
    install -m 644 "$source" "$target"
done

# Scripts
for s in $(python3 -c "import json; d=json.load(open('$MANIFEST')); print('\n'.join(str(x) for x in d.get('scripts',[])))" 2>/dev/null); do
    source="$ROOT/scripts/$s"
    target="$PAYLOAD_DIR/scripts/$s"
    if [ ! -f "$source" ]; then echo "  MISSING source: scripts/$s"; DRIFT=true; continue; fi
    mkdir -p "$(dirname "$target")"
    if [ -x "$source" ]; then install -m 755 "$source" "$target"; else install -m 644 "$source" "$target"; fi
done

# References (mirror)
ref_mode=$(python3 -c "import json; d=json.load(open('$MANIFEST')); r=d.get('references',''); print(r if isinstance(r,str) else '')" 2>/dev/null)
if [ "$ref_mode" = "*" ]; then
    mkdir -p "$PAYLOAD_DIR/references"
    find "$PAYLOAD_DIR/references" -type f -delete 2>/dev/null || true
    cp "$ROOT/references/"*.md "$PAYLOAD_DIR/references/"
fi

# Orphan cleanup
orphans=0
while IFS= read -r -d '' f; do
    relpath="$f"
    # shellcheck disable=SC2295
    rel="${relpath#$PAYLOAD_DIR/}"
    if ! is_covered "$rel"; then
        echo "  ORPHANED: $rel"
        rm -f "$f"
        orphans=$((orphans + 1))
    fi
done < <(find "$PAYLOAD_DIR" -type f -print0)
find "$PAYLOAD_DIR" -type d -empty -delete 2>/dev/null || true

[ "$orphans" -gt 0 ] && DRIFT=true
if $DRIFT; then
    echo ""
    echo "DRIFT DETECTED"
    $CI_MODE && exit 1
else
    echo "Payload in sync"
fi