ทดสอบ 2026-09-30 ใน container devtools-pwmcp-c34a6add: คำสั่ง LLM ตัดสินใจของ agent
ส่งพรอมต์สั้น (combobox e107) ทาง stdin ใช้ --output-format stream-json --verbose เพื่อดู init.tools
before: yolo1 -p --model haiku --effort low --json-schema <schema> --no-session-persistence --strict-mcp-config --tools ""
after : คำสั่งเดิม + --disallowedTools mcp__playwright
ไฟล์ .summary.jsonl = ตัดเฉพาะ init.tools / tool_use / tool_result / result (ลบ session_id, uuid ฯลฯ ออก)
