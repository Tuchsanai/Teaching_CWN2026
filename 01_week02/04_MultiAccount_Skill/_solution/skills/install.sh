#!/usr/bin/env bash
# install.sh - copy every skill folder next to this script (folders with SKILL.md) into the
# shared skills of both CLIs, back up a different existing copy first, then verify that every
# account sees every SKILL.md. Idempotent; never touches other skills or any credential file.
#   bash install.sh            (inside the multi-account container)
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE="${AI_ACCOUNTS_BASE:-$HOME/ai-accounts}"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP="$BASE/.skill-backup-$STAMP"
EXCL=(-x __pycache__ -x '*.pyc')

skills=()
for d in "$SRC"/*/; do
    [ -f "$d/SKILL.md" ] && skills+=("$(basename "$d")")
done
[ ${#skills[@]} -gt 0 ] || { echo "install.sh: ไม่พบโฟลเดอร์สกิล (ที่มี SKILL.md) ข้าง $SRC" >&2; exit 1; }

# the shared core must be identical in yolo and cyolo
if [ -f "$SRC/yolo/scripts/macore.py" ] && [ -f "$SRC/cyolo/scripts/macore.py" ] &&
   ! cmp -s "$SRC/yolo/scripts/macore.py" "$SRC/cyolo/scripts/macore.py"; then
    echo "install.sh: yolo/scripts/macore.py กับ cyolo/scripts/macore.py ไม่เหมือนกัน — sync ก่อนติดตั้ง" >&2
    exit 1
fi
for f in "$SRC"/*/scripts/*.py; do python3 -m py_compile "$f" 2>/dev/null || { echo "syntax error: $f" >&2; exit 1; }; done
find "$SRC" -name __pycache__ -type d -prune -exec rm -rf {} + 2>/dev/null || true

declare -a installed=() unchanged=() backed=()
for side in Claude Codex; do
    dest="$BASE/.$side/shared/skills"
    mkdir -p "$dest"
    for s in "${skills[@]}"; do
        if [ -e "$dest/$s" ]; then
            if diff -rq "${EXCL[@]}" "$SRC/$s" "$dest/$s" >/dev/null 2>&1; then
                unchanged+=("$side/$s"); continue
            fi
            mkdir -p "$BACKUP/$side"
            cp -a "$dest/$s" "$BACKUP/$side/$s"
            backed+=("$side/$s")
        fi
        tmp="$dest/.$s.installing.$$"
        rm -rf "$tmp"
        cp -a "$SRC/$s" "$tmp"
        find "$tmp" -name __pycache__ -type d -prune -exec rm -rf {} + 2>/dev/null || true
        chmod +x "$tmp"/scripts/*.py 2>/dev/null || true
        rm -rf "$dest/$s"
        mv "$tmp" "$dest/$s"
        installed+=("$side/$s")
    done
done

# verify: an account whose skills/ is a whole-folder symlink to shared/ already sees everything;
# otherwise (every account on a fresh volume, Claude and Codex alike) create one relative symlink
# per skill, same as the wrapper's link_shared_skills does on first use
problems=0
declare -a linked=()
for acct in "$BASE"/.Claude/yolo*/ "$BASE"/.Codex/cyolo*/; do
    [ -d "$acct" ] || continue
    acct="${acct%/}"; name="$(basename "$acct")"
    case "$name" in yolo[0-9]*|cyolo[0-9]*) ;; *) continue ;; esac
    for s in "${skills[@]}"; do
        if [ ! -e "$acct/skills/$s" ] && [ ! -L "$acct/skills/$s" ] && [ ! -L "$acct/skills" ]; then
            mkdir -p "$acct/skills"
            ln -s "../../shared/skills/$s" "$acct/skills/$s"
            linked+=("$name/$s")
        fi
        if [ ! -r "$acct/skills/$s/SKILL.md" ]; then
            echo "  ✗ $name มองไม่เห็น $s/SKILL.md" >&2
            problems=$((problems + 1))
        fi
    done
done

n_acct=$(ls -d "$BASE"/.Claude/yolo[0-9]* "$BASE"/.Codex/cyolo[0-9]* 2>/dev/null | wc -l)
echo "ติดตั้งสกิล: ${skills[*]}"
echo "  ปลายทาง: $BASE/.Claude/shared/skills และ $BASE/.Codex/shared/skills"
echo "  เขียนใหม่: ${installed[*]:-ไม่มี}"
echo "  เหมือนเดิม (ข้าม): ${unchanged[*]:-ไม่มี}"
if [ ${#backed[@]} -gt 0 ]; then echo "  สำรองของเดิมไว้ที่: $BACKUP (${backed[*]})"; else echo "  สำรอง: ไม่ต้องสำรอง"; fi
[ ${#linked[@]} -gt 0 ] && echo "  สร้าง symlink รายสกิล: ${linked[*]}"
if [ "$problems" -eq 0 ]; then
    echo "  ตรวจแล้ว: ทั้ง $n_acct บัญชีมองเห็น SKILL.md ของทั้ง ${#skills[@]} สกิล"
else
    echo "  ตรวจแล้ว: พบปัญหา $problems จุด" >&2
    exit 1
fi
