# TEST.md · รวมระบบและทดสอบเบื้องต้น (B10)

- วันที่ทดสอบ: 2026-11-19 (เวลาประเทศไทย 07:52–08:15)
- เครื่อง: Linux 6.6 (WSL2) · Docker Engine 29.9.3 · Docker Compose v5.7.0 · Node.js 22.23.4 · Python 3.12.3 · **ไม่มี GPU**
- โหมดของฝั่งเว็บ: profile `test` · `AI_MODE=mock` · `ENABLE_TEST_RESET=1` · `BUG_MODE=0` (จาก `.env.test.example`)
- ฝั่ง AI ทดสอบด้วยตัวตรวจจำลอง (fake detector) แทน YOLO ทุกข้อ

## 1. สรุปตามเกณฑ์เสร็จ

| # | เกณฑ์ | ผล | หลักฐาน (หัวข้อ) |
|---|---|---|---|
| 1 | build ของ web | **ผ่าน** | `npm run build` exit 0 · `docker compose build` (Dockerfile รัน `next build`) ผ่าน (§2) |
| 2 | unit test ของ web | **ผ่าน** | `BUG_MODE=0 npm test` 119/119 · `npm run typecheck` ผ่าน (§2) |
| 3 | unit test ของ ai/gateway | **ผ่าน** | 95 ผ่าน, 4 ข้าม (integration) · ตั้ง `RABBITMQ_TEST_URL` แล้ว 99/99 (§3) |
| 4 | unit test ของ ai/worker | **ผ่าน** | 16 ผ่าน, 5 ข้าม (integration) · ตั้ง `RABBITMQ_TEST_URL` แล้ว 21/21 (§3) |
| 5 | unit test ของ ai/train | **ผ่าน** | 30/30 (§3) |
| 6 | `/api/health` เป็น ok | **ผ่าน** | `"status":"ok","db":"ok","storage":"ok","dispatcher":"ok","gateway":"ok","ai_mode":"mock"` (§4) |
| 7 | รีเซ็ตข้อมูลได้ 3 ไซต์ 5 ผู้ใช้ 1233 รูป | **ผ่าน** | `{"reset":true,"sites":3,"users":5,"photos":1233,"overrides":1,…}` ทั้งทาง API และ `docker compose run --rm web npm run seed` (§4) |
| 8 | ล็อกอินครบ 3 บทบาท | **ผ่าน** | 5 บัญชี: manager · supervisor (SITE-A/B/C) · executive · รหัสผิด → 401 ไม่มี cookie (§4) |
| 9 | อัปโหลด h1_v0 / h0_v2 / h0_v1 / h0_v0 ได้ ไม่ผ่าน / ไม่ผ่าน / เตือน / ผ่าน | **ผ่าน** | FAIL (H1 V0) · FAIL (H0 V2) · WARN (H0 V1) · PASS (H0 V0) · จำนวนกรอบ = H + V (§4) |
| 10 | รายงานรายวันตรง TEST-DATA หัวข้อ 3 | **ผ่าน** | P-1 ถึง P-9 ตรงทุกค่า 9 ช่อง (§4.1) |
| 11 | เปิดลิงก์รูปโดยไม่ล็อกอินไม่ได้รูป | **ผ่าน** | `401` `application/json` ไม่มีไบต์รูป · cookie ปลอม → 401 · หัวหน้างานไซต์อื่น → 404 (§4) |
| 12 | โลโก้อยู่ที่ `web/public/logo.png` | **ผ่าน** | คัดลอกจาก `logo.png` · `GET /logo.png` → 200 PNG · หน้า `/login` อ้าง `src="/logo.png"` |
| 13 | ค้นทั้ง repository แล้ว `BUG_MODE` ถูกอ่านที่ `web/lib/rules.ts` ที่เดียว | **ผ่าน** | §5 |
| 14 | `docker-compose.yml` และ `ai/docker-compose.yml` build และ config ผ่าน | **ผ่าน** | config ผ่านทั้งสองไฟล์ · build web, gateway, worker ผ่าน · worker ยังไม่ได้รันบน GPU (§6, §9) |
| 15 | ปิดบริการที่เปิดไว้ | **ผ่าน** | §8 |

นอกขอบเขตของบล็อกนี้ (ไม่ได้ทำ): เช่า GPU · เทรนโมเดลจริง · ทดสอบ SLO ตาม NFR-02 และ NFR-03 · Q-3 ถึง Q-7 กับ GPU จริง

## 2. ฝั่งเว็บ: build และ unit test

```
$ cd web && BUG_MODE=0 npm test
 Test Files  7 passed (7)
      Tests  119 passed (119)
$ npm run typecheck        → exit 0
$ npm run build            → exit 0 (14 API route + 8 หน้า + middleware)
$ docker compose --env-file .env.test --profile test build   → Image sitesafe-web:local Built (exit 0)
```

## 3. ฝั่ง AI: unit test (ไม่มี GPU)

venv ใหม่จาก `ai/requirements-test.txt` (fastapi, aio-pika, pika, pillow, pyyaml, pytest) · ไม่ติดตั้ง ultralytics/torch

| ส่วน | คำสั่ง | ผล | integration (`RABBITMQ_TEST_URL` → RabbitMQ 4 ใน Docker) |
|---|---|---|---|
| ai/gateway | `python -m pytest ai/gateway/tests -q` | 95 passed, 4 skipped | 99 passed |
| ai/worker | `python -m pytest ai/worker/tests -q` | 16 passed, 5 skipped | 21 passed |
| ai/train | `python -m pytest ai/train/tests -q` | 30 passed | – |
| ai/common | `python -m pytest ai/common/tests -q` | 9 passed | – |
| รวม | `python -m pytest ai -q` | 150 passed, 9 skipped | 159 passed |

- worker: ตัวตรวจจำลอง + pika จำลอง ตรวจลำดับ STARTED → DONE/FAILED → ack, รูปเสีย → `IMAGE_UNREADABLE`, ตรวจล้ม → `basic_reject(requeue=True)`, ข้อความผิดรูป → reject ไม่ requeue, publish ไม่ได้ confirm → ไม่ ack, การแปลงชื่อคลาสผ่าน `classes.json`
- worker integration (`test_pipeline_integration.py`): gateway จริง (aio-pika) + RabbitMQ จริง + `run_worker` จริง (pika) + ตัวตรวจจำลอง: งาน DONE ได้ H=1 V=2 และกรอบ 3 กรอบ, ไฟล์ชั่วคราวถูกลบหลังจบ, ส่ง `job_id` ซ้ำ → 200, รูปตัดครึ่ง → FAILED `IMAGE_UNREADABLE`, งานพิษ → FAILED `MAX_RETRIES` (ข้อความเข้า `ppe.jobs.dead` จริง), 20 งานจบครบ
- train: เกณฑ์ Recall 79/80/81 จาก 100 → ไม่ผ่าน/ผ่าน/ผ่าน, Precision < 0.80 ไม่ผ่าน, Test Set < 100 ต่อกลุ่ม → ปฏิเสธ, threshold ต้องมาจาก split val, score เท่ากับ threshold นับ, `main()` เขียน metrics.json และ exit code ตามเกณฑ์ (ultralytics/torch จำลอง)
- common: ค่าคิวของ `ai/common/queues.py` เท่ากับค่าที่ gateway ใช้ (และเท่ากับ fallback ตาม DESIGN 6.1) ทุกค่า `MAX_QUEUE_DEPTH`/`MAX_DELIVERY` ที่ลอง

## 4. ฝั่งเว็บผ่าน HTTP (docker compose profile test)

```bash
cp .env.test.example .env.test
docker compose --env-file .env.test --profile test up -d
python3 scripts/smoke_test.py --test-key <TEST_RESET_KEY ของ .env.test>
```

สถานะบริการ: `db` healthy · `migrate` Exited (0) · `web` healthy · `dispatcher` Up · `mock-gateway` Up
dispatcher ส่งงานไปที่บริการ `mock-gateway` (`GATEWAY_URL=http://mock-gateway:8080`) ไม่ใช่ mock ในตัว

ผลของ `scripts/smoke_test.py` (44 ข้อ ผ่าน 44 · exit 0):

```
PASS  GET /api/health → 200 status ok  · {"status": "ok", "db": "ok", "storage": "ok", "dispatcher": "ok", "gateway": "ok", "ai_mode": "mock", ...}
PASS  health: ai_mode mock · dispatcher ok · gateway ok
PASS  reset with a wrong X-Test-Key → 401
PASS  POST /api/test/reset → 200 · 3 sites · 5 users · 1233 photos · 1 override  · {"reset": true, "sites": 3, "users": 5, "photos": 1233, "overrides": 1, ...}
PASS  login manager@sitesafe.test → role manager
PASS  login sup.a@sitesafe.test → role supervisor · site SITE-A
PASS  login sup.b@sitesafe.test → role supervisor · site SITE-B
PASS  login sup.c@sitesafe.test → role supervisor · site SITE-C
PASS  login exec@sitesafe.test → role executive
PASS  login with a wrong password → 401 without cookie (A-3)
PASS  POST /api/uploads {count: 4} as sup.a → 201
PASS  upload h1_v0.jpg → 201 · upload h0_v2.jpg → 201 · upload h0_v1.jpg → 201 · upload h0_v0.jpg → 201
PASS  h1_v0.jpg → FAIL  · status=DONE result=FAIL H=1 V=0     · detail shows 1 boxes (1 NO_HARDHAT, 0 NO_VEST)
PASS  h0_v2.jpg → FAIL  · status=DONE result=FAIL H=0 V=2     · detail shows 2 boxes (0 NO_HARDHAT, 2 NO_VEST)
PASS  h0_v1.jpg → WARN  · status=DONE result=WARN H=0 V=1     · detail shows 1 boxes (0 NO_HARDHAT, 1 NO_VEST)
PASS  h0_v0.jpg → PASS  · status=DONE result=PASS H=0 V=0     · detail shows 0 boxes
PASS  report 2026-11-16 / 2026-11-17 / 2026-11-18: 3 sites · ready label · รายงานประจำวันพร้อมแล้ว
PASS  report … = TEST-DATA §3 (9 แถว ดู §4.1)
PASS  executive opens the report → 200 with 3 sites (A-9)
PASS  sup.a sees only SITE-A in the report (A-5)
PASS  GET /api/photos/{id}/image without login → 401, no image bytes (A-2)  · HTTP 401 application/json
PASS  … with a forged session cookie → 401
PASS  … as the owner supervisor → 200 image/jpeg · Cache-Control private, no-store
PASS  … as the supervisor of another site → 404 (A-4)
PASS  GET /api/photos without login → 401 (A-1)
PASS  executive POST /api/uploads → 403 (A-7)
PASS  GET /logo.png → 200 image/png
ALL PASSED
```

`model_result` ของทั้ง 4 รูปเท่ากับ `current_result` · ทั้ง 4 รูปเสร็จภายในรอบ poll แรก ๆ (< 2 วินาที)

### 4.1 รายงานรายวันเทียบ TEST-DATA หัวข้อ 3 (ล็อกอินเป็น U-1 · `now` = เวลาจริง 2026-11-19 จึงพร้อมแล้วทั้ง 3 วัน)

| รหัส | วัน · ไซต์ | ถ่าย | มีผล | ผ่าน | ไม่ผ่าน | ผลรวม H | อัตราผ่าน | แดง | ถูกแก้ | ตรวจไม่สำเร็จ | ตรง |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P-1 | D1 · SITE-A | 300 | 300 | 269 | 20 | 15 | 89.67 | แดง | 0 | 0 | ✔ |
| P-2 | D1 · SITE-B | 300 | 300 | 270 | 20 | 20 | 90.00 | ไม่แดง | 0 | 0 | ✔ |
| P-3 | D1 · SITE-C | 300 | 300 | 271 | 20 | 20 | 90.33 | ไม่แดง | 0 | 0 | ✔ |
| P-4 | D2 · SITE-A | 0 | 0 | 0 | 0 | 0 | ไม่มีข้อมูล | ไม่แดง | 0 | 0 | ✔ |
| P-5 | D2 · SITE-B | 10 | 10 | 9 | 0 | 0 | 90.00 | ไม่แดง | 0 | 0 | ✔ |
| P-6 | D2 · SITE-C | 10 | 9 | 9 | 0 | 0 | 100.00 | ไม่แดง | 0 | 1 | ✔ |
| P-7 | D3 · SITE-A | 300 | 300 | 270 | 19 | 15 | 90.00 | ไม่แดง | 1 | 0 | ✔ |
| P-8 | D3 · SITE-B | 12 | 10 | 8 | 1 | 1 | 80.00 | แดง | 0 | 0 | ✔ |
| P-9 | D3 · SITE-C | 1 | 1 | 0 | 1 | 2 | 0.00 | แดง | 0 | 0 | ✔ |

### 4.2 ตรวจเพิ่มเติมกับระบบที่รันอยู่

| เรื่อง | ผล |
|---|---|
| บัญชีฐานข้อมูลของ web/dispatcher (`sitesafe_app`, สมาชิก `sitesafe_web`) สั่ง `UPDATE result_overrides` / `DELETE FROM result_overrides` | `ERROR: permission denied for table result_overrides` ทั้งสองคำสั่ง (NFR-07) |
| `/api/health` อ่าน heartbeat ของ dispatcher ผ่าน `pg_stat_activity` เมื่อทั้งสองใช้บัญชี runtime เดียวกัน | `dispatcher: ok` · `application_name = sitesafe-dispatcher;gw=ok` |
| `docker compose run --rm web npm run seed` (คำสั่งคู่กันของ DESIGN 7.2) | `{"reset":true,"sites":3,"users":5,"photos":1233,"overrides":1}` |
| `GET /login` · `GET /photos` โดยไม่ล็อกอิน | 200 · 307 → `/login?next=%2Fphotos` |
| ค้น log ของทุกบริการหาค่า key/รหัสผ่านใน `.env.test` | ไม่พบ (0 บรรทัด) |

## 5. `BUG_MODE` อ่านที่ `web/lib/rules.ts` ที่เดียว

ค้นทั้ง repository (ยกเว้น `node_modules`, `.next`):

```
$ grep -rnI -E "process\.env(\.|\[['\"])BUG_MODE|environ.*BUG_MODE|getenv\(.?BUG_MODE" .
web/lib/rules.ts:39:const MODE: 0 | 1 = readMode(process.env.BUG_MODE);
```

ไฟล์อื่นที่มีคำนี้เป็นการ **ตั้งค่า** ไม่ใช่การอ่าน: `docker-compose.yml` (ส่ง `BUG_MODE: ${BUG_MODE:-0}` ให้ web/dispatcher ตาม DESIGN 8), `.env.example`, `.env.test.example` (`BUG_MODE=0`), คำอธิบายใน `scripts/smoke_test.py`, `README.md`, `TEST.md` และเอกสารใน `docs/` · unit test `web/tests/single-source.test.ts` ยืนยันซ้ำว่าในซอร์สของ web มีแค่ `lib/rules.ts` · `web/lib/rules.ts` ไม่ถูกแก้ในบล็อกนี้

เส้นแบ่งของ BR: ในฝั่งเว็บ เส้นแบ่งทุกค่าอยู่ใน `web/lib/rules.ts` (ค้น `15728640`, `1048576`, `VEST_*`/`HELMET_*`, `h >=`/`v >=`, `90`, `18:00`, `50` ในโค้ด .ts/.tsx/.sql/.py นอก tests ไม่พบเส้นแบ่งซ้ำ) · dispatcher และ mock-gateway ใช้ `judge()` และ `MAX_FILE_BYTES` จาก `lib/rules`
หมายเหตุ: `web/components/UploadForm.tsx` มี `1024 * 1024` เพื่อแสดงขนาดไฟล์เป็น MB บนหน้าจอเท่านั้น (การตัดสินใช้ `limits.max_file_bytes` จาก API) · `ai/gateway/main.py` มี `MAX_IMAGE_BYTES = 15 * 1024 * 1024` ซึ่งเป็นเพดานของ API 1 ฝั่ง AI ตาม DESIGN 5.1 (`413 FILE_TOO_LARGE`) บนเครื่อง GPU ที่ import ไฟล์ TypeScript ไม่ได้ ค่านี้ไม่ใช้ตัดสินผลของรูป (เว็บตัดสิน BR-05 ก่อนส่ง) ถ้าเปลี่ยน BR-05 ต้องแก้ค่านี้ตามด้วย

## 6. docker compose: config และ build

| ไฟล์ | คำสั่ง | ผล |
|---|---|---|
| `docker-compose.yml` | `docker compose config -q` | ผ่าน |
| `docker-compose.yml` | `docker compose --env-file .env.test.example --profile test config -q` | ผ่าน · services: db, migrate, web, dispatcher, mock-gateway |
| `docker-compose.yml` | `docker compose --env-file .env.test.example --profile test build` | ผ่าน · `sitesafe-web:local` (ใช้ร่วมกัน 4 บริการ) |
| `ai/docker-compose.yml` | `docker compose --env-file .env.example config -q` | ผ่าน · services: rabbitmq, gateway, worker |
| `ai/docker-compose.yml` | `docker compose config -q` โดยไม่มี `.env` | หยุดพร้อมข้อความ `set GATEWAY_API_KEY in ai/.env` / `set CONF_THRESHOLD …` (ตั้งใจ ให้ล้มตั้งแต่ต้น) |
| `ai/docker-compose.yml` | `docker compose --env-file .env.test.example build gateway` | ผ่าน · `sitesafe-gateway:local` |
| `ai/docker-compose.yml` | `docker compose --env-file .env.test.example build worker` | ผ่าน · `sitesafe-worker:local` 9.84 GB (torch 2.5.1+cu124, ultralytics 8.4.215) · ใน container แบบไม่มี network: import `torch`, `ultralytics`, `pika`, `ai.worker.worker`, `ai.common.queues` ได้ · `torch.cuda.is_available()` = False เพราะเครื่องนี้ไม่มี GPU · ไม่มีไฟล์โมเดล → หยุดด้วย `FileNotFoundError` ตามที่ตั้งใจ |

### 6.1 ฝั่ง AI ใน Docker (ไม่มี GPU)

`docker compose --env-file .env.test.example up -d rabbitmq gateway` แล้วรัน worker จำลอง (`ai/worker/tests/fake_worker.py` ใช้ `run_worker` จริง + ตัวตรวจคืน H=1 V=2) ใน container บน network `ai_default` และ volume `ai_ai-data` เดียวกับ gateway:

| ข้อ | ผล |
|---|---|
| gateway ต่อ RabbitMQ | log: `queues from ai.common.queues (arguments)` · worker ประกาศคิวด้วย `declare_queues` ได้โดยไม่มี `PRECONDITION_FAILED` |
| `GET /v1/health` ก่อนมี worker | `503` `{"status":"down","rabbitmq":"ok","workers":0,…}` |
| `GET /v1/health` หลังมี worker | `200` `{"status":"ok","rabbitmq":"ok","workers":1,"queue_depth":0,"max_queue_depth":200,…}` |
| Q-1: `POST /v1/jobs` และ `GET /v1/health` ไม่มี key | `401` ทั้งคู่ |
| Q-2: `GET /v1/jobs/{id}` key ผิด | `401` |
| ส่งรูป 800×600 | `202 QUEUED` → `DONE` · H=1 V=2 · กรอบ 3 · image 800×600 |
| ส่งรูปตัดครึ่ง | `202` → `FAILED` `IMAGE_UNREADABLE` |
| ส่ง `job_id` เดิมซ้ำ · งานที่ไม่มี | `200` · `404` (`GET /v1/jobs?ids=` ให้ใน `not_found`) |
| ไฟล์ชั่วคราวใน `/data/images` หลังงานจบ | ถูกลบหมด (worker อ่านไฟล์ที่ path เดียวกับ gateway ผ่าน volume เดียวกัน, uid 10001) |

### 6.2 ครบวง: dispatcher ของเว็บ → gateway จริง → RabbitMQ → worker loop → เว็บ

หยุด `dispatcher` ของ compose ชั่วคราว แล้วรัน dispatcher จาก image เดียวกันที่ชี้ `GATEWAY_URL=http://gateway:8000` (ต่อ network ของทั้งสองฝั่ง · `AI_MODE=mock` เพื่อยอมรับ http ในการทดสอบนี้เท่านั้น) จากนั้น U-4 อัปโหลด 2 รูปผ่านเว็บ:

| รูป | ผลที่เว็บ |
|---|---|
| `site.jpg` 1024×768 | `DONE` ใน 1.5 วินาที · H=1 V=2 · ผลของโมเดล `FAIL` (ตัดสินที่ `lib/rules`) · `model_version=ppe-yolo-fake` · กรอบ 3 กรอบพิกัดตรงกับที่ worker ส่ง |
| `corrupt_half.jpg` | `FAILED` · เหตุผล "เปิดไฟล์รูปไม่ได้" |

`/api/health` ระหว่างนั้น: `gateway: "ok"` · log ของ gateway ใช้ `photos.id` เป็น `job_id` (D-05) · เสร็จแล้วลบ dispatcher ชั่วคราวและเปิด dispatcher ของ compose กลับ

## 7. สิ่งที่บล็อกนี้แก้หรือเพิ่มเพื่อให้ส่วนต่าง ๆ ต่อกันติด

| ไฟล์ | เหตุผล |
|---|---|
| `web/public/logo.png` | คัดลอกจาก `logo.png` (B09) · เดิม `/logo.png` ตอบ 404 |
| `web/Dockerfile`, `web/.dockerignore` | `docker-compose.yml` อ้าง `build: ./web` แต่ไม่มี Dockerfile |
| `docker-compose.yml` | เดิมอ้าง `build: ./mock-gateway` ที่ไม่มี → ใช้ image เว็บรัน `npm run dispatcher -- --mock-gateway` · เพิ่มบริการ `migrate` (เดิมไม่มีใครสร้าง schema ตอนเริ่ม) · แยกบัญชี DB: `DATABASE_URL` = บัญชี runtime, `DATABASE_OWNER_URL` = เจ้าของตาราง (ตามกระดานของ B02) · ส่ง `web/db/initdb` ให้ PostgreSQL |
| `web/db/initdb/10-runtime-role.sh` | สร้างบัญชี login `sitesafe_app` ใน role `sitesafe_web` ตอนสร้าง volume ครั้งแรก |
| `.env.example`, `.env.test.example` | ค่าตั้งของโหมดจริงและ profile test (`GATEWAY_URL=http://mock-gateway:8080`) |
| `ai/common/queues.py` (+ `ai/common/tests/test_queues.py`) | worker import ไฟล์นี้แต่ไม่มีใครสร้าง (กระดาน B05/B06) · ค่าคิวตรงกับ fallback ของ gateway ทุกค่า |
| `ai/gateway/Dockerfile`, `ai/worker/Dockerfile`, `ai/.dockerignore`, `ai/docker-compose.yml`, `ai/.env.example`, `ai/.env.test.example` | ยังไม่มีมาก่อน · rabbitmq รันด้วย `user: rabbitmq` เพราะเครื่องนี้เริ่มแบบ root แล้วอ่าน `.erlang.cookie` ไม่ได้ (eacces) |
| `ai/worker/requirements.txt`, `ai/train/requirements.txt`, `ai/requirements-test.txt` | ยังไม่มีมาก่อน |
| `ai/worker/classes.json`, `ai/train/classes.json` | ชื่อคลาสตั้งต้น (ค่าเดียวกันทั้งสองไฟล์) · evaluate.py ใช้เป็นค่าเริ่มต้นของ `--classes` |
| `ai/worker/tests/test_worker.py`, `test_pipeline_integration.py`, `fake_worker.py` · `ai/train/tests/test_evaluate.py` | test ที่ B06/B07 รายงานไว้ไม่อยู่ใน repository จึงเขียนใหม่ |
| `scripts/smoke_test.py` | ทดสอบเบื้องต้นผ่าน HTTP ที่รันซ้ำได้ |
| `README.md` | คำสั่งเปิดระบบตามที่ทดสอบจริงในไฟล์นี้ |

ไม่ได้แก้ `web/lib/rules.ts` หรือพฤติกรรมของ `BUG_MODE` · ไม่ได้แก้โค้ดของ dispatcher, gateway, worker, evaluate.py หรือหน้าเว็บ (API Contract และรูปแบบข้อความในคิวของทั้ง 4 ส่วนตรงกันอยู่แล้ว ยืนยันด้วย §3, §6.1, §6.2)

## 8. ปิดบริการหลังทดสอบ

```
docker compose --env-file .env.test --profile test down -v     # ฝั่งเว็บ + volume ทดสอบ
cd ai && docker compose --env-file .env.test.example down -v   # ฝั่ง AI + volume ทดสอบ
docker rm -f b10-rabbit                                         # RabbitMQ ของ integration test
```

ผล: ลบ container `app-*`, `ai-*`, `b10-*` และ volume `app_*`, `ai_*` หมดแล้ว · พอร์ต 3000, 8000, 56730 ปิด (`curl` ต่อไม่ได้) · ลบ `.env.test` ที่คัดลอกไว้ · เก็บ image `sitesafe-web:local`, `sitesafe-gateway:local`, `sitesafe-worker:local` ไว้ใช้ซ้ำ

## 9. ข้อสังเกตที่ยังเหลือ

- worker image (`ai/worker/Dockerfile`) ยังไม่ได้รันบน GPU จริง (เครื่องนี้ไม่มี GPU) · `YoloDetector` ทดสอบด้วย ultralytics จำลองเท่านั้น
- ยังไม่ได้รัน TEST-DATA หัวข้อ 10 Q-3 ถึง Q-7 กับ gateway บนเครื่อง GPU (ต้องใช้ worker จริงและ `MAX_QUEUE_DEPTH=5`) · ส่วนที่เทียบเท่าใน unit/integration test ของ gateway ผ่าน
- ไม่ได้ทดสอบหน้าเว็บด้วยเบราว์เซอร์ในบล็อกนี้ (B08 ทดสอบไว้แล้ว) · ตรวจเฉพาะ `/login` และการ redirect
- ฝั่งเว็บ ↔ gateway ใช้ HTTPS ผ่าน reverse proxy ตาม DESIGN 10 ยังไม่ได้ตั้ง (DQ-03)
