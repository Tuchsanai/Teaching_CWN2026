# ให้ AI สร้างและปรับ Skill — หลักฐานจาก launcher จริง

ทั้งสามขั้นใช้ `./learn run ask` รับข้อความภาษาคน แล้ว launcher เรียก `cyolo1 exec -m gpt-6-astra -c model_reasoning_effort="high"` พร้อม -o ไฟล์จริงและ stdin=/dev/null บริบท exec ใหม่ทุกครั้ง ไม่มีผู้เรียนเขียนไฟล์หรือแก้โค้ด

| ขั้น | หลักฐาน | สิ่งที่เกิดขึ้นจริง |
|---|---|---|
| สร้าง | [Prompt](create/prompt.txt) · [คำตอบ](create/answer.md) · [Skill](create/SKILL.md) · [JSONL](create/events.jsonl) · [metadata](create/metadata.json) | file_change เพิ่ม .agents/skills/complaint-desk/SKILL.md เพียงไฟล์เดียว |
| ปรับ | [Prompt](improve/prompt.txt) · [คำตอบ](improve/answer.md) · [Skill](improve/SKILL.md) · [diff](skill-improvement.diff) · [metadata](improve/metadata.json) | เพิ่มตรวจรุ่น/ขอบเขตทุกครั้ง ไม่ hard-code วัน และระบุระดับชั่วคราวเมื่อคิวทับกัน |
| เรียก Skill ใหม่ทำ C | [Prompt](rerun-C/prompt.txt) · [คำตอบดิบ](rerun-C/answer.md) · [JSONL](rerun-C/events.jsonl) · [metadata](rerun-C/metadata.json) | ใช้ $complaint-desk และมี cat .agents/skills/complaint-desk/SKILL.md exit 0 ตามด้วย input/manual เท่านั้น |

ไฟล์ create และ improve ผ่าน quick_validate.py ทั้งคู่ ไม่มี scripts หรือคำตอบเฉพาะชุด C ฝังใน Skill ลิงก์ /tmp ที่โมเดลให้ในคำตอบดิบเป็น path ตอนทดลองซึ่งปิดแล้ว ใช้สำเนา SKILL.md ในตารางเพื่ออ่านไฟล์ที่เก็บรักษาไว้

ตัวอย่าง flawed v1 เรื่อง “7 วัน/ห้ามเปลี่ยนใจเสมอ” ในคำขอปรับถูกติดป้ายชัดว่าเป็นตัวอย่างผู้สอนแต่ง ไม่ใช่ความผิดจริงของ Skill ที่เพิ่งสร้าง ตัวอย่างนี้สาธิตวิธีสั่งปรับด้วยภาษาคน ส่วนความกำกวมคิวเป็นประเด็นจริงจาก pilot

ผล C หลังปรับ: ผ่าน 4/4 ด้านขอบเขตใหม่ การตัดสินตาม v2 การขอข้อมูล/ส่งคน และการไม่อนุมัติเอง แยกข้อเท็จจริงจากการประเมินใน M2 และถามผู้มีอำนาจว่าควรใช้ P2 หรือ P3 แต่มีคำถามเพิ่มเรื่องวันที่ปฏิทิน/จุดเริ่มนับที่อาจเพิ่มภาระ ผู้สอนควรทบทวนความจำเป็น เพราะ C-P1 ระบุขอบเขตว่ามีผลกับชุด C อยู่แล้ว การปรับ Skill ไม่รับประกันว่างานจะสั้นหรือสะดวกขึ้น

เป็น assisted demonstration หลังเห็นข้อมูล/เกณฑ์แล้ว ไม่รวมกับการเปรียบเทียบ A/B หรือ frozen transfer C การตรวจคะแนนเป็นผู้จัดทำ AI worker ยังไม่มีผู้ประเมินมนุษย์อิสระ
