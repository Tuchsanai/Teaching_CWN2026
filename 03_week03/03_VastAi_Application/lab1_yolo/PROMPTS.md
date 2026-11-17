# LAB 1 · พรอมต์ Copy & Paste

วางทีละพรอมต์ในช่องพิมพ์ของ Claude Code app (เปิดที่โฟลเดอร์ของบทนี้) · ทำตามลำดับ 1 → 2 → 3

## พรอมต์ 1 · เช่า RTX 4090 เทรน YOLO และเปิด AI server (~20–40 นาที)

```text
ทำงานใน container `multi-account` โฟลเดอร์ /workspace/vastapp_lab ด้วยสกิล vastai

เทรนโมเดลตรวจอุปกรณ์ความปลอดภัยและเปิด AI server ตามสูตรในไฟล์ lab1_yolo/RECIPE.md ของโฟลเดอร์ปัจจุบัน
LABEL=vapp-v-lab1 MAX_DPH=0.70 EPOCHS=50
```

## พรอมต์ 2 · เปิดเว็บบนเครื่องนี้แล้วต่อ AI server (~3 นาที)

```text
เปิดเว็บตรวจความปลอดภัยในโฟลเดอร์ lab1_yolo/web บนเครื่องนี้ (Docker Desktop) แล้วต่อกับ AI server บน Vast.ai
1. คัดลอกไฟล์ /workspace/vastapp_lab/lab1_yolo/yolo.env จาก container `multi-account` มาเป็นไฟล์ lab1_yolo/web/.env
2. เปิดเว็บตาม lab1_yolo/web/README.md แล้วรอจน http://localhost:3401 เปิดได้
3. ทดสอบรูปตัวอย่าง sample-1.jpg sample-2.jpg sample-5.jpg ใน lab1_yolo/web/public/samples ผ่าน POST http://localhost:3401/api/detect

สรุปเป็นตาราง: รูป · ผล (ผ่าน/ไม่ผ่าน) · คนไม่สวมหมวก · เวลาที่โมเดลใช้ (ms) · เวลาส่งรูปไป-กลับ (ms) ห้ามแสดงค่า key
```

เปิด http://localhost:3401 ในเบราว์เซอร์ แล้วลองกดรูปตัวอย่างหรืออัปโหลดรูปเอง · ดูผลย้อนหลังที่หน้า "ประวัติ"

## พรอมต์ 3 · ลบเครื่องและสรุปค่าใช้จ่าย

```text
ทำงานใน container `multi-account` โฟลเดอร์ /workspace/vastapp_lab ด้วยสกิล vastai

ปิดทุกอย่างของ LAB 1
1. ลบเครื่อง vapp-v-lab1 แล้วตรวจว่าไม่มีเครื่องป้ายนี้ค้างในบัญชี (ห้ามแตะเครื่องอื่น)
2. ปิดเว็บใน lab1_yolo/web ของโฟลเดอร์ปัจจุบันด้วย docker compose down (เก็บประวัติไว้)
3. สรุปค่าใช้จ่ายของเครื่อง vapp-v-lab1: อายุเครื่อง · ราคาต่อชั่วโมง · ยอดที่ถูกคิดจริง
```
