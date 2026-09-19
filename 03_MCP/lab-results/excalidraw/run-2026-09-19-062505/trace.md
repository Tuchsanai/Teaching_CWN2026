# บันทึกการทดลอง Case Study 1 — Excalidraw MCP

ผู้ดำเนินการ: Claude Fable 5.1 (Claude Code 2.1.258, บัญชี yolo2) เรียก MCP server `excalidraw` (mcp-excalidraw-server, canvas ที่ http://127.0.0.1:8892 เปิดใน headless Chrome)
เริ่ม: 2026-09-19T06:25:05Z

ทุกภาพในบทเรียนสร้างจาก prompt → AI Agent → MCP Client (ใน Claude Code) → Excalidraw MCP Server → canvas แล้ว export เป็น PNG + .excalidraw
บันทึกด้านล่างเรียงตามลำดับการเรียก tool จริง (ชื่อ tool = ชื่อที่ server ประกาศผ่าน tools/list)

| ลำดับ | ภาพ | tool ที่เรียก | ผล |
| --- | --- | --- | --- |
| 1 | d01-nxm-problem | `read_diagram_guide` → `describe_scene` (canvas ว่าง) → `batch_create_elements` (49 elements: 2 zone, 3+3 app, 4+4 tool, 1 MCP bar, 4 server, 12+11 arrow, 5 text) → `set_viewport` (scrollToContent) → `get_canvas_screenshot` → `export_to_image` (png) → `export_scene` (.excalidraw) | ผ่านรอบแรก ข้อความไทยแสดงครบ ไม่มีทับซ้อน |
| 2 | d02-mcp-architecture | `clear_canvas` → `batch_create_elements` (31 elements: 3 zone, user, LLM, 3 client, 3 server, 3 tool, arrows, notes) → `set_viewport` → `get_canvas_screenshot` → พบลูกศร LLM→Client #2/#3 ลากทะลุกล่อง Client #1 → `delete_element` ×2 → `batch_create_elements` (ลูกศรหักมุมอ้อมด้านซ้าย 2 เส้น) → `get_canvas_screenshot` ตรวจซ้ำ → `export_to_image` → `export_scene` | แก้ 1 รอบ (arrow crossing) แล้วผ่าน |
| 3 | d03-mcp-sequence | `clear_canvas` → `batch_create_elements` (37 elements: 5 lifeline header, 5 เส้น lifeline, 11 ลูกศรข้อความ + ป้าย, กล่อง permission, กรอบ loop, footer) → `set_viewport` → `get_canvas_screenshot` → พบป้าย "วนซ้ำข้อ 4–9" ทับลูกศรข้อ 9 → `update_element` (ย้ายป้ายไป x=700) → `get_canvas_screenshot` → `export_to_image` → `export_scene` | แก้ 1 รอบ (label overlap) แล้วผ่าน |
| 4 | d04-three-ways | `clear_canvas` → `batch_create_elements` (24 elements: 3 zone, 3 caller, 3 adapter, core bar, 6 arrows, 3 note, footer) → `set_viewport` → `get_canvas_screenshot` → พบข้อความล้นกล่อง caller และป้ายลูกศร HTTP/JSON, JSON-RPC ทับข้อความ → `update_element` ×6 (ขยายกล่อง ย้ายตำแหน่ง ย่อข้อความ) → `get_canvas_screenshot` → `export_to_image` → `export_scene` | แก้ 1 รอบ (text overflow) แล้วผ่าน |
| 5 | d05-case1-excalidraw-flow | `clear_canvas` → `batch_create_elements` (32 elements: 5 กล่อง pipeline, loop arrow, zone tool 8 กล่องแถวเดียว, out box, note) → `set_viewport` → `get_canvas_screenshot` → พบชื่อ tool ตัดคำผิด (กล่องกว้าง 140 px ไม่พอ) และ URL ตัดบรรทัด → `update_element` ×14 (จัดเป็น 2 แถว กล่องกว้าง 280 px, ย่อข้อความ, เลื่อน out box) → `delete_element` ×2 → `batch_create_elements` (ลูกศรหักมุมข้ามแถว + ลูกศรผลลัพธ์ใหม่) → `set_viewport` → `get_canvas_screenshot` → `export_to_image` → `export_scene` | แก้ 1 รอบ (text truncation) แล้วผ่าน |
| 6 | d06-case2-playwright-flow | `clear_canvas` → `batch_create_elements` (35 elements: 5 กล่อง pipeline, loop arrow, เว็บ Kokoro + core 2 กล่อง, zone tool 8 กล่อง 2 แถว, out box, notes) → `set_viewport` → `get_canvas_screenshot` → พบข้อความล้นกล่องแถวบนและกล่องขวา, ป้ายใต้ kokoro ทับกล่อง → `update_element` ×12 (ขยายกล่อง ลด font ย่อข้อความ) → `delete_element` (loop arrow) → `batch_create_elements` (loop arrow ใหม่ให้ตรงจุดกึ่งกลางกล่องที่ขยับ) → `set_viewport` → `get_canvas_screenshot` → `export_to_image` → `export_scene` | แก้ 1 รอบ (text overflow) แล้วผ่าน |
| 7 | d07-own-server | `clear_canvas` → `batch_create_elements` (18 elements: 3 client, server, wire_capture, tts server, 3 กล่องผล, 7 arrows, footer) → `set_viewport` → `get_canvas_screenshot` → พบป้ายลูกศรยาวทับกล่อง client และ tts box ล้นทับ footer → `update_element` ×10 (ขยับ server/ผลไปขวา, ย่อข้อความ, ขยาย tts box, เลื่อน footer) → `delete_element` ×3 → `batch_create_elements` (ลูกศร 3 เส้นป้ายสั้นลง) → `set_viewport` → `get_canvas_screenshot` → `export_to_image` → `export_scene` | แก้ 1 รอบ (arrow-label overlap) แล้วผ่าน |
| 8 | d08-lesson-map | `clear_canvas` → `batch_create_elements` (21 elements: 8 กล่องบท 2 แถว, 7 arrows, legend 4 กล่อง, footer) → `set_viewport` → `get_canvas_screenshot` → `export_to_image` → `export_scene` | ผ่านรอบแรก |
| 9 | Lab 5.4 แก้ d02 จาก Prompt | `import_scene` (filePath ใน 03_MCP/img) → **error** `Path traversal blocked: ... resolves outside the allowed directory "/root/workspace/.mcp/excalidraw/diagrams"` → `import_scene` จากโฟลเดอร์ที่อนุญาต (43 elements) → `update_element` ×5 (ขยาย zone 3 กล่อง, เลื่อน footer, เปลี่ยนสี hello_server.py เป็นเขียว) → `batch_create_elements` (Client #4, tts_server.py, kokoro_core, ลูกศร 3 เส้น) → `set_viewport` → `get_canvas_screenshot` → พบว่า scene ที่ import กลับมา **ตำแหน่งกล่องกับข้อความเลื่อนไม่เท่ากัน** (zone และกล่องเลื่อนขวา ~570 px แต่ข้อความอิสระไม่เลื่อน) → ตัดสินใจ `clear_canvas` แล้ว `batch_create_elements` ใหม่จาก JSON เดิมของ d02 + ส่วนที่ Prompt สั่งเพิ่ม (41 elements) → `set_viewport` → `get_canvas_screenshot` → `export_to_image` → `export_scene` | สำเร็จหลังเปลี่ยนวิธี (ข้อค้นพบ: import_scene ของ server รุ่นนี้ทำให้พิกัดเพี้ยน จึงควรเก็บ JSON ต้นฉบับไว้สร้างซ้ำ) |

จบ: 2026-09-19T06:45:32Z

## สรุปจำนวนการเรียก tool (นับจากตารางด้านบน)

| tool | จำนวนครั้ง |
| --- | --- |
| batch_create_elements | 14 |
| update_element | 49 |
| delete_element | 8 |
| get_canvas_screenshot | 16 |
| set_viewport | 13 |
| export_to_image / export_scene | 9 / 9 |
| clear_canvas | 9 |
| import_scene | 2 (ครั้งแรก error path traversal, ครั้งที่สองพิกัดเพี้ยน) |
| read_diagram_guide / describe_scene | 1 / 1 |

## ข้อสังเกตจากการทดลอง
1. ทุกภาพต้องผ่านวงจร วาด → screenshot → แก้ อย่างน้อย 1 รอบ (7 จาก 9 ภาพ) ปัญหาที่พบบ่อยคือข้อความล้นกล่อง (กล่องแคบเกินไปสำหรับฟอนต์ลายมือ) และลูกศรลากทะลุกล่องอื่น
2. ข้อความภาษาไทยแสดงผลได้เมื่อกำหนด fontFamily เป็น helvetica (รหัส 2); ป้ายในกล่อง (bound label) ยังใช้ฟอนต์ลายมือของ Excalidraw ซึ่งรองรับไทยได้เช่นกัน
3. export_to_image / export_scene / import_scene เขียนและอ่านได้เฉพาะในโฟลเดอร์ EXCALIDRAW_EXPORT_DIR (/root/workspace/.mcp/excalidraw/diagrams) ต้องคัดลอกไฟล์ออกมาเอง
4. import_scene แล้วแก้ต่อ ทำให้พิกัดกล่องกับข้อความไม่ตรงกัน จึงเก็บ JSON ต้นฉบับ (ในบันทึกการสนทนาและไฟล์ .excalidraw) แล้วสร้างใหม่ทั้งภาพเมื่อจะแก้
