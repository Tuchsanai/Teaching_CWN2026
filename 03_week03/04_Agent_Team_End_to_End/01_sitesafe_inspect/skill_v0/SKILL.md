---
name: agent-team-delivery
description: รับบันทึกการสัมภาษณ์ลูกค้า 1 ไฟล์ แล้วส่งมอบระบบ (เว็บ + AI บน GPU ที่เช่า) แบบครบวงจร 4 ระยะ — Requirement (User Story · Requirement · System Design · ข้อมูลทดสอบ) → Planning (แตกบล็อก DAG + Gantt ด้วย dag-planner) → Build · Train · Deploy (ทีม agent สร้างระบบด้วย dag-planner/agent-team · เช่า GPU เทรนและ deploy ด้วย vastai) → Verification (Test Charter · Exploration · Test Plan ตรวจไขว้ · Playwright Test · Bug Hunt · รายงานส่งมอบ · ลบเครื่องและสรุปค่าใช้จ่าย) มีจุดหยุดถามคนก่อนรันทีมจริงและก่อนเช่าเครื่อง และกติกาเรื่องเงิน ใช้เมื่อผู้ใช้สั่ง "agent-team-delivery", "ทำระบบจากบันทึกสัมภาษณ์", "ส่งมอบงานด้วยทีม agent ตั้งแต่ requirement ถึงทดสอบ", "end-to-end delivery" · Deliver a web + GPU-AI system from one interview note through Requirement, Planning, Build/Train/Deploy and Verification with dag-planner, agent-team and vastai.
---

# agent-team-delivery — จากบันทึกสัมภาษณ์ถึงรายงานส่งมอบ

สกิลนี้เป็น "ผู้ควบคุมงาน" อยู่บน host (Claude Code ในโฟลเดอร์โปรเจกต์) งานหนักส่งต่อให้ 3 สกิลใน container `multi-account`:

| สกิล | ใช้ในระยะ | อ่านคำสั่งจริงก่อนใช้ |
|---|---|---|
| `dag-planner` | B แผน · C รันทีม · รายงานแผนเทียบจริง | `MSYS_NO_PATHCONV=1 docker exec multi-account cat /root/ai-accounts/.Claude/shared/skills/dag-planner/SKILL.md` |
| `agent-team` | C รันต่อบล็อกที่ล้ม · D ผู้ตรวจไขว้ Test Plan | `.../skills/agent-team/SKILL.md` |
| `vastai` | C เช่า GPU · เทรน · deploy · D ลบเครื่อง | `.../skills/vastai/SKILL.md` |

ห้ามเดาคำสั่ง ให้อ่าน SKILL.md ของสกิลนั้นทุกครั้งก่อนเรียก (ตัวอย่างคำสั่งจริงที่ใช้ในรอบต้นแบบอยู่ใน [references/phases.md](references/phases.md))

## ค่าที่ปรับได้ (ผู้ใช้บอกในพรอมต์ ถ้าไม่บอกใช้ค่าเริ่มต้น)

| ค่า | ค่าเริ่มต้น | หมายเหตุ |
|---|---|---|
| `interview` | `./INTERVIEW.md` | บันทึกการสัมภาษณ์ 1 ไฟล์ (input เดียวที่จำเป็น) |
| `plan_name` | ชื่อโฟลเดอร์ปัจจุบันแบบสั้น ตัวพิมพ์เล็ก | ชื่อแผนของ dag-planner (`/workspace/plans/<plan_name>/`) |
| `accounts` | `yolo2,yolo3,cyolo1` | ใช้เฉพาะบัญชีที่ผู้ใช้อนุญาต · ต้องมี Codex (cyolo) ≥ 1 เพราะบล็อก review ต้องให้ผู้ตรวจคนละ CLI |
| `max_agents` | `3` | agent พร้อมกันสูงสุด (`dagplan.py plan --max-agents`) |
| `gpu` · `max_price` | `RTX_3090` · `$0.30/ชม.` | เพดานราคาต่อชั่วโมงรวมดิสก์ (`dph_total`) ห้ามเกิน |
| `budget_usd` | `$2.00` | เพดานค่าเช่ารวมทั้งงาน (รอบต้นแบบใช้จริง $0.76 · 3 ชม. 25 นาที) |
| `label` | `e2e-<plan_name>` | ป้ายเครื่อง · แตะได้เฉพาะเครื่องป้ายนี้ |
| `epochs` | `30` (ภาพ 640 · seed 0 · YOLO11s) | |
| `web_port` | `3410` | เว็บ docker compose บนเครื่องนี้ |
| `stop_after` | `planning` | `requirement` · `planning` · `build` · `verification` — ค่าเริ่มต้นหยุดก่อนใช้โทเคนทีมและเงิน |
| `out` | `./results` | answers/ · model/ · deploy/ · ผลแต่ละขั้น (เอกสารอยู่ `./docs` แผนอยู่ `./plan` ทดสอบอยู่ `./test`) |
| `gpu_photo_cap` | `80` รูปต่อรอบทดสอบ | งบรูปจริงที่ส่งเข้า GPU ในระยะ D |

ก่อนเริ่ม พิมพ์ตารางค่าที่จะใช้ 1 ครั้ง แล้วทำต่อ (ไม่ต้องรอตอบ ยกเว้นถึงจุดถามคน)

## จุดที่ต้องถามคนก่อนทำต่อ (Human Gate)

หยุดแล้วถามด้วยข้อความสั้นพร้อมตัวเลข · ไม่ได้คำตอบ "อนุมัติ" = ไม่ทำ · การอนุมัติในพรอมต์ของผู้ใช้ (เช่น "ผมอนุมัติให้รันจริง") นับเป็นคำตอบของ gate นั้นเท่านั้น ไม่ข้ามไป gate อื่น

| Gate | เมื่อไร | สิ่งที่ต้องแสดงก่อนถาม |
|---|---|---|
| **G1 ก่อนรันทีมจริง** | หลัง `dagplan.py plan` ก่อน `export`/`run` | จำนวนบล็อก · Critical Path · เวลาแผน · โทเคนประมาณ (S 0.6 / M 1.5 / L 3 ล้าน) · บัญชีที่จะใช้ · บล็อก review |
| G1b ก่อนรันต่อ | มีบล็อก `bad_output`/`blocked` | บล็อกที่จะรันซ้ำ · ข้อที่ผู้ตรวจขอ · รอบตรวจใหม่ |
| **G2 ก่อนเช่าเครื่อง** | ก่อน `vastai create instance` | offer ที่เลือก (GPU · `dph_total` · ประเทศ · reliability) · ชั่วโมงที่คาด · ค่าเช่าคาด ≤ `budget_usd` · ป้าย |
| G3 ก่อนใช้เงินเกินกรอบ | ค่าเช่าสะสมจะเกิน 80% ของ `budget_usd` · ต้องเช่าเพิ่ม · รอบทดสอบ B (เกิน `gpu_photo_cap`) | ยอดถึงตอนนี้ · สิ่งที่จะได้เพิ่ม |
| G4 ข้อสมมติของลูกค้า | จบระยะ A | จุดที่ลูกค้าขัดกัน + ทางที่เลือก (ทำต่อด้วยข้อสมมติได้ แต่ต้องรายงาน) |

## กติกาเรื่องเงิน (ห้ามละเว้น)

1. ก่อนเช่าและหลังลบ: `vastai show instances --raw` เพื่อรู้ว่ามีเครื่องใดอยู่ · แตะได้เฉพาะเครื่องป้าย `label` ห้ามลบ/หยุดเครื่องป้ายอื่น
2. เช่าเฉพาะ offer ที่ `dph_total ≤ max_price` · on-demand · 1 ใบ · ติด `--label` ตั้งแต่ create
3. รอสถานะด้วย loop ที่มี timeout (`scripts/poll_instance.sh`) — ค้าง `created`/`loading` เกิน 5 นาที หรือเป็น `exited/offline` → ลบทันทีแล้วเลือก offer ใหม่ (ไม่เกิน 3 ครั้ง แล้วถามคน)
4. เทรนและบริการบน GPU รันใน `tmux` แบ่งขั้นมีไฟล์สถานะ (`scripts/run_pipeline.sh`) การเชื่อมต่อหลุดไม่ต้องเริ่มใหม่ ไม่เสียเงินซ้ำ
5. ทุกคำตอบที่เครื่องยังเปิด ต้องบอก "เครื่องยังเปิดอยู่" + ค่าเช่าถึงตอนนี้ (ชม. × `dph_total`)
6. **ขั้นสุดท้ายห้ามข้าม (แม้งานล้มกลางทาง หรือ `stop_after=build`)**: ดึงน้ำหนักโมเดล + ผลวัดกลับ ตรวจ sha256 → `vastai destroy instance <id> -y` → list ซ้ำต้องเหลือป้ายนี้ 0 เครื่อง → ค่าเช่าจริงจาก `vastai show invoices-v1 --charges`
7. key อ่านจาก `.env` ผ่าน `scripts/vast.sh` เท่านั้น ห้ามแสดงค่า key/token ห้ามคัดลอก `.env` ห้ามทิ้ง key บนเครื่องเช่า (ส่งเป็นไฟล์ชั่วคราวแล้วลบทันที)
8. โทเคนทีม: รายงานโทเคนรวมต่อบล็อกจาก ledger ทุกครั้ง · รันต่อเฉพาะบล็อกที่ไม่เสร็จ ห้ามรันบล็อกที่เสร็จแล้วซ้ำ

## 4 ระยะ

แต่ละขั้นบันทึกคำตอบไว้ที่ `<out>/answers/NN_<ชื่อ>.md` (ภาษาไทย ปิดท้ายด้วยตารางสรุป + "เวลาที่ใช้: ~N นาที") · จบแต่ละระยะตรวจเกณฑ์ผ่าน ถ้าไม่ผ่านให้แก้ในระยะนั้นก่อน หรือรายงานตามจริงแล้วหยุด

### A · Requirement (ทำบน host ไม่ใช้โทเคนทีม ไม่เขียนโค้ด)

1. `docs/USER-STORIES.md` — "ในฐานะ… ฉันต้องการ… เพื่อ…" ครบทุกบทบาท · US-01… · Must/Should/Could · เกณฑ์ยอมรับ · อ้างคำพูดลูกค้า · ตารางจุดขัดกัน + คำถาม · หัวข้อ "นอกขอบเขต"
2. `docs/REQUIREMENTS.md` — FR (อ้าง US) · BR เป็นตัวเลขพร้อมค่า ต่ำกว่า/เท่ากับ/สูงกว่า เส้นแบ่ง · NFR ≥ 5 (เกณฑ์โมเดล · SLO · ความจุ · ข้อมูลห้ามหาย · ความเป็นส่วนตัว) · จุดขัดกันเลือกทางเสี่ยงน้อยสุดเป็น "ข้อสมมติ"
3. `docs/DESIGN.md` + `docs/TEST-DATA.md` — Mermaid 4 ภาพ (Architecture · ER · Sequence · State) · API Contract (ส่งงาน · ถามสถานะ · คิวเต็ม 429 · API key) · คิวที่งานไม่หายเมื่อ Worker ล่ม · `/api/health` · ทางรีเซ็ตข้อมูลทดสอบ · `data-testid` · **`AI_MODE=mock` (mock-gateway ตัดสินตามชื่อไฟล์)** · `BUG_MODE=1` ทำ BR ผิด 3 ข้อ บันทึกรายชื่อไว้ที่ `docs/BUGS-SECRET.md` ไฟล์เดียว
**ผ่านเมื่อ:** ทุก US อ้างคำพูดลูกค้า · ทุก FR อ้าง US · ทุก BR มี 3 ค่าขอบ · เกณฑ์โมเดลวัดได้บน Test Set (เช่น Image-level Recall ≥ 0.80 + Precision ≥ 0.80 + จำนวนรูปขั้นต่ำ) · ข้อมูลทดสอบคำนวณผลที่คาดหวังครบทุก BR · มี BUGS-SECRET.md → **G4** รายงานข้อสมมติ

### B · Planning (dag-planner · ไม่รันจริง)

แตก 8–10 บล็อกตามกติกา dag-planner: บล็อกแรก = โครงโปรเจกต์ · บล็อกท้าย = รวม + ทดสอบ (`exclusive`) · ครอบคลุม DB+seed · gateway+คิว · GPU Worker · **โค้ด Training และ Evaluation (ต้องมีสคริปต์ train จริง)** · หน้าเว็บ · mock-gateway · โลโก้ (`image`) · บล็อกที่ผิดแล้วเสียหายที่สุด 1 บล็อกใช้ `review` (`max_rounds: 3`) · timeout S 900 / M 1800 / L 2700 วินาที · `done` ตรวจได้จริง (เช่น "เทสต์ผ่าน + build ผ่าน" ไม่ใช่แค่ "มีไฟล์")
คำสั่ง: `dag <plan> --blocks -` → `plan <plan> --max-agents <max_agents> --accounts <accounts>` แล้วคัดลอก `blocks.json dag.png gantt-plan.png PLAN.md plan.json` มาที่ `./plan`
**ผ่านเมื่อ:** `dag` ไม่มี ERROR · ทุกบล็อกได้บัญชีในรายชื่อที่อนุญาต · agent พร้อมกัน ≤ `max_agents` · มี Critical Path และเวลารวม · ไม่มีบล็อกเกิน L → `stop_after=planning` จบตรงนี้ · ไม่งั้น **G1**

### C · Build · Train · Deploy

1. **ทีมสร้างระบบ** (หลัง G1): คัดลอก `./docs` ไปที่ `/workspace/plans/<plan>/app/docs/` ก่อน → `export` → `run` → `report` · คัดลอกไฟล์ทีมมาที่ `./app` (ไม่เอา node_modules/.next/__pycache__/docs) และ REPORT/gantt-actual/compare มาที่ `./plan` · **ห้ามเขียนโค้ดแทนทีม** บล็อกล้มรายงานตามจริง
2. **รันต่อ** (G1b): `team.py run --resume <run_id>` เฉพาะบล็อกที่ไม่เสร็จ · บล็อก review ให้แก้เฉพาะข้อที่ผู้ตรวจขอรอบล่าสุด (แนบข้อความตรงตัว) + `max_rounds` 3 · run เดิมใช้รายชื่อบัญชีเดิม (บัญชีใหม่ไม่ถูกเรียก)
3. **เช่า + Dataset** (G2): เช่าตามกติกาเงิน · ดาวน์โหลด Dataset ลงเครื่องเช่า · นับภาพต่อชุดและกรอบต่อคลาส · ภาพตัวอย่าง 8 รูปพร้อมกรอบ · **ตรวจว่า Test Set มีรูปพอตามเงื่อนไขเกณฑ์โมเดลหรือไม่ แจ้งตั้งแต่ตอนนี้**
4. **เทรน + Acceptance Gate**: ใช้โค้ดของทีม แก้ให้น้อยที่สุดและจดว่าแก้อะไร · เลือก Threshold บน Validation แล้วล็อกก่อนวัด Test (`scripts/select_threshold.py`) · วัดก่อน/หลังเทรน · เก็บผลที่ `<out>/model`
5. **Deploy**: บน GPU เปิด RabbitMQ + gateway (HTTPS) + Worker ใน tmux (เครื่อง Vast เป็น container ใช้ docker ซ้อนไม่ได้) · API key ใหม่เก็บใน `.env` เท่านั้น · บนเครื่องนี้ `docker compose` ที่ `web_port` · ทดสอบเส้นทาง 5 รูป (ผลใน DB = ผลจาก gateway) · คิว 20 งานหยุด Worker กลางทางแล้วเปิดใหม่ · จดการแก้ที่ `<out>/deploy/FIXES.md`
**ผ่านเมื่อ:** 10/10 บล็อกเสร็จ (review = APPROVED) · โทเคนในรายงานตรงกับ ledger · เครื่องมีป้ายถูกและราคา ≤ เพดาน · Acceptance Gate ตัดสินตามเกณฑ์จริง (Test Set ไม่พอ = "ยังตัดสินไม่ได้" ห้ามเขียนว่าผ่าน) · E2E 5/5 ตรงกัน · คิว 20/20 ไม่หาย ไม่ซ้ำ · ไม่มี key ใน log

### D · Verification

1. **Charter + Exploration**: อ่าน `docs` + เดินเว็บ 1 รอบ (ห้ามเปิดโค้ดใน `./app` และห้ามเปิด BUGS-SECRET) → `test/CHARTERS.md` 4 ข้อ "สำรวจ… ด้วย… เพื่อหา…" ทุก BR มีเจ้าของ → รีเซ็ต 1 ครั้ง → subagent 4 ตัวในข้อความเดียว ตัวละ 1 session playwright-cli + บัญชีทดสอบของตัวเอง ≤ 10 นาที → `test/exploration/` + `test/EXPLORATION.md` (ความเสี่ยง P1–P3)
2. **Test Plan + ตรวจไขว้**: `test/TEST-PLAN.md` 8 หัวข้อ · 30–40 TC (TC-<กลุ่ม>-<เลข> กลุ่ม 5.1–5.5) ผลที่คาดหวังคำนวณจาก Requirement · ให้ cyolo ผ่าน agent-team ตรวจ (คนละผู้เขียน) → `test/PLAN-REVIEW.md` แก้ข้อรุนแรงสูงครบ
3. **Playwright Test**: `test/e2e` 1 ไฟล์ต่อกลุ่ม (subagent ตัวละกลุ่มในข้อความเดียว) → รัน Chromium 1 รอบ → แยกข้อล้ม เว็บผิด/แผนผิด/เทสต์ผิด แก้เฉพาะเทสต์ผิด **ห้ามแก้ผลที่คาดหวังให้ตรงกับเว็บ** → `test/TEST-REPORT.md` 6 ส่วน + `test/index.html` → ตัดสินตาม Exit Criteria
4. **Bug Hunt**: เปิดเว็บด้วย `BUG_MODE=1` รันชุดเดิม → `test/BUG-HUNT.md` → เขียนเสร็จแล้วจึงเปิด BUGS-SECRET เทียบจับได้กี่ตัว → `DELIVERY.md` (US → Requirement → TC → ผล + สิ่งที่ยังไม่ผ่าน) → ปิด BUG_MODE ตรวจซ้ำ
5. **ปิดงาน**: กติกาเงินข้อ 6 · หยุดเว็บด้วย `docker compose down` (ไม่ใส่ `-v`) · ตารางค่าใช้จ่าย: เวลาเปิดเครื่อง · ค่าเช่ารวม · โทเคนทีม
**ผ่านเมื่อ:** ทุก BR มี Charter · ทุก FR มี TC และเส้นแบ่ง BR ครบ 3 จุด · ข้อสูงจากผู้ตรวจแก้ครบ · ผลตัดสินส่งมอบตาม Exit Criteria (ตัวเลข P1 · อัตราผ่าน · บั๊ก P1 เปิด = 0) · BUG_MODE จับได้กี่ตัวจาก 3 · BUG_MODE กลับเป็น 0 · เครื่องป้ายนี้เหลือ 0 · มีค่าเช่าจริง

## ข้อห้าม

- ห้ามอ่าน/แสดงข้อมูลล็อกอินของบัญชี · บัญชีไม่พร้อม → บอกผู้ใช้ให้ล็อกอินเอง
- ห้ามสร้าง/หยุด/ลบ container `multi-account` หรือ volume · ห้ามแก้สกิลอื่น
- ห้ามเปิด `docs/BUGS-SECRET.md` ระหว่างทดสอบ จนกว่ารายงานบั๊กจะเสร็จ
- ห้ามเขียนโค้ดแทนทีมในระยะ C ข้อ 1–2 · ในข้อ 3–5 แก้ได้ "น้อยที่สุด" และต้องจดทุกจุด
- ไม่ commit ถ้าผู้ใช้ไม่สั่ง

## ไฟล์ในสกิล

- [references/phases.md](references/phases.md) — คำสั่งจริงของแต่ละขั้น (เรียกจาก host) และตัวเลขอ้างอิงจากรอบต้นแบบ
- [references/lessons.md](references/lessons.md) — กับดักที่เจอจริงและวิธีเลี่ยง
- `scripts/vast.sh` (เรียก vastai โดยอ่าน key จาก .env ไม่แสดงค่า) · `scripts/poll_instance.sh` (รอเครื่องพร้อมแบบมี timeout) · `scripts/train.py` (เทรน YOLO ต่อจาก last.pt ได้) · `scripts/select_threshold.py` (เลือก Threshold บน Validation ใช้ `evaluate.py` ของทีม) · `scripts/run_pipeline.sh` (ตัวอย่างไปป์ไลน์ 9 ขั้นใน tmux มีไฟล์สถานะ ต้องแก้ path ก่อนใช้)
