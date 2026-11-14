# ที่มาของสกิล evoskill

ที่มา: Huang, Nama, Alzubi, *EvoSkill v2: Fully Agentic Skill Evolution from Benchmark Adaptation to a Stateful Evolver* (arXiv:2610.25931) อ่านผ่านสรุปภาษาไทยของบทเรียน (`03_week03/07_EvoSkill_v2/01_theory/README.md`) และไฟล์รูปแบบ (`evoskill_format.md`) · prompt ทั้ง 3 ไฟล์เขียนใหม่ด้วยถ้อยคำของสกิลนี้

## วงรอบของ EvoSkill v2 ที่สกิลนี้ทำตาม

Agent 3 ตัว และสิ่งที่แต่ละตัวเห็น

| Agent | ทำอะไร เมื่อไร | เห็น | ไม่เห็น |
|---|---|---|---|
| Benchmark Adaptor | 1 เซสชัน ก่อนการรัน: เขียน plug-in (รายการโจทย์ + การแบ่งชุด) และเติม `reference/` | คำสั่งของผู้ใช้ · ข้อมูลทั้งหมด · การแบ่งชุด · ตัวตรวจ (อ่านได้ แก้ไม่มีผล) | ผลของ Solver (ยังไม่มี) |
| Solver | ทุก epoch: ทำโจทย์แต่ละข้อ N ครั้ง | ข้อความโจทย์ · ชุดสกิลของ epoch นั้นใน `./skills` | เฉลย · ตัวตรวจ · `evo/` |
| Evolver | 1 ตาต่อ epoch ในเซสชันเดียวตลอดการรัน: อ่านผลแล้วเขียนชุดสกิลถัดไป | trace · คะแนน (ตัวเลขอย่างเดียว) · โฟลเดอร์ทำงานของ Solver ของ **ชุด Training** ทุก epoch · ชุดสกิลของทุก epoch · `reference/` · บันทึกของตัวเอง | ทุกอย่างของ Validation และ Test · ตัวตรวจและผลรายข้อ · จำนวน epoch ทั้งหมด |

ลำดับของ 1 การรัน (E epochs · N ครั้งต่อโจทย์)

```text
init                         อ่านขนาดของการรันจากคำสั่งของผู้ใช้ · บันทึก hash ของสิ่งที่ส่งมา
adapt                        Benchmark Adaptor → plug-in + reference/ → ล็อก (freeze) → ตรวจการรั่ว
base                         epoch 0: Solver ทำ Training · Validation · Test โดยไม่มีสกิล
for K = 1 … E:
    turn                     ส่งผล Training ของ epoch K−1 เข้า evo/ → Evolver 1 ตา → skills_vK (รับเสมอ)
    rollout                  Solver ทำ Validation ด้วย skills_vK · และ Training ถ้า K < E
test                         Solver ทำ Test ด้วย skills_vE 1 ครั้ง
```

## ส่วนของสกิล | มาจากข้อไหนของเปเปอร์ | เหมือนหรือต่าง

| ส่วนของสกิล | มาจากข้อไหนของเปเปอร์ | เหมือนหรือต่าง |
|---|---|---|
| `init`: ขนาดของการรันอ่านจากคำสั่งของผู้ใช้ ไม่พบ = ไม่เริ่ม | Section 3 · คำสั่งของผู้ใช้ 5 หัวข้อ (Appendix) · ไม่มีการหยุดก่อนกำหนด | เหมือน |
| `adapt`: Agent แยกเซสชัน เขียน plug-in `list_tasks(root)` และ Reference Folder | Section 3 Benchmark Adaptor · Figure 1 แถบ BEFORE THE RUN | เหมือน |
| `plugin_api.py` (`class Task`) และ `plugin_skeleton.py` | plug-in API ของ source code | เหมือนในหน้าที่ · ฟิลด์ตามไฟล์รูปแบบของบทเรียน |
| การล็อกด้วย hash (`setup/freeze.json`) และตรวจ hash ก่อนทุก leg | Section 3: การแบ่งชุดและตัวตรวจถูกตรึงก่อนมีสกิลตัวแรก | เหมือน · เพิ่ม: ตรวจก่อน `turn` `audit` `eval` ด้วย |
| ตรวจ plug-in | เปเปอร์รัน plug-in ใน sandbox (`python -I -S`) | **ต่าง:** ตรวจรายการ import ด้วย `ast` แล้วรัน `list_tasks` ใน process แยก |
| ตรวจการแบ่งชุดของ plug-in กับ `split.json` ของผู้ใช้ | ข้อ "ผู้ถูกวัดต้องไม่เป็นผู้กำหนดการวัด" | เหมือนในหลักการ · เป็นการตรวจโดยโปรแกรม |
| ตรวจการรั่วใน `reference/` (`audit`) | Reference Folder ต้องไม่มีของ Validation · Test · ตัวตรวจ | **เพิ่มจากเปเปอร์:** เปเปอร์ฝากไว้กับ Adaptor · สกิลนี้ตรวจซ้ำด้วยโปรแกรม 4 กฎ |
| ผู้ใช้ให้ตัวตรวจ `grade(task, snapshot)` → 0 ถึง 1 | Section 3 · บทเรียนเรื่องช่องโหว่ของตัวตรวจ | เหมือนในสัญญา · **ต่าง:** คะแนนเป็นสัดส่วนของข้อตรวจ ไม่ใช่ผ่านหรือไม่ผ่าน |
| Solver = `skillopt.py run` ของบท 05 กับโฟลเดอร์ `legs/` | Solver คือ Claude Code ที่ใช้ system prompt เดิม | **ต่าง:** สกิลวางที่ `./skills/` และพรอมต์บอกให้อ่าน (ไม่ใช่ Progressive Disclosure) · ไม่มี container ต่อ rollout |
| N ครั้งต่อโจทย์ ทั้ง Training Validation Test | Design choice: หลายครั้งต่อโจทย์ (Table 2) | เหมือน |
| `turn`: Evolver เป็น Claude Code ที่มีเครื่องมือครบ ปิดเฉพาะ WebSearch และ WebFetch | Design choice: Evolver เป็น Agent ที่มี bash | เหมือน |
| เซสชันเดียว: `--session-id` ในตาแรก แล้ว `--resume` | Design choice: Stateful Evolver | เหมือน · `--fresh-session` เป็นการทดลองตัดส่วนประกอบของบทเรียน |
| `evo/` 7 โฟลเดอร์ (traces · scores · solver_workspaces · skills · reference · staging · evolver_workspace) | Table 1 | เหมือน (ชื่อเดียวกัน) |
| ส่งเฉพาะผลของ Training เข้า `evo/` · `scores` เป็นตัวเลขอย่างเดียว | Section 3: Evolver ได้เฉพาะของ Training และได้แต่คะแนน | เหมือน |
| คัดลอก `staging/` เป็น `skills_vK` โดยไม่มีเงื่อนไข · Test ใช้ `skills_vE` | Design choice: รับทุก epoch ทดสอบชุดสุดท้าย | เหมือน |
| Validation วัดทุก epoch แต่ไม่ใช้ตัดสิน และไม่ส่งให้ Evolver | Section 3 · ผลราย epoch (Figure 2–5) | เหมือน |
| `prompts/evolver_system.md` สั้น: บทบาท · เป้าหมาย · แผนที่ · ไม่บอกวิธีวิเคราะห์ | Appendix (EVOLVER_SYSTEM) | เหมือนในเนื้อหา · **ต่าง:** ภาษาไทย ถ้อยคำใหม่ + ให้เขียนสกิลเป็นภาษาไทย |
| `prompts/evolver_message.md` 1 ย่อหน้า: เวลา · เส้นตาย · หมายเลข epoch · ไม่บอกจำนวน epoch ทั้งหมด | Appendix (EPOCH_MESSAGE) | เหมือนในเนื้อหา · ถ้อยคำใหม่ |
| `prompts/adaptor.md` | Appendix (BA_GUIDANCE) | เหมือนในเนื้อหา · ถ้อยคำใหม่ |
| การแยกเครื่องด้วย `unshare -m` + bind mount + tmpfs บน `/workspace` | เปเปอร์: เครื่อง Daytona แยกกัน ปิดเครือข่ายเหลือ API ของโมเดล | **ต่าง:** container เดียว แยกด้วย mount namespace · ไม่ได้ปิดเครือข่าย |
| เวลาต่อตา 30 นาที (`--turn-minutes`) | เปเปอร์ 2 ชั่วโมง | **ต่าง** (งานเล็ก) |
| `status`: pass@1 pass@3 all@3 และต้นทุนของ Evolver ต่อ 1 จุดที่เพิ่ม | ผลการทดลองของเปเปอร์ (Held-out pass@1 pass@3 all@3 และต้นทุนของผู้ปรับสกิลต่อ 1 จุด) | เหมือนในตัววัด · รายงานต้นทุนของ Solver เพิ่ม (เปเปอร์ไม่รวม) |
| `noise`: โจทย์ที่ผ่านบางครั้ง และประตูรับแบบวัดครั้งเดียวจะตัดสินอย่างไร | Table 2 และเหตุผลของการไม่มีประตูรับ | **เพิ่มจากเปเปอร์:** เป็นคำสั่งที่จำลองจากผลจริงของการรัน |
| `turns/*/actions.md` และ `stats.json` | เปเปอร์รายงานจำนวนคำสั่ง bash · การรันสคริปต์เดิมซ้ำ · การย่อบริบท | เหมือนในตัววัด · เป็นไฟล์หลักฐานของบทเรียน |
| `eval` · `export` | ไม่มีในเปเปอร์ | **เพิ่ม:** ใช้ใน LAB (วัดชุดสกิลอื่น · เก็บผลลงเครื่อง) |
