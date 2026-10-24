#!/usr/bin/env bash
# maccount.sh — เตรียม container multi-account-devtool (ขั้น 1–4 ของ SKILL.md) ในคำสั่งเดียว
#   bash maccount.sh             ข้อ 1–4: เช็ก → (ใช้ตัวเดิมถ้าค่าไม่เปลี่ยน | rm -f + docker run) → sync+ตรวจ skill + ตรวจล็อกอิน → เช็ก Jupyter ท้ายสุด
#   bash maccount.sh --recreate  บังคับ rm -f แล้วสร้างใหม่ แม้ค่าไม่เปลี่ยน (volume ai-accounts ไม่ถูกลบ)
#                                ยังไม่มี image → เริ่ม pull เบื้องหลัง พิมพ์ NOTICE แล้วออกด้วย exit 10
#   bash maccount.sh --wait-pull ใช้หลังได้ exit 10: รอ pull ให้เสร็จแล้วทำต่อจนจบ
#   bash maccount.sh check       ข้อ 1 อย่างเดียว (ไม่สร้าง container)
# พิมพ์เฉพาะชื่อตัวแปร/สถานะ — ไม่พิมพ์ค่าใน env (ยกเว้น LOCAL_SKILLS_DIR) และไม่พิมพ์เนื้อหา SKILL.md
# ใช้ได้ทุก OS ที่มี bash (Windows = Git Bash, macOS = bash 3.2 ที่ติดเครื่อง, Linux)
#
# ความเร็ว: บน Docker Desktop ทุกคำสั่ง docker เสีย ~300 ms → เรียก docker ให้น้อยที่สุดและขนานกันเมื่อทำได้
#   docker ps 1 ครั้ง (ใช้ทั้งเช็ก container และ port) · docker exec 1 ครั้ง (รอ installer + skill + ล็อกอิน 10 บัญชีขนานกัน)
#   ใช้ container ตัวเดิม: ป้าย maccount.fp = cksum(image ID + path/เนื้อหาไฟล์ env + mount local skill + MACCOUNT_PORT)
#   ตรงกับรอบนี้ → ไม่ rm/run ไม่ต้องรอ Jupyter บูต (ข้ามได้ ~2 วิ) · skill ยัง sync และล็อกอินยังตรวจทุกครั้ง

# ---- ตั้งค่า ----------------------------------------------------------------------
# path ไฟล์ env สำรองของ skill: ใช้เมื่อไม่พบ .env ในโฟลเดอร์ปัจจุบัน (ไม่มีไฟล์นี้ = ข้าม)
# แก้ที่บรรทัด ENV_FILE_WINDOWS= / ENV_FILE_MACOS= / ENV_FILE_LINUX= บนสุดของ SKILL.md (เลือกตาม OS เอง)
# หรือ override ด้วย MACCOUNT_ENV_FILE=<path>
cfg() { sed -n "s/^$1=//p" "$(dirname "$0")/SKILL.md" | head -1 | tr -d '\r' | sed -e 's/[[:space:]]*$//' -e 's/^["'\'']//' -e 's/["'\'']$//'; }
case "$(uname -s)" in
  MINGW*|MSYS*|CYGWIN*) OS=windows; DEFAULT_ENV_FILE=$(cfg ENV_FILE_WINDOWS) ;;
  Darwin)               OS=macos;   DEFAULT_ENV_FILE=$(cfg ENV_FILE_MACOS) ;;
  *)                    OS=linux;   DEFAULT_ENV_FILE=$(cfg ENV_FILE_LINUX) ;;
esac
N=${MACCOUNT_NAME:-multi-account-devtool}
IMG=tuchsanai/multi-account-devtool:2569_1
JUP0=${MACCOUNT_PORT:-8886}
# -------------------------------------------------------------------------------

export MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL="*"   # Git Bash: ห้ามแปลง /workspace เป็น path Windows
MODE=${1:-run}
abspath() { (cd "$1" 2>/dev/null && { pwd -W 2>/dev/null || pwd; }); }   # Git Bash ได้ C:/... ที่ docker เข้าใจ
ms() { local t; t=$(date +%s%N 2>/dev/null); case $t in *[!0-9]*|'') t=$(date +%s)000 ;; esac; echo $(( ${t:0:13} )); }   # macOS (BSD date) ไม่มี %N
T0=$(ms); lap() { echo "TIME $1 $(( $(ms) - T0 ))ms"; }

# ---- env: .env ในโฟลเดอร์ปัจจุบัน → DEFAULT_ENV_FILE → .env_example / .env.example → ไม่ใส่ ----
ENV_FILE=; ENV_KIND=
pick_env() {
  local d f; d=$(abspath .)
  if [ -f .env ]; then ENV_FILE="$d/.env"; ENV_KIND=cwd; return; fi
  f=${MACCOUNT_ENV_FILE:-$DEFAULT_ENV_FILE}; f=${f/#\~/$HOME}
  if [ -n "$f" ] && [ -f "$f" ]; then ENV_FILE="$(abspath "$(dirname "$f")")/$(basename "$f")"; ENV_KIND=skill; return; fi
  for f in .env_example .env.example; do [ -f "$f" ] && { ENV_FILE="$d/$f"; ENV_KIND=example; return; }; done
}
env_val() { grep -E "^[[:space:]]*$1=" "$ENV_FILE" | tail -1 | cut -d= -f2- | tr -d '\r' | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e 's/^["'\'']//' -e 's/["'\'']$//'; }
is_placeholder() { [ -z "$1" ] || [[ "$1" == \<* ]] || [[ "$1" =~ (/path/to|your[_-]|xxx|changeme) ]]; }

# ---- local skill จาก LOCAL_SKILLS_DIR (relative นับจากโฟลเดอร์ของไฟล์ env) ----
LS_MOUNT=(); LS_DESC="ไม่ได้กำหนด"
pick_local_skills() {
  [ -n "$ENV_FILE" ] || return
  local v p; v=$(env_val LOCAL_SKILLS_DIR)
  is_placeholder "$v" && return
  case "$v" in /*|[A-Za-z]:*|~*) p=${v/#\~/$HOME} ;; *) p="$(dirname "$ENV_FILE")/$v" ;; esac
  if [ ! -d "$p" ]; then echo "WARN LOCAL_SKILLS_DIR=$v ไม่พบโฟลเดอร์"; return; fi
  p=$(abspath "$p")
  if [ -f "$p/SKILL.md" ]; then LS_MOUNT=(-v "$p:/opt/local-skills/$(basename "$p"):ro"); LS_DESC="$p (skill เดี่ยว)"
  else LS_MOUNT=(-v "$p:/opt/local-skills:ro"); LS_DESC="$p (โฟลเดอร์รวม skill)"; fi
}

report_env() {
  case "$ENV_KIND" in
    cwd)     echo "ENV $ENV_FILE (.env ในโฟลเดอร์ปัจจุบัน)" ;;
    skill)   echo "ENV $ENV_FILE (path ที่ตั้งไว้ใน skill — ไม่พบ .env ในโฟลเดอร์ปัจจุบัน)" ;;
    example) echo "ENV $ENV_FILE"
             echo "WARN ไม่พบ .env — ใช้ $(basename "$ENV_FILE") แทน กรุณา copy เป็น .env แล้วใส่ค่าจริง" ;;
    *)       echo "ENV none"
             echo "WARN ไม่พบ .env หรือ .env_example — container จะไม่มี environment variable"; return ;;
  esac
  # ชื่อตัวแปรเท่านั้น + ตัวที่ว่าง/เป็นค่าตัวอย่าง (ไม่พิมพ์ค่า)
  awk -F= '/^[[:space:]]*[A-Za-z_][A-Za-z0-9_]*=/{n=$1; gsub(/[[:space:]]/,"",n); v=substr($0,index($0,"=")+1); gsub(/\r|^[[:space:]]+|[[:space:]]+$/,"",v)
      names=names" "n
      if(v=="" || v=="\"\"" || v=="\047\047") empty=empty" "n
      else if(n!="LOCAL_SKILLS_DIR" && tolower(v) ~ /(\/path\/to|^<|your[_-]|xxx|changeme|example)/) ex=ex" "n }
    END{print "VARS" names; if(empty!="") print "EMPTY" empty; if(ex!="") print "PLACEHOLDER" ex}' "$ENV_FILE"
}

# ---- ข้อ 1: เช็ก image + container + port ด้วย docker 2 คำสั่งที่รันขนานกัน ----
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
docker image inspect -f '{{.Id}}' "$IMG" >"$TMP/img" 2>/dev/null &
PS=$(docker ps -a --format '{{.Names}}|{{.State}}|{{.Ports}}|{{.Label "maccount.fp"}}')
LISTEN=$({ netstat -an 2>/dev/null || ss -ltn 2>/dev/null; } | grep -i listen | grep -oE '[:.][0-9]+ ' | tr -d ':. ')
wait
ST=$(awk -F'|' -v n="$N" '$1==n{print $2}' <<<"$PS")
OLDFP=$(awk -F'|' -v n="$N" '$1==n{print $4}' <<<"$PS")
OWN=$(awk -F'|' -v n="$N" '$1==n{print $3}' <<<"$PS" | grep -oE ':[0-9]+->' | sed 's/[^0-9]//g' | sort -u)
USED=" $( { awk -F'|' -v n="$N" '$1!=n && $2=="running"{print $3}' <<<"$PS" | grep -oE ':[0-9]+->' | sed 's/[^0-9]//g'
            grep -vxF -f <(echo "${OWN:-none}") <<<"$LISTEN"; } | sort -u | tr '\n' ' ') "
free_port() { local p=$1; while [[ "$USED" == *" $p "* ]]; do p=$((p+1)); done; echo $p; }
JUP=$(free_port "$JUP0")

pick_env
echo "OS $OS ($(uname -s)) | shell bash $BASH_VERSION"
[ -n "$DEFAULT_ENV_FILE" ] && [ ! -f "${DEFAULT_ENV_FILE/#\~/$HOME}" ] && echo "WARN ไม่พบไฟล์ ENV_FILE_$(echo $OS | tr a-z A-Z) ที่ตั้งไว้ใน SKILL.md: $DEFAULT_ENV_FILE"
[ -s "$TMP/img" ] && echo "IMAGE present"
report_env
pick_local_skills
echo "LOCAL_SKILLS $LS_DESC"

# ลายนิ้วมือของค่าที่ใช้สร้าง container — ตรงกับป้ายของตัวเดิม = ใช้ตัวเดิมได้
FP=$( { echo "$(cat "$TMP/img")|$ENV_FILE|${LS_MOUNT[*]}|${MACCOUNT_PORT:-}"; [ -n "$ENV_FILE" ] && cat "$ENV_FILE"; } | cksum | cut -d' ' -f1)
REUSE=
if [ -z "$ST" ]; then echo "CONTAINER none"
elif [ "$MODE" = --recreate ]; then echo "CONTAINER $N exists ($ST) → --recreate: docker rm -f แล้วสร้างใหม่ (volume ai-accounts ไม่ถูกลบ)"
elif [ -s "$TMP/img" ] && [ "$OLDFP" = "$FP" ]; then REUSE=1; echo "CONTAINER $N exists ($ST) → REUSE ค่าไม่เปลี่ยน ใช้ตัวเดิม"
elif [ -z "$OLDFP" ]; then echo "CONTAINER $N exists ($ST) → ไม่มีป้าย maccount.fp (สร้างจากที่อื่น) → docker rm -f แล้วสร้างใหม่ (volume ai-accounts ไม่ถูกลบ)"
else echo "CONTAINER $N exists ($ST) → ค่าเปลี่ยน (image/env/local skill/port) → docker rm -f แล้วสร้างใหม่ (volume ai-accounts ไม่ถูกลบ)"; fi
[ -n "$REUSE" ] && JUP=$(head -1 <<<"$OWN")
[ -n "$JUP" ] && echo "PORT $JUP"   # container ที่หยุดอยู่ยังไม่รู้ port — พิมพ์หลัง docker start

if [ ! -s "$TMP/img" ]; then
  if [ "$MODE" = --wait-pull ]; then
    echo "IMAGE pulling (รอให้เสร็จ)"; docker pull -q "$IMG" >/dev/null || { echo "FAIL docker pull $IMG"; exit 1; }
  else
    nohup docker pull "$IMG" >"${TMPDIR:-/tmp}/maccount-pull.log" 2>&1 &
    echo "IMAGE pulling (background, log ${TMPDIR:-/tmp}/maccount-pull.log)"
    echo "NOTICE ⏳ ยังไม่มี image ในเครื่อง กำลังดาวน์โหลด (~4.5 GB) ครั้งแรกอาจใช้หลายนาที กรุณารอสักครู่"
    exit 10
  fi
fi
[ "$MODE" = check ] && exit 0
lap check

# ---- ข้อ 2: ใช้ตัวเดิม (หยุดอยู่ → docker start) หรือ rm -f → docker run ----
if [ -n "$REUSE" ] && [ "$ST" != running ]; then
  # container ที่หยุดอยู่ docker ps ไม่แสดง port → อ่าน port ใหม่หลัง start
  if docker start "$N" >/dev/null 2>&1; then
    JUP=$(docker port "$N" 8888/tcp 2>/dev/null | head -1 | sed 's/.*://'); echo "STARTED $N"; echo "PORT $JUP"
  fi
  [ -n "$JUP" ] || { echo "WARN docker start ไม่ขึ้น → สร้างใหม่"; REUSE=; JUP=$(free_port "$JUP0"); }
fi
if [ -z "$REUSE" ]; then
[ -n "$ST" ] && docker rm -f "$N" >/dev/null 2>&1
[ -n "$ENV_FILE" ] && ENV_ARGS=(--env-file "$ENV_FILE") || ENV_ARGS=()
RUN_OK=
for try in $(seq 20); do
  OUT=$(docker run -dit --name "$N" --label "maccount.fp=$FP" --privileged -w /workspace -p "$JUP:8888" "${ENV_ARGS[@]}" \
        -v ai-accounts:/root/ai-accounts "${LS_MOUNT[@]}" "$IMG" 2>&1) && { RUN_OK=1; break; }
  if echo "$OUT" | grep -qiE 'ports are not available|address already in use|port is already allocated|forbidden by its access permissions|bind: permission denied'; then
    docker rm -f "$N" >/dev/null 2>&1; USED="$USED$JUP "; JUP=$(free_port $((JUP+1)))
    echo "RETRY port ถูกใช้/สงวน → ลอง $JUP"
  else echo "FAIL docker run"; echo "$OUT" | tail -5; exit 1; fi
done
[ -n "$RUN_OK" ] || { echo "FAIL docker run (หา port ว่างไม่ได้)"; echo "$OUT" | tail -3; exit 1; }
echo "CREATED $N"; echo "PORT $JUP"
fi
lap run

# ---- ข้อ 3–4: docker exec ครั้งเดียว — รอ installer → login 10 บัญชีขนานกัน + sync/ตรวจ skill ----
[ ${#LS_MOUNT[@]} -gt 0 ] && echo "LOCAL_SKILLS_MOUNTED yes" || echo "LOCAL_SKILLS_MOUNTED no"
docker exec -e MACCOUNT_JOBS="${MACCOUNT_JOBS:-}" "$N" bash -lc '
for i in $(seq 300); do grep -qs "done:" /var/log/ai-accounts-setup.log && break; sleep 0.1; done
[ $i = 300 ] && echo "WARN ai-accounts-setup ยังไม่เสร็จใน 30 วิ (ผลตรวจ skill/ล็อกอินอาจไม่ครบ)"
L=$(mktemp -d); A="yolo1 yolo2 yolo3 yolo4 yolo5 cyolo1 cyolo2 cyolo3 cyolo4 cyolo5"
# ตรวจล็อกอินขนาน: worker = จำนวน core แต่อยู่ในช่วง 2–4 เสมอ · override ด้วย MACCOUNT_JOBS (ถูกบีบให้อยู่ในช่วงเดียวกัน)
# วัดจริง: เร็วขึ้นตามจำนวน worker จนเท่ากับ core แล้วนิ่ง (เกิน core ไม่เร็วขึ้น)
P=${MACCOUNT_JOBS:-$(nproc)}; [ "$P" -lt 2 ] && P=2; [ "$P" -gt 4 ] && P=4
echo "LOGIN_WORKERS $P (cores $(nproc))"
export L
chk() { case $1 in yolo*) $1 auth status 2>/dev/null | grep -q loggedIn.:.true ;; *) $1 login status 2>&1 | grep -q ^Logged.in ;; esac && echo $1 LOGGED_IN > $L/$1 || echo $1 NOT_LOGGED_IN > $L/$1; }
export -f chk
echo $A | xargs -n1 -P$P bash -c "chk \"\$0\"" &
echo "--- SKILLS"
B=$HOME/ai-accounts; K=/tmp/skills.txt; echo vastai yolo cyolo > $K; n=0; for d in /opt/local-skills/*/; do [ -d $d ] || continue; s=$(basename $d); if [ ! -f $d/SKILL.md ]; then echo SKIP $s no-SKILL.md; continue; fi; if [ $s = shared-check ]; then echo SKIP $s reserved; continue; fi; for t in .Claude .Codex; do rm -rf $B/$t/shared/skills/$s; cp -rL $d $B/$t/shared/skills/$s; done; echo SYNCED $s; n=$((n+1)); echo $s >> $K; done; echo TOTAL $n; for t in .Claude .Codex; do for s in $(xargs -n1 < $K | sort -u); do [ -d $B/$t/shared/skills/$s ] && echo $t/$s OK || echo $t/$s MISSING; done; done
wait
echo "--- LOGIN"
for a in $A; do cat $L/$a; done; rm -rf $L'
lap skills+login

# ---- เช็ก Jupyter ตอนท้ายสุด (ทุก 0.25 วิ สูงสุด 5 นาที) ----
OK=; for i in $(seq 1200); do
  [ "$(curl -s -m 3 -o /dev/null -w '%{http_code}' "http://localhost:$JUP/lab")" = 200 ] && { OK=1; break; }
  [ $((i % 40)) = 0 ] && { [ "$(docker inspect -f '{{.State.Running}}' "$N" 2>/dev/null)" = true ] || { echo "FAIL container หยุดทำงาน"; docker logs --tail 10 "$N"; exit 1; }; }
  sleep 0.25
done
echo "--- JUPYTER"
[ -n "$OK" ] && echo "JUPYTER 200" || echo "WARN Jupyter ไม่ตอบ 200 ภายใน 5 นาที"
lap total
