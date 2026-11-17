รันการวัดผลบน Test Set เสร็จแล้ว ใช้ไฟล์ `lab1_yolo/eval.py` บนเครื่อง vapp-lab1 (RTX 4090) ซึ่งเทรนครบ 50 Epoch ไว้แล้ว Test Set มี 82 ภาพ และไม่ได้ใช้ตอนเทรน

## ก่อนเทรน vs หลังเทรน (Test Set 82 ภาพ)

| ตัวชี้วัด | ก่อนเทรน (yolo11s COCO เดิม) | หลังเทรน (fine-tuned) |
|---|---:|---:|
| mAP50 (เฉลี่ย 10 คลาส) | 0.090 | **0.782** |
| mAP50-95 | 0.066 | **0.504** |
| AP50 Hardhat | 0.000 | **0.940** |
| AP50 NO-Hardhat | 0.000 | **0.578** |
| AP50 Safety Vest | 0.000 | **0.888** |
| AP50 NO-Safety Vest | 0.000 | **0.839** |
| AP50 Person | 0.753 | **0.880** |
| เวลาต่อรูป (ms) | 8.3 | 8.2 |

- **ทำไมก่อนเทรนได้ 0:** โมเดล COCO เดิมไม่มีคลาสหมวก เสื้อกั๊ก หรือหน้ากาก จึงได้คะแนนแค่คลาส Person (0.753) และ vehicle (0.149)
- **ตัวเลขทางการของ Ultralytics (หลังเทรน):** mAP50 0.787 · mAP50-95 0.512 · Precision 0.914 · Recall 0.736
- **ข้อที่ยังอ่อน:** NO-Hardhat ได้ AP50 แค่ 0.578 ซึ่งเป็นคลาสที่สำคัญที่สุดของงานนี้
- **ความเร็ว:** เวลาต่อรูปเท่าเดิม เพราะใช้โมเดลขนาดเดียวกัน (yolo11s)

## ไฟล์ที่ได้กลับมาใน `lab1_yolo/results/`
- `metrics.json` (อยู่ในโฟลเดอร์นี้ตามที่ขอ)
- `images/`: `ap50_per_class.png`, `curves.png`, `confusion_matrix_normalized.png` และภาพก่อน/หลัง `before_after_1.jpg` ถึง `before_after_5.jpg` ผมเปิดดูภาพที่ 1 แล้ว ด้านซ้ายเห็นแค่ person ส่วนด้านขวาจับ Hardhat, NO-Hardhat และ NO-Safety Vest ได้
- `train/`: `args.yaml`, `results.csv`, `train_info.json`
- `weights/best.pt`: ไฟล์โมเดลหลังเทรน

## สถานะเครื่อง
**เครื่อง vapp-lab1 (instance <id>, RTX 4090, $0.41 ต่อชั่วโมง) ยังเปิดอยู่** และยังคิดเงินอยู่ พร้อมใช้ต่อในขั้นที่ 5 (เปิด AI server)
