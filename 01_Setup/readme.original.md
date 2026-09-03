# Master Prompt — Multi-Account AI CLI Builder

คัดลอกข้อความทั้งหมดในไฟล์นี้ส่งให้ AI coding agent เพื่อให้ตรวจเครื่อง วางแผน สร้างคำสั่ง
และทดสอบระบบ Multi-Account AI CLI สำหรับ Ubuntu หรือ Windows

> **ขอบเขตความปลอดภัย:** ห้ามใส่ API key, password หรือ credential จริงใน prompt นี้
> ขั้นตอน login และกรอก secret ต้องให้เจ้าของบัญชีดำเนินการเอง

---

## Prompt

คุณคือผู้เชี่ยวชาญด้าน DevOps และ AI CLI ให้สร้างระบบสำหรับใช้งาน Claude Code, Codex CLI
และ Qwen Code หลายบัญชีบนเครื่องเดียว โดยทำงานตามขั้นตอนต่อไปนี้

### 1. ตรวจสภาพแวดล้อมก่อนสร้าง

1. ตรวจว่า host เป็น Ubuntu/Linux หรือ Windows/PowerShell
2. ตรวจ shell, architecture, Node.js, npm และเวอร์ชัน CLI ที่ติดตั้งจริง
3. อ่าน `--help` ของ CLI ทุกตัวและตรวจ official docs ล่าสุดก่อนเลือก env, path, endpoint,
   model หรือ permission flag
4. ถ้า docs กับ CLI ที่ติดตั้งไม่ตรงกัน ให้รายงานความต่างและใช้เฉพาะค่าที่พิสูจน์ได้จากเวอร์ชันจริง
5. แสดงแผนและคำสั่งที่จะใช้ก่อนแก้เครื่องจริง

### 2. ตัวแปรตั้งค่ากลาง

ถามผู้ใช้หรือเลือกค่าตามระบบปฏิบัติการ โดยห้าม hard-code path ซ้ำหลายจุด

- Ubuntu ค่าเริ่มต้น: `BASE_PATH=/root/workspace`
- Windows ค่าเริ่มต้น: `$BasePath = "$env:USERPROFILE\workspace"`

ถ้า path ไม่มีอยู่ ให้ถามก่อนสร้างเมื่อการเลือกตำแหน่งอาจกระทบข้อมูลเดิม

### 3. โครงสร้างเป้าหมาย

สร้างโครงสร้างเทียบเท่ากันบนทั้งสองระบบ:

```text
<BASE_PATH>/
├── .Claude/  yolo1..yolo5   + shared/{skills,mcp}
├── .Codex/   cyolo1..cyolo5 + shared/{skills,mcp}
└── .Qwen/    qyolo1..qyolo3 + shared/{skills,mcp}
```

คำสั่งเป้าหมาย:

- `yolo1` ถึง `yolo5` เรียก Claude Code ด้วย Anthropic account แยกกัน
- `cyolo1` ถึง `cyolo5` เรียก Codex CLI ด้วย OpenAI account แยกกัน
- `qyolo1` ถึง `qyolo3` เรียก Qwen Code โดยตรงด้วย QwenCloud account แยกกัน

### 4. กฎ Isolation

1. ทุก account ต้องแยก credential, config, session, history และ cache เปิดพร้อมกันแล้วไม่ชน
2. ห้ามเปลี่ยน `$HOME` บน Linux และห้ามเปลี่ยน `$env:USERPROFILE` บน Windows
3. ใช้ config-root mechanism อย่างเป็นทางการของ CLI เท่านั้น เช่น `CLAUDE_CONFIG_DIR` และ
   `CODEX_HOME`; สำหรับ Qwen ให้ยืนยันจาก official docs และ `qwen --help` ของรุ่นจริง
4. ถ้า CLI ใดไม่รองรับการแยกบางส่วนอย่างเป็นทางการ ให้หยุดส่วนนั้นและเขียนข้อจำกัดชัดเจน
5. ห้ามแก้ shell profile, Git config, SSH config หรือ project environment เดิมโดยไม่จำเป็น

### 5. Wrapper commands

สร้าง wrapper ตามระบบปฏิบัติการ:

- Ubuntu: executable Bash scripts และใช้ `exec` กับ `"$@"`
- Windows: PowerShell scripts/functions และส่งต่อ argument ด้วย `@args`

Wrapper ทุกตัวต้องตั้ง config root เฉพาะ process ของตัวเอง ห้ามตั้ง env แบบ global
และต้องรองรับ `--version` รวมถึง argument อื่นครบถ้วน

permission/approval bypass flag ต้องตรวจจาก `--help` ของเวอร์ชันจริงก่อนใช้ พร้อมเตือนว่า
โหมด skip permission เหมาะเฉพาะ sandbox หรืองานที่ควบคุมได้

### 6. Qwen credential

ครั้งแรกที่เรียก `qyoloN` ให้ผู้ใช้เลือก plan จากตัวเลือกที่ official docs รองรับ แล้วรับ API key
แบบซ่อนตัวอักษร โดย endpoint, credential variable และ default model ต้องตรงกับ plan

- ห้ามฝัง key ใน source, template, command-line argument, log หรือ process list
- เก็บ credential แยกต่อ account ด้วยสิทธิ์เจ้าของเท่านั้น (`600` บน Linux หรือ ACL เฉพาะผู้ใช้บน Windows)
- ห้ามพิมพ์ค่า secret ออกหน้าจอ
- ให้เจ้าของ credential เป็นผู้กรอกเอง

### 7. Shared Skills และ MCP

แต่ละ CLI ใช้ `<tool>/shared` เป็น source เดียว แก้ครั้งเดียวแล้วทุก account ของ CLI นั้นเห็น

- Skills ใช้ symlink/junction หรือ official discovery mechanism
- MCP ใช้ config include ถ้ารองรับ มิฉะนั้นใช้การ sync ที่ตรวจสอบได้
- ระบุข้อจำกัดของแต่ละ CLI ตามจริง

### 8. Installer

สร้าง installer แยกตาม OS หรือสร้างตัวเดียวที่ตรวจ OS ได้ โดยต้อง:

1. รันซ้ำได้โดยไม่ลบหรือเขียนทับ credential/config เดิม
2. มี `--dry-run` หรือโหมด preview ที่ไม่เปลี่ยนแปลงเครื่อง
3. ตรวจ dependency และแสดงสิ่งที่ขาด
4. สร้าง generated wrapper ใหม่ได้ แต่ต้องสำรองไฟล์เดิมที่ผู้ใช้แก้เอง
5. ไม่ติดตั้ง package จากอินเทอร์เน็ตจนกว่าผู้ใช้จะอนุมัติ

### 9. ทดสอบในพื้นที่แยกก่อนใช้จริง

ห้ามเริ่มด้วย credential จริง ให้สร้าง test matrix และทดสอบแบบ disposable ก่อน:

- Ubuntu: ใช้ container ใหม่หรือ VM snapshot โดย mount เฉพาะไฟล์ installer ที่ต้องทดสอบ
- Windows: ใช้ Windows Sandbox, disposable VM หรือ test user; ถ้าทดสอบเฉพาะ Bash installer
  สามารถใช้ Linux container ได้ แต่ห้ามอ้างว่าผลนั้นยืนยัน PowerShell/Windows แล้ว
- ปิด network ในการทดสอบโครงสร้างและ dry-run ถ้าไม่จำเป็น
- ใช้ fake placeholder credential เท่านั้น และตรวจว่าค่านั้นไม่ปรากฏใน argument, process list หรือ log
- ลบ container/VM ทดสอบเมื่อจบ โดยไม่แตะ host data

รายงานผลทุกข้อเป็น `PASS`, `FAIL` หรือ `SKIP` ห้ามรายงาน `PASS` หากไม่ได้รันจริง

### 10. ตัวอย่าง Model Routing ที่ต้องส่งมอบ

สร้างตัวอย่าง policy ที่แสดงว่าไม่มี AI agent ตัวเดียวเหมาะกับทุกงาน เช่น:

- งาน Frontend/WebDev เลือก agent จากคะแนนหมวด WebDev ราคา และความเร็ว
- งานวิเคราะห์หรือ code review ความเสี่ยงสูง เลือก agent ที่เด่นด้าน reasoning/verification
- งานปริมาณมากเลือก agent ต้นทุนต่ำ แล้วสุ่มตรวจผลด้วย agent อีกตัว
- งานลูกค้าใช้บัญชีลูกค้าเท่านั้น ไม่ใช้ credential ส่วนตัว

ตัวอย่างเป็น policy สำหรับการสอน ไม่ใช่การรับรองว่าโมเดลใดชนะตลอดไป ต้องบันทึกแหล่งข้อมูล
วันที่ ราคา และช่วงความเชื่อมั่นทุกครั้ง

### 11. รูปแบบผลลัพธ์จาก AI agent

ส่งผลลัพธ์ตามลำดับนี้:

1. Environment report และข้อจำกัด
2. แผนผัง directory/config/credential
3. Dry-run plan
4. Installer และ wrapper สำหรับ OS ที่ตรวจพบ
5. คำสั่งทดสอบใน container/sandbox/VM
6. Test report แบบ PASS/FAIL/SKIP พร้อมหลักฐานที่ไม่เปิดเผย secret
7. วิธี rollback
8. คู่มือ login ที่เว้นให้เจ้าของบัญชีดำเนินการเอง

ก่อนแก้ host จริง ให้หยุดและขออนุมัติหลังแสดง dry-run plan เสมอ
