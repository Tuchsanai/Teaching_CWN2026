เตรียม Dataset บนเครื่อง **vapp-lab1** (Vast instance <id>, RTX 4090) เสร็จแล้วครับ ไฟล์อยู่ที่ `/workspace/construction-site-safety-28` (รูปแบบ YOLO)

| ชุดข้อมูล | จำนวนภาพ | จำนวนไฟล์ label |
|---|---:|---:|
| Training Set | 2,605 | 2,605 |
| Validation Set | 114 | 114 |
| Test Set | 82 | 82 |
| **รวม** | **2,801** | **2,801** |

**รายชื่อคลาส (10 คลาส)**

| # | คลาส | # | คลาส |
|---|---|---|---|
| 0 | Hardhat | 5 | Person |
| 1 | Mask | 6 | Safety Cone |
| 2 | NO-Hardhat | 7 | Safety Vest |
| 3 | NO-Mask | 8 | machinery |
| 4 | NO-Safety Vest | 9 | vehicle |

**สิ่งที่ทำ**
- **ติดตั้งแพ็กเกจ:** ได้ ultralytics 8.4.215 และ roboflow 1.7.3 ลองนำเข้าแล้วใช้ได้ และ GPU ใช้งานได้ (`torch.cuda` = True)
  - ติดตั้งครั้งแรก `import cv2` ล้ม เพราะเครื่องไม่มีไลบรารีหน้าจอ (`libxcb.so.1`) จึงถอด `opencv-python` ออก แล้วใช้ `opencv-python-headless` แทน
- **การดูแล key:**
  - ส่ง `ROBOFLOW_API_KEY` จาก `.env` ไปทาง stdin ของ SSH เท่านั้น ไม่ได้ใส่ในบรรทัดคำสั่งหรือเขียนลงไฟล์ และไม่ได้แสดงค่า key
  - ลบสคริปต์ดาวน์โหลดออกจากเครื่องที่เช่าแล้ว
  - ค้นหาค่า key ทั้งเครื่อง (`/root`, `/workspace`, `/tmp`, `/etc`) พบ **0 ไฟล์**
- **แก้ `data.yaml`:** ไฟล์ที่ Roboflow ให้มาชี้ path แบบ `../train/images` จึงเพิ่ม `path: /workspace/construction-site-safety-28` และเปลี่ยน path ของแต่ละชุดให้ชี้ในโฟลเดอร์นี้ ตรวจด้วย ultralytics แล้วอ่านได้ครบ 10 คลาส พร้อมใช้ train

**สถานะเครื่อง:** vapp-lab1 **ยังเปิดอยู่ (running)** ราคาประมาณ $0.41/ชั่วโมง ยังคิดเงินอยู่จนกว่าจะสั่ง destroy
