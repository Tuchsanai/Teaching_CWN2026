# e2e — Playwright "เพลย์ลิสต์" ทดสอบ BuildMart ทั้งระบบ

ทุกเคสในข้อ 7 ของ `BUILDMART.md` (W01–W14 · C01–C14 · R01–R08 · Q01–Q03 · T01–T03 รวม 42 เคส · R08 เล่นก่อน R07 เพราะ R07 อัปโหลด/ลบเอกสาร) เล่นตามลำดับใน `playlist.json`
ทีละเคส (workers 1) · อัดวิดีโอ 1280×800 ทุกเคส → MP4 + GIF · สรุปผลเป็น `TEST_REPORT.md`

## เริ่มใช้

```bash
# ต้องมี stack รันอยู่ก่อน (จากโฟลเดอร์ buildmart/)
docker compose -p buildmart --profile mock up -d --build
docker compose -p buildmart --profile mock --profile tts up -d     # ถ้าจะรันกลุ่ม T (เสียง)

cd e2e
npm ci && npx playwright install chromium
```

## คำสั่ง

| คำสั่ง | ทำอะไร |
|---|---|
| `npm run playlist` | รันทั้งเพลย์ลิสต์โหมด mock (กลุ่ม T ข้าม) → `results.json` + วิดีโอใน `test-results/` |
| `BM_MODE=ai BM_TTS=1 npm run playlist` | โหมด AI จริง (ตรวจแบบยืดหยุ่น) + กลุ่ม T |
| `npm run media` | วิดีโอ → `test-videos/<id>.mp4` (H.264 CRF 28 · กว้าง 1280 · faststart · เคส T มีเสียง) + `test-gifs/<id>.gif` (กว้าง 800 · 6 fps · 96 สี · ≲ 2.5 MB/ไฟล์) · ถ้า webm หาย (รัน `BM_ONLY` ทีหลัง Playwright ล้าง `test-results/`) จะทำ GIF ใหม่จาก MP4 เดิม |
| `npm run report` | `TEST_REPORT.<mode>.md` + รวมทุกโหมดเป็น `TEST_REPORT.md` |
| `BM_ONLY=R npm run playlist` | รันเฉพาะกลุ่ม R (หรือ `BM_ONLY=W01,C07` เฉพาะบางเคส) |
| `npx playwright test -g " R\d\d "` | เหมือนข้างบนด้วย grep ของ Playwright |

> `npx playwright test -g "^R"` **หาไม่เจอ** เพราะ Playwright เอาชื่อไฟล์ (`3-rag.spec.ts`) ไปต่อหน้าชื่อ test ก่อน grep
> ให้ใช้ `-g " R\d\d "` หรือ `BM_ONLY=R` แทน

บน PowerShell ตั้ง env แบบ `$env:BM_MODE='ai'; $env:BM_TTS='1'; npm run playlist`

## ตัวแปร

| env | ค่าเริ่มต้น | ความหมาย |
|---|---|---|
| `BM_URL` | `http://localhost:3400` | เว็บที่ทดสอบ (และที่ดาวน์โหลด WAV ตอนทำ media) |
| `BM_MODE` | `mock` | `mock` = ตรวจตัวเลข/คำตรงตัว · `ai` = ตรวจ "มีตัวเลข/คำสำคัญที่ถูกต้อง" (ยอม comma 7,120/7120 · เลขไทย · `21ถุง` · รูปแบบเวลา · คำปฏิเสธตามความหมาย) · รอคำตอบ ≤ 120 วิ (Q01 ≤ 240 วิ) · เคส R ต้องมี cite ไฟล์ที่ถูกทุกโหมด |
| `BM_GIF_WIDTH` `BM_GIF_FPS` `BM_GIF_COLORS` `BM_MP4_CRF` | 800 · 6 · 96 · 28 | ปรับขนาด/คุณภาพสื่อใน `make-media.mjs` |
| `BM_TTS` | – | `1` = รันกลุ่ม T (ต้องเปิด profile `tts`) |
| `BM_ONLY` | – | `R` / `W01,C07` เลือกกลุ่มหรือเคส |
| `BM_HOLD_MS` | `3500` | เวลาค้างภาพหลังผลแต่ละขั้น (3–5 วิ) |
| `BM_ADMIN_PASSWORD` | `admin1234` | รหัสหลังร้าน (ค่า dev) |
| `BM_MQ_URL` `BM_MQ_USER` `BM_MQ_PASS` | `http://localhost:15672` guest/guest | RabbitMQ Management (ค่า dev ในเครื่อง) ใช้ใน Q01/Q02 |

## โครงสร้าง

```
playlist.json          รายการเคสตามลำดับเล่น (id · group · title · what · expect)
playwright.config.ts   viewport 1280x800 · video on · workers 1 · JSON reporter → results.json
global-setup.ts        รอ /api/health ก่อนเริ่ม
tests/_bm.ts           fixture (ป้ายมุมจอ · การ์ดเปิดเคส · คำบรรยาย) + typeHuman / hold / show / ask
tests/_shop.ts         ขั้นตอนหน้าร้านที่ใช้ซ้ำ (ใส่ตะกร้า · checkout · track)
tests/1-web … 5-tts    1 test ต่อเคส ชื่อขึ้นต้นด้วย id
make-media.mjs         webm → mp4/gif (ffmpeg-static) · เคส T รวม WAV ด้วย adelay=offsetMs · ตรวจ audio stream
make-report.mjs        results.json + media.json → TEST_REPORT*.md
```

## เทคนิควิดีโอ (ให้คนดูทัน)

- พิมพ์ทีละตัว `pressSequentially(delay 60ms)` · ค้างภาพ 3–5 วิหลังผลแต่ละขั้น · ไฮไลต์ element ที่ตรวจด้วยกรอบสีส้มชั่วคราว
- ทุกเคสมีการ์ดเปิด (ทำอะไร / ผ่านเมื่อ) 3 วิ · ป้ายมุมจอ `R01 · ปูนเก็บได้นานแค่ไหน` · คำบรรยายล่างจอ
- เคส T: ChatWidget บันทึก `window.__bmAudioLog` ตอนเริ่มเล่น → เทสต์คำนวณ `offsetMs = performance.timeOrigin + startedAt − เวลาเริ่มวิดีโอ`
  แล้ว attach `{audioId, offsetMs, durationMs}` → `make-media.mjs` ดึง `/api/tts/<audioId>` มารวมเข้า MP4 ตรงจังหวะ
- Q01 เปิด 8 browser context ถามพร้อมกัน วิดีโอหลักแสดงตาราง 8 คำตอบแบบสด + จำนวนข้อความในคิว แล้วเปิด RabbitMQ UI หน้า `chat.request` ให้เห็น consumer
- Q02 สั่ง `docker compose -p buildmart stop chat-worker` (finally start กลับเสมอ)

## ข้อมูลที่เทสต์สร้าง

ทุกเคสใช้ browser context ใหม่ (= session/ตะกร้าใหม่) · คำสั่งซื้อจริงใน W12/W14/Q03 ตัดสต็อกจริง (Q03 เลือก SKU/สาขาที่ใกล้จุดสั่งซื้อซ้ำเองจาก API) ·
R07 ลบ `BM-PROMO-NOV.pdf` ทิ้งตอนจบเสมอ · อยากรีเซ็ตข้อมูลทั้งหมด: `docker compose -p buildmart down -v` แล้ว up ใหม่
