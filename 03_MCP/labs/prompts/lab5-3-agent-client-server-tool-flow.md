# Lab 5.3 — วาด Flow: AI Agent → MCP Client → MCP Server → Tool

```text
ใช้ Excalidraw MCP วาดภาพ "Flow ของ Case Study 1" 1 ภาพ ประกอบด้วย
แถวบน 5 กล่องซ้ายไปขวา: Prompt ของนักศึกษา → AI Agent (Claude Code) → MCP Client → Excalidraw MCP Server → Canvas ในเบราว์เซอร์ (127.0.0.1:8892)
ลูกศรเส้นประโค้งจาก Canvas ย้อนกลับไป AI Agent พร้อมป้าย "screenshot ส่งกลับให้ AI ตรวจแล้วแก้จนผ่าน"
โซนด้านล่าง: รายชื่อ tool ของ Excalidraw MCP ที่ถูกเรียกจริงในแล็บ เรียงตามลำดับ (read_diagram_guide → describe_scene → batch_create_elements → set_viewport → get_canvas_screenshot → update_element/delete_element → export_to_image → export_scene) จัด 2 แถว แถวละ 4 กล่อง กล่องกว้างพอให้ชื่อ tool อยู่บรรทัดเดียว
กล่องผลลัพธ์ด้านล่าง: "PNG + .excalidraw ใน img/ และ trace.md ใน lab-results/"
ตรวจด้วย screenshot: ชื่อ tool ต้องไม่ถูกตัดคำ ถ้าถูกตัดให้ขยายกล่องหรือลด font แล้ว export PNG + .excalidraw ชื่อ case1-flow และรายงานลำดับ tool ที่เรียก
```

ผลที่คาดหวัง: ภาพแบบ `img/d05-case1-excalidraw-flow.png` (ในรอบทดลองจริง กล่องกว้าง 140 px ทำให้ชื่อ tool ถูกตัดคำ ต้องแก้เป็น 2 แถว กล่องกว้าง 280 px)
