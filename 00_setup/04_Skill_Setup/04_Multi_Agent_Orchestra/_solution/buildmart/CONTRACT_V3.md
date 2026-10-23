# CONTRACT_V3 — ส่วนเพิ่มของ v3 (อ่านต่อจาก CONTRACT.md · ถ้าขัดกัน ไฟล์นี้ชนะ)

ภาพรวมการออกแบบ: `../../ARCHITECTURE_V3.md` (อ่านก่อน)
ROOT = `C:/Users/oishi/Documents/GitHub/CWN/Teaching/00_setup/04_Skill_Setup/04_Multi_Agent_Orchestra/_solution/buildmart`
LAB = `C:/Users/oishi/Documents/GitHub/CWN/Teaching/00_setup/04_Skill_Setup/04_Multi_Agent_Orchestra`

**เครื่องนี้มี GPU RTX 5090 ในเครื่อง** (Docker Desktop `--gpus all` ใช้ได้) · ห้ามแตะ container `deep_vision_5090_vllm` / `multi-account-devtool` · กติกาความปลอดภัยใน CONTRACT.md ยังใช้ทั้งหมด (ห้าม git ที่เปลี่ยนสถานะ · ห้าม Playwright MCP · ห้ามพิมพ์ secret)

## 1) เอกสาร PDF → `LAB/documents/` (ชั้นแรกของ LAB ให้คนหาเจอ)
- 6 ไฟล์เดิม (`BM-DS-CEM` `BM-DS-STL` `BM-DS-PNT` `BM-DS-TIL` `BM-DS-ELC-PIP` `BM-POLICY`) **ไฟล์ละ 18–22 หน้า A4** · source HTML อยู่ `ROOT/docs/docs-src/*.html` · build: `cd ROOT/docs/docs-src && node make_pdfs.mjs <ชื่อ>` → เขียนลง `LAB/documents/<ชื่อ>.pdf`
- **ไม่มีราคา/สต็อกใน PDF** (ราคา/สต็อกอยู่ใน DB เท่านั้น → ใช้ทดสอบคำถามแบบ SQL) · PDF มี **ตารางสเปกสินค้าตาม SKU** (SKU ต้องตรงกับ seed ใน `ROOT/db/init/02_seed.sql`)
- ข้อเท็จจริงที่ BUILDMART ข้อ 5 บังคับไว้ต้องยังอยู่ครบและตัวเลขเดิม (เคส R01–R08 ใช้)
- compose: workers ได้ PDF ผ่าน `additional_contexts: { documents: ../../documents }` + `COPY --from=documents *.pdf /app/docs/`

## 2) ai-box (`ROOT/../vast_aibox/` · โค้ดชุดเดียว 2 เครื่อง: GPU-2 `MODELS=stt` · GPU-3 `MODELS=tts,rerank` · local dev ใช้ `MODELS=all`) — พอร์ตเดียวต่อเครื่อง · ทุก endpoint (ยกเว้น /health) ต้องมี `Authorization: Bearer <AIBOX_API_KEY>`
| endpoint | รับ | คืน |
|---|---|---|
| `GET /health` | – | `{status:'ok', models:{stt, tts, rerank}, vram_mb}` |
| `POST /v1/audio/transcriptions` | multipart `file` (webm/ogg/wav/mp3) · `language` (`th`/`en`/ว่าง=auto) | `{text, language, duration}` (รูปแบบ OpenAI) |
| `POST /v1/audio/speech` | JSON `{input, voice:'nongchang', response_format:'wav', language?}` | `audio/wav` |
| `POST /v1/rerank` | JSON `{query, documents:[string], top_n}` | `{results:[{index, relevance_score}]}` (เรียงมาก→น้อย) |
- โมเดล: faster-whisper (`large-v3` หรือ `large-v3-turbo` เลือกจากผลวัดไทย) · VoxCPM2 (โคลนเสียงจาก `voices/nongchang.wav` + ข้อความอ้างอิง) · `BAAI/bge-reranker-v2-m3`

## 3) โหมด mock (ฟรี) — `mock-llm` ให้ API เดียวกับ ai-box เพิ่ม (พอร์ต 8000)
- `/v1/audio/transcriptions`: sha256 ของไฟล์เสียง → ข้อความจาก `ROOT/e2e/voice-fixtures/index.json` (`{"<sha256>": {"text": "...", "language": "th"}}`) · ไม่รู้จัก → `{text:''}` · `/v1/rerank`: คืนลำดับเดิม (score ลดหลั่น) · `/v1/audio/speech`: เล่นเสียง VoxCPM2 ที่อัดไว้แล้ว `ROOT/e2e/voice-fixtures/tts-cache/<sha256(input)>.wav` ถ้ามี ไม่งั้น `tts-cache/generic.wav` (ประโยคทั่วไปของน้องช่าง) · สคริปต์ `e2e/make-tts-cache.mjs` สร้าง cache จาก ai-box จริง
- env ของ worker: `STT_URL` `TTS_URL` `RERANK_URL` (ค่าเริ่มต้นทั้งหมด `http://mock-llm:8000` ถ้าไม่มี `.env.aibox`) · `AIBOX_API_KEY` (key เดียวกันทั้ง 2 เครื่อง) · ไฟล์ `.env.aibox` (optional, 4 บรรทัด ไม่มี quote) ให้ chat-worker/stt-worker/tts-worker ผ่าน `env_file required:false`

## 4) RabbitMQ เพิ่ม
- queue `stt.request` (durable) body `{audioB64, mime, lang?}` + reply_to/correlation_id แบบเดียวกับ tts (exchange `chat.reply` · routing key = instanceId) → reply `{type:'stt', text, language, durationMs}` หรือ `{type:'stt', error}` · `stt-worker` prefetch `STT_PREFETCH` (4)
- `tts.request` เดิม: tts-worker เรียก `${TTS_URL}/v1/audio/speech` อย่างเดียว (**เลิกใช้ Kokoro/PyThaiTTS** · ลบ service `kokoro` และ profile `tts` · tts-worker เปิดตลอดเพราะไม่มีโมเดลในตัว) · reply เพิ่ม `engine:'voxcpm2'|'mock'`
- chat-worker: ประวัติ **10 ข้อความล่าสุด** ของ session (บทสนทนา 4–6 รอบต้องเข้าใจ "อันนั้น/ตัวเมื่อกี้") · RAG: hybrid RRF **top 20 → `/v1/rerank` → top 4** เมื่อ `RERANK=on` (ค่าเริ่มต้น on · mock = ลำดับเดิม) · reply `done` เพิ่ม `retrieved:[{filename,page,score}]` (top 4 ที่ใส่ในพรอมต์ · ใช้ประเมิน Hit@4/MRR) และ `products:[sku]` (สินค้าที่ดึงจาก DB) — web ส่งต่อใน SSE `done`

## 5) web เพิ่ม
- `POST /api/voice` multipart `audio` → `{text, language, durationMs}` (ส่ง stt.request รอ ≤ 60 วิ) · `GET /api/voice/status` → `{enabled}` (มี consumer ที่ `stt.request`)
- chat widget: ปุ่มไมค์ `voice-mic` (กดค้าง/กดเริ่ม-หยุด · MediaRecorder) · ข้อความที่ถอดได้แสดงเป็นฟองผู้ใช้พร้อมป้าย 🎙 `chat-msg-voice` · โหมด "คุยด้วยเสียง" `voice-mode` (ถาม → ตอบ → เล่นเสียงอัตโนมัติ) · มาสคอต 3D `mascot` (data-state = `idle|listening|thinking|talking`) ขยับปากตามเสียงที่เล่น
- testid เดิมทุกตัวใน CONTRACT.md ต้องยังอยู่และทำงานเหมือนเดิม (e2e เดิม 42 เคสต้องผ่าน)
- หน้า **`/admin/eval`** dashboard ผลประเมิน RAG: อ่าน `GET /api/admin/eval` → รายการ run + run ล่าสุด · testid: `eval-run-select` `eval-metric`(data-metric, data-set) `eval-item`(data-id, data-pass) `eval-compare`
- `POST /api/admin/eval` (cookie admin หรือ header `x-eval-token: ${EVAL_TOKEN:-bm-eval}`) body = results.json (ข้อ 6) → เก็บตาราง `eval_runs`

## 6) Database เพิ่ม
```sql
eval_runs(id serial pk, label text, created_at timestamptz default now(), config jsonb, summary jsonb, items jsonb)
```
`results.json`: `{label, config:{llm, rerank, stt, tts}, summary:{<set>:{<metric>:number 0..1, n}}, items:[{id, set, question|turns, expected, answer, retrieved, cites, metrics:{...}, pass, reason}]}`

## 7) ประเมิน RAG (`ROOT/eval/`)
- `qa.json`: set `rag` **150–170 ข้อ** (จาก PDF · ระบุ `sources:[{filename,page}]` + `key_facts`) · set `qa` **คำถามปกติ 70–80 ข้อ** (ไม่ต้องใช้ PDF: ราคา/ราคาส่ง/สต็อกสาขา/คูปอง/ค่าส่ง · `expected_values` + `sql` ที่ใช้หาคำตอบ · ข้อมูลร้าน/เวลาเปิด/สาขา · คำนวณวัสดุ · คำถามนอกเรื่องที่ต้องปฏิเสธ) · set `conv` (10–12 บท × **4–6 รอบ** (ขั้นต่ำ 4) · บางบท `audio` = ไฟล์ใน `e2e/voice-fixtures/`)
- metric: rag → `hit_at_4` `mrr` `citation_acc` `faithfulness` `correctness` · qa → `exact_value` `sql_correct` `correctness` · conv → `context_retention` `correctness` (+ `stt_cer` ถ้าเป็นเสียง)
- `run_eval.mjs` ถามผ่าน `POST /api/chat` (session ใหม่ต่อข้อ/ต่อบท) → คำนวณ metric ที่คำนวณได้ด้วยโค้ด (hit/mrr/citation/exact/cer) → `answers.json` · metric ที่ต้องใช้ผู้ตัดสิน (`faithfulness` `correctness` `context_retention`) ตัดสินโดย AI ที่รันพรอมต์ (Claude) เขียน `judgments.json` → `score.mjs` รวมเป็น `results.json` แล้ว POST เข้า `/api/admin/eval`

## 8) Load test (`ROOT/loadtest/`)
- `run_load.mjs --mode chat|stt|tts|voice --users 1,2,4,8,16,32 --stage-sec 120` ยิงผ่าน web API จริง (`/api/chat` SSE · `/api/voice` · `/api/tts`) ด้วย session แยกต่อผู้ใช้จำลอง · อ่านความยาวคิวจาก RabbitMQ management API ทุก 2 วิ
- ผล `loadtest/results/<label>.json`: ต่อขั้น `{users, n, errors, p50, p95, ttft_p50, ttft_p95, rtf, tokens_per_s, queue_max}` + `max_users_ok` ตามเกณฑ์ใน config · POST เข้า `POST /api/admin/load` (เก็บตาราง `load_runs` แบบเดียวกับ eval_runs) → หน้า `/admin/load` (testid `load-run-select` `load-chart` `load-max-users`)
- prefetch ต่อคิวตั้งได้ด้วย env: `CHAT_PREFETCH` (4) `STT_PREFETCH` (4) `TTS_PREFETCH` (2) · scale worker ด้วย `--scale`

## 9) เพิ่มเติม (จากการทดลองไมค์ปลอม)
- e2e ป้อนเสียงด้วย init script ที่ห่อ `navigator.mediaDevices.getUserMedia` ให้คืน stream จาก WebAudio ที่เล่นไฟล์ fixture (deterministic กว่า `--use-file-for-fake-audio-capture`) → web ได้ webm จาก MediaRecorder ซึ่ง **sha256 ไม่ตรงไฟล์ fixture** → mock STT จับคู่ด้วย sha256 ก่อน ไม่ตรงให้ใช้ **fingerprint**: ความยาว ±0.4 วิ + ความสัมพันธ์ของ RMS envelope ≥ 0.8 (decode ด้วย ffmpeg) · `index.json` มีฟิลด์ `file` `durationMs` เพิ่ม
- มาสคอตมี `data-mouth` (0.00–1.00 ความกว้างปากปัจจุบัน) ให้ e2e ตรวจว่าขยับตามเสียง
- `GET /api/admin/eval?id=<n>` ดึง run ที่เลือก · POST ไม่มี token/cookie → 401
