# CONTRACT — สัญญากลางของ `_solution/buildmart` (ทุก agent ต้องยึดตามนี้)

Requirement เต็ม: `BUILDMART.md` (อยู่ที่ `C:/Users/oishi/Documents/GitHub/CWN/Teaching/00_setup/04_Skill_Setup/04_Multi_Agent_Orchestra/BUILDMART.md`) — อ่านให้จบก่อนเริ่ม
ROOT = `C:/Users/oishi/Documents/GitHub/CWN/Teaching/00_setup/04_Skill_Setup/04_Multi_Agent_Orchestra/_solution/buildmart`

## กติกาความปลอดภัย (ทุก agent)
- ห้ามใช้คำสั่ง git ที่เปลี่ยนสถานะ repo (commit/stash/checkout/reset/branch) · อ่าน (`git status/diff/log`) ได้
- ห้ามใช้ Playwright MCP / ห้ามแตะ browser cookie ของผู้ใช้ · ทดสอบเว็บด้วย Playwright headless ของตัวเองเท่านั้น
- ห้ามพิมพ์ค่า secret · ห้าม `docker volume rm` / `docker system prune` / `compose down -v` ของโปรเจกต์อื่น (ของ `buildmart` เองใช้ `-v` ได้)
- ห้ามแตะ container `multi-account-devtool`, `deep_vision_5090_vllm` และ volume `ai-accounts`
- แก้เฉพาะไฟล์ที่เป็นของงานตัวเอง (ดู "เจ้าของไฟล์") · ถ้าต้องแก้ไฟล์ส่วนกลางให้แก้น้อยที่สุดและบอกในรายงาน
- เครื่อง: Windows 11 + Git Bash + Docker Desktop (compose v2) · Node 22 · Python 3.13 · 32 core / 64 GB · ไม่มี GPU

## โครงโฟลเดอร์ + เจ้าของไฟล์
```
ROOT/
  docker-compose.yml        (A)   .env.example (A)   README.md (G)
  shared/                   (A)   pricing.js · calc.js  — ESM ล้วน ไม่มี dependency ใช้ทั้ง web และ workers
  db/                       (A)   Dockerfile (FROM pgvector/pgvector:pg16) · init/01_schema.sql · init/02_seed.sql
  web/                      Next.js 14 App Router + TS
    app/layout.tsx, app/page.tsx, components/Header.tsx, lib/db.ts, lib/amqp.ts, lib/session.ts, Dockerfile  (A)
    app/products/**, app/calculator/**, app/api/products/**, app/api/calc/**                               (B1)
    app/cart/**, app/checkout/**, app/quote/**, app/track/**, app/api/{cart,checkout,quotes,orders,track}/** (B2)
    app/admin/**, app/api/admin/**, app/api/docs/**                                                         (B3)
    components/ChatWidget.tsx, app/api/chat/**, app/api/tts/**                                              (C1)
  workers/                  Node 22 ESM (ไม่ใช้ TS) · package.json · Dockerfile · lib/ (A สร้างโครง)
    chat-worker.js, lib/llm.js, lib/context.js, lib/rag-search.js, lib/tags.js                              (C2)
    rag-worker.js, lib/pdf.js, lib/embed.js                                                                  (D)
    notify-worker.js                                                                                         (B3)
  mock-llm/                 server.js · Dockerfile                                                          (C3)
  tts/                      worker.py · requirements.txt · Dockerfile                                       (E)
  docs/                     6 PDF (ข้อ 5 ของ BUILDMART) · docs-src/ (HTML + make_pdfs.mjs) · tests/fixtures/BM-PROMO-NOV.pdf  (D)
  e2e/                      Playwright tests + playlist + media pipeline + report                           (G)
```
compose build context = `ROOT` (ทุก Dockerfile `COPY shared/ ...` ได้) · ทุก Dockerfile อยู่ในโฟลเดอร์ของ service

## docker compose (project name `buildmart`)
| service | build/image | ports บนเครื่อง | env สำคัญ | profile |
|---|---|---|---|---|
| db | `db/Dockerfile` | – | POSTGRES_USER=bm POSTGRES_PASSWORD=bm POSTGRES_DB=buildmart | – |
| rabbitmq | `rabbitmq:4.4-management` | `127.0.0.1:15672:15672` | default guest/guest | – |
| embedder | `ghcr.io/huggingface/text-embeddings-inference:cpu-1.9` `--model-id intfloat/multilingual-e5-small` | – | volume `bm-hf` สำหรับ cache โมเดล | – |
| web | `web/Dockerfile` | `3400:3000` | DATABASE_URL AMQP_URL ADMIN_PASSWORD TTS_ENABLED | – |
| chat-worker | `workers/Dockerfile` cmd `node chat-worker.js` | – | DATABASE_URL AMQP_URL EMBED_URL MODE LLM_BASE_URL LLM_MODEL LLM_API_KEY | – |
| rag-worker | `workers/Dockerfile` cmd `node rag-worker.js` | – | DATABASE_URL AMQP_URL EMBED_URL | – |
| notify-worker | `workers/Dockerfile` cmd `node notify-worker.js` | – | DATABASE_URL AMQP_URL | – |
| mock-llm | `mock-llm/Dockerfile` | – | port 8000 ใน network | `mock` |
| tts-worker | `tts/Dockerfile` | – | AMQP_URL DATABASE_URL KOKORO_URL=http://kokoro:8880 | `tts` |
| kokoro | `ghcr.io/remsky/kokoro-fastapi-cpu:v0.9.0` | – | – | `tts` |

- `env_file`: `.env.vast` (optional: `required: false`) ให้ chat-worker · ค่าเริ่มต้นใน compose: `MODE=${MODE:-ai}` ถ้าไม่มี `.env.vast` และเปิด profile mock ให้ chat-worker ใช้ mock: กำหนดให้ chat-worker ใช้ `LLM_BASE_URL` ถ้ามีค่า ไม่งั้นใช้ `http://mock-llm:8000` (MODE=mock)
- named volumes: `bm-db`, `bm-hf`, `bm-mq` · ห้าม bind mount
- healthcheck ทุกตัว + depends_on condition: service_healthy (web รอ db+rabbitmq · worker รอ db+rabbitmq(+embedder))
- `TTS_ENABLED`: web ตรวจตอน runtime ว่ามี consumer ที่คิว `tts.request` ไหม (ผ่าน `channel.checkQueue`) → `/api/tts/status` คืน `{enabled}` → widget ซ่อนปุ่ม 🔊 ถ้าไม่มี

## Database (PostgreSQL 16 + pgvector + pg_trgm) — A สร้าง
```sql
products(sku pk, name, category, unit, price numeric(12,2), weight_kg numeric(10,3), reorder_point int, description text)
branches(code pk 'LKB'|'BNA'|'RST', name, phone)
stock(sku fk, branch fk, qty int, pk(sku,branch))
coupons(code pk, percent numeric, min_subtotal numeric)
carts(id uuid pk default gen_random_uuid(), session_id text unique, created_at)   cart_items(cart_id, sku, qty, pk(cart_id,sku))
quotes(id serial, quote_no text unique 'QT-YYYYMMDD-NNNN', session_id, customer_name, company, tax_id, coupon, totals jsonb, created_at, expires_at)  quote_items(quote_id, sku, qty, unit_price)
orders(id serial, order_no text unique 'BM-YYYYMMDD-NNNN', session_id, customer_name, phone, address, branch, delivery_date date, delivery_slot 'morning'|'afternoon', coupon, totals jsonb, status text default 'received', created_at)  order_items(order_id, sku, qty, unit_price)
order_status_history(order_id, status, changed_at)     -- status: received → preparing → shipping → delivered
chat_sessions(id text pk, created_at)   chat_messages(id serial, session_id, role 'user'|'assistant', content, cites jsonb, created_at)
docs(id serial pk, filename text unique, bytes bytea, pages int, chunks int default 0, status text default 'queued', error text, created_at, updated_at)
doc_chunks(id serial, doc_id fk on delete cascade, filename, page int, chunk_no int, content text, embedding vector(384))
  index hnsw (embedding vector_cosine_ops) · index gin (content gin_trgm_ops)
notifications(id serial, kind 'order'|'low_stock', message text, ref text, created_at, read boolean default false)
tts_audio(id uuid pk default gen_random_uuid(), lang text, text text, wav bytea, duration_ms int, created_at)
```
seed = ข้อมูลร้านข้อ 1–2 ของ BUILDMART ครบทุกแถว (สินค้า 36 รายการ · 3 สาขา · คูปอง 2 ใบ) · **ข้อมูลข้อ 5 (PDF) ห้ามใส่ใน DB seed**

## shared/ (A)
- `pricing.js`: `tierPrice(price, qty)` (1–49 ปกติ · 50–199 ×0.95 · ≥200 ×0.90 ปัด 2 ตำแหน่ง) · `computeTotals({items:[{sku,qty,price,weight_kg}], coupon})` → `{subtotal, discount, afterDiscount, weight, vehicle:'pickup'|'6wheel'|'10wheel', vehicleLabel:'กระบะ'|'รถ 6 ล้อ'|'รถ 10 ล้อ', shipping, vat, total, couponError?}` ตามลำดับข้อ 1 · `formatBaht(n)` → "15,607.29"
- `calc.js`: `calculate(type, input)` type ∈ concrete|wall|tile|paint|rebar → `{rows:[{sku, qty, unit, label}], extra?}` ตามสูตรข้อ 3.3 (rebar คืน `{bars, weightKg}` + rows)
- ต้องผ่านตัวเลข W05–W10 และ C05/C09/C13 · มี `shared/selftest.mjs` รัน `node shared/selftest.mjs` แล้ว OK

## RabbitMQ (ตามข้อ 4.2 ของ BUILDMART) — ชื่อตายตัว
- queue `chat.request` (durable, arguments: `x-dead-letter-exchange: ''`, `x-dead-letter-routing-key: chat.dlq`) · queue `chat.dlq` (durable)
- exchange `chat.reply` (direct, durable=false) · web สร้างคิว exclusive `chat.reply.<instanceId>` bind routing key = instanceId · ส่ง `reply_to = instanceId`, `correlation_id = messageId`, persistent
- chat.request body: `{sessionId, messageId, text, lang?}` · reply body: `{messageId, type:'status'|'delta'|'done'|'error', status?:'thinking', text?, cites?:[{filename,page,snippet}], cartCount?, quoteNo?}` (delta = ข้อความสะสมทั้งหมด ไม่ใช่ส่วนต่าง)
- chat-worker: `prefetch(4)` · ack หลังส่ง done · error → nack(requeue=false) ถ้า header `x-retries`≥2 ไม่งั้น republish พร้อม x-retries+1
- queue `rag.ingest` (durable) body `{docId}` · rag-worker prefetch 1
- queue `tts.request` (durable) body `{text, lang}` + reply_to/correlation_id (ใช้ exchange `chat.reply` เดียวกัน: routing key = instanceId) reply `{type:'tts', audioId, durationMs}` หรือ `{type:'tts', error}`
- exchange `order.events` (fanout, durable) · notify-worker ผูกคิว `notify.orders` (durable) · web publish `{type:'order.created', orderNo, items:[{sku,qty}], branch}` หลังตัดสต็อกสำเร็จ · notify-worker เขียน notifications 'order' + เช็ค stock < reorder_point → 'low_stock' (message มีชื่อ/SKU/สาขา/คงเหลือ)

## web API (Next.js route handlers · runtime nodejs · dynamic)
- session: cookie `bm_sid` (httpOnly, สร้างใน middleware หรือ lib/session.ts `getSessionId()`)
- `GET /api/products?q&category&min&max&inStock&sort=price_asc|price_desc&page` → `{items, total, page, pages}` (12/หน้า · ค้นไทยบางส่วนด้วย ILIKE ทั้ง name/sku)
- `GET /api/products/[sku]` → product + tiers[3] + stock[3]
- `POST /api/calc/[type]` → ผลจาก shared/calc.js
- `GET/POST/PATCH/DELETE /api/cart` (`{sku,qty}`) → `{items:[{sku,name,qty,unitPrice,lineTotal,weight}], totals, count}` · `POST /api/cart/coupon {code}`
- `POST /api/checkout {name, phone, address, branch, deliveryDate, slot}` → 200 `{orderNo}` · 409 `{error:'stock', items:[...]}` (ไม่ตัดอะไร) · ตัดสต็อกใน transaction แล้ว publish order.events แล้วล้างตะกร้า
- `POST /api/quotes {name, company?, taxId?}` → `{quoteNo}` · `GET /api/quotes/[no]` · `POST /api/quotes/[no]/order` (แปลงเป็นคำสั่งซื้อ: เติมตะกร้าจาก quote แล้ว redirect /checkout)
- `POST /api/track {orderNo, phone}` → `{status, history[]}`
- `/api/admin/*` ใช้ cookie `bm_admin` หลัง `POST /api/admin/login {password}` · stock GET/PATCH · orders GET/PATCH status · dashboard · notifications GET · docs GET/POST(multipart field `file`)
- `GET /api/docs/[filename]` → application/pdf (จาก docs.bytes) — ใช้กับลิงก์อ้างอิง `/api/docs/BM-DS-CEM.pdf#page=1`
- `POST /api/chat {text}` → **SSE** (`text/event-stream`) events: `queued` (ทันที, data `{messageId}`) → `status` → `delta` (data `{text}`) → `done` (data `{text, cites, cartCount, quoteNo}`) / `error` · timeout รอ 240 วิ (Q02 ต้องรอ worker กลับมาได้)
- `GET /api/chat/history` → ข้อความของ session
- `POST /api/tts {text}` → `{audioId, durationMs}` (รอ reply ≤ 60 วิ) · `GET /api/tts/[id]` → audio/wav · `GET /api/tts/status` → `{enabled}`

## chat-worker (C2)
- context: ① ค้นสินค้าที่เกี่ยวข้อง (คำไทย/SKU ในคำถาม + ประวัติ 6 ข้อความล่าสุด) ใส่ตาราง sku/name/price/unit/stock 3 สาขา · ② `rag-search.js` Hybrid RAG (ข้อ 4.3) top 4 → ใส่หัวข้อ "เอกสารอ้างอิง" ในรูป `[1] BM-DS-CEM.pdf หน้า 1: ...` · ③ ข้อมูลร้านข้อ 1 + กฎ + รูปแบบ tag
- `rag-search.js` export `hybridSearch(pool, query, k=4)` → `[{filename,page,content,score,vecSim}]` (ใช้ embedder `query: ` prefix, เอกสาร `passage: `)
- cites ที่ส่งให้ web: chunk ที่โมเดลอ้าง `[n]` ในคำตอบ ถ้าโมเดลไม่ใส่ `[n]` → ใช้ chunk อันดับ 1–2 ที่ vecSim ≥ เกณฑ์ (ปรับเกณฑ์ให้ R01–R07 ได้ไฟล์ถูก และคำถามทั่วไปเช่น C01 ไม่มี cite) · ตัด `[n]` ออกจากข้อความที่แสดง
- LLM: OpenAI-compatible stream (ดูตัวอย่าง `01_VastAi_Skill/_solution/ex2_chatbot/frontend/lib/llm.ts`) ส่ง `"enable_thinking": false` และ `chat_template_kwargs: {enable_thinking:false}` · ตัด `<think>` · timeout 90 วิ
- tag `[CALC]` `[ADD_TO_CART]` `[QUOTE]` ตามข้อ 4.4 · ใช้ shared/calc.js + shared/pricing.js · ADD_TO_CART เขียน cart_items ของ session ตรง (DB) แล้วส่ง `cartCount` · QUOTE สร้าง quote แบบเดียวกับ /api/quotes (ฟังก์ชันใน workers/lib/quote.js) — **รหัสเลข QT/BM ใช้ sequence ใน DB เดียวกับ web** (ฟังก์ชัน SQL `next_doc_no(prefix)` ที่ A สร้างใน schema)
- ภาษา: ถ้าคำถามไม่มีอักษรไทย → สั่งให้ตอบอังกฤษ
- บันทึก chat_messages ทั้ง user และ assistant (พร้อม cites)

## mock-llm (C3)
- `POST /v1/chat/completions` (รองรับ stream SSE และ non-stream) · `GET /health`
- deterministic: อ่าน system prompt (ตารางสินค้า + เอกสารอ้างอิง) + ข้อความผู้ใช้ล่าสุด + ประวัติ → ตอบให้ผ่าน C01–C14 · R01–R07 (ตอบจากประโยคในเอกสารอ้างอิงที่ตรงคำถามที่สุด แล้วใส่ `[n]`) · T01–T03 · Q
- ใช้ tag `[CALC]` เมื่อถามคำนวณ แล้วเมื่อได้ข้อความ role user/system ที่ขึ้นต้น `ผลคำนวณ:` ให้ตอบตัวเลขนั้น · "ใส่ตะกร้าให้เลย" หลังผลคำนวณ → `[ADD_TO_CART]` ตาม SKU/จำนวนล่าสุด
- **ห้ามเปิดอ่าน PDF เอง** — ต้องได้ข้อมูลจาก context ที่ chat-worker ส่งมาเท่านั้น (พิสูจน์ว่า RAG ทำงาน)

## UI testid (ทุกหน้าใช้ชื่อนี้ — e2e พึ่งพา)
header: `nav-cart-count` `search-input` `search-btn` · list: `product-card`(data-sku) `filter-category` `filter-min` `filter-max` `filter-instock` `sort-select`(price_asc/price_desc) `pagination-next`
product: `product-sku` `tier-price-1` `tier-price-2` `tier-price-3` `stock-LKB` `stock-BNA` `stock-RST` `qty-input` `add-to-cart`
calculator: `calc-tab-{concrete|wall|tile|paint|rebar}` `calc-input-volume` `calc-input-area` `calc-input-coats` `calc-paint-type`(interior/exterior) `calc-wall-type`(brick/light) `calc-rebar-size` `calc-input-length` `calc-submit` `calc-row`(data-sku,data-qty) `calc-add-all`
cart: `cart-row`(data-sku) `cart-unit-price` `cart-qty` `coupon-input` `coupon-apply` `cart-subtotal` `cart-discount` `cart-weight` `cart-vehicle` `cart-shipping` `cart-vat` `cart-total` `checkout-btn` `request-quote-btn`
checkout: `checkout-name` `checkout-phone` `checkout-address` `branch-select` `delivery-date` `delivery-slot` `place-order` `order-no` `stock-error`
quote: `quote-name` `quote-company` `quote-taxid` `quote-submit` `quote-no` `quote-row` `quote-total` `quote-to-order`
track: `track-order-no` `track-phone` `track-submit` `track-step`(data-status, data-active="true|false") `track-current`
admin: `admin-password` `admin-login` `admin-stock-row`(data-sku) `admin-low-stock` `admin-order-row`(data-order) `admin-status-select` `admin-status-save` `admin-notifications` `admin-notification`(data-kind) `admin-dlq-count` · docs: `doc-upload-input` `doc-upload-btn` `doc-row`(data-filename) `doc-status`
chat: `chat-open` `chat-panel` `chat-input` `chat-send` `chat-suggest` `chat-msg-user` `chat-msg-bot` `chat-status` (ข้อความ "รอคิว…"/"กำลังคิด…") `chat-cite` `tts-play` `tts-auto` `chat-audio`(<audio>)

## หน้าตา
- ภาษาไทยทั้งเว็บ ฟอนต์ `Sarabun`/`Noto Sans Thai` (next/font หรือ system fallback) · โทนส้ม-เทาเข้ม (สีแบรนด์ #F26B1D) · responsive · ไม่มี UI library
- ฟองแชทบอทแสดง markdown แบบง่าย (ขึ้นบรรทัด/ตัวหนา/รายการ)

## Notes from C3 (mock input format)
mock-llm (`http://mock-llm:8000`) อ่าน **เฉพาะ** messages ที่ chat-worker ส่ง · endpoint: `POST /v1/chat/completions` (`stream:true` → SSE หลาย delta + `data: [DONE]` · `stream:false` → `choices[0].message.content`) · `GET /health` → `{status:'ok'}` · `GET /v1/models` · field อื่น (`enable_thinking`, `chat_template_kwargs`, `model`, `temperature`) ไม่สนใจ
**messages ที่ C2 ต้องส่ง:** `[system, ...history(user/assistant ล่าสุด ≤6), user(คำถาม)]` และรอบ tag: `[..., assistant(คำตอบที่มี tag ดิบ), user("ผลคำนวณ: <JSON>")]`
**system (ข้อความเดียว)** — หัวข้อ `## ` ตามนี้ (ลำดับไม่สำคัญ แต่สะกดหัวข้อตรงตัว):
```
## ข้อมูลร้าน
ชื่อร้าน: บ้านช่าง BuildMart
เวลาเปิด: จันทร์–เสาร์ 07:00–18:00 · อาทิตย์ 08:00–12:00
สาขา: LKB ลาดกระบัง โทร 02-111-0001 · BNA บางนา โทร 02-111-0002 · RST รังสิต โทร 02-111-0003
LINE: @buildmart-demo
ราคาส่ง: 1–49 ชิ้น ราคาปกติ · 50–199 ชิ้น ลด 5% · 200 ชิ้นขึ้นไป ลด 10% (ต่อรายการ)
ค่าส่ง: ≤ 1,000 กก. กระบะ 500 บาท (ฟรีถ้ายอดก่อน VAT หลังส่วนลด ≥ 20,000) · 1,000.01–6,000 กก. รถ 6 ล้อ 1,500 บาท · > 6,000 กก. รถ 10 ล้อ 3,500 บาท
คูปอง: BUILD5 ลด 5% เมื่อยอดก่อน VAT ≥ 5,000 · CONTRACTOR10 ลด 10% เมื่อยอดก่อน VAT ≥ 30,000 (ใช้ได้ทีละ 1 ใบ)

## สินค้าที่เกี่ยวข้อง
- CEM-001 | ปูนซีเมนต์ปอร์ตแลนด์ ประเภท 1 (50 กก.) | 145 บาท/ถุง | สต็อก LKB 800 · BNA 500 · RST 300
- (ไม่พบสินค้าที่เกี่ยวข้อง)          ← ถ้าไม่มีสักรายการ
## เอกสารอ้างอิง
[1] BM-DS-CEM.pdf หน้า 1: <เนื้อหา chunk (ขึ้นบรรทัดในตัวได้)>
[2] BM-POLICY.pdf หน้า 1: <...>
(ไม่มีเอกสารที่เกี่ยวข้อง)          ← ถ้าไม่มี
## กฎ
<กฎ + รูปแบบ tag ข้อ 4.4 · ถ้าคำถามไม่มีอักษรไทย: "ตอบเป็นภาษาอังกฤษ">
```
- รูปแบบแถวสินค้า regex: `- SKU | ชื่อ | ราคา(ใส่ , ได้ ทศนิยมได้) บาท/หน่วย | สต็อก LKB n · BNA n · RST n` · ราคาเป็นราคาปกติ (mock คิดราคาส่งเอง) · **ให้ค้นสินค้าจากคำถาม + ประวัติ** (คำตอบของ mock มี SKU อยู่ในข้อความ เช่น `- PNT-001 สี... : 8 แกลลอน` → C13 "แล้วราคารวมเท่าไร" ต้องมีแถว PNT-001/PNT-003 ในตาราง) · คำถามอังกฤษ (T02 "Portland cement") ต้องหา CEM-001 ให้ได้ (แปลคำอังกฤษ→ไทยก่อนค้น หรือใช้ pg_trgm)
- เอกสาร: บรรทัดหัว `[n] <filename> หน้า <page>: ` (n เริ่ม 1 ตามลำดับ top-k) · mock ใส่ `[n]` ในคำตอบเฉพาะตอนใช้เอกสารจริง (C01/C03/C09… จะไม่มี `[n]`) → C2 ใช้ `[n]` ที่เจอเป็น cites ได้เลย
**tag ที่ mock ปล่อย (บรรทัดละ 1 tag ท้ายคำตอบ, JSON บรรทัดเดียว):**
- `[CALC]{"type":"concrete","volume":3}` · `{"type":"paint","area":120,"coats":2,"paintType":"exterior"}` · `{"type":"tile","area":50}` · `{"type":"wall","area":10,"wallType":"brick|light"}` · `{"type":"rebar","size":"DB12","length":100}` (key ตรง `shared/calc.js`) → C2 เรียก `calculate()` แล้วเรียก LLM อีกรอบโดยต่อท้าย `assistant`(ข้อความที่มี tag) + `user`: `ผลคำนวณ: {"type":"concrete","input":{"volume":3},"rows":[{"sku":"CEM-001","qty":21,"unit":"ถุง","label":"..."}],"extra":{...}}` (คือผล `calculate()` + `type` + `input`; error → `{"type":..,"error":"..."}`) → คำตอบรอบ 2 = คำตอบสุดท้าย (ไม่มี tag) ให้บันทึกลง chat_messages
- `[ADD_TO_CART]{"sku":"CEM-001","qty":21}` (อาจหลายบรรทัด) → ข้อความยืนยันอยู่ในคำตอบแล้ว ไม่ต้องเรียกรอบ 2 · mock หา SKU/จำนวนจากคำตอบ assistant ล่าสุดใน history (บรรทัด `- SKU ชื่อ : N หน่วย`) หรือจาก `ผลคำนวณ:` ถ้ายังอยู่ใน history → **history ต้องมีคำตอบ assistant ก่อนหน้า (ตัด tag แล้วได้)**
- `[QUOTE]{}` → C2 สร้าง quote แล้ว **เรียกรอบ 2** ด้วย `user`: `ผลคำสั่ง: {"quoteNo":"QT-20261023-0001","total":15607.29}` (ตะกร้าว่าง → `ผลคำสั่ง: {"error":"empty cart"}`) → mock ตอบพร้อมเลข QT (ถ้าไม่เรียกรอบ 2 ให้ C2 ต่อท้ายข้อความ "เลขที่ใบเสนอราคา QT-…" เอง)
- ตัด tag ทุกตัวออกก่อนแสดง · คำตอบไทยลงท้าย "ครับ" · คำถามไม่มีอักษรไทย → mock ตอบอังกฤษล้วน
- dev: `node mock-llm/selftest.mjs` (35 เคส: C01–C14, R01–R07, Q, T, stream/non-stream, 8 concurrent) · env `MOCK_DELAY_MS` (ดีฟอลต์ 15 ms/delta) `MOCK_CHUNK` (6 ตัวอักษร/delta)

## Notes from A
**สถานะ:** `docker compose -p buildmart --profile mock up -d --build` ขึ้นครบ healthy · stack รันค้างไว้ · placeholder: `workers/{chat,rag,notify}-worker.js`, `mock-llm/server.js` (echo), `tts/worker.py`, `web/components/ChatWidget.tsx` (return null) — เจ้าของเขียนทับได้ทั้งไฟล์

**build ใหม่ทีละ service:** `cd ROOT && docker compose -p buildmart up -d --build --no-deps web` (หรือ `chat-worker` / `rag-worker` / `notify-worker` / `mock-llm`) · tts: เติม `--profile tts` · แก้ schema/seed → `docker compose -p buildmart down -v` แล้ว up ใหม่ (เฉพาะ buildmart)

**import shared/**
- web: `import { computeTotals, tierPrice, tierTable, formatBaht, shippingFor, COUPONS } from '@/shared/pricing.js'` · `import { calculate, REBAR } from '@/shared/calc.js'` (Dockerfile copy `ROOT/shared` → `/app/shared`; tsconfig `@/*` → `./*`; allowJs) · `next dev` นอก docker ต้อง `cp -r ../shared web/shared` ก่อน
- workers: `import ... from '../shared/pricing.js'` (จากไฟล์ใน `workers/`) หรือ `'../../shared/...'` (จาก `workers/lib/`) — ใช้ได้ทั้งใน docker (`/app/workers` + `/app/shared`) และนอก docker
- เพิ่ม `shared/topology.js` (ชื่อคิว/exchange + `assertTopology(ch)`) — **ทุก service assert ผ่านไฟล์นี้เท่านั้น** (args ไม่ตรง = PRECONDITION_FAILED) · `shared/package.json` = `{type: module}`
- `computeTotals({items:[{sku,qty,price,weight_kg}], coupon})` coupon = code string (หรือ `{code,percent,min_subtotal}`) → `{lines:[{sku,qty,unitPrice,lineTotal,weight}], subtotal, discount, coupon(code ที่ใช้ได้|null), afterDiscount, weight, vehicle, vehicleLabel, shipping, vat, total, couponError?}` · ตะกร้าว่าง shipping = 0
- `calculate(type, input)` keys: concrete `{volume}` · wall `{area, wallType:'brick'|'light'}` · tile `{area}` · paint `{area, coats=2, paintType:'interior'|'exterior'}` · rebar `{size:'RB6'|'RB9'|'DB12'|'DB16', length}` → rebar คืน `bars`, `weightKg` ด้วย · ตรวจด้วย `node shared/selftest.mjs`

**web/lib (A)**
- `@/lib/db`: `pool`, `query(sql, params)`, `tx(async c => ...)` · numeric/int8 → number
- `@/lib/session`: `getSessionId()` (route handler) · `peekSessionId()` · cookie `bm_sid` ถูกสร้างใน `web/middleware.ts` ทุก request
- `@/lib/amqp`: `rpc(queue, body, {correlationId, timeoutMs=240000, onMessage, isFinal})` → `{correlationId, result: Promise<lastMsg>, cancel()}` (final = type done|error|tts; publish persistent + replyTo=instanceId + correlationId=messageId) · `sendToQueue(q, body, opts)` · `publish(exchange, routingKey, body)` (order.events → routingKey `''`) · `onReply(cid, fn)` → unsubscribe · `checkQueue(name)` → `{messageCount, consumerCount}|null` (ใช้ channel ชั่วคราว — ใช้กับ `/api/tts/status` และ DLQ count) · `getChannel()`, `instanceId`, `Q`, `EX`
- `GET /api/cart/count` → `{count}` = **SUM(qty)** ของตะกร้า session (A สร้างแล้ว · B2 อย่าลบ และให้ `count` ใน /api/cart ใช้นิยามเดียวกัน)
- header (`components/Header.tsx`) อัปเดตตัวเลขตะกร้าเมื่อ `window.dispatchEvent(new CustomEvent('bm:cart', {detail:{count}}))` (ไม่มี detail = refetch) — B2/C1 เรียกหลังแก้ตะกร้า
- `@/lib/categories`: `CATEGORIES` 11 หมวด · global CSS classes: `.btn .btn.secondary .input .select .card .muted .price .container`, CSS vars `--brand` ฯลฯ ใน `app/globals.css`

**workers/lib (A)**
- `db.js`: `pool`, `waitForDb()`, `tx(fn)` · `ready.js`: `markReady()` (เขียน `/tmp/ready` = healthcheck ของ worker ใน compose — **worker จริงต้องเรียกหลังพร้อม**), `idleForever(cleanup)`
- `amqp.js`: `connectAmqp({prefetch, onReconnect})` → `{conn, ch}` (retry, assert topology; ไม่ให้ onReconnect = exit(1) ให้ docker restart) · `replyTo(ch, msg, body)` publish ไป `chat.reply` routing key = `msg.properties.replyTo` + correlationId เดิม · `publishJson(ch, ex, rk, body)` · `parseJson(msg)` · `Q`, `EX`
- `config.js`: `getLlmConfig()` → `{mode, baseUrl, model, apiKey, timeoutMs}` — ไม่มี `LLM_BASE_URL` → mock (`MOCK_LLM_URL`=http://mock-llm:8000) · compose **ไม่** ใส่ LLM_*/MODE ใน `environment:` (จะทับ `.env.vast`)
- `cart.js`: `addToCart(db, sid, sku, qty)` → count ใหม่ · `cartCount(db, sid)` · `loadCart(db, sid)` → `{cartId, coupon, items, totals}` · `getOrCreateCartId`
- `quote.js`: `createQuoteFromCart(pool, sid, {name, company, taxId})` → `{quoteNo, quoteId, totals, items, expiresAt}` (throw `cart_empty`) · `quotes.totals` = ผล `computeTotals()` ทั้งก้อน · `quote_items.unit_price` = ราคาหลังราคาส่ง

**DB เพิ่มจาก contract:** `carts.coupon text` (คูปองที่ใส่ในตะกร้า) · `order_status_history.id serial` · `doc_counters` + `next_doc_no(prefix)` (เวลาไทย; `SELECT next_doc_no('BM')`) · timezone DB = Asia/Bangkok · ไม่มี seed เอกสาร/ข้อมูลข้อ 5
**compose:** web มี `TTS_ENABLED=${TTS_ENABLED:-auto}` · worker healthcheck = `test -f /tmp/ready` · embedder พร้อมแล้ว (โมเดลอยู่ใน volume `buildmart_bm-hf`) · workers image มี `pdftotext` (poppler-utils) + ฟอนต์ไทย · root `.dockerignore` กัน node_modules/.next/.env*

## Notes from E
**สถานะ:** `tts/` = `worker.py` · `textnorm.py` · `healthcheck.py` · `requirements.txt` · `Dockerfile` (python:3.12-slim, ~1.2 GB · โมเดล PyThaiTTS fastthaig2p โหลด+warm ตอน build → รัน offline ได้) · ทดสอบจริงผ่าน RabbitMQ+DB แล้ว · `docker compose -p buildmart --profile mock --profile tts up -d --build tts-worker kokoro`
**ขอ (request) → คิว `tts.request`** (durable): body `{text, lang?}` (lang ไม่บังคับ — worker ตัดสินเอง: มีอักษรไทย U+0E00–U+0E7F → `th` ไม่งั้น `en`) · properties `replyTo = instanceId`, `correlationId` = id ของ request · ส่ง raw ข้อความบอทได้เลย worker ตัด `<think>`, tag `[CALC]{..}`/`[ADD_TO_CART]{..}`/`[QUOTE]{}`, `[n]`, markdown, URL, emoji เอง แล้วตัดเหลือ 600 ตัวอักษร
**ตอบ (reply) → exchange `chat.reply`** routing key = replyTo, correlationId เดิม: `{type:'tts', audioId, durationMs, lang}` หรือ `{type:'tts', error}` (เช่น ข้อความว่างหลังตัด → `error:'empty text'`)
**web:** `POST /api/tts` = `rpc('tts.request', {text}, {timeoutMs: 60000})` → final msg type `tts` (lib/amqp ของ A รองรับแล้ว) → ถ้ามี `error` ตอบ 502 · `GET /api/tts/[id]` = `SELECT wav FROM tts_audio WHERE id=$1` → `audio/wav` (24 kHz mono 16-bit) · `/api/tts/status` → `checkQueue('tts.request').consumerCount > 0` (worker เป็น consumer prefetch 2 ตลอดเวลาที่ต่ออยู่)
**เสียง:** ไทย = PyThaiTTS `fastthaig2p` เสียง `thai_som` (in-process) · อังกฤษ = Kokoro `af_heart` (fallback `af_bella` อัตโนมัติ) · ไทยแปลงก่อนพูด: เวลา `07:00`/`18:00 น.` → "เจ็ดนาฬิกา", ราคา `145 บาท`/`15,607.29 บาท` → อ่านบาท/สตางค์, ตัวเลข/ทศนิยม, ช่วง `16–20` → "สิบหก ถึง ยี่สิบ", `/` → "ต่อ", ตร.ม./ลบ.ม./ตร.ซม./กก./มม./ซม./ชม./%/A
**latency (CPU):** ไทย 1 ประโยค (เสียง 4.2 วิ) ≈ 1.0–1.3 วิ · อังกฤษ (เสียง 4.5 วิ) ≈ 0.5–0.7 วิ · ข้อความไทย 600 ตัวอักษร ≈ 14 วิ (เสียง ~54 วิ) — ยังอยู่ใน timeout 60 วิ
**healthcheck:** worker เขียน `/tmp/tts-heartbeat` ทุก ≤5 วิขณะต่อ RabbitMQ อยู่ · compose `python healthcheck.py` (ไฟล์อายุ < 60 วิ) — E แก้ใน compose เฉพาะ healthcheck ของ tts-worker · kokoro ใช้ healthcheck เดิมของ A (`/health`) · หลุด RabbitMQ → ลบ heartbeat แล้ว reconnect ทุก 3 วิ (ทดสอบ force-close แล้วกลับมา consume เอง)

## Notes from C2 (chat-worker)
**สถานะ:** `workers/chat-worker.js` + `lib/{llm,context,tags}.js` เสร็จ · ใช้ `lib/rag-search.js` ของ D (โหลดแบบ dynamic import · ไม่มีไฟล์ → fallback pg_trgm) · ทดสอบ: `docker compose -p buildmart exec -T chat-worker node chat-selftest.mjs [--rpc|--http] [--dlq]` (auto = /api/chat ถ้ามี) → mock ผ่านครบ C01–C14 · R01–R06 · Q01 · T02 · DLQ (R07 รันเมื่อมี BM-PROMO-NOV.pdf ready)
- reply: `status:'thinking'` ทันที → `delta` (ข้อความสะสม ตัด tag/think/[n] แล้ว · throttle 50 ms · รอบที่มี [CALC]/[QUOTE] หยุด stream) → `done {text, cites, cartCount (SUM qty ทุกครั้ง), quoteNo?}` · ครบ retry → `error {text}` แล้ว nack → chat.dlq
- cites: `[n]` ที่โมเดลอ้าง · ไม่มี `[n]` → อันดับ 1–2 ที่ vecSim ≥ `CITE_MIN_VECSIM` ของ D (0.84) **และ** คำตอบมีข้อความจาก chunk ≥ 8 ชิ้น (5 ตัวอักษร ที่ไม่อยู่ในข้อมูลร้าน/ตารางสินค้า/คำถาม) — vecSim ของ e5-small อย่างเดียวแยกไม่ได้ ("ปูนซีเมนต์ถุงละเท่าไร" ได้ 0.90)
- ข้อความทดสอบ DLQ: ส่ง text `__bm_test_fail__` → error 3 ครั้ง → เข้า chat.dlq (selftest `--dlq` ดึงออกให้เอง)
- ตั้ง env `CHAT_DEBUG=1` ให้ chat-worker log คำตอบดิบ + เอกสารที่ค้นได้

## Notes from D
**สถานะ (อัปเดตตาม §5 ใหม่):** `docs/` 6 PDF ยาว **9 หน้าทุกไฟล์** (ปก · สารบัญพร้อมเลขหน้า · หัว/ท้ายกระดาษ "หน้า X/Y" · ตารางหัว 2–3 ชั้น/rowspan/colspan/ตารางยาวข้ามหน้าหัวซ้ำ/เมทริกซ์/เชิงอรรถ ¹ ²/เปรียบเทียบหลายรุ่น) + `tests/fixtures/BM-PROMO-NOV.pdf` (1 หน้า) · ข้อเท็จจริง §5 ครบ + ตาราง R08 ใน BM-DS-CEM (ตารางที่ 5: 60x60 → เกรียงฟัน 10 มม. → 5.5 กก./ตร.ม.)
- สร้างใหม่: `cd docs/docs-src && npm i && node make_pdfs.mjs [ชื่อไฟล์] [--png dir]` (Playwright 1.63 · `tagged: true` = Tagged PDF · สารบัญเติมเลขหน้าอัตโนมัติจาก structure tree) · แม่แบบ `docs-src/_template.html`
- chunks ที่ ingest แล้ว: CEM 48 · ELC-PIP 50 · PNT 48 · STL 48 · TIL 44 · POLICY 50 = **288** (ready) · PROMO 3 chunks
**ดึงข้อความ (lib/pdf.js + lib/pdf-struct.js · จาก bytes ของ PDF เท่านั้น ใช้กับไฟล์อัปโหลดด้วย):** Tagged PDF → structure tree (pdf-lib) + กรอบ MCID (pdfjs-dist) + คำไทยที่ถูกต้อง (poppler `pdftotext -bbox-layout`) → หัวข้อ/ย่อหน้า/ตาราง · ตาราง: วางกริดตาม RowSpan/ColSpan (ค่าเซลล์รวมถูกกระจายทุกแถว) · หัวคอลัมน์หลายชั้นรวมเป็น `ชั้น1 › ชั้น2` · หัวซ้ำข้ามหน้าถูกตัดซ้ำ · ตัดสารบัญ/หัว-ท้ายกระดาษ (artifact) · PDF ไม่มีโครงสร้าง → ย่อหน้าจากพิกัด (แบบเดิม)
- chunk ย่อหน้า: บรรทัดแรก = หัวข้อระดับ 2 · ~500 ตัวอักษร ซ้อน 80 · chunk ตาราง: บรรทัดแรก = caption (`ตารางที่ N …` + "(ต่อ)") แล้วแถวละบรรทัด `หัวคอลัมน์: ค่า, …` (~700 ตัวอักษร ไม่ตัดกลางแถว) + เชิงอรรถที่แถวอ้างถึง
- ตัวอย่างแถว: `ประเภทงาน: พื้น, ขนาดกระเบื้อง: 60x60 ซม., เกรียงหวี › ขนาดฟันเกรียง: 10 มม., เกรียงหวี › รูปฟัน: ฟันเหลี่ยม, อัตราการใช้ปูนกาว › กก./ตร.ม.: 5.5, …`
- ดู chunk ของไฟล์ใด ๆ: `docker compose -p buildmart exec rag-worker node rag-chunks.mjs /app/docs/BM-DS-CEM.pdf`
**B3 อัปโหลด:** `INSERT INTO docs(filename, bytes, status) VALUES ($1,$2,'queued') ON CONFLICT (filename) DO UPDATE SET bytes=EXCLUDED.bytes, status='queued', error=NULL, updated_at=now() RETURNING id` แล้ว `sendToQueue('rag.ingest', {docId})` → processing → ready (pages, chunks) / failed (+error)
**API (C2):** `import { hybridSearch, embedQuery, isCiteworthy, CITE_MIN_VECSIM, CITE_MIN_KW } from './lib/rag-search.js'`
- `await hybridSearch(pool, query, k=4)` → `[{filename, page, chunkNo, content, score, vecSim, kwScore}]` (RRF k=60 ของ vector top20 + keyword top20 · keyword = token ละติน/ตัวเลข ×2 + คำไทย ×1 + pg_trgm word_similarity)
- **เกณฑ์ cite fallback (เมื่อโมเดลไม่ใส่ `[n]`): `isCiteworthy(r)` = `vecSim ≥ 0.865` และ `kwScore ≥ 1`** ใช้กับอันดับ 1–2 (env `RAG_CITE_MIN_VECSIM`, `RAG_CITE_MIN_KW`) · vecSim อย่างเดียวแยกไม่ได้แล้ว ("ร้านเปิดกี่โมงครับ" .866 ≈ R07 .870, "ปูนซีเมนต์ถุงละเท่าไร" .894)
- rag-selftest: R01–R06, R08 ไฟล์ถูกอันดับ 1 + มีข้อเท็จจริงใน chunk ทุกข้อ · vecSim อันดับ 1: R01 .917 · R02 .916 · R03 .915 · R04 .887 · R05 .912 · R06 .874 (อันดับ 2 .899) · R08 .925 · R07 .870 (kw 2.5) · กฎ 2 เงื่อนไข: cite ถูก 11/12 (พลาดเฉพาะคำถามอังกฤษ X05 kw=0) · คำถามทั่วไปได้ cite 0/10
**mock-llm (แก้น้อยที่สุด, บอก C3):** `searchDocs` ① ไม่ตัดประโยคหลังคำย่อไทยที่มีจุด (มม. ซม. ตร.มม.) ② ลดคะแนน ×0.8 ช่วงที่เป็นคำถาม FAQ (กี่/ไหม/อย่างไร/?) และบรรทัด caption "ตารางที่ N" ③ คะแนนเท่ากันให้ช่วงที่มีตัวเลขชนะ ④ codes จับ `60x60` ทั้งก้อน · `node mock-llm/selftest.mjs` 35/35
**chat-selftest (`--http` ผ่าน web):** 26/26 ผ่าน รวม R01–R08 (R07 อัปโหลด promo ชั่วคราวแล้วลบออก · DB คงเหลือ 6 เอกสาร) · เพิ่ม R08 ใน `workers/chat-selftest.mjs` แล้ว
**dependency ใหม่ใน workers/package.json:** `pdf-lib`, `pdfjs-dist` (แก้ไฟล์ของ A เล็กน้อย) · workers/Dockerfile มี `COPY docs/*.pdf /app/docs/`
