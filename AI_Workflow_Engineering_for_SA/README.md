# AI Workflow Engineering for SA

วิศวกรรมเวิร์กโฟลว์ AI สำหรับนักวิเคราะห์ระบบ — กรณีศึกษา “ครัวคุณยาย”

## ภาพรวมและเป้าหมาย

ฝึกงาน System Analyst ตั้งแต่ User Story ไปจนถึงชิ้นงานที่ Developer และ QA ตรวจย้อนกลับได้
ใช้กรณีร้านอาหารเดียวกันเพื่อเห็นความต่างของ Single Prompt, Loop, Static Graph,
Conditional Graph และ Dynamic Workflow ที่ปรับแผนเมื่อมีข้อกำหนดเพิ่ม

ผู้เรียนเหมาะกับนักศึกษาที่อ่าน User Story และใช้ Terminal เบื้องต้นได้
ไม่จำเป็นต้องมีระบบร้านอาหารจริง แต่ต้องแยกข้อเท็จจริง สมมติฐาน และข้อมูลจำลองให้ชัด

เมื่อจบควรอธิบายการส่งต่อ US → FR/NFR → Flow/Structure → UI → Test ได้
เลือก workflow ให้เหมาะกับงาน และเปรียบเทียบคุณภาพกับทรัพยากรจากหลักฐานจริง
การมีไฟล์ผลลัพธ์หรือการคลิก mock-up ผ่านไม่เท่ากับผ่านเกณฑ์ของระบบจริง

## เตรียมเครื่อง

- Terminal และโปรแกรมอ่าน Markdown/CSV/JSON
- Python 3 และ Chromium สำหรับทดสอบอัตโนมัติ
- Codex CLI หรือ Claude Code ที่ตั้งค่าบัญชี `<ACCOUNT>` ของผู้เรียนแล้ว
- โฟลเดอร์บทเรียนครบชุด รวมรูปภาพและผลอ้างอิง
- ไฟล์ `appendix-a-restaurant.md` และ `ai-agent-routing.html` อยู่ข้างโฟลเดอร์บทเรียน

`<ACCOUNT>` เป็น placeholder สำหรับการตั้งค่าบัญชี ไม่ใช่อาร์กิวเมนต์ของคำสั่งส่ง Prompt
อย่าใส่บัญชีจริง อีเมล หรือ token ลงใน Prompt หรือชิ้นงานที่ส่ง
เปิดดูเวอร์ชันของเครื่องมือที่เลือกก่อนบันทึกผล:

```bash
python3 --version
codex --version
# หรือเมื่อเลือก Claude Code
claude --version
```

การอ่านบทเรียนและลอง UI ไม่ต้องเรียกโมเดล ส่วนการรัน Prompt อาจใช้โควตาบัญชีของผู้เรียน
การติดตั้งชุดทดสอบดู [tests/README.md](tests/README.md)

## โครงสร้างไฟล์ที่มีจริง

```text
AI_Workflow_Engineering_for_SA/
├── README.md
├── AI_Workflow_Engineering_SA.html
├── docs/
│   ├── case-study-source.md
│   ├── data-issues.md
│   ├── us-coverage.md
│   ├── rubric.md
│   └── test-report.md
├── img/                         # แผนภาพ PNG, SVG และ Excalidraw
├── 001_LAB_Single_Prompt_Baseline/
├── 002_LAB_Loop_FR_NFR/
├── 003_LAB_Static_Graph_Flow_Structure/
├── 004_LAB_Conditional_Graph_UI_Mockup/
├── 005_LAB_Dynamic_Workflow_Replanning/
├── 006_LAB_Test_Scenarios_Traceability/
├── 007_LAB_Evaluation_Compare_Workflows/
└── tests/                       # สคริปต์ ผล JSON และภาพ QA
```

แต่ละ LAB มี `README.md`, `input/`, `prompts/`, `reference/`, `img/` และ `work/`
ใช้ `work/` สำหรับผลของตนเอง โดยอ่านขั้นตอนของ LAB ก่อนเลือกชื่อไฟล์และรอบ
ตัวอย่างชิ้นงาน Flow ตามบทบาทใช้ `work/flow-<role>.md`

## เปิดสไลด์

ดับเบิลคลิก [AI_Workflow_Engineering_SA.html](AI_Workflow_Engineering_SA.html) เพื่อเปิดด้วยเบราว์เซอร์
เก็บไฟล์ HTML ไว้ร่วมกับโฟลเดอร์ LAB และรูปภาพ เพื่อให้ลิงก์ relative ทำงาน
เปิดผ่าน `file://` ได้โดยไม่ต้องเริ่มเว็บเซิร์ฟเวอร์:

```bash
cd AI_Workflow_Engineering_for_SA
xdg-open "file://$(pwd)/AI_Workflow_Engineering_SA.html"
```

| คีย์ | การทำงาน |
|---|---|
| → / Space / PageDown | หน้าถัดไป |
| ← / PageUp | หน้าก่อน |
| Home / End | หน้าแรก / หน้าสุดท้าย |
| O | เปิดหรือปิด overview แล้วคลิกหน้าที่ต้องการ |
| F | เต็มจอ ตามสิทธิ์ที่เบราว์เซอร์รองรับ |
| ? | แสดงวิธีควบคุม |
| Esc | ปิดวิธีควบคุมหรือ overview |

เมื่อคลิก UI ที่ฝังอยู่ แป้นพิมพ์จะส่งให้ iframe; คลิกพื้นที่หัวสไลด์ก่อนเลื่อนหน้าต่อ
UI ในสไลด์เป็นสำเนาฝังสำหรับสาธิต การทดสอบไฟล์ UI อ้างอิงแยกแสดงในรายงาน QA

## ลำดับ LAB

เวลาในตารางเป็นประมาณการจัดการเรียนตามคู่มือ ไม่ใช่เวลารันที่วัดจาก log
ช่อง “ไม่มีข้อมูล” คงไว้เมื่อคู่มือไม่ได้ให้ประมาณการ

| LAB | workflow | ชิ้นงานหลัก | เวลาเรียน | คู่มือ |
|---|---|---|---|---|
| 001 | Single Prompt baseline | US analysis, FR/NFR v0, self-check | 60–90 นาที | [เริ่ม LAB 001](001_LAB_Single_Prompt_Baseline/README.md) |
| 002 | Generator → Checker → Fixer loop | FR/NFR ที่ตรวจแล้วและ loop log | 90–120 นาที | [เริ่ม LAB 002](002_LAB_Loop_FR_NFR/README.md) |
| 003 | Static Graph แยกบทบาทแล้วรวม | Flow รายบทบาท, state machine, structure, merge | ไม่มีข้อมูล | [เริ่ม LAB 003](003_LAB_Static_Graph_Flow_Structure/README.md) |
| 004 | Conditional Graph | UI v1 และผลตัดสินผ่าน/แก้/หยุด | ไม่มีข้อมูล | [เริ่ม LAB 004](004_LAB_Conditional_Graph_UI_Mockup/README.md) |
| 005 | Dynamic Workflow และ Re-planning | แผนหลายรุ่น, impact analysis, UI v2 | 150–180 นาที | [เริ่ม LAB 005](005_LAB_Dynamic_Workflow_Replanning/README.md) |
| 006 | Static Graph และ coverage loop | Scenarios, traceability, NFR split, UI test | 150–180 นาที | [เริ่ม LAB 006](006_LAB_Test_Scenarios_Traceability/README.md) |
| 007 | Evaluation และทดลองข้อเปลี่ยน | Metrics, rubric, comparison report | 120–150 นาที | [เริ่ม LAB 007](007_LAB_Evaluation_Compare_Workflows/README.md) |

## เริ่ม LAB และรัน Prompt

อ่านโจทย์ ขอบเขต US เกณฑ์ตรวจ และเพดานรอบใน README ของ LAB ก่อนเริ่ม
ทำตามลำดับ **อ่าน Input → คัดลอก Prompt → รัน → เปิดผล → เทียบ → ตรวจ → ขั้นถัดไป**
รันจาก working directory ที่ขั้นนั้นกำหนด เพราะ Prompt ใช้ path สัมพันธ์กับตำแหน่งรัน

ตัวอย่างจากโฟลเดอร์บทเรียนสำหรับเริ่ม LAB 001:

```bash
cd 001_LAB_Single_Prompt_Baseline
mkdir -p work
ls prompts
```

เลือกชื่อไฟล์ Prompt ที่มีจริงจาก `prompts/` แล้วตั้งตัวแปรก่อนส่ง:

```bash
PROMPT_FILE='prompts/<ชื่อไฟล์จริง>.md'
codex exec "$(cat "$PROMPT_FILE")"
```

หรือใช้เครื่องมืออีกแบบกับ Prompt เดียวกัน:

```bash
claude -p "$(cat "$PROMPT_FILE")"
```

ตัวอย่างคำสั่งนี้เป็นวิธีใช้ ไม่ใช่หลักฐานรันใหม่
ตรวจไฟล์ใน `work/` หลังเรียกทุกครั้ง และอ่าน feedback ก่อนเริ่มรอบถัดไป
ถ้าไม่มีข้อมูลเวลา/โทเคนใน log ให้บันทึก “ไม่มีข้อมูล” แทนการประมาณเอง
เก็บผลแต่ละรอบแยกกันเพื่อเทียบข้อแก้และตรวจย้อนกลับได้

## ดูผลอ้างอิง

`reference/` เก็บผลรันล่วงหน้า รายงาน และหลักฐานของผู้จัดทำ
อ่าน README ของแต่ละ LAB เพื่อเลือกผล final และเข้าใจรอบที่ล้มเหลวหรือถูกแก้
เมื่อใช้ผลอ้างอิงเรียนต่อ ให้ระบุว่า “ใช้ผลอ้างอิง” ไม่บันทึกเป็นผลรันของตนเอง

| LAB | ผลอ้างอิง |
|---|---|
| 001 | [reference/](001_LAB_Single_Prompt_Baseline/reference/) |
| 002 | [reference/](002_LAB_Loop_FR_NFR/reference/) |
| 003 | [reference/](003_LAB_Static_Graph_Flow_Structure/reference/) |
| 004 | [reference/](004_LAB_Conditional_Graph_UI_Mockup/reference/) |
| 005 | [reference/](005_LAB_Dynamic_Workflow_Replanning/reference/) |
| 006 | [reference/](006_LAB_Test_Scenarios_Traceability/reference/) |
| 007 | [reference/](007_LAB_Evaluation_Compare_Workflows/reference/) |

หลักฐานดิบที่ผูก SHA-256 คงข้อความและ path เครื่องเดิมไว้เพื่อให้ตรวจ hash ได้
ลิงก์บางจุดในหลักฐานเดิมยังชี้ตำแหน่งขณะรัน ดูรายการที่เหลือในรายงานทดสอบ
LAB 003 มีสถานะ BLOCKED ด้าน readiness; การมีผล merge ไม่ได้แปลว่าพร้อมพัฒนาระบบจริง

## ทดลอง UI v1 และ v2

เปิด [UI v1](004_LAB_Conditional_Graph_UI_Mockup/reference/final/ui-mockup.html)
หรือ [UI v2](005_LAB_Dynamic_Workflow_Replanning/reference/step-05-execute-v2/ui-mockup-v2.html)
ด้วยเบราว์เซอร์ผ่าน `file://` เช่นเดียวกับสไลด์

1. กด **รีเซ็ตทั้งหมด / ออกจากระบบ** แล้วเลือกแท็บลูกค้า
2. เลือกโต๊ะ → เปิดเมนู / เริ่มรอบสั่ง → เลือกอาหาร → เพิ่มลงตะกร้า → ส่งออเดอร์เข้าครัว
3. เลือกแท็บครัวและหน้าร้าน → เลือกบัญชีสาธิตครัวจากรายการ → ใส่ PIN สาธิต `0000` → เข้าสู่ระบบ
4. เปิดหน้าคิวครัวและเปลี่ยนสถานะ แล้วกลับแท็บลูกค้าเพื่อดูสถานะใหม่
5. เลือกเงินสดหรือ PromptPay จำลอง จากนั้นใช้บัญชีสาธิตหน้าร้านยืนยันการรับเงิน
6. ทดลองแท็บผู้จัดการด้วยบัญชีสาธิตผู้จัดการและ PIN เดียวกัน เพื่อดูเมนูและสิทธิ์ตามบทบาท
7. ใน v2 ทดลองปุ่มแจ้งรายการทำไม่ได้จากครัว แล้วกลับลูกค้าเพื่อเลือกคืนรายการหรือเปลี่ยนเมนู
8. ก่อนทดลองกรณีใหม่ กด **รีเซ็ตทั้งหมด / ออกจากระบบ**; เปิดไฟล์ใหม่จะเริ่มข้อมูลจำลองใหม่เช่นกัน

บัญชีใน dropdown เป็นข้อมูลสาธิตใน UI ไม่ใช่บัญชี CLI ของผู้เรียน
ครัวและหน้าร้านอยู่แท็บเดียวกัน แต่ต้องเลือกบัญชีบทบาทให้ถูกก่อนใช้งาน
ข้อมูลอยู่ในหน่วยความจำของหน้านั้น การสลับบทบาทในแท็บเดียวกันไม่ใช่การทดสอบหลายอุปกรณ์
นาฬิกาใน UI เป็นนาฬิกาจำลอง ปุ่มเพิ่มเวลาช่วยดูกรณีรอสลิปโดยไม่รอเวลาจริง
PromptPay ไม่มีการโอนเงินจริง; คืนรายการเป็นการปรับข้อมูลจำลอง ไม่ใช่บริการคืนเงิน

## ขอบเขต US และข้อมูลที่ต้องยืนยัน

| กลุ่ม LAB | จำนวน US ในขอบเขตกิจกรรม |
|---|---|
| 001, 006, 007 | 26 |
| 002, 003 | 18 |
| 004 | 16 |
| 005 | 14 |

ตารางนี้เป็นขอบเขตกิจกรรมจาก [us-coverage.md](docs/us-coverage.md) ไม่ใช่จำนวน US ที่ผ่านระบบจริง
การเปิดเผยข้อกำหนดเพิ่มใน LAB 005 เป็นวิธีจัดกิจกรรม แม้ต้นฉบับและ LAB 001 จะเห็น US เหล่านั้นแล้ว
หมายเหตุ ก./ค./ช. ไม่มีนิยามครบ และ US-20 อ้างรหัสที่ต้องยืนยันตามทะเบียนปัญหา
แยกสมมติฐานเรื่องชื่อสถานะ ETA และการคืนรายการออกจากข้อความต้นฉบับเสมอ

## เอกสารกลาง

- [แหล่งข้อมูลกรณีศึกษา](docs/case-study-source.md): ตารางต้นฉบับและบริบทร้าน
- [ปัญหาข้อมูลและสมมติฐาน](docs/data-issues.md): สิ่งที่ไม่รู้และข้อเสนอที่ยังรอยืนยัน
- [ความครอบคลุม US](docs/us-coverage.md): ขอบเขตและลิงก์ชิ้นงานแต่ละ LAB
- [Rubric](docs/rubric.md): มิติประเมินและแบบบันทึก
- [รายงานสถานะทดสอบ](docs/test-report.md): ผลจริงราย scenario ข้อจำกัด และรายการลิงก์

## รัน QA และอ่านผล

จากโฟลเดอร์บทเรียน:

```bash
bash tests/run_all.sh
```

เลือก Python ที่ติดตั้ง Playwright ได้ด้วย `PYTHON=.venv/bin/python bash tests/run_all.sh`
ดูวิธีแยกรันแต่ละชุดใน [คู่มือ tests](tests/README.md)
สคริปต์บันทึก [results.json](tests/results.json), [link-report.json](tests/link-report.json)
และภาพใน [screenshots/](tests/screenshots/)

สรุปผลรอบนี้: สไลด์ 143 หน้าและ 143 ภาพผ่าน ไม่พบ console error หรือล้นตามเกณฑ์
UI v1 ผ่าน 11 ตก 3 ข้าม 0; UI v2 ผ่าน 12 ตก 2 ข้าม 0
เคสที่ตกยังอยู่ในผล JSON และมีเหตุผล ไม่ถูกเปลี่ยนเป็นข้ามเพื่อให้ผลผ่าน
ลิงก์ในไฟล์ที่นักศึกษาใช้เสีย 0; ลิงก์ในหลักฐานดิบ 121 จุดเป็น known issue ดูรายการใน [รายงานทดสอบ](docs/test-report.md)
รายละเอียดและตัวเลขล่าสุดอยู่ใน [test-report.md](docs/test-report.md)

## ข้อจำกัดในการตีความ

ผลนี้ตรวจ offline mock-up บน Chromium ไม่ได้ตรวจมือถือจริง เบราว์เซอร์อื่น หรือระบบหลังบ้าน
ยังไม่พิสูจน์ NFR บน LAN/Wi-Fi ร้าน ความแม่น ETA สิทธิ์ฝั่งเซิร์ฟเวอร์ และการติดตั้งจริง
ผลรันล่วงหน้าเป็นการรันครั้งเดียวภายใต้บริบทที่บันทึกไว้ ไม่ใช่ค่าเฉลี่ยหรือสัญญาระดับบริการ
ต้นทุนเงินและค่าที่ไม่มี event รองรับให้คง “ไม่มีข้อมูล”
ใช้ผลทดสอบประกอบการตัดสินใจและออกแบบการตรวจระบบจริงต่อ ตาม NFR split ใน LAB 006
