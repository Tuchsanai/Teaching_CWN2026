# การทดลอง Prompt กับ native Skill — คู่มือ parent/ผู้สอน

**สถานะเริ่มต้น: pending ทุกผลการทดลองโมเดล** ผู้เขียนสร้างสินทรัพย์และตรวจโปรแกรมเท่านั้น parent จะใช้ cyolo1 / gpt-6-astra / high รันจริงภายหลัง ห้ามนำตัวอย่างผู้สอนมาใส่ช่อง observed และห้ามเรียกซ้อนจากชุดเตรียมพื้นที่นี้

## สิ่งที่เปรียบเทียบและสิ่งที่ควบคุม

P = คำแนะนำเต็มใน Prompt; S = native Skill มี body เดียวกันทุกไบต์หลัง YAML frontmatter ไม่ใช่ Prompt สั้นเทียบกับ Skill ละเอียด Canonical คือ [lab1](../canonical/lab1.md), [lab2](../canonical/lab2.md), [lab3](../canonical/lab3.md) ต้นฉบับ Skill อยู่ [requirements-check](../skills/requirements-check/SKILL.md), [shop-recovery](../skills/shop-recovery/SKILL.md), [complaint-triage](../skills/complaint-triage/SKILL.md)

ใช้โมเดล/effort เดียวกัน เครื่องมือ/สิทธิ์เหมือนกัน และเอกสารอ้างอิงกับ template เหมือนกัน ตัวสร้างพื้นที่ใส่ canonical body เต็มใน prompt.txt ของ P; ของ S ติดตั้ง body เดียวกันใต้ `.agents/skills/ชื่อ/SKILL.md` แล้วเรียก `$ชื่อ` มี intake ขอบเขตเดียวกันทั้งสองแบบ ความต่างของ metadata/กลไกโหลดคือสิ่งที่ต้องบันทึก ไม่อ้างว่าจำนวน context tokens เท่ากันแบบสมบูรณ์

ข้อมูล A/B ของ Lab 1 มีจำนวนบรรทัด ประเด็นขัดแย้ง3 ขาด3 ยืนยัน4 เท่ากัน แต่ร้าน/อัตรา/ช่วงเวลาต่างกัน Lab3 มี6ประเภทเคสเท่ากัน วันผ่านไปเท่ากัน ข้อมูล B เป็นชุดใหม่ทั้งวันที่และID DevOps จับ basic-A ↔ basic-B และ rollback-A ↔ rollback-B **ห้ามจับ basic เทียบ rollback แล้วเรียกว่าเทียบเท่า** C เปลี่ยนข้อกำหนดหรือบริบท เป็น transfer แยกจากคะแนนหลัก

## สุ่มสลับสี่กลุ่ม

| กลุ่ม | รอบ 1 | รอบ 2 |
|---|---|---|
| G1 | P-A | S-B |
| G2 | S-A | P-B |
| G3 | P-B | S-A |
| G4 | S-B | P-A |

แบ่งจำนวนใกล้กันและจับฉลากก่อนเรียน ใช้ตารางนี้แยกสำหรับ Lab1, Lab3, Lab2-basic และ Lab2-rollback เก็บกลุ่มและลำดับใน scores.csv ไม่แจกเฉลยจนจบคู่ ห้ามผู้เรียนแลกคำตอบข้ามกลุ่มระหว่างทำ ผู้ที่เคยเห็นเฉลยให้ระบุ exposed และแยกวิเคราะห์

## Budget ที่ประกาศล่วงหน้า

| งาน | เวลาต่อรอบคน | เวลาสูงสุดต่อ model invocation | จำนวนข้อความขอแก้สูงสุด | คำใบ้สูงสุด |
|---|---:|---:|---:|---:|
| Lab1 | 15 นาที | 300 วินาที | 2 | 3 ครั้ง |
| Lab2 basic | 15 นาที | 300 วินาที | 2 | 3 ครั้ง |
| Lab2 rollback | 15 นาที | 300 วินาที | 2 | 3 ครั้ง |
| Lab3 | 20 นาที | 300 วินาที | 2 | 3 ครั้ง |

เก็บร่างแรกก่อนแก้เสมอ การวิเคราะห์/ตรวจที่ส่งเป็นข้อความเพิ่มเพื่อเปลี่ยนคำตอบนับ correction ด้วย ไม่แอบเพิ่มงบหลังเห็นว่าแบบใดเสียเปรียบ ไม่มี seed deterministic หรือ hard token cap ที่ยืนยันสำหรับคำสั่งนี้ จึงไม่อ้างควบคุม tokens เท่ากัน ใช้เวลา/จำนวนรอบเป็น budget และบันทึก usage จริงจาก JSONL

รอบ machine baseline ใช้ 1 invocation ต่อโจทย์ ไม่มี hints/corrections ทั้ง P/S เพื่อแยกผลจากคน; รอบช่วยแก้ถ้าทำให้แยกผลเป็น assisted และรักษาเพดานเดียวกัน การรอเครือข่าย/ล้มเหลว/timeouts เก็บเป็นผล censored ไม่ลบออกเงียบ ๆ และไม่ retry อัตโนมัติเมื่อโมเดล error

## เตรียมพื้นที่จริง (ผู้สอน/parent เท่านั้น)

จากรากแพ็กเกจ คำสั่งต่อไปนี้สร้างเฉพาะพื้นที่ใหม่ ไม่ส่งคำขอ AI:

```bash
python3 instructor/runtime/prepare_experiment.py lab1 A P --label lab1-A-P-r1
python3 instructor/runtime/prepare_experiment.py lab1 B S --label lab1-B-S-r1
python3 instructor/runtime/prepare_experiment.py lab3 A P --label lab3-A-P-r1
python3 instructor/runtime/prepare_experiment.py lab3 B S --label lab3-B-S-r1
python3 instructor/runtime/prepare_experiment.py lab2 basic-A P --label lab2-basic-A-P-r1
python3 instructor/runtime/prepare_experiment.py lab2 basic-B S --label lab2-basic-B-S-r1
python3 instructor/runtime/prepare_experiment.py lab2 rollback-A P --label lab2-rollback-A-P-r1
python3 instructor/runtime/prepare_experiment.py lab2 rollback-B S --label lab2-rollback-B-S-r1
```

แต่ละคำสั่งพิมพ์ WORKSPACE ให้เข้าโฟลเดอร์นั้น สร้างเป็น nested repo ใหม่เพื่อจำกัดการค้นหา Skill จาก repo ancestor ไม่มี commit/push หรือแก้บัญชี ผู้สอนตรวจ skill ระดับ user/admin ที่อาจซ้ำและให้ทั้งสองแบบได้รายการพื้นฐานเหมือนกัน ตัวช่วยไม่แก้ config หรือ credential ใดให้

ไฟล์ในพื้นที่: input.md, references.md, template.md, prompt.txt; P เพิ่ม instruction.md; S เพิ่ม native skill; Lab2 เพิ่ม labctl และ helper source ที่จำเป็น ไม่มีเฉลย worksheet ที่กรอกแล้ว หรือผลรันก่อนหน้า พร้อม manifest SHA-256 ที่เก็บนอกพื้นที่ทดลอง ในนั้น native_loaded ยัง pending

การแยกโฟลเดอร์และ repo ช่วยลดการอ่านปนกัน **ไม่ใช่ filesystem sandbox** wrapper นี้ข้าม approval/sandbox ผู้สอนต้องเตรียม OS/เครื่องฝึกที่จำกัดการเข้าถึงให้ตามบริบท โดยให้ P/S เท่ากัน ตรวจ trace ว่าไม่มีการอ่าน instructor keys หรือข้ามขอบเขต ถ้าพบให้ตัดสิน invalid และรายงานเหตุผล ไม่ใช้ผลนั้นสรุปประสิทธิภาพ

## Native discovery gate ก่อนนับเป็น S

1. เปิด Codex ใน workspace S ด้วยคำสั่งใน setup.md ใช้ `/skills` หรือ `$` ดูชื่อและเส้นทาง `.agents/skills/.../SKILL.md`; เก็บหลักฐานรายการโดยไม่ส่งข้อมูลทดสอบเพื่อขอคำตอบ
2. ปิด session ตรวจแล้วเริ่ม `exec` ใหม่สำหรับงานจริง ดู trace ว่า Skill ถูกค้นพบ/เลือกและโหลด body ที่ path นั้นจริง ถ้ารุ่นนี้ไม่แสดง trace การอ่าน ให้เก็บ session context/list และหลักฐานอื่นที่ยืนยัน host loaded body; คำกล่าวของ AI เพียงอย่างเดียวไม่พอ
3. ถ้าหาไม่พบหรือยืนยันการโหลดไม่ได้ บันทึก native_discovery=fail/unverified ห้ามนับเป็น S สำเร็จ การอ่าน attached text แทนต้องเรียกเป็น manual-file condition แยก

Syntax `$skill-name` ตรวจจาก binary ที่ติดตั้ง และตำแหน่ง project ยืนยันด้วย official docs ตาม setup.md; **การค้นพบ/ใช้สกิลใหม่ทั้งสามจริงยัง pending** parent เป็นผู้ทำ gate และแนบหลักฐาน ไม่ต้องเรียก nested cyolo เพื่อเตรียมไฟล์

## Exact invocation สำหรับ parent

ตัวอย่างอยู่ใน workspace ที่สร้างแล้ว (เปิด terminal ณ โฟลเดอร์นั้น) ไฟล์ prompt.txt เตรียมพร้อมทุกตัวอักษรแล้ว ห้าม shell-expand `$skill-name` ด้วย double-quoted inline prompt

```bash
cyolo1 exec --skip-git-repo-check -m gpt-6-astra -c model_reasoning_effort=high --json -o answer.md - < prompt.txt > run.jsonl 2> run.stderr
```

`-` อ่าน prompt จาก stdin จึงใช้ `< prompt.txt` แทน `< /dev/null` ในคำสั่งนี้โดยตั้งใจ รุ่นติดตั้งมี exec help รองรับวิธีนี้; ไม่ใช่เปิด TUI ค้าง ถ้า parent ส่ง prompt เป็น argument จาก orchestration ให้ปิด stdin ด้วย DEVNULL และรักษาเนื้อหา literal เหมือนเดิม

Parent จับ monotonic start/end และบังคับ timeout 300 วินาทีด้วย orchestrator ที่มีอยู่ หยุด session ของงานนั้นเมื่อหมดเวลา ไม่ฆ่า process อื่น อย่าให้ exit code 0 อย่างเดียวตัดสินสำเร็จ ตรวจ run.jsonl ว่าไม่มี turn.failed และมีคำตอบใน answer.md เก็บ usage เมื่อมี turn.completed บันทึก CLI version/model/effort/เวลาUTC/คำสั่ง/manifest/trace คู่กัน

Lab2 ต้อง setup scenario ก่อนเริ่มนับเวลาใน workspace นั้น เช่น:

```bash
./labctl setup rollback-B
```

หลังงานหรือ timeout parent รัน `./labctl stop` ใน workspace นั้นเสมอและเก็บ stdout ถ้ามีการขัดข้องของเครื่องให้ลงบันทึกแยก ไม่เปลี่ยนเป็นเว็บดีแล้วค่อยจับเวลา

## Controlled repeat และ transfer

รอบหลักทำครบ 4 allocation กลุ่ม จากนั้นทำ controlled machine repeat 3 ครั้งต่อ condition/variant โดย workspace ใหม่, session ใหม่, input/canonical/ref hashes เท่าเดิม เปลี่ยน label เป็น r2/r3 และสลับลำดับเริ่ม P/S ตามตาราง ไม่ให้ผลเก่าเข้า context ระบุผลของการ warm cache และความไม่แน่นอนของโมเดล ไม่ใช้ best-of-three แทนรายงานทุกครั้ง

คนทำ A/B ซ้ำอาจจำโจทย์ จึงไม่เรียกว่าหลักฐานอิสระใหม่ หากจะ repeat คน ใช้ cohort ใหม่ที่ยังไม่เห็นข้อมูล หรือบันทึก memory exposure และวิเคราะห์แยก

Transfer: `python3 instructor/runtime/prepare_experiment.py lab1 C S` หรือ lab3 C S หรือ lab2 transfer-C S ใช้ Skill frozen เดิมก่อนแก้ จากนั้นค่อยวัด maintenance หากจำเป็น Prompt transfer เตรียมใช้ในแต่ละ Lab ประเมิน accuracy ด้วย rubric C แยก ไม่เอา C ปน A/B

## สรุปผลอย่างซื่อสัตย์

กรอก [scores.md](scores.md), [scores.csv](scores.csv), [summary.md](summary.md) ตามนิยาม ไม่เติมเลขประมาณลง observed เปรียบเทียบเป็นคู่ในแต่ละความยาก/กลุ่ม รายงานทุกครั้งและใช้ median/range เมื่อมี repeated machine runs เวลาเครื่องเป็น latency ของงานเครื่อง ไม่ใช่เวลามือใหม่ทำงานสำเร็จ

ข้อสรุปที่เป็นไปได้: Skill อาจช่วยลดการคัดลอกคำแนะนำในการใช้ซ้ำ แต่คุณภาพไม่ต่างเมื่อ body เท่ากัน; ถ้า body ขาดขั้นหรือนโยบายเก่า Skill ก็ทำผิดซ้ำได้ ข้อความนี้เป็นสมมติฐานสำหรับอภิปราย ไม่ใช่ผลที่พบแล้ว
