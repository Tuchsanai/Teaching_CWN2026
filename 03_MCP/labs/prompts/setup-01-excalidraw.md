# Setup Prompt S1 — ติดตั้งเฉพาะ Excalidraw MCP

```text
ติดตั้งและลงทะเบียน Excalidraw MCP ให้ Claude Code บนเครื่องนี้ โดยไม่ต้องถามกลับ
1. ตรวจว่ามี node และ npm (รายงานเวอร์ชัน) ถ้าไม่มีให้บอกวิธีติดตั้งแล้วหยุด
2. npm install -g mcp-excalidraw-server แล้วตรวจว่าคำสั่ง mcp-excalidraw-server อยู่ใน PATH (บอก path เต็ม)
3. claude mcp add --scope user excalidraw -- <path เต็มของ mcp-excalidraw-server> (ถ้ามีชื่อ excalidraw อยู่แล้วให้ remove ก่อน)
4. claude mcp list แล้วรายงานว่า excalidraw เป็น Connected หรือไม่ ถ้าไม่ให้อ่าน error และแก้จนผ่าน
5. บอกผู้ใช้ว่า canvas จะเปิดอัตโนมัติที่ http://127.0.0.1:3000 เมื่อ Claude Code เรียก tool ครั้งแรก และต้องเปิด URL นี้ในเบราว์เซอร์ก่อนจึงจะ screenshot / export ได้ แล้วให้พิมพ์ /exit และเปิด claude ใหม่
```

**ตรวจอย่างไรว่าพรอมป์ต์นี้ทำงานสำเร็จ**

**วิธีอ่านผล:** ตัวอย่างด้านล่างเป็น **ผลที่คาดหวัง (Expected output)** เพื่อใช้ตรวจงาน ไม่ใช่ผลรันใหม่หรือข้อความที่ Host ต้องตอบตรงทุกตัวอักษร ค่า path ชื่อไฟล์ และเวลาจะแตกต่างกันได้ ต้องมีผลจาก tool หรือไฟล์จริงรองรับคำว่า “ผ่าน”

**ทดสอบหลังติดตั้ง:** เปิด Host เป็น session ใหม่ เปิด canvas ตาม URL ที่ server รายงานในเบราว์เซอร์ (หรือใช้ Playwright ถ้าติดตั้งแล้ว) แล้ววางข้อความนี้

```text
ใช้ Excalidraw MCP วาดกล่องข้อความ “MCP พร้อมใช้งาน” 1 กล่อง ถ่ายภาพตรวจ แล้วส่งออก PNG รายงานชื่อ tool และ path ของไฟล์ที่สร้างจริง
```

**ตัวอย่างผลที่ควรเห็น**

```text
สร้างกล่องบน canvas ได้
get_canvas_screenshot → เห็นกล่องและข้อความ
export_to_image → ได้ path ของ PNG ที่เปิดดูได้
```

**ผ่านเมื่อ:** เปิด PNG แล้วเห็นกล่องและข้อความที่ขอ หากเจอ `No frontend client connected` ให้เปิด canvas ก่อนแล้วลองใหม่ ถ้ามีเพียงรายการ tool แต่ไม่มีภาพ ยังไม่ผ่านการทดสอบส่งออก


