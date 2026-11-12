# บ้านช่าง BuildMart v3 — เฉลย (`_solution/buildmart`)

เว็บร้านวัสดุก่อสร้าง 3D + แชทบอท "น้องช่าง" ที่ฟังและพูดได้ ตามโจทย์ [`BUILDMART.md`](../../BUILDMART.md): Next.js 14 + Three.js · PostgreSQL + pgvector · RabbitMQ · Hybrid RAG + reranker · Whisper (ฟัง) · VoxCPM2 (พูด) · Qwen บน Vast.ai — หรือ `mock-llm` แทน GPU ทั้งหมด (ฟรี)
สัญญากลางของทีม (ชื่อคิว · API · data-testid): [`CONTRACT.md`](CONTRACT.md) + ส่วนเพิ่ม v3 [`CONTRACT_V3.md`](CONTRACT_V3.md) · วิธีใช้ทั้ง LAB: [readme หลัก](../../readme.md)

## รัน — `docker compose` คำสั่งเดียว (ที่โฟลเดอร์นี้)

```bash
# ① ฟรี (mock): mock-llm แทน LLM + STT + TTS + rerank · เสียงตอบ = เสียง VoxCPM2 ที่อัดไว้แล้ว
docker compose -p buildmart --profile mock up -d --build

# ② AI จริง (GPU 3 ใบบน Vast.ai): วาง 2 ไฟล์ไว้ที่โฟลเดอร์นี้ก่อน แล้ว (ไม่ใส่ --profile mock)
#    .env.vast  = LLM_BASE_URL / LLM_MODEL / LLM_API_KEY          ← ../vast_qwen/README.md  (GPU-1 RTX 5090)
#    .env.aibox = STT_URL / TTS_URL / RERANK_URL / AIBOX_API_KEY  ← ../vast_aibox/README.md (GPU-2/3 RTX 4090 × 2)
docker compose -p buildmart up -d --build

# ขยาย worker (RabbitMQ แจกงาน round-robin) · ปรับ prefetch ด้วย env CHAT_PREFETCH / STT_PREFETCH / TTS_PREFETCH
docker compose -p buildmart up -d --scale chat-worker=2
# ปิด reranker (ใช้เทียบในการประเมิน): ตั้ง RERANK=off ใน .env แล้ว up -d chat-worker
```

- มีแค่ `.env.vast` (ไม่มี `.env.aibox`) = แชทใช้ Qwen จริง แต่ฟัง/พูด/rerank ใช้ mock · ค่าอื่นที่ตั้งได้ดู [`.env.example`](.env.example)
- build ครั้งแรก ~5–10 นาที (โมเดล embedding) · PDF มาจาก [`../../documents/`](../../documents/) ตอน build (6 ไฟล์ → 930 chunk)
- ตรวจโหมดจริง: `docker compose -p buildmart logs chat-worker | grep mode` → `mode=ai model=qwen3.8-27b rerank=on` · stt-worker `whisper` · tts-worker `voxcpm2`

| URL | |
|---|---|
| http://localhost:3400 | หน้าร้าน 3D (แชท + ไมค์ปุ่มลอยมุมขวาล่าง) |
| http://localhost:3400/admin | หลังร้าน · รหัส dev `admin1234` · `/admin/docs` PDF ของ RAG · **`/admin/eval`** ผลประเมิน · **`/admin/load`** ผล load test |
| http://localhost:15672 | RabbitMQ Management (`guest/guest` ใช้ในเครื่องเท่านั้น) |

รีเซ็ตข้อมูลทั้งหมด: `docker compose -p buildmart down -v` แล้ว up ใหม่ (seed + ingest PDF ใหม่อัตโนมัติ)

## ทดสอบ + วัดผล

**① เพลย์ลิสต์ Playwright 62 เคส** (W C R Q T M V D E L · วิดีโอ GIF/MP4 · [e2e/README.md](e2e/README.md))

```bash
cd e2e
npm ci && npx playwright install chromium
npm run playlist                     # mock (ระบบรันแบบ ①)
BM_MODE=ai npm run playlist          # AI จริง (ระบบรันแบบ ②) · PowerShell: $env:BM_MODE='ai'; npm run playlist
npm run media && npm run report      # → test-videos/*.mp4 (T/V มีเสียง) · test-gifs/*.gif · TEST_REPORT.md
```

**② ประเมิน RAG** 260 ข้อ (rag 169 · qa 79 · conv 12 บท/60 รอบ · [eval/README.md](eval/README.md) · ตัวชี้วัด [METRICS.md](eval/METRICS.md) · ผลจริง [RESULTS.md](eval/RESULTS.md) · [results.html](eval/results.html))

```bash
cd eval
node merge.mjs --strict                                          # รวม parts/ → qa.json
node run_eval.mjs --label ai-rerank-on --mode ai --rerank on     # ถามผ่าน /api/chat + /api/voice จริง
# … Claude ตัดสิน runs/<label>/judge_batches/batch-NN.md ตาม rubric ใน eval/README.md …
node score.mjs --label ai-rerank-on --post http://localhost:3400 # → results.json + /admin/eval
node make_report.mjs                                             # → RESULTS.md · results.html · SAMPLES.md
```

**③ Load test** 1 → 32 ผู้ใช้ (ผล `loadtest/results/<label>.json` → `/admin/load` · เกณฑ์ใน [`loadtest/config.json`](loadtest/config.json))

```bash
node loadtest/run_load.mjs --mode chat   --users 1,2,4,8,16,32 --stage-sec 60 --label ai-chat
node loadtest/run_load.mjs --mode stt    --users 1,2,4,8,16,32 --stage-sec 60 --label ai-stt
#   --mode tts | rerank | voice  · --url http://localhost:3400 · --aibox-env .env.aibox (โหมด rerank)
```

ผลล่าสุด (23 ต.ค. 2026 · AI จริง 3 GPU): ประเมิน rag ผ่าน **95.9%** (rerank off 88.8%) · qa 91.1% · conv 66.7% · load test แชท 4 คน · ฟัง 32 คน (prefetch 8) · พูด 2 คน · เสียง→เสียง 4 คน
เพลย์ลิสต์: ผล mock **62/62** · AI จริง **62/62** → [e2e/TEST_REPORT.md](e2e/TEST_REPORT.md) · [e2e/TEST_REPORT.ai.md](e2e/TEST_REPORT.ai.md)

selftest ที่ไม่ต้องรันทั้งระบบ: `node shared/selftest.mjs` (สูตรราคา/คำนวณ) · `node mock-llm/selftest.mjs` · `node workers/chat-selftest.mjs` · `node workers/rag-selftest.mjs`

## โครงสร้าง

| โฟลเดอร์ / ไฟล์ | หน้าที่ |
|---|---|
| `docker-compose.yml` | ทั้งระบบในไฟล์เดียว: db · rabbitmq · embedder · web · chat/rag/notify/stt/tts-worker · mock-llm (`--profile mock`) |
| `web/` | Next.js หน้าร้าน + ฉาก 3D/มาสคอต (Three.js) + API (`/api/chat` SSE · `/api/voice` · `/api/tts` · `/api/admin/eval` · `/api/admin/load`) — ไม่เรียก AI ตรง ส่งงานเข้าคิว |
| `workers/` | `chat-worker` (SQL สินค้า + Hybrid RAG + rerank + จำ 10 ข้อความ + tag `[CALC]` `[ADD_TO_CART]` `[QUOTE]`) · `rag-worker` (PDF → chunk → vector) · `stt-worker` (→ Whisper) · `tts-worker` (→ VoxCPM2) · `notify-worker` |
| `shared/` | สูตรราคา/ค่าส่ง/VAT · เครื่องคำนวณวัสดุ · topology คิว · แปลงตัวเลขไทย (`thainum.js`) — ใช้ร่วม web + workers + eval |
| `db/` | schema + seed สินค้า 36 รายการ · 3 สาขา · คูปอง · ตาราง `eval_runs` `load_runs` |
| `docs/docs-src/` | ต้นฉบับ HTML ของ PDF ใน `../../documents/` (`node make_pdfs.mjs <ชื่อ>`) |
| `mock-llm/` | แทน GPU ทั้ง 3 ใบ: LLM แบบ deterministic · STT จับคู่ไฟล์เสียงทดสอบ · TTS เล่นเสียงที่อัดไว้ · rerank ลำดับเดิม |
| `tests/fixtures/` | `BM-PROMO-NOV.pdf` ไฟล์ทดสอบอัปโหลด (เคส R07) |
| `e2e/` | Playwright เพลย์ลิสต์ · `voice-fixtures/` เสียงทดสอบ + `tts-cache/` · `fixtures/` ผลประเมิน/load ตัวอย่าง |
| `eval/` | ชุดคำถาม · `run_eval.mjs` · `score.mjs` · `make_report.mjs` · `runs/ai-rerank-on|off/` ผลจริง |
| `loadtest/` | `run_load.mjs` · `config.json` (เกณฑ์ "ไหว") · `results/ai-*.json` ผลจริง |
| `../vast_qwen/` · `../vast_aibox/` | เฉลยเปิด GPU-1 (Qwen) · GPU-2/3 (ai-box: Whisper + VoxCPM2 + reranker) |
