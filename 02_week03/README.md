# Week 03 · Reverse Engineer ANYTHING (REA)

ให้ AI "สืบ" เว็บที่มีอยู่จริง (Google Flights: กรุงเทพ → ญี่ปุ่น) แล้วสร้างแอปจองตั๋วของเราเอง (Next.js + PostgreSQL ใน Docker) ทุกอย่างรันใน container `multi-account-devtool` (`yolo1–3` · `cyolo1–2` · REA MCP · Playwright) ผู้เรียนแค่ copy พรอมต์ไปวางใน Claude Code Desktop

แต่ละบทเพิ่มเครื่องมือ แล้ว **วัดผลด้วย Playwright** ว่าแอปที่ได้ดีขึ้นจริงไหม

| บท | หัวข้อ | เครื่องมือที่เพิ่ม | แอปที่ได้ | ผลวัดจริง |
|---|---|---|---|---|
| [01_REA_Basics_Flight](01_REA_Basics_Flight/README.md) | ทฤษฎี REA แบบละเอียด + ติดตั้งใน container + เดโม | REA อย่างเดียว | **SkyThai Mini** (v1) · :5081 | playlist ผ่าน 5/5 |
| [02_REA_Playwright_Exploration](02_REA_Playwright_Exploration/README.md) | สำรวจเว็บแบบ EXPLORATION (A–E) | + Playwright MCP | **SkyThai Plus** (v2) · :5082 | ชุดเทียบของบท: v1 4/35 (11.4%) → v2 33/35 (94.3%) |
| [03_REA_Toolchain_Loop](03_REA_Toolchain_Loop/README.md) | ปิดวงจรโคลน | + HAR · trace/GIF · กรรมการอิสระ (Codex) · วนแก้ · visual diff | **SkyThai Pro** (v3) · :5083 | กรรมการ 82 ข้อ: v1 0 · v2 51 (62%) · v3 74 (90%) · เที่ยวบิน 22 → 300 |
| [04_REA_Differential_Oracle](04_REA_Differential_Oracle/README.md) | ใช้ต้นฉบับเป็นเฉลย | + ต้นฉบับแช่แข็งจาก HAR · differential testing · เทียบโครงสร้าง (ariaSnapshot) · mutation testing · แก้แบบรุม (swarm) | **SkyThai Max** (v4) · :5084 | differential v3 4/8 → **v4 8/8** · โครงสร้าง 70.5% → **78.6%** · visual diff 8.32% → **5.13%** |

### ภาพรวมผลวัดทุกเวอร์ชัน (รันจริง · ชุดทดสอบเดียวกัน)

| เวอร์ชัน | acceptance 82 ข้อ (กรรมการ cyolo1) | differential 8 สถานการณ์ (เทียบต้นฉบับแช่แข็ง) | โครงสร้างหน้า (ariaSnapshot) | visual diff (ต่ำ = ใกล้) | เที่ยวบิน |
|---|---:|---:|---:|---:|---:|
| v1 Mini · REA | 0/82 | 0/8 | 3.8% | 27.88% | 22 |
| v2 Plus · + Playwright | 51/82 | 3/8 | 55.8% | 8.19% | 22 |
| v3 Pro · + HAR · กรรมการ · วนแก้ | 74/82 | 4/8 | 70.5% | 8.32% | 300 |
| v4 Max · + ต้นฉบับแช่แข็ง · differential · swarm | 74/82 | **8/8** | **78.6%** | **5.13%** | 300 |

**ต้องมีก่อน:** [LAB 03 container](../01_week02/03_MultiAccount_Container/) (เปิดด้วย `/maccount`) · [LAB 04 shared skills](../01_week02/04_Skill_Setup/00_Setup_Skill/readme.md) · Docker Desktop · Claude Code Desktop

> ⚠️ เราสืบเว็บของคนอื่นเพื่อ **เรียนรู้แนวคิด** เท่านั้น: ไม่ล็อกอิน ไม่จ่ายเงิน ไม่ข้าม CAPTCHA ไม่ลอกโลโก้/โค้ด/แบรนด์ ไฟล์ HAR/trace มี cookie ห้ามนำออกนอก container · ราคาในแอปเป็นข้อมูลจำลอง ณ 31 ต.ค. 2569
