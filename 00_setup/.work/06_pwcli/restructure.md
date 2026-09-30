# งานรอบใหม่: เรียบเรียง 06_Playwright_CLI_Trip ใหม่ทั้งหมดให้เข้าใจง่าย

ROOT=/root/workspace/CWN/Teaching/00_setup · WORK=$ROOT/.work/06_pwcli · OUT=$ROOT/06_Playwright_CLI_Trip
- เวอร์ชันเดิม backup แล้วที่ $ROOT/backup/06_Playwright_CLI_Trip_v1_2026-09-30 (ห้ามแก้ backup)
- ได้รับอนุญาตให้เขียน README.md ใหม่ทั้งไฟล์ และจัด img/ log/ ใหม่ได้ (ของเดิมอยู่ใน backup)
- brief.md + addendum.md (ข้อ 1–11) ยังใช้ทั้งหมด ไฟล์นี้คือ "ฉบับรวม + โครงใหม่" ถ้าขัดกันให้ยึดไฟล์นี้
- ใช้ของจริงที่ทำไว้แล้วได้ (agent.py, log/steps 01–12, guardrail) แต่ถ้าต้องรันใหม่เพื่อให้ได้ compare.png / 4 ช่วงต่อ step ให้รันใหม่
- ไฟล์ทำงานทั้งหมดอยู่ใน WORK; OUT มีแค่ README.md, img/, log/ (น้อยที่สุด, log/ ≤ ~15MB)
- ห้ามแตะ chrome :9222, ห้าม pkill -f กว้าง, ห้ามแสดงค่า .env/token/อีเมล

## หลักการเขียน (สำคัญที่สุด)
- ผู้อ่าน = นักศึกษา: ภาษาไทยง่าย ประโยคสั้น ทีละเรื่อง มีตัวอย่างจริงจากงานนี้ทุกแนวคิด ศัพท์เทคนิคอธิบายครั้งแรกที่ใช้
- ลำดับ "ภาพรวม → ทฤษฎีทีละชั้น → ลงมือทีละ LAB จากง่ายไปยาก" แต่ละ LAB ใช้ของจาก LAB ก่อนหน้า
- ทุก LAB ย่อยเป็น prompt-based: copy พรอมต์ plain text 1 กรอบ ```text ไปวางใน yolo1 (container LAB 03, cwd /workspace) แล้วทำงานได้ทันที
  พรอมต์สั้น กระชับ ครบในตัว (เตรียม alias/config เองถ้ายังไม่มี) บอกไฟล์ output ที่ต้องได้
- ทุก LAB ย่อยมีโครงเดียวกัน: 🎯 เป้าหมาย → 💬 พรอมต์ → 📖 คำอธิบาย (AI ทำอะไรทีละขั้น + ทำไม โยงทฤษฎี) → 🔍 snapshot เทียบหน้าเว็บจริง → ✅ ผลที่ควรได้ + วิธีตรวจ
- 🔍 ทุก LAB ที่ใช้เว็บ: compare.png (ซ้าย screenshot จริง --hires มีกรอบสี+เลข ①②③ จาก [box]; ขวา YAML บรรทัดเดียวกันสี/เลขตรงกัน) + ```yaml ของจริงพร้อม # ①
- ผลที่ควรได้ = output จริง (code block) + ภาพจริง ห้ามแต่ง ห้ามภาพ terminal ปลอม
- ทุกพรอมต์ต้องทดสอบจริงด้วย `yolo2 -p --model sonnet "<พรอมต์>"` ในโฟลเดอร์ scratch ใหม่ใน WORK (จำลอง นศ ไม่มีบริบท) จนผ่าน บันทึกใน WORK/prompt_tests.md

## โครง README ใหม่
0. หัวเรื่อง + ย่อหน้าเดียวว่าจะได้อะไร · ต้องมีก่อน (LAB 03) · เวลา · "แผนที่บทเรียน" ตาราง ส่วน/LAB → ได้เรียนอะไร → ไฟล์ที่ได้
   สัญลักษณ์ 💬 🎯 📖 🔍 ✅ อธิบายครั้งเดียว

ส่วน A · ทฤษฎี (แต่ละหัวข้อ: ย่อหน้าสั้น + ภาพ + ตัวอย่างจริง + "จำง่าย" 1 บรรทัด)
 A1 ใครคุมพวงมาลัย? scripted / LLM-in-control / code-in-control — ตารางเทียบ ข้อดี ข้อเสีย ความเสี่ยง เมื่อไรใช้  [img concept-09]
 A2 สามส่วนสามหน้าที่: CLI = ตาและมือ, LLM = ผู้ตัดสินใจ, โค้ด = ผู้คุม  [concept-01]
 A3 ตาของ agent: DOM/selector vs screenshot+vision vs accessibility tree; accessibility snapshot คืออะไร สร้างจาก DOM+ARIA อ่าน YAML อย่างไร [concept-03]
     กล่องอธิบายเทคนิค: role / name / state&value / ref (รูปแบบ f1e21 — อธิบายตามที่ทดลองพิสูจน์แล้วเท่านั้น) / box (css px, ภาพ hires ×2)
 A4 ref ใช้ได้กับ snapshot ล่าสุดเท่านั้น  [concept-04]
 A5 Loop Observe → Decide → Act → Verify (verify ด้วยโค้ด ไม่เชื่อคำพูด LLM)  [concept-02]
 A6 การตัดสินใจ: prompt plain text → JSON schema ตายตัว (--json-schema), ตัด snapshot ให้สั้น (token budget)  [concept-06, concept-10]
 A7 Guardrail อยู่ในโค้ด: allowlist, denylist, ref ต้องมีจริง, max steps, fail-closed, prompt injection จากเนื้อหาเว็บ  [concept-05]
 A8 หลักฐาน: log/steps/NN/ + วงกลมแดงบนหน้าจริงทำอย่างไร  [concept-08, concept-11]
 A9 เว็บจริงพังได้อย่างไร (UI เปลี่ยน, dropdown/async, consent, CAPTCHA → หยุดและรายงาน ไม่เลี่ยง) + จริยธรรม (ToS, ไม่ทำธุรกรรมแทนคน, ไม่เดาข้อมูล)
 A10 คำสั่ง playwright-cli ที่ใช้ในบทนี้ (ตารางสั้น: คำสั่ง · ทำอะไร · ตัวอย่างที่ตรวจแล้ว) + session/daemon, config, headless/headed

ส่วน B · LAB ย่อย (ง่าย → ยาก)
 LAB 1 เตรียม playwright-cli (alias + .playwright/cli.config.json: chromiumSandbox false ฯลฯ) → ตรวจ --version / open example.com
 LAB 2 "ตา": เปิด Google Flights แล้ว snapshot --boxes → compare.png เทียบหน้าเว็บจริงกับ YAML, find, partial snapshot
 LAB 3 "มือ": ใช้ ref กด One way / fill ต้นทาง แล้ว snapshot ใหม่ verify (ทำด้วยคำสั่ง CLI ผ่าน AI ทีละคำสั่ง ยังไม่มี LLM ตัดสินใจ)
 LAB 4 ref เก่าใช้ไม่ได้: ใช้ ref จาก snapshot เก่าหลังหน้าเปลี่ยน → error จริง → snapshot ใหม่แล้วผ่าน
 LAB 5 "ผู้ตัดสินใจ" 1 ครั้ง: โค้ดส่ง prompt.txt (plain text) + snapshot ที่ตัดแล้ว ให้ LLM → decision.json → validate → act → verify (1 step ครบ 4 ช่วง)
 LAB 6 agent เต็ม code-in-control: One way BKK → Tokyo, Japan, Economy, 1 ผู้ใหญ่, วันที่ 15 ของเดือนถัดไป (คำนวณในโค้ด print ลง log)  [concept-07]
       เดินดูทีละ step ทุก step (ห้ามรวบ): หัวข้อย่อยต่อ step มี ① Observe (คำสั่ง + ตัดตอน YAML) ② Decide (ตัดตอน prompt.txt + decision.json)
       ③ Validate→Act (ผลตรวจ ✓/✗ ทีละข้อ + คำสั่ง CLI จริง + page.png วงกลมแดง+callout) ④ Verify (บรรทัด snapshot ใหม่ที่พิสูจน์ + ref เก่าหมดอายุ)
       แต่ละช่วงมีคำอธิบายภาษาไทยสั้น "เกิดอะไรขึ้น/ทำไม"; ตาราง 3 อันดับเที่ยวบินคัดจาก snapshot พร้อม ref/บรรทัดที่มา (ห้ามเดาราคา)
 LAB 7 ทดสอบ guardrail: เป้าหมายหลอก/ข้อความ injection ให้กด Sign in หรือ Book → โค้ดหยุด (decision.json + log จริง)
 LAB 8 Checklist ตรวจผลงานตัวเอง + คำถามทบทวน 5 ข้อ (พร้อมเฉลยพับไว้ <details>)

ส่วน C · ข้อควรรู้ · ปัญหาที่พบบ่อย/วิธีแก้ (จากที่เจอจริง) · คำสั่งที่ใช้บ่อย · อภิธานศัพท์สั้น

## ภาพ
- ภาพแนวคิดชุดสุดท้าย 11 ภาพ (ตรวจแล้ว): WORK/img_gen/v2/concept-01..11-*.png → คัดลอกไป OUT/img/ ชื่อเดิม ใช้ครบทุกภาพตามตำแหน่งข้างบน (ลบ v1 ที่ไม่ใช้)
- ภาพจริง: OUT/img/labN-*.png (compare/page) และ log/steps/NN_*/page.png; บีบอัด PNG แต่ยังคม
- เปิดดูทุกภาพที่ใส่ก่อนส่ง (callout ไม่บังเป้าหมาย, วงกลมตรง element)

## ส่งมอบ
สรุปสั้น: โครงสร้าง OUT + ขนาด, ผล prompt_tests (LAB ไหนผ่าน/แก้อะไร), วันที่ที่คำนวณได้, 3 อันดับเที่ยวบิน (ตามจริง), สิ่งที่ยังค้าง
ลบภาพ/ไฟล์ใน OUT ที่ README ไม่อ้างถึง; ปิด browser ของ playwright-cli เมื่อเสร็จ (ไม่ปิด Xvfb/x11vnc/websockify)
