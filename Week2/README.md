# Week 2 · แก้ปัญหาการทำงานด้วย AI

**เปรียบเทียบ Prompt ทั่วไปที่มีขั้นตอนครบ กับ Skill ที่นำวิธีทำงานกลับมาใช้ซ้ำ** สำหรับผู้ใช้คอมพิวเตอร์/แชตทั่วไป ไม่ต้องมีพื้นฐานเขียนโปรแกรม System Analysis หรือ DevOps

เริ่มที่ [สไลด์ภาษาไทย](index.html) → เลือก Lab → กรอก [scorecard](scorecard.html) → อ่าน [ผลทดลองและข้อจำกัด](evidence/summary.md)

| บทฝึก | งานที่ผู้เรียนทำ | คู่มือ |
|---|---|---|
| 1 · System Analysis | อ่านแชตและกติกา แยกข้อขัดแย้ง ตั้งคำถาม และตรวจข้อตกลง | [Lab1](001_LAB_System_Analysis/README.html) |
| 2 · DevOps | ดูสถานะ เลือกคำสั่งสำเร็จรูป และตรวจการจองหลังร้านกลับมา | [Lab2](002_LAB_DevOps_Recovery/README.html) |
| 3 · LLM | จัดคิวข้อร้องเรียน ร่างคำตอบตามนโยบาย และส่งต่อคน | [Lab3](003_LAB_LLM_Business/README.html) |

ผู้เรียนวางข้อความ/คำสั่งพร้อมใช้และใช้ Skill เท่านั้น AI หรือผู้สอนเป็นคนสร้างไฟล์ให้ ไม่มีงานเขียนหรือแก้โค้ด สคริปต์ หรือ config

สไลด์ `index.html` เปิดออฟไลน์ได้ด้วยตัวเอง CSS/JS/SVG และภาพประกอบฝังในไฟล์เดียว ไม่มี CDN ส่วนลิงก์ Lab/หลักฐานต้องอยู่กับโฟลเดอร์แพ็กเกจ ใช้ Chrome/Chromium ที่ตรวจแล้วหรือ browser รุ่นปัจจุบันที่รองรับ JavaScript

## โครงสร้างโฟลเดอร์ Lab

```text
Week2/
├── 001_LAB_System_Analysis/
├── 002_LAB_DevOps_Recovery/
└── 003_LAB_LLM_Business/
```


แต่ละโฟลเดอร์ Lab มีไฟล์หลักเพียง `README.md` และ `README.html` เท่านั้น ข้อมูล A/B/C อยู่ในกรอบข้อความภายในไฟล์พร้อมคัดลอก ไม่มีโฟลเดอร์ data แยก ส่วนคู่มือ Prompt, Skill, ใบงาน, คำใบ้ และเฉลยรวมอยู่ใน README เดียวกัน ตารางคำสั่งซื้อของ Lab3 ดาวน์โหลด CSV ได้จากหน้า HTML

## สำหรับผู้สอน

ทำ [setup](instructor/setup.html) ก่อนจับเวลาภารกิจ อ่าน [แผนเปรียบเทียบ](instructor/protocol.html) และ [รายงานตรวจสอบ](verification.html) กำหนดกลุ่ม 1 = P-A → S-B, กลุ่ม 2 = S-A → P-B ให้ทุกฝ่ายได้คู่มือและความช่วยเหลือเท่ากัน

เวลาแนะนำ: ทฤษฎี/สาธิต 30 นาที; Lab1 65 นาที; Lab2 เปรียบเทียบครบ A/B 60 นาที + ถ่ายโอน/อภิปราย 20 นาที (ภารกิจกู้ 30 นาทีต่อชุด ไม่รวม setup); Lab3 65 นาที แบ่งสอนได้หลายคาบ ไม่อ้างว่าแพ็กเกจทั้งหมดจบใน 30 นาที

- [Native Skill ทั้งสาม](.agents/skills) และ [วิธีสร้างด้วยคำขอภาษาคน](instructor/setup.html)
- [แผนผัง Excalidraw แก้ไขได้](diagrams/workflow.excalidraw) · [SVG](diagrams/workflow.svg) · [PNG](diagrams/workflow.png) · [แผนผังแนวตั้งสำหรับมือถือ](diagrams/workflow-mobile.excalidraw)
- [เปิดหลักฐานและข้อมูลดิบ](evidence/index.html) · [หลักฐาน browser](evidence/browser) · [ผลประเมิน](evidence/summary.html)
- [รายงานส่งมอบ](evidence/build/cyolo-completion.md) · [ดาวน์โหลด ZIP พร้อมใช้](Week2-teaching-package.zip)

ผลในแพ็กเกจเป็น technical pilot และการทดสอบบริการอัตโนมัติ ไม่ใช่การศึกษากับผู้เรียนจริง ไม่ตั้งผลว่า Skill ต้องชนะ และไม่ใช้ผลทดลองเก่าจาก Week1 เป็นผลใหม่
