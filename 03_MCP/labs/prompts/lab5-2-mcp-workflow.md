# Lab 5.2 — วาด MCP Workflow (ลำดับข้อความ) ด้วย Excalidraw MCP

```text
ใช้ Excalidraw MCP วาดแผนภาพลำดับการทำงาน (sequence) ของ MCP เมื่อผู้ใช้สั่งงาน 1 ครั้ง
ผู้ร่วมงาน 5 คอลัมน์ซ้ายไปขวา: ผู้ใช้ · AI Agent (LLM) · MCP Client (ใน Host) · MCP Server · Tool จริง
วาดเส้น lifeline แนวตั้งแบบเส้นประใต้แต่ละคอลัมน์ แล้ววาดข้อความเป็นลูกศรแนวนอนเรียงจากบนลงล่าง:
1. ผู้ใช้ → Agent: Prompt
2. MCP Client → MCP Server: tools/list (ตอนเริ่ม session) และ MCP Server → MCP Client: รายการ tool + inputSchema (เส้นประ)
3. MCP Client → Agent: ใส่รายการ tool ลง context
4. Agent → MCP Client: เลือก tool + arguments
5. กล่องสีเหลืองบน MCP Client: Host ขออนุมัติผู้ใช้
6. MCP Client → MCP Server: tools/call {name, arguments}
7. MCP Server → Tool: ทำงานจริง และ Tool → MCP Server: ผล (เส้นประ)
8. MCP Server → MCP Client: result {content, isError}
9. MCP Client → Agent: ผล tool เข้า context
10. Agent → ผู้ใช้: คำตอบ
ตีกรอบเส้นประรอบข้อ 4–9 พร้อมป้าย "วนซ้ำได้หลายรอบ (agent loop)"
ใส่ป้ายข้อความเป็น text แยกวางเหนือลูกศร (ไม่ใช้ label บนลูกศร เพราะจะทับกัน)
ตรวจด้วย screenshot แก้จนไม่มีป้ายทับลูกศร แล้ว export PNG + .excalidraw ชื่อ mcp-sequence และรายงานลำดับ tool ที่เรียก
```

ผลที่คาดหวัง: ภาพแบบ `img/d03-mcp-sequence.png`
