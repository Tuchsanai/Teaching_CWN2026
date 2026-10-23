# โจทย์: เว็บร้านวัสดุก่อสร้าง "บ้านช่าง BuildMart" v3 + แชทบอท AI ที่ฟังและพูดได้ (RabbitMQ · Hybrid RAG + reranker · Whisper · VoxCPM2 · เว็บ 3D · ประเมิน RAG · load test · Vast.ai 3 GPU)

> ไฟล์นี้คือ **requirement** ที่ AI อ่านแล้วแตกเป็นงานย่อย (DAG) ให้ทีม agent — นักศึกษาแก้ไขได้ (เพิ่ม/ลดฟีเจอร์ เปลี่ยนชื่อร้าน)
> ทุกข้อในหัวข้อ "เกณฑ์ทดสอบ" ต้องมี Playwright test ที่ผ่าน · เฉลยที่ทำตามไฟล์นี้ครบอยู่ใน `_solution/buildmart/`
>
> **v3 เพิ่มจาก v2:** 👂 **ฟังเสียง** (ถามด้วยไมค์ → Whisper ถอดความ) · 🗣️ **พูด** (VoxCPM2 เสียงไทย/อังกฤษ โคลนเสียงมาสคอต) · 🎯 **reranker** (bge-reranker-v2-m3 จัดอันดับ RAG top 20 → top 4) · 🧊 **เว็บ 3D** (Three.js) + มาสคอต 3D **"น้องช่าง"** ที่ขยับตามสถานะและขยับปากตามเสียง · 💬 **บทสนทนาหลายรอบ** (จำ 10 ข้อความ · ทดสอบ 4–6 รอบ) · 📊 **ประเมิน RAG** 150–170 ข้อ + คำถามปกติ 70–80 ข้อ + บทสนทนา 10–12 บท + dashboard `/admin/eval` · 📈 **load test** รับผู้ใช้พร้อมกันได้กี่คน (1→32 คน) + `/admin/load` · 🐇 **RabbitMQ กระจายโหลด** (1 คิวต่อ GPU · prefetch ตั้งได้ · `--scale` worker) · 🖥️ **GPU 3 ใบ** (GPU-1 RTX 5090 = Qwen · GPU-2 RTX 4090 = ai-box `stt` Whisper · GPU-3 RTX 4090 = ai-box `tts,rerank` VoxCPM2 + reranker) · 📄 เอกสาร PDF 6 ไฟล์ **ให้มาแล้ว** ใน `documents/` (18–22 หน้า/ไฟล์ · ไม่ต้องสร้างเอง) · เลิกใช้ Kokoro/PyThaiTTS (VoxCPM2 พูดไทยได้แล้ว)

## 1) ข้อมูลร้าน

| หัวข้อ | ค่า |
|---|---|
| ชื่อร้าน | บ้านช่าง BuildMart |
| เวลาเปิด | จันทร์–เสาร์ 07:00–18:00 · อาทิตย์ 08:00–12:00 |
| สาขา (คลังสินค้า) | `LKB` ลาดกระบัง โทร 02-111-0001 · `BNA` บางนา โทร 02-111-0002 · `RST` รังสิต โทร 02-111-0003 |
| LINE | @buildmart-demo |
| ราคา | ราคาสินค้า **ยังไม่รวม VAT** · VAT 7% คิดตอนสรุปยอด |

**ราคาส่งตามจำนวน (ทุกสินค้า):** 1–49 ชิ้น ราคาปกติ · 50–199 ชิ้น ลด 5% · 200 ชิ้นขึ้นไป ลด 10% (คิดต่อรายการสินค้า)

**ค่าส่ง (ตามน้ำหนักรวมของตะกร้า):**

| น้ำหนักรวม | รถ | ค่าส่ง |
|---|---|---|
| ≤ 1,000 กก. | กระบะ | 500 บาท (**ฟรี** ถ้ายอดก่อน VAT หลังส่วนลด ≥ 20,000 บาท) |
| 1,000.01–6,000 กก. | รถ 6 ล้อ | 1,500 บาท |
| > 6,000 กก. | รถ 10 ล้อ | 3,500 บาท |

**คูปอง:** `BUILD5` ลด 5% เมื่อยอดก่อน VAT ≥ 5,000 · `CONTRACTOR10` ลด 10% เมื่อยอดก่อน VAT ≥ 30,000 (ใช้ได้ทีละ 1 ใบ · ลดจากยอดหลังราคาส่ง)

**ลำดับการคิดเงิน:** ยอดสินค้า (หลังราคาส่ง) → หักคูปอง → + ค่าส่ง → + VAT 7% ของ (ยอดหลังคูปอง + ค่าส่ง) → ปัดเศษ 2 ตำแหน่ง

## 2) สินค้าตั้งต้น (seed · ต้องมีครบทุกตัวด้านล่าง เพิ่มเองได้อีก)

| SKU | ชื่อ | หมวด | หน่วย | ราคา (บาท) | น้ำหนัก/หน่วย (กก.) | สต็อก LKB/BNA/RST | จุดสั่งซื้อซ้ำ |
|---|---|---|---|---|---|---|---|
| CEM-001 | ปูนซีเมนต์ปอร์ตแลนด์ ประเภท 1 (50 กก.) | ปูน | ถุง | 145 | 50 | 800/500/300 | 200 |
| CEM-002 | ปูนก่อ สำเร็จรูป (50 กก.) | ปูน | ถุง | 120 | 50 | 400/300/0 | 100 |
| CEM-003 | ปูนฉาบ สำเร็จรูป (50 กก.) | ปูน | ถุง | 125 | 50 | 350/250/150 | 100 |
| CEM-004 | ปูนกาวซีเมนต์ ปูกระเบื้อง (20 กก.) | ปูน | ถุง | 185 | 20 | 200/120/80 | 50 |
| AGG-001 | ทรายหยาบ | หิน-ทราย | ลบ.ม. | 450 | 1500 | 60/40/30 | 20 |
| AGG-002 | ทรายละเอียด | หิน-ทราย | ลบ.ม. | 480 | 1450 | 50/30/20 | 20 |
| AGG-003 | หิน 3/4 (หินเบอร์ 1) | หิน-ทราย | ลบ.ม. | 650 | 1600 | 70/50/40 | 20 |
| STL-001 | เหล็กเส้นกลม RB6 ยาว 10 ม. | เหล็ก | เส้น | 48 | 2.22 | 1000/800/600 | 300 |
| STL-002 | เหล็กเส้นกลม RB9 ยาว 10 ม. | เหล็ก | เส้น | 105 | 4.99 | 900/700/500 | 300 |
| STL-003 | เหล็กข้ออ้อย DB12 ยาว 10 ม. | เหล็ก | เส้น | 195 | 8.88 | 700/500/400 | 200 |
| STL-004 | เหล็กข้ออ้อย DB16 ยาว 10 ม. | เหล็ก | เส้น | 340 | 15.78 | 400/300/200 | 100 |
| STL-005 | ลวดผูกเหล็ก (1 กก.) | เหล็ก | ม้วน | 55 | 1 | 300/200/100 | 50 |
| BRK-001 | อิฐมอญ (ก้อน) | อิฐ-บล็อก | ก้อน | 1.20 | 1.1 | 50000/30000/20000 | 10000 |
| BRK-002 | อิฐมวลเบา 7.5 ซม. (ก้อน) | อิฐ-บล็อก | ก้อน | 22 | 3.5 | 8000/6000/4000 | 2000 |
| BRK-003 | บล็อกประสาน (ก้อน) | อิฐ-บล็อก | ก้อน | 9 | 6 | 5000/3000/0 | 1000 |
| TIL-001 | กระเบื้องพื้น 60x60 ลายหินอ่อน (กล่อง 4 แผ่น = 1.44 ตร.ม.) | กระเบื้อง | กล่อง | 389 | 32 | 400/300/200 | 100 |
| TIL-002 | กระเบื้องผนัง 30x60 ขาวเงา (กล่อง 8 แผ่น = 1.44 ตร.ม.) | กระเบื้อง | กล่อง | 299 | 24 | 300/200/150 | 80 |
| TIL-003 | ยาแนว สีเทา (1 กก.) | กระเบื้อง | ถุง | 65 | 1 | 200/150/100 | 50 |
| PNT-001 | สีน้ำอะคริลิก ภายนอก สีขาว (แกลลอน 3.785 ล.) | สี | แกลลอน | 890 | 5 | 120/80/60 | 30 |
| PNT-002 | สีน้ำอะคริลิก ภายใน สีขาว (แกลลอน 3.785 ล.) | สี | แกลลอน | 590 | 5 | 150/100/80 | 30 |
| PNT-003 | สีรองพื้นปูนใหม่ (แกลลอน) | สี | แกลลอน | 650 | 5 | 100/60/40 | 20 |
| PNT-004 | แปรงทาสี 4 นิ้ว | สี | อัน | 75 | 0.2 | 200/150/100 | 50 |
| PIP-001 | ท่อ PVC 1/2 นิ้ว ชั้น 13.5 ยาว 4 ม. | ประปา | เส้น | 62 | 1.1 | 500/400/300 | 100 |
| PIP-002 | ท่อ PVC 4 นิ้ว ชั้น 8.5 ยาว 4 ม. | ประปา | เส้น | 420 | 9.5 | 120/80/60 | 30 |
| PIP-003 | ข้องอ PVC 1/2 นิ้ว 90° | ประปา | ชิ้น | 6 | 0.02 | 2000/1500/1000 | 300 |
| PIP-004 | กาวทาท่อ PVC (250 กรัม) | ประปา | กระป๋อง | 85 | 0.3 | 150/100/80 | 40 |
| ELC-001 | สายไฟ THW 2.5 ตร.มม. (ม้วน 100 ม.) | ไฟฟ้า | ม้วน | 1650 | 3.3 | 60/40/30 | 15 |
| ELC-002 | เบรกเกอร์ลูกย่อย 16A | ไฟฟ้า | ตัว | 145 | 0.2 | 300/200/150 | 60 |
| ELC-003 | ตู้คอนซูเมอร์ 6 ช่อง | ไฟฟ้า | ตู้ | 1290 | 3 | 40/30/20 | 10 |
| ROF-001 | กระเบื้องหลังคาลอนคู่ สีแดง (แผ่น) | หลังคา | แผ่น | 68 | 4 | 3000/2000/1500 | 500 |
| ROF-002 | เมทัลชีท 0.35 มม. ยาว 4 ม. (แผ่น) | หลังคา | แผ่น | 520 | 13 | 300/200/150 | 60 |
| WOD-001 | ไม้อัด 4 มม. 4x8 ฟุต | ไม้ | แผ่น | 210 | 9 | 200/150/100 | 50 |
| WOD-002 | ไม้แบบ ยาว 4 ม. 1x6 นิ้ว | ไม้ | แผ่น | 145 | 6 | 400/300/200 | 100 |
| TOL-001 | ค้อนหงอน 27 มม. | เครื่องมือ | อัน | 220 | 0.7 | 80/60/40 | 20 |
| TOL-002 | สว่านกระแทกไร้สาย 18V | เครื่องมือ | เครื่อง | 2490 | 1.8 | 25/15/10 | 5 |
| TOL-003 | ตลับเมตร 5 ม. | เครื่องมือ | อัน | 159 | 0.3 | 150/100/80 | 30 |

หมวดทั้งหมด 10 หมวด: ปูน · หิน-ทราย · เหล็ก · อิฐ-บล็อก · กระเบื้อง · สี · ประปา · ไฟฟ้า · หลังคา · ไม้ · เครื่องมือ (เครื่องมือรวมเป็นหมวดที่ 11 ได้)

## 3) ฟีเจอร์หน้าเว็บ (frontend)

1. **หน้าแรก + รายการสินค้า** `/` และ `/products` — ค้นหาภาษาไทยแบบคำบางส่วน (เช่น "ปูน" เจอ CEM-*), กรองหมวด/ช่วงราคา/มีของ, เรียงราคา ต่ำ→สูง / สูง→ต่ำ, แบ่งหน้า 12 ชิ้นต่อหน้า · หน้าแรกมีฉาก 3D (ข้อ 12)
2. **หน้าสินค้า** `/products/[sku]` — สเปก น้ำหนัก ตารางราคาส่ง 3 ขั้น สต็อกแยก 3 สาขา (สาขาที่ 0 ชิ้นแสดง "หมด") ปุ่มเพิ่มลงตะกร้าพร้อมจำนวน
3. **เครื่องคำนวณวัสดุ** `/calculator` (5 แท็บ) — ทุกผลลัพธ์ปัดขึ้นเป็นจำนวนเต็ม และมีปุ่ม "เพิ่มทั้งหมดลงตะกร้า" ที่จับคู่ SKU ให้อัตโนมัติ
   - คอนกรีต (ส่วนผสม 1:2:4) ปริมาตร V ลบ.ม. → ปูน CEM-001 = ⌈V×7⌉ ถุง · ทรายหยาบ AGG-001 = ⌈V×0.5⌉ ลบ.ม. · หิน AGG-003 = ⌈V×0.9⌉ ลบ.ม.
   - ก่อผนัง พื้นที่ A ตร.ม. → อิฐมอญ BRK-001 = ⌈A×140⌉ ก้อน + ปูนก่อ CEM-002 = ⌈A×0.25⌉ ถุง · หรือ อิฐมวลเบา BRK-002 = ⌈A×8.33⌉ ก้อน + ปูนก่อ = ⌈A×0.12⌉ ถุง
   - ปูกระเบื้อง พื้นที่ A ตร.ม. + เศษเผื่อ 10% → TIL-001 = ⌈A×1.10/1.44⌉ กล่อง · ปูนกาว CEM-004 = ⌈A/4⌉ ถุง · ยาแนว TIL-003 = ⌈A/5⌉ ถุง
   - ทาสี พื้นที่ A ตร.ม. จำนวนเที่ยว N (ค่าเริ่มต้น 2) อัตรา 30 ตร.ม./แกลลอน/เที่ยว → ⌈A×N/30⌉ แกลลอน (ภายใน PNT-002 หรือ ภายนอก PNT-001) + รองพื้น PNT-003 = ⌈A/40⌉
   - เหล็กเส้น ขนาด (RB6/RB9/DB12/DB16) ยาวรวม L เมตร → จำนวนเส้น ⌈L/10⌉ และน้ำหนัก = L × (0.222/0.499/0.888/1.578) กก. (ทศนิยม 2 ตำแหน่ง)
4. **ตะกร้า + ชำระเงิน** `/cart` `/checkout` — แสดงราคาส่งที่ได้ต่อรายการ ใส่คูปอง เลือกสาขาที่ส่งของ วันส่ง (7 วันถัดไป ยกเว้นวันอาทิตย์) ช่วงเช้า/บ่าย แสดงรถที่ใช้ + ค่าส่ง + VAT + ยอดสุทธิ (ตามลำดับข้อ 1) · ตะกร้าเก็บใน DB ผูกกับ cookie session
5. **ใบเสนอราคา** — ปุ่ม "ขอใบเสนอราคา" จากตะกร้า → กรอกชื่อ/บริษัท/เลขผู้เสียภาษี (ไม่บังคับ) → หน้า `/quote/QT-YYYYMMDD-NNNN` พิมพ์ได้ (print CSS) มีอายุ 7 วัน และปุ่ม "แปลงเป็นคำสั่งซื้อ"
6. **คำสั่งซื้อ + ติดตาม** — สั่งซื้อแล้วได้เลข `BM-YYYYMMDD-NNNN` ตัดสต็อกสาขาที่เลือก (ถ้าไม่พอต้องแจ้งเตือนและไม่ให้สั่ง) · หน้า `/track` กรอกเลขคำสั่งซื้อ + เบอร์โทร → timeline: รับคำสั่งซื้อ → เตรียมสินค้า → กำลังจัดส่ง → ส่งแล้ว
7. **หลังร้าน** `/admin` (รหัสผ่านจาก env `ADMIN_PASSWORD` ค่า dev `admin1234`) — ตารางสต็อกแก้ไขได้, แจ้งเตือนสินค้าต่ำกว่าจุดสั่งซื้อซ้ำ, รายการคำสั่งซื้อ + เปลี่ยนสถานะ, แดชบอร์ดยอดขายวันนี้/7 วัน + 5 สินค้าขายดี (กราฟ SVG/CSS ไม่ต้องใช้ไลบรารี)
8. **แชทบอท** — ปุ่มลอยมุมขวาล่างทุกหน้า เปิดหน้าต่างแชท ประวัติแชทเก็บใน DB · มีปุ่มคำถามแนะนำ 3 ปุ่ม · ถ้าบอทสั่งเพิ่มลงตะกร้า ตัวเลขบนไอคอนตะกร้าต้องอัปเดตทันที · **คุยต่อเนื่องหลายรอบได้** (บอทเข้าใจ "อันนั้น" "ตัวเมื่อกี้" จากรอบก่อน · ข้อ 4.4)
9. **อ่านออกเสียง (TTS)** — ทุกคำตอบของบอทมีปุ่ม 🔊 `data-testid="tts-play"` และมีสวิตช์ "อ่านออกเสียงอัตโนมัติ" `data-testid="tts-auto"` ในหัวหน้าต่างแชท · เสียงคือ **VoxCPM2** เสียง "น้องช่าง" (ไทย + อังกฤษ) ผ่าน ai-box GPU-3 (`TTS_URL`) อย่างเดียว · โหมด mock เล่นเสียง VoxCPM2 ที่อัดไว้แล้ว (ข้อ 4.5) · เล่นผ่าน `<audio data-testid="chat-audio">`
10. **อ้างอิงเอกสาร (RAG)** — ถ้าบอทตอบโดยใช้ข้อมูลจากเอกสาร PDF ต้องแสดงป้ายอ้างอิงใต้คำตอบ `data-testid="chat-cite"` เช่น `📄 BM-DS-CEM.pdf · หน้า 1` (คลิกแล้วเปิด PDF หน้านั้น)
11. **หลังร้าน → เอกสาร** `/admin/docs` — ตารางเอกสาร PDF ทั้งหมด (ชื่อ · จำนวน chunk · สถานะ `queued/processing/ready/failed`) · อัปโหลด PDF ใหม่ได้ → เข้าคิว RabbitMQ แล้ว worker ทำ RAG ให้เอง · หลังร้านมีกล่อง **แจ้งเตือน** (คำสั่งซื้อใหม่ · สินค้าต่ำกว่าจุดสั่งซื้อซ้ำ) ที่มาจากคิว `order.events`
12. **ธีม 3D (Three.js)** — ใช้ **react-three-fiber** (+ drei) · โหลดเฉพาะฝั่ง client (`next/dynamic` `ssr:false`) ไม่ให้หน้าเว็บช้า/พังตอน SSR
    - **หน้าแรก `/`**: ฉาก 3D เต็มความกว้างด้านบน — กล่องวัสดุลอย (ถุงปูน · เหล็กเส้น · อิฐ · กระป๋องสี · กระเบื้อง) หมุนช้า ๆ · แสงอุ่นโทนแบรนด์ (#F26B1D) + bloom เบา ๆ · **เลื่อนหน้าแล้วกล้องเคลื่อน** (scroll → camera) · คลิกกล่องวัสดุ → ไป `/products?category=<หมวด>` · ข้อความหัว + ช่องค้นหาวางทับฉากได้
    - ประสิทธิภาพ: `dpr` ไม่เกิน 2 · หยุด render เมื่อแท็บไม่ active / ฉากเลื่อนพ้นจอ · ผู้ใช้ตั้ง `prefers-reduced-motion` → ฉากนิ่ง
    - **fallback เมื่อไม่มี WebGL** (ตรวจก่อนสร้าง canvas): แสดงแบนเนอร์รูปภาพ (ข้อ 15) แทนฉาก 3D และมาสคอตเป็นรูป 2D · ห้ามมี error ค้างหน้าจอ · ฟีเจอร์อื่นทำงานปกติ
13. **มาสคอต 3D "น้องช่าง"** ในหน้าต่างแชท (มุมบนของหน้าต่าง) `data-testid="mascot"`
    - ตัวกลม ๆ น่ารัก สวม**หมวกนิรภัยสีส้ม** เสื้อกั๊กสะท้อนแสง ถือค้อน/ตลับเมตร · สร้างจาก primitive ของ Three.js เอง (sphere/capsule/box) ไม่ต้องหาไฟล์ GLB · ใช้ภาพ concept จาก cyolo (ข้อ 15) เป็นต้นแบบสี/สัดส่วน
    - **4 ท่า** ตาม `data-state`: `idle` (หายใจ/โยกตัวเบา ๆ กะพริบตา) · `listening` (เอียงหัวฟัง มีวงคลื่นเสียงรอบตัว ระหว่างอัดไมค์) · `thinking` (มองขึ้น หมุนค้อน มีจุด … ระหว่างรอคำตอบ/สถานะ "กำลังคิด…") · `talking` (ระหว่างเล่นเสียงคำตอบ)
    - **ขยับปากตามความดังเสียงจริง**: ต่อ `<audio>` เข้า WebAudio `AnalyserNode` → RMS ทุกเฟรม → scale ปาก · เขียนค่าเปิดปากล่าสุด 0.00–1.00 ไว้ที่ attribute `data-mouth` ของ `mascot` (อัปเดต ≥ 10 ครั้ง/วิ ระหว่าง talking · กลับเป็น 0 เมื่อจบ) ไว้ให้ e2e ตรวจ
    - ลำดับมาตรฐาน: ถามด้วยเสียง `idle → listening → thinking → talking → idle` · ถามด้วยการพิมพ์ + เล่นเสียง `idle → thinking → talking → idle` · ไม่เล่นเสียง `idle → thinking → idle`
14. **ถามด้วยเสียง (ไมค์)** — ปุ่มไมค์ `voice-mic` ข้างช่องพิมพ์ (กดค้างพูด หรือกด 1 ครั้งเริ่ม/กดอีกครั้งหยุด · MediaRecorder `audio/webm;codecs=opus` · ยาวสุด 30 วิ แล้วหยุดเอง)
    - ทุกครั้งที่อัดให้เรียก `getUserMedia` ใหม่และ `stop()` track เมื่ออัดเสร็จ (ไฟไมค์ดับ · e2e ใส่ไฟล์เสียงคนละไฟล์ต่อรอบได้)
    - อัดเสร็จ → `POST /api/voice` → ได้ข้อความ → แสดงเป็นฟองผู้ใช้ (`chat-msg-user`) ที่มีป้าย 🎙 `chat-msg-voice` → ส่งเข้าแชทต่อทันที (เหมือนพิมพ์ · ส่ง `lang` ที่ Whisper ตรวจได้) · ถอดไม่ได้/ว่าง → แจ้ง "ไม่ได้ยินเสียง ลองพูดอีกครั้งครับ" ไม่ส่งแชท
    - **โหมด "คุยด้วยเสียง"** สวิตช์ `voice-mode` ในหัวหน้าต่างแชท: เปิดแล้ว ถามด้วยไมค์ → บอทตอบ → **เล่นเสียงคำตอบอัตโนมัติ** (ไม่ต้องกด 🔊) และมาสคอตพูด · ปิดอยู่ = ถามด้วยไมค์ได้แต่ตอบเป็นข้อความ (ยกเว้นเปิด `tts-auto`)
    - `GET /api/voice/status` → `{enabled:false}` (ไม่มี consumer ที่ `stt.request`) → ซ่อนปุ่มไมค์และ `voice-mode` · เบราว์เซอร์ไม่อนุญาตไมค์ → แจ้งเป็นข้อความในแชท
15. **รูปภาพทั้งเว็บสร้างด้วย cyolo (งาน image)** — ในแผน DAG ต้องมีงานประเภท image ที่มอบให้บัญชี `cyolo*` สร้างไฟล์ต่อไปนี้ (ห้ามใช้รูปจากเว็บอื่น · ห้ามมีโลโก้/ยี่ห้อจริง · ห้ามมีตัวหนังสือในภาพ ยกเว้น "BuildMart")
    - `web/public/img/banner-hero.webp` (1920×800 · ฉากร้านวัสดุก่อสร้างโทนส้ม-เทาเข้ม · ใช้เป็น fallback ของฉาก 3D) + `banner-promo.webp` (1200×400)
    - `web/public/img/cat/<หมวด>.webp` 11 รูป (ปูน หิน-ทราย เหล็ก อิฐ-บล็อก กระเบื้อง สี ประปา ไฟฟ้า หลังคา ไม้ เครื่องมือ · 600×600 สไตล์เดียวกัน · ใช้ในหน้าแรกและหน้ารายการ · ชื่อไฟล์ใช้ slug อังกฤษ เช่น `cement.webp`)
    - `web/public/img/mascot/nongchang-concept.webp` (ภาพ concept หน้า+ข้าง ให้ทีม 3D ใช้อ้างอิง) + `nongchang-{idle,listening,thinking,talking}.webp` 4 ท่า (512×512 พื้นโปร่งใส · ใช้เป็นมาสคอต 2D ตอนไม่มี WebGL)
    - เก็บ prompt ที่ใช้สร้างทุกรูปไว้ใน `web/public/img/PROMPTS.md`
16. **หลังร้าน → ประเมิน RAG** `/admin/eval` (ต้องล็อกอิน admin) — dashboard ผลประเมิน (ข้อ 8): เลือก run `eval-run-select` · การ์ดคะแนนต่อชุด×metric `eval-metric` (`data-set` `data-metric` · แสดงเป็น %) · กราฟแท่งแยก **ต่อเอกสาร** (Hit@4 ต่อไฟล์ PDF) และ **ต่อประเภทคำถาม** (ข้อความ/ตารางหัว 2 ชั้น/เซลล์รวม/เชิงอรรถ/ข้ามหน้า) · ตาราง **เทียบ 2 run** `eval-compare` (เช่น มี/ไม่มี reranker · แสดงผลต่าง +/− เป็นสีเขียว/แดง) · รายการข้อ `eval-item` (`data-id` `data-pass="true|false"`) กดขยายดูคำถาม · คำตอบที่คาด · คำตอบจริง · หน้าที่ค้นได้ · เหตุผลที่ผิด · checkbox **"เฉพาะข้อผิด"** (หรือ URL `?only=fail`) · กราฟใช้ SVG/CSS ไม่ใช้ไลบรารี
17. **หลังร้าน → load test** `/admin/load` (ต้องล็อกอิน admin) — ผล load test (ข้อ 9) จาก `GET /api/admin/load`: เลือก run `load-run-select` (label · โหมด chat/stt/tts/voice · วันที่) · กราฟเส้น `load-chart` (แกน X = ผู้ใช้พร้อมกัน 1/2/4/8/16/32 · แกน Y = p50/p95 วินาที · เส้น TTFT p95 ในโหมด chat · แท่งความยาวคิวสูงสุด `queue_max`) · การ์ด `load-max-users` แสดง `max_users_ok` (ผู้ใช้พร้อมกันสูงสุดที่ยังผ่านเกณฑ์) ตัวเลขเดียว · ตารางต่อขั้น (users · n · errors · p50 · p95 · ttft · rtf · tokens/s · queue_max) · ขั้นที่ไม่ผ่านเกณฑ์เป็นสีแดง · กราฟใช้ SVG/CSS ไม่ใช้ไลบรารี

**data-testid ใหม่ของ v3** (testid ของ v2 ทุกตัวต้องยังอยู่และทำงานเหมือนเดิม — เคส v2 ทั้ง 42 เคสต้องผ่าน):

| ที่ | testid | หมายเหตุ |
|---|---|---|
| แชท | `voice-mic` | ปุ่มไมค์ |
| แชท | `chat-msg-voice` | ป้าย 🎙 ในฟองผู้ใช้ที่มาจากเสียง |
| แชท | `voice-mode` | สวิตช์ "คุยด้วยเสียง" |
| แชท | `mascot` | `data-state` = `idle\|listening\|thinking\|talking` · `data-mouth` = 0.00–1.00 · ข้างในเป็น `<canvas>` (WebGL) หรือ `<img>` (fallback) |
| `/admin/eval` | `eval-run-select` | `<select>` เลือก run |
| `/admin/eval` | `eval-metric` | `data-set` (`rag\|qa\|conv`) · `data-metric` (ชื่อ metric ข้อ 8) · ข้อความ = ค่าเป็น % |
| `/admin/eval` | `eval-item` | `data-id` · `data-pass` |
| `/admin/eval` | `eval-compare` | ตารางเทียบ 2 run |
| `/admin/load` | `load-run-select` | `<select>` เลือก run ของ load test |
| `/admin/load` | `load-chart` | กราฟ latency vs ผู้ใช้ (SVG) · `data-points` = จำนวนขั้น |
| `/admin/load` | `load-max-users` | ข้อความ = `max_users_ok` ของ run ที่เลือก |

## 4) สถาปัตยกรรมระบบ (backend)

```text
เบราว์เซอร์ ──► web (Next.js :3400) ──publish──► RabbitMQ ──► chat-worker ×N ──► LLM (Qwen · GPU-1 RTX 5090 บน Vast · หรือ mock-llm)
 🎙 ไมค์ ▲  SSE (รอคำตอบ)                         │  │  │  │       │ ▲  └──► GPU-3 ai-box /v1/rerank (top 20 → top 4 · RERANK_URL)
 🔊 + มาสคอต └──────── chat.reply ◄────────────────┘  │  │  │       ├─► PostgreSQL + pgvector (สินค้า · ตะกร้า · RAG chunks · eval_runs · load_runs)
                                                       │  │  │       └─► embedder (แปลงข้อความเป็นเวกเตอร์ · CPU)
                    admin อัปโหลด PDF ── rag.ingest ───┘  │  └── tts.request ──► tts-worker ×N ──► GPU-3 ai-box VoxCPM2 (TTS_URL)
                    อัดเสียงไมค์ ── stt.request ─────────┘ ──► stt-worker ×N ──► GPU-2 ai-box Whisper (STT_URL)
                    สั่งซื้อ ── order.events (fanout) ──► notify-worker (แจ้งเตือนหลังร้าน · สต็อกต่ำ)

1 คิวต่อ 1 GPU: chat.request → GPU-1 · stt.request → GPU-2 · tts.request → GPU-3 (rerank เรียกตรงจาก chat-worker)
ai-box = โค้ดชุดเดียว 2 เครื่อง · GPU-2 RTX 4090 `MODELS=stt` (Whisper) · GPU-3 RTX 4090 `MODELS=tts,rerank` (VoxCPM2 + bge-reranker-v2-m3)
         FastAPI พอร์ตเดียวต่อเครื่อง + API key เดียวกัน (โหมด mock: mock-llm ให้ API เดียวกันทั้งหมด)
```

**เส้นทาง "ถามด้วยเสียง → ตอบด้วยเสียง":** ไมค์ (webm) → `POST /api/voice` → `stt.request` → stt-worker → GPU-2 Whisper → ข้อความ → (เหมือนพิมพ์) `chat.request` → chat-worker (SQL + Hybrid RAG → GPU-3 rerank → GPU-1 Qwen สตรีม) → `chat.reply` → SSE → `tts.request` → tts-worker → GPU-3 VoxCPM2 → WAV → เบราว์เซอร์เล่น + มาสคอตขยับปาก · **เป้า: หยุดพูด → ได้ยินเสียงตอบ < 6 วินาที** (โหมด ai · วัดและรายงาน)

### 4.1 service ใน `docker compose` (ทั้งหมดอยู่บนเครื่องเรา ยกเว้น LLM และ ai-box)

| service | image / ภาษา | หน้าที่ |
|---|---|---|
| `web` | Next.js 14 · port **3400**→3000 | หน้าร้าน + API · **ไม่เรียก LLM/ai-box ตรง** ส่งงานเข้าคิวแล้วรอคำตอบ · env เพิ่ม `EVAL_TOKEN` (ค่าเริ่มต้น `bm-eval`) |
| `rabbitmq` | `rabbitmq:4-management` · 5672 · UI **15672** (`guest/guest` ใช้ในเครื่องเท่านั้น) | คิวข้อความกลางของทั้งระบบ |
| `chat-worker` | Node.js | รับ `chat.request` → ค้นสินค้าใน DB + ค้นเอกสาร (Hybrid RAG → **rerank**) → เรียก LLM → ทำ tag คำสั่ง → ตอบกลับคิว · env `RERANK_URL` `AIBOX_API_KEY` `RERANK` (`on`/`off` · ค่าเริ่มต้น `on`) `CHAT_PREFETCH` (4) · scale ได้ |
| `rag-worker` | Node.js หรือ Python | รับ `rag.ingest` → อ่าน PDF → ตัด chunk → ขอเวกเตอร์จาก `embedder` → บันทึกลง `doc_chunks` · ตอนเริ่มระบบ ingest PDF 6 ไฟล์จาก `/app/docs` (ข้อ 5) |
| `stt-worker` **(ใหม่)** | Node.js หรือ Python | รับ `stt.request` → ส่งไฟล์เสียงให้ GPU-2 `${STT_URL}/v1/audio/transcriptions` → ตอบข้อความกลับ · prefetch `STT_PREFETCH` (4) · **เริ่ม consume เมื่อ `${STT_URL}/health` ตอบ ok เท่านั้น** (ไม่งั้นปุ่มไมค์ซ่อนเอง) · ไม่มี profile (เปิดเสมอ) · scale ได้ |
| `tts-worker` | Node.js หรือ Python (เบา · ไม่มีโมเดลในตัว · ไม่มี profile เปิดเสมอ) | รับ `tts.request` → เรียก GPU-3 `${TTS_URL}/v1/audio/speech` (**VoxCPM2 อย่างเดียว**) → ได้ WAV แล้วตอบกลับ · prefetch `TTS_PREFETCH` (2) · scale ได้ |
| `notify-worker` | Node.js | รับ `order.events` → เขียนตาราง `notifications` (คำสั่งซื้อใหม่ · สต็อกต่ำ) |
| `embedder` | text-embeddings-inference (CPU) + โมเดลหลายภาษาที่รองรับไทย | แปลงข้อความเป็นเวกเตอร์ |
| `db` | `pgvector/pgvector:pg16` | PostgreSQL + pgvector · schema/seed ตอนเริ่มครั้งแรก |
| `mock-llm` | Node.js (profile `mock`) · port 8000 ใน network | LLM จำลอง **+ ai-box จำลอง** (STT · TTS จากเสียงที่อัดไว้ · rerank · ข้อ 4.6) ตอบแบบ deterministic · ใช้พัฒนา/ทดสอบโดยไม่ต้องเช่า GPU |

- ไฟล์ตั้งค่า (optional · `env_file: { path, required: false }` · ห้าม commit · ห้ามพิมพ์ค่าออกจอ/log): `.env.vast` (`LLM_BASE_URL` `LLM_MODEL` `LLM_API_KEY`) ให้ chat-worker · **`.env.aibox`** 4 บรรทัดไม่มี quote (`STT_URL` = GPU-2 · `TTS_URL` = GPU-3 · `RERANK_URL` = GPU-3 · `AIBOX_API_KEY` key เดียวกันทั้ง 2 เครื่อง) ให้ chat-worker · stt-worker · tts-worker
- ไม่มี `.env.aibox` → `STT_URL` `TTS_URL` `RERANK_URL` ค่าเริ่มต้นทั้งหมด `http://mock-llm:8000`

### 4.2 ทำไมต้องมี RabbitMQ (ออกแบบคิว)

LLM บน GPU 1 ใบรับงานพร้อมกันได้จำกัด (`--max-concurrency 4`) ถ้าเว็บยิงตรง ลูกค้าคนที่ 5 จะ error/timeout · คิวช่วย 4 อย่าง:
1. **พักงาน (buffer)** — ลูกค้า 20 คนถามพร้อมกัน งานเข้าคิวเรียงกัน worker ดึงทีละ `prefetch` เท่ากับที่ GPU รับไหว (แชท 4 = `--max-concurrency 4` ของ Qwen) ที่เกินรอในคิว ไม่ error
2. **ไม่หาย (durable)** — worker ล่ม/รีสตาร์ท ข้อความยังอยู่ในคิว worker กลับมาก็ทำต่อ (ack หลังทำเสร็จเท่านั้น)
3. **แยกส่วน (decouple)** — เว็บไม่ต้องรู้ว่า LLM/ai-box อยู่ที่ไหน · เพิ่ม worker ได้ทันที (`docker compose up --scale chat-worker=2`)
4. **งานหนักไม่ถ่วงเว็บ** — อ่าน PDF ทำเวกเตอร์ ถอดเสียง และสร้างเสียง ทำเบื้องหลัง

**กระจายโหลด 3 GPU ด้วย RabbitMQ (v3):**
- **1 คิวต่อ 1 GPU** — `chat.request` → GPU-1 Qwen · `stt.request` → GPU-2 Whisper · `tts.request` → GPU-3 VoxCPM2 · งานแต่ละชนิดรอในคิวของตัวเอง จึงไม่แย่งกัน (คนพูดพร้อมกันหลายคน STT ไม่ทำให้เสียงตอบช้า · แชทยาว ๆ ไม่ถ่วงการถอดเสียง)
- **prefetch = จำนวนงานพร้อมกันสูงสุดที่ GPU ใบนั้นรับไหว** ตั้งจาก env: `CHAT_PREFETCH` (ค่าเริ่มต้น 4) · `STT_PREFETCH` (4) · `TTS_PREFETCH` (2 · TTS หนักสุดในฝั่งเสียง) — ค่าต่อ worker 1 ตัว · ปรับตามผล load test (ข้อ 9)
- **scale worker** ด้วย `docker compose up -d --scale chat-worker=2 --scale stt-worker=2 --scale tts-worker=2` → RabbitMQ แจกงาน round-robin ให้ทุก consumer · งานพร้อมกันรวม = จำนวน worker × prefetch (อย่าให้เกินที่ GPU รับไหว · หรือชี้ worker อีกชุดไป GPU ใบที่ 2 ของงานเดียวกัน)
- ack หลังทำเสร็จ → worker/GPU ล่ม ข้อความกลับเข้าคิว · ล้มเกิน 2 ครั้ง → dead-letter

| ชื่อ | ชนิด | ใครส่ง → ใครรับ | ข้อความ (JSON) | หมายเหตุ |
|---|---|---|---|---|
| `chat.request` | queue (durable) | web → chat-worker | `{sessionId, messageId, text, lang?}` + property `reply_to` `correlation_id` | **RPC pattern** · prefetch `CHAT_PREFETCH` (4) · retry 2 ครั้ง แล้วไป `chat.dlq` |
| `chat.reply` | exchange `direct` | chat-worker / stt-worker / tts-worker → web | แชท: `{messageId, type:"status"\|"delta"\|"done"\|"error", text, cites[], cartCount, quoteNo}` · **`done` เพิ่ม `retrieved:[{filename,page,score}]`** (top 4 ที่ใส่ในพรอมต์จริง) และ **`products:[sku]`** (สินค้าที่ดึงจาก DB) | web ผูกคิวชั่วคราวของตัวเอง (routing key = instanceId) แล้วส่งต่อให้เบราว์เซอร์ทาง SSE (`done` ส่ง `retrieved` `products` ต่อด้วย) |
| `rag.ingest` | queue (durable) | web (admin upload) / ตอนเริ่มระบบ → rag-worker | `{docId}` | ตัวไฟล์อยู่ใน DB (bytea) ไม่ส่งไฟล์ในคิว · prefetch 1 |
| **`stt.request`** (ใหม่) | queue (durable) | web → stt-worker | `{audioB64, mime, lang?}` + `reply_to` `correlation_id` | reply `{type:"stt", text, language, durationMs}` หรือ `{type:"stt", error}` · prefetch `STT_PREFETCH` (4) · ไฟล์ ≤ 30 วิ / 2 MB |
| `tts.request` | queue (durable) | web → tts-worker | `{text, lang:"th"\|"en"}` + `reply_to` | reply `{type:"tts", audioId, durationMs, engine:"voxcpm2"\|"mock"}` · WAV ดึงจาก `/api/tts/<audioId>` · prefetch `TTS_PREFETCH` (2) |
| `order.events` | exchange `fanout` | web → ทุกคิวที่ผูก (เช่น `notify.orders`) | `{type:"order.created", orderNo, items[], branch}` | **pub/sub**: เพิ่มผู้ฟังใหม่ได้โดยไม่แก้เว็บ |
| `chat.dlq` | queue | ข้อความที่ล้มเกินจำนวนครั้ง | – | หลังร้านเห็นจำนวนใน dashboard |

**web API ที่เพิ่ม (v3):**
- `POST /api/voice` multipart field `audio` → ส่ง `stt.request` รอ ≤ 60 วิ → `{text, language, durationMs}` · ว่าง → 422 · ใหญ่เกิน → 413
- `GET /api/voice/status` → `{enabled}` (มี consumer ที่ `stt.request` ไหม · ตรวจด้วย `channel.checkQueue`)
- `POST /api/chat {text, lang?}` เดิม · SSE `done` เพิ่ม `retrieved` `products`
- `GET /api/admin/eval` → `{runs:[{id,label,created_at,config,summary}], latest:{…รวม items}}` · `?id=<n>` ได้ run นั้นเต็ม
- `POST /api/admin/eval` (cookie admin **หรือ** header `x-eval-token: ${EVAL_TOKEN:-bm-eval}`) body = `results.json` (ข้อ 8) → insert `eval_runs` → `{id}` · ไม่มี token/cookie → 401
- `GET /api/admin/load` → `{runs:[{id,label,created_at,config,max_users_ok}], latest:{…รวม stages}}` · `?id=<n>` ได้ run นั้นเต็ม
- `POST /api/admin/load` (cookie admin หรือ header `x-eval-token`) body = `loadtest/results/<label>.json` (ข้อ 9) → insert `load_runs` → `{id}` · ไม่มี token/cookie → 401

**Database เพิ่ม:**
```sql
eval_runs(id serial pk, label text, created_at timestamptz default now(), config jsonb, summary jsonb, items jsonb)
load_runs(id serial pk, label text, created_at timestamptz default now(), config jsonb, stages jsonb, max_users_ok int)
```

### 4.3 ทำไมต้องมี RAG · ออกแบบเป็น **Hybrid RAG + reranker**

ข้อมูลร้านมี 2 แบบ:
- **ข้อมูลมีโครงสร้าง** (ราคา สต็อก ค่าส่ง) → อยู่ในตาราง DB · บอทค้นด้วย SQL แล้วใส่ใน prompt (เหมือนเดิม) — **ตัวเลขต้องมาจาก DB เท่านั้น**
- **ข้อมูลในเอกสาร** (สเปก วิธีใช้ มาตรฐาน มอก. การเก็บรักษา การรับประกัน นโยบายคืนสินค้า) → อยู่ในไฟล์ PDF ยาว ๆ (6 ไฟล์ × 18–22 หน้า) ใส่ prompt ทั้งหมดไม่ได้ → ใช้ **RAG**: ค้นเฉพาะย่อหน้าที่เกี่ยว แล้วแนบให้โมเดลพร้อมบอกแหล่งอ้างอิง

**Hybrid** = รวมผลค้น 2 วิธี แล้วจัดอันดับใหม่ด้วย **RRF** (Reciprocal Rank Fusion · `score = Σ 1/(60+rank)`):
1. **ค้นตามความหมาย** (vector · pgvector cosine) — ถาม "ปูนเก็บได้นานแค่ไหน" เจอย่อหน้า "อายุการเก็บรักษา"
2. **ค้นตามคำ** (keyword · `pg_trgm` similarity) — จับรหัส/คำเฉพาะได้แม่น เช่น `DB12` `มอก.24` `THW`

**Reranker (v3):** เอา RRF **top 20** → ส่ง `{query, documents:[เนื้อหา chunk 20 อัน], top_n:4}` ให้ GPU-3 `${RERANK_URL}/v1/rerank` (bge-reranker-v2-m3 · cross-encoder อ่านคำถามคู่กับย่อหน้าทีละคู่ จึงแม่นกว่าเวกเตอร์) → ใช้ **top 4** ตาม `relevance_score` · `RERANK=off` หรือ ai-box ล่ม/ช้าเกิน 5 วิ → ใช้ top 4 ของ RRF (log คำเตือน ห้ามทำให้แชทล้ม) · โหมด mock: rerank คืนลำดับเดิม

chunk ละ ~500 ตัวอักษร ซ้อนกัน 80 · เก็บ `filename` + `page` เพื่อทำป้ายอ้างอิง · **chunk ของแถวตารางต้องมีชื่อตาราง + หัวคอลัมน์ทุกชั้น/หัวแถวติดไปด้วย** (ตารางหัว 2 ชั้น เซลล์รวม ตารางข้ามหน้า) · ตรวจว่าข้อความไทยที่ดึงจาก PDF สระ/วรรณยุกต์ไม่เพี้ยนก่อนทำเวกเตอร์

### 4.4 แชทบอท "น้องช่าง" (chat-worker)

- พูดสุภาพลงท้าย "ครับ" ตอบภาษาไทย (ลูกค้าพิมพ์/พูดอังกฤษ → ตอบอังกฤษ)
- ก่อนเรียก LLM: ① ค้นสินค้าที่เกี่ยวข้องจาก DB (ชื่อ/SKU/ราคา/สต็อก) จากคำถาม **+ ประวัติ 10 ข้อความล่าสุด** ② Hybrid RAG + rerank จากเอกสาร (ข้อ 4.3) ③ ใส่ข้อมูลร้านข้อ 1 + ตะกร้าปัจจุบันของ session (sku/จำนวน/น้ำหนัก) · **ห้ามแต่งราคาหรือสินค้าที่ไม่มีใน DB และห้ามแต่งข้อมูลสเปกที่ไม่มีในเอกสาร**
- **บทสนทนาหลายรอบ**: ส่ง **ประวัติ 10 ข้อความล่าสุด** ของ session (user + assistant ที่ตัด tag แล้ว) ให้ LLM ทุกครั้ง · คำที่อ้างถึงรอบก่อน ("อันนั้น" "ตัวนั้น" "ตัวเมื่อกี้" "แล้วถ้า…ล่ะ" "ใส่ตะกร้าให้หน่อย") ต้องหมายถึงสินค้า/ตัวเลขล่าสุดที่คุยกัน · ใช้ประวัติช่วยค้น RAG ด้วย (ต่อคำถามสั้นเข้ากับหัวข้อรอบก่อนก่อนค้น เช่น "แล้วถ้าเป็น DB16 ล่ะ" → ค้น "ระยะทาบ DB16")
- ใช้ **tag คำสั่ง** ในคำตอบของโมเดล แล้ว worker ทำงานจริง:
  - `[CALC]{"type":"concrete","volume":3}` → คำนวณด้วยฟังก์ชันเดียวกับ `/calculator` แล้วส่งผลให้โมเดลตอบต่อ (วนไม่เกิน 2 รอบ)
  - `[ADD_TO_CART]{"sku":"CEM-001","qty":21}` → เพิ่มลงตะกร้าจริง แล้วตอบยืนยัน
  - `[QUOTE]{}` → สร้างใบเสนอราคาจากตะกร้า แล้วตอบพร้อมเลข QT
  - ตัด tag และ `<think>…</think>` ออกก่อนแสดงผล
- คำถามนอกเรื่อง (การเมือง ทำการบ้าน เขียนโค้ด) → ปฏิเสธสุภาพและชวนกลับมาเรื่องวัสดุก่อสร้าง
- **โหมด** `MODE=ai` เรียก LLM จริง (OpenAI-compatible: `LLM_BASE_URL` `LLM_MODEL` `LLM_API_KEY` จาก `.env.vast`) · `MODE=mock` ใช้ `mock-llm` (รองรับ tag ทั้ง 3 ตัว · ตอบจาก chunk RAG ที่ได้รับ · **ตามบริบทหลายรอบได้**: หา SKU/จำนวนล่าสุดจากประวัติเมื่อเจอ "อันนั้น/ตัวเมื่อกี้/แล้วถ้า…ล่ะ" · แปลงคำตัวเลขไทยพื้นฐาน เช่น "ร้อยถุง" = 100 · "หกสิบคูณหกสิบ" = 60x60 · "สองจุดห้า" = 2.5)
- `done` ส่ง `retrieved` (top 4 ที่ใส่ในพรอมต์ · filename/page/score) และ `products` (SKU ที่ใส่ในพรอมต์) เสมอ — ใช้วัด Hit@4/MRR (ข้อ 8)
- timeout 90 วินาที · ถ้า LLM ล่มให้ตอบขอโทษ ไม่ใช่ error 500

### 4.5 เสียง: ฟัง (stt-worker) + พูด (tts-worker)

**ฟัง (STT)**
- stt-worker รับ `{audioB64, mime, lang?}` → `POST ${STT_URL}/v1/audio/transcriptions` (GPU-2) (multipart `file` + `language` · header `Authorization: Bearer ${AIBOX_API_KEY}`) timeout 30 วิ → `{type:'stt', text, language, durationMs}`
- ตัดช่องว่างหัวท้าย · ข้อความว่าง → `{type:'stt', text:''}` (web ตอบ 422)
- Whisper บน GPU-2 (`MODELS=stt` · ตัวเดียวในใบ): faster-whisper `large-v3` หรือ `large-v3-turbo` (int8_float16) — **วัด CER ไทยกับไฟล์เสียงทดสอบ V01–V10 ทั้ง 2 รุ่นแล้วเลือก** (บันทึกผลในรายงาน) · ใส่ `initial_prompt` คำเฉพาะร้าน (ปูน เหล็กข้ออ้อย DB12 THW เบรกเกอร์ เกรียงฟัน) ช่วยให้ถอดรหัสสินค้าถูก

**พูด (TTS)**
- **VoxCPM2 อย่างเดียว** ผ่าน GPU-3 `${TTS_URL}/v1/audio/speech` `{input, voice:'nongchang', response_format:'wav', language}` — เสียง "น้องช่าง" เดียวกันทั้งไทยและอังกฤษ (โคลนจาก `voices/nongchang.wav` 5–15 วิ + ข้อความอ้างอิงในไฟล์นั้น) · **เลิกใช้ Kokoro/PyThaiTTS แล้ว** (ไม่มี TTS สำรองบน CPU)
- โหมด mock: `TTS_URL` = mock-llm ซึ่งเล่น**เสียง VoxCPM2 ที่อัดไว้แล้ว** จาก `e2e/voice-fixtures/tts-cache/` (sha256 ของข้อความ → `<sha256>.wav` · ไม่เจอ → `generic.wav`) · reply บอก `engine` (`voxcpm2` / `mock`) · TTS_URL ล่ม/ตอบผิด → reply `{type:'tts', error}` (ปุ่ม 🔊 แจ้ง "สร้างเสียงไม่ได้" แชทไม่ล้ม)
- ส่ง `language` ตามตัวอักษร: มีอักษรไทย (U+0E00–U+0E7F) → `th` · ไม่มี → `en`
- ตัด emoji / tag / markdown / ป้ายอ้างอิงออกก่อนสร้างเสียง · อ่านเลข SKU/ตัวเลขให้เป็นคำอ่าน (เช่น 137.75 → "หนึ่งร้อยสามสิบเจ็ดจุดเจ็ดห้า") · ข้อความยาวเกิน 600 ตัวอักษรอ่านแค่ 600 ตัวแรก
- ไม่มี consumer ที่ `tts.request` (tts-worker หยุด) → ปุ่ม 🔊 / `tts-auto` / `voice-mode` ซ่อนอัตโนมัติ (ระบบที่เหลือทำงานปกติ · ไมค์ยังถามได้ ตอบเป็นข้อความ)

### 4.6 AI บน Vast.ai — **GPU 3 ใบ**

| เครื่อง | GPU | รันอะไร | ทำไม |
|---|---|---|---|
| 🧠 **GPU-1 "สมอง"** | **RTX 5090** 32 GB | **Qwen บน NInfer ตัวเดียว (ใบนี้ไม่รันอย่างอื่น)** · ใช้ VRAM ~24 GB | nvfp4 ใช้ได้เฉพาะการ์ด Blackwell · KV cache ต้องพอให้ 4 คนพร้อมกัน · LLM เป็นคอขวด ถ้าแชร์ใบจะช้าทั้งระบบ |
| 👂 **GPU-2 "หู"** | **RTX 4090** 24 GB | **`ai-box` `MODELS=stt`**: **Whisper** (faster-whisper large-v3 หรือ turbo) **ตัวเดียว** · ~3–6 GB | เสียงเข้ามาพร้อมกันหลายคน → ใบเดียวรับได้หลาย stream ไม่ต้องแย่ง compute กับ TTS |
| 🗣️ **GPU-3 "ปาก + จัดอันดับ"** | **RTX 4090** 24 GB | **`ai-box` `MODELS=tts,rerank`**: **VoxCPM2** (~8 GB) + **bge-reranker-v2-m3** (~2 GB) | TTS หนักสุดในฝั่งเสียง (สร้างเสียงยาว) · reranker เล็กและเร็ว แชร์ใบเดียวได้ |

ทำไมไม่รวม: ทุกอย่างบน 5090 → 24 + ~12 GB > 32 GB ล้น · Whisper + VoxCPM2 + reranker บน 4090 ใบเดียว VRAM พอ แต่ตอนคนพูดพร้อมกัน STT กับ TTS แย่ง compute → เสียงตอบช้า (ยืนยันด้วย load test ข้อ 9) · Qwen บน 4090 ไม่ได้ (nvfp4 ของ NInfer ไม่รองรับ Ada)

**GPU-1 (Qwen):**
- เช่า **RTX 5090** ผ่าน skill `vastai` · รัน **Qwen** ด้วย [NInfer](https://github.com/Neroued/ninfer) (เปิด API แบบ OpenAI + API key)
- **อ่านวิธีติดตั้งจาก GitHub ของ NInfer เอง** (README) แล้วเลือกโมเดล Qwen สำหรับ NInfer จาก Hugging Face `neroued` · เขียนค่าเชื่อมต่อ 3 บรรทัดลง `.env.vast` (`LLM_BASE_URL` `LLM_MODEL` `LLM_API_KEY`)

**GPU-2 + GPU-3 (ai-box):** โค้ด**ชุดเดียว**อยู่ในโฟลเดอร์ `vast_aibox/` (ข้างโฟลเดอร์แอป) — `app.py` (FastAPI) · `requirements.txt` · `setup.sh` (ติดตั้ง + ดาวน์โหลดโมเดล + สตาร์ต) · `voices/nongchang.wav` + `voices/nongchang.txt` · `README.md` · เลือกโมเดลด้วย env **`MODELS`**: GPU-2 `MODELS=stt` · GPU-3 `MODELS=tts,rerank` · เครื่องเดียว/local dev `MODELS=all`
- เช่า **RTX 4090 × 2** ผ่าน skill `vastai` · แต่ละเครื่องเปิดพอร์ตเดียว (เช่น 8800) · สุ่ม `AIBOX_API_KEY` 1 ค่าใช้ทั้ง 2 เครื่อง · เขียน `.env.aibox` 4 บรรทัด: `STT_URL=http://<ip GPU-2>:<port ที่ Vast map>` · `TTS_URL=http://<ip GPU-3>:<port>` · `RERANK_URL=http://<ip GPU-3>:<port>` · `AIBOX_API_KEY=…`
- **อ่านวิธีติดตั้ง VoxCPM2 / faster-whisper / bge-reranker-v2-m3 จาก GitHub / Hugging Face ของแต่ละตัวเอง** · โหลดโมเดลตาม `MODELS` ครบตอนสตาร์ต (ไม่ใช่ตอนเรียกครั้งแรก) · endpoint ของโมเดลที่ไม่ได้โหลด → 404 · `/health` บอก `models` ที่โหลด (ตัวที่ไม่โหลด = `null`) · แต่ละโมเดลมี semaphore ของตัวเอง (ค่าเริ่มต้น STT 4 · TTS 2 · rerank 4 · ให้ตรงกับ prefetch)
- ทุก endpoint (ยกเว้น `/health`) ต้องมี `Authorization: Bearer <AIBOX_API_KEY>` ไม่งั้น 401 · ห้าม log ค่า key

| endpoint | รับ | คืน |
|---|---|---|
| `GET /health` | – | `{status:'ok', models:{stt, tts, rerank}, vram_mb}` |
| `POST /v1/audio/transcriptions` | multipart `file` (webm/ogg/wav/mp3) · `language` (`th`/`en`/ว่าง = auto) | `{text, language, duration}` (รูปแบบ OpenAI) |
| `POST /v1/audio/speech` | JSON `{input, voice:'nongchang', response_format:'wav', language?}` | `audio/wav` |
| `POST /v1/rerank` | JSON `{query, documents:[string], top_n}` | `{results:[{index, relevance_score}]}` (เรียงมาก→น้อย) |

**โหมด mock (ฟรี · ไม่เช่า GPU):** `mock-llm` ให้ API เดียวกับ ai-box เพิ่ม (พอร์ต 8000 · ไม่ตรวจ key)
- `/v1/audio/transcriptions`: ① sha256 ของไฟล์ตรงกับ `e2e/voice-fixtures/index.json` (`{"<sha256>": {"text", "language", "file", "durationMs"}}`) → คืนข้อความนั้น ② ไม่ตรง (เช่นเสียงที่อัดผ่าน MediaRecorder เป็น webm) → ถอดเป็น PCM 16 kHz mono ด้วย ffmpeg แล้วเทียบกับไฟล์ fixture ทุกไฟล์: ความยาวต่างกัน ≤ 0.4 วิ และ correlation ของ RMS envelope (เฟรม 50 ms) ≥ 0.8 → คืนข้อความของไฟล์ที่ใกล้สุด ③ ไม่เจอ → `{text:''}` · `index.json` และไฟล์ fixture copy เข้า image ตอน build (`additional_contexts`)
- `/v1/rerank`: คืนลำดับเดิม (score ลดหลั่น) · `/v1/audio/speech`: เล่น**เสียง VoxCPM2 ที่อัดไว้แล้ว** `e2e/voice-fixtures/tts-cache/<sha256(input)>.wav` ถ้ามี ไม่งั้น `tts-cache/generic.wav` (ประโยคทั่วไปของน้องช่าง) · สคริปต์ `e2e/make-tts-cache.mjs` สร้าง cache จาก GPU-3 จริง (คำตอบของ mock-llm ทุกเคสในเพลย์ลิสต์) แล้ว commit · `/health`: `{status:'ok', models:{stt:'mock', tts:'mock', rerank:'mock'}}`

| โหมด | LLM | STT | TTS | rerank |
|---|---|---|---|---|
| `mock` (ฟรี) | mock-llm | mock-llm (เทียบไฟล์เสียงทดสอบ) | mock-llm เล่นเสียง VoxCPM2 ที่อัดไว้ (`tts-cache`) | ลำดับเดิม |
| `ai` | GPU-1 Qwen | GPU-2 Whisper | GPU-3 VoxCPM2 | GPU-3 bge-reranker-v2-m3 |

- **เพดานราคา: 5090 ≤ $1.20/ชม. · 4090 ≤ $0.50/ชม. ต่อใบ** (รวม 3 ใบประมาณ $1.6–1.9/ชม. · ไม่เกิน $2.20/ชม.) · ใช้เสร็จต้อง **ลบเครื่องทั้ง 3 ใบ (destroy)** และสรุปค่าใช้จ่ายแยกเครื่องเสมอ
- **ต้องวัดจริงและรายงาน:** VRAM ของ GPU-2 (Whisper) และ GPU-3 (VoxCPM2 + reranker) แยกใบ (`/health` `vram_mb` + `nvidia-smi`) · Whisper large-v3 vs turbo: CER ไทยของ V01–V10 + เวลาต่อประโยค · VoxCPM2: RTF (เวลาสร้าง ÷ ความยาวเสียง) · เวลา หยุดพูด → ได้ยินเสียงตอบ (เป้า < 6 วิ) · ผล load test ทั้ง 4 โหมด (ข้อ 9 · ผู้ใช้พร้อมกันสูงสุดต่อ GPU + prefetch ที่แนะนำ) · ผลประเมิน RAG มี/ไม่มี reranker

## 5) เอกสารสินค้า (PDF · แหล่งข้อมูลของ RAG)

**ไม่ต้องสร้าง PDF แล้ว** — ใช้ **6 ไฟล์ที่ให้มาในโฟลเดอร์ `documents/`** (ชั้นแรกของ LAB ข้างไฟล์นี้) **ห้ามแก้ไฟล์เหล่านี้**: `BM-DS-CEM.pdf` (ปูนและคอนกรีต) · `BM-DS-STL.pdf` (เหล็กเสริม) · `BM-DS-PNT.pdf` (สี) · `BM-DS-TIL.pdf` (กระเบื้อง) · `BM-DS-ELC-PIP.pdf` (ไฟฟ้าและประปา) · `BM-POLICY.pdf` (นโยบายร้าน)
- แต่ละไฟล์ยาว **18–22 หน้า A4** แบบเอกสารเทคนิคจริง (ไทย · สารบัญ · เลขหน้า) มีทั้งเนื้อหาเชิงเทคนิค ตารางสเปกตาม SKU (ตรงกับ seed ข้อ 2) FAQ อภิธานศัพท์ และ**ตารางที่อ่านยาก**: หัวตาราง 2–3 ชั้น · เซลล์รวม (rowspan/colspan) · ตารางยาวข้ามหน้า (หัวซ้ำ) · ตารางเมทริกซ์ (แถว × คอลัมน์ → ค่า) · เชิงอรรถ (¹ ² ใต้ตาราง) · ตารางเปรียบเทียบหลายรุ่น · บางข้อเท็จจริงต้องอ่าน**ข้ามหน้า**
- **ระบบต้อง ingest ไฟล์จากโฟลเดอร์นี้**: copy เข้า image ตอน build (แนะนำ · ตรงกฎห้าม bind mount) — compose ของ worker/web ใส่ `build.additional_contexts: { documents: ../../documents }` (path จาก `my_buildmart/app`) แล้ว Dockerfile `COPY --from=documents *.pdf /app/docs/` · หรือ mount อ่านอย่างเดียว `../../documents:/app/docs:ro` (ข้อยกเว้นเดียวของกฎห้าม bind mount) · ตอนเริ่มระบบครั้งแรก insert ลงตาราง `docs` แล้วส่ง `rag.ingest` ทุกไฟล์ · หน้า `/admin/docs` ต้องเห็นครบ 6 ไฟล์สถานะ `ready`
- ระบบ RAG ต้องดึงข้อความจากตารางพวกนี้ให้ถูก (chunk ของแถวตารางต้องมีหัวคอลัมน์/หัวแถวติดไปด้วย ไม่งั้นตัวเลขลอย ๆ ไม่มีความหมาย)
- **ข้อมูลในเอกสารต้องอยู่ใน PDF เท่านั้น** ห้ามใส่ใน DB หรือ system prompt — บอทต้องตอบได้เพราะ RAG · **ราคา/สต็อกอยู่ใน DB เท่านั้น** (PDF ไม่มีราคา/สต็อก → คำถามราคา/สต็อกใช้ทดสอบ SQL)

**ตัวอย่างข้อเท็จจริงที่ต้องตอบได้** (อยู่ใน PDF แน่นอน · เคส R01–R08, M, V ใช้):

| ไฟล์ | ข้อเท็จจริง |
|---|---|
| `BM-DS-CEM.pdf` ปูนและคอนกรีต | **ตารางอัตราการใช้ปูนกาว CEM-004** (หัว 2 ชั้น: ขนาดกระเบื้อง × ขนาดฟันเกรียง · เซลล์รวม): กระเบื้อง **60×60 ซม. ใช้เกรียงฟัน 10 มม. อัตรา 5.5 กก./ตร.ม.** (30×30 → เกรียง 6 มม. 3.5 กก. · 30×60 → 8 มม. 4.5 กก.) · CEM-001 ผ่าน **มอก.15** ประเภท 1 · กำลังอัดที่ 28 วัน ≥ **325 กก./ตร.ซม.** · **เก็บได้ 3 เดือน**นับจากวันผลิต วางบนพาเลทสูงจากพื้น 10 ซม. ซ้อนไม่เกิน 10 ถุง · คอนกรีตต้อง**บ่มชื้นอย่างน้อย 7 วัน** · CEM-004 ปูนกาว ใช้ให้หมดภายใน **2 ชั่วโมง**หลังผสม เดินได้หลัง 24 ชม. |
| `BM-DS-STL.pdf` เหล็กเสริม | DB12/DB16 ชั้นคุณภาพ **SD40** มาตรฐาน **มอก.24-2559** กำลังครากไม่ต่ำกว่า 4,000 กก./ตร.ซม. · RB6/RB9 ชั้น **SR24** มอก.20-2559 · ระยะทาบเหล็กอย่างน้อย **40 เท่าของเส้นผ่านศูนย์กลาง** (DB12 → **48 ซม.**, DB16 → 64 ซม.) · เก็บเหล็กยกจากพื้น ไม่ให้โดนฝน |
| `BM-DS-PNT.pdf` สี | PNT-001 ภายนอก **รับประกัน 8 ปี** · PNT-002 ภายใน รับประกัน 5 ปี · ทาเที่ยวที่ 2 ห่างจากเที่ยวแรก **2 ชั่วโมง** · ผนังปูนใหม่ต้องรอ **28 วัน**ก่อนทารองพื้น PNT-003 · ผสมน้ำไม่เกิน 10% |
| `BM-DS-TIL.pdf` กระเบื้อง | TIL-001 พอร์ซเลนเกรด A **ดูดซึมน้ำ < 0.5%** ปูพื้นภายนอกได้ ค่ากันลื่น **R10** · TIL-002 สำหรับ**ผนังเท่านั้น ห้ามปูพื้น** · เว้นร่องยาแนว 2–3 มม. · ยาแนว TIL-003 รอ 24 ชม. ก่อนโดนน้ำ |
| `BM-DS-ELC-PIP.pdf` ไฟฟ้าและประปา | สาย THW 2.5 ตร.มม. รับกระแสได้ **21 A** ใช้คู่**เบรกเกอร์ 16–20 A** · เบรกเกอร์ ELC-002 **รับประกัน 2 ปี** · ท่อ PVC ชั้น 13.5 ใช้**น้ำดี/น้ำประปา** · ชั้น 8.5 ใช้**น้ำทิ้ง** · กาวทาท่อ รอ **1 ชั่วโมง**ก่อนเปิดน้ำ |
| `BM-POLICY.pdf` นโยบายร้าน | **คืนสินค้าได้ภายใน 7 วัน** สภาพเดิมพร้อมใบเสร็จ · **ปูนที่เปิดถุงแล้วคืนไม่ได้** · เหล็กที่สั่งตัดคืนไม่ได้ · สมาชิก **BuildMart Pro** ได้ 1 แต้มต่อทุก 100 บาท (100 แต้ม = ส่วนลด 50 บาท) · รับประกันสินค้าไฟฟ้าตามผู้ผลิต |

ไฟล์สำหรับทดสอบการอัปโหลด (ทีมสร้างเอง 1 หน้า · **ไม่อยู่ใน `documents/`** · เก็บไว้ที่ `tests/fixtures/BM-PROMO-NOV.pdf`): **"โปรเดือนพฤศจิกายน: ซื้อปูน CEM-001 ครบ 100 ถุง แถมลวดผูกเหล็ก STL-005 2 ม้วน"**

## 6) เทคนิค (บังคับ)

- Next.js 14 (App Router) + TypeScript + `pg` + `amqplib` · ไม่ใช้ UI library ใหญ่ · **3D: `three` + `@react-three/fiber` 8.x + `@react-three/drei` 9.x** (รุ่นที่เข้ากับ React 18 · ล็อกเวอร์ชันใน package.json · bloom ใช้ `@react-three/postprocessing` 2.x ได้) — เป็นไลบรารีเดียวที่อนุญาตเพิ่ม
- `docker compose` ไฟล์เดียว build ได้ทั้งระบบ · ห้ามใช้ bind mount (ข้อมูล seed / fixtures ให้ `COPY` ใน Dockerfile · PDF ใช้ `additional_contexts` ตามข้อ 5) · ทุก service มี healthcheck และ `depends_on: condition: service_healthy`
- port บนเครื่อง: `3400` (เว็บ) · `15672` (RabbitMQ UI) · นอกนั้นไม่ต้องเปิดออกนอก (ผูก `127.0.0.1` ถ้าเปิด)
- ตัวแปร: `.env.example` (MODE, LLM_*, STT_URL, TTS_URL, RERANK_URL, AIBOX_API_KEY, RERANK, CHAT_PREFETCH, STT_PREFETCH, TTS_PREFETCH, EVAL_TOKEN, ADMIN_PASSWORD, DATABASE_URL, AMQP_URL) · `.env` / `.env.vast` / `.env.aibox` ห้าม commit
- คำสั่ง:
  - ฟรี (mock): `docker compose --profile mock up -d --build` (LLM/STT/TTS/rerank = mock-llm · tts-worker เปิดเสมอ ไม่มี profile อื่น)
  - AI จริง: วาง `.env.vast` + `.env.aibox` (4 บรรทัด) แล้ว `docker compose up -d --build`
  - ขยาย worker: `docker compose up -d --scale chat-worker=2 --scale stt-worker=2 --scale tts-worker=2` · ปรับ prefetch: `CHAT_PREFETCH=4 STT_PREFETCH=4 TTS_PREFETCH=2` (ใน `.env`)
  - ปิด reranker เพื่อเทียบ: `RERANK=off docker compose up -d chat-worker`
- **ไฟล์เสียงทดสอบ** `e2e/voice-fixtures/`: `questions.json` (`[{id, lang, text, accept:[คำถอดที่ยอมรับ], file}]`) · `V01.wav`…`V10.wav` · `index.json` (sha256 → `{text, language, file, durationMs}` · ให้ mock-llm) · `make-fixtures.mjs` (สร้างใหม่ได้) · `tts-cache/` (`<sha256(ข้อความ)>.wav` + `generic.wav` · เสียงตอบ VoxCPM2 "น้องช่าง" ที่อัดไว้ให้โหมด mock · สร้างด้วย `make-tts-cache.mjs`)
  - รูปแบบไฟล์: WAV mono 16-bit 48 kHz · เงียบหน้า 0.3 วิ ท้าย 0.6 วิ · normalize ความดัง (ffmpeg `loudnorm` −16 LUFS) · ความยาวแต่ละไฟล์ต่างกัน ≥ 0.5 วิ (mock แยกไฟล์ด้วยความยาวได้)
  - ที่มาของเสียงคำถาม: **VoxCPM2 บน GPU-3 ด้วยเสียง "ลูกค้า"** (โคลนจากไฟล์เสียงอ้างอิงลูกค้า · **ไม่ใช่ `nongchang`** เพื่อไม่ให้เสียงคำถามกับเสียงตอบเหมือนกัน) หรือคนอัดจริง · สร้างแล้ว commit ไว้ (ไม่สร้างใหม่ทุกรอบ ให้ผล mock คงที่)

  | ไฟล์ | ภาษา | ข้อความ |
  |---|---|---|
  | V01 | th | ปูนซีเมนต์ CEM-001 เก็บได้นานแค่ไหน |
  | V02 | th | ถ้าซื้อร้อยถุงราคาส่งเท่าไร |
  | V03 | th | ใส่ตะกร้าให้หน่อย |
  | V04 | th | ปูกระเบื้องหกสิบคูณหกสิบ ใช้เกรียงฟันกี่มิล |
  | V05 | th | แล้วต้องใช้ปูนกาวกี่กิโลต่อตารางเมตร |
  | V06 | th | สาขารังสิตมีเหล็กข้ออ้อย DB12 เหลือกี่เส้น |
  | V07 | th | สายไฟ THW สองจุดห้า ใช้คู่กับเบรกเกอร์กี่แอมป์ |
  | V08 | en | What is the warranty of the exterior paint? |
  | V09 | th | แล้วส่งด้วยรถอะไร ค่าส่งเท่าไร |
  | V10 | th | ขอใบเสนอราคาด้วย |

- **Playwright ไมค์ปลอม**: launch Chromium ด้วย `--use-fake-ui-for-media-stream --use-fake-device-for-media-stream` (อนุญาตไมค์อัตโนมัติ · ไม่มีป๊อปอัป) + `context.grantPermissions(['microphone'])` · **ใส่เสียงคำถามด้วย init script** `e2e/fixtures/fake-mic.ts` (`page.addInitScript`) ที่ห่อ `navigator.mediaDevices.getUserMedia` ให้คืน `MediaStream` จาก `AudioContext.createMediaStreamDestination()` ที่เล่นไฟล์ fixture ที่เลือกด้วย `window.__setMicFile('V02.wav')` (ไฟล์เสิร์ฟผ่าน `page.route`) → เปลี่ยนไฟล์ได้ทุกรอบในหน้าเดียว/วิดีโอเดียว · ⚠️ อย่าใช้ `--use-file-for-fake-audio-capture` เป็นวิธีหลัก: ทดสอบแล้วตำแหน่งเล่นไม่เริ่มใหม่ทุกครั้งที่อัด และ `%noloop` ไม่เสถียร (ได้เสียงไม่ตรงไฟล์)
- **Playwright WebGL**: headless ใช้ SwiftShader — เติม `--enable-unsafe-swiftshader --use-angle=swiftshader` · เคส fallback (D03) ใช้ `--disable-webgl --disable-3d-apis`
- e2e ต้องมี `ffmpeg` (รวมเสียงเข้า MP4 · ตรวจเสียงด้วย `silencedetect`)

## 7) เกณฑ์ทดสอบ (Playwright "เพลย์ลิสต์" · ทุกข้อมี test + วิดีโอ → GIF)

- วิดีโอทุกเคส **ช้าพอให้คนดูทัน**: พิมพ์ทีละตัว (delay ~60 ms) · หลังได้ผลแต่ละขั้น **ค้างภาพ 3–5 วินาที** · เคส TTS ต้องได้ **MP4 ที่มีเสียงพูดจริง** (เอาไฟล์ WAV ที่ระบบสร้างมารวมกับวิดีโอด้วย ffmpeg ตรงเวลาที่กดเล่น) · **เคสเสียง V ต้องได้ MP4 ที่มีทั้งเสียงคำถาม (ไฟล์ fixture ตรงเวลาที่กดไมค์) และเสียงตอบ (WAV ตรงเวลาที่เล่น)** — ตรวจด้วย ffmpeg `silencedetect` ว่ามีช่วงมีเสียง ≥ 2 ช่วงต่อรอบ · GIF ไม่มีเสียง
- test บันทึกเวลาเริ่มอัด/เริ่มเล่นเสียง (วินาทีนับจากเริ่มวิดีโอ) ลงผลทดสอบ ไว้ให้ขั้นทำ MP4 ใช้
- ทุกเคสผ่านทั้ง `MODE=mock` และ `MODE=ai` (ตอนใช้ AI จริง ตรวจแบบยืดหยุ่น: มีตัวเลข/คำสำคัญที่ถูกต้อง) ยกเว้นที่ระบุ

**เว็บ (W)**

| # | ทดสอบ | ผ่านเมื่อ |
|---|---|---|
| W01 | ค้นหา "ปูน" | เจอ CEM-001…004 อย่างน้อย 4 รายการ |
| W02 | กรองหมวด "เหล็ก" + เรียงราคาสูง→ต่ำ | รายการแรกคือ STL-004 |
| W03 | หน้า STL-003 | ตารางราคาส่ง 195 / 185.25 / 175.50 และสต็อก 3 สาขา |
| W04 | หน้า CEM-002 | สาขารังสิตแสดง "หมด" |
| W05 | คำนวณคอนกรีต 3 ลบ.ม. | ปูน 21 ถุง · ทราย 2 ลบ.ม. · หิน 3 ลบ.ม. → เพิ่มลงตะกร้าได้ 3 รายการ |
| W06 | คำนวณกระเบื้อง 50 ตร.ม. | TIL-001 39 กล่อง · ปูนกาว 13 ถุง · ยาแนว 10 ถุง |
| W07 | คำนวณสี 120 ตร.ม. 2 เที่ยว ภายนอก | PNT-001 8 แกลลอน + รองพื้น 3 แกลลอน |
| W08 | ตะกร้า STL-003 × 60 | ราคาต่อเส้น 185.25 (ลด 5%) |
| W09 | ตะกร้า CEM-001 × 100 + คูปอง BUILD5 | ราคาส่ง 137.75 → 13,775 · หลังคูปอง 13,086.25 · น้ำหนัก 5,000 กก. → รถ 6 ล้อ 1,500 · VAT 1,021.04 · ยอดสุทธิ 15,607.29 |
| W10 | ตะกร้าหนัก > 6,000 กก. (AGG-003 × 4) | ใช้รถ 10 ล้อ ค่าส่ง 3,500 |
| W11 | ขอใบเสนอราคา | ได้เลข QT-… หน้าใบเสนอราคาแสดงรายการและยอดตรงตะกร้า |
| W12 | สั่งซื้อ → ติดตาม | ได้เลข BM-… สต็อกสาขาที่เลือกลดลง และ `/track` แสดง "รับคำสั่งซื้อ" |
| W13 | สั่งเกินสต็อก (BRK-003 สาขารังสิต) | แจ้งเตือนของไม่พอ และสั่งไม่ได้ |
| W14 | หลังร้าน: เปลี่ยนสถานะเป็น "กำลังจัดส่ง" | `/track` ของคำสั่งซื้อนั้นแสดงขั้น "กำลังจัดส่ง" |

**แชทบอท (C)**

| # | ผู้ใช้พิมพ์ | ผ่านเมื่อ |
|---|---|---|
| C01 | ร้านเปิดกี่โมงครับ | มี 07:00 และ 18:00 |
| C02 | วันอาทิตย์เปิดไหม | มี 08:00 และ 12:00 |
| C03 | ปูนซีเมนต์ถุงละเท่าไร | มี 145 |
| C04 | เหล็ก DB12 มีกี่สาขาที่มีของ | ตอบสต็อกตรง DB (3 สาขา) |
| C05 | ถ้าซื้อเหล็ก DB12 60 เส้น ได้ราคาเท่าไร | มี 185.25 |
| C06 | เทพื้นคอนกรีต 3 คิว ต้องใช้ปูนกี่ถุง | มี 21 (ผ่าน `[CALC]`) |
| C07 | (ต่อจาก C06) ใส่ตะกร้าให้เลย | ตะกร้ามี CEM-001 × 21 และตัวเลขบนไอคอนตะกร้าเพิ่ม |
| C08 | ขอใบเสนอราคาหน่อย | ได้เลข QT- |
| C09 | ส่งของน้ำหนัก 5 ตันใช้รถอะไร ค่าส่งเท่าไร | รถ 6 ล้อ 1,500 |
| C10 | มีโค้ดส่วนลดไหม | มี BUILD5 และ CONTRACTOR10 |
| C11 | มีกระเบื้องยางขายไหม (ไม่มีใน DB) | บอกว่าไม่มี ไม่แต่งสินค้า |
| C12 | ช่วยเขียนโค้ด Python ให้หน่อย | ปฏิเสธสุภาพ ชวนกลับเรื่องวัสดุ |
| C13 | ทาสีบ้านภายนอก 120 ตร.ม. ใช้สีกี่แกลลอน → (ต่อ) แล้วราคารวมเท่าไร | มี 8 แกลลอน และ 7,120 (8 × 890) |
| C14 | สาขาบางนาเบอร์อะไร | มี 02-111-0002 |

**เอกสาร · RAG (R)** — ข้อมูลเหล่านี้มีแค่ใน PDF (ข้อ 5) · ต้องมีป้ายอ้างอิง `chat-cite` ชี้ไฟล์ที่ถูก

| # | ผู้ใช้พิมพ์ / ทำ | ผ่านเมื่อ |
|---|---|---|
| R01 | ปูนซีเมนต์เก็บได้นานแค่ไหนครับ | มี "3 เดือน" · อ้างอิง `BM-DS-CEM.pdf` |
| R02 | สีทาภายนอกรับประกันกี่ปี | มี 8 ปี · อ้างอิง `BM-DS-PNT.pdf` |
| R03 | กระเบื้อง TIL-001 ปูพื้นนอกบ้านได้ไหม | ได้ · มี 0.5% หรือ R10 · อ้างอิง `BM-DS-TIL.pdf` |
| R04 | ซื้อปูนไปแล้วเปิดถุง ขอคืนได้ไหม | ตอบว่าคืนไม่ได้ · อ้างอิง `BM-POLICY.pdf` |
| R05 | ทาบเหล็ก DB12 ต้องยาวเท่าไร | มี 48 · อ้างอิง `BM-DS-STL.pdf` |
| R06 | สาย THW 2.5 ใช้กับเบรกเกอร์กี่แอมป์ แล้วเบรกเกอร์ 16A ราคาเท่าไร | มี 16 และ 145 (**Hybrid**: สเปกจาก PDF + ราคาจาก DB) |
| R08 | ปูกระเบื้อง 60x60 ด้วยปูนกาว ต้องใช้เกรียงฟันกี่มิล และใช้ปูนกาวกี่กิโลต่อตารางเมตร | มี 10 และ 5.5 (**อ่านจากตารางหัว 2 ชั้น**) · อ้างอิง `BM-DS-CEM.pdf` |
| R07 | หลังร้านอัปโหลด `BM-PROMO-NOV.pdf` → รอสถานะ `ready` → ถาม "เดือนพฤศจิกายนมีโปรอะไร" | มี "ลวดผูกเหล็ก" · อ้างอิง `BM-PROMO-NOV.pdf` |

**คิว RabbitMQ (Q)**

| # | ทำอะไร | ผ่านเมื่อ |
|---|---|---|
| Q01 | เปิดแชท 8 หน้าต่างพร้อมกัน ถามพร้อมกัน | ได้คำตอบครบ 8 · ไม่มี error · หน้า RabbitMQ UI (`:15672`) เห็นคิว `chat.request` มี consumer |
| Q02 | หยุด `chat-worker` → ถาม "ปูนซีเมนต์ถุงละเท่าไร" → เห็นสถานะ "รอคิว" → เปิด `chat-worker` กลับ | ข้อความไม่หาย ได้คำตอบที่มี 145 |
| Q03 | สั่งซื้อ 1 รายการที่ทำให้สต็อกต่ำกว่าจุดสั่งซื้อซ้ำ | หลังร้านมีแจ้งเตือน "คำสั่งซื้อใหม่ BM-…" และ "สต็อกต่ำ" (มาจาก `order.events`) |

**อ่านออกเสียง (T)** — tts-worker เปิดเสมอ (ไม่มี profile) · วิดีโอต้องได้ยินเสียง

| # | ทำอะไร | ผ่านเมื่อ |
|---|---|---|
| T01 | ถาม "ร้านเปิดกี่โมงครับ" → กด 🔊 | ได้ไฟล์เสียง WAV ยาว > 1 วินาที (ภาษาไทย) และเล่นในหน้าเว็บ · `engine` = `voxcpm2` (ai) / `mock` (mock · เสียง VoxCPM2 จาก `tts-cache`) |
| T02 | ถาม "How much is Portland cement?" → กด 🔊 | ตอบภาษาอังกฤษ · เสียงยาว > 1 วินาที · `engine` = `voxcpm2` (ai) / `mock` (mock) |
| T03 | เปิดสวิตช์ "อ่านออกเสียงอัตโนมัติ" → ถาม "มีโค้ดส่วนลดไหม" | เล่นเสียงเองโดยไม่ต้องกด |

**บทสนทนาหลายรอบ (M)** — พิมพ์ทุกรอบใน session เดียว (หน้าต่างแชทเดียว · ตะกร้าเริ่มว่าง) · **ทุกบท 5 รอบ (ขั้นต่ำ 4)** · **ต้องผ่านทุกรอบ** · คำถามอ้างถึงรอบก่อนต้องตีความถูก · ค้างภาพ 3 วิหลังแต่ละรอบ

| # | รอบ | ผู้ใช้พิมพ์ | ผ่านเมื่อ (คำตอบที่คาด) |
|---|---|---|---|
| M01 | 1 | ปูกระเบื้อง 60x60 ต้องใช้เกรียงฟันกี่มิล | มี 10 (มม.) · อ้างอิง `BM-DS-CEM.pdf` |
| | 2 | ปูนกาวอันนั้นถุงละเท่าไร | หมายถึง CEM-004 · มี 185 |
| | 3 | ถ้าซื้อ 60 ถุงล่ะ | ราคาส่ง 175.75/ถุง (ลด 5%) · รวม 10,545 |
| | 4 | ใส่ตะกร้าให้เลย | ตะกร้ามี CEM-004 × 60 · `nav-cart-count` เพิ่ม |
| | 5 | ขอใบเสนอราคาด้วย | ได้เลข QT- · ใบเสนอราคามี CEM-004 × 60 |
| M02 | 1 | ทาบเหล็ก DB12 ต้องยาวเท่าไร | มี 48 (ซม.) · อ้างอิง `BM-DS-STL.pdf` |
| | 2 | แล้วถ้าเป็น DB16 ล่ะ | มี 64 (ซม.) · อ้างอิง `BM-DS-STL.pdf` |
| | 3 | ตัวเมื่อกี้ถ้าซื้อ 200 เส้น ได้ราคาเส้นละเท่าไร | หมายถึง STL-004 · มี 306 (ลด 10%) · รวม 61,200 |
| | 4 | สาขาไหนมีของพอบ้าง | ทั้ง 3 สาขา: ลาดกระบัง 400 · บางนา 300 · รังสิต 200 (ตรง DB ขณะทดสอบ) |
| | 5 | ใส่ตะกร้า 200 เส้นตามนั้นเลย | ตะกร้ามี STL-004 × 200 · `nav-cart-count` เพิ่ม |
| M03 | 1 | สีทาภายนอกรับประกันกี่ปี | มี 8 ปี · อ้างอิง `BM-DS-PNT.pdf` |
| | 2 | ผนัง 120 ตร.ม. ทา 2 เที่ยว ต้องใช้สีตัวนั้นกี่แกลลอน | มี 8 (PNT-001 · ผ่าน `[CALC]`) |
| | 3 | ทาเที่ยวที่สองต้องรอนานเท่าไร | มี 2 ชั่วโมง · อ้างอิง `BM-DS-PNT.pdf` |
| | 4 | ใส่ตะกร้าให้ตามจำนวนนั้น | ตะกร้ามี PNT-001 × 8 |
| | 5 | ถ้าเป็นผนังปูนใหม่ ต้องรอกี่วันก่อนทารองพื้น | มี 28 วัน · อ้างอิง `BM-DS-PNT.pdf` |
| M04 | 1 | เทพื้นคอนกรีต 5 คิว ต้องใช้ปูนกี่ถุง | มี 35 (ผ่าน `[CALC]`) |
| | 2 | ใส่ตะกร้าให้เลย | ตะกร้ามี CEM-001 × 35 |
| | 3 | ต้องบ่มคอนกรีตกี่วัน | มี 7 วัน · อ้างอิง `BM-DS-CEM.pdf` |
| | 4 | ของที่ใส่ตะกร้าเมื่อกี้หนักรวมเท่าไร ส่งด้วยรถอะไร | มี 1,750 กก. · รถ 6 ล้อ · 1,500 บาท |
| | 5 | ขอใบเสนอราคาด้วย | ได้เลข QT- · ใบเสนอราคามี CEM-001 × 35 |
| M05 | 1 | สายไฟ THW 2.5 ใช้กับเบรกเกอร์กี่แอมป์ | มี 16 (16–20 A) · อ้างอิง `BM-DS-ELC-PIP.pdf` |
| | 2 | เบรกเกอร์ตัวนั้นร้านมีขายไหม ราคาเท่าไร | ELC-002 · มี 145 |
| | 3 | รับประกันกี่ปี | มี 2 ปี · อ้างอิง `BM-DS-ELC-PIP.pdf` |
| | 4 | เอา 10 ตัว ใส่ตะกร้าให้หน่อย | ตะกร้ามี ELC-002 × 10 |
| | 5 | ยอดสุทธิรวมค่าส่งและ VAT เท่าไร | ยอดสินค้า 1,450 · กระบะ 500 · VAT 136.50 · ยอดสุทธิ 2,086.50 |
| M06 | 1 | กระเบื้อง TIL-001 ปูพื้นนอกบ้านได้ไหม | ได้ · มี 0.5% หรือ R10 · อ้างอิง `BM-DS-TIL.pdf` |
| | 2 | พื้นที่ 50 ตร.ม. ต้องใช้กี่กล่อง | มี 39 (ผ่าน `[CALC]`) |
| | 3 | ใส่ตะกร้าให้หน่อย | ตะกร้ามี TIL-001 × 39 (ใส่ปูนกาว 13 / ยาแนว 10 ด้วยก็ผ่าน) |
| | 4 | ถ้าไม่ได้ใช้ ขอคืนได้ภายในกี่วัน | มี 7 วัน (สภาพเดิม + ใบเสร็จ) · อ้างอิง `BM-POLICY.pdf` |
| | 5 | ยอดในตะกร้าตอนนี้ใช้คูปองอะไรได้ | BUILD5 ได้ (ยอด ≥ 5,000) · CONTRACTOR10 ไม่ได้ (ต้อง ≥ 30,000) |

**เสียง (V)** — ใส่เสียงคำถามด้วยไมค์ปลอม (ข้อ 6) · เปิด `voice-mode` ก่อนถาม · **V02 และ V03 เป็นบทสนทนาเสียง 4 รอบ** (session เดียว · ตะกร้าเริ่มว่าง) · **ทุกรอบต้องผ่านครบ 5 ข้อ**: ① ฟองผู้ใช้ที่มี `chat-msg-voice` แสดงข้อความถอดที่ถูก (mock: ตรงข้อความใน `questions.json` · ai: CER ≤ 0.25 เทียบข้อความหรือ `accept` ตัวที่ใกล้สุด หลัง normalize ข้อ 8) ② บอทตอบถูกตามตาราง ③ `chat-audio` เล่นเสียงตอบเองยาว > 1 วิ ④ `mascot` ผ่าน `listening → thinking → talking` และ `data-mouth` > 0 อย่างน้อยครั้งหนึ่งระหว่าง talking แล้วกลับ `idle` ⑤ MP4 มีเสียงคำถามและเสียงตอบ · บันทึกเวลา "หยุดพูด → เริ่มเล่นเสียงตอบ" ทุกรอบ (เป้า ai < 6 วิ · ไม่ใช่เกณฑ์ผ่าน)

| # | รอบ | ไฟล์เสียง (พูด) | ผ่านเมื่อ (คำตอบที่คาด) |
|---|---|---|---|
| V01 | 1 | V01 "ปูนซีเมนต์ CEM-001 เก็บได้นานแค่ไหน" | มี 3 เดือน · อ้างอิง `BM-DS-CEM.pdf` |
| V02 | 1 | V01 "ปูนซีเมนต์ CEM-001 เก็บได้นานแค่ไหน" | มี 3 เดือน |
| (เสียงหลายรอบ) | 2 | V02 "ถ้าซื้อร้อยถุงราคาส่งเท่าไร" | หมายถึง CEM-001 · มี 137.75 (ลด 5%) · รวม 13,775 |
| | 3 | V03 "ใส่ตะกร้าให้หน่อย" | ตะกร้ามี CEM-001 × 100 · `nav-cart-count` เพิ่ม |
| | 4 | V09 "แล้วส่งด้วยรถอะไร ค่าส่งเท่าไร" | น้ำหนัก 5,000 กก. → รถ 6 ล้อ · 1,500 บาท |
| V03 | 1 | V04 "ปูกระเบื้องหกสิบคูณหกสิบ ใช้เกรียงฟันกี่มิล" | มี 10 · อ้างอิง `BM-DS-CEM.pdf` |
| (เสียงหลายรอบ) | 2 | V05 "แล้วต้องใช้ปูนกาวกี่กิโลต่อตารางเมตร" | มี 5.5 · อ้างอิง `BM-DS-CEM.pdf` |
| | 3 | V02 "ถ้าซื้อร้อยถุงราคาส่งเท่าไร" | หมายถึงปูนกาว CEM-004 · มี 175.75 · รวม 17,575 |
| | 4 | V03 "ใส่ตะกร้าให้หน่อย" | ตะกร้ามี CEM-004 × 100 |
| V04 | 1 | V06 "สาขารังสิตมีเหล็กข้ออ้อย DB12 เหลือกี่เส้น" | ตัวเลขตรงสต็อก STL-003 สาขา RST ใน DB ขณะทดสอบ (seed = 400) · ถอดได้ `DB12` (หรือ "DB 12") |
| V05 | 1 | V07 "สายไฟ THW สองจุดห้า ใช้คู่กับเบรกเกอร์กี่แอมป์" | มี 16 (16–20 A) · อ้างอิง `BM-DS-ELC-PIP.pdf` |
| V06 | 1 | V08 "What is the warranty of the exterior paint?" | ตอบอังกฤษ · มี 8 (years) · อ้างอิง `BM-DS-PNT.pdf` · เสียงตอบยาว > 1 วิ (`engine` = `voxcpm2` ใน ai / `mock` ใน mock) |

**3D + มาสคอต (D)**

| # | ทำอะไร | ผ่านเมื่อ |
|---|---|---|
| D01 | เปิด `/` → เลื่อนหน้าลง 600 px → เปิดแชท | หน้าแรกมี `<canvas>` ที่ได้ WebGL context · ภาพในฉากไม่ใช่สีเดียว (screenshot ของ canvas มีสีต่างกัน > 5% ของพิกเซล) · screenshot ก่อน/หลังเลื่อนต่างกัน (กล้องเคลื่อน) · `mascot` มี `<canvas>` และ `data-state="idle"` · ไม่มี error ใน console |
| D02 | ติดตัวบันทึก `data-state` (MutationObserver) → เปิด `tts-auto` แล้วพิมพ์ "ร้านเปิดกี่โมงครับ" → จากนั้นถามด้วยเสียง V01 (`voice-mode` เปิด) | ลำดับที่บันทึกได้: พิมพ์ = `idle → thinking → talking → idle` · เสียง = `idle → listening → thinking → talking → idle` · ระหว่าง talking `data-mouth` เปลี่ยนค่า ≥ 5 ครั้ง และมีค่า > 0.1 · จบเสียงแล้ว `data-mouth` = 0 |
| D03 | launch Chromium ด้วย `--disable-webgl --disable-3d-apis` → เปิด `/` → ค้นหา "ปูน" → เปิดแชท ถาม "ร้านเปิดกี่โมงครับ" | หน้าแรกแสดงรูป `banner-hero` แทนฉาก 3D (ไม่มี `<canvas>`) · ไม่มีข้อความ error บนจอ · ค้นหาเจอ CEM-* · `mascot` แสดง `<img>` 2D และ `data-state` ยังเปลี่ยน `thinking → idle` · แชทตอบมี 07:00 |

**ประเมิน RAG · dashboard (E)** — ใช้ไฟล์ผลประเมินตัวอย่าง `e2e/fixtures/eval-run-a.json` (rerank on) และ `eval-run-b.json` (rerank off) ที่รู้ค่าแน่นอน (รูปแบบ `results.json` ข้อ 8 · มีครบ 3 ชุด · มีข้อผิด ≥ 3 ข้อ)

| # | ทำอะไร | ผ่านเมื่อ |
|---|---|---|
| E01 | `POST /api/admin/eval` (header `x-eval-token`) ด้วย run A → ล็อกอินหลังร้าน → เปิด `/admin/eval` | ได้ `{id}` · มี `eval-metric` ครบทุกคู่ชุด×metric ใน summary (rag 5 · qa 3 · conv 2–3) และค่าที่แสดงตรงกับไฟล์ (ปัดเป็น % 1 ตำแหน่ง) · มีกราฟต่อเอกสาร 6 ไฟล์ · ไม่ส่ง token/ cookie → 401 |
| E02 | POST run B → เลือก 2 run เทียบกัน | `eval-run-select` มีทั้ง 2 run · `eval-compare` แสดงค่าทั้ง 2 run และผลต่างของทุก metric ถูกต้อง (เช่น Hit@4 A − B) |
| E03 | เลือก run A → ติ๊ก "เฉพาะข้อผิด" → กดขยายข้อแรก | เหลือเฉพาะ `eval-item` ที่ `data-pass="false"` จำนวนเท่ากับในไฟล์ · ขยายแล้วเห็นคำถาม คำตอบที่คาด คำตอบจริง และเหตุผล (`reason`) |

**Load test · dashboard (L)** — ใช้ไฟล์ผล load test ตัวอย่าง `e2e/fixtures/load-run-a.json` (โหมด chat · 6 ขั้น 1→32 · รู้ค่า `max_users_ok` แน่นอน · ขั้น 32 ไม่ผ่านเกณฑ์) · รูปแบบตามข้อ 9

| # | ทำอะไร | ผ่านเมื่อ |
|---|---|---|
| L01 | `POST /api/admin/load` (header `x-eval-token`) ด้วย run A → ล็อกอินหลังร้าน → เปิด `/admin/load` | ได้ `{id}` · `load-run-select` มี run A · `load-chart` มีจุดครบ 6 ขั้น (`data-points="6"`) · `load-max-users` แสดงค่าเท่ากับ `max_users_ok` ในไฟล์ · ขั้นที่ไม่ผ่านเป็นสีแดง · ไม่ส่ง token/cookie → 401 |
| L02 | รัน `node loadtest/run_load.mjs --mode chat --users 1,2,4 --stage-sec 15 --label e2e-mini` กับระบบที่รันอยู่ (mock ได้) → เปิด `/admin/load` แล้วเลือก run `e2e-mini` | สคริปต์จบ exit 0 และ POST สำเร็จ · `load-run-select` มี `e2e-mini` · `load-chart` มี 3 ขั้น · ทุกขั้น `errors` = 0 · `load-max-users` แสดงตัวเลข (≥ 1 ในโหมด mock) |

**รายงาน:** `TEST_REPORT.md` ตารางสรุป "โหมด | ผ่าน / ทั้งหมด" ไว้บนสุด (แยกกลุ่ม W C R Q T M V D E L · รวม **62 เคส** = W14 C14 R8 Q3 T3 M6 (30 รอบ) V6 (12 รอบ) D3 E3 L2) แล้วตารางทุกเคส (กลุ่ม · โหมด · ผล · เวลา · คำตอบจริงของบอท · เคส M/V แสดงทุกรอบ · เคส V แสดงข้อความถอด + CER + engine + เวลาหยุดพูด→ได้ยิน) + `test-gifs/<เคส>.gif` ทุกเคส + `test-videos/<เคส>.mp4` (เคส T และ V มีเสียง)

## 8) ประเมิน RAG (`eval/` · ใหม่ใน v3)

เป้าหมาย: วัดเป็นตัวเลขว่าแชทบอทค้นเอกสารถูก อ้างอิงถูก ตอบถูก และไม่แต่ง — แล้วเทียบ **มี/ไม่มี reranker** (และ mock vs ai) บน dashboard `/admin/eval`

### 8.1 ชุดคำถาม `eval/qa.json` — 3 ชุด: `rag` 150–170 ข้อ · `qa` 70–80 ข้อ · `conv` 10–12 บท

| ชุด (`set`) | จำนวน | เนื้อหา | ฟิลด์ที่ต้องมี |
|---|---|---|---|
| `rag` จากเอกสาร | **150–170** | ทุกไฟล์ PDF ≥ 20 ข้อ · ประเภท (`type`) ครบ: `text` (ย่อหน้า) · `table2` (ตารางหัว 2–3 ชั้น) · `merged` (เซลล์รวม) · `footnote` (เชิงอรรถ) · `crosspage` (ข้ามหน้า) อย่างละ ≥ 20 ข้อ · `negative` 8–10 ข้อ (ไม่มีในเอกสาร → ต้องตอบว่าไม่มีข้อมูล ไม่แต่ง) | `id` `question` `expected` `key_facts:[...]` `sources:[{filename,page}]` `type` |
| `qa` คำถามปกติ (ไม่ต้องใช้ PDF) | **70–80** | ราคา · ราคาส่ง 3 ขั้น · สต็อกรายสาขา · คูปอง · ค่าส่ง/รถ · ยอดสุทธิรวม VAT (หาด้วย **SQL**) · ข้อมูลร้าน/เวลาเปิด/สาขา/เบอร์โทร · คำนวณวัสดุ (`[CALC]`) · คำถามนอกเรื่องที่ต้องปฏิเสธ · ระบุ `type` (`price` `wholesale` `stock` `coupon` `shipping` `store` `calc` `offtopic`) | `id` `question` `expected` `expected_values:[...]` `sql` (คำสั่งที่ใช้หาคำตอบจาก seed · ข้อ store/calc/offtopic ไม่ต้องมี) `type` |
| `conv` หลายรอบ | **10–12 บท × 4–6 รอบ** (ขั้นต่ำ 4) | ผสมเอกสาร + DB + ตะกร้า · มีคำอ้างถึงรอบก่อน · **≥ 3 บทเป็นเสียง** (`audio` = ไฟล์ใน `e2e/voice-fixtures/`) | `id` `turns:[{text \| audio, expected, key_facts \| expected_values, sources?}]` |

- `id`: `RAG-001…` `QA-01…` `CONV-01…` · เขียนจากการ**อ่าน PDF จริง** (ดึงข้อความด้วย pypdf/pdfjs แล้วยืนยันเลขหน้าทุกข้อ) · ตัวเลขของชุด qa คำนวณจาก seed ข้อ 2 + กติกาข้อ 1 (รัน `sql` กับ DB จริงยืนยันทุกข้อ) · ห้ามคัดคำถามซ้ำกับเคส R/M/V ทั้งหมด (ซ้ำได้ ≤ 10 ข้อ)

### 8.2 metric (ทุกตัวอยู่ในช่วง 0..1 · dashboard แสดงเป็น %)

| ชุด | metric | ความหมายสั้น ๆ | คิดอย่างไร |
|---|---|---|---|
| rag | `hit_at_4` | หน้าที่มีคำตอบ ถูกค้นเจอใน 4 ย่อหน้าที่ส่งให้ LLM ไหม | **Hit@4 = (1/N) · Σᵢ 𝟙[ ∃ r ∈ retrievedᵢ(top 4) : (r.filename, r.page) ∈ sourcesᵢ ]** · โค้ด |
| rag | `mrr` | หน้าที่ถูกอยู่อันดับต้นแค่ไหน | **MRR = (1/N) · Σᵢ 1/rankᵢ** · rankᵢ = อันดับแรก (1–4) ใน `retrieved` ที่ตรง `sources` · ไม่เจอ = 0 · โค้ด |
| rag | `citation_acc` | ป้าย 📄 ที่ให้ผู้ใช้ชี้ถูกที่ไหม | ต่อข้อ = 1 ถ้ามี cite ≥ 1 อันที่ (filename, page) ตรง `sources` **และ**ไม่มี cite จากไฟล์ที่ไม่อยู่ใน `sources` · ไม่งั้น 0 · เฉลี่ยทุกข้อ · โค้ด |
| rag | `faithfulness` | ทุกข้อความในคำตอบมีหลักฐานในย่อหน้าที่ค้นได้ (ไม่แต่ง) | ผู้ตัดสิน (LLM judge) แยกคำตอบเป็นข้อกล่าวอ้าง → **จำนวนที่มีหลักฐาน ÷ จำนวนทั้งหมด** |
| rag / qa / conv | `correctness` | คำตอบถูกตามข้อเท็จจริงหลัก | ผู้ตัดสิน: 1 = `key_facts`/ตัวเลขครบและถูก · 0.5 = ถูกบางส่วน · 0 = ผิด/ไม่ตอบ (conv = เฉลี่ยทุกรอบ) |
| qa | `exact_value` | ตัวเลขจาก DB ตรงเป๊ะ | ต่อข้อ = 1 ถ้า**ทุก**ค่าใน `expected_values` อยู่ในคำตอบ (normalize: ตัด `,` และช่องว่าง · 137.75 = 137.750 · "13,775" = 13775) · ข้อที่ไม่มี `expected_values` (offtopic) ไม่นับ · โค้ด |
| qa | `sql_correct` | บอทดึงข้อมูลถูกตาราง/ถูกสินค้า | ต่อข้อ = 1 ถ้า `products` ใน `done` มี SKU ทุกตัวที่ `sql` ของข้อนั้นอ้างถึง (ข้อราคา/สต็อก) · ข้อคูปอง/ค่าส่ง = ตัวเลขกติกาข้อ 1 ตรง · ข้อที่ไม่มี `sql` ไม่นับ · โค้ด |
| conv | `context_retention` | รอบหลังเข้าใจคำอ้างถึงรอบก่อน ("อันนั้น" "ตัวเมื่อกี้") | ผู้ตัดสิน: ตั้งแต่รอบที่ 2 · **จำนวนรอบที่ตีความสิ่งที่อ้างถึงถูก ÷ จำนวนรอบที่ 2 ขึ้นไป** |
| conv (เสียง) | `stt_cer` | Whisper ถอดเสียงผิดกี่ % (ยิ่งต่ำยิ่งดี) | **CER = (S + D + I) / N** — S แทนที่ · D หาย · I เกิน (ระดับตัวอักษร · Levenshtein) · N = จำนวนตัวอักษรของข้อความจริง · normalize ก่อน: ตัดช่องว่าง/เครื่องหมาย · ตัวพิมพ์เล็ก · เลขไทย→อารบิก · ใช้ค่าต่ำสุดเทียบข้อความหลักกับ `accept` · โค้ด |

- ข้อ `negative`: ไม่นับใน `hit_at_4` `mrr` `citation_acc` (ไม่มี sources) · `correctness` = 1 เมื่อบอกว่าไม่มีข้อมูลและไม่แต่ง
- `pass` ต่อข้อ: rag = `correctness` = 1 และ (`hit_at_4` = 1 หรือ negative) · qa = `correctness` = 1 และ (`exact_value` = 1 หรือไม่มี `expected_values`) · conv = ทุกรอบ `correctness` = 1 · `reason` = เหตุผลสั้น ๆ ภาษาไทยเมื่อไม่ผ่าน (เช่น "ไม่พบหน้า 7 ของ BM-DS-CEM ใน top 4" / "ตอบ 64 แทน 48")
- `summary`: `{rag:{hit_at_4, mrr, citation_acc, faithfulness, correctness, n}, qa:{exact_value, sql_correct, correctness, n}, conv:{context_retention, correctness, stt_cer?, n}}` + แยก `by_doc` (hit_at_4 ต่อไฟล์) และ `by_type` (correctness ต่อ `type` ของ rag และ qa)

### 8.3 ขั้นตอน + ไฟล์

1. **`eval/run_eval.mjs`** `--base http://localhost:3400 --label ai-rerank-on [--sets rag,qa,conv] [--concurrency 2]` → ถามผ่าน `POST /api/chat` (SSE) **session ใหม่ต่อข้อ/ต่อบท** (cookie jar ใหม่) · รอบที่เป็นเสียง: `POST /api/voice` ด้วยไฟล์ fixture ก่อน → ได้ข้อความ → ส่งแชท · เก็บ `text` `cites` `retrieved` `products` `transcript` เวลา · ดึงข้อความหน้า PDF ของ `retrieved` จาก `documents/` แนบเป็น `context` (ให้ผู้ตัดสินใช้ตรวจ faithfulness) · คำนวณ metric ที่ใช้โค้ดได้ (`hit_at_4` `mrr` `citation_acc` `exact_value` `stt_cer`) → `eval/out/<label>/answers.json`
2. **ผู้ตัดสิน** = AI ที่รันพรอมต์ (Claude) อ่าน `answers.json` + `eval/JUDGE.md` (เกณฑ์ให้คะแนน + ตัวอย่าง) แล้วเขียน `eval/out/<label>/judgments.json` (`{<id>:{faithfulness?, correctness, context_retention?, reason}}`) · ไม่ใช้ Qwen ตัดสินตัวเอง
3. **`eval/score.mjs`** `--label …` รวม answers + judgments → `eval/out/<label>/results.json` แล้ว `POST /api/admin/eval` (header `x-eval-token`)
   - `results.json`: `{label, config:{llm, rerank, stt, tts}, summary:{…}, items:[{id, set, question|turns, expected, answer, retrieved, cites, metrics:{…}, pass, reason}]}`
4. รันอย่างน้อย 2 run ใน `MODE=ai`: `RERANK=on` และ `RERANK=off` → dashboard เทียบกัน · เขียนสรุป `eval/REPORT.md` (ตาราง metric 2 run · ผลต่าง · 5 ข้อที่ reranker ช่วย/ทำให้แย่ · ข้อสังเกตเรื่องตารางหัว 2 ชั้น/ข้ามหน้า)
- โหมด mock รัน `run_eval.mjs` ได้ (ใช้ทดสอบสคริปต์ · ค่า rerank on/off จะเท่ากันเพราะ mock คืนลำดับเดิม)

## 9) Load test — รับผู้ใช้พร้อมกันได้กี่คน (`loadtest/` · ใหม่ใน v3)

เป้าหมาย: รู้ว่าระบบ (web → RabbitMQ → worker → GPU) รับผู้ใช้พร้อมกันได้กี่คนต่อ GPU โดยยังเร็วพอ · ได้ค่า prefetch / จำนวน worker ที่แนะนำ · ยิงผ่าน**ทางเดียวกับผู้ใช้จริง** (web API) ไม่ยิงตรงเข้า GPU

**สคริปต์** `loadtest/run_load.mjs --base http://localhost:3400 --mode chat|stt|tts|voice --users 1,2,4,8,16,32 --stage-sec 120 --label <ชื่อ> [--criteria loadtest/criteria.json]`
- ผู้ใช้จำลองแต่ละคน = session (cookie jar) ของตัวเอง ยิงต่อเนื่องตลอดขั้น (ได้คำตอบแล้วถามต่อทันที) · ขั้นละ `--stage-sec` วินาที (ค่าเริ่มต้น 120) เพิ่มผู้ใช้ 1 → 2 → 4 → 8 → 16 → 32
- อ่านความยาวคิว `chat.request` `stt.request` `tts.request` จาก RabbitMQ management API (`:15672/api/queues`) ทุก 2 วิ → เก็บค่าสูงสุดต่อขั้น
- ใช้ Node 22 ล้วน (`fetch` + อ่าน SSE เอง) ไม่ต้องลงไลบรารีเพิ่ม

| โหมด | ยิงอะไร | วัด |
|---|---|---|
| `chat` (L1 · GPU-1 Qwen) | `POST /api/chat` คำถามสุ่มจาก `eval/qa.json` (rag + qa) | **TTFT** (เวลาถึง `delta` แรก) p50/p95 · เวลาจบ (`done`) p50/p95 · tokens/s รวม · ความยาวคิว `chat.request` |
| `stt` (L2 · GPU-2 Whisper) | `POST /api/voice` ไฟล์ `e2e/voice-fixtures/V*.wav` (3–8 วิ) | เวลาถอดความ p50/p95 · RTF (เวลา ÷ ความยาวเสียง) · ความยาวคิว `stt.request` |
| `tts` (L3 · GPU-3 VoxCPM2) | `POST /api/tts` คำตอบ 1–3 ประโยค | เวลาได้เสียง p50/p95 · RTF · ความยาวคิว `tts.request` |
| `voice` (L4 · ครบวง) | `/api/voice` → `/api/chat` → `/api/tts` ต่อกัน | เวลาจากส่งเสียงถึงได้ WAV คำตอบ p50/p95 · ความยาวทั้ง 3 คิว |

**ผล** `loadtest/results/<label>.json`:
```json
{"label":"ai-chat-p4","config":{"mode":"chat","base":"…","prefetch":{"chat":4,"stt":4,"tts":2},"workers":{"chat":1,"stt":1,"tts":1},"criteria":{"p95_s":5,"error_rate":0}},
 "stages":[{"users":1,"n":42,"errors":0,"p50":1.8,"p95":2.6,"ttft_p50":0.6,"ttft_p95":0.9,"rtf":null,"tokens_per_s":38.5,"queue_max":0,"pass":true}, …],
 "max_users_ok":8}
```
- เกณฑ์ผ่านต่อขั้น (ค่าเริ่มต้นใน `loadtest/criteria.json` แก้ได้): chat → `ttft_p95` < 5 วิ · stt → `p95` < 3 วิ · tts → `p95` < 5 วิ · voice → `p95` < 8 วิ · ทุกโหมด error 0%
- **`max_users_ok`** = จำนวนผู้ใช้มากที่สุดของขั้นที่ผ่านเกณฑ์ (ทุกขั้นก่อนหน้าต้องผ่านด้วย · ไม่มีขั้นผ่าน = 0)
- จบแล้ว POST เข้า `POST /api/admin/load` (header `x-eval-token`) → ตาราง `load_runs` → หน้า `/admin/load` (ข้อ 3.17 · testid `load-run-select` `load-chart` `load-max-users`)

**ต้องรันและรายงาน (`loadtest/REPORT.md`, `MODE=ai`):** ครบ 4 โหมด ด้วยค่าเริ่มต้น (`CHAT_PREFETCH=4` `STT_PREFETCH=4` `TTS_PREFETCH=2` · worker ละ 1) → ตาราง `max_users_ok` ต่อโหมด/ต่อ GPU + กราฟ · ลองอย่างน้อย 1 การปรับ (เช่น `--scale tts-worker=2` หรือเปลี่ยน prefetch) แล้วเทียบ · สรุปค่า prefetch/จำนวน worker ที่แนะนำ และ GPU ใบไหนเป็นคอขวด · โหมด mock รันได้ (ใช้ทดสอบสคริปต์และหน้า dashboard · ตัวเลขไม่สะท้อน GPU จริง)
