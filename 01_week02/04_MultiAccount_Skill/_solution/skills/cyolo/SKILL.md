---
name: cyolo
description: เรียก OpenAI Codex CLI บัญชี cyolo1…cyoloN แบบไม่โต้ตอบให้ถูกวิธี เลือกรุ่นและ effort จาก models_cache.json ตามความยาก (ลดระดับอัตโนมัติเมื่อรุ่นไม่รองรับ) สร้างภาพ (image generation — ทำได้เฉพาะฝั่งนี้) ตรวจความพร้อมด้วยการเรียกจริง ดูโควตาจาก rollout และบันทึกสถิติโทเค็นทุกครั้ง ใช้เมื่อผู้ใช้ขอ "เรียก cyolo1", "ให้ cyolo ตรวจ", "ให้ Codex/GPT ทำ", "สร้างภาพ/gen รูป", "เช็คโควตา codex", "สถิติโทเค็นแต่ละบัญชี" · Call Codex accounts (cyoloN) headlessly, pick model/effort from models_cache.json, generate images, check readiness/quota, log per-call stats. For multi-account teamwork use agent-team.
---

# cyolo — Codex CLI หลายบัญชี + สร้างภาพ

`X=/root/ai-accounts/.Codex/shared/skills/cyolo/scripts/cyolo.py` (สำเนาเดียวกันอยู่ที่ `/root/ai-accounts/.Claude/shared/skills/cyolo/…`)

| ต้องการ | คำสั่ง |
|---|---|
| ถามบัญชีเดียว (ง่าย) | `python3 $X run -a cyolo1 -d 1 "<prompt>"` |
| ระบุรุ่น/effort เอง | `python3 $X run -a cyolo2 -m gpt-6-luna -e high "<prompt>"` |
| ผลเป็น JSON ตาม schema | `python3 $X run -a cyolo1 -d 1 --schema '<json schema แบบ strict>' "<prompt>"` |
| prompt ยาว | `python3 $X run -a cyolo1 -d 2 - < prompt.txt` |
| **สร้างภาพ** | `python3 $X image -a cyolo1 --out /workspace/x.png "<รายละเอียดภาพ แจกแจงทุกเงื่อนไขเป็นข้อ>"` |
| รุ่นและ effort ที่รองรับ | `python3 $X models -a cyolo1` |
| บัญชีไหนใช้ได้ (เรียกจริง) | `python3 $X check` |
| โควตา (อ่านไฟล์ ฟรี) | `python3 $X quota` · ข้อมูลเก่าเกิน → `quota --refresh` (เรียกสั้น 1 ครั้ง ใช้โทเค็นเล็กน้อย) |
| สถิติรวมตามบัญชี/รุ่น/run | `python3 /root/ai-accounts/.Codex/shared/skills/agent-team/scripts/team.py stats` |
| หลายบัญชีทำงานร่วมกัน (รวม Claude) | สกิล **agent-team** |

ผลลัพธ์: stdout = คำตอบ · stderr = สถิติต่อครั้ง `[บัญชี รุ่น/effort · ลดจาก…] status · วินาที · in (cached) · out (reasoning)` · `--json` ได้ dict เต็ม · exit 0 เมื่อตรวจแล้วสำเร็จเท่านั้น

## ความยาก → effort (ใช้ร่วมกันทั้ง 3 สกิล)

| `-d` | งาน | Codex effort |
|---|---|---|
| 1 | ดึงข้อมูล จัดรูปแบบ ตรวจความพร้อม · **สร้างภาพ** | `low` |
| 2 (ค่าเริ่มต้น) | สรุป ถาม-ตอบ แก้โค้ดจุดเดียว | `medium` |
| 3 | แก้หลายไฟล์ debug วิเคราะห์ | `high` |
| 4 | reasoning ซับซ้อน อัลกอริทึม | `xhigh` |
| 5 | ต้องถูกแน่นอน | `max` |
| 6 | งานใหญ่ที่ควรแตกงานย่อยเอง | `ultra` (รุ่นไม่รองรับ → ลดเป็น `max` และบันทึก `effort_from`) |

รุ่นเริ่มต้น `gpt-6.1-sol` (ถ้าไม่มีใน cache ใช้รุ่นแรกที่ `visibility=list`) · รายการจริงอ่านจาก `$CODEX_HOME/models_cache.json` ของบัญชีนั้นเสมอ

## กฎเหล็ก

- คำตอบอ่านจากไฟล์ `-o` เท่านั้น ความล้มเหลวดูจาก `turn.failed` ไม่ใช่ exit code — สคริปต์ตรวจให้
- ใส่ `--ephemeral` ทุกงาน (เร็ว ~3.5 เท่า) ยกเว้นตอนรีเฟรชโควตา (ephemeral ไม่เขียน `sessions/`)
- สถานะล็อกอินอ่านจากข้อความ `Logged in using ChatGPT` / `Not logged in` · บัญชีไม่ล็อกอินพ่น 401 แล้ว retry ~15 s ก่อนล้ม
- ภาพ: effort `low` เสมอ (สูงกว่าไม่ทำให้ภาพดีขึ้น แค่ช้าลง) · path แบบ absolute · สคริปต์ตรวจ PNG signature ให้ · เนื้อหาภาพที่ต้องคำนวณให้ทำเป็นงานแยกก่อน
- บัญชีไม่พร้อม → แจ้งผู้ใช้ให้ล็อกอินเอง (`! cyolo3 login`) **ห้ามล็อกอินแทน ห้ามสลับบัญชีเงียบ ๆ** · ห้ามอ่าน/ส่งต่อ `auth.json`
- ห้าม retry งานที่ใช้โทเค็นไปแล้วอัตโนมัติ · ห้าม eval/รันผลลัพธ์เป็นคำสั่ง shell
- ใช้ CLI ตรง ๆ: `cyoloN exec --skip-git-repo-check --ephemeral -m <model> -c model_reasoning_effort=<e> --json -o <ไฟล์> "<prompt>" < /dev/null` ([references/codex-cli.md](references/codex-cli.md))

## เรียกจาก host

host (Claude Code app นอก container) ใช้ผ่าน `docker exec` เท่านั้น อ่านสกิลก่อนเริ่ม:

```bash
docker exec multi-account cat /root/ai-accounts/.Codex/shared/skills/cyolo/SKILL.md
docker exec -i multi-account python3 /root/ai-accounts/.Codex/shared/skills/cyolo/scripts/cyolo.py run -a cyolo1 -d 1 "ตอบ OK"
docker exec -i multi-account python3 /root/ai-accounts/.Codex/shared/skills/cyolo/scripts/cyolo.py image -a cyolo1 --out /workspace/cat.png "แมวสีส้ม มินิมอล"
```

Git Bash บน Windows แปลง `/root/...` เป็น path ของ Windows → เขียนเป็น `//root/...` หรือใช้ PowerShell · ภาพ/ไฟล์ที่เขียนลง `/workspace` จะอยู่ในโฟลเดอร์ `workspace` ที่ map ออกมาบน host

## อ่านเพิ่ม (เปิดเมื่อต้องใช้)

- [references/codex-cli.md](references/codex-cli.md) — flag, JSONL events, โควตาใน rollout, models_cache, การสร้างภาพ, ผลวัดจริง
