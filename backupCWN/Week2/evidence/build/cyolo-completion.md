# Week2 — cyolo completion report

ส่งมอบ ณ **2026-09-12T14:07:18.361377+00:00** ใน `/root/workspace/CWN/Teaching/Week2` งานส่วนนี้เสร็จแล้ว เริ่มใช้จาก [README](../../README.html), [สไลด์](../../index.html) หรือ [ZIP](../../Week2-teaching-package.zip)

## สิ่งที่ส่งมอบ

- สไลด์ภาษาไทย self-contained 23 หน้า + ปก ใช้โครงสร้างภาพและลำดับทฤษฎี Week1 เป็นแนวทาง มี navigation/เลขหน้า/คัดลอก/มือถือ/พิมพ์; อธิบาย Skill เป็นคำแนะนำและ workflow ใช้ซ้ำ ไม่ใช่การ retrain และไม่รับประกันว่าดีกว่า Prompt
- [Lab1](../../001_LAB_System_Analysis/README.html), [Lab2](../../002_LAB_DevOps_Recovery/README.html), [Lab3](../../003_LAB_LLM_Business/README.html) ครบวัตถุประสงค์ เวลา เตรียมงาน สถานการณ์ A/B/C คู่มือ 4 ช่วง prompt ตัวอย่างดี/ผิด ใบงาน คำใบ้สามระดับ troubleshooting rubric/เฉลยผู้สอน อภิปรายและ transfer ผู้เรียนใช้เฉพาะภาษาคน/คำสั่งพร้อมใช้
- Native text-only SKILL.md สามตัวใน `.agents/skills`; launcher `./learn` จัดพื้นที่ input-only ใหม่ ยืนยัน Skill ด้วย log; สาธิตให้ AI สร้าง complaint-desk ปรับด้วยตัวอย่าง v1 ที่ติดป้ายว่าแต่ง และเรียกกับ C จริง
- ร้านฝึก Python stdlib แบบ loopback ที่ทำงานจริง `./shop` ครบคำสั่ง เปิดบริการ/เปลี่ยนรุ่น/rollback/ทำรายการจองจริง ไม่ให้ผู้เรียนแก้ internals การเตรียม runtime อยู่ฝั่งผู้สอนแยกจากภารกิจ 30 นาที
- Excalidraw source และ SVG/PNG ที่สร้าง/export ด้วย CLI จริงทั้งแนวนอนและมือถือ พร้อมภาพจริงจาก browser, PDF 24 หน้า, scorecard กรอกได้และดาวน์โหลด CSV
- [หลักฐานผลทดลอง](../index.html), prompts/raw JSONL/answers/metadata/input snapshots, [คะแนนและข้อจำกัด](../summary.html), [รายงานตรวจสอบ](../../verification.html), คำสั่งทดสอบและ sources ทางการลงวันที่

## วิธีตรวจรับและผล

Playwright **CLI** 1.58.2: **12 ผ่าน / 0 ล้มเหลว / 0 skipped / 0 flaky** ในรอบสุดท้าย 20.852 วินาที ตรวจ basic-A/B ว่า browser ล้มเหลวก่อน start, advanced-A/B ว่าจอง 503 ก่อน rollback และรายการจองสำเร็จหลังเปลี่ยนเป็น v1; ตรวจ C, command transitions และพอร์ตแยก ใช้ Chrome for Testing 153.0.8010.12 ที่ติดตั้งจริง ดู [CLI log](../browser/final-cli.log) และ [JSON](../browser/playwright-results.json)

ตรวจ slides desktop 1440×1000/mobile 390×844, หน้า Lab 390×900, overflow/console errors/link status/navigation/copy, scorecard persistence/CSV download/formula escaping, offline file:// ไม่มี asset ภายนอก และ print PDF 24 หน้า เปิด screenshots และ Excalidraw PNG ตรวจด้วยตาจริง

[ZIP smoke](zip-check.json) แตกลงพื้นที่ใหม่ ตรวจ CRC/native skill/executable bits และกู้บริการจริงทั้งสองเหตุด้วยพอร์ต 18764 พร้อมเลขจอง server-side; หยุดบริการและลบโฟลเดอร์ชั่วคราวแล้ว ZIP ไม่มี credential/auth/cache/node_modules/สถานะ process/learner-results ซ้ำ หรือ log orchestration ที่ parent กำลังเขียน

[audit](package-audit.json) ตรวจลิงก์ภายใน, baseline body เท่ากับ Skill, hash input snapshot, รุ่น/effort และรักษา Week1 **76 ไฟล์ไม่เปลี่ยน** จาก fingerprint ต้นงาน เก็บไฟล์ Week2 ที่มีอยู่และตารางคำสั่งซื้อที่ parent เพิ่มไว้ ไม่มี git commit ไม่มีการส่งอีเมล [cleanup](cleanup.json) ยืนยันพอร์ตของงานทั้งหมดปิด

## การทดลองและ token usage

ทุก call ในชุดทดลองนี้ใช้ `cyolo1 exec -m gpt-6-astra -c model_reasoning_effort="high"` มี `-o` เป็นไฟล์จริง, stdin `/dev/null`, fresh exec/input-only workspace, time cap 240 วินาทีและไม่มี retry อัตโนมัติ ตรวจ login ก่อนเริ่ม

| กลุ่มที่เก็บ raw logs ครบ | calls | เวลารวมของ calls (วินาที) | input tokens | output tokens |
|---|---:|---:|---:|---:|
| เปรียบเทียบหลัก A/B × P/S × 3 Lab | 12 | 917.679 | 526,285 | 24,227 |
| S เดิมที่ยังพิสูจน์ native จาก read-event ไม่ได้ — กันออก | 4 | 308.093 | 136,623 | 7,681 |
| ใช้ frozen Skill กับ C | 3 | 220.216 | 156,122 | 5,538 |
| สร้าง Skill / ปรับ / assisted rerun C | 3 | 259.816 | 178,089 | 6,984 |
| รวม | **22** | **1,705.804** | **997,119** | **44,430** |

Input + output = **1,041,549 tokens**; cached input 829,312 เป็นส่วนหนึ่งของ input และ reasoning output 3,712 เป็นส่วนหนึ่งของ output ไม่บวกซ้ำ เวลารวมของ calls ไม่ใช่ elapsed time ของการสร้างแพ็กเกจหรือเวลาผู้เรียน ทุก call ใน 22 ครั้ง exit 0; ไม่มี timeout/paid failure ที่แอบ retry ดู [usage JSON](../usage-summary.json)

เฉพาะต้นทุนสาธิต: สร้าง 83.508 วินาที/60,055 tokens; ปรับ 71.123 วินาที/61,392 tokens; rerun C 105.185 วินาที/63,626 tokens ไม่รวมในผลเปรียบเทียบหลัก เวลาเตรียมไฟล์อัตโนมัติแยกใน [launcher checks](launcher-prepare-checks.json); เวลา setup/maintenance ของมนุษย์ = not-measured

มี [metadata งานจัดตารางประกอบที่ parent เพิ่ม](orders-packaging-usage.json) แยกต่างหาก ระบุ input 75,120 + output 2,147 = 77,267 tokens ของงาน authoring ซึ่งไม่ใช่ experimental trial; ไม่รวมในยอด 22 calls ที่มี raw trial logs และไม่ได้รับรอง trace เต็มของรายการนั้นในรายงานนี้

## ผลที่ควรใช้สอนและข้อจำกัด

Lab1/2 ได้ 12/12 ทั้งสองวิธี Lab1 ฝั่ง Skill มีคำต่างภาษาปนในร่างจริงและ C จึงยังต้องตรวจภาษา Lab3 ตาม key เดิม P=10/12 และ S=11/12 แต่เกณฑ์ความเสี่ยง/ข้อมูลขาดทับกัน เมื่อวิเคราะห์ sensitivity หลังเห็นผลอย่างเท่าเทียม ทั้งสองวิธีได้ 12/12 ไม่มีหลักฐานจาก pilot นี้ให้ตั้งผู้ชนะทั่วไป

สี่รอบ S เดิมไม่แสดง read-event จึงเก็บเป็น native-unverified แล้วทำสี่รอบยืนยันเพิ่มอย่างเปิดเผย S-confirmed จึงมีลำดับและคำสั่งอ่านไฟล์เพิ่ม ซึ่งกระทบการเปรียบเทียบเวลาและ tokens แม้ขั้นตอนหลักเท่ากัน AI Lab2 วินิจฉัยจากข้อมูลสถานะ ส่วนการกู้ผ่าน browser เป็น automated runtime test แยกกัน

ผลนี้เป็น **technical pilot ไม่ใช่ human classroom study** คะแนนเป็นผู้จัดทำ AI worker อ่านเทียบแหล่ง/รูบริก ไม่ใช่ผู้ประเมินมนุษย์อิสระ ความแม่นยำทุกข้ออ้าง เวลา/คำใบ้/จำนวนการแก้ไขของมนุษย์ยัง not-measured บริบทแยกมี audit แต่ไม่ใช่ OS sandbox; ทดสอบ Linux/Chromium ตามรุ่นระบุเท่านั้น ส่วน `$`/`/skills` TUI อ้าง docs แต่เส้นทางที่ลงมือยืนยันคือ launcher/native exec รายละเอียด PASS/UNVERIFIED/LIMIT อยู่ใน [verification](../../verification.html)
