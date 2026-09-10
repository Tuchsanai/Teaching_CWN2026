# Skill_LAB 006 · Fork and Model: รัน skill ในบริบทแยกด้วยโมเดลที่ถูกกว่า (★★★★)

## 1. วัตถุประสงค์

1. สร้าง skill `cheap-check` ที่รันใน **subagent แยก** (`context: fork`) ด้วย **โมเดลและ effort ที่กำหนดเอง** (`model: haiku`, `effort: low`) และรอผลในรอบเดียวกัน (`background: false`)
2. พิสูจน์จาก JSON ของ `-p` ว่าโมเดลที่ทำงานเปลี่ยนจริง (`modelUsage`) และต้นทุนต่อครั้งลดลงเท่าไร
3. พิสูจน์ว่า subagent **ไม่เห็นประวัติสนทนา** ของ session หลัก และเข้าใจว่าเมื่อไรควร/ไม่ควร fork

## 2. ข้อกำหนดเบื้องต้น

| รายการ | ข้อกำหนด |
|---|---|
| ต้องผ่านก่อน | Skill_LAB 001–005 และทฤษฎีหัวข้อ 10 |
| บัญชี | `yolo1` (LAB นี้เป็นเรื่องของ Claude Code เท่านั้น Codex ไม่มีฟิลด์เหล่านี้ ดูหัวข้อ 6) |
| โมเดลของ session หลัก | Opus · high (ค่าเริ่มต้น) — skill จะสลับไป haiku · low เอง |
| เวลา | 40 นาที |

## 3. ความรู้พื้นฐาน

| ฟิลด์ | ผล |
|---|---|
| `context: fork` | body ของ skill กลายเป็นพรอมต์งานของ subagent ที่มีบริบทใหม่ (ไม่มีประวัติสนทนา) ผลสรุปของ subagent ถูกส่งกลับเข้าบริบทหลัก |
| `agent: general-purpose` | ชนิดของ subagent (`Explore` = อ่านอย่างเดียว, `Plan`, หรือ agent ที่กำหนดเองใน `.claude/agents/`) |
| `model: haiku`, `effort: low` | subagent ใช้โมเดล/effort นี้แทนของ session หลัก |
| `background: false` | รอผลในรอบเดียวกัน (ค่าเริ่มต้น `true` = รันเบื้องหลัง แต่ในโหมด `-p` จะรอเสมอ) |

body ของ skill แบบ fork ต้องเป็น **คำสั่งงานที่ทำได้จริง** เพราะไม่มีใครมาอธิบายเพิ่ม ใน LAB นี้ให้ subagent ตรวจคำตอบเลขคณิตโดยบังคับใช้ `python3 -c` (ห้ามคิดในหัว) ซึ่งเป็นงานที่โมเดลเล็กทำได้ดีและถูกกว่า

## 4. ขั้นตอนการทดลอง

### ขั้นที่ 1 · สร้าง skill แบบ fork (~5 นาที)

```bash
BASE_PATH="$HOME/ai-accounts"
mkdir -p "$BASE_PATH/.Claude/shared/skills/cheap-check"
cat > "$BASE_PATH/.Claude/shared/skills/cheap-check/SKILL.md" <<'EOF'
---
name: cheap-check
description: ตรวจคำตอบเลขคณิตหรือยอดจ่ายด้วยโมเดลราคาถูก (haiku, effort ต่ำ) ในบริบทแยก ใช้เมื่อผู้ใช้ขอ "ตรวจแบบประหยัด" หรือ "ให้ haiku ตรวจ" หรือพิมพ์ /cheap-check ตามด้วยโจทย์และคำตอบ
context: fork
agent: general-purpose
model: haiku
effort: low
background: false
---

ตรวจโจทย์และคำตอบต่อไปนี้: $ARGUMENTS

1. คำนวณค่าที่ถูกต้องด้วยคำสั่ง `python3 -c` ผ่านเครื่องมือ Bash ห้ามคิดในหัว
2. ตอบบรรทัดเดียว: `ถูก` หรือ `ผิด` ตามด้วยค่าที่ถูกต้อง
3. ถ้าในบทสนทนาก่อนหน้ามีข้อมูลที่ผู้ใช้บอกให้จำ ให้ระบุด้วยว่าคุณเห็นข้อมูลนั้นหรือไม่
EOF
```

ข้อ 3 ใน body ใส่ไว้เพื่อการทดลองขั้นที่ 3 (ทดสอบว่า subagent เห็นประวัติหรือไม่)

### ขั้นที่ 2 · วัดโมเดลและต้นทุน (~10 นาที)

รัน 2 ครั้งด้วย `--output-format json` เพื่ออ่าน `modelUsage` และ `total_cost_usd`

```bash
yolo1 -p --output-format json '/cheap-check โจทย์: ซื้อของ 1500 บาท ลด 10% เมื่อครบ 1000 คำตอบที่ได้มา: 1350 บาท' \
  | python3 -c "import json,sys;d=json.load(sys.stdin);print(d['result']);print({m:(v['outputTokens'],round(v['costUSD'],4)) for m,v in d['modelUsage'].items()});print('total',round(d['total_cost_usd'],4),'turns',d['num_turns'])"
```

จากนั้นทำ **ฉบับเทียบ** ที่ตัด 5 บรรทัด (`context`…`background`) ออกจาก frontmatter ([skills/cheap-check-nofork/SKILL.md](skills/cheap-check-nofork/SKILL.md)) แล้วรันคำสั่งเดิมอีก 2 ครั้ง

**ผลรันจริง** ([evidence/cheap-check-claude.summary.jsonl](evidence/cheap-check-claude.summary.jsonl), [evidence/cheap-check-nofork-claude.summary.jsonl](evidence/cheap-check-nofork-claude.summary.jsonl), รายละเอียด `modelUsage` ใน `*.json`):

| ฉบับ | ครั้ง | โมเดลที่ทำงาน (`modelUsage`) | สิ่งที่เกิดขึ้น | คำตอบ | เวลา | list price |
|---|---|---|---|---|---|---|
| fork + haiku/low | 1 | **haiku เท่านั้น** (output 818, thinking 617) | subagent รัน python แล้วตอบ; session หลัก 0 turn | ถูก 1350 | 12.7 s | **$0.023** |
| fork + haiku/low | 2 | haiku เท่านั้น (output 699) | เหมือนครั้งที่ 1 | ถูก 1350 | 13.0 s | **$0.011** |
| ไม่ fork | 1 | opus (output 220) | Opus รัน Bash เอง 1 ครั้ง | ถูก 1350 | 9.0 s | $0.088 |
| ไม่ fork | 2 | opus + haiku | Opus อ่าน description ว่า "ให้ haiku ตรวจ" จึง **สร้าง subagent haiku เอง** ด้วยเครื่องมือ Agent (`subagent_stats.spawned = 1`) แล้วตรวจซ้ำอีกรอบ | ถูก 1350 | 45.6 s | $0.134 |

อ่านผล:

- `context: fork` + `model: haiku` ทำให้ **Opus ไม่ถูกใช้เลย** (ไม่มี key `claude-opus-5` ใน `modelUsage`) ต้นทุนต่อครั้ง $0.011–0.023 เทียบกับ $0.088–0.134 เมื่อไม่ fork (ถูกลง 4–12 เท่า) เวลาใกล้เคียง
- `num_turns` ของ session หลักเป็น 0 เพราะงานทั้งหมดเกิดใน subagent ผลกลับมาเป็นข้อความสรุป
- ฉบับไม่ fork ครั้งที่ 2 แสดงอันตรายของ description ที่ "เล่า" ว่าจะใช้ haiku: Opus ตีความเป็นคำสั่งแล้วสร้าง subagent เอง เสียเวลา 5 เท่า วิธีที่ถูกคือประกาศใน frontmatter ให้ CLI จัดการ ไม่ใช่ให้โมเดลตัดสินใจ

### ขั้นที่ 3 · subagent ไม่เห็นประวัติสนทนา (~10 นาที)

สนทนา 2 รอบใน session เดียว (ใช้ `--continue` ต่อ session ล่าสุดในโฟลเดอร์นี้)

```bash
yolo1 -p 'จำไว้ว่ารหัสลับของฉันคือ 4321 ตอบแค่คำว่า รับทราบ'
yolo1 -p --continue '/cheap-check โจทย์: 12*12 คำตอบที่ได้มา: 144 และบอกด้วยว่ารหัสลับของฉันคืออะไร'
```

| ฉบับ | คำตอบรอบที่ 2 (ผลรันจริง) |
|---|---|
| fork | "ถูก (12 × 12 = 144 ถูกต้อง) — หมายเหตุ: **ไม่เห็นข้อมูลรหัสลับ**ที่ผู้ใช้ส่งมาก่อนหน้านี้ในบทสนทนา" |
| ไม่ fork | "ถูก — ค่าที่ถูกต้องคือ 144 (**รหัสลับที่คุณให้จำไว้คือ 4321** ครับ เห็นข้อมูลนั้นอยู่)" |

หลักฐาน: [evidence/cheap-check-C2-claude.transcript.txt](evidence/cheap-check-C2-claude.transcript.txt), [evidence/cheap-check-nofork-C2-claude.transcript.txt](evidence/cheap-check-nofork-C2-claude.transcript.txt)

subagent ที่ fork มีบริบทใหม่ล้วน ๆ จึงเหมาะกับงานที่ "ให้ข้อมูลครบใน `$ARGUMENTS`" และไม่เหมาะกับงานที่ต้องอ้างสิ่งที่คุยกันไว้ก่อน

ข้อสังเกตข้างเคียงจาก log ฉบับไม่ fork: เมื่อบอกว่า "จำไว้ว่า…" Opus เขียนไฟล์ memory ของโปรเจกต์ (`projects/<cwd>/memory/secret-code.md`) ให้เองด้วย นี่คือกลไก memory ของ Claude Code ที่แยกจาก skill และเป็นอีกเหตุผลที่ไม่ควรพิมพ์ความลับจริงลงในบทสนทนา

### ขั้นที่ 4 · เมื่อไรควร fork (สรุปจากผล)

| สถานการณ์ | fork? | เหตุผล |
|---|---|---|
| งานตรวจ/คำนวณ/ค้นไฟล์ที่ข้อมูลครบใน argument | ✅ | ถูกกว่า ไม่ทำบริบทหลักบวม |
| งานที่ต้องอ้างบทสนทนาก่อนหน้า | ❌ | subagent ไม่เห็น |
| skill ที่เป็น "แนวทาง" ไม่ใช่ "คำสั่งงาน" | ❌ | subagent จะกลับมาโดยไม่มีผลลัพธ์ที่ใช้ได้ |
| อยากใช้โมเดลถูกแต่ยังต้องการบริบทหลัก | ใช้ `model:` โดยไม่ใส่ `context: fork` | เปลี่ยนโมเดลเฉพาะรอบนั้น (ยังไม่ได้ทดลองใน LAB นี้ — แนวทาง) |

## 5. ผลการทดลองเปรียบเทียบ

| ตัวชี้วัด | fork + haiku/low (2 ครั้ง) | ไม่ fork (2 ครั้ง) |
|---|---|---|
| โมเดลที่ทำงาน | haiku 2/2 | opus 2/2 (+haiku 1 ครั้งที่ Opus สร้างเอง) |
| list price ต่อครั้ง | $0.011 / $0.023 | $0.088 / $0.134 |
| เวลา | 12.7 / 13.0 s | 9.0 / 45.6 s |
| คำตอบถูก | 2/2 | 2/2 |
| เห็นประวัติสนทนา | ไม่เห็น | เห็น |

## 6. ฝั่ง Codex

Codex ไม่มี `context`, `model`, `effort` ใน frontmatter ทางเลือกคือให้ skill สั่งเรียก Codex อีกโปรเซสด้วยโมเดลถูก เช่น `cyolo1 exec -m gpt-5.4-mini -c model_reasoning_effort=low -o out.txt "<โจทย์>"` แล้วอ่านผลจากไฟล์ (แนวเดียวกับ skill `cyolo` ใน LAB 004) หรือใช้ sub-agent ของ Codex เมื่อ skill ระบุให้ทำ **แนวทาง — ยังไม่ได้ทดลองใน LAB นี้** และจะใช้จริงใน Skill_LAB 007

## 7. สรุป

1. `context: fork` + `model`/`effort` ใน frontmatter คือวิธีสลับโมเดลเฉพาะงานที่ CLI รับประกัน (เห็นได้จาก `modelUsage`) ต่างจากการเขียนใน description ซึ่งโมเดลอาจตีความไปเอง
2. ต้นทุนลดลง 4–12 เท่าในงานตรวจง่าย ๆ โดยความถูกต้องเท่าเดิม
3. subagent ไม่เห็นประวัติสนทนา จึงต้องส่งข้อมูลครบใน `$ARGUMENTS` และ body ต้องเป็นคำสั่งงานที่ทำได้เอง
4. ใช้ `--output-format json` แล้วดู `modelUsage`, `total_cost_usd`, `subagent_stats` เป็นหลักฐาน อย่าเชื่อคำตอบว่า "ใช้ haiku แล้ว"

## 8. หมายเหตุวิธีการทดลอง

รันด้วย [evidence/lab006-driver.sh](evidence/lab006-driver.sh) ในคอนเทนเนอร์เดียวกับ Skill_LAB 001 (Claude Code 2.1.267) session หลัก `yolo1` = Opus · high ทุกครั้ง list price คือ `total_cost_usd` ที่ CLI รายงาน ไม่ใช่ยอดที่บัญชี subscription ถูกเรียกเก็บ log ทั้งหมดใน `evidence/` (ไฟล์ `*-C2-*.session.jsonl` คือ session ที่ต่อด้วย `--continue`)
