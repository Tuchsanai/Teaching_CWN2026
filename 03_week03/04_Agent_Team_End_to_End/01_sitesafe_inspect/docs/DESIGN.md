# Design · SiteSafe Inspect

**ที่มา:** `docs/REQUIREMENTS.md` (FR-01 ถึง FR-22 · BR-01 ถึง BR-07 · NFR-01 ถึง NFR-08 · AS-01 ถึง AS-14)
**สถานะ:** ร่างรุ่นแรก ยังไม่มีโค้ด
**เอกสารคู่กัน:** `docs/TEST-DATA.md` (ข้อมูลทดสอบและผลที่คาดหวัง)

## 0. ภาพรวมและข้อตัดสินใจหลัก

ระบบแบ่งเป็น 2 ฝั่ง

| ฝั่ง | ที่ตั้ง | ส่วนประกอบ | หน้าที่ |
|---|---|---|---|
| เว็บ | เครื่องนี้ รันด้วย `docker compose` | `web` (Next.js) · `dispatcher` (image เดียวกับ web) · `db` (PostgreSQL) · volume `photos` | ล็อกอิน สิทธิ์ รับและเก็บรูปต้นฉบับ ตัดสินผลตาม Business Rule แก้ผล รายงาน |
| AI | เครื่อง GPU ที่เช่า 1 ใบ | `gateway` (API gateway) · `rabbitmq` · `worker` (GPU Worker 1 ตัว ใช้โมเดล YOLO) | รับงานตรวจรูป เข้าคิว ตรวจหา แล้วคืนค่า H, V และกรอบ |

| ข้อ | ข้อตัดสินใจ | เหตุผล | อ้าง |
|---|---|---|---|
| D-01 | เว็บเก็บรูปต้นฉบับลง volume และเขียนแถวในฐานข้อมูลให้เสร็จก่อนตอบผู้อัปโหลดว่ารับแล้ว | รูปห้ามหายแม้ฝั่ง AI ใช้ไม่ได้ | NFR-04 |
| D-02 | การส่งรูปไปฝั่ง AI ทำโดย `dispatcher` ที่ทำงานเบื้องหลัง ไม่ผูกกับหน้าจอของผู้ใช้ | ผู้ใช้ปิดหน้าจอแล้วงานยังเดินต่อ | FR-05 |
| D-03 | ฝั่ง AI คืนเฉพาะสิ่งที่โมเดลเห็น (H, V, กรอบ) การตัดสิน "ผ่าน / เตือน / ไม่ผ่าน" ทำที่เว็บในไฟล์กติกาไฟล์เดียว | เส้นแบ่งของ BR เปลี่ยนได้โดยแก้ค่าเดียว (AS-03) และไม่ต้องแตะฝั่ง AI | FR-09, BR-01–03 |
| D-04 | เว็บเป็นฝ่ายถามสถานะจาก gateway (polling) ฝั่ง AI ไม่เรียกกลับมาที่เว็บ | เครื่องที่เช่าไม่ต้องรู้ที่อยู่ของเว็บ และเว็บไม่ต้องเปิดพอร์ตรับจากภายนอก | NFR-05 |
| D-05 | รหัสงานของ gateway (`job_id`) คือ `photos.id` ที่เว็บสร้างเอง | ส่งซ้ำกี่ครั้งก็เป็นงานเดียว (idempotent) ผลของโมเดลจึงมีชุดเดียว | NFR-04 |
| D-06 | คิวเป็น RabbitMQ quorum queue แบบ durable · Worker ยืนยัน (ack) หลังส่งผลสำเร็จเท่านั้น | Worker ล่มกลางงาน งานกลับเข้าคิวเอง | NFR-04 |
| D-07 | gateway ปฏิเสธงานใหม่ด้วย 429 เมื่องานค้าง ≥ `MAX_QUEUE_DEPTH` · เว็บเก็บรูปนั้นไว้ที่ "รอคิว" แล้วส่งใหม่ภายหลัง | คิวไม่โตจนล้นหน่วยความจำ และผู้ใช้ไม่เสียรูป | NFR-03, NFR-04 |
| D-08 | กรอบแจ้งปัญหาวาดทับรูปที่หน้าเว็บจากพิกัดในฐานข้อมูล ไม่สร้างไฟล์รูปชุดที่สอง | รูปต้นฉบับไม่ถูกแก้ และไม่เพิ่มพื้นที่เก็บ | FR-07 |
| D-09 | รายงานรายวันคำนวณสดจากตาราง `photos` ทุกครั้งที่เปิด | เปิดดูได้ตลอด จึงพร้อมก่อน 18:00 น. เสมอ และรูปที่เข้าหลัง 18:00 น. ถูกนับเอง | BR-07, FR-17 |

---

## 1. Architecture

```mermaid
flowchart LR
  subgraph USERS["ผู้ใช้ (เบราว์เซอร์)"]
    SUP["หัวหน้างานไซต์"]
    MGR["ผู้จัดการความปลอดภัย"]
    EXE["ผู้บริหาร"]
  end

  subgraph LOCAL["เครื่องนี้ · docker compose"]
    WEB["web<br/>Next.js: หน้าจอ + /api"]
    DSP["dispatcher<br/>ส่งงานและถามสถานะ"]
    DB[("db<br/>PostgreSQL")]
    VOL[("volume photos<br/>รูปต้นฉบับ")]
    MOCK["mock-gateway<br/>(เฉพาะ profile test)"]
  end

  subgraph GPU["เครื่อง GPU ที่เช่า · 1 ใบ"]
    GW["gateway<br/>API gateway + ตรวจ API key"]
    JOBS[("jobs.db + ไฟล์รูปชั่วคราว")]
    MQ[["RabbitMQ<br/>ppe.jobs · ppe.results · ppe.jobs.dead"]]
    WK["GPU Worker<br/>YOLO"]
  end

  SUP -->|HTTPS| WEB
  MGR -->|HTTPS| WEB
  EXE -->|HTTPS| WEB
  WEB --> DB
  WEB --> VOL
  DSP --> DB
  DSP --> VOL
  DSP -->|"HTTPS + X-API-Key<br/>POST /v1/jobs · GET /v1/jobs"| GW
  DSP -.->|"AI_MODE=mock"| MOCK
  GW --> JOBS
  GW -->|publish งาน| MQ
  MQ -->|consume ทีละ 1 งาน| WK
  WK -->|อ่านรูป| JOBS
  WK -->|publish ผล| MQ
  MQ -->|consume ผล| GW
```

| ส่วน | เทคโนโลยี | เก็บอะไร | หมายเหตุ |
|---|---|---|---|
| `web` | Next.js (App Router, Route Handler) | – | ตรวจ session และสิทธิ์ทุกคำขอที่ฝั่งเซิร์ฟเวอร์ (NFR-06) |
| `dispatcher` | Node.js กระบวนการแยก ใช้โค้ดชุดเดียวกับ web | – | วนทุก 1 วินาที: ส่งรูปที่ยังไม่ได้ส่ง · ถามสถานะงานที่ค้าง · เฝ้ารูปที่ค้างเกินเวลา |
| `db` | PostgreSQL | 7 ตาราง (หัวข้อ 2) | volume ถาวร |
| volume `photos` | ระบบไฟล์ | รูปต้นฉบับ `photos/{site}/{yyyy-mm-dd}/{photo_id}.{ext}` | เข้าถึงได้ผ่าน `/api/photos/{id}/image` เท่านั้น ไม่มีเส้นทาง static |
| `mock-gateway` | บริการจำลองที่ทำตาม API Contract เดียวกับ gateway จริง | – | ใช้เมื่อ `AI_MODE=mock` คืนค่า H, V ตามชื่อไฟล์ (หัวข้อ 7.3) |
| `gateway` | HTTP API | `jobs.db` (SQLite 1 ตาราง: สถานะและผลของงาน) + ไฟล์รูปชั่วคราว | ลบไฟล์รูปชั่วคราวเมื่องานจบ เก็บผลไว้ 24 ชั่วโมง |
| `rabbitmq` | RabbitMQ | คิว 3 คิว (หัวข้อ 6) | volume ถาวร |
| `worker` | Python + YOLO บน GPU 1 ใบ | – | โหลดโมเดลครั้งเดียวตอนเริ่ม รับงานทีละ 1 งาน |

---

## 2. ER Diagram (PostgreSQL ฝั่งเว็บ · 7 ตาราง)

```mermaid
erDiagram
  sites ||--o{ users : "สังกัด"
  sites ||--o{ upload_batches : "มี"
  sites ||--o{ photos : "มี"
  users ||--o{ sessions : "ล็อกอิน"
  users ||--o{ upload_batches : "อัปโหลด"
  upload_batches ||--o{ photos : "ประกอบด้วย"
  photos ||--o{ detections : "ตรวจพบ"
  photos ||--o{ result_overrides : "ถูกแก้ผล"
  users ||--o{ result_overrides : "เป็นผู้แก้"

  sites {
    int id PK
    text code UK "SITE-A"
    text name
  }
  users {
    int id PK
    text email UK
    text password_hash "argon2id"
    text full_name
    text role "manager | supervisor | executive"
    int site_id FK "มีค่าเฉพาะ supervisor"
    boolean is_active
  }
  sessions {
    text token_hash PK
    int user_id FK
    timestamptz expires_at
  }
  upload_batches {
    uuid id PK
    int site_id FK
    int uploaded_by FK
    int declared_count "1 ถึง 50"
    timestamptz created_at
  }
  photos {
    uuid id PK "ใช้เป็น job_id ของ gateway"
    uuid batch_id FK
    int site_id FK
    int uploaded_by FK
    date upload_date "วันตามเวลาประเทศไทย"
    text original_filename
    text mime "image/jpeg | image/png"
    bigint size_bytes
    text sha256
    text storage_path
    text status "QUEUED | PROCESSING | DONE | FAILED"
    text fail_reason
    text dispatch_state "PENDING | SUBMITTED | CLOSED"
    int submit_attempts
    timestamptz accepted_at
    timestamptz submitted_at
    timestamptz finished_at
    int model_h
    int model_v
    text model_result "PASS | WARN | FAIL ไม่ถูกเขียนทับ"
    text current_result "ผลล่าสุด"
    boolean is_overridden
    text model_version
    numeric conf_threshold
    int image_w
    int image_h
  }
  detections {
    bigint id PK
    uuid photo_id FK
    text cls "NO_HARDHAT | NO_VEST"
    numeric confidence
    int x1
    int y1
    int x2
    int y2
  }
  result_overrides {
    bigint id PK
    uuid photo_id FK
    int edited_by FK
    timestamptz edited_at
    text result_before
    text result_after
    text reason "ห้ามว่าง"
  }
```

| ตาราง | กติกาของข้อมูล |
|---|---|
| `users` | `role = supervisor` ต้องมี `site_id` · บทบาทอื่น `site_id` เป็น NULL · สร้างด้วยสคริปต์ seed ของฝ่ายไอทีเท่านั้น ไม่มีหน้าสมัคร (AS-13) |
| `upload_batches` | CHECK `declared_count BETWEEN 1 AND 50` · จำนวนแถว `photos` ต่อ batch ไม่เกิน `declared_count` |
| `photos` | `site_id` และ `upload_date` มาจากบัญชีผู้อัปโหลดและเวลาเซิร์ฟเวอร์ (Asia/Bangkok) ผู้ใช้ส่งมาเองไม่ได้ (FR-04) · `model_*` เขียนได้ครั้งเดียวตอนเปลี่ยนเป็น `DONE` · index `(site_id, upload_date, current_result)` สำหรับรายงาน |
| `detections` | เขียนใน transaction เดียวกับการเปลี่ยน `photos.status` เป็น `DONE` จึงมีผลของโมเดลชุดเดียวต่อรูป |
| `result_overrides` | เพิ่มได้อย่างเดียว: บัญชีฐานข้อมูลของเว็บถูกถอนสิทธิ์ UPDATE และ DELETE บนตารางนี้ และไม่มี API สำหรับลบหรือแก้ (NFR-07) |
| รายงานรายวัน | ไม่เป็นตาราง เป็น query รวมจาก `photos` ตาม `(site_id, upload_date)` |

ฝั่ง AI มีตาราง `jobs` 1 ตารางใน `jobs.db` ของ gateway (`job_id` · `status` · `queued_at` · `started_at` · `finished_at` · `result_json` · `error_code` · `delivery_count`) ไม่นับรวมใน 7 ตารางข้างต้น

---

## 3. ลำดับการทำงาน: อัปโหลดรูปจนเห็นผล

```mermaid
sequenceDiagram
  autonumber
  actor U as หัวหน้างาน
  participant W as web
  participant D as db + volume
  participant P as dispatcher
  participant G as gateway
  participant Q as RabbitMQ
  participant K as GPU Worker

  U->>W: POST /api/uploads (จำนวนรูปที่จะส่ง)
  W->>W: ตรวจสิทธิ์ และจำนวน ≤ 50 (BR-06)
  W->>D: สร้าง upload_batches
  W-->>U: 201 batch_id

  loop ทีละรูป (ส่งขนานไม่เกิน 3 รูป)
    U->>W: POST /api/uploads/{batch_id}/photos (ไฟล์)
    W->>W: ตรวจชนิดไฟล์ (FR-02) และขนาด ≤ 15 MB (BR-05)
    W->>D: เขียนไฟล์ลง volume แล้ว INSERT photos (QUEUED, PENDING)
    W-->>U: 201 รับรูปแล้ว (เริ่มนับเวลารอผล)
  end

  loop ทุก 1 วินาที
    P->>D: อ่านรูปที่ dispatch_state = PENDING
    P->>G: POST /v1/jobs (job_id = photo_id, รูป) + X-API-Key
    alt คิวยังไม่เต็ม
      G->>G: เก็บไฟล์ชั่วคราว + INSERT jobs (QUEUED)
      G->>Q: publish งานลง ppe.jobs (persistent, รอ confirm)
      G-->>P: 202 QUEUED
      P->>D: dispatch_state = SUBMITTED
    else คิวเต็ม
      G-->>P: 429 QUEUE_FULL + Retry-After
      P->>D: คงสถานะ QUEUED / PENDING แล้วลองใหม่ตาม Retry-After
    end
  end

  Q->>K: ส่งงาน 1 งาน (prefetch = 1)
  K->>Q: publish "เริ่มตรวจ" ลง ppe.results
  Q->>G: jobs.status = PROCESSING
  K->>K: YOLO ตรวจรูป นับ H และ V
  K->>Q: publish ผล ลง ppe.results (รอ confirm)
  K->>Q: ack งาน
  Q->>G: jobs.status = DONE + result_json

  loop ทุก 1 วินาที
    P->>G: GET /v1/jobs?ids=... + X-API-Key
    G-->>P: สถานะและผลของแต่ละงาน
    P->>D: transaction: detections + model_h, model_v + ตัดสินผลตาม BR-01–03 + status = DONE
  end

  loop ทุก 2 วินาที ขณะหน้าจอเปิดอยู่
    U->>W: GET /api/uploads/{batch_id}
    W-->>U: สถานะและผลของทุกรูป (แสดงทีละรูปที่เสร็จ, FR-10)
  end
```

---

## 4. สถานะของงาน

สถานะที่ผู้ใช้เห็นมี 4 ค่าตาม FR-06 เก็บที่ `photos.status`

```mermaid
stateDiagram-v2
  state "รอคิว (QUEUED)" as QUEUED
  state "กำลังตรวจ (PROCESSING)" as PROCESSING
  state "เสร็จแล้ว (DONE)" as DONE
  state "ตรวจไม่สำเร็จ (FAILED)" as FAILED

  [*] --> QUEUED: เว็บเก็บรูปและตอบว่ารับแล้ว
  QUEUED --> QUEUED: gateway ตอบ 429 หรือเชื่อมต่อไม่ได้ (ส่งใหม่ภายหลัง)
  QUEUED --> PROCESSING: Worker หยิบงาน
  PROCESSING --> QUEUED: Worker ล่มกลางงาน (งานกลับเข้าคิว)
  PROCESSING --> DONE: ได้ H, V และกรอบ แล้วตัดสินผล
  PROCESSING --> FAILED: เปิดไฟล์รูปไม่ได้
  PROCESSING --> FAILED: ลองครบ 3 ครั้ง (งานเข้า ppe.jobs.dead)
  QUEUED --> FAILED: ค้างเกิน 15 นาที
  PROCESSING --> FAILED: ค้างเกิน 15 นาที
  DONE --> [*]
  FAILED --> [*]
```

| กติกาของสถานะ | รายละเอียด |
|---|---|
| สถานะปลายทาง | `DONE` และ `FAILED` เปลี่ยนต่อไม่ได้ คำสั่ง UPDATE ทุกคำสั่งมีเงื่อนไข `WHERE status IN ('QUEUED','PROCESSING')` ผลที่มาถึงช้าหรือมาซ้ำจึงถูกทิ้ง |
| `FAILED` ต้องมีเหตุผล | `fail_reason` หนึ่งในค่า: "เปิดไฟล์รูปไม่ได้" · "ตรวจซ้ำครบ 3 ครั้งแล้วไม่สำเร็จ" · "เกินเวลา 15 นาที" |
| การแก้ผลโดยคน | ไม่ใช่สถานะของงาน: รูปที่ `DONE` มี `current_result` และ `is_overridden` เปลี่ยนได้ผ่าน `result_overrides` ส่วน `model_result` คงเดิม (FR-14) |
| ยอดรวม | รูปที่ระบบรับแล้ว = จำนวนแถว `photos` = QUEUED + PROCESSING + DONE + FAILED เสมอ เพราะเป็นคอลัมน์เดียว (NFR-04) |
| สถานะย่อยของการส่ง | `dispatch_state`: `PENDING` (ยังไม่ถึง gateway) → `SUBMITTED` (gateway ตอบ 202 หรือ 200) → `CLOSED` (ถึงสถานะปลายทาง) · ถ้า gateway ตอบ 404 สำหรับงานที่ `SUBMITTED` ให้กลับเป็น `PENDING` เพื่อส่งใหม่ |

---

## 5. API Contract

### 5.1 เว็บ ↔ gateway (4 API)

ข้อกำหนดร่วม

| เรื่อง | ข้อกำหนด |
|---|---|
| ที่อยู่ | `GATEWAY_URL` ในไฟล์ `.env` ของเว็บ เป็น `https://` เท่านั้น |
| API key | ทุกคำขอส่ง header `X-API-Key: <key>` · ค่าเก็บใน `.env` ของทั้งสองฝั่ง (`GATEWAY_API_KEY`) · ผู้เรียกมีเฉพาะ `dispatcher` เบราว์เซอร์ไม่เคยได้รับ key |
| ไม่มี key หรือ key ผิด | `401` `{"error":"UNAUTHORIZED"}` สำหรับทุกเส้นทาง รวม `/v1/health` · เทียบแบบ constant-time · ไม่เขียนค่า key ลง log |
| รูปแบบข้อมูล | คำตอบเป็น JSON (UTF-8) · เวลาเป็น ISO 8601 UTC |
| ข้อผิดพลาด | `{"error":"<CODE>","message":"<ข้อความ>"}` |

**API 1 · ส่งรูป** `POST /v1/jobs` (`multipart/form-data`)

| ช่อง | ชนิด | ความหมาย |
|---|---|---|
| `job_id` | UUID | เท่ากับ `photos.id` ใช้กันงานซ้ำ |
| `image` | ไฟล์ JPG หรือ PNG ไม่เกิน 15 MB | รูปต้นฉบับ |
| `sha256` | ข้อความ | gateway ตรวจว่าไฟล์มาครบ |

| รหัส | เมื่อไร | เนื้อคำตอบ |
|---|---|---|
| `202` | รับงานใหม่และ publish ลงคิวสำเร็จ | `{"job_id":"…","status":"QUEUED","queue_depth":37}` |
| `200` | `job_id` นี้มีอยู่แล้ว (ส่งซ้ำ) ไม่สร้างงานใหม่ | สถานะปัจจุบันของงาน รูปแบบเดียวกับ API 2 |
| `400` | ขาดช่อง หรือ `sha256` ไม่ตรง | `BAD_REQUEST` |
| `401` | ไม่มี key หรือ key ผิด | `UNAUTHORIZED` |
| `413` / `415` | ไฟล์เกิน 15 MB / ไม่ใช่ JPG, PNG | `FILE_TOO_LARGE` / `UNSUPPORTED_TYPE` |
| `429` | คิวเต็ม (หัวข้อ 6.3) ไม่เก็บไฟล์ ไม่สร้างงาน | `{"error":"QUEUE_FULL","queue_depth":200,"max_queue_depth":200,"retry_after_s":20}` พร้อม header `Retry-After: 20` |
| `503` | RabbitMQ ใช้ไม่ได้ หรือ publish ไม่ได้รับ confirm | `QUEUE_UNAVAILABLE` (ไม่สร้างงาน เว็บส่งใหม่ภายหลัง) |

**API 2 · ถามสถานะ 1 งาน** `GET /v1/jobs/{job_id}`

```json
{
  "job_id": "5b0e…",
  "status": "DONE",
  "queued_at": "2026-11-18T03:00:01Z",
  "started_at": "2026-11-18T03:00:04Z",
  "finished_at": "2026-11-18T03:00:05Z",
  "result": {
    "h": 1,
    "v": 0,
    "detections": [
      {"cls": "NO_HARDHAT", "confidence": 0.87, "box": [412, 130, 596, 380]}
    ],
    "image_w": 4000,
    "image_h": 3000,
    "model_version": "ppe-yolo-v1",
    "conf_threshold": 0.5,
    "infer_ms": 41
  },
  "error": null
}
```

| ช่อง | ค่า |
|---|---|
| `status` | `QUEUED` · `PROCESSING` · `DONE` · `FAILED` |
| `result` | มีค่าเมื่อ `DONE` เท่านั้น · `h` = จำนวนกรอบคลาส `NO_HARDHAT` · `v` = จำนวนกรอบคลาส `NO_VEST` ที่ confidence ≥ `conf_threshold` · `box` = `[x1, y1, x2, y2]` เป็นพิกเซลของรูปต้นฉบับ |
| `error` | มีค่าเมื่อ `FAILED`: `{"code":"IMAGE_UNREADABLE" หรือ "MAX_RETRIES","message":"…"}` |
| รหัสคำตอบ | `200` พบงาน · `404` `JOB_NOT_FOUND` (เว็บจะส่งรูปนั้นใหม่) · `401` |

**API 3 · ถามสถานะหลายงาน** `GET /v1/jobs?ids=<job_id คั่นด้วยจุลภาค ไม่เกิน 100 รายการ>`
คำตอบ `200` `{"jobs":[ …รูปแบบเดียวกับ API 2… ],"not_found":["…"]}`

**API 4 · สุขภาพของฝั่ง AI** `GET /v1/health`
คำตอบ `200` `{"status":"ok","rabbitmq":"ok","workers":1,"queue_depth":37,"max_queue_depth":200,"gpu":"<รุ่น GPU>","model_version":"ppe-yolo-v1"}` (รุ่น GPU ใช้ระบุในผลทดสอบตาม NFR-08) · `503` เมื่อ RabbitMQ ใช้ไม่ได้หรือไม่มี Worker

**พฤติกรรมของเว็บต่อคำตอบของ gateway**

| คำตอบ | สิ่งที่ `dispatcher` ทำ | สิ่งที่ผู้ใช้เห็น |
|---|---|---|
| `202` / `200` | `dispatch_state = SUBMITTED` | "รอคิว" |
| `429` | รอตาม `Retry-After` แล้วส่งใหม่ (เพิ่มช่วงรอได้ถึง 60 วินาที) | "รอคิว" |
| `503` / timeout / เชื่อมต่อไม่ได้ | ส่งใหม่แบบ backoff 2, 4, 8 … 60 วินาที | "รอคิว" |
| `401` | หยุดส่ง เขียน log ระดับ error (ไม่มีค่า key) และ `/api/health` รายงาน `gateway: "unauthorized"` | "รอคิว" จนครบ 15 นาทีแล้วเป็น "ตรวจไม่สำเร็จ" |
| `413` / `415` / `400` | `FAILED` พร้อมเหตุผล | "ตรวจไม่สำเร็จ" |
| `404` ตอนถามสถานะ | `dispatch_state = PENDING` เพื่อส่งใหม่ | "รอคิว" |

### 5.2 เบราว์เซอร์ ↔ เว็บ (14 API)

ทุกเส้นทางยกเว้น 3 เส้นทางที่ระบุ ต้องมี session cookie (`HttpOnly` · `Secure` · `SameSite=Lax`) ไม่มี → `401` · บทบาทไม่มีสิทธิ์ → `403` · ทรัพยากรของไซต์อื่น → `404`

| # | Method และเส้นทาง | สิทธิ์ | หน้าที่ | อ้าง |
|---|---|---|---|---|
| 1 | `GET /api/health` | ไม่ต้องล็อกอิน | สุขภาพของเว็บ (หัวข้อ 7.1) | – |
| 2 | `POST /api/auth/login` | ไม่ต้องล็อกอิน | อีเมล + รหัสผ่าน → ตั้ง cookie · ผิด → `401` ข้อความเดียวกันทั้งอีเมลผิดและรหัสผ่านผิด | FR-18 |
| 3 | `POST /api/auth/logout` | ทุกบทบาท | ลบ session | FR-18 |
| 4 | `GET /api/auth/me` | ทุกบทบาท | ชื่อ บทบาท ไซต์ของผู้ใช้ | – |
| 5 | `POST /api/uploads` | supervisor | เปิดการอัปโหลด: `{"count": n}` · `n` > 50 → `422 TOO_MANY_PHOTOS` "ส่งได้ครั้งละไม่เกิน 50 รูป กรุณาแบ่งส่ง" · `n` < 1 → `422` | FR-01, BR-06 |
| 6 | `POST /api/uploads/{batchId}/photos` | supervisor เจ้าของ batch | รับ 1 ไฟล์: ตรวจชนิดจากเนื้อไฟล์ (magic bytes) → `415` · ขนาด > 15 MB → `413` "ขนาดสูงสุด 15 MB" · เกิน `declared_count` → `422` · สำเร็จ → `201` หลังเก็บไฟล์แล้ว | FR-02, FR-03, BR-05 |
| 7 | `GET /api/uploads/{batchId}` | ผู้เห็นไซต์นั้นได้ | รายการสถานะและผลของทุกรูปใน batch | FR-06, FR-10 |
| 8 | `GET /api/photos?date=&site=&result=&status=&problems=1&page=` | manager ทุกไซต์ · supervisor ไซต์ตัวเอง | รายการรูป · `problems=1` ได้เฉพาะ "ไม่ผ่าน" และ "เตือน" | FR-11, FR-12 |
| 9 | `GET /api/photos/{id}` | เหมือนข้อ 8 | รายละเอียด: H, V, กรอบ, ผลของโมเดล, ผลล่าสุด | FR-07, FR-08 |
| 10 | `GET /api/photos/{id}/image` | เหมือนข้อ 8 | ส่งไฟล์รูป · header `Cache-Control: private, no-store` | FR-22 |
| 11 | `POST /api/photos/{id}/overrides` | manager ทุกไซต์ · supervisor ไซต์ตัวเอง | `{"result":"PASS|WARN|FAIL","reason":"…"}` · เหตุผลว่าง → `422` · ผลเท่าผลล่าสุด → `422` · รูปยังไม่ `DONE` → `422` | FR-13 |
| 12 | `GET /api/photos/{id}/overrides` | manager ทุกไซต์ · supervisor ไซต์ตัวเอง | ประวัติการแก้ผล เรียงตามเวลา | FR-14 |
| 13 | `GET /api/reports/daily?date=` | manager และ executive ทุกไซต์ · supervisor ไซต์ตัวเอง | รายงานรายวันต่อไซต์ (หัวข้อ 9.2) | FR-15–17 |
| 14 | `POST /api/test/reset` | ไม่ใช้ session ใช้ `X-Test-Key` | รีเซ็ตข้อมูลทดสอบ (หัวข้อ 7.2) | – |

ผู้บริหาร (executive) เรียกได้เฉพาะข้อ 1–4 และ 13 (FR-19)

---

## 6. การออกแบบคิว

### 6.1 คิวและการตั้งค่า

| คิว | ชนิด | ผู้ส่ง → ผู้รับ | ข้อความ | การตั้งค่า |
|---|---|---|---|---|
| `ppe.jobs` | quorum, durable | gateway → Worker | `{"job_id","image_path","queued_at"}` (ไม่มีตัวรูป) | `x-delivery-limit = 3` · `x-dead-letter-exchange` → `ppe.jobs.dead` · `x-max-length = MAX_QUEUE_DEPTH` · `x-overflow = reject-publish` |
| `ppe.results` | quorum, durable | Worker → gateway | `{"job_id","event":"STARTED|DONE|FAILED","result","error"}` | – |
| `ppe.jobs.dead` | quorum, durable | RabbitMQ → gateway | งานที่ส่งซ้ำครบ 3 ครั้ง | gateway ตั้งงานเป็น `FAILED` (`MAX_RETRIES`) |

### 6.2 งานต้องไม่หายเมื่อ Worker ล่ม

| กลไก | ทำอย่างไร | ป้องกันอะไร |
|---|---|---|
| ข้อความถาวร | คิว durable + ข้อความ persistent + volume ของ RabbitMQ | RabbitMQ รีสตาร์ตแล้วงานยังอยู่ |
| Publisher confirm | gateway ตอบ `202` หลัง RabbitMQ ยืนยันว่ารับข้อความแล้วเท่านั้น ไม่ได้ confirm → `503` | งานที่เว็บเชื่อว่าส่งแล้วแต่ไม่อยู่ในคิว |
| Manual ack | Worker ตั้ง `prefetch = 1` และ ack หลัง publish ผลลง `ppe.results` และได้ confirm แล้ว | Worker ล่มระหว่างตรวจ: ข้อความที่ยังไม่ ack กลับเข้าคิวเองและถูกส่งให้ Worker ที่กลับมา |
| ผลชุดเดียว | gateway เขียนผลด้วยเงื่อนไข "งานยังไม่จบ" · เว็บเขียน `detections` ใน transaction เดียวกับ `status = DONE` ที่มีเงื่อนไข `WHERE status IN ('QUEUED','PROCESSING')` | งานที่ถูกตรวจ 2 รอบ (ล่มหลังส่งผลแต่ก่อน ack) ไม่สร้างผลซ้ำ |
| งานพิษ | ส่งซ้ำครบ 3 ครั้ง → `ppe.jobs.dead` → `FAILED` พร้อมเหตุผล | รูปที่ทำให้ Worker ล่มทุกครั้งไม่วนในคิวตลอดไป |
| สถานะหลัง Worker ล่ม | งานที่เป็น `PROCESSING` เกิน `PROCESSING_TIMEOUT_S` (120 วินาที) โดยไม่มีเหตุการณ์ใหม่ gateway รายงานเป็น `QUEUED` | ผู้ใช้ไม่เห็น "กำลังตรวจ" ค้างขณะที่งานกลับไปรอคิวแล้ว |
| ฝั่ง AI หายทั้งเครื่อง | เว็บยังมีรูปต้นฉบับ · งานที่ gateway ตอบ `404` ถูกส่งใหม่ด้วย `job_id` เดิม | เครื่องที่เช่าถูกลบหรือเปลี่ยนเครื่อง |
| เฝ้ารูปค้าง | `dispatcher` ตั้ง `FAILED` ("เกินเวลา 15 นาที") ให้รูปที่ยังไม่จบหลัง `accepted_at` 15 นาที (เฉพาะรูปที่ `dispatch_state` ไม่ใช่ `CLOSED`) | รูปค้างในสถานะกลางทางเกิน 15 นาที (NFR-04) |

### 6.3 คิวยาวเกินกำหนดต้องปฏิเสธงานใหม่

| เรื่อง | ข้อกำหนด |
|---|---|
| ความยาวคิว | `queue_depth` = จำนวนงานใน `jobs.db` ที่เป็น `QUEUED` + `PROCESSING` |
| เส้นแบ่ง | `queue_depth ≥ MAX_QUEUE_DEPTH` → ปฏิเสธ · ต่ำกว่า → รับ · ตัวอย่างเมื่อ `MAX_QUEUE_DEPTH = 200`: ค้าง 199 → รับ (กลายเป็น 200) · ค้าง 200 → `429` · ค้าง 201 เกิดไม่ได้ |
| ค่าเริ่มต้น | `MAX_QUEUE_DEPTH = 200` (ภาระช่วงเร่งด่วน 150 รูปตาม NFR-03 ต้องเข้าได้ทั้งหมด เหลือที่ว่าง 50) ตั้งผ่าน `.env` ของฝั่ง AI |
| คำตอบ | `429` + `Retry-After` · ไม่เก็บไฟล์ ไม่สร้างงาน ไม่ publish |
| `Retry-After` | `max(5, ceil((queue_depth − MAX_QUEUE_DEPTH + 10) × เวลาตรวจเฉลี่ยต่อรูป))` วินาที · เวลาตรวจเฉลี่ยมาจาก 50 งานล่าสุด |
| ชั้นที่สอง | `x-max-length` + `reject-publish` ที่ RabbitMQ: ถ้านับพลาดจากคำขอที่เข้าพร้อมกัน RabbitMQ ปฏิเสธการ publish แล้ว gateway ตอบ `429` เช่นกัน |
| ผลต่อผู้ใช้ | เว็บไม่ปฏิเสธผู้อัปโหลดเพราะคิวเต็ม รูปอยู่ที่ "รอคิว" ในฐานข้อมูลของเว็บและถูกส่งใหม่ จึงไม่ขัดกับ "รูปห้ามหาย" |

---

## 7. ความสามารถเพื่อการทดสอบของเว็บ

### 7.1 `/api/health`

`GET /api/health` ไม่ต้องล็อกอิน ไม่มีข้อมูลผู้ใช้ รูป หรือ key

```json
{
  "status": "ok",
  "db": "ok",
  "storage": "ok",
  "dispatcher": "ok",
  "gateway": "ok",
  "ai_mode": "real",
  "time": "2026-11-18T18:00:00+07:00",
  "version": "0.1.0"
}
```

| ช่อง | ค่า | ผลต่อรหัสคำตอบ |
|---|---|---|
| `db` · `storage` | `ok` / `down` | `down` → `503` และ `status: "down"` |
| `dispatcher` | `ok` เมื่อวนรอบล่าสุดไม่เกิน 10 วินาที | `down` → `200` และ `status: "degraded"` |
| `gateway` | `ok` / `down` / `unauthorized` จาก `GET /v1/health` ล่าสุด | ไม่ `ok` → `200` และ `status: "degraded"` (เว็บยังรับรูปได้) |
| `ai_mode` | `real` / `mock` | – |
| `time` | เวลาปัจจุบันของระบบ (Asia/Bangkok) รวมเวลาที่ตั้งจากการรีเซ็ต | – |

docker compose ใช้เส้นทางนี้เป็น healthcheck ของ `web`

### 7.2 ทางรีเซ็ตข้อมูลทดสอบ

`POST /api/test/reset`

| เรื่อง | ข้อกำหนด |
|---|---|
| เปิดใช้ | เฉพาะเมื่อ `ENABLE_TEST_RESET=1` ถ้าไม่ตั้ง เส้นทางนี้ตอบ `404` |
| การยืนยัน | header `X-Test-Key` ต้องตรงกับ `TEST_RESET_KEY` ใน `.env` ผิด → `401` |
| เนื้อคำขอ (ไม่บังคับ) | `{"now":"2026-11-18T17:59:00+07:00"}` ตั้งนาฬิกาของระบบสำหรับทดสอบ BR-07 และวันที่ของรูป · ไม่ส่ง → ใช้เวลาจริง |
| สิ่งที่ทำ | 1) หยุด `dispatcher` ชั่วคราว 2) ล้าง 7 ตารางและไฟล์ใน volume `photos` 3) ใส่ข้อมูล seed ตาม `docs/TEST-DATA.md` (ไซต์ ผู้ใช้ และรูปของชุดรายงาน) 4) ให้ `dispatcher` ทำงานต่อ |
| คำตอบ | `200` `{"reset":true,"sites":3,"users":5,"photos":1233,"overrides":1,"now":"…"}` |
| คุณสมบัติ | เรียกซ้ำกี่ครั้งได้ผลเท่าเดิม (รหัสของแถว seed คงที่) จึงใช้ก่อนทุกชุดทดสอบได้ |
| คำสั่งคู่กัน | `docker compose run --rm web npm run seed` ทำงานเดียวกันจากบรรทัดคำสั่ง |

### 7.3 โหมดจำลองฝั่ง AI (`AI_MODE=mock`)

ใช้ทดสอบ Business Rule โดยไม่ต้องเช่า GPU และได้ H, V ที่กำหนดได้แน่นอน `dispatcher` ชี้ไปที่ `mock-gateway` ซึ่งทำตาม API Contract ในหัวข้อ 5.1 ทุกข้อ

| ชื่อไฟล์ที่อัปโหลด | ผลจาก `mock-gateway` |
|---|---|
| `h{H}_v{V}*.jpg` หรือ `.png` เช่น `h0_v2.jpg` | `DONE` ด้วย `h = H`, `v = V` และกรอบตามจำนวนนั้น |
| `corrupt*.jpg` | `FAILED` `IMAGE_UNREADABLE` |
| ชื่ออื่น | `DONE` ด้วย `h = 0`, `v = 0` |

`mock-gateway` อ่านชื่อจากช่อง `filename` ของส่วน `image` ใน multipart · gateway จริงไม่ใช้ชื่อไฟล์

### 7.4 `data-testid`

กติกา: ปุ่ม ลิงก์เมนู ช่องกรอก ตัวเลือก และค่าที่ชุดทดสอบต้องอ่าน ทุกชิ้นมี `data-testid` · รูปแบบ `{หน้า}-{ชิ้นส่วน}` ตัวพิมพ์เล็กคั่นด้วยขีด · ชิ้นที่ซ้ำตามแถวต่อท้ายด้วยรหัส เช่น `photo-row-{photoId}` · ค่าคงที่ ไม่ขึ้นกับภาษาบนหน้าจอ

| หน้า (เส้นทาง) | ปุ่มและช่องกรอก | ค่าที่อ่านได้ |
|---|---|---|
| ทุกหน้า (แถบบน) | `nav-upload` · `nav-photos` · `nav-problems` · `nav-report` · `nav-logout` | `nav-user-name` · `nav-user-role` · `nav-user-site` |
| ล็อกอิน `/login` | `login-email` · `login-password` · `login-submit` | `login-error` |
| อัปโหลด `/upload` | `upload-file-input` · `upload-submit` · `upload-clear` | `upload-selected-count` · `upload-error` · `upload-file-error-{index}` |
| สถานะการอัปโหลด `/uploads/{batchId}` | `batch-refresh` · `batch-open-photo-{photoId}` | `batch-accepted-count` · `batch-count-queued` · `batch-count-processing` · `batch-count-done` · `batch-count-failed` · `batch-row-{photoId}` · `batch-row-status-{photoId}` · `batch-row-result-{photoId}` · `batch-row-reason-{photoId}` |
| รูปทั้งหมด `/photos` | `photos-filter-date` · `photos-filter-site` · `photos-filter-result` · `photos-filter-status` · `photos-filter-apply` · `photos-page-prev` · `photos-page-next` · `photo-open-{photoId}` | `photos-total-count` · `photo-row-{photoId}` · `photo-row-result-{photoId}` · `photo-row-edited-{photoId}` |
| รูปที่มีปัญหา `/photos/problems` | `problems-filter-date` · `problems-filter-site` · `problems-filter-apply` · `photo-open-{photoId}` | `problems-total-count` · `problems-count-fail` · `problems-count-warn` |
| รายละเอียดรูป `/photos/{id}` | `override-result-select` · `override-reason` · `override-submit` · `override-cancel` · `history-toggle` · `photo-back` | `photo-image` · `photo-box-{index}` · `photo-box-label-{index}` · `photo-h` · `photo-v` · `photo-model-result` · `photo-current-result` · `photo-edited-badge` · `override-error` · `history-row-{overrideId}` |
| รายงานรายวัน `/reports/daily` | `report-date` · `report-apply` · `report-prev-day` · `report-next-day` | `report-ready-badge` · `report-row-{siteCode}` · `report-taken-{siteCode}` · `report-fail-{siteCode}` · `report-h-{siteCode}` · `report-rate-{siteCode}` · `report-red-{siteCode}` (`data-red="true|false"`) · `report-edited-{siteCode}` · `report-failed-{siteCode}` |

ชิ้นที่บทบาทนั้นไม่มีสิทธิ์จะไม่ถูกแสดง (เช่น ผู้บริหารไม่มี `nav-upload`) แต่สิทธิ์จริงตรวจที่ API (NFR-06)

---

## 8. โหมด `BUG_MODE=1`

| เรื่อง | ข้อกำหนด |
|---|---|
| จุดประสงค์ | ใช้ตรวจว่าชุดทดสอบจับความผิดของ Business Rule ได้จริง |
| การเปิด | ตัวแปรสภาพแวดล้อม `BUG_MODE=1` ของบริการ `web` และ `dispatcher` ใน docker compose · ค่าเริ่มต้น `0` · อ่านครั้งเดียวตอนเริ่มบริการ |
| ผล | Business Rule 3 ข้อจาก BR-01 ถึง BR-07 ทำงานผิดจากข้อกำหนด ส่วนอื่นของระบบทำงานเหมือนเดิม |
| ตำแหน่งในโค้ด | ไฟล์กติกาไฟล์เดียว (`lib/rules`) ซึ่งเป็นที่เดียวที่อ่าน `BUG_MODE` |
| รายชื่อ 3 ข้อ | อยู่ที่ `docs/BUGS-SECRET.md` ที่เดียว ไม่ปรากฏในเอกสารอื่น ในหน้าเว็บ ใน `/api/health` ใน log และในชื่อตัวแปรหรือคำอธิบายในโค้ดส่วนอื่น |
| ผู้ที่เปิดไฟล์ได้ | ผู้สร้างระบบและผู้ตรวจผลการทดสอบ ผู้ทดสอบไม่เปิดไฟล์นี้ |

---

## 9. การนำ Business Rule ไปใช้

### 9.1 การตัดสินผลของรูป (BR-01 ถึง BR-03)

ค่าคงที่ในไฟล์กติกา: `HELMET_FAIL_MIN = 1` · `VEST_FAIL_MIN = 2` · `VEST_WARN_MIN = 1`

| ลำดับ | เงื่อนไข | ผล |
|---|---|---|
| 1 | `H ≥ HELMET_FAIL_MIN` | ไม่ผ่าน (BR-01) |
| 2 | `V ≥ VEST_FAIL_MIN` | ไม่ผ่าน (BR-02) |
| 3 | `V ≥ VEST_WARN_MIN` | เตือน (BR-03) |
| 4 | นอกเหนือจากนั้น | ผ่าน |

### 9.2 รายงานรายวัน (BR-04, BR-07, FR-15)

| ค่าในรายงาน | วิธีคำนวณ (ต่อไซต์ ต่อ `upload_date`) |
|---|---|
| จำนวนรูปที่ถ่าย | จำนวนแถว `photos` ทุกสถานะ |
| จำนวนรูปที่มีผล | จำนวนแถวที่ `status = DONE` |
| จำนวนรูปไม่ผ่าน | `status = DONE` และ `current_result = FAIL` |
| จำนวนคนไม่ใส่หมวก | ผลรวม `model_h` ของรูปที่ `DONE` |
| อัตราผ่าน | รูปที่ `current_result = PASS` ÷ รูปที่มีผล × 100 แสดงทศนิยม 2 ตำแหน่ง |
| สีแดง | `ผ่าน × 100 < 90 × รูปที่มีผล` เทียบด้วยจำนวนเต็ม ไม่ใช้ค่าที่ปัดแล้ว |
| จำนวนรูปที่ถูกแก้ผล | `is_overridden = true` |
| จำนวนรูปที่ตรวจไม่สำเร็จ | `status = FAILED` |
| ไม่มีรูปเลย | แสดง "ไม่มีข้อมูล" ไม่เป็นสีแดง |
| มีรูปแต่ยังไม่มีรูปใดมีผล | อัตราผ่านแสดง "ยังไม่มีผล" ไม่เป็นสีแดง |
| ป้ายความพร้อม | เวลาปัจจุบัน ≥ 18:00 น. ของวันที่เลือก → "รายงานประจำวันพร้อมแล้ว" · ก่อนนั้น → "ข้อมูลระหว่างวัน" · รายงานแสดงครบ 3 ไซต์เสมอ |

### 9.3 การรับรูป (BR-05, BR-06)

| กติกา | การนำไปใช้ |
|---|---|
| BR-05 | 1 MB = 1,048,576 ไบต์ · เพดาน 15 MB = 15,728,640 ไบต์ · `size_bytes ≤ 15,728,640` รับ · นับจากไบต์ที่ได้รับจริง ไม่เชื่อ header · ตัดการรับทันทีที่เกิน |
| BR-06 | ตรวจที่ `POST /api/uploads` ก่อนรับไฟล์ใด: `count ≤ 50` รับ · หน้าจอตรวจซ้ำก่อนส่งเพื่อบอกผู้ใช้เร็วขึ้น แต่ผลตัดสินอยู่ที่ API |
| FR-02 | ตรวจจากไบต์ต้นไฟล์ (JPG: `FF D8 FF` · PNG: `89 50 4E 47`) ไม่ใช้นามสกุล · ไฟล์ที่ถูกปฏิเสธไม่ถูกเขียนลง volume |

---

## 10. ความปลอดภัยและความเป็นส่วนตัว

| ข้อกำหนด | การออกแบบ |
|---|---|
| ล็อกอิน (FR-18, NFR-06) | รหัสผ่านเก็บเป็น argon2id · session token สุ่ม 256 บิต เก็บเฉพาะค่า hash ใน `sessions` · middleware ส่งผู้ที่ไม่ล็อกอินไป `/login` ทุกหน้า |
| สิทธิ์ (FR-19–21) | ฟังก์ชันเดียว `canAccess(user, action, siteId)` เรียกในทุก Route Handler · query ของ supervisor มี `WHERE site_id = :userSite` เสมอ |
| รูปไม่สาธารณะ (FR-22, NFR-05) | ไม่มีไฟล์รูปใต้เส้นทาง static · ลิงก์รูปคือ API ที่ตรวจ session และไซต์ |
| API key (NFR-05) | อยู่ใน `.env` (ไม่เข้า repository) ส่งให้ `dispatcher` เท่านั้น · ไม่อยู่ในตัวแปรที่ขึ้นต้นด้วย `NEXT_PUBLIC_` · ตัวกรอง log ตัด header `X-API-Key` |
| การเข้ารหัส (NFR-05) | เว็บ ↔ gateway ใช้ HTTPS โดย gateway อยู่หลัง reverse proxy ที่ทำ TLS และเว็บตรวจใบรับรองด้วย `GATEWAY_CA_CERT` · เว็บ ↔ ผู้ใช้ ใช้ HTTPS ผ่าน reverse proxy ของเครื่องนี้ |
| รูปไม่ออกนอกโครงการ (NFR-05) | รูปถูกส่งไปที่ `GATEWAY_URL` ที่เดียว · gateway ลบไฟล์ชั่วคราวเมื่องานจบ · Worker โหลดโมเดลจากไฟล์ในเครื่อง ไม่เรียกบริการภายนอก |
| ไม่ลบอัตโนมัติ (AS-12) | ไม่มีงานลบรูปหรือผลตรวจตามเวลา |

---

## 11. ค่าตั้ง (ตัวแปรสภาพแวดล้อม)

| ตัวแปร | ฝั่ง | ค่าเริ่มต้น | ความหมาย |
|---|---|---|---|
| `DATABASE_URL` | เว็บ | – | การเชื่อมต่อ PostgreSQL |
| `GATEWAY_URL` | เว็บ | – | ที่อยู่ gateway (`https://…`) |
| `GATEWAY_API_KEY` | เว็บ, AI | – | API key |
| `GATEWAY_CA_CERT` | เว็บ | – | ใบรับรองที่ใช้ตรวจ gateway |
| `AI_MODE` | เว็บ | `real` | `real` หรือ `mock` |
| `BUG_MODE` | เว็บ | `0` | หัวข้อ 8 |
| `ENABLE_TEST_RESET` · `TEST_RESET_KEY` | เว็บ | `0` · – | หัวข้อ 7.2 |
| `STUCK_TIMEOUT_MIN` | เว็บ | `15` | เฝ้ารูปค้าง |
| `MAX_QUEUE_DEPTH` | AI | `200` | หัวข้อ 6.3 |
| `MAX_DELIVERY` | AI | `3` | จำนวนครั้งที่ส่งงานซ้ำ |
| `PROCESSING_TIMEOUT_S` | AI | `120` | หัวข้อ 6.2 |
| `MODEL_PATH` · `CONF_THRESHOLD` | AI | – · – | ไฟล์โมเดล YOLO และ Threshold ที่เลือกบน Validation Set (NFR-01) |

---

## 12. ตรวจย้อน Requirement → การออกแบบ

| Requirement | อยู่ในหัวข้อ |
|---|---|
| FR-01–06 | 3 · 4 · 5.2 (API 5–7) · 9.3 |
| FR-07–12 | 5.1 (API 2) · 5.2 (API 8–10) · 9.1 · D-08 |
| FR-13–14 · NFR-07 | 2 (`result_overrides`) · 5.2 (API 11–12) |
| FR-15–17 · BR-04 · BR-07 | 9.2 · 5.2 (API 13) |
| FR-18–22 · NFR-05 · NFR-06 | 10 · 5.1 (API key) |
| BR-01–03 | 9.1 |
| BR-05 · BR-06 | 9.3 |
| NFR-01 | 5.1 (`conf_threshold`, `model_version`) · 11 · คำถาม DQ-02 |
| NFR-02 · NFR-03 · NFR-08 | 3 · 6.3 · 5.1 (API 4) · คำถาม DQ-01 |
| NFR-04 | 4 · 6.2 · D-01 · D-05 |

---

## 13. คำถามที่การออกแบบยังตอบไม่ได้

| รหัส | คำถาม | ทำไมยังตอบไม่ได้ | กระทบ |
|---|---|---|---|
| DQ-01 | GPU 1 ใบตรวจรูปขนาด 8–10 MB ได้กี่รูปต่อวินาที | ต้องวัดบนเครื่องที่เช่าจริง ภาระ 150 รูปใน 600 วินาทีต้องได้อย่างน้อย 0.25 รูปต่อวินาที ส่วน p95 ≤ 30 วินาทีของ 50 รูปต้องได้ราว 1.7 รูปต่อวินาที | NFR-02 · NFR-03 · ค่า `MAX_QUEUE_DEPTH` |
| DQ-02 | ใช้ไฟล์โมเดล YOLO ตัวใด ชื่อคลาสใดแทน "ไม่ใส่หมวก" และ "ไม่ใส่เสื้อสะท้อนแสง" ค่า Threshold เท่าใด และ Test Set มาจากไหน | ยังไม่มีผลวัด Recall และ Precision ระดับรูป | NFR-01 · `CONF_THRESHOLD` |
| DQ-03 | ที่อยู่และใบรับรอง HTTPS ของ gateway บนเครื่องที่เช่า (IP และพอร์ตเปลี่ยนทุกครั้งที่เช่า) และของเว็บบนเครื่องนี้ จะใช้โดเมนหรือใบรับรองแบบใด | ขึ้นกับผู้ให้เช่าเครื่องและโดเมนของลูกค้า | NFR-05 |
| DQ-04 | เมื่อคนแก้ผลของรูป ค่า H ที่ใช้รวม "จำนวนคนไม่ใส่หมวก" ในรายงานต้องเปลี่ยนตามหรือไม่ | Requirement ให้แก้เฉพาะผล ไม่ได้ให้แก้จำนวนคน การออกแบบนี้ใช้ H ของโมเดลเสมอ | FR-15 · AS-10 |
| DQ-05 | รูปจาก iPhone ที่เป็น HEIC จะถูกปฏิเสธตาม FR-02 ลูกค้ายอมรับหรือต้องการให้แปลงเป็น JPG | ต้องถามลูกค้า | FR-02 |
| DQ-06 | ถ้าเครื่อง GPU ใช้ไม่ได้นานเกิน 15 นาที รูปจะเป็น "ตรวจไม่สำเร็จ" ตาม NFR-04 แล้วใครเป็นผู้สั่งตรวจใหม่ (ระบบส่งเองเมื่อเครื่องกลับมา หรือมีปุ่มให้คนกด) และรูปที่ "ตรวจไม่สำเร็จ" ให้คนใส่ผลเองได้หรือไม่ | Requirement กำหนดเพียงว่าห้ามค้างเกิน 15 นาที | NFR-04 · FR-13 |
| DQ-07 | ต้องเตรียมพื้นที่เก็บรูปเท่าใดและสำรองข้อมูลอย่างไร (ช่วงเร่งด่วน 1 รอบประมาณ 150 รูป × 10 MB = 1.5 GB และยังไม่ลบอัตโนมัติ) | ลูกค้ายังไม่กำหนดระยะเวลาเก็บ (AS-12) และจำนวนรอบต่อวัน | NFR-05 |
| DQ-08 | ชื่อจริงของ 3 ไซต์ รายชื่อบัญชีผู้ใช้ และหัวหน้างาน 1 คนดูแลได้มากกว่า 1 ไซต์หรือไม่ | การออกแบบนี้ให้ 1 บัญชีหัวหน้างานผูกกับ 1 ไซต์ | FR-04 · FR-20 |

ข้อสมมติ AS-01 ถึง AS-14 ใน Requirement ยังรอลูกค้ายืนยัน การออกแบบนี้ทำตามข้อสมมติทุกข้อ และเส้นแบ่งทุกค่าเป็นค่าคงที่ที่แก้ได้ที่เดียว
