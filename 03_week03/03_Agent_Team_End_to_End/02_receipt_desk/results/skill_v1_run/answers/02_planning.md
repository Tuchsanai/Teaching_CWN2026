# ระยะ B · Planning + What-if (ไม่รันทีม)

แผน `receiptdesk-skill` · 14 บล็อก (cyolo 6 · yolo 4 · review 1 · debate 1 · best_of 1 · image 1) · `dag` ไม่มี ERROR
ไฟล์: `results/skill_v1_run/plan/` (blocks.json · dag.png · gantt-plan.png · PLAN.md · plan.json · dag.json) · What-if: `plan/whatif/`

## What-if 3 แผน (blocks.json เดียวกัน md5 `88f43bf9…` ก่อน/หลังตรงกันทั้ง 3)

| แผน | บัญชี · agent | วางได้ | เวลา | Critical Path | บัญชีที่หนักสุด | บล็อกที่วางไม่ได้ |
|---|---|---|---|---|---|---|
| **receiptdesk-skill** (แนะนำ) | yolo1-3 + cyolo1 · 4 | **14/14** | **≈ 53.8 นาที** | B01 → B02 → B04 → B11 → B14 | cyolo1 (10 บทบาท) | – |
| receiptdesk-skill-2 | yolo1-3 + cyolo1 · 2 | 7/14 | นับแค่ 7 บล็อก ยังไม่เสร็จ (32.8 นาที) | เดิม แต่ B14 วางไม่ได้ | cyolo1 (5) | B03 debate · B12 best_of (ต้อง 3 agent) → ติดตามทอด B05 B06 B07 B08 B14 |
| receiptdesk-skill-nocodex | yolo1-3 · 4 | 0/14 | นับแค่ 0 บล็อก ยังไม่เสร็จ | – | – | B01 cyolo · B13 image ไม่มี Codex → ทุกบล็อกติดตามทอด |

แนะนำ **receiptdesk-skill (4 agent · 4 บัญชี)**: แผนเดียวที่วางได้ครบ · debate/best_of ต้องใช้ 3 agent พร้อมกัน · บล็อกแรกเป็น cyolo จึงต้องมี Codex
ข้อสังเกต: cyolo1 รับ 10 บทบาท (คอขวด) และ B12 best_of ต้องรอ slot agent จนนาทีที่ 31.3 ทำให้จบที่ 53.8 นาที แม้สายวิกฤตตาม rank (…B11) จะจบที่ 31.5 นาที

โทเคนที่จองโควตาตามแผน ≈ 24.9 ล้าน (ขนาดบล็อก 21.3 ล้าน + บทบาทผู้ตรวจ/ผู้ตอบที่ 2/ผู้ตัดสิน) · ต่อบัญชีใช้ 5 ชม. ไม่เกิน ~8% ต่อบล็อก

| เกณฑ์ผ่านระยะ B | ผล |
|---|---|
| `dag` ไม่มี ERROR | ผ่าน |
| วางได้ครบทุกบล็อกในแผนที่แนะนำ | ผ่าน 14/14 |
| ทุกบล็อกใช้บัญชีที่อนุญาต | ผ่าน (yolo1 yolo2 yolo3 cyolo1) |
| agent พร้อมกัน ≤ 4 | ผ่าน (สูงสุด 4/4) |
| มี Critical Path + เวลารวม | ผ่าน |
| ตาราง What-if 3 แผน + md5 ไม่เปลี่ยน | ผ่าน |

`stop_after=planning` → จบที่นี่ ไม่ export/run ทีม ไม่เช่าเครื่อง (ถ้าจะทำต่อต้องผ่าน G1 ก่อน)

เวลาที่ใช้: ~3 นาที
