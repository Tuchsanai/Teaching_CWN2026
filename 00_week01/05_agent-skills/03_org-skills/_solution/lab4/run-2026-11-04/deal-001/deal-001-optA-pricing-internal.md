# คิดราคา (ภายใน) — ระบบจองคิวสาขาและพยากรณ์ปริมาณคิว (TOR NLP-PROC-2026-114) — ตัวเลือก A: MA-STD 8x5 (ฉบับใน proposal)

> ⚠️ **เอกสารภายใน** มีต้นทุนและ margin — ห้ามส่งลูกค้า
> ลูกค้า: ธนาคารนครหลวงพัฒนา จำกัด (มหาชน) — ฝ่ายพัฒนาช่องทางสาขา · คิดโดย จอย พัฒนสิน (fin-joy) · 2026-11-04 · fixed-price (บวก buffer 10% ใน man-day แล้ว)

## ผลสรุป

| | |
|---|---|
| ราคาขายก่อน VAT (หลังส่วนลด) | **4,800,000** บาท |
| ต้นทุนรวม | 3,365,700 บาท |
| กำไรขั้นต้น | 1,434,300 บาท |
| **Gross margin** | **29.9%** → ✅ ผ่าน |
| **ผู้อนุมัติ (เข้มสุดของ margin + ส่วนลด)** | **หัวหน้าทีมขาย (sales-nida)** |
| ส่วนลด | 409,000 บาท = 9.5% ของยอดที่ลดได้ → หัวหน้าทีมขาย (sales-nida) |
| VAT 7% / รวมทั้งสิ้น | 336,000 / 5,136,000 บาท |
| งบลูกค้า (ก่อน VAT) | 4,800,000 บาท · ใช้ 100.0% |

man-day รวม 300 วัน (ประเมินก่อน buffer 271 วัน)

## รายการ

| รหัส | รายการ | ประเมิน | จำนวน (รวม buffer) | หน่วย | ราคา/หน่วย | ราคาขาย | ต้นทุน/หน่วย | ต้นทุน | margin บรรทัด | หมายเหตุ |
|---|---|--:|--:|---|--:|--:|--:|--:|--:|---|
| MD-SA | Solution Architect (SA) | 18 | 20 | man-day | 18,000 | 360,000 | 11,000 | 220,000 | 38.9% | ออกแบบ, integration core banking mTLS / Q-Matic / Entra ID, security |
| MD-PM | Project Manager | 36 | 40 | man-day | 16,000 | 640,000 | 10,000 | 400,000 | 37.5% | แผนงาน 6 เดือน, นำร่อง 10 สาขา, rollout 120 สาขา |
| MD-DEV-SR | Senior Developer / Tech Lead | 45 | 50 | man-day | 15,000 | 750,000 | 9,500 | 475,000 | 36.7% | tech lead, booking engine, slot lock, core-connector |
| MD-DEV | Developer | 80 | 88 | man-day | 11,000 | 968,000 | 7,000 | 616,000 | 36.4% | 2 คน: LIFF, Web Booking, Branch Console, Dashboard |
| MD-UX | UX/UI Designer | 10 | 11 | man-day | 12,000 | 132,000 | 7,500 | 82,500 | 37.5% | หน้าจอลูกค้า + branch console + ทดสอบกับผู้ใช้ |
| MD-QA | QA Engineer | 40 | 44 | man-day | 9,000 | 396,000 | 5,800 | 255,200 | 35.6% | แผนทดสอบ, load test, UAT, retest หลัง pentest, นำร่อง |
| MD-DEVOPS | DevOps Engineer | 14 | 16 | man-day | 14,000 | 224,000 | 9,000 | 144,000 | 35.7% | cloud 3 env, CI/CD, monitoring, backup |
| MD-ML | ML Engineer / Data Scientist | 28 | 31 | man-day | 17,000 | 527,000 | 11,000 | 341,000 | 35.3% | โมเดลพยากรณ์, pipeline ทุกคืน, registry, rollback |
| CL-M | Cloud hosting Medium (Thailand region) 4 vCPU x3 + managed PostgreSQL HA + Redis | 12 | 12 | month | 45,000 | 540,000 | 32,000 | 384,000 | 28.9% | ปีแรก: PostgreSQL HA + Redis |
| LIC-LINE | LINE OA Messaging API (plan + push quota) | 12 | 12 | month | 6,000 | 72,000 | 4,500 | 54,000 | 25.0% | ปีแรก |
| LIC-APM | Monitoring / APM + log management license | 12 | 12 | month | 8,000 | 96,000 | 5,500 | 66,000 | 31.2% | ปีแรก |
| LIC-WAF | Web Application Firewall + DDoS protection | 12 | 12 | month | 12,000 | 144,000 | 9,000 | 108,000 | 25.0% | ปีแรก |
| MA-STD | Maintenance Standard 8x5 (per system) | 1 | 1 | year | 360,000 | 360,000 | 220,000 | 220,000 | 38.9% | ปีแรก 8x5 |
| — | ส่วนลดพิเศษ | | | | | −409,000 | | | | ปิดส่วนต่างให้พอดีงบ 4.8M |
| | **รวม** | | | | | **4,800,000** | | **3,365,700** | **29.9%** | |

## สมมติฐาน

- man-day ก่อน buffer ตาม deal-001-internal-notes.md ข้อ 2 (sa-ice) · script บวก buffer 10% ปัดขึ้น
- สมมติ reuse ฐานระบบจากงานเกษตรไทย 2025 จึงใกล้ benchmark 4 เดือน 225 man-day แม้งานนี้ใหญ่กว่า (120 สาขา, mTLS, Entra ID, Q-Matic, ML) — เสี่ยง under-estimate
- ค่า pentest, SMS/OTP, อุปกรณ์สาขา ไม่รวม (ธนาคารจ่าย) — ถ้าไม่ใช่ต้องเพิ่มบรรทัด external

## จุดที่ตัดสินใจเอง (ให้ Sales/MD ยืนยัน)

- ส่วนลด 9.5% ชิดเพดาน 10% ของหัวหน้าทีมขาย — ไม่เหลือที่ต่อรอง
- MA-STD 8x5 อาจไม่ตรง TOR (Sev 1 ตอบรับ 30 นาที ไม่ระบุชั่วโมง) — benchmark ระบุว่า Sev 1 30 นาที/24x7 → MA-PREM
- ลูกค้าธนาคาร + มูลค่า ≥ 1M → ต้องผ่าน MD ทาง deal-approval อยู่แล้ว ไม่ว่า margin เท่าไร

## ถ้าต้องลดราคา — ตัวเลือกที่ไม่ผิดกฎ

- ย้าย ML ปรับจูนรอบ 2 ไป MA/เฟส 2 (ต้องให้ ml-jay ยืนยันว่ายังได้ MAPE ≤ 20%)
- แยก MA ปีแรกเป็นสัญญาต่างหาก (ให้ Sales ถามธนาคาร)
- ห้าม: ตัด QA / buffer / ลด MA-CL
