# ขั้นที่ 8 · เทรน YOLO11s และตัดสิน Acceptance Gate (NFR-01)

เทรนเสร็จและวัดผลครบแล้วบนเครื่องป้าย `e2e-sitesafe` (RTX 3090) **ผลตัดสิน: ยังประกาศว่า "ผ่าน Acceptance Gate" ไม่ได้** เพราะ Test Set ไม่ครบเงื่อนไขการวัดของ NFR-01 (ต้องมีรูป Positive ≥ 100 และรูป Negative ≥ 100 แต่มีจริง 25 และ 57 รูป) ส่วนค่าที่วัดได้บนรูปที่มีอยู่ถึงเกณฑ์ทั้งสองตัว โดย Recall อยู่ที่ขอบเกณฑ์พอดี (20 จาก 25 รูป = 0.80)

## 1. สิ่งที่ทำ

- เทรน YOLO11s (ตั้งต้นจากน้ำหนัก COCO) 30 Epoch · ภาพ 640 · seed 0 · batch 16 ใช้เวลา 8 นาที 55 วินาที
- เลือก Confidence Threshold บน Validation Set (114 รูป · Positive 37 รูป) ตามกติกา NFR-01 คือ Recall สูงสุดโดย Precision ไม่ต่ำกว่า 0.80 ได้ค่า **0.32** (บน Validation: Recall 0.946 · Precision 0.946) แล้วกำหนดค่านี้ให้คงที่ก่อนวัดบน Test Set
- วัดบน Test Set (82 รูป) ด้วย `evaluate.py` ของทีม นับระดับรูปตามนิยาม TP / FN / FP ของ NFR-01
- งานทั้งหมดรันใน tmux บนเครื่อง GPU และแบ่งเป็น 9 ขั้นที่มีไฟล์บอกสถานะ ถ้าการเชื่อมต่อหลุดงานยังเดินต่อ และสั่งซ้ำได้โดยเริ่มจากขั้นที่ยังไม่เสร็จ (การเทรนต่อจาก `last.pt`)

## 2. โค้ดของทีมรันไม่ได้ตรงไหน และแก้อะไร

โฟลเดอร์ `./app/ai/train` มีเฉพาะโค้ด Evaluation (`evaluate.py`) **ไม่มีสคริปต์ Training** และ `evaluate.py` หยุดด้วย error 3 จุดเมื่อรันกับ Dataset นี้ (ทดลองรันโค้ดเดิมยืนยันแล้วทั้ง 3 จุด)

| ปัญหา | ข้อความ error ของโค้ดเดิม | วิธีแก้ |
|---|---|---|
| `data.yaml` ของ Roboflow ชี้ `../test/images` ซึ่งไม่มีอยู่จริง | `Expected a split directory or image-list file` | ไม่แก้โค้ดทีม · สร้าง `data_fixed.yaml` (path แบบ absolute) ไว้ข้างไฟล์เดิม |
| ชื่อคลาสใน Dataset คือ `NO-Safety Vest` ไม่ตรงกับชื่อใน `classes.json` | `no class name matches NO_VEST` | **แก้ `app/ai/train/classes.json`** เพิ่มชื่อ `"NO-Safety Vest"` 1 ชื่อ |
| Test Set เล็กกว่าเงื่อนไข จึงไม่ยอมวัดเลย | `Test set needs at least 100 ... (found 25 positive, 57 negative)` | **แก้ `app/ai/train/evaluate.py`** เพิ่มตัวเลือก `--allow-small-test` (ค่าเริ่มต้นยังเข้มงวดเหมือนเดิม) เมื่อเปิดจะวัดและรายงานค่า พร้อมจำนวนรูป `positive_images` `negative_images` `test_size_ok` `metrics_pass` และ **ไม่ให้ผล "ผ่าน" ถ้า Test Set ไม่ครบเงื่อนไข** |

ไฟล์ของทีมที่ถูกแก้มี 2 ไฟล์เท่านั้น (สำเนาก่อนแก้อยู่ที่ `./code_step08/evaluate.orig.py` และ `classes.orig.json`) Unit test ของทีมได้ผลเท่าเดิมก่อนและหลังแก้ (ผ่าน 28 · ไม่ผ่าน 2 ข้อเดิมซึ่งเกิดจากการอ่านไฟล์ภาษาไทยบน Windows ไม่เกี่ยวกับการแก้ครั้งนี้)

โค้ดที่เขียนเพิ่มอยู่ใน `./code_step08/` : `train.py` (Training) · `select_threshold.py` (เลือก Threshold บน Validation) · `map_eval.py` (mAP) · `baseline_gate.py` (ผลก่อนเทรน) · `make_examples.py` (ภาพตัวอย่าง) · `fix_data_yaml.py` · `run_pipeline.sh`

## 3. ผลวัดบน Test Set (82 รูป · Positive 25 · Negative 57 · Threshold 0.32)

| คลาส | TP | FN | FP | TN | Recall | Precision |
|---|---|---|---|---|---|---|
| ไม่ใส่หมวก (ก่อนเทรน) | 0 | 25 | 0 | 57 | 0.00 | 0.00 |
| ไม่ใส่หมวก (หลังเทรน) | 20 | 5 | 1 | 56 | 0.80 | 0.952 |
| ไม่ใส่เสื้อสะท้อนแสง (หลังเทรน · รายงานค่า ยังไม่เป็นเกณฑ์) | 31 | 5 | 0 | 46 | 0.861 | 1.00 |

- ก่อนเทรน: โมเดล COCO ไม่มีคลาส "ไม่ใส่หมวก" ระบบจึงให้ H = 0 ทุกรูป Recall เป็น 0 (mAP50 ที่ 0.011 เกิดจากเลขคลาสของ COCO ไม่ตรงกับ Dataset จึงใช้เป็นเพียงจุดอ้างอิง)
- mAP50 รวม 10 คลาสหลังเทรน 0.749 แต่เฉพาะคลาส NO-Hardhat ระดับกรอบได้ 0.509 ซึ่งต่ำที่สุดในกลุ่มคลาสคน

## 4. การตัดสิน Acceptance Gate อย่างตรงไปตรงมา

- ค่าที่วัดได้: Recall 0.80 (≥ 0.80) และ Precision 0.952 (≥ 0.80) → ถึงเกณฑ์ตัวเลข
- เงื่อนไขการวัด: Test Set ต้องมี Positive ≥ 100 และ Negative ≥ 100 รูป (AS-14) → **ไม่ครบ** (25 / 57)
- จึงสรุปว่า **ยังไม่ผ่าน Acceptance Gate อย่างเป็นทางการ (ยังตัดสินไม่ได้)** ผลข้างบนเป็นผลเบื้องต้นบนรูปที่มีอยู่
- ข้อควรระวัง: Recall อยู่ที่ขอบเกณฑ์พอดี ถ้าจับพลาดเพิ่มอีก 1 รูปจะเหลือ 19/25 = 0.76 และไม่ถึงเกณฑ์ ด้วยรูป Positive เพียง 25 รูป ตัวเลขนี้ยังไม่มั่นคงพอจะยืนยันกับลูกค้า
- สิ่งที่ต้องทำก่อนตัดสินจริง: หา Test Set ให้ครบ 100 + 100 รูป (ไม่ซ้ำกับรูป Training และ Validation) แล้ววัดซ้ำด้วย Threshold 0.32 เดิมโดยไม่ปรับ

## 5. ไฟล์ที่เก็บไว้

- บนเครื่อง GPU: น้ำหนักที่ดีที่สุด `/workspace/e2e_sitesafe/model/best.pt` (สำเนาจาก `/workspace/e2e_sitesafe/runs/train/weights/best.pt`) พร้อม `threshold.json` ในโฟลเดอร์เดียวกัน
- ที่ `./results/model` : `metrics_before.json` · `metrics_after.json` · `threshold.json` · `threshold_sweep_val.json` · `threshold_selection_val.png` · `map_before.json` · `map_after.json` · `results.png` · `results.csv` · `train_time.json` · `args.yaml` · `examples_test_predictions.jpg` (ตัวอย่าง TP / FN / FP / TN) · `test_image_results.json` (ผลรายรูป) · `pipeline.log` · โฟลเดอร์ `val_before/` และ `val_after/` (กราฟ PR · Confusion Matrix · ภาพผลตรวจ)

## 6. ตารางสรุป

| ตัวชี้วัด | ก่อนเทรน | หลังเทรน | เกณฑ์ | ผ่านหรือไม่ | เวลาเทรน | ค่าเช่าถึงตอนนี้ |
|---|---|---|---|---|---|---|
| Image-level Recall "ไม่ใส่หมวก" | 0.00 (0/25) | 0.80 (20/25) | ≥ 0.80 | ค่าที่วัดได้ถึงเกณฑ์ (ขอบเกณฑ์พอดี) | 8 นาที 55 วินาที | ประมาณ $0.09 |
| Image-level Precision "ไม่ใส่หมวก" | 0.00 (0/0) | 0.952 (20/21) | ≥ 0.80 | ค่าที่วัดได้ถึงเกณฑ์ | เท่ากัน | เท่ากัน |
| จำนวนรูป Test Set (Positive / Negative) | 25 / 57 | 25 / 57 | ≥ 100 / ≥ 100 | **ไม่ครบเงื่อนไข** | – | – |
| Image-level Recall / Precision "ไม่ใส่เสื้อสะท้อนแสง" | 0.00 / 0.00 | 0.861 / 1.00 | รายงานค่า ยังไม่เป็นเกณฑ์ | – | – | – |
| mAP50 (10 คลาส · ระดับกรอบ) | 0.011 | 0.749 | ไม่มีใน Requirement | – | – | – |
| **Acceptance Gate (NFR-01)** | ไม่ผ่าน | ค่าถึงเกณฑ์ แต่ Test Set ไม่ครบเงื่อนไข | Recall และ Precision ≥ 0.80 บน Test Set ที่มี ≥ 100 + ≥ 100 รูป | **ยังไม่ผ่าน (ยังตัดสินไม่ได้)** | 8 นาที 55 วินาที | ประมาณ $0.09 (0.39 ชั่วโมง × $0.2215/ชั่วโมง) |

**เครื่องยังเปิดอยู่:** instance 61353544 ป้าย `e2e-sitesafe` สถานะ running คิดเงินต่อเนื่อง $0.2215 ต่อชั่วโมง ไม่ได้เช่าเครื่องเพิ่ม ไม่ได้ลบเครื่อง และไม่ได้แตะเครื่องป้ายอื่น

เวลาที่ใช้: ~21 นาที
