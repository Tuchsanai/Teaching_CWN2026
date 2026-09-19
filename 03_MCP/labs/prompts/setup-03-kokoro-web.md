# Setup Prompt S3 — ติดตั้งและเริ่มเว็บทดลอง Kokoro TTS

```text
ติดตั้งและเริ่มเว็บทดลอง Kokoro TTS ของบทเรียน 03_MCP (โฟลเดอร์ปัจจุบันคือ 03_MCP) โดยไม่ต้องถามกลับ ห้ามแก้โค้ดใน labs/kokoro-web
1. สร้าง venv ที่ labs/.venv ถ้ายังไม่มี แล้วใช้ python/pip ของ venv นี้
2. pip install soundfile fastapi uvicorn จากนั้นถ้ายังไม่มี torch ให้ pip install torch --index-url https://download.pytorch.org/whl/cpu แล้ว pip install kokoro ถ้ามี apt ให้ติดตั้ง espeak-ng
3. ตั้ง PYTHON=<python ของ venv> แล้วรัน labs/kokoro-web/run.sh
4. รอจน curl http://127.0.0.1:8765/api/health ได้ "ok":true แล้วทดสอบ POST /api/tts ด้วยข้อความ "Setup test from prompt." บันทึกเวลาที่ใช้และขนาดไฟล์เสียงที่ได้
5. รายงาน pid ของเว็บ (อยู่ใน labs/kokoro-web/server.pid) และวิธีหยุด (kill pid) พร้อมปัญหาที่พบตามจริง
```
