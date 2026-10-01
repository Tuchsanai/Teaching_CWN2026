# Main prompt: เรียกใช้ web_agent_prompt.md

แทนค่า `{{url}}` และ `{{goal}}` แล้วส่งข้อความด้านล่างทั้งหมดให้ agent ที่มี Playwright MCP และ skill typesafe-ai

---

ใช้ skill typesafe-ai และ Playwright MCP ทำ goal นี้บนเว็บให้สำเร็จ

- url: {{url}}
- goal: {{goal}}
- prompt สำหรับ Jev: `web_agent_prompt.md` (ใช้ตามนั้น ห้ามแก้)
- โฟลเดอร์เก็บผล: `runs/<วันเวลา>/`

**เริ่มต้น**
1. เปิด url ด้วย `browser_navigate`
2. ตั้ง `steps_done` เป็น `["nothing yet"]`

**ทำซ้ำทีละขั้น (สูงสุด 12 ขั้น)**

1. **เก็บ snapshot:** เรียก `browser_snapshot` แบบ `boxes: true` แล้วบันทึกเป็น `step_N_snapshot.yml`
2. **เก็บ screenshot:** ถ่ายหน้าจอแล้วบันทึกเป็น `step_N_screenshot.png`
3. **แปลง snapshot เป็น state ของ TypeSafe:**
   - เลือกเฉพาะ element ที่กดหรือพิมพ์ได้, อยู่ในหน้าจอ, ไม่ disabled และไม่ถูกหน้าต่างหรือ dialog บัง
   - เขียนคำบรรยายแต่ละตัวเป็นประโยคเดียว บอกชนิด, ชื่อ, ค่าปัจจุบัน (หรือ "currently empty"), ส่วนของหน้าที่อยู่ และสถานะ
   - state คือ `{ "url", "goal", "steps_done", "elements": { ref: คำบรรยาย } }`
4. **วาดรูป:** วาดวงกลมแดงพร้อม label ref บนทุก element ใน `elements` แล้วบันทึกเป็น `step_N_refs.png` ถ้ารู้ ref ที่ Jev เลือกแล้ว ให้วาดตัวนั้นเป็นวงเขียวหนา
5. **ถาม Jev ครั้งที่ 1:** ใช้คำถามในหัวข้อ `next_step` ของ `web_agent_prompt.md` และเพิ่มทุก ref ลงใน `criteria` ของ `next` บันทึก request และ response เป็น `step_N_request.json` และ `step_N_response.json`
6. **ทำตามคำตอบของ `action`:**
   - `finished` หรือ `stuck`: หยุด แล้วรายงานผล
   - `click`: คลิก element ที่ `next` เลือก
   - `type`: ถาม Jev ครั้งที่ 2 ด้วยหัวข้อ `value` ใช้ state `{ goal, field, other_fields, steps_done }` ตัวเลือกคือกลุ่มคำ 1–5 คำที่ต่อกันใน goal ตัดมาจาก goal ตรงตัว แล้วพิมพ์คำที่ Jev เลือก ถ้าได้ `none` ให้หยุด
   - ถ้า `next` ตอบ `none` แต่ `action` ตอบ `click` หรือ `type` ให้ใช้ element ที่ความน่าจะเป็นสูงสุดใน `next`
7. **บันทึกขั้นนี้:** เพิ่มประโยคลงใน `steps_done` บอกว่าทำอะไร และหลังทำหน้า "still on the same page" หรือ "now on <ชื่อหน้าใหม่>" (ดูจากชื่อหน้า)

**กฎ**
- **Jev ตัดสินใจทั้งหมด:** ให้ Jev เป็นคนเลือกว่าจะทำอะไรต่อและเมื่อไรจะหยุด อย่าตัดสินใจแทน
- **ไม่แต่งข้อความเอง:** ข้อความที่พิมพ์ต้องตัดมาจาก goal เท่านั้น
- **ส่ง Jev ทีละขั้น:** ทุกขั้นต้องใช้ snapshot ใหม่ เพราะ ref เปลี่ยนหลังหน้าเปลี่ยน

**รายงานท้ายงาน**
- ตารางแต่ละขั้น: ขั้นที่, ref ที่ Jev เลือก, action, confidence, ผลหลังทำ
- goal สำเร็จหรือไม่ พร้อมรูป `step_N_refs.png` ของขั้นสุดท้าย
- path ของโฟลเดอร์ผลลัพธ์
