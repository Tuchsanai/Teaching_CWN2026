#!/usr/bin/env bash
# ทดสอบแชทบอทครบ 26 เคสในคำสั่งเดียว (รันใน Linux container, รันซ้ำได้)
#   bash run-all.sh
# ตัวแปรที่ปรับได้:  BASE_URL (ค่าเริ่มต้น http://localhost:3300)  WORKERS (ค่าเริ่มต้น 2)
# ผลลัพธ์อยู่ใน out/ : TEST_REPORT.md, results.json, gifs/, videos/, answers/
set -u
cd "$(dirname "$0")"
export BASE_URL="${BASE_URL:-http://localhost:3300}"
FRONTEND_DIR="../frontend"

step() { echo; echo "== $* =="; }

# ลองซ้ำได้ 6 ครั้ง (เผื่อ apt ถูกโปรแกรมอื่นล็อกอยู่)
retry() {
  for i in 1 2 3 4 5 6; do
    "$@" && return 0
    echo "ไม่สำเร็จ (ครั้งที่ $i) รอ 20 วินาทีแล้วลองใหม่: $*"
    sleep 20
  done
  return 1
}

step "1/6 ติดตั้งเครื่องมือ (ครั้งแรกเท่านั้น)"
if [ ! -d node_modules/@playwright/test ]; then
  npm ci || exit 1
fi
# มี Chromium ของ Playwright รุ่นนี้แล้วหรือยัง
if ! node -e 'process.exit(require("fs").existsSync(require("@playwright/test").chromium.executablePath()) ? 0 : 1)'; then
  retry npx playwright install --with-deps chromium || exit 1
fi
if ! command -v ffmpeg >/dev/null; then
  retry apt-get -o DPkg::Lock::Timeout=300 update -qq
  retry apt-get -o DPkg::Lock::Timeout=300 install -y -qq ffmpeg || exit 1
fi
echo "พร้อม: playwright $(npx playwright --version | tail -1), $(ffmpeg -version | head -1 | cut -d' ' -f1-3)"

step "2/6 ตรวจว่าเว็บแชทบอทเปิดอยู่ที่ $BASE_URL"
ok=0
for i in $(seq 1 30); do
  if curl -fsS -o /dev/null "$BASE_URL"; then ok=1; break; fi
  sleep 2
done
if [ "$ok" != 1 ]; then
  echo "เปิด $BASE_URL ไม่ได้ — เริ่มเว็บก่อน:  cd $FRONTEND_DIR && docker compose up -d --build"
  exit 1
fi
echo "เว็บพร้อม"

step "3/6 ล้างตารางการจองและประวัติแชท"
if (cd "$FRONTEND_DIR" && docker compose exec -T db sh -c \
    'psql -q -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "TRUNCATE bookings, chat_messages RESTART IDENTITY"'); then
  echo "ล้างแล้ว"
else
  echo "ข้าม: ล้างตารางไม่ได้ (ฐานข้อมูลไม่ได้รันจากโฟลเดอร์ $FRONTEND_DIR) — เทสต์ยังรันต่อได้"
fi

step "4/6 รันเทสต์ 26 เคส (workers=${WORKERS:-2})"
rm -rf out test-results
START=$(date +%s)
npx playwright test || true   # มีเคสไม่ผ่านก็ไปต่อ เพื่อทำ GIF และรายงาน
echo "ใช้เวลารันเทสต์ $(( $(date +%s) - START )) วินาที"

step "5/6 ทำ GIF ของแต่ละเคส"
if node make-media.mjs; then
  rm -rf out/frames   # ภาพหน้าจอดิบกินที่มาก (หลายร้อย MB) ทำ GIF เสร็จแล้วลบได้
else
  echo "ทำ GIF ไม่สำเร็จ"
fi

step "6/6 เขียนรายงาน"
node make-report.mjs
exit 0
