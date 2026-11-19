# ระยะ B · Planning (รอบสกิล · ยังไม่รันจริง)

แผน `sitesafe-skill` · บัญชี cyolo1, yolo2, yolo3 · agent พร้อมกันสูงสุด 3/3 · ไฟล์ที่ `results/skill_v0_run/plan/` (blocks.json · dag.png · gantt-plan.png · PLAN.md · plan.json)

| เกณฑ์ผ่าน | ผล |
|---|---|
| dag ไม่มี ERROR | ✔ OK 10 บล็อก |
| บัญชีอยู่ในรายชื่อที่อนุญาต | ✔ yolo2 · yolo3 · cyolo1 |
| agent พร้อมกัน ≤ 3 | ✔ 3/3 |
| Critical Path + เวลารวม | ✔ B01 → B02 → B03 → B08 → B10 · ≈ 60.6 นาที |
| ไม่มีบล็อกเกิน L | ✔ (L 2 บล็อก: B03 · B08) |

บล็อก review: B03 (กฎ BR + API) yolo2 ทำ · cyolo1 ตรวจ · max_rounds 3 · โทเคนประมาณ ≈ 16.2 ล้าน (รวมผู้ตรวจ 0.9 ล้าน)
stop_after = planning → จบที่นี่ (ยังไม่ export/run · ยังไม่เช่าเครื่อง)
