# รายงานตรวจสอบ Week2

ตรวจและจัดทำรายงาน ณ **2026-09-12T14:07:18.361377+00:00** สถานะ PASS หมายถึงผ่านขอบเขตที่ทดสอบในเครื่องนี้ ไม่ใช่การรับรองผลการเรียนหรือความเหนือกว่าของ Skill

| รายการ | สถานะ | หลักฐานและขอบเขต |
|---|---|---|
| สไลด์ไทยไฟล์เดียว | PASS | [index.html](index.html), 23 หน้ามีเลข + ปก; CSS/JS/SVG/ภาพฝังในไฟล์; เปิด file:// โดยไม่มี HTTP asset request |
| เดสก์ท็อป/มือถือ | PASS | [desktop](evidence/browser/slides-desktop.json) 1440×1000, [mobile](evidence/browser/slides-mobile.json) 390×844; ตรวจ overflow, console, ลิงก์, navigation, ปุ่มคัดลอก |
| พิมพ์ | PASS | [PDF จริง](evidence/browser/slides-print.pdf) 24 หน้า A4 แนวนอน; [จำนวนหน้า/ข้อความ](evidence/browser/print-check.json); เปิดภาพหน้า 1, 8, 15, 23 ตรวจด้วยตา |
| สาม Lab ครบและอ่านบนมือถือ | PASS | [Lab1](001_LAB_System_Analysis/README.html), [Lab2](002_LAB_DevOps_Recovery/README.html), [Lab3](003_LAB_LLM_Business/README.html); A/B/C, prompts, manual, worksheet, hints, examples, rubric/key, transfer; [หลักฐาน viewport](evidence/browser/lab-guide-checks.json) |
| Excalidraw จริง | PASS | สร้างและ export ผ่าน installed CLI 2.0.0 + canvas ที่เป็นเจ้าของ; [บันทึกคำสั่ง](evidence/build/excalidraw-commands.md), [source](diagrams/workflow.excalidraw), [SVG](diagrams/workflow.svg), [PNG](diagrams/workflow.png); มีชุดแนวตั้งมือถือและเปิดภาพตรวจจริง |
| ร้านฝึก basic-A/B | PASS | เริ่ม STOPPED/browser เชื่อมต่อไม่ได้ → start → กดจอง → เลขรายการปรากฏในบริการ; [A](evidence/browser/basic-A.json), [B](evidence/browser/basic-B.json) |
| ร้านฝึก advanced-A/B | PASS | v2 เปิดหน้าได้แต่จอง 503 → rollback เปลี่ยนบริการจริงเป็น v1 → กดจองสำเร็จ; [A](evidence/browser/advanced-A.json), [B](evidence/browser/advanced-B.json) |
| คำสั่งร้านและการแยกพอร์ต | PASS | ทดสอบ open/preflight/status/logs/start/rollback/check/reset/stop, คำสั่งซ้ำ, [C](evidence/browser/transfer-C.json), [พอร์ตแยก](evidence/browser/port-isolation.json); ไม่มี Docker |
| Playwright CLI | PASS | **12 passed, 0 skipped, 0 flaky, 0 failed** รอบสุดท้าย 2026-09-12T14:00:00.618Z, 20.852 วินาที; [CLI log](evidence/browser/final-cli.log), [JSON](evidence/browser/playwright-results.json), [คำสั่ง/รุ่น](instructor/testing.html) |
| Scorecard ไม่เขียนโค้ด | PASS | แก้ช่องได้, localStorage คงค่าหลัง reload, ดาวน์โหลด CSV จริงและ escape formula; [ผลตรวจ](evidence/browser/scorecard-test.json), [ไฟล์ดาวน์โหลด](evidence/browser/scorecard-download.csv) |
| Native Skill | PASS สำหรับ 6 S หลักและ C/สาธิตที่ยืนยัน | `.agents/skills` พร้อม name/description; ตรวจไฟล์ด้วย validator และ JSONL ที่อ่าน SKILL.md exit 0 จริง; [validation](evidence/build/skill-validation.json), [ผลรายรอบ](evidence/index.html) |
| Baseline ขั้นตอนครบ | PASS | body ของ Skill ตรง procedure ที่ใส่ P ทุก Lab; directory ใหม่/input-only ทุก run, snapshots/hash, คู่มือ/ข้อมูล/โมเดล/effort/time cap เดียวกัน; [audit](evidence/build/package-audit.json), [protocol](instructor/protocol.html) |
| ให้ AI สร้าง/ปรับ Skill และใช้ C | PASS | เรียกผ่าน `./learn run ask` จริง; file_change จำกัด SKILL.md, rerun อ่าน Skill ใหม่; [ก่อน/หลัง/prompt/raw/log](evidence/creation/README.md) |
| ZIP แบบย้ายโฟลเดอร์ | PASS ภายใน Linux | [ZIP](Week2-teaching-package.zip) แตกใหม่ใน /tmp, มี executable bits และ 3 native skills, ตรวจ CRC; ร้านล่ม→start และ v2→rollback→จองจริง; [ผล](evidence/build/zip-check.json). รอบนี้เป็น HTTP smoke ไม่อ้างว่า browser suite รันซ้ำใน ZIP |
| Week1 และ cleanup | PASS ณ เครื่องต้นทาง | fingerprint 76 ไฟล์ไม่เปลี่ยนจากเริ่มงาน; [audit](evidence/build/package-audit.json). หยุด process ที่สร้างเองและปิดพอร์ต 3017/18761–18764; [cleanup](evidence/build/cleanup.json) |

## ผลทดลองกับข้อจำกัดที่ต้องอ่านร่วมกัน

มี raw logs และ metadata ครบ **22 calls**: เปรียบเทียบหลัก 12, S เดิมที่ยังยืนยัน native ไม่ได้ 4, frozen Skill ใช้ C 3, สาธิตสร้าง/ปรับ/ใช้ C อีก 3 ทุก call ตอบจบ exit 0 และไม่ timeout สี่รอบที่กันออกไม่ใช่คำตอบล้มเหลว แต่ CLI trace ไม่แสดงการอ่านไฟล์ จึงไม่ใช้เป็นหลักฐาน native และไม่รวมคะแนนหลัก

ใช้ cyolo1 / gpt-6-astra / high เท่านั้นในทุก call ที่ระบุ ตรวจ login ก่อนทดลอง; มี `-o` เป็นไฟล์จริงและ stdin `/dev/null` ไม่คัดลอก credential ไม่มีอีเมลหรือข้อความถึงลูกค้า ไม่มีการใช้ผล Week1 เป็นผลรอบนี้

Lab1/2 ได้ 12/12 ทั้ง P/S ตาม 12 เกณฑ์ที่กำหนด Lab1 Skill ยังมีคำภาษาจีนปนซึ่งคะแนนความครบถ้วนไม่ครอบคลุม Lab3 ได้ P=10/12, S=11/12 ตาม key เดิม แต่ทั้งคู่ได้ 12/12 ใน sensitivity ที่ยอมรับการตีความคิวที่มีเหตุผล การวิเคราะห์นี้ทำ **หลังเห็นผล** และแสดงแยกจากคะแนนเดิม ดู [คะแนนรายข้อ/ความผิดพลาด/สิ่งที่ต้องแก้](evidence/summary.html) และ [C](evidence/transfer-review.html)

- **UNVERIFIED — ผู้เรียนจริง:** ไม่มี classroom study, ผู้ให้คะแนนมนุษย์อิสระ หรือการให้คะแนนแบบปกปิดเงื่อนไข คะแนนเป็น AI worker ผู้จัดทำอ่านเทียบแหล่งและ key; ความแม่นยำรายข้ออ้างทั้งหมด, เวลา/คำใบ้/การแก้ไขของมนุษย์ = not-measured
- **LIMIT — ความเที่ยงของการเปรียบเทียบ:** เพียง A/B หนึ่งครั้งต่อเงื่อนไขต่อ Lab; S-confirmed Lab1/3 รันหลัง P และมีคำขออ่านไฟล์เพิ่ม ผลเวลา/โทเคนจึงมี instrumentation, ลำดับ และ caching ปน แม้ body ขั้นตอนเท่ากัน ไม่ใช้สถิติอ้างประสิทธิผลทั่วไป
- **LIMIT — บริบทแยก:** แต่ละ run เริ่ม exec ใหม่ใน git-root ชั่วคราว มีเพียง inputs/manual/Skill ที่เกี่ยวข้อง; audit trace ไม่พบอ่านเฉลยหรือรอบอื่น แต่เป็นขอบเขตจากคำสั่งและตรวจ log ไม่ใช่ OS sandbox เพราะ wrapper ห้องมีสิทธิ์กว้าง
- **LIMIT — Lab2:** AI ให้การวินิจฉัยจาก snapshot และแนะนำคำสั่ง คนเป็นผู้ตัดสินใจในกิจกรรม; ผล browser เป็นการทดสอบ runtime อัตโนมัติแยกกัน ห้ามนำเวลาการรัน AI ไปเรียกว่าเวลามนุษย์กู้ระบบ
- **LIMIT — assisted C:** Skill ที่ปรับหลังเห็นตัวอย่างผิด/C ถือเป็น assisted transfer; frozen C แยกเก็บก่อนสาธิต ไม่อ้างว่า rerun เป็นข้อมูลที่ไม่เคยเห็น
- **UNVERIFIED — สภาพแวดล้อมอื่น:** ทดสอบ Linux + Playwright CLI 1.58.2 + Chrome for Testing 153.0.8010.12 ที่ติดตั้งอยู่; ไม่ได้ทดสอบ Windows/macOS/Safari/Firefox หรือผู้ใช้ assistive technology จริง การเลือก `$`/`/skills` ใน TUI อ้างเอกสารทางการ ส่วนเส้นทางที่ลงมือทดสอบคือ native exec ผ่าน launcher
- **LIMIT — ต้นทุน:** แยกเวลา/token ของการสร้างและปรับ Skill; เวลา setup และ maintenance ของมนุษย์ไม่ได้วัด ไม่แปลง subscription usage เป็นราคา API

## ข้อบกพร่องระหว่างสร้างที่แก้และเก็บไว้

รอบ runtime แรกตรวจพอร์ตผิดเมื่อ socket อยู่ TIME_WAIT จึงแก้ preflight ด้วย SO_REUSEADDR แล้วทดสอบใหม่ครบ รอบสไลด์ระหว่างพัฒนาพบลิงก์รายงานยังไม่สร้างและ favicon 404 จึงแก้ก่อนชุดสุดท้าย [หลักฐานรอบแรก](evidence/browser/initial-failure) ยังอยู่ ไม่ลบหรือเปลี่ยนให้เป็น PASS

เปิดภาพจริงทั้ง incident/recovery, desktop/mobile, Excalidraw และหน้า PDF ตรวจความอ่านได้แล้ว รูปแบบตัวอักษรบนเครื่องอื่นอาจต่างจาก font fallback ของเครื่องทดสอบ แหล่งอ้างอิงพฤติกรรมผลิตภัณฑ์และวันที่อยู่ใน [sources](sources.html)


## การปรับชื่อโฟลเดอร์ Lab

ปรับเป็น `001_LAB_System_Analysis`, `002_LAB_DevOps_Recovery` และ `003_LAB_LLM_Business` ใต้ Week2 โดยตรง พร้อมแก้ลิงก์และตัวช่วยเตรียมพื้นที่เรียน คำสั่งพร้อมใช้ยังรับรหัส lab1/lab2/lab3 ตามเดิม ตรวจลิงก์ 354 จุดและเตรียมพื้นที่ 6 กรณีผ่าน ตรวจเบราว์เซอร์เพิ่มด้วย Playwright CLI ผ่าน 3 tests โดยไม่มีการเรียกโมเดลใหม่ หลักฐานทดลองเดิมคงไว้ตามต้นฉบับ; hash และเส้นทางในรายงานทดสอบเดิมหมายถึงฉบับก่อนย้ายโฟลเดอร์ ดู [บันทึกการปรับโครงสร้าง](evidence/build/lab-rename.json) และ [ผลตรวจเว็บรอบนี้](evidence/build/lab-rename-browser/results.json)


## การรวมไฟล์ Lab รอบแรก — ประวัติก่อนเปลี่ยนเป็นสองไฟล์

แต่ละ Lab เหลือ README.md และ README.html พร้อมข้อมูล data/A.md, data/B.md, data/C.md รวม 5 ไฟล์ต่อ Lab เนื้อหาคู่มือ Prompt, Skill, ใบงาน, คำใบ้ ตัวอย่าง และเฉลยครบใน README; เฉลยและคำใบ้พับไว้ใน HTML ตารางคำสั่งซื้อ Lab3 ดาวน์โหลด CSV ได้จากตารางในหน้าเดียว ตัวช่วย ./learn และเครื่องมือทดลองดึงเฉพาะคู่มือ/คำสั่งที่จำเป็น ไม่ส่ง README ที่มีเฉลยให้ AI

ตรวจข้อมูลและคำสั่งเดิมตรงทุกตัวอักษร เตรียมพื้นที่เรียน/ทดลอง 36 กรณีผ่าน Prompt พร้อมใช้ 15 ชุดคงเดิม Playwright CLI ผ่าน 8 tests ทั้งเดสก์ท็อป มือถือ การคัดลอก การเปิดส่วนพับ การดาวน์โหลด CSV และออฟไลน์ CSV ทั้งสามชุดตรงกับต้นฉบับ ไม่มีการเรียกโมเดลใหม่

[หลักฐานการรวมไฟล์](evidence/build/lab-consolidation.json) · [ผลตรวจเบราว์เซอร์](evidence/build/lab-consolidation-browser/results.json)


## สถานะล่าสุด: สองไฟล์ต่อ Lab พร้อมคัดลอกและ Expected output

แต่ละ Lab มีเพียง `README.md` และ `README.html` รวมข้อมูล A/B/C ในกรอบข้อความ ไม่มีโฟลเดอร์ data แยก เพิ่มคำสั่งเริ่มงานทีละขั้น ตำแหน่งที่ต้องวาง และผลลัพธ์ที่คาดหวัง พร้อมปุ่มคัดลอกข้อมูล Prompt และคำสั่งใน HTML คำว่า Expected output เป็นเกณฑ์ที่ผู้เรียนต้องตรวจ ไม่ใช่การอ้างผลทดลอง AI รอบใหม่

ตรวจข้อมูลฝังทั้ง 9 ชุดตรงต้นฉบับทุกตัวอักษร และคู่มือ/Prompt/Skill เดิมไม่เปลี่ยน ตัวช่วยเตรียมพื้นที่เรียนและทดลองผ่าน 36 กรณีหลังลบไฟล์ data แล้ว โดยไม่แนบเฉลยเข้า AI Playwright CLI ผ่าน 13 tests: การแสดงผล 1440×900 และ 390×900, สารบัญ/ส่วนพับ, การคัดลอกข้อมูลทุกชุด, คำสั่ง DevOps, Clipboard fallback, CSV และออฟไลน์ CSV ทั้งสามชุดตรงกับฉบับก่อนรวมไฟล์ ไม่ได้เรียกโมเดลหรือทดสอบการกู้เว็บเพิ่มในการปรับคู่มือรอบนี้

ลบไฟล์ข้อมูลแยก 9 ไฟล์หลังรวมแล้ว ลบตัวเรียกสคริปต์เก่า 2 ไฟล์ที่ไม่มีการใช้งาน และไฟล์สำรองอัตโนมัติ เก็บเครื่องมือกลางที่จำเป็น สื่อภาพและหลักฐานการทดลองเดิมไว้สำหรับการสอนและตรวจสอบ

หลักฐาน: [โครงสร้างและการล้างไฟล์](evidence/build/two-file-cleanup.json) · [ตรวจการเตรียมงาน](evidence/build/two-file-runtime.json) · [ผล Playwright](evidence/build/two-file-browser/results.json) · [ภาพข้อมูลพร้อมคัดลอก](evidence/build/two-file-browser/003_LAB_LLM_Business-copy-data.png)
