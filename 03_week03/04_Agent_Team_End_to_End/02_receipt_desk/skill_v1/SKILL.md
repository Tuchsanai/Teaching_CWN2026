---
name: agent-team-delivery
description: รับบันทึกการสัมภาษณ์ลูกค้า 1 ไฟล์ แล้วส่งมอบระบบ (เว็บ + AI บน GPU ที่เช่า) แบบครบวงจร 4 ระยะ — Requirement (User Story · Requirement · System Design · ข้อมูลทดสอบ) → Planning (แตกบล็อก DAG + Gantt ด้วย dag-planner + What-if ก่อนรันทีม) → Build · Train · Deploy (ทีม agent สร้างระบบด้วย dag-planner/agent-team · รันต่อเมื่อมีบล็อกไม่เสร็จ · เช่า GPU ด้วย vastai เทรนเทียบ 1 กับ N GPU · deploy · Capacity Test ตาม SLO และ Failure Test) → Verification (Test Charter · Exploration · Test Plan ตรวจไขว้ที่แยก Test Case ตัวอ่านจำลองออกจากโมเดลจริง · Playwright Test 2 ชุดเว็บ · Bug Hunt · รายงานส่งมอบ · ลบเครื่องและสรุปค่าใช้จ่าย) มีจุดหยุดถามคนก่อนรันทีมจริงและก่อนเช่าเครื่อง และกติกาเรื่องเงิน ใช้เมื่อผู้ใช้สั่ง "agent-team-delivery", "ทำระบบจากบันทึกสัมภาษณ์", "ส่งมอบงานด้วยทีม agent ตั้งแต่ requirement ถึงทดสอบ", "end-to-end delivery" · Deliver a web + GPU-AI system from one interview note through Requirement, Planning (with what-if), Build/Train/Deploy (resume, GPU-count training, SLO capacity test) and Verification (mock vs real-model test split) with dag-planner, agent-team and vastai.
---

# agent-team-delivery v1 — จากบันทึกสัมภาษณ์ถึงรายงานส่งมอบ

สกิลนี้เป็น "ผู้ควบคุมงาน" อยู่บน host (Claude Code ในโฟลเดอร์โปรเจกต์) งานหนักส่งต่อให้ 3 สกิลใน container `multi-account`:

| สกิล | ใช้ในระยะ | อ่านคำสั่งจริงก่อนใช้ |
|---|---|---|
| `dag-planner` | B แผน + What-if · C รันทีม · รายงานแผนเทียบจริง | `MSYS_NO_PATHCONV=1 docker exec multi-account cat /root/ai-accounts/.Claude/shared/skills/dag-planner/SKILL.md` |
| `agent-team` | C รันต่อบล็อกที่ไม่เสร็จ · เปลี่ยนขอบเขตตรวจ · D ผู้ตรวจไขว้ Test Plan | `.../skills/agent-team/SKILL.md` |
| `vastai` | C เช่า GPU · เทรน · deploy · Capacity Test · D ลบเครื่อง | `.../skills/vastai/SKILL.md` |

ห้ามเดาคำสั่ง ให้อ่าน SKILL.md ของสกิลนั้นทุกครั้งก่อนเรียก (คำสั่งจริงของรอบต้นแบบอยู่ใน [references/phases.md](references/phases.md) · กับดักที่เจออยู่ใน [references/lessons.md](references/lessons.md))

**ใหม่ใน v1** (จากรอบต้นแบบ ReceiptDesk 17 ขั้น): ① What-if ก่อนรันทีม (B2) · ② รันต่อเมื่อมีบล็อกไม่เสร็จ + เปลี่ยนขอบเขตตรวจโดยคน (C2–C3) · ③ เทรนเทียบจำนวน GPU (C5) · ④ Capacity Test ตาม SLO + Failure Test (C7) · ⑤ แยก Test Case ที่ต้องใช้ตัวอ่านจำลองออกจากข้อที่ใช้โมเดลจริง (D2–D3)

## ค่าที่ปรับได้ (ผู้ใช้บอกในพรอมต์ ถ้าไม่บอกใช้ค่าเริ่มต้น)

| ค่า | ค่าเริ่มต้น | หมายเหตุ |
|---|---|---|
| `interview` | `./INTERVIEW.md` | บันทึกการสัมภาษณ์ 1 ไฟล์ (input เดียวที่จำเป็น) |
| `plan_name` | ชื่อโฟลเดอร์ปัจจุบันแบบสั้น ตัวพิมพ์เล็ก | แผนอยู่ที่ `/workspace/plans/<plan_name>/` ห้ามแตะแผนชื่ออื่น |
| `accounts` | `yolo1,yolo2,yolo3,cyolo1` | ใช้เฉพาะบัญชีที่ผู้ใช้อนุญาต ส่งรายชื่อทุกคำสั่งที่รับได้ (`--accounts` / `--workers`) · ต้องมี Codex (cyolo) ≥ 1 · ห้าม `dagplan.py doctor` (แตะทุกบัญชี) |
| `max_agents` | `4` | agent พร้อมกันสูงสุด · debate / best_of ต้องใช้ 3 agent จึงต้อง ≥ 3 |
| `gpu` · `num_gpus` · `max_price` | `RTX_3090` · `2` (ในเครื่องเดียว) · `$0.60/ชม.` | เพดาน `dph_total` ของทั้งเครื่อง (รวมดิสก์) ห้ามเกิน |
| `budget_usd` | `$3.00` | เพดานค่าเช่ารวมทั้งงาน (รอบต้นแบบ $2.06 · เปิดเครื่อง 4 ชม. 48 นาที) |
| `label` | `e2e-<plan_name>` | ป้ายเครื่อง · แตะได้เฉพาะเครื่องป้ายนี้ |
| `epochs` | `1` | ค่าอื่นที่ใช้: Qwen/Qwen3-VL-2B-Instruct · LoRA r16 · Training 400 ใบ · seed 0 · global batch 16 |
| `web_port` · `mock_port` | `3420` · `web_port + 1` | เว็บโมเดลจริง · เว็บตัวอ่านจำลอง (`AI_MODE=mock`) แยก compose project และฐานข้อมูล |
| `stop_after` | `planning` | `requirement` · `planning` · `build` · `verification` — ค่าเริ่มต้นหยุดก่อนใช้โทเคนทีมและเงิน |
| `out` | `./results` | `answers/` · `model/` · `deploy/` · `capacity/` (เอกสาร `./docs` · แผน `./plan` · โค้ดทีม `./app` · ทดสอบ `./test` · ภาพ What-if `./plan/whatif`) |
| `gpu_receipt_cap` | `40` ต่อรอบทดสอบ · `120` ต่อขั้น | งบภาพจริงที่ส่งเข้า GPU ในระยะ D (subagent สำรวจตัวละ ≤ 10) |

ก่อนเริ่ม พิมพ์ตารางค่าที่จะใช้ 1 ครั้ง แล้วทำต่อ (ไม่ต้องรอตอบ ยกเว้นถึงจุดถามคน)

## จุดที่ต้องถามคนก่อนทำต่อ (Human Gate)

หยุดแล้วถามด้วยข้อความสั้นพร้อมตัวเลข · ไม่ได้คำตอบ "อนุมัติ" = ไม่ทำ · การอนุมัติในพรอมต์ (เช่น "ผมอนุมัติให้รันจริง") นับเป็นคำตอบของ gate นั้นเท่านั้น ไม่ข้ามไป gate อื่น

| Gate | เมื่อไร | สิ่งที่ต้องแสดงก่อนถาม |
|---|---|---|
| G0 ข้อสมมติของลูกค้า | จบระยะ A | จุดที่ลูกค้าขัดกัน + ทางที่เลือก + ตัวเลขที่ทีมตั้งเอง (ทำต่อได้ แต่ต้องรายงาน) |
| **G1 ก่อนรันทีมจริง** | หลัง `plan` และ What-if ก่อน `export`/`run` | ตาราง What-if 3 แผน · แผนที่แนะนำ · จำนวนบล็อก · Critical Path · เวลาแผน · โทเคนประมาณ · บัญชี |
| G1b ก่อนรันต่อ | มีบล็อก `bad_output` / `blocked` | บล็อกที่จะรันซ้ำ · ข้อที่ผู้ตรวจขอรอบล่าสุด · โทเคนที่ใช้ไปแล้ว |
| G1c เปลี่ยนขอบเขตตรวจ | บล็อก review ไม่ผ่านซ้ำเพราะผู้ตรวจพบกรณีขอบใหม่นอก Requirement ทุกรอบ | เกณฑ์ใหม่ที่เสนอ (ผูกกับข้อมูลทดสอบใน `docs`) · รายการที่จะย้ายไป FOLLOW-UPS — **คนตัดสิน สกิลห้ามลดเกณฑ์เอง** |
| **G2 ก่อนเช่าเครื่อง** | ก่อน `vastai create instance` | offer (GPU × จำนวน · `dph_total` · ประเทศ · reliability) · ชั่วโมงที่คาด · ค่าเช่าคาด ≤ `budget_usd` · ป้าย |
| G3 ก่อนใช้เงินเกินกรอบ | ค่าเช่าสะสมจะเกิน 80% ของ `budget_usd` · ต้องเช่าเพิ่ม · ภาพจริงจะเกิน `gpu_receipt_cap` | ยอดถึงตอนนี้ · สิ่งที่จะได้เพิ่ม |

## กติกาเรื่องเงิน (ห้ามละเว้น)

1. ก่อนเช่าและหลังลบ: `show instances --raw` เพื่อรู้ว่ามีเครื่องใดอยู่ · แตะได้เฉพาะเครื่องป้าย `label` · ทุกสคริปต์ตรวจป้ายก่อนทำ (`scripts/vast/cost_now.sh` ปฏิเสธถ้าป้ายไม่ตรง)
2. เช่าเฉพาะ offer ที่ `num_gpus` ตรง · `dph_total ≤ max_price` · verified · ติด `--label` ตั้งแต่ create (`scripts/vast/rent.sh`)
3. รอด้วย loop ที่มี timeout (`scripts/vast/poll_instance.sh`) · ค้าง `loading` เกิน 5 นาที หรือ running แต่ SSH เข้าไม่ได้เกิน 5 นาที → **ลบทันที** แล้วเลือก offer ใหม่ (ไม่เกิน 3 ครั้ง แล้วถามคน) · ค่าเช่าของเครื่องที่ลบไปต้องนับรวม
4. เทรน วัดผล และบริการบน GPU รันใน `tmux` มีไฟล์สถานะ (`scripts/train/pipeline.sh`) การเชื่อมต่อหลุดไม่ต้องเริ่มใหม่ ไม่เสียเงินซ้ำ · ใช้ GPU ทุกใบพร้อมกันเมื่อทำได้ (เช่น วัดผลก่อน/หลังเทรนคนละ GPU)
5. ทุกคำตอบที่เครื่องยังเปิด ต้องบอก "เครื่องยังเปิดอยู่" + ค่าเช่าถึงตอนนี้ (`scripts/vast/cost_now.sh`)
6. เงินต่อ Epoch รายงาน 2 แบบ: ตามส่วนของ GPU ที่ใช้ และตามราคาทั้งเครื่อง (เช่าทั้งเครื่องอยู่แล้ว)
7. **ขั้นสุดท้ายห้ามข้าม (แม้งานล้มกลางทาง หรือ `stop_after=build`)**: ดึง LoRA + ผลวัดกลับ ตรวจ sha256 → `destroy instance <id> -y` → list ซ้ำต้องเหลือป้ายนี้ 0 เครื่อง → ค่าเช่าจริงจาก `show invoices-v1 --charges` → หยุดเว็บทั้ง 2 ชุด (`docker compose stop`/`down` ไม่ใส่ `-v`)
8. key อ่านจาก `.env` ผ่าน `scripts/vast/vast.sh` เท่านั้น · ห้ามแสดงค่า key/token และห้ามพิมพ์ค่าใน `.env` แม้เป็นตัวแปรเปิดปิด (แสดงแค่ชื่อ + ความยาว) · ห้ามคัดลอก `.env` · key บนเครื่องเช่าเก็บเป็น `secrets.env` chmod 600 (`scripts/deploy/push_c.sh`)
9. โทเคนทีม: รายงานโทเคนต่อบล็อกจาก ledger และตรวจว่าผลรวมใน REPORT ตรงกับ ledger ทุกครั้ง · รันต่อเฉพาะบล็อกที่ไม่เสร็จ ห้ามรันบล็อกที่เสร็จแล้วซ้ำ ห้ามเริ่ม run ใหม่

## 4 ระยะ

แต่ละขั้นบันทึกคำตอบไว้ที่ `<out>/answers/NN_<ชื่อ>.md` (ภาษาไทย ปิดท้ายด้วยตารางสรุป + "เวลาที่ใช้: ~N นาที") · จบแต่ละระยะตรวจเกณฑ์ผ่าน ถ้าไม่ผ่านให้แก้ในระยะนั้นก่อน หรือรายงานตามจริงแล้วหยุด

### A · Requirement (ทำบน host ไม่ใช้โทเคนทีม ไม่เขียนโค้ด)

1. `docs/USER-STORIES.md` — "ในฐานะ… ฉันต้องการ… เพื่อ…" ครบทุกบทบาท · US-01… · Must/Should/Could · เกณฑ์ยอมรับ · อ้างคำพูดลูกค้าพร้อมเลขบรรทัด · ตารางจุดขัดกัน + คำถาม · หัวข้อ "นอกขอบเขต"
2. `docs/REQUIREMENTS.md` — FR (อ้าง US) · BR เป็นตัวเลขพร้อมค่า ต่ำกว่า/เท่ากับ/สูงกว่า เส้นแบ่ง · NFR ≥ 6: เกณฑ์โมเดล (แปลงคำลูกค้าเป็นตัวชี้วัดบน Test Set เช่น Accuracy · Silent Error · Flag Recall/Rate · Abstention · JSON Validity + จำนวนใบขั้นต่ำ) · SLO งานปกติและงานด่วน · ความจุช่วงพีค (อัตราต่อ Worker · เพดานคิว) · ข้อมูลห้ามหาย · ความเป็นส่วนตัว · **ความคุ้มของการเพิ่ม GPU (เช่น Speedup ≥ 1.6 เท่า)** · จุดขัดกันเลือกทางเสี่ยงน้อยสุดเป็น "ข้อสมมติ"
3. `docs/DESIGN.md` + `docs/TEST-DATA.md` — Mermaid 4 ภาพ · API Contract (ส่งงาน · สถานะ · งานด่วน · คิวเต็ม 429 + Retry-After · API key) · Priority Queue ที่งานปกติไม่ค้าง · Backpressure · Dead-letter Queue · ack หลังบันทึกผล (Worker ล่มงานไม่หาย) · `/api/health` · ทางรีเซ็ตข้อมูลทดสอบ (รับค่าคิวค้าง/โควตาได้) · `data-testid` · **`AI_MODE=mock` ตัวอ่านจำลองที่ให้ผลตามชื่อไฟล์** · `BUG_MODE=1` ทำ BR ผิด 3 ข้อ รายชื่ออยู่ที่ `docs/BUGS-SECRET.md` ไฟล์เดียว (เอกสารอื่นห้ามบอก)

**ผ่านเมื่อ:** ทุก US อ้างคำพูดลูกค้า · ทุก FR อ้าง US และทุก US ถูกอ้าง · ทุก BR มี 3 ค่าขอบ · เกณฑ์โมเดลและ SLO เป็นตัวเลขที่วัดได้ · ข้อมูลทดสอบคำนวณผลที่คาดหวังครบทุก BR · มี BUGS-SECRET.md · ตัวเลขที่ทีมตั้งเองถูกบันทึกเป็นข้อสมมติ → **G0** · `stop_after=requirement` จบตรงนี้

### B · Planning (dag-planner · ไม่รันจริง)

1. **แผนหลัก** — 12–14 บล็อก: บล็อกแรก = โครงโปรเจกต์ · บล็อกท้าย = รวมระบบ + ทดสอบ · ครอบคลุม DB+seed · กติกา BR + สิทธิ์ + API เว็บ · dispatcher + ตัวอ่านจำลอง · gateway · คิว (Priority/Backpressure/DLQ) · GPU Worker + NGINX · **โค้ด Training บน 1 และ N GPU + Evaluation** · หน้าเว็บ · โลโก้ (`image`) · ใช้ครบ 6 สกิล: บล็อกกติกา BR ใช้ `review` (ผู้ตรวจคนละ CLI · `max_rounds: 3`) · บล็อกออกแบบกติกาแซงคิวใช้ `debate` · หน้าจอตรวจแก้ใช้ `best_of` · ที่เหลือ `yolo`/`cyolo`/`image` · timeout S 900 / M 1800 / L 2700 วินาที · `done` ตรวจได้จริงและระบุไฟล์ประกอบทุกไฟล์ (ไม่ใช่แค่ไฟล์หลัก) · บล็อก review ระบุว่า "ผ่านเมื่อกรณีทดสอบ BR ทุกข้อใน `docs/TEST-DATA.md` ผ่าน" ตั้งแต่แผน
   คำสั่ง: `dag <plan> --blocks -` → `plan <plan> --max-agents <max_agents> --accounts <accounts>` → คัดลอก `blocks.json dag.png gantt-plan.png PLAN.md plan.json dag.json` มาที่ `./plan`
2. **What-if ก่อนรันทีม (ใหม่ใน v1)** — ใช้ `blocks.json` เดิม **ห้ามแก้บล็อก** (ตรวจ md5 ก่อน/หลัง) วางเพิ่ม 2 แผน: `<plan>-2` (`--max-agents 2`) และ `<plan>-nocodex` (เฉพาะบัญชี Claude) → เทียบ: เวลารวม · Critical Path · บัญชีที่งานหนักที่สุด · บล็อกที่วางไม่ได้หรือถูกลดคุณภาพ (และบล็อกที่ติดตามเป็นทอด) → แนะนำ 1 แผนพร้อมเหตุผล 2–3 บรรทัด → ภาพ Gantt + PLAN.md ของแผนใหม่ไว้ที่ `./plan/whatif/`
   แผนที่ "วางได้ไม่ครบ" ห้ามรายงานเวลารวมเหมือนแผนที่เสร็จ ให้เขียน "นับแค่ N บล็อก ยังไม่เสร็จ"

**ผ่านเมื่อ:** `dag` ไม่มี ERROR · วางได้ครบทุกบล็อกในแผนที่แนะนำ · ทุกบล็อกได้บัญชีในรายชื่อที่อนุญาต · agent พร้อมกัน ≤ `max_agents` · มี Critical Path และเวลารวม · มีตาราง What-if 3 แผน · `blocks.json` md5 ไม่เปลี่ยน → `stop_after=planning` จบตรงนี้ · ไม่งั้น **G1**

### C · Build · Train · Deploy

1. **ทีมสร้างระบบ** (หลัง G1): สร้างสำเนาทำงาน `/workspace/e2e_lab/<plan>` และคัดลอก `./docs` (ไม่รวม BUGS-SECRET เว้นแต่บล็อกต้องทำ BUG_MODE) ไปที่ `/workspace/plans/<plan>/app/docs/` → `export` → `run --detach` แล้ว poll ทุก ~2 นาที → `report` · คัดลอกไฟล์ทีมมาที่ `./app` (ไม่เอา node_modules/.next/__pycache__/weights/`.env*`) และ REPORT/gantt-actual/compare/run.json มาที่ `./plan` · **ห้ามเขียนโค้ดแทนทีม** · บล็อก `ok` ให้ตรวจไฟล์ตามเกณฑ์ done ทุกไฟล์ แล้วรายงานไฟล์ที่ขาด
2. **รันต่อเมื่อมีบล็อกไม่เสร็จ (ใหม่ใน v1 · G1b)**: `team.py run --resume <run_id>` ของ run เดิม (ห้ามเริ่ม run ใหม่) · รันเฉพาะ `bad_output`/`blocked` · บล็อก review ให้ผู้ทำแก้ **เฉพาะข้อที่ผู้ตรวจขอรอบล่าสุด** (ยกข้อความตรงตัวใส่ `--set <B>.prompt=...`) ไม่เขียนใหม่ทั้งบล็อก · run เดิมใช้รายชื่อบัญชีเดิม · ออก `report` ใหม่ทุกครั้งและรวมโทเคนทุกรอบ
3. **เปลี่ยนขอบเขตตรวจ (G1c)**: เมื่อคนตัดสินแล้ว ใช้ `--resume <run_id> --set <B>.criteria="ผ่านเมื่อกรณีทดสอบ BR ทุกข้อใน docs/TEST-DATA.md ผ่านครบ และไม่ขัดกับ Requirement" --set <B>.prompt=...` แก้เฉพาะ node นั้น ห้ามแตะเกณฑ์บล็อกอื่น · ข้อนอกขอบเขตจดที่ `./plan/FOLLOW-UPS.md` (ระดับ · ไฟล์ · ผู้ตรวจ · รอบ)
4. **เช่า + Dataset** (G2): เช่าตามกติกาเงิน · ดาวน์โหลดโมเดลและ Dataset ลงเครื่องเช่าใน tmux · นับจำนวนต่อชุดจากไฟล์จริง · ภาพตัวอย่าง 6 ใบคู่ JSON เฉลย · อธิบาย label และช่องที่ Requirement ใช้ตัดสิน · **แจ้งทันทีถ้า Test Set น้อยกว่าเกณฑ์ของ NFR หรือขาดช่องที่ FR ต้องการ หรือไม่มีตัวอย่าง "อ่านไม่ได้"**
5. **เทรนเทียบจำนวน GPU + Acceptance Gate (ใหม่ใน v1)**: ใช้โค้ดของทีม (แก้ให้น้อยที่สุดและจดว่าแก้อะไร) · เทรน 2 รอบค่าเดิมทุกอย่าง (`epochs` · seed · global batch เท่ากัน ปรับแค่ grad-accum): 1 GPU (`python`) กับ `num_gpus` GPU (`torchrun --nproc_per_node N`) (`scripts/train/run_train.sh`) · เวลาต่อ Epoch จาก `train_runtime` (ไม่รวมโหลดโมเดล) → Speedup · Efficiency = Speedup ÷ N · เงินต่อ Epoch 2 แบบ → ตัดสินความคุ้มตาม NFR · **ตรึง Threshold บน Validation ก่อนเปิด Test** · วัดก่อน/หลังเทรนบน Test Set ทุกตัวชี้วัด (`scripts/train/run_eval.sh`) · เก็บ LoRA ที่ดีที่สุดบนเครื่องและผลวัด/กราฟ/ตัวอย่างคำตอบที่ `<out>/model` (ไม่เอาน้ำหนักโมเดล)
6. **Deploy**: รวม LoRA เข้าโมเดล (`scripts/deploy/merge_lora.py`) · vLLM GPU ละ 1 ตัวหลัง NGINX `least_conn` · RabbitMQ · gateway · Worker N ตัว ทีละ tmux (`scripts/deploy/svc.sh` · `gpu.sh` · เครื่อง Vast ใช้ docker ไม่ได้) · API key ใหม่เก็บใน `.env` เท่านั้น · บนเครื่องนี้ `docker compose` ที่ `web_port` (`scripts/deploy/web.sh`) · ทดสอบทั้งเส้นทาง 5 ใบผ่านหน้าเว็บจริงถึงสถานะรอตรวจ และยอดใน DB = คำตอบ gateway (`compare_db_gateway.py`) · เวลาอ่านเฉลี่ยต่อใบ · จดการแก้ที่ `<out>/deploy/FIXES.md`
7. **Capacity Test ตาม SLO + Failure Test (ใหม่ใน v1)**: ตัวยิงโหลด `scripts/loadtest/loadgen.py` รันบนเครื่อง GPU ยิง gateway ที่ `127.0.0.1` ด้วยภาพจาก Test Set (คุมจาก host ด้วย `lt.sh push|run|log|pull`) · บีบภาพที่เกินเพดานขนาดไฟล์ก่อน · 5 การทดสอบ:
   - ความจุ: งานปกติ 100 ใบ Worker 1 ตัว แล้ว N ตัว → เวลาจนผลครบ เทียบ SLO + Speedup ของ Worker (วัด ≥ 2 รอบ รอบที่มีช่วงนิ่งผิดปกติให้วัดซ้ำ)
   - งานด่วน: ระหว่างงานปกติค้าง ส่งด่วน 10 ใบ → เวลาจนครบเทียบ SLO ด่วน + ลำดับการหยิบตามกติกาสลับ (เช่น `UUUUN`)
   - คิวเต็ม: ส่งเกินเพดาน → `429` + `Retry-After` ตาม DESIGN · งานด่วนยังรับ · ใบที่ถูกปฏิเสธไม่ถูกเก็บ · ใบที่รับไว้มีผลครบ
   - Worker ล่ม: 40 ใบ `kill -9` Worker 1 ตัวกลางงาน → ครบ 40 · หาย 0 · ซ้ำ 0 · เวลาที่ระบบเห็น · เปิดกลับ
   - ใบอ่านไม่ได้: ไฟล์เสีย 2 + ใบดี 20 → DLQ หลังลองครบ 3 ครั้ง · ไม่ขวางใบอื่น · ล้าง DLQ ของการทดสอบ
   ผลเป็น `summary.json` · `capacity.csv` · `raw/` · กราฟ 2 รูป (`plot.py`) ที่ `<out>/capacity` · จบแล้วคืนระบบสู่สภาพปกติ (Worker ครบ · คิวว่าง · เพดานเดิม)

**ผ่านเมื่อ:** ทุกบล็อกเสร็จ (review = APPROVED) · โทเคนใน REPORT ตรงกับ ledger · เครื่องมีป้ายถูกและราคา ≤ เพดาน · ตาราง 1 กับ N GPU มี Speedup/Efficiency/เงินต่อ Epoch · Acceptance Gate ตัดสินตามเกณฑ์จริงทุกตัวชี้วัด (Test Set ไม่ครบตาม NFR = "ผลเบื้องต้น" ห้ามเขียนว่าผ่าน) · E2E 5/5 ตรงกัน · Capacity Test ทุกข้อมีค่าที่วัดได้ · เกณฑ์ · ผ่าน/ไม่ผ่าน · ใบหาย 0 ผลซ้ำ 0 · ไม่มี key ใน log → `stop_after=build` ทำกติกาเงินข้อ 7 แล้วจบ

### D · Verification

1. **Charter + Exploration**: อ่าน `docs` + เดินเว็บ 1 รอบ (ห้ามเปิดโค้ดใน `./app` และห้ามเปิด BUGS-SECRET) → `test/CHARTERS.md` 6 ข้อ "สำรวจ… ด้วย… เพื่อหา…" ทุก BR มีเจ้าของ → รีเซ็ต 1 ครั้ง (ใส่คิวค้าง/โควตา/ใบค้างไว้ล่วงหน้าเพื่อไม่ต้องส่งใบเข้า GPU) → subagent 6 ตัวในข้อความเดียว (ไม่ใช้โหมดเบื้องหลัง) ตัวละ 1 session playwright-cli + บัญชีทดสอบของตัวเอง ≤ 10 นาที ≤ 10 ใบจริง → เขียนผลที่คาดหวังก่อนลอง → `test/exploration/` + `test/EXPLORATION.md` (ความเสี่ยง P1–P3) → ปิดทางรีเซ็ตกลับ
2. **Test Plan + ตรวจไขว้**: `test/TEST-PLAN.md` 8 หัวข้อ · 45–60 TC (TC-<กลุ่ม>-<เลข> กลุ่ม 5.1–5.8) ผลที่คาดหวังคำนวณจาก Requirement (ไม่ใช่จากหน้าเว็บ) · เรื่องที่ Requirement ไม่ชัดเป็นคำถามลูกค้า ไม่ใส่เป็นเฉลยเอง · **หัวข้อ 5.9 แยกสภาพแวดล้อมของทุก TC (ใหม่ใน v1):**
   - **M** ต้องกำหนดผลอ่านให้แน่นอน (เช่น ความมั่นใจ 0.89/0.90/0.91 · ผลต่าง 0.99/1.00/1.01 · อ่านล้ม 1/2/3 ครั้ง) → รันกับเว็บตัวอ่านจำลองที่ `mock_port`
   - **A** ไม่ขึ้นกับผลอ่าน (สิทธิ์ · รายงาน · โควตา) → รันที่ `mock_port` เพื่อไม่ใช้ GPU
   - **R** ต้องใช้โมเดลจริง → รันที่ `web_port` พร้อมงบภาพจริง (`gpu_receipt_cap`)
   - วิธี "พักการอ่าน" (หยุด dispatcher ของชุด mock) ให้ใบค้าง "รออ่าน" แบบทำซ้ำได้
   ให้ cyolo ผ่าน agent-team ตรวจ (ผู้ตรวจไม่ใช่ผู้เขียน · ส่งเฉพาะแผน + docs ไม่มี BUGS-SECRET): ตรวจได้จริงไหม ตัวเลขถูกไหม กำกวมไหม ซ้ำไหม → `test/PLAN-REVIEW.md` แก้ข้อรุนแรงสูงครบ (ลดขอบเขตได้ แต่ต้องย้ายไปหัวข้อ "นอกขอบเขต" อย่างเปิดเผย)
3. **Playwright Test 2 ชุดเว็บ**: เปิดชุดที่สองด้วย `scripts/test/mock.sh` (compose project แยก · DB แยก · env แยก · `AI_MODE=mock` · `mock_port`) · `test/e2e` 1 ไฟล์ต่อกลุ่ม (subagent ตัวละกลุ่มในข้อความเดียว ห้ามรันทั้งชุดระหว่างเขียน) · M/A → `mock_port` · R → `web_port` · Chromium 4 shard (ล็อกเว็บต่อข้อ · ตรวจว่าไม่มีชุดอื่นรันซ้อนก่อนสั่ง) · trace + screenshot ข้อที่ล้ม · แยกข้อล้ม เว็บผิด/แผนผิด/เทสต์ผิด แก้เฉพาะเทสต์ผิดแล้วรันซ้ำ **ห้ามแก้ผลที่คาดหวังให้ตรงกับเว็บ** → `test/TEST-REPORT.md` 6 ส่วน + `test/index.html` (`scripts/test/make_index.py`) → ตัดสินตาม Exit Criteria
4. **Bug Hunt**: เปิดเว็บทั้ง 2 ชุดด้วย `BUG_MODE=1` รันชุดเดิมไม่แก้เทสต์ → เทียบข้อที่ล้มเพิ่ม/อาการเปลี่ยน → จัดกลุ่มตามสาเหตุเป็นบั๊ก → `test/BUG-HUNT.md` (ขั้นตอนทำซ้ำ · ผลที่คาดหวัง · ผลจริง · หลักฐาน) → เขียนเสร็จแล้วจึงเปิด BUGS-SECRET เทียบจับได้กี่ตัว · คืนไฟล์รายงานรอบปกติ → `DELIVERY.md` (US → Requirement → TC → ผล · Acceptance Gate · Capacity เทียบ SLO · สิ่งที่ยังไม่ผ่าน/ยังไม่ทำ) → ปิด BUG_MODE ตรวจซ้ำทั้ง 2 ชุด
5. **ปิดงาน**: กติกาเงินข้อ 7 · ตารางค่าใช้จ่าย: เวลาเปิดเครื่อง · ค่าเช่ารวม (รวมเครื่องที่เช่าไม่สำเร็จ) · โทเคนรวมของทีม

**ผ่านเมื่อ:** ทุก BR มี Charter · ทุก FR มี TC และเส้นแบ่ง BR ครบ 3 จุด · **ทุก TC มีป้าย M/A/R และรันกับเว็บที่ถูกชุด** · ข้อสูงจากผู้ตรวจแก้ครบ · ภาพจริงไม่เกินงบ · ผลตัดสินส่งมอบตาม Exit Criteria (อัตราผ่านรวม · P1 · บั๊กด้านเงินเปิด = 0) · BUG_MODE จับได้กี่ตัวจาก 3 · BUG_MODE กลับเป็น 0 · เครื่องป้ายนี้เหลือ 0 · มีค่าเช่าจริงจาก invoice

## ข้อห้าม

- ห้ามอ่าน/แสดงข้อมูลล็อกอินของบัญชี · บัญชีไม่พร้อม → บอกผู้ใช้ให้ล็อกอินเอง · ห้ามเรียกบัญชีนอก `accounts`
- ห้ามสร้าง/หยุด/ลบ container `multi-account` หรือ volume · ห้ามแก้สกิลอื่นหรือแผนของโปรเจกต์อื่น
- ห้ามเปิด `docs/BUGS-SECRET.md` ระหว่างทดสอบ จนกว่ารายงานบั๊กจะเสร็จ
- ห้ามเขียนโค้ดแทนทีมในระยะ C ข้อ 1–3 · ข้อ 4–7 แก้ได้ "น้อยที่สุด" และต้องจดทุกจุด
- ห้ามลดเกณฑ์ตรวจหรือเกณฑ์ยอมรับเอง (ต้องผ่าน G1c หรือรายงานว่า "ไม่ผ่าน")
- ไม่ commit ถ้าผู้ใช้ไม่สั่ง

## ไฟล์ในสกิล

- [references/phases.md](references/phases.md) — คำสั่งจริงของแต่ละขั้น (เรียกจาก host) และตัวเลขอ้างอิงจากรอบต้นแบบ
- [references/lessons.md](references/lessons.md) — กับดักที่เจอจริงและวิธีเลี่ยง
- `scripts/` — สำเนาจากรอบต้นแบบ ใช้โดยคัดลอกโฟลเดอร์ย่อยไปไว้ในโปรเจกต์ (เช่น `./code_deploy/`, `./loadtest/`) เพราะสคริปต์อ้าง `./app` `./results` จากโฟลเดอร์แม่ · path/ป้าย/พอร์ตตั้งผ่าน env (`W` `R` `S` `LABEL` `STEP_DIR` `MODEL` `EPOCHS` `GW_URL` `WEB_PORT` `MOCK_PORT` `P` `STACK_DIR` `DATA_DIR`)
  - `vast/` vast.sh (เรียก vastai อ่าน key จาก .env ไม่แสดงค่า) · rent.sh · poll_instance.sh · remote.sh (SSH) · cost_now.sh
  - `train/` run_train.sh (1 หรือ N GPU ค่าเดียวกัน) · run_eval.sh (Validation/Test + sweep เส้นแบ่ง) · pipeline.sh (tmux: เทรน → วัดผล 2 GPU พร้อมกัน)
  - `deploy/` svc.sh (บน GPU: rabbitmq vllm0/1 nginx gateway worker0/1) · gpu.sh + push_c.sh (คุมจาก host · secrets.env) · web.sh (compose โมเดลจริง) · merge_lora.py · compare_db_gateway.py
  - `loadtest/` loadgen.py (capacity · urgent · queuefull · crash · dlq · state) · lt.sh · plot.py
  - `test/` mock.sh (เว็บชุดตัวอ่านจำลอง) · make_index.py (หน้า test/index.html)
