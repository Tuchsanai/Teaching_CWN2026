# FIXES · ขั้นที่ 9 เปิดระบบจริง (2026-11-19)

## 1. โค้ดของทีมที่แก้ (1 ไฟล์ · 1 บรรทัด)

| ไฟล์ | แก้อะไร | เพราะอะไร |
|---|---|---|
| `app/ai/worker/classes.json` | เพิ่มชื่อ `"NO-Safety Vest"` ในรายการของ `NO_VEST` (ให้เท่ากับ `app/ai/train/classes.json` ที่แก้ไว้แล้วในขั้นที่ 8) | โมเดลที่เทรนเรียกคลาสนี้ว่า `NO-Safety Vest` (มีเว้นวรรค) แต่ไฟล์ของ Worker มีแค่ `no-safety-vest` · `YoloDetector` จะหาคลาส `NO_VEST` ไม่เจอและหยุดด้วย `The model is missing PPE classes configured in classes.json` · พบจากการเทียบชื่อคลาสของ `best.pt` กับไฟล์นี้ก่อนเปิด Worker จึงแก้ก่อนเปิดครั้งแรก |

ไม่ได้แก้ `gateway/main.py`, `worker/worker.py`, `common/queues.py`, dispatcher, หน้าเว็บ, `lib/rules.ts`, `docker-compose.yml` และ `ai/docker-compose.yml`

## 2. สิ่งที่ทำต่างจาก README ของทีม โดยไม่แก้โค้ด

| เรื่อง | ที่ทำ | เพราะอะไร |
|---|---|---|
| ฝั่ง AI ไม่ใช้ `ai/docker-compose.yml` | เปิด RabbitMQ, gateway, Worker เป็น process ใน tmux ด้วย `code_step09/gpu/svc.sh` (คำสั่งเดียวกับ `CMD` ใน Dockerfile ของทีม) | เครื่องที่เช่าเป็น Docker container เอง ใช้ docker ซ้อนไม่ได้ |
| RabbitMQ | ติดตั้งจาก apt ได้รุ่น 3.12.1 (ทีมทดสอบกับรุ่น 4) · ฟังเฉพาะ `127.0.0.1:5672` · ลบผู้ใช้ `guest` สร้างผู้ใช้ `sitesafe` รหัสผ่านสุ่มบนเครื่อง GPU | คิว quorum + `x-delivery-limit` + `reject-publish` ใช้ได้ในรุ่น 3.12 · gateway และ Worker ประกาศคิวผ่านทั้งคู่ |
| HTTPS ของ gateway (ข้อค้าง DQ-03 ใน TEST.md) | ใช้ TLS ของ uvicorn เอง (`--ssl-keyfile` / `--ssl-certfile`) กับใบรับรองที่สร้างเอง (SAN = IP ของเครื่อง อายุ 30 วัน) แล้วใส่ใบรับรองใน `GATEWAY_CA_CERT` ของ `app/.env` | dispatcher ไม่ยอมรับ `http://` ในโหมด `AI_MODE=real` · เปิดพอร์ตเพิ่มไม่ได้ จึงให้ gateway ทำ TLS ที่พอร์ต 8000 (ออกสู่ภายนอกที่ 51909) แทน reverse proxy |
| ไลบรารี Python | ติดตั้ง fastapi, python-multipart, aio-pika, uvicorn, pika ลงใน `/venv/main` ที่มี torch 2.14.1+cu130 และ ultralytics 8.4.215 อยู่แล้ว | ไม่ติดตั้ง torch 2.5.1 ตาม `worker/requirements.txt` ซ้ำ เพราะโมเดลเทรนด้วยชุดที่มีอยู่ |
| ค่าตั้งฝั่งเว็บ | สร้าง `app/.env` (ไม่เข้า git): `WEB_PORT=3410`, `AI_MODE=real`, `GATEWAY_URL=https://137.175.22.196:51909`, `BUG_MODE=0`, `ENABLE_TEST_RESET=1` · รหัสผ่านฐานข้อมูลและ `TEST_RESET_KEY` ใช้ค่าทดสอบของ `.env.test.example` · API key อยู่ใน `./.env` ที่เดียว (`code_step09/web.sh` ส่ง env-file สองไฟล์ ชื่อ project `sitesafe-e2e`) | ขั้นถัดไปต้องรีเซ็ตข้อมูลทดสอบได้ · เว็บเปิดที่ `127.0.0.1` เท่านั้น |

## 3. ปัญหาที่เจอระหว่างเปิด (แก้ในสคริปต์ของขั้นนี้ ไม่ใช่โค้ดของทีม)

| อาการ | สาเหตุ | แก้ที่ |
|---|---|---|
| `rabbitmqctl` ขึ้น `Error when reading /root/.erlang.cookie: eacces` | สคริปต์ของ Debian สลับเป็นผู้ใช้ `rabbitmq` แต่ `HOME` ยังเป็น `/root` | `svc.sh` เรียกด้วย `runuser -u rabbitmq -- env HOME=/var/lib/rabbitmq …` |
| RabbitMQ ไม่ขึ้น `failed_to_parse_configuration_file` | `/etc/rabbitmq/rabbitmq.conf` ที่สร้างเป็นสิทธิ์ 600 ของ root ผู้ใช้ `rabbitmq` อ่านไม่ได้ | `setup_gpu.sh` ใส่ `chmod 644` |

## 4. ข้อสังเกตที่ยังไม่ได้แก้ (ไม่ทำให้เปิดไม่ได้)

- dispatcher ส่งรูปให้ gateway ทีละรูป และเปิดการเชื่อมต่อ TLS ใหม่ทุกคำขอ (ไป-กลับ 213 ms ต่อรอบ · คำขอละ 1.0–1.5 วินาที) จึงส่งได้ราว 0.6–0.8 รูปต่อวินาที ทั้งที่ GPU ใช้ราว 20 ms ต่อรูป · รูป 300 รูปจะใช้ราว 6–8 นาที ต้องดูคู่กับ NFR-02 และ NFR-03 ในขั้นทดสอบ
- `REQUEST_TIMEOUT_MS = 3000` ของ dispatcher ห่างจากเวลาคำขอจริง (1.0–1.5 วินาที) ไม่มาก ถ้าเครือข่ายช้าจะเกิดการส่งซ้ำ (gateway ตอบ `200` กับ `job_id` เดิม งานไม่ซ้ำ)
- เว็บผูกที่ `127.0.0.1` เท่านั้น บน Windows โปรแกรมที่ไม่ใช่เบราว์เซอร์ (curl, Python) เรียก `http://localhost:3410` จะช้าคำขอละราว 2 วินาทีเพราะลอง IPv6 ก่อน ให้ใช้ `http://127.0.0.1:3410` ในสคริปต์
- ใบรับรองของ gateway ผูกกับ IP `137.175.22.196` ถ้าเครื่องเปลี่ยน IP ต้องสร้างใหม่และแก้ `app/.env`
