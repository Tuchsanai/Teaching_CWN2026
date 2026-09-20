# Setup Prompt S4 — แล็บต่อเนื่องของบทเรียน (hello-lab, kokoro-tts, เว็บ Kokoro)

ส่วนนี้ **ไม่ใช่เงื่อนไขเริ่มต้นของการติดตั้งเครื่องมือภายนอก** แต่เป็นแล็บต่อเนื่องเมื่อจะ "สร้าง MCP server เอง" ในบทที่ 7 และใช้เว็บทดลองในบทที่ 6 โฟลเดอร์ [`labs/my-mcp-server/`](../my-mcp-server/) มี `hello_server.py` และ `tts_server.py` ที่เขียนไว้แล้วเป็นตัวอย่างอ้างอิง ส่วน [`labs/kokoro-web/`](../kokoro-web/) คือเว็บ FastAPI ที่ใช้เป็นเป้าหมายให้ Playwright ควบคุม ถ้าเพิ่งเริ่มบทที่ 4 ให้ข้ามข้อนี้ไปก่อนได้

```text
ในโฟลเดอร์บทเรียน 03_MCP นี้มีโค้ดแล็บเตรียมไว้ที่ labs/my-mcp-server (hello_server.py, tts_server.py) และเว็บทดลองที่ labs/kokoro-web
ช่วยเตรียมให้ใช้งานได้โดยไม่แก้โค้ดในสองโฟลเดอร์นั้น: สร้าง virtual environment ที่ labs/.venv ติดตั้งแพ็กเกจที่โค้ดต้องใช้ (อ่านจากไฟล์เอง) ทดสอบ server ด้วย labs/my-mcp-server/client_test.py โดยยังไม่ผ่าน LLM ให้เห็น tools/list และผล add(17, 25) = 42 จากนั้นตั้งค่าให้ Claude Code รู้จัก server ทั้งสองตัว และเริ่มเว็บทดลองด้วย labs/kokoro-web/run.sh แล้วตรวจ health endpoint จนพร้อมใช้งาน
รายงานคำสั่งที่รันจริง ผลทดสอบ และปัญหาที่เจอตามจริง
```

**ตรวจอย่างไรว่าคำขอนี้ทำงานสำเร็จ**

**วิธีอ่านผล:** ตัวอย่างด้านล่างเป็น **ผลที่คาดหวัง (Expected output)** เพื่อใช้ตรวจงาน ไม่ใช่ผลรันใหม่หรือข้อความที่ Host ต้องตอบตรงทุกตัวอักษร ค่า path ชื่อไฟล์ และเวลาจะแตกต่างกันได้ ต้องมีผลจาก tool หรือไฟล์จริงรองรับคำว่า “ผ่าน”

**ทดสอบหลังติดตั้ง:** จากโฟลเดอร์ `03_MCP` ทดสอบ server โดยตรงก่อน (คำสั่งสำหรับ Linux/macOS)

```bash
labs/.venv/bin/python labs/my-mcp-server/client_test.py --server hello
labs/.venv/bin/python labs/my-mcp-server/client_test.py --server tts
curl -sS http://127.0.0.1:8765/api/health
```

จากนั้นเปิด Host เป็น session ใหม่ แล้ววางข้อความนี้

```text
ใช้ tool add ของ hello-lab บวก 17 กับ 25 แล้วใช้ tool speak ของ kokoro-tts สร้างเสียง “Hello students.” รายงาน tool ที่เรียก ผลบวก path ของไฟล์เสียง และความยาวจากผลจริง
```

**ตัวอย่างผลที่ควรเห็น**

```text
Python client: พบ add ใน tools/list และ add(17, 25) = 42
Python client ฝั่ง TTS: พบ speak และสร้างไฟล์เสียงได้
health ของเว็บ: ok = true, device = cpu
Host เรียก add: 42
Host เรียก speak: ได้ path ของ .wav และ duration_sec > 0
```

**ผ่านเมื่อ:** ทั้ง Python client และ Host เรียกได้จริง หาก client ผ่านแต่ Host หา tool ไม่พบ ให้ตรวจการตั้งค่าและเปิด session ใหม่ หาก TTS ขาดแพ็กเกจหรือโหลดโมเดลไม่ได้ ให้ทำ S3 ก่อนแล้วทดสอบซ้ำ ค่า `model_loaded` อาจเป็น false ก่อนสร้างเสียงครั้งแรก จึงไม่ควรตัดสินจากค่านี้เพียงอย่างเดียว

---

เนื้อหาไฟล์นี้ตรงกับ readme.md บทที่ 4 (ฉบับแก้ 20 กันยายน 2026) เส้นทางหลักคือส่งลิงก์ repo ต้นทางพร้อมคำขอภาษาธรรมดา แล้วให้ AI อ่าน README เลือกวิธีติดตั้งเอง พรอมป์ต์ติดตั้งฉบับละเอียดของเดิมย้ายไปเป็นข้อมูลอ้างอิงใน readme.md ข้อ 4.6.9
