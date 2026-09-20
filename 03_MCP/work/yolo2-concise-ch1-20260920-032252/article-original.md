### 1.2 MCP คืออะไร

**Model Context Protocol (MCP)** คือโปรโตคอลเปิด (open protocol) ที่ Anthropic เผยแพร่ในเดือนพฤศจิกายน 2024 และปัจจุบันดูแลโดยชุมชนที่ [modelcontextprotocol.io](https://modelcontextprotocol.io) สเปกฉบับล่าสุดที่ใช้ในบทเรียนนี้คือรุ่น **2026-07-28** ซึ่งนิยามไว้ว่า

> MCP is an open protocol that enables seamless integration between LLM applications and external data sources and tools.

หัวใจของ MCP มี 3 อย่าง

1. **ภาษากลางแบบเดียว** — ทุกข้อความเป็น [JSON-RPC 2.0](https://www.jsonrpc.org/) (JSON ที่มี `method`, `params`, `id`, `result`)
2. **การค้นพบอัตโนมัติ** — server "ประกาศ" ว่ามีเครื่องมืออะไร รับ argument แบบไหน (`tools/list`) โดย Host ไม่ต้องรู้ล่วงหน้า
3. **แยกบทบาทชัดเจน** — Host/Client เป็นฝั่ง AI, Server เป็นฝั่งเครื่องมือ ใครเขียนฝั่งไหนก็ได้ ภาษาอะไรก็ได้

สเปกเปรียบ MCP กับ Language Server Protocol (LSP) ที่ทำให้ editor ทุกตัวรองรับภาษาโปรแกรมได้ผ่านมาตรฐานเดียว หลายคนจึงเรียก MCP ว่า "USB-C ของ AI"

### 1.3 ทำไม AI Agent / LLM จึงต้องใช้ MCP

| ถ้าไม่มี MCP | เมื่อมี MCP |
| --- | --- |
| ต้องเขียนโค้ดบอก LLM เองว่า tool แต่ละตัวชื่ออะไร รับ argument อะไร | Host เรียก `tools/list` แล้วได้ชื่อ คำอธิบาย และ `inputSchema` (JSON Schema) จาก server อัตโนมัติ |
| ต้องเขียน glue code แปลงคำตอบของ LLM ไปเรียก API จริง | Host ส่ง `tools/call {name, arguments}` ตามมาตรฐาน server ทำงานแล้วตอบ `result` |
| เครื่องมือที่ทำให้ Claude Code ใช้ ไม่ได้ทำให้ Codex ใช้ | server เดียวใช้ได้กับทุก Host ที่พูด MCP (บทเรียนนี้ใช้ Excalidraw MCP และ Playwright MCP ตัวเดียวกันทั้งใน Claude Code และ Codex) |
| ไม่มีจุดกลางสำหรับขออนุมัติผู้ใช้ | สเปกกำหนดให้ Host ถามผู้ใช้ก่อนเรียก tool ("there SHOULD always be a human in the loop") |

ตัวอย่างในบทเรียนนี้เอง: **แผนภาพทั้ง 9 ภาพวาดโดย AI Agent (Claude Code) ผ่าน Excalidraw MCP** และ **การกรอกฟอร์มบนเว็บ Kokoro ทำผ่าน Playwright MCP** โดยผู้สอนไม่ได้เขียนโค้ดเชื่อม Excalidraw หรือเบราว์เซอร์กับ Claude เลย เพียงตั้งค่าให้ Claude Code รู้จัก MCP server สองตัวนี้

### 1.4 สิ่งที่ MCP ไม่ใช่

- ไม่ใช่โมเดล AI และไม่ใช่ agent framework — เป็นแค่ "ภาษากลาง" ระหว่าง AI กับเครื่องมือ
- ไม่ได้มาแทน REST API หรือ Python function — แต่ครอบของเดิมให้ AI ค้นพบและเรียกได้ (ดูบทที่ 3)
- ไม่ได้ทำให้ AI ทำอะไรก็ได้ — Host ยังเป็นผู้คุมสิทธิ์และผู้ใช้เป็นผู้อนุมัติ

---

