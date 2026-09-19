# Setup Prompt S3 — ติดตั้งและเริ่มเว็บทดลอง Kokoro TTS

```text
ติดตั้งและเริ่มเว็บทดลอง Kokoro TTS ของบทเรียน 03_MCP (โฟลเดอร์ปัจจุบันคือ 03_MCP) โดยไม่ต้องถามกลับ ห้ามแก้โค้ดใน labs/kokoro-web
1. สร้าง venv ที่ labs/.venv ถ้ายังไม่มี แล้วใช้ python/pip ของ venv นี้
2. pip install soundfile fastapi uvicorn จากนั้นถ้ายังไม่มี torch ให้ pip install torch --index-url https://download.pytorch.org/whl/cpu แล้ว pip install kokoro ถ้ามี apt ให้ติดตั้ง espeak-ng
3. ตั้ง PYTHON=<python ของ venv> แล้วรัน labs/kokoro-web/run.sh
4. รอจน curl http://127.0.0.1:8765/api/health ได้ "ok":true แล้วทดสอบ POST /api/tts ด้วยข้อความ "Setup test from prompt." บันทึกเวลาที่ใช้และขนาดไฟล์เสียงที่ได้
5. รายงาน pid ของเว็บ (อยู่ใน labs/kokoro-web/server.pid) และวิธีหยุด (kill pid) พร้อมปัญหาที่พบตามจริง
```

**ตรวจอย่างไรว่าพรอมป์ต์นี้ทำงานสำเร็จ**

**วิธีอ่านผล:** ตัวอย่างด้านล่างเป็น **ผลที่คาดหวัง (Expected output)** เพื่อใช้ตรวจงาน ไม่ใช่ผลรันใหม่หรือข้อความที่ Host ต้องตอบตรงทุกตัวอักษร ค่า path ชื่อไฟล์ และเวลาจะแตกต่างกันได้ ต้องมีผลจาก tool หรือไฟล์จริงรองรับคำว่า “ผ่าน”

**ทดสอบหลังติดตั้ง:** รันคำสั่งต่อไปนี้บนเครื่องเดียวกับเว็บ หรือให้ Host รันแล้วรายงานผล

```bash
curl -sS http://127.0.0.1:8765/api/health
curl -sS -w '\nHTTP_STATUS=%{http_code}\n' -X POST http://127.0.0.1:8765/api/tts -H 'Content-Type: application/json' -d '{"text":"Hello students.","voice":"af_heart"}'
```

**ตัวอย่างผลที่ควรเห็น** (สรุปเฉพาะค่าที่ใช้ตรวจ)

```text
health: ok = true, device = cpu
POST /api/tts: HTTP_STATUS=200
audio_url: /audio/<ชื่อไฟล์ที่สร้างจริง>.wav
duration_sec: มากกว่า 0
sample_rate: 24000
voice: af_heart
```

**ผ่านเมื่อ:** นำ `audio_url` ที่ได้มาต่อท้าย `http://127.0.0.1:8765` แล้วเปิดฟังได้ หรือเปิดเว็บ กรอกข้อความ กด Speak แล้วเครื่องเล่นเล่นเสียงได้ ค่า `model_loaded` อาจเป็น false ก่อนสร้างเสียงครั้งแรก จึงไม่ควรตัดสินจากค่านี้เพียงอย่างเดียว ถ้า health ผ่านแต่สร้างเสียงไม่ได้ ให้ตรวจ error ของ POST และ log ของเว็บ


