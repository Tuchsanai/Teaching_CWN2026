# Lab 5.1 — วาด Architecture Diagram ของ MCP ด้วย Excalidraw MCP

คัดลอกทั้งบล็อกไปวางใน Claude Code (หรือ Codex) ที่ต่อ MCP server `excalidraw` แล้ว

```text
ใช้ Excalidraw MCP วาด Architecture Diagram ของ MCP บนเครื่องนี้ 1 ภาพ (ข้อความในภาพเป็นภาษาไทยผสมคำเทคนิคอังกฤษได้)

โครงสร้างที่ต้องมี (ซ้ายไปขวา 3 โซน):
1. โซน Host = โปรแกรม AI ที่ผู้ใช้ใช้ (Claude Code): มีกล่อง "ผู้ใช้พิมพ์ Prompt", กล่อง "LLM" และกล่อง MCP Client 3 ตัว (ต่อกับ excalidraw, playwright, hello-lab)
2. โซน MCP Server: mcp-excalidraw-server (Node.js), playwright-mcp (Node.js), hello_server.py (Python) พร้อมข้อความอธิบายว่า server ประกาศ Tools / Resources / Prompts
3. โซนเครื่องมือจริง: Excalidraw canvas, Chrome ผ่าน CDP, ฟังก์ชัน Python ของนักศึกษา
ลูกศร: ผู้ใช้→LLM, LLM→MCP Client แต่ละตัว, MCP Client→MCP Server (ป้าย JSON-RPC 1 เส้น), MCP Server→เครื่องมือจริง

กติกา:
- อ่าน read_diagram_guide ก่อน วาง layout เป็นพิกัดก่อนสร้าง ใช้ fontFamily helvetica เพื่อให้ภาษาไทยแสดงผลได้
- ห้ามใส่ text บนกล่องโซน ให้ใช้ text แยกวางที่มุมบนของโซน
- สร้างเสร็จให้ set_viewport แล้ว get_canvas_screenshot ตรวจว่า ข้อความไม่ล้นกล่อง ลูกศรไม่ลากทะลุกล่องอื่น แล้วแก้ด้วย update_element / delete_element จนผ่าน
- export_to_image เป็น PNG และ export_scene เป็น .excalidraw ชื่อ mcp-architecture
- สุดท้ายรายงาน: ลำดับ tool ที่เรียกทั้งหมด จำนวนรอบที่ต้องแก้ และปัญหาที่พบ
```

ผลที่คาดหวัง: ภาพแบบ `img/d02-mcp-architecture.png` และบันทึกลำดับ tool แบบ `lab-results/excalidraw/run-*/trace.md`
