---
name: cyolo
description: เรียก Codex CLI ทุกบัญชี (cyolo1…cyoloN) แบบไม่โต้ตอบ เลือกรุ่นและ effort จาก models_cache.json สร้างภาพ ตรวจล็อกอิน โควตา และสถิติต่อครั้ง ใช้เมื่อ "ให้ cyolo ตรวจ", "เรียก cyolo1", "สร้างภาพ", "โควตา Codex", "สถิติโทเค็นแต่ละบัญชี". Run any Codex account non-interactively, pick model/effort from models_cache.json, generate PNG images, verify login, read quota and per-call stats. Use for "have cyolo review", "call cyolo1", "generate an image", "Codex quota", "token stats per account".
---

# cyolo — Codex CLI ทุกบัญชี

สคริปต์: `/root/ai-accounts/.Codex/shared/skills/cyolo/scripts/cyolo.py` (เรียกว่า `C` ด้านล่าง)

| ต้องการ | คำสั่ง |
|---|---|
| เรียกงานเดียว | `python3 C run --account cyolo1 --difficulty 1 "ตอบ OK"` |
| ระบุรุ่น/effort เอง | `python3 C run --account cyolo1 --model gpt-5.6-luna --effort medium "..."` |
| สร้างภาพ PNG | `python3 C image --account cyolo1 --out /workspace/a.png "แมวสีแดงเล็ก ๆ"` |
| รุ่นและ effort ที่รองรับ | `python3 C models --account cyolo1` |
| ตรวจความพร้อมทุกบัญชี (เรียกจริง) | `python3 C check` |
| โควตาทุกบัญชี | `python3 C quota` (`--refresh` เรียกโมเดล 1 ครั้งเพื่ออัปเดต) |
| สถิติตามบัญชี/รุ่น/run | `python3 C stats` (`--run <id>`, `--json`) |
| prompt จากไฟล์ / stdin | `--prompt-file x.txt` หรือส่ง `-` เป็น prompt |

## ความยาก → effort

`--difficulty 1..6` → `low, medium, high, xhigh, max, ultra` · ระดับที่รุ่นไม่รองรับสคริปต์ลดเป็นระดับสูงสุดที่รองรับ และบันทึก `effort_note` · ไม่ระบุรุ่นใช้รุ่นแรกที่แสดงใน `models_cache.json`

## กฎสำคัญ

- สคริปต์ใช้ `exec --skip-git-repo-check --ephemeral --json -o <ไฟล์>` ปิด stdin และอ่านคำตอบจากไฟล์ `-o`
- exit 0 อาจไม่สำเร็จ (401 แล้ว retry) จึงตรวจ `turn.failed` และไฟล์คำตอบ `run` คืน non-zero เมื่อไม่สำเร็จ
- `--ephemeral` เร็วกว่าแต่ไม่อัปเดตโควตา `quota` จึงบอกเวลาของข้อมูลเสมอ
- `input_tokens` ของ Codex รวม `cached_input_tokens` อยู่แล้ว
- สถานะล็อกอินอ่านข้อความจาก `login status` ไม่ใช่ exit code
- สร้างภาพใช้ effort `low` และตรวจ PNG signature ก่อนคืนผล
- ทุกครั้งที่สคริปต์เรียกบัญชีจะเพิ่มแถวใน `/workspace/.agent-team/ledger.jsonl`
- ห้ามอ่านหรือส่งต่อ `auth.json`

## เรียกจาก host

อ่านสกิลก่อนเริ่ม แล้วเรียกผ่าน `docker exec` (ใช้ path แบบ `../root/...` ได้ทั้ง PowerShell และ Git Bash โดยไม่ต้องแก้):

```
docker exec multi-account cat ../root/ai-accounts/.Codex/shared/skills/cyolo/SKILL.md
docker exec -i multi-account python3 ../root/ai-accounts/.Codex/shared/skills/cyolo/scripts/cyolo.py check
docker exec -i multi-account python3 ../root/ai-accounts/.Codex/shared/skills/cyolo/scripts/cyolo.py quota
docker exec -i multi-account python3 ../root/ai-accounts/.Codex/shared/skills/cyolo/scripts/cyolo.py models --account cyolo1
docker exec -i multi-account python3 ../root/ai-accounts/.Codex/shared/skills/cyolo/scripts/cyolo.py stats
docker exec -i multi-account python3 ../root/ai-accounts/.Codex/shared/skills/cyolo/scripts/cyolo.py run --account cyolo1 --difficulty 1 "ตอบ OK"
docker exec -i multi-account python3 ../root/ai-accounts/.Codex/shared/skills/cyolo/scripts/cyolo.py image --account cyolo1 --out host_a.png "จุดสีแดง"
```

`--out` แบบ relative จะอยู่ใน `/workspace` (ถ้าส่ง absolute path จาก Git Bash ให้เขียน `--out ../workspace/a.png` เพื่อเลี่ยงการแปลง path)
