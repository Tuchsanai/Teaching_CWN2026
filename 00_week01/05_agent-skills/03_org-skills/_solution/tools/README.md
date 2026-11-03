# เครื่องมือที่ผู้สอนใช้รันส่วน 03 จริง

| ไฟล์ | ใช้ทำอะไร |
|---|---|
| `run-desk.sh <lab> <user> <prompt.txt>` | เปิด Claude Code แบบ headless ที่โต๊ะ `desks/<user>` แล้วเก็บ log แบบ stream-json (ใช้พิสูจน์ว่าหยิบ skill ไหน) |
| `summarize.py <log.jsonl>` | สรุป log: skill ที่หยิบ, จำนวนคำสั่ง, เวลา, คำตอบสุดท้าย |
| `ci-status.sh <PR...>` | ดูสถานะ CI ของ PR ใน Gitea |
| `cap.mjs <scenes.json>` + `capture-scenes/` | ล็อกอิน Gitea แบบ headless แล้วถ่ายภาพ/วิดีโอ (แปลงเป็น GIF ด้วย ffmpeg) — "playlist" ของทุก LAB |
| `joblogs2.mjs` | ดึง log ของ job CI จากหน้าเว็บ Gitea |
| `chart-lab3.py`, `chart-graph.py` | วาดกราฟจากข้อมูลจริงของ LAB 3 และ LAB 7 |

ผลจริงในส่วน 03 รันในสำเนาแยก `C:/t/org05/novatech` ด้วย `claude -p ... --strict-mcp-config --model opus` (ไม่เชื่อม Chrome) และ `--resume <session>` เมื่อเป็น "แชตเดิม"
