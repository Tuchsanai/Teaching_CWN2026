ใช้ skill typesafe-ai และ Playwright MCP ทำ goal นี้บนเว็บให้สำเร็จ โดยให้ Jev (TypeSafe) เป็นคนตัดสินใจทุกขั้น

- url: https://www.google.com/travel/flights?gl=TH&hl=th
- goal: จอง ตั๋วเครืองบินไปญี่ปุ่นวันที่ 15 เดือนหน้า
- today: 2026-10-01
- โฟลเดอร์เก็บผล: `runs/<วันเวลา>/`
- เรียก Jev: `POST https://api.typesafe.ai/v1/systemone` พร้อม header `Authorization: Bearer $TYPESAFE_API_KEY`

## เริ่มต้น

1. เปิด url ด้วย `browser_navigate`
2. ตั้ง `steps_done` เป็น `["nothing yet"]`

## ทำซ้ำทีละขั้น (สูงสุด 12 ขั้น)

1. **เก็บ snapshot:** เรียก `browser_snapshot` แบบ `boxes: true` แล้วบันทึกเป็น `step_N_snapshot.yml`
2. **เก็บ screenshot:** ถ่ายหน้าจอแล้วบันทึกเป็น `step_N_screenshot.png`
3. **แปลง snapshot เป็น state:**
   - เลือกเฉพาะ element ที่กดหรือพิมพ์ได้ (button, link, tab, option, combobox, textbox, searchbox, checkbox, radio) ที่อยู่ในหน้าจอ, ไม่ disabled และไม่ถูก dialog บัง
   - **วิธีตรวจว่าถูกบัง:** ใช้ `document.elementFromPoint` ที่จุดกึ่งกลางของ element
   - **คำบรรยาย:** เขียนเป็นประโยคเดียวต่อ element เช่น `input field with a suggestion/option list labelled "ปลายทาง"; currently empty; inside search "เที่ยวบิน"; state: active`
   - **dropdown:** combobox ที่กดได้ให้เขียนเป็น `dropdown selector labelled "..." (the label ends with the option currently selected)`
4. **ถาม Jev ครั้งที่ 1:**
   - ส่ง request A (ด้านล่าง) โดยใส่ refs ทั้งหมดใน `elements` และใน `criteria` ของ `next`
   - บันทึก request และ response เป็น `step_N_request.json` และ `step_N_response.json`
5. **วาดรูป:** วาดวงกลมแดงพร้อม label ref บนทุก element ที่ส่งให้ Jev ส่วนตัวที่ Jev เลือกให้วาดเป็นวงเขียวหนา บันทึกเป็น `step_N_refs.png`
6. **ทำตามคำตอบของ `action`:**
   - **`finished` หรือ `stuck`:** หยุด แล้วรายงานผล
   - **`click`:** คลิก element ที่ `next` เลือก
   - **`type`:** ส่ง request B (ด้านล่าง) แล้วพิมพ์คำที่ Jev เลือกลง element นั้น ถ้าได้ `none` ให้หยุด
   - **ถ้า `next` ตอบ `none` แต่ `action` ตอบ `click` หรือ `type`:** ใช้ element ที่ความน่าจะเป็นสูงสุดใน `next`
7. **บันทึกขั้นนี้:** เพิ่มประโยคลงใน `steps_done` เช่น `clicked button labelled "ค้นหา" -> still on the same page` หรือ `-> now on "<ชื่อหน้าใหม่>"` (ดูจากชื่อหน้า)

## Request A: เลือกขั้นถัดไป

```json
{
  "model": "jev-latest",
  "state": {
    "url": "<url ปัจจุบัน>",
    "goal": "จอง ตั๋วเครืองบินไปญี่ปุ่นวันที่ 15 เดือนหน้า",
    "today": "2026-10-01",
    "steps_done": ["nothing yet"],
    "elements": { "<ref>": "<คำบรรยาย>" }
  },
  "questions": {
    "next": {
      "type": "choice",
      "instructions": "I'm on `url` and want to: `goal`. Today is `today`. `steps_done` lists what I have already done. Which element should I use next? Only fill fields my goal gives a value for, and skip fields that are already filled in correctly. Pick a suggestion when the list shows the one I want. For dates, open the date picker and click the exact day my goal means (work out relative dates such as next month from `today`) instead of typing them. If a picker or dialog already shows my choice, confirm it with its done/OK button. Once every field my goal mentions is filled, press search/submit.",
      "criteria": {
        "<ref>": "<คำบรรยาย>",
        "none": "No element should be used next"
      }
    },
    "action": {
      "type": "choice",
      "instructions": "I'm on `url` and want to: `goal`. Today is `today`. `steps_done` lists what I have already done. What should happen next?",
      "criteria": {
        "click": "Click a button, link, tab, option, day or dropdown on this page",
        "type": "Type part of my goal into an input field on this page",
        "finished": "My goal is done: this page already shows the results or content I asked for. A form that is still showing, even fully filled in, is not done; a click in `steps_done` may not have worked, so judge from this page",
        "stuck": "My goal is not done and nothing on this page can move it forward"
      }
    }
  }
}
```

## Request B: เลือกคำที่จะพิมพ์

**ตัวเลือก:** กลุ่มคำ 1–5 คำที่อยู่ติดกันใน goal ตัดมาจาก goal ตรงตัว ภาษาไทยให้ตัดคำด้วย `Intl.Segmenter('th')` ตั้งชื่อตัวเลือกเป็น `v0`, `v1`, ...

```json
{
  "model": "jev-latest",
  "state": {
    "goal": "จอง ตั๋วเครืองบินไปญี่ปุ่นวันที่ 15 เดือนหน้า",
    "field": "<คำบรรยายช่องที่จะพิมพ์>",
    "other_fields": ["<คำบรรยายช่องกรอกอื่นพร้อมค่าปัจจุบัน>"],
    "steps_done": ["..."]
  },
  "questions": {
    "value": {
      "type": "choice",
      "instructions": "I want to: `goal`. Which piece of my goal should I type into `field`? Choose the exact words that belong in that field and nothing extra. Words already used for `other_fields` or in `steps_done` do not belong here. If my goal has no words of the kind this field expects (for example no date for a date field), choose none.",
      "criteria": {
        "v0": "ญี่ปุ่น",
        "v1": "...",
        "none": "My goal says nothing that belongs in this field"
      }
    }
  }
}
```

## กฎ

- **Jev ตัดสินใจทั้งหมด:** Jev เป็นคนเลือกว่าจะทำอะไรต่อและเมื่อไรจะหยุด อย่าตัดสินใจแทน
- **ไม่แต่งข้อความเอง:** ข้อความที่พิมพ์ต้องตัดมาจาก goal เท่านั้น
- **snapshot ใหม่ทุกขั้น:** ref เปลี่ยนเมื่อหน้าเปลี่ยน
- **ห้ามจองหรือจ่ายเงินจริง:** หยุดก่อนถึงหน้าชำระเงินหรือหน้าที่ต้องกรอกข้อมูลส่วนตัว

## รายงานท้ายงาน

- ตารางแต่ละขั้น: ขั้นที่, ref ที่ Jev เลือก, action, confidence, ผลหลังทำ
- goal สำเร็จหรือไม่ พร้อมแสดง `step_N_refs.png` ของขั้นสุดท้าย
- path ของโฟลเดอร์ผลลัพธ์
