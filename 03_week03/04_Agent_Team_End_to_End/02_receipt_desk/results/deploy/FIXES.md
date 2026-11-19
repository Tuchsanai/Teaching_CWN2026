# FIXES · ขั้นที่ 11 ขึ้นระบบจริงครั้งแรก (GPU จริง + เว็บ)

## แก้โค้ดของทีม: 1 บรรทัด
| ไฟล์ | เดิม | ใหม่ | เหตุผล |
|---|---|---|---|
| `app/docker-compose.yml` (service `web`) | `- '3000:3000'` | `- '${WEB_PORT:-3000}:3000'` | ต้องเปิดเว็บที่พอร์ต 3420 แต่พอร์ต 3000 เขียนตายตัวไว้ ถ้าไม่ตั้ง `WEB_PORT` ก็ยังได้ 3000 เหมือนเดิม (ไฟล์เดิมเก็บไว้ที่ `results/deploy/docker-compose.yml.orig`) |

ไฟล์อื่นใน `./app` (gateway, worker, queue, nginx.conf, dispatcher, เว็บ) **ไม่ได้แก้เลย** ใช้ได้ทันทีบน GPU จริง

## สิ่งที่ต้องทำเพิ่มตอนเปิด (ไม่ได้แก้โค้ด)
1. **RabbitMQ เปิดไม่ขึ้น**: สั่ง `rabbitmq-server` ตรง ๆ ใน tmux ในฐานะ root แล้วล้ม (`Error when reading /root/.erlang.cookie: eacces`) เพราะสคริปต์ของแพ็กเกจเปลี่ยนไปใช้ผู้ใช้ `rabbitmq` แต่ HOME ยังเป็น `/root`
   → เปิดด้วย `runuser -u rabbitmq -- env HOME=/var/lib/rabbitmq rabbitmq-server` (อยู่ใน `code_step11/svc.sh`)
2. **ฐานข้อมูลว่าง ไม่มีบัญชีให้เข้าสู่ระบบ**: `schema.sql` สร้างแค่ตาราง บัญชีและลูกค้าเกิดจากฟังก์ชัน `reset_test_data()` เท่านั้น ซึ่งปกติเรียกผ่าน `/api/test/reset` ที่ปิดอยู่ (`ENABLE_TEST_RESET=0`)
   → เรียกฟังก์ชันนี้ครั้งเดียวผ่าน psql (`select reset_test_data('{}'::jsonb,'1')`) โดยเว็บยังปิด test reset ไว้ ได้ผู้ใช้ 6 · ลูกค้า 3 · ใบตัวอย่าง S-01–S-08 อีก 8 ใบ
   → ข้อเสนอ: ทีมควรมีสคริปต์ seed บัญชีจริงแยกจากข้อมูลทดสอบ
3. **โมเดล**: รวม LoRA ที่ดีที่สุด (รอบ 2 GPU, `step10/runs/best`) เข้ากับ Qwen3-VL-2B-Instruct เป็นโมเดลเดียว (`code_step11/merge_lora.py`) แล้วให้ vLLM เสิร์ฟชื่อ `receipt-vlm` ตามวิธีที่สองใน `ai/train/README.md`
4. **ติดตั้งบนเครื่อง GPU** (ไม่มี Docker): `nginx` + `rabbitmq-server` จาก apt · venv ของ gateway/worker (fastapi, uvicorn, aio-pika, httpx, pydantic, pillow, python-multipart) · venv ของ vLLM 0.34.0 (+ peft สำหรับรวม LoRA)
5. **ใส่ key ให้ vLLM** (`VLLM_API_KEY` ซึ่งโค้ดของทีมรองรับอยู่แล้ว) เพราะพอร์ตสาธารณะ 8080 ของเครื่องชี้ไปที่ NGINX ทดสอบจากนอกเครื่องได้ 403 อยู่แล้ว (allow-list ใน nginx.conf) key นี้กันอีกชั้น
6. **API key ของ gateway ตัวใหม่** เก็บใน `./.env` (`GATEWAY_API_KEY`) ส่งไปเครื่อง GPU เป็น `secrets.env` (chmod 600) และเขียนลง `app/.env` ให้ dispatcher ไม่มีการแสดงค่า

## ยังค้าง / ต้องระวัง
- **gateway ยังเป็น HTTP ธรรมดา** key วิ่งผ่านอินเทอร์เน็ตแบบไม่เข้ารหัส โค้ดรองรับ TLS แล้ว (`GATEWAY_TLS_CERT/_KEY` และ `GATEWAY_CA_CERT` ฝั่ง dispatcher) แต่ compose ยังไม่ mount ไฟล์ CA ให้ dispatcher ต้องเพิ่ม volume อีกจุดถ้าจะเปิด TLS
- ใบ te0004 โมเดลตอบ 174,000 (เฉลย 174,600) ความมั่นใจ 0.64 → ระบบติดธง "ไม่แน่ใจยอดรวม" ตาม BR-04 ถูกต้อง ไม่ใช่ข้อผิดของการ deploy
