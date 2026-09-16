# รายงานส่งมอบชุดสื่อ — 2026-09-12

สร้างไฟล์จริงทั้งหมดภายใต้ `/root/workspace/CWN/Teaching/Week1/005_LAB_AI_Work_Prompt_vs_Skill` ไม่มี commit/push ไม่แก้ข้อมูลบัญชีหรือ credential ไม่เรียก Claude/Qwen/subagent และไม่เปิด nested cyolo experiments ตามคำสั่ง task

## ไฟล์ที่ส่งมอบ

- [README ภาษาไทย](README.md), [ทฤษฎี/ศัพท์](theory.md), [เตรียมเครื่อง](setup.md), [บทพูดผู้สอน](instructor/slides.md): หลักสูตร1วัน 360นาทีเรียน+60นาทีพัก เตรียมเครื่อง30–60นาทีแยก
- [Lab1](labs/lab1/README.md), [Lab2](labs/lab2/README.md), [Lab3](labs/lab3/README.md): ข้อมูล A/B/C, Prompt เริ่ม/วิเคราะห์/แก้/ตรวจ, คำใบ้3ระดับ, ใบงาน, template, transfer และอภิปราย
- [เฉลย1](instructor/lab1-key.md), [เฉลย2](instructor/lab2-key.md), [เฉลย3](instructor/lab3-key.md) และร่างเต็มทุกเคส A/B/C: แยกจาก input, ติดป้าย constructed instructor examples ชัดเจน
- [Skill requirements-check](skills/requirements-check/SKILL.md), [shop-recovery](skills/shop-recovery/SKILL.md), [complaint-triage](skills/complaint-triage/SKILL.md): YAML name/description + คำแนะนำภาษาธรรมชาติ8ส่วน ไม่มี scripts; body ตรง canonical ทุกไบต์
- [Workshop](skill-workshop.md) และ [known-flaw demo](instructor/demo/known-flaw.md): ให้ AI เขียน/install/ปรับ Skill เป็นไฟล์จริงผ่าน Prompt, v1/v2 พร้อมใช้ กรณีบกพร่องสร้างขึ้นเพื่อสาธิต ไม่ใช่ผลที่แอบอ้างว่าเคยรัน
- [labctl](labctl), [คู่มือคำสั่ง](labs/lab2/commands.md), helper/test ใน instructor/runtime: ร้าน HTTP offline พร้อมคำสั่งทั้งหมดและการตรวจเบราว์เซอร์ด้วยคน
- [ทดลอง](experiments/README.md), input bundles ใน experiments/inputs, [ตัวเตรียม workspace](instructor/runtime/prepare_experiment.py), [scores.md](experiments/scores.md), [CSVว่าง](experiments/scores.csv), [summaryว่าง](experiments/summary.md)
- [Verification matrix](verification.md), [หลักฐานดิบ](evidence/README.md), [coverage](instructor/coverage.md), [progress](progress.md), [inventory](evidence/file-inventory.txt)

## การออกแบบสำคัญ

Lab1 มีข้อยืนยัน4 ขัดแย้ง3 ข้อมูลขาด3 และคำถาม/UATครบ ตัวหาร accuracy/completeness26; conflict/missingอย่างละ3 ไม่เลือกฉบับใหม่เอง ผล UAT ที่ยังไม่ตกลงคง pending; C มีมติเจ้าของที่ระบุสิทธิ์แทนข้อเก่าชัดเจน

Lab3 แต่ละชุดมี6เคสและ5ออเดอร์ ครอบคลุมวันที่7/8/10/2 ข้อมูลขาด เงินซ้ำ ชำรุด และยกเว้นฉุกเฉิน มีนโยบายลงวันที่ ผู้อนุมัติ วันรับเป็น0 และ tie-breakเวลา/รหัส ครบคำตอบอ้างอิงและร่างให้คนตรวจ C เปลี่ยนกำหนดเป็น5วันอย่างได้รับอนุมัติ ไม่มีการส่งจริงหรือคืนเงินจริง

DevOps มีสาเหตุเดียวต่อรอบ จับ A/B ภายใน basic และ rollback แยกกัน โปรแกรมครอง loopback port0 แล้วส่ง socket ที่เปิดอยู่ให้ process ลูก จึงไม่ใช้วิธีจองพอร์ตแล้วปล่อยก่อนเริ่ม แยก runtime ตามสำเนา/instance ตรวจเจ้าของ process ก่อนหยุด และ order smoke คำนวณยอดจาก catalog โดยไม่สร้างออเดอร์ถาวร

Fair test มี4 crossoverกลุ่ม P/S ได้ full body, refs, template และสิทธิ์เท่ากัน แยก session/workspaceไม่มีคำตอบเก่า มีงบเวลา/จำนวนแก้/คำใบ้และ controlled repeats คะแนนยังว่าง ไม่ตั้งข้อสรุปว่า Skill ดีกว่า แยกเวลาสร้าง/ดูแล/ใช้งานและ machine latency ออกจากเวลามือใหม่

## ตรวจแล้วเทียบกับยังรอ

**PASS จริง:** functional stopped→start→HTTPครบ, bad503→rollback→HTTPครบ, wrong fixยังเสีย, setup/resetทำซ้ำ, สอง instanceพร้อมกันคนละพอร์ตและหยุดไม่กระทบกัน, smokeไม่มีธุรกรรมถาวร, cleanup; ตรวจ Skillส่วนหัว/8ส่วน/body, local links, จำนวนข้อมูล, CSVว่าง และสร้าง experiment workspaceพร้อมรันร้านได้ ดู stdout พร้อมUTC/version/commands ใน evidence

**PENDING:** native discovery/loadจริงของสามSkill, model P/S runsผ่าน cyolo1, ให้ AI ทำ creation/maintenance prompts, browser UI manual, beginner pilot และเวลาสอนจริง ไม่อ้างว่าการอ่านไฟล์หรือ syntaxที่ตรวจจากbinaryเท่ากับ native invocationสำเร็จแล้ว

## คำสั่งแนะนำให้ parent ทดลองต่อ

จากรากแพ็กเกจ สร้างพื้นที่ข้อมูลเท่านั้น:

```bash
python3 instructor/runtime/prepare_experiment.py lab1 A P --label parent-lab1-A-P-r1
python3 instructor/runtime/prepare_experiment.py lab1 B S --label parent-lab1-B-S-r1
```

เปิด Terminal ใน WORKSPACE ที่คำสั่งพิมพ์ ทำ native discovery gate สำหรับ S ตาม experiments/README.md แล้วรัน (parent เป็นผู้รัน ภายในงบ300วินาที):

```bash
cyolo1 exec --skip-git-repo-check -m gpt-6-astra -c model_reasoning_effort=high --json -o answer.md - < prompt.txt > run.jsonl 2> run.stderr
```

stdinใช้ prompt.txt โดยตั้งใจและ help รุ่นติดตั้งรองรับ `-`; ไม่เปิด nested run ใน authoring นี้ ไม่ใช้ shell inline double quotesที่ขยาย `$skill-name` ตัวเตรียมรองรับ lab1 A/B/C, lab3 A/B/C, lab2 basic-A/basic-B/rollback-A/rollback-B/transfer-C และ arm P/S

สำหรับ Lab2 รัน `./labctl setup` ตามด้วยชื่อscenarioที่ตัวเตรียมพิมพ์ ก่อนจับเวลา; หลังงาน/timeout `./labctl stop` เสมอ ตรวจ JSONL turn.failed/คำตอบ/usage ไม่ใช้ exit0อย่างเดียว รันทุกกลุ่มและ repeatsตามคู่มือ ไม่เลือกเฉพาะคำตอบที่ดีที่สุด

## ข้อจำกัดที่ต้องคงไว้ในรายงานผล

runtimeตรวจบน Linux/Python3.12 ใช้ /proc/pidfd/flock ไม่ยืนยัน Windows/macOS; browserต้องอยู่เครื่องเดียวกับ loopbackหรือผู้สอนจัดการเข้าถึงล่วงหน้า โปรแกรมร้านofflineได้ แต่ AIต้องมีเครือข่าย/โควตา; cyolo1คือwrapperท้องถิ่น ไม่ใช่คำสั่งสากล และ workspace separationไม่ใช่OS sandbox ควรให้ parentตรวจtraceและขอบเขตเครื่องตามคู่มือก่อนนับผล งานนี้ไม่ครอบคลุม DevOps productionทั้งหมด

ไม่มี service ของการทดสอบตั้งใจปล่อยรันต่อ หลักฐานการตรวจท้ายอยู่ final-audit.txt ผลทดลองที่ยังรอไม่ใช่งาน authoring ที่อ้างว่าทำแล้ว
