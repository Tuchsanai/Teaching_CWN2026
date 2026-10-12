// แถวคะแนนตาม EXAM.md / EXAM-B.md / EXAM-KEY §10 · kind auto = เครื่องตรวจ · teacher = ผู้สอนกรอก
export function rubric(set) {
  const R = [];
  const add = (item, key, label, max, kind = "auto") => R.push({ item, key, label, max, kind, score: kind === "auto" ? 0 : null, detail: "" });
  add(1, "q1", "Q1.json ข้อละ 0.8 (ไฟล์ถูก + คำตอบ/ชื่อถูก)", 8);
  add(1, "q1-teacher", "ปรับเฉพาะกรณี: path ถูกแต่คำตอบไม่ครบ ให้ครึ่ง (0.4)", 0, "teacher");
  add(2, "gate", "บังคับ: golden ของ EX2 รันกับระบบตั้งต้น exit 0 (ไม่ผ่าน = ข้อนี้ 0)", 0);
  for (const m of set === "A" ? ["M2", "M3", "M4", "M7"] : ["M1", "M6", "M8", "M9"]) add(2, m.toLowerCase(), `จับ mutant ${m} ได้ (exit ≠ 0)`, 3);
  add(2, "readme", "tests/exam2/README.md วิธีรัน · ที่มาของค่า · ฟิลด์ที่ตัด", 2, "teacher");
  add(3, "impact", "IMPACT.md พบจุดที่ต้องแตะ (recall × 6 ปัดลงครึ่ง)", 6);
  add(3, "proof", "ความเสี่ยงมีวิธีพิสูจน์ที่รันได้", 2, "teacher");
  add(4, "hidden", "hidden test ตาม VARIANT", 7);
  add(4, "cr", "check-rules.mjs ของ EX4 ผ่านทั้งหมด", 1);
  add(4, "cases", "เคสที่แก้ใน EX4 = เคสที่กฎกระทบจริง (ไม่ขาด ไม่เกิน)", 1);
  add(4, "oracle", "ทุกเคสที่แก้ใน EX4 มีแถว ORACLE-CHANGES อ้างข้อ 4", 1);
  add(4, "const", "ค่าคงที่จุดเดียว ไม่ hardcode ซ้ำ · ข้อความครบ", 2, "teacher");
  if (set === "A") {
    add(5, "hidden-api", "hidden test ฝั่ง API (+ ไม่ติ๊กรถ)", 4);
    add(5, "hidden-ui", "hidden test หน้าจอ (Playwright)", 3);
  } else {
    add(5, "hidden-api", "hidden test API (ขอบเวลา completeAfterMin · ของเดิม)", 4.5);
    add(5, "hidden-ui", "hidden test หน้าตารางคิว (ปุ่ม disabled/enabled)", 1.5);
    add(5, "evidence", "EX5-EVIDENCE.json ตรงกับที่เครื่องตรวจทำซ้ำบนระบบตั้งต้น", 1);
  }
  add(5, "cr", "check-rules.mjs ของ EX5 ผ่านทั้งหมด", 1);
  add(5, "legacy", set === "A" ? "เทสต์เดิมที่เปลี่ยนสถานะ (TC-TRN-03) ทำถูกวิธี + ORACLE ข้อ 5" : "เทสต์เดิมเปลี่ยนเฉพาะการเตรียมสถานการณ์ (E39 E40 E88 TC-MEM-04) + ORACLE ข้อ 5", 1);
  add(5, "red", "commit EX5-red แดงจริงบนโค้ดเดิม และเขียวที่ EX5", 1);
  add(5, "bugfix", "BUGFIX.md ต้นเหตุ · กฎที่ขัด · ผลข้างเคียง/เหตุที่ไม่มีใครจับได้", 2, "teacher");
  add(6, "mig", "① migration รัน 2 ครั้งบนฐานที่มีข้อมูล ไม่ error", 2);
  add(6, "data", "① ข้อมูลเดิมอยู่ครบ (ลูกค้า 10 · นัด 18 · นัดของข้อมูลจริง)", 2);
  add(6, "s2", set === "A" ? "② ลูกค้าไม่เห็น/จองไม่ได้ทุกช่องทาง" : "② คิวว่างไม่นับคนที่ลา", 2);
  add(6, "s3", set === "A" ? "③ ระบบแนะนำทุกตัวไม่แนะนำ S03" : "③ จองระบุคนที่ลา → 409", 2);
  add(6, "s4", set === "A" ? "④ เจ้าของร้านเปิด/ปิดได้" : "④ จัดคนอัตโนมัติข้ามคนที่ลา", 2);
  add(6, "s5", "⑤ ติดตั้งใหม่ / reset ได้ผลเดียวกัน", 2);
  add(6, "cr", "⑥ check-rules (HEAD) ผ่านบนฐานที่ migrate แล้ว", 2);
  add(6, "rollback", "ไฟล์ถอยกลับใช้ได้จริงตามที่เขียน · MIGRATION.md บอกข้อมูลที่จะหาย", 2, "teacher");
  add(7, "api", "hidden test ฝั่ง API", 10);
  add(7, "ui", "hidden test ฝั่งหน้าจอ (Playwright)", 3);
  add(7, "cr", "check-rules.mjs ของ EX7 ผ่านทั้งหมด", 1);
  add(7, "own", "เทสต์ของผู้สอบเอง (ไฟล์ที่เพิ่มใน EX7) รันผ่านบนโค้ดของผู้สอบ", 1);
  add(7, "steps", "แตกงานเป็นขั้นชัด · ไม่ทำลายกฎเดิม", 3, "teacher");
  add(8, "regr", "ตัวเลขใน REGRESSION.md ตรงกับที่เครื่องตรวจรันได้", 3);
  add(8, "oracle", "ทุกเคสที่เปลี่ยนตั้งแต่ EX0 มีใน ORACLE-CHANGES และอ้างข้อ 4–7", 2);
  add(8, "golden", "golden ข้อ 2 (ฉบับ HEAD) ผ่านบนโค้ดสุดท้าย", 2);
  add(8, "smoke", "smoke.mjs ผ่านบนระบบของเรา · ไม่ผ่านบนระบบตั้งต้น · ไม่เปลี่ยนข้อมูล", 2);
  add(8, "notes", "release notes ภาษาคน · ปัญหาที่ยังเหลือ · ขั้นตอนขึ้นระบบปลอดภัย", 3, "teacher");
  return R;
}
export const ITEM_MAX = { 1: 8, 2: 14, 3: 8, 4: 12, 5: 12, 6: 16, 7: 18, 8: 12 };
