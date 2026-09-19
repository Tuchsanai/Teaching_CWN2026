# Lab 5.4 — ปรับแก้ Diagram เดิมจาก Prompt

```text
จากภาพ Architecture Diagram ของ MCP ที่วาดไว้ใน Lab 5.1 (ไฟล์ mcp-architecture.excalidraw) ให้แก้ตามนี้
1. เพิ่มแถวล่างสุด: MCP Client #4 ต่อกับ server kokoro-tts, กล่อง tts_server.py (Python mcp SDK · stdio) และกล่องเครื่องมือจริง kokoro_core.synthesize() → ไฟล์เสียง .wav พร้อมลูกศรเชื่อมเหมือนแถวอื่น และลูกศรจาก LLM มายัง Client #4
2. ขยายกรอบทั้ง 3 โซนให้ครอบแถวใหม่ และเลื่อนข้อความสรุปด้านล่างลงตาม
3. เปลี่ยนสีกล่อง server ที่นักศึกษาเขียนเอง (hello_server.py และ tts_server.py) เป็นสีเขียว เพื่อแยกจาก server สำเร็จรูปสีม่วง และเพิ่มคำอธิบายสี
4. เปลี่ยนชื่อภาพให้บอกว่าเป็นฉบับแก้จาก Prompt
ตรวจด้วย screenshot แล้ว export PNG + .excalidraw ชื่อ mcp-architecture-modified
รายงาน: tool ที่ใช้แก้ (update_element / batch_create_elements / delete_element) และปัญหาที่พบ
```

ผลที่คาดหวัง: ภาพก่อน `img/d02-mcp-architecture.png` → ภาพหลัง `img/d02b-mcp-architecture-modified.png`
ข้อค้นพบจากรอบทดลอง: `import_scene` ของ mcp-excalidraw-server 2.0.0 อ่านไฟล์ได้เฉพาะในโฟลเดอร์ EXCALIDRAW_EXPORT_DIR และหลัง import พิกัดของกล่องกับข้อความเลื่อนไม่เท่ากัน จึงสร้างภาพใหม่จาก JSON เดิมแทน
