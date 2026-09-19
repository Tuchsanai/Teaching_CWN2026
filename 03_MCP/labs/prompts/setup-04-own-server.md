# Setup Prompt S4 — ลงทะเบียน MCP server ของนักศึกษา (hello-lab, kokoro-tts)

```text
ลงทะเบียน MCP server ของบทเรียนกับ Claude Code (โฟลเดอร์ปัจจุบันคือ 03_MCP) โดยไม่ต้องถามกลับ
1. ใช้ python ของ labs/.venv (ถ้ายังไม่มี venv หรือยังไม่มีแพ็กเกจ mcp ให้สร้างและ pip install "mcp[cli]" ก่อน)
2. ทดสอบ server โดยไม่ใช้ LLM: <python ของ venv> labs/my-mcp-server/client_test.py --server hello ต้องได้ add(17, 25) = 42
3. claude mcp add --scope user hello-lab -- <python ของ venv> <path เต็มของ labs/my-mcp-server/hello_server.py>
4. claude mcp add --scope user kokoro-tts -e KOKORO_DEVICE=cpu -- <python ของ venv> <path เต็มของ labs/my-mcp-server/tts_server.py>
5. claude mcp list ต้องเห็นทั้งสองตัว Connected ถ้าไม่ให้แก้จนผ่าน แล้วบอกผู้ใช้ให้พิมพ์ /exit และเปิด claude ใหม่
```

**ตรวจอย่างไรว่าพรอมป์ต์นี้ทำงานสำเร็จ**

**วิธีอ่านผล:** ตัวอย่างด้านล่างเป็น **ผลที่คาดหวัง (Expected output)** เพื่อใช้ตรวจงาน ไม่ใช่ผลรันใหม่หรือข้อความที่ Host ต้องตอบตรงทุกตัวอักษร ค่า path ชื่อไฟล์ และเวลาจะแตกต่างกันได้ ต้องมีผลจาก tool หรือไฟล์จริงรองรับคำว่า “ผ่าน”

**ทดสอบหลังติดตั้ง:** จากโฟลเดอร์ `03_MCP` ทดสอบ server โดยตรงก่อน (คำสั่งสำหรับ Linux/macOS)

```bash
labs/.venv/bin/python labs/my-mcp-server/client_test.py --server hello
labs/.venv/bin/python labs/my-mcp-server/client_test.py --server tts
```

จากนั้นเปิด Host เป็น session ใหม่ แล้ววางข้อความนี้

```text
ใช้ tool add ของ hello-lab บวก 17 กับ 25 แล้วใช้ tool speak ของ kokoro-tts สร้างเสียง “Hello students.” รายงาน tool ที่เรียก ผลบวก path ของไฟล์เสียง และความยาวจากผลจริง
```

**ตัวอย่างผลที่ควรเห็น**

```text
Python client: พบ add ใน tools/list และ add(17, 25) = 42
Python client ฝั่ง TTS: พบ speak และสร้างไฟล์เสียงได้
Host เรียก add: 42
Host เรียก speak: ได้ path ของ .wav และ duration_sec > 0
```

**ผ่านเมื่อ:** ทั้ง Python client และ Host เรียกได้จริง หาก client ผ่านแต่ Host หา tool ไม่พบ ให้ตรวจการลงทะเบียนและเปิด session ใหม่ หาก TTS ขาดแพ็กเกจหรือโหลดโมเดลไม่ได้ ให้ทำ S3 ก่อนแล้วทดสอบซ้ำ


