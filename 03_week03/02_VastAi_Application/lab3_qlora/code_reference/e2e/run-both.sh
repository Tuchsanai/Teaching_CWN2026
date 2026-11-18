#!/usr/bin/env bash
# รันชุดทดสอบ 26 เคสเดิมกับโมเดล Base แล้วกับ Fine-tuned (ไม่แก้ cases.json / tests/)
#   bash run-both.sh
# ตัวแปรที่ปรับได้: BASE_URL (ค่าเริ่มต้น http://host.docker.internal:3403) · WORKERS (2) · REPEAT (5) · SKIP_UI=1 (ข้ามรอบเบราว์เซอร์)
# ผลลัพธ์: out-base/ out-ft/ (รายงาน + GIF ของแต่ละโมเดล) · repeat.json · compare.json · COMPARE.md
set -u
cd "$(dirname "$0")"
export BASE_URL="${BASE_URL:-http://host.docker.internal:3403}"
REPEAT="${REPEAT:-5}"

step() { echo; echo "######## $* ########"; }

# สลับโมเดลเริ่มต้นของเว็บ แล้วตรวจว่าเปลี่ยนจริง
switch_model() {
  curl -fsS -X PUT "$BASE_URL/api/model" -H 'Content-Type: application/json' -d "{\"model\":\"$1\"}" >/dev/null || return 1
  local now
  now=$(curl -fsS "$BASE_URL/api/model" | node -e 'let s="";process.stdin.on("data",d=>s+=d).on("end",()=>console.log(JSON.parse(s).default))')
  [ "$now" = "$1" ] || { echo "สลับโมเดลไม่สำเร็จ (ตอนนี้ $now)"; return 1; }
  echo "โมเดลเริ่มต้นของเว็บ = $1"
}
# ล้างตารางจองและประวัติแชท (ผ่าน API ของเว็บ เพราะ container นี้เข้า PostgreSQL ตรงไม่ได้)
reset_db() { curl -fsS -X POST "$BASE_URL/api/reset" && echo; }

model_name() {
  curl -fsS "$BASE_URL/api/model" | node -e 'let s="";process.stdin.on("data",d=>s+=d).on("end",()=>{const j=JSON.parse(s);console.log(j.models.find(m=>m.key===process.argv[1]).name)})' "$1"
}

if [ "${SKIP_UI:-0}" != 1 ]; then
  for m in base ft; do
    step "รอบเบราว์เซอร์ · โมเดล $m"
    switch_model "$m" || exit 1
    reset_db || exit 1
    # run-all.sh เดิม: ติดตั้ง Playwright → ตรวจเว็บ → รัน 26 เคส → GIF → รายงาน (ข้ามขั้นล้างตารางของมันเอง เพราะล้างไปแล้วด้านบน)
    LLM_MODEL="$(model_name "$m")" LLM_BASE_URL="$(grep ^OPENAI_BASE_URL= ../../chatbot.env 2>/dev/null | cut -d= -f2-)" bash run-all.sh
    rm -rf "out-$m" && mv out "out-$m"
    rm -rf "out-$m/videos" test-results   # วิดีโอเต็มไม่ใช้ (มี GIF แล้ว)
    echo "รายงาน: out-$m/TEST_REPORT.md · $(node -e 'const r=require("./out-'"$m"'/results.json");console.log(r.passed+"/"+r.total+" ผ่าน")')"
  done
fi

step "รันซ้ำ $REPEAT รอบต่อโมเดล ผ่าน API ของเว็บ (ไม่เปิดเบราว์เซอร์)"
REPEAT="$REPEAT" node repeat.mjs || exit 1

step "เทียบผล"
node compare.mjs
reset_db >/dev/null
switch_model ft   # คืนค่าเริ่มต้นของเว็บเป็น Fine-tuned
