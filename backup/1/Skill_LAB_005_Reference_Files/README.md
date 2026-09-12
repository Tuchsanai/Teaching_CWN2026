# Skill_LAB 005 · Reference Files: โหลดทีละชั้นด้วย references/ (★★★)

## 1. วัตถุประสงค์

1. สร้าง skill `shop-rules` ที่ `SKILL.md` เป็น **ตัวชี้ทาง** และกฎจริงอยู่ใน `references/` 3 ไฟล์ (ราคา ค่าส่ง คืนสินค้า)
2. เห็นจาก log ว่า AI **อ่านเฉพาะไฟล์ที่ตรงคำถาม** ทั้งใน Claude Code และ Codex
3. วัดโทเคน เวลา และต้นทุนเทียบกับการยัดทุกอย่างในไฟล์เดียว ทั้งกรณี skill เล็กและ skill ใหญ่ เพื่อรู้ว่า **เมื่อไรควรแตกไฟล์**

## 2. ข้อกำหนดเบื้องต้น

| รายการ | ข้อกำหนด |
|---|---|
| ต้องผ่านก่อน | Skill_LAB 001–004 และทฤษฎีหัวข้อ 3 |
| บัญชี | `yolo1`, `cyolo1` |
| โมเดล | Claude = Opus · high, Codex = gpt-6-astra · medium |
| เวลา | 40 นาที |

## 3. ความรู้พื้นฐาน

progressive disclosure 3 ชั้น: (1) `description` ของทุก skill อยู่ในบริบทตลอด (2) body ของ `SKILL.md` โหลดเมื่อถูกเลือก (3) ไฟล์ใน `references/` โหลดเมื่อ body บอกให้อ่าน มาตรฐาน Agent Skills แนะนำ `SKILL.md` < 500 บรรทัด และอ้างอิงไฟล์ลึกชั้นเดียว

ทั้งสอง CLI **ไม่ได้โหลด references ให้เอง** — body ต้องเขียนว่า "คำถามแบบไหน อ่านไฟล์ไหน" แล้วโมเดลไปอ่านด้วยเครื่องมือ (Claude: Read/Bash, Codex: exec) ทุกการอ่านคือ 1 รอบเรียกเครื่องมือ ซึ่งมีต้นทุน LAB นี้จึงวัดทั้งสองด้าน

## 4. ขั้นตอนการทดลอง

### ขั้นที่ 1 · สร้าง skill แบบตัวชี้ทาง + 3 ไฟล์อ้างอิง (~10 นาที)

ไฟล์ทั้งหมดอยู่ใน [skills/shop-rules/](skills/shop-rules/) วางทั้งสองฝั่ง

```bash
BASE_PATH="$HOME/ai-accounts"
for ROOT in "$BASE_PATH/.Claude/shared/skills" "$BASE_PATH/.Codex/shared/skills"; do
  rm -rf "$ROOT/shop-rules"; cp -r skills/shop-rules "$ROOT/shop-rules"
done
find "$BASE_PATH/.Claude/shared/skills/shop-rules" -type f
```

`SKILL.md` (ตัวชี้ทาง 14 บรรทัด):

```markdown
---
name: shop-rules
description: ตอบคำถามเกี่ยวกับกฎของร้านค้า ได้แก่ ราคาและส่วนลด ค่าส่งสินค้า และการคืนสินค้า ใช้เมื่อผู้ใช้ถามว่าต้องจ่ายเท่าไร ค่าส่งเท่าไร ส่งฟรีไหม คืนของได้ไหม หรือถามเงื่อนไขของร้าน
---

# กฎของร้าน (ตัวชี้ทาง)

อ่านเฉพาะไฟล์ที่ตรงกับคำถาม ไม่ต้องอ่านทุกไฟล์

- ราคา ส่วนลด สมาชิก → อ่าน [references/pricing.md](references/pricing.md)
- ค่าส่ง ส่งฟรี ระยะเวลาส่ง → อ่าน [references/shipping.md](references/shipping.md)
- คืนสินค้า เปลี่ยนสินค้า คืนเงิน → อ่าน [references/returns.md](references/returns.md)

ตอบสั้น ๆ พร้อมอ้างชื่อไฟล์กฎที่ใช้ ไม่ต้องสร้างไฟล์หรือรันคำสั่ง
```

กฎในไฟล์อ้างอิง (ย่อ): `pricing.md` ลด 10% เมื่อครบ 1000 และสมาชิก Gold ลดเพิ่ม 5% จากยอดหลังลด · `shipping.md` ส่งฟรีเมื่อยอดหลังลดครบ 1500 ไม่งั้น 50 บาท EMS +30 · `returns.md` คืนได้ใน 7 วัน ไม่คืนค่าส่ง สินค้าป้ายแดงไม่รับคืน

### ขั้นที่ 2 · ถาม 3 คำถามที่ต้องใช้กฎคนละไฟล์ (~10 นาที)

| รหัส | คำถาม | ไฟล์ที่ควรอ่าน | เฉลย |
|---|---|---|---|
| Q1 | ซื้อของ 1200 บาท ส่งแบบธรรมดา ต้องจ่ายรวมค่าส่งเท่าไร | pricing + shipping | 1,080 + 50 = **1,130** |
| Q2 | คืนสินค้าได้ภายในกี่วัน มีเงื่อนไขอะไร | returns | 7 วัน |
| Q3 | สมาชิก Gold ซื้อของ 2000 บาท ต้องจ่ายค่าสินค้าเท่าไร | pricing | 1800 × 0.95 = **1,710** |

```bash
yolo1 -p 'ซื้อของ 1200 บาท ส่งแบบธรรมดา ต้องจ่ายรวมค่าส่งเท่าไร ตอบสั้น ๆ ไม่ต้องสร้างไฟล์'
cyolo1 exec --skip-git-repo-check 'ซื้อของ 1200 บาท ส่งแบบธรรมดา ต้องจ่ายรวมค่าส่งเท่าไร ตอบสั้น ๆ ไม่ต้องสร้างไฟล์'
```

**ผลรันจริง** (คำถามละ 2 ครั้งต่อ CLI [evidence/shop-rules-claude.summary.jsonl](evidence/shop-rules-claude.summary.jsonl), [evidence/shop-rules-codex.summary.jsonl](evidence/shop-rules-codex.summary.jsonl)):

| คำถาม | Claude: ไฟล์ที่อ่าน (ผ่าน Bash `cat`) | Claude: คำตอบ | Codex: คำสั่ง | Codex: คำตอบ |
|---|---|---|---|---|
| Q1 | `shipping.md` + `pricing.md` (ครั้ง 1) / `pricing.md` + `shipping.md` (ครั้ง 2) | 1,130.00 ✓ ×2 | `cat SKILL.md` → `cat pricing.md shipping.md` | 1,130.00 ✓ / **1,250** ✗ (ลืมหักส่วนลดก่อนคิดค่าส่ง) |
| Q2 | `returns.md` เท่านั้น | 7 วัน ✓ ×2 | `cat SKILL.md` → `cat returns.md` | 7 วัน ✓ ×2 |
| Q3 | `pricing.md` เท่านั้น | 1,710.00 ✓ ×2 | `cat SKILL.md` → `cat pricing.md` | 1,710.00 ✓ ×2 |

ทั้งสอง CLI อ่าน **เฉพาะไฟล์ที่ตัวชี้ทางบอก** ไม่มีครั้งไหนอ่านครบ 3 ไฟล์ ตัวอย่าง log ของ Claude ([evidence/shop-rules-Q1-claude-1.transcript.txt](evidence/shop-rules-Q1-claude-1.transcript.txt)):

```text
TOOL 1 Skill: {"skill": "shop-rules", "args": "ซื้อของ 1200 บาท ส่งแบบธรรมดา ต้องจ่ายรวมค่าส่งเท่าไร"}
TOOL 2 Bash: {"command": "cat .../shop-rules/references/shipping.md; echo \"-----\"; cat .../shop-rules/references/pricing.md"}
ASSISTANT: **รวม 1,130.00 บาท** - ยอด 1200 → ลด 10% = 1,080.00 บาท (pricing.md) - ยอดหลังลด 1,080 < 1,500 → ค่าส่งธรรมดา 50
```

### ขั้นที่ 3 · เทียบกับไฟล์เดียว (skill เล็ก) (~10 นาที)

รวมกฎทั้ง 3 หมวดไว้ใน `SKILL.md` เดียว ([skills/shop-rules-mono/SKILL.md](skills/shop-rules-mono/SKILL.md), 30 บรรทัด ไม่มี `references/`) แล้วถาม 3 คำถามเดิม

| ตัวชี้วัด (เฉลี่ยจาก 6 ครั้งต่อ CLI) | แยกไฟล์ (`references/`) | ไฟล์เดียว |
|---|---|---|
| Claude: turn / tool call | 4 turn (Skill + Bash) | 3 turn (Skill เท่านั้น) |
| Claude: เวลา | 9.4–11.7 s | 8.5–12.4 s |
| Claude: list price | $0.047–0.111 | $0.028–0.047 |
| Claude: cache read (opus) | 49.6k–56.4k โทเคน | 35.5k–37.5k โทเคน |
| Codex: คำสั่ง | 2 (`cat SKILL.md`, `cat <ref>`) | 1 (`cat SKILL.md`) |
| Codex: เวลา | 16.0–23.6 s | 12.1–18.2 s |
| Codex: input tokens | 46.7k–63.7k | 31.1k |
| คำตอบถูก | Claude 6/6 · Codex 5/6 | Claude 6/6 · Codex 6/6 |

**สำหรับ skill เล็ก (กฎรวมกัน ~1,000 ตัวอักษร) การแตกไฟล์แพงกว่าและช้ากว่า** เพราะการอ่านไฟล์ 1 รอบต้องส่งบริบททั้งหมดไปอีกครั้ง (cache read เพิ่ม ~15k โทเคนต่อรอบ) มากกว่าที่ประหยัดได้จากการไม่โหลดกฎอีก 2 หมวด (ไม่กี่ร้อยโทเคน) นี่ตรงกับคำแนะนำของ `skill-creator`: "A simple self-contained skill does not need a router or extra files"

### ขั้นที่ 4 · เมื่อไฟล์อ้างอิงใหญ่ (~10 นาที)

ขยายแต่ละหมวดให้มีกฎรายหมวด/รายเขตอีก 45 ข้อ (รวม ~17,000 ตัวอักษร; [skills/shop-rules-big/](skills/shop-rules-big/) แยกไฟล์ และ [skills/shop-rules-mono-big/SKILL.md](skills/shop-rules-mono-big/SKILL.md) ไฟล์เดียว 174 บรรทัด) แล้วถาม Q1 และ Q2 อย่างละ 2 ครั้งต่อ CLI

**ผลรันจริง** ([evidence/partB/](evidence/partB/)):

| ตัวชี้วัด | แยกไฟล์ (big) | ไฟล์เดียว (big) |
|---|---|---|
| Claude Q2 (ใช้หมวดเดียว: คืนสินค้า) — ไฟล์ที่อ่าน | `returns.md` เท่านั้น 2/2 | – |
| Claude Q2 — list price / เวลา | **$0.149 / $0.150** · 14.5–17.2 s (4 turn) | $0.190 / $0.191 · 16.0–16.1 s (3 turn) |
| Claude Q2 — โทเคนที่โหลดใหม่ (cache creation) | ~10.9k | ~15.9k |
| Claude Q1 (ใช้ 2 หมวด: ราคา + ค่าส่ง) — ไฟล์ที่อ่าน | `shipping.md` + `pricing.md` 2/2 | – |
| Claude Q1 — list price / เวลา | $0.166 / $0.236 · 10.7–17.7 s (5 turn) | **$0.183 / $0.187** · 8.5–10.6 s (3 turn) |
| Codex Q2 — คำสั่ง | `cat SKILL.md` → `cat returns.md` (2) | `cat SKILL.md` → `sed`/`rg` หาหมวดในไฟล์เดียวกัน (2) |
| Codex Q2 — input tokens / เวลา | 48.0k · 18.5–19.3 s | 50.6k · 18.1–20.1 s |
| Codex Q1 — input tokens / เวลา / ถูก | 48.1k–67.0k · 16.9–26.4 s · **1/2** (ครั้งหนึ่งตอบ 1,250 ลืมหักส่วนลด) | 49.3k · 17.5–17.9 s · 2/2 |
| คำตอบถูก (8 ครั้งต่อฝั่ง) | Claude 4/4 · Codex 3/4 | Claude 4/4 · Codex 4/4 |

เมื่อกฎรวม ~17,000 ตัวอักษร การแยกไฟล์เริ่มคุ้มสำหรับคำถามที่ใช้หมวดเดียว (Claude ถูกลง 22% เพราะโหลดเฉพาะ 1 ใน 3 ไฟล์) แต่ยังแพงกว่าเมื่อคำถามต้องใช้ 2 หมวด (ต้องอ่าน 2 รอบ) และฝั่ง Codex แทบไม่ต่างเพราะโทเคนส่วนใหญ่เป็น system prompt + เครื่องมือ (~30k) ไม่ใช่ตัวกฎ ที่น่าสังเกตคือ Codex กับไฟล์เดียวใหญ่ใช้ `sed`/`rg` ค้นหมวดที่ต้องการในไฟล์เองโดยไม่ต้องแยกไฟล์ให้

## 5. สรุป

1. `SKILL.md` แบบตัวชี้ทาง + `references/` ทำงานได้จริงทั้งสอง CLI: โมเดลอ่านเฉพาะไฟล์ที่ตัวชี้ทางบอก (log ยืนยัน)
2. การอ่านไฟล์มีต้นทุนคงที่ต่อรอบ (บริบททั้งหมดถูกส่งซ้ำ) skill เล็กจึง **ควรอยู่ไฟล์เดียว** แตกไฟล์เมื่อเนื้อหาแต่ละหมวดใหญ่พอที่จะคุ้มค่ารอบอ่าน และเมื่อคำถามส่วนใหญ่ใช้แค่หมวดเดียว
3. ตัวชี้ทางที่ดีบอก "คำถามแบบไหน → ไฟล์ไหน" ชัดเจน และเตือนว่า "ไม่ต้องอ่านทุกไฟล์"
4. การกระจายกฎหลายไฟล์เพิ่มโอกาสพลาดข้ามหมวด (Codex Q1 ลืมหักส่วนลดก่อนคิดค่าส่ง 1 ใน 2 ครั้ง) คำถามที่ต้องใช้กฎหลายหมวดควรเขียนลำดับการคิดไว้ในตัวชี้ทาง

## 6. หมายเหตุวิธีการทดลอง

รันด้วย [evidence/lab005-driver.sh](evidence/lab005-driver.sh) และ `lab005b-driver.sh` ในคอนเทนเนอร์เดียวกับ Skill_LAB 001 (Claude Code 2.1.267, codex-cli 0.154.0) ตัวเลขโทเคนของ Claude อ่านจาก `modelUsage["claude-opus-5"]` ใน `*.json` และของ Codex จาก `turn.completed.usage` ใน `*.jsonl` list price = `total_cost_usd` ที่ CLI รายงาน
