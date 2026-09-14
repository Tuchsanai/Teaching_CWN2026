# การใช้แม่แบบกับชุดสาธิตแยก

ใช้เนื้อหาแม่แบบ `prompts/02-fix-screen.md` ด้านล่างโดยแทนรายการที่ตกด้วย JSON จริงครบทั้ง detail และ US
ข้อกำหนดการแมป path ต่อไปนี้มีลำดับเหนือชื่อ path และข้อห้ามเขียน reference/ ในแม่แบบสำหรับการรันนี้เท่านั้น:
- cwd คือโฟลเดอร์ LAB 004; ห้ามสร้างหรือแก้ work/ ของผู้เรียน
- อ่าน HTML ปัจจุบันและ snapshot ก่อนแก้จาก `reference/demo-fix-path/seed/ui-mockup-broken.html` ซึ่งคงไว้ไม่แก้ไข
- อ่านรอบก่อนจาก `reference/demo-fix-path/round-1/ui-check.json` และภาพใน `reference/demo-fix-path/round-1/shots/`
- อ่านตัวนับการแก้จาก `reference/demo-fix-path/round-2/current-round.txt` ค่า 1 คือการแก้ครั้งแรก; round-1 เป็น baseline และ round-2 เป็นผลหลังแก้ ไม่ใช่แก้ครั้งที่สอง
- work/upstream/ ให้หมายถึง `reference/step-00-input/`; อ่าน input/ui-contract.md, input/mock-data.json และ tests/ui-check.py ตามเดิมได้
- เขียนได้เฉพาะ `reference/demo-fix-path/round-2/ui-mockup-fixed.html` และ `reference/demo-fix-path/round-2/fix-report.md` เท่านั้น
- ใช้ seed เป็นฐานคัดลอกแล้วแก้เฉพาะสาเหตุของ checks ที่ตก ห้ามคัดลอก HTML ผ่านจาก reference/round-1/ หรือ reference/final/ และห้ามอ่าน HTML สองชุดนั้น
- ห้ามแก้ไฟล์อื่นทุกแห่ง รวม README.md, tests/, input/, prompts/, review/, final/, img/ และ log/ผลตรวจ
- ไม่ต้องรันตัวตรวจใน session นี้ ผู้จัดทำจะรันทั้งชุดพร้อม --prev หลังส่งงาน; รายงานสถานะว่า รอตรวจซ้ำ
- ไม่เรียกโมเดลหรือผู้ช่วยเพิ่ม ไม่ใช้ network; ห้ามใส่ชื่อบัญชีจริง path เครื่องจริง หรือรหัสงานภายในในไฟล์และคำตอบ
- คำตอบท้าย session เป็นภาษาไทยสั้น ๆ ระบุจุดที่แก้และสิ่งที่รอตรวจ

ข้อบกพร่องถูกฉีดโดยผู้จัดทำเพื่อสาธิต edge=fix ไม่ใช่ผลของลูปหลัก; ใช้ข้อมูลจำลองเดิมและเก็บต้นฉบับไว้

---

# ขั้น 4.3 — แก้เฉพาะหน้าจอที่ตก

## บริบทและ Input
คุณเป็นผู้แก้ UI ของครัวคุณยาย เริ่ม session ใหม่จากโฟลเดอร์ LAB 004
อ่าน work/ui-mockup.html, work/current-round.txt, JSON รอบก่อนใน work/, input/ui-contract.md, input/mock-data.json และ work/upstream/
รายการจากตัวตรวจที่ต้องแก้ (แทนช่องนี้ด้วย JSON จริงก่อนรัน):
[
  {
    "id": "option-price",
    "us": [
      "US-04"
    ],
    "passed": false,
    "detail": "AssertionError: Locator expected to contain text '60'\nActual value: 50 บาท \nCall log:\n  - Expect \"to_contain_text\" with timeout 2500ms\n  - waiting for get_by_test_id(\"item-total\")\n    9 × locator resolved to <strong class=\"amount\" data-testid=\"item-total\">50 บาท</strong>\n      - unexpected value \"50 บาท\"\n\nAria snapshot:\n- strong: 50 บาท"
  },
  {
    "id": "promptpay-slip",
    "us": [
      "US-08",
      "US-15"
    ],
    "passed": false,
    "detail": "TimeoutError: Locator.click: Timeout 2500ms exceeded.\nCall log:\n  - waiting for get_by_test_id(\"front-orders\").locator(\"[data-order-id=\\\"1\\\"]\").get_by_test_id(\"btn-confirm-slip\")\n    - locator resolved to <button disabled data-id=\"1\" data-action=\"confirm-slip\" data-testid=\"btn-confirm-slip\">ยืนยันสลิปจำลอง</button>\n  - attempting click action\n    2 × waiting for element to be visible, enabled and stable\n      - element is not enabled\n    - retrying click action\n    - waiting 20ms\n    2 × waiting for element to be visible, enabled and stable\n      - element is not enabled\n    - retrying click action\n      - waiting 100ms\n    5 × waiting for element to be visible, enabled and stable\n      - element is not enabled\n    - retrying click action\n      - waiting 500ms\n"
  }
]
## งาน
จับคู่ check ID → US → หน้าจอ → สาเหตุจาก detail และ screenshot ของรอบก่อน
แก้เฉพาะหน้าจอ/ฟังก์ชันที่ทำให้ข้อในรายการตก ห้ามแตะส่วนที่ผ่าน ห้ามจัดหน้าใหม่ทั้งไฟล์
หากปัญหาอยู่ใน shared state ให้ระบุผลกระทบต่อหน้าจอที่ผ่านก่อน; ถ้าซ่อมแบบจำกัดขอบเขตไม่ได้ ให้รายงาน BLOCKED แทนขยายงานเอง
เก็บ data-testid, mock seed และกฎธุรกิจเดิมทุกข้อ; ห้าม hardcode ให้ผ่านตาม check โดยไม่ทำพฤติกรรม
## ข้อจำกัด
ห้ามแก้ tests/, input/, prompts/, work/upstream/, reference/ หรือ img/ และห้ามลบหลักฐานก่อนแก้
ไม่แก้ถ้า JSON ก่อนหน้า edge=cancel หรือ pass; ถ้าแก้ครบ 3 รอบแล้วให้หยุดและรายงานยกเลิก
ไม่ข้ามข้อที่เคยผ่านในการตรวจซ้ำ; ห้ามเปลี่ยน failed เป็น passed เองหรือสรุปผลก่อนรัน
## Output และตำแหน่งบันทึก
แก้ work/ui-mockup.html หลังตรวจว่ามี snapshot work/ui-before-round-N.html แล้ว โดย N อ่านจาก work/current-round.txt
เขียน work/fix-report-round-N.md: check ID, หน้าจอ, สาเหตุ, จุดแก้, ส่วนที่คงไว้, regression ที่ต้องตรวจ และข้อค้าง
หาก placeholder ยังไม่แทนหรือไม่มี snapshot ให้หยุดพร้อมเหตุ; ให้ผู้เรียนรัน tests/ui-check.py ทั้งชุดเป็นผู้ตัดสิน
