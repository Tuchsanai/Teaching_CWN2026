---
name: cyolo
description: เรียก Codex CLI ของบัญชี cyolo1…cyoloN แบบไม่โต้ตอบ — เลือกรุ่น/effort จาก models_cache.json (ลดระดับที่รุ่นไม่รองรับให้เอง), สร้างภาพ PNG, ตรวจล็อกอินจริง, อ่านโควตา rate_limits พร้อมเวลาของข้อมูล และบันทึกสถิติโทเค็นทุกครั้งลง ledger ใช้เมื่อ "ให้ cyolo ตรวจ", "เรียก cyolo1", "สร้างภาพด้วย codex", "โควตา codex", "สถิติโทเค็นแต่ละบัญชี" · Use to call Codex CLI accounts (cyoloN) non-interactively, pick model/effort, generate images, check login, quota and token stats.
---

# cyolo — Codex CLI หลายบัญชี (`cyolo1`…`cyoloN`)

สคริปต์: `/root/ai-accounts/.Codex/shared/skills/cyolo/scripts/cyolo.py` (ใน container `multi-account`; สำเนาเดียวกันอยู่ที่ `/root/ai-accounts/.Claude/shared/skills/cyolo/`) เรียกสั้น ๆ ว่า `X`

| ต้องการ | คำสั่ง |
|---|---|
| ถามงานเดียว (effort ตามความยาก) | `python3 X ask cyolo1 "<prompt>" --difficulty 1` |
| ระบุรุ่น/effort | `python3 X ask cyolo2 "<prompt>" -m gpt-6.1-sol --effort high` |
| ผล + สถิติเป็น JSON | `python3 X ask cyolo1 "<prompt>" --json` |
| ผลแบบมีโครงสร้าง | `python3 X ask cyolo1 "<prompt>" --output-schema /path/schema.json` (schema แบบ strict) |
| สร้างภาพ PNG | `python3 X image cyolo1 "<เงื่อนไขภาพเป็นข้อ ๆ>" /workspace/out/pic.png` |
| ตรวจความพร้อม | `python3 X check` |
| โควตา (+เวลาของข้อมูล) | `python3 X quota` · อัปเดตด้วย `python3 X quota --refresh` (เรียกสั้น 1 ครั้ง) |
| รุ่นและ effort ที่รองรับ | `python3 X models` |

`ask` พิมพ์คำตอบทาง stdout, บรรทัดสถิติทาง stderr `[cyolo1 gpt-6.1-sol/low 4.5s in=17790 (cached 12288) out=5 reasoning=0 ok]` · exit 0 = สำเร็จจริง

## ความยาก → effort (ตารางเดียวกับ yolo และ agent-team)

| difficulty | งาน | Codex effort |
|---|---|---|
| 1 | ดึงข้อมูล จัดรูปแบบ ตรวจความพร้อม · สร้างภาพ | `low` |
| 2 | สรุป ถาม-ตอบ แก้โค้ดจุดเดียว (ค่าเริ่มต้น) | `medium` |
| 3 | แก้โค้ดหลายไฟล์ debug วิเคราะห์ | `high` |
| 4 | reasoning ซับซ้อน | `xhigh` |
| 5 | ต้องถูกแน่นอน | `max` |
| 6 | งานใหญ่ที่ควรแตกงานย่อยเอง | `ultra` (ถ้ารุ่นรองรับ ไม่งั้นลดเป็น `max` และบันทึก `effort_note`) |

รุ่นเริ่มต้น = รุ่นที่ไม่ซ่อนและ priority สูงสุดใน `models_cache.json` (ตอนนี้ `gpt-6.1-sol`) · ตั้งเองด้วย env `MA_CODEX_MODEL`

## กฎที่สคริปต์ทำให้แล้ว

- `cyoloN exec --skip-git-repo-check --ephemeral -m M -c model_reasoning_effort=E --json -o <ไฟล์> "<prompt>" < /dev/null`
- คำตอบอ่านจากไฟล์ `-o` (ห้าม `-o /dev/stdout`) · usage จาก `turn.completed` (`input_tokens` รวม cached แล้ว) · ล้ม = `turn.failed`
- `--ephemeral` เร็วกว่า ~3.5 เท่า แต่ไม่เขียน `sessions/` → โควตาไม่อัปเดต (ใช้ `quota --refresh`)
- ล็อกอินดูจากข้อความ `login status` (`Logged in using ChatGPT` / `Not logged in`) ไม่ใช่ exit code · บัญชีไม่ล็อกอิน exec จะ retry 401 ~15 s แล้วล้ม → `check` ข้ามการเรียก exec ของบัญชีที่ `Not logged in` (ใส่ `--deep` ถ้าต้องการเรียกจริง)
- effort ที่รุ่นไม่รองรับ → ลดเป็นระดับสูงสุดที่รองรับก่อนเรียก
- สร้างภาพทำได้ฝั่ง Codex เท่านั้น · effort `low` เสมอ (~60–80 s/ภาพ) · แจกแจงเงื่อนไขภาพเป็นข้อ (จำนวน สี ตำแหน่ง ข้อความ) · ตรวจ PNG signature ให้
- ทุกการเรียกเพิ่ม 1 แถวใน `/workspace/.agent-team/ledger.jsonl` · `MA_SIMULATE_LIMIT=cyolo1` จำลองโควตาหมด
- ห้ามอ่าน/ส่งต่อ `auth.json` · ห้ามพิมพ์ส่วน `identity` ของ models_cache · ห้ามล็อกอินแทนผู้ใช้

รายละเอียด JSONL, โควตา และภาพ: [`references/codex-cli.md`](references/codex-cli.md)

## เรียกจาก host (ใช้ได้ทั้ง PowerShell และ Git Bash)

```
docker exec multi-account sh -c "cat /root/ai-accounts/.Codex/shared/skills/cyolo/SKILL.md"
docker exec multi-account sh -c "python3 /root/ai-accounts/.Codex/shared/skills/cyolo/scripts/cyolo.py check"
docker exec multi-account sh -c "python3 /root/ai-accounts/.Codex/shared/skills/cyolo/scripts/cyolo.py ask cyolo1 'ตอบ OK' --difficulty 1"
docker exec multi-account sh -c "python3 /root/ai-accounts/.Codex/shared/skills/cyolo/scripts/cyolo.py image cyolo1 'วงกลมสีแดง 1 วงกลางพื้นขาว' /workspace/pic.png"
docker exec multi-account sh -c "python3 /root/ai-accounts/.Codex/shared/skills/cyolo/scripts/cyolo.py quota"
```

งานหลายบัญชี ใช้สกิล `agent-team`
