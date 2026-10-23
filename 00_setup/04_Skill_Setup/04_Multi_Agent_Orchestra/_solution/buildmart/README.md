# บ้านช่าง BuildMart — เฉลย (`_solution/buildmart`)

เว็บร้านวัสดุก่อสร้าง + แชทบอท "น้องช่าง" ตามโจทย์ [`BUILDMART.md`](../../BUILDMART.md): Next.js 14 · PostgreSQL + pgvector · RabbitMQ · Hybrid RAG · อ่านออกเสียง (Kokoro + PyThaiTTS) · LLM Qwen บน Vast.ai หรือ mock-llm
สัญญากลางของทีม (ชื่อคิว · API · data-testid) อยู่ใน [`CONTRACT.md`](CONTRACT.md)

## รัน

```bash
# ฟรี (mock-llm ไม่ต้องเช่า GPU)
docker compose -p buildmart --profile mock up -d --build
# + เสียงอ่าน (kokoro + tts-worker · CPU)
docker compose -p buildmart --profile mock --profile tts up -d --build
# AI จริง: วาง .env.vast (LLM_BASE_URL / LLM_MODEL / LLM_API_KEY) แล้ว — วิธีเปิด Qwen บน Vast: ../vast_qwen/README.md
docker compose -p buildmart up -d --build
```

| URL | |
|---|---|
| http://localhost:3400 | หน้าร้าน (แชทบอทปุ่มลอยมุมขวาล่าง) |
| http://localhost:3400/admin | หลังร้าน · รหัส dev `admin1234` · `/admin/docs` จัดการ PDF ของ RAG |
| http://localhost:15672 | RabbitMQ Management (`guest/guest` ใช้ในเครื่องเท่านั้น) |

รีเซ็ตข้อมูลทั้งหมด: `docker compose -p buildmart down -v` แล้ว up ใหม่ (seed + ingest PDF ใหม่อัตโนมัติ)

## โครงสร้าง

| โฟลเดอร์ | หน้าที่ |
|---|---|
| `web/` | Next.js หน้าร้าน + API (ไม่เรียก LLM ตรง — ส่งงานเข้าคิว `chat.request` แล้วรอทาง SSE) |
| `workers/` | `chat-worker` (context สินค้า + Hybrid RAG + tag `[CALC]` `[ADD_TO_CART]` `[QUOTE]`) · `rag-worker` (PDF → chunk → vector) · `notify-worker` (`order.events` → แจ้งเตือนหลังร้าน) |
| `shared/` | สูตรราคา/ค่าส่ง/VAT และเครื่องคำนวณวัสดุ ใช้ร่วมทั้ง web และ workers (`node shared/selftest.mjs`) |
| `db/` | schema + seed สินค้า 36 รายการ · 3 สาขา · คูปอง |
| `docs/` | PDF 6 ไฟล์ (แหล่งข้อมูลของ RAG) + ต้นฉบับ HTML · `tests/fixtures/BM-PROMO-NOV.pdf` ไฟล์ทดสอบอัปโหลด |
| `mock-llm/` | LLM จำลองแบบ deterministic (OpenAI-compatible) |
| `tts/` | tts-worker (ไทย PyThaiTTS · อังกฤษส่งต่อ Kokoro) |
| `e2e/` | Playwright "เพลย์ลิสต์" 42 เคส + วิดีโอ MP4/GIF + `TEST_REPORT.md` — ดู [`e2e/README.md`](e2e/README.md) |

## ทดสอบ

```bash
cd e2e
npm ci && npx playwright install chromium
BM_TTS=1 npm run playlist     # โหมด mock (+ กลุ่มเสียงถ้าเปิด profile tts)
npm run media && npm run report
```

ผลล่าสุด (23 ต.ค. 2026): **mock 42/42 · AI จริง (Qwen3.8-27B บน Vast.ai RTX 5090) 42/42** → [`e2e/TEST_REPORT.md`](e2e/TEST_REPORT.md) · วิดีโอ `e2e/test-videos/<เคส>.mp4` · GIF `e2e/test-gifs/<เคส>.gif`
