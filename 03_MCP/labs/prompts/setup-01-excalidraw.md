# Setup Prompt S1 — ติดตั้งเฉพาะ Excalidraw MCP

```text
ติดตั้งและลงทะเบียน Excalidraw MCP ให้ Claude Code บนเครื่องนี้ โดยไม่ต้องถามกลับ
1. ตรวจว่ามี node และ npm (รายงานเวอร์ชัน) ถ้าไม่มีให้บอกวิธีติดตั้งแล้วหยุด
2. npm install -g mcp-excalidraw-server แล้วตรวจว่าคำสั่ง mcp-excalidraw-server อยู่ใน PATH (บอก path เต็ม)
3. claude mcp add --scope user excalidraw -- <path เต็มของ mcp-excalidraw-server> (ถ้ามีชื่อ excalidraw อยู่แล้วให้ remove ก่อน)
4. claude mcp list แล้วรายงานว่า excalidraw เป็น Connected หรือไม่ ถ้าไม่ให้อ่าน error และแก้จนผ่าน
5. บอกผู้ใช้ว่า canvas จะเปิดอัตโนมัติที่ http://127.0.0.1:3000 เมื่อ Claude Code เรียก tool ครั้งแรก และต้องเปิด URL นี้ในเบราว์เซอร์ก่อนจึงจะ screenshot / export ได้ แล้วให้พิมพ์ /exit และเปิด claude ใหม่
```
