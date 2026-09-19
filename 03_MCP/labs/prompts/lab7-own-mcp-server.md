# Lab 7.1–7.4 — สร้างและทดสอบ MCP server ของตัวเอง

## Lab 7.1 เขียน server (ไม่ต้องใช้ AI)
คัดลอก `labs/my-mcp-server/hello_server.py` แล้วเพิ่ม tool ของตัวเอง 1 ตัว (เช่น `to_upper(text)`), resource 1 ตัว และ prompt 1 ตัว

## Lab 7.2 ทดสอบด้วย Python client และดูข้อความบนสาย
```bash
cd labs/my-mcp-server
/opt/venv/bin/python client_test.py --server hello --wire wire-hello.jsonl
```
ตอบคำถาม: protocol_version ที่ client รายงานคืออะไร · ข้อความแรกที่ client ส่งคือ method อะไร · inputSchema ของ tool ที่เพิ่มถูกสร้างจากอะไร

## Lab 7.3 ให้ Claude Code ค้นพบและเรียก tool ของเรา
Prompt รอบค้นพบ (ไม่เรียก tool):
```text
แสดงรายชื่อ tool ทั้งหมดที่ได้จาก MCP server ชื่อ hello-lab และ kokoro-tts พร้อมพารามิเตอร์ของแต่ละ tool ไม่ต้องเรียกใช้ tool
```
Prompt รอบใช้งาน:
```text
ใช้ tool จาก MCP server hello-lab: บวก 17 กับ 25, บอกเวลาปัจจุบัน และนับคำในประโยค 'Model Context Protocol lets one server serve many agents' จากนั้นอ่าน resource lab://info แล้วสรุปผลทั้งหมด พร้อมระบุว่าเรียก tool ชื่ออะไรบ้างและด้วย argument อะไร
```
คำสั่งรัน (ครั้งเดียว ไม่ต้องติดตั้งถาวร):
```bash
claude -p --strict-mcp-config --mcp-config labs/my-mcp-server/mcp.json --output-format stream-json --verbose "<prompt>"
```

## Lab 7.4 เปิด Kokoro เป็น MCP tool
```text
ใช้ tool speak จาก MCP server kokoro-tts สร้างเสียงจากข้อความ 'Model Context Protocol lets one server serve many agents.' แล้วบอก path ของไฟล์เสียงและความยาวเป็นวินาที
```
เปรียบเทียบกับ Lab 6: งานเดียวกัน แต่ AI ไม่ต้องเปิดเบราว์เซอร์และไม่ต้องรู้ URL ของ API
