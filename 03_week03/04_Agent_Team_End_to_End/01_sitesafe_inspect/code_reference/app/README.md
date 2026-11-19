# SiteSafe Inspect

ระบบตรวจรูปหน้างานก่อสร้าง: หัวหน้างานอัปโหลดรูป ระบบนับคนไม่ใส่หมวก (H) และคนไม่ใส่เสื้อสะท้อนแสง (V)
แล้วตัดสินผล ผ่าน / เตือน / ไม่ผ่าน ตาม BR-01 ถึง BR-07 แก้ผลได้พร้อมร่องรอย และมีรายงานรายวันต่อไซต์

เอกสาร: `docs/REQUIREMENTS.md` · `docs/DESIGN.md` · `docs/TEST-DATA.md` · `docs/USER-STORIES.md` · ผลทดสอบล่าสุด: `TEST.md`

| ฝั่ง | ที่ตั้ง | ส่วนประกอบ |
|---|---|---|
| เว็บ | เครื่องนี้ · `docker-compose.yml` | `db` (PostgreSQL 16) · `migrate` (สร้าง/ปรับ schema แล้วจบ) · `web` (Next.js) · `dispatcher` · volume `photos` · `mock-gateway` (เฉพาะ profile `test`) |
| AI | เครื่อง GPU ที่เช่า 1 ใบ · `ai/docker-compose.yml` | `gateway` (FastAPI + X-API-Key) · `rabbitmq` · `worker` (YOLO) |

```
web/            Next.js (หน้าเว็บ + /api) · dispatcher/ · db/ (schema, seed, migrate, initdb) · lib/rules.ts (กติกาทั้งหมด)
ai/gateway/     API gateway (DESIGN §5.1) · ai/common/queues.py (ชื่อคิวและค่าคิวที่ gateway กับ worker ใช้ร่วมกัน)
ai/worker/      GPU Worker · classes.json (ชื่อคลาสของโมเดล → NO_HARDHAT / NO_VEST)
ai/train/       evaluate.py (ประเมินโมเดลบน Test Set ตาม NFR-01)
scripts/        smoke_test.py (ทดสอบเบื้องต้นผ่าน HTTP)
```

---

## 1. ฝั่งเว็บ

ต้องมี Docker Engine + Docker Compose v2

### 1.1 ใช้งานจริง (ต่อ gateway จริง)

```bash
cp .env.example .env          # เปลี่ยนรหัสผ่านทุกค่า และตั้ง GATEWAY_URL (https://…), GATEWAY_API_KEY, GATEWAY_CA_CERT
docker compose up -d --build
docker compose ps             # web ต้องเป็น healthy · migrate ต้องเป็น Exited (0)
curl -s http://127.0.0.1:3000/api/health
```

- เว็บเปิดที่ `127.0.0.1:${WEB_PORT:-3000}` ให้ผู้ใช้เข้าผ่าน reverse proxy ที่ทำ HTTPS (cookie ของ session ตั้ง `Secure`)
- ใส่ผู้ใช้ตั้งต้น (ไซต์ 3 แห่ง ผู้ใช้ 5 บัญชี ตาม `docs/TEST-DATA.md`): `docker compose run --rm web npm run seed`
  **คำสั่งนี้ล้างข้อมูลและรูปทั้งหมดก่อนใส่ข้อมูลใหม่** ใช้เฉพาะตอนติดตั้งครั้งแรกหรือระบบทดสอบ
- บัญชีฐานข้อมูลมี 2 บัญชี: เจ้าของตาราง (`sitesafe`, ใช้โดย `migrate` / seed / รีเซ็ตทดสอบ) และบัญชีที่ `web` กับ `dispatcher` ใช้
  (`WEB_DB_USER`, สมาชิกของ `sitesafe_web` ซึ่งไม่มีสิทธิ์ UPDATE / DELETE ตาราง `result_overrides` ตาม NFR-07)
  บัญชีหลังสร้างโดย `web/db/initdb/10-runtime-role.sh` ตอนสร้าง volume `db-data` ครั้งแรกเท่านั้น
  ถ้าเปลี่ยน `WEB_DB_PASSWORD` ภายหลังต้องเปลี่ยนในฐานข้อมูลเองด้วย `ALTER ROLE`
- ปรับ schema หลังอัปเดตโค้ด: บริการ `migrate` รันเองทุกครั้งที่ `docker compose up` (ไม่ลบข้อมูล)

### 1.2 โหมดทดสอบ (profile `test`, ไม่ต้องใช้ GPU)

`AI_MODE=mock` · `ENABLE_TEST_RESET=1` · `BUG_MODE=0` · dispatcher ส่งงานไปที่ `mock-gateway` ซึ่งคืน H, V ตามชื่อไฟล์ `h{H}_v{V}*.jpg`
(`corrupt*.jpg` → ตรวจไม่สำเร็จ · ชื่ออื่น → H = 0, V = 0)

```bash
cp .env.test.example .env.test
docker compose --env-file .env.test --profile test up -d --build
curl -s http://127.0.0.1:3000/api/health                       # "status":"ok","ai_mode":"mock"

# รีเซ็ตข้อมูลทดสอบ (ทุกครั้งก่อนชุดทดสอบ) · ส่ง {"now":"2026-11-18T17:59:00+07:00"} เพื่อตั้งนาฬิกาได้
curl -s -X POST http://127.0.0.1:3000/api/test/reset \
     -H "X-Test-Key: $(grep ^TEST_RESET_KEY .env.test | cut -d= -f2)" \
     -H 'Content-Type: application/json' -d '{}'
# → {"reset":true,"sites":3,"users":5,"photos":1233,"overrides":1,"now":"…"}

# ทดสอบเบื้องต้นผ่าน HTTP (Python 3 มาตรฐาน ไม่ต้องติดตั้งเพิ่ม)
python3 scripts/smoke_test.py --test-key "$(grep ^TEST_RESET_KEY .env.test | cut -d= -f2)"

# ปิด (เพิ่ม -v ถ้าต้องการลบฐานข้อมูลและรูปทดสอบทิ้งด้วย)
docker compose --env-file .env.test --profile test down
```

บัญชีทดสอบอยู่ใน `docs/TEST-DATA.md` หัวข้อ 2 · หลังรีเซ็ตทุกครั้ง session เดิมหายหมด ต้องล็อกอินใหม่
ชุดทดสอบ E2E ต้องเข้าเว็บผ่าน `localhost` / `127.0.0.1` หรือ HTTPS เพราะเบราว์เซอร์ไม่เก็บ cookie `Secure` บน `http://` ชื่ออื่น

### 1.3 พัฒนาโดยไม่ใช้ Docker

```bash
cd web
npm ci
npm test              # vitest (unit test)
npm run typecheck
npm run build
# รันจริงต้องมี PostgreSQL: DATABASE_URL (บัญชี runtime) และ DATABASE_OWNER_URL (เจ้าของตาราง), PHOTOS_DIR
npm run migrate && npm start          # เว็บที่พอร์ต 3000
npm run dispatcher                    # กระบวนการแยก · AI_MODE=mock และไม่ตั้ง GATEWAY_URL = ใช้ mock ในตัวบน loopback
npm run dispatcher -- --mock-gateway  # mock-gateway แบบแยกที่พอร์ต 8080 (MOCK_GATEWAY_PORT)
```

ค่าตั้งทั้งหมดอยู่ใน `docs/DESIGN.md` หัวข้อ 11 · `BUG_MODE` ต้องเป็น `0` ในการใช้งานทุกกรณี (DESIGN หัวข้อ 8)

---

## 2. ฝั่ง AI (เครื่อง GPU)

ต้องมี Docker + NVIDIA Container Toolkit และไฟล์โมเดลที่ผ่านเกณฑ์ NFR-01

```bash
cd ai
cp .env.example .env      # GATEWAY_API_KEY (ค่าเดียวกับฝั่งเว็บ), RABBITMQ_PASSWORD, CONF_THRESHOLD, MODEL_VERSION
mkdir -p models && cp /path/to/best.pt models/best.pt
# แก้ worker/classes.json ถ้าชื่อคลาสของโมเดลไม่อยู่ในรายการ (ต้องมีทั้ง NO_HARDHAT และ NO_VEST) แล้ว build ใหม่
docker compose up -d --build
curl -s -H "X-API-Key: <key>" http://127.0.0.1:8000/v1/health     # "status":"ok","workers":1,"gpu":"…"
```

- gateway เปิดที่ `127.0.0.1:${GATEWAY_PORT:-8000}` เท่านั้น ให้เปิดสู่ภายนอกผ่าน reverse proxy ที่ทำ TLS
  แล้วตั้ง `GATEWAY_URL=https://…` และ `GATEWAY_CA_CERT` ที่ฝั่งเว็บ (DESIGN หัวข้อ 10)
- ไม่ตั้ง `GATEWAY_API_KEY` หรือ `CONF_THRESHOLD` แล้ว `docker compose` จะหยุดพร้อมบอกชื่อตัวแปร
- `MAX_QUEUE_DEPTH` / `MAX_DELIVERY` ต้องตรงกันทั้ง gateway และ worker (compose ส่งค่าเดียวกันให้ทั้งคู่ผ่าน `ai/common/queues.py`)
  ถ้าเปลี่ยนภายหลังต้องลบคิว `ppe.jobs` ตอนว่างก่อน: `docker compose exec rabbitmq rabbitmqctl delete_queue ppe.jobs`
- `rabbitmq` รันด้วย `user: rabbitmq` เพราะบางเครื่อง (เช่น Docker บน WSL) เริ่มแบบ root แล้วอ่าน `.erlang.cookie` ไม่ได้

### 2.1 ตรวจฝั่ง AI โดยไม่มี GPU

```bash
cd ai
cp .env.test.example .env.test
docker compose --env-file .env.test up -d --build rabbitmq gateway
# worker จำลอง: ใช้ลูปของ worker จริง แต่ตัวตรวจคืน H = FAKE_H, V = FAKE_V ทุกรูป
docker run -d --name sitesafe-fake-worker --network ai_default -v ai_ai-data:/data:ro -v "$PWD":/app/ai:ro -w /app \
  -e RABBITMQ_URL=amqp://sitesafe:sitesafe-mq-test@rabbitmq:5672/ -e FAKE_H=1 -e FAKE_V=2 \
  --user root --entrypoint sh sitesafe-gateway:local \
  -c "pip install -q pika pillow && exec python -m ai.worker.tests.fake_worker"
curl -s -H "X-API-Key: ai-gateway-test-key" http://127.0.0.1:8000/v1/health    # "workers":1
docker rm -f sitesafe-fake-worker && docker compose --env-file .env.test down
```

### 2.2 Unit test ฝั่ง AI (CPU)

```bash
python3 -m venv .venv && .venv/bin/pip install -r ai/requirements-test.txt
.venv/bin/python -m pytest ai -q        # gateway · worker · train · common (ตัวตรวจจำลอง ไม่ต้องมี ultralytics)

# รวม integration test กับ RabbitMQ จริง (gateway + worker + คิว)
docker run -d --name rabbit-test --user rabbitmq -p 127.0.0.1:56720:5672 rabbitmq:4-management
docker exec rabbit-test rabbitmqctl await_startup
docker exec rabbit-test rabbitmqctl add_user t t
docker exec rabbit-test rabbitmqctl set_permissions -p / t ".*" ".*" ".*"
RABBITMQ_TEST_URL=amqp://t:t@127.0.0.1:56720/ .venv/bin/python -m pytest ai -q
docker rm -f rabbit-test
```

### 2.3 ประเมินโมเดล (NFR-01)

```bash
pip install -r ai/train/requirements.txt
python ai/train/evaluate.py --data dataset/data.yaml --model runs/best.pt --model-version ppe-yolo-v1 \
       --threshold threshold.json --classes ai/train/classes.json --device 0 --output metrics.json
# threshold.json: {"conf_threshold": 0.5, "split": "val"} (เลือกจาก Validation Set) · exit 0 = ผ่านเกณฑ์ Recall/Precision ≥ 0.80
```
