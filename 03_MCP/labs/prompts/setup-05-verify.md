# Prompt S5 — ตรวจว่า MCP ทุกตัวใช้งานได้จริง (รันใน session ใหม่หลังติดตั้ง)

```text
ตรวจว่า MCP server ที่ติดตั้งไว้ใช้งานได้จริง ทำตามลำดับและรายงานผลทุกข้อพร้อมชื่อ tool ที่เรียก
1. เรียก tool add ของ server hello-lab ด้วย a=17, b=25 ต้องได้ 42
2. ใช้ Playwright MCP เปิด http://127.0.0.1:3000 (canvas ของ Excalidraw) แล้วคง tab นี้ไว้ (ถ้าเครื่องมีจอและผู้ใช้เปิด URL นี้ไว้แล้ว ให้ข้ามข้อนี้ได้)
3. ใช้ Excalidraw MCP วาดกล่อง 3 กล่อง "Host" → "MCP Client" → "MCP Server" เชื่อมด้วยลูกศร แล้ว get_canvas_screenshot และ export_to_image เป็น PNG บอก path ของไฟล์ที่ได้
4. ใช้ Playwright MCP เปิด http://127.0.0.1:8765 กรอกข้อความ "Verify prompt works." กด Speak รอจน "สร้างเสียงสำเร็จ" แล้วอ่านความยาวเสียง
5. เรียก tool speak ของ server kokoro-tts ด้วยข้อความ "Hello from MCP." บอก path และความยาวไฟล์เสียง
6. สรุปเป็นตาราง: server, tool ที่เรียก, ผล, ผ่าน/ไม่ผ่าน ถ้าข้อใดไม่ผ่านให้คัดลอกข้อความ error จริง
```
