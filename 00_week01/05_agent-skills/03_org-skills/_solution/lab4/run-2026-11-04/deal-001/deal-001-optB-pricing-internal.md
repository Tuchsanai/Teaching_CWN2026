# คิดราคา (ภายใน) — ระบบจองคิวสาขาและพยากรณ์ปริมาณคิว (TOR NLP-PROC-2026-114) — ตัวเลือก B: MA-PREM 24x7 ในงบเดียวกัน

> ⚠️ **เอกสารภายใน** มีต้นทุนและ margin — ห้ามส่งลูกค้า
> ลูกค้า: ธนาคารนครหลวงพัฒนา จำกัด (มหาชน) — ฝ่ายพัฒนาช่องทางสาขา · คิดโดย จอย พัฒนสิน (fin-joy) · 2026-11-04 · fixed-price (บวก buffer 10% ใน man-day แล้ว)

## ผลสรุป

| | |
|---|---|
| ราคาขายก่อน VAT (หลังส่วนลด) | **4,800,000** บาท |
| ต้นทุนรวม | 3,595,700 บาท |
| กำไรขั้นต้น | 1,204,300 บาท |
| **Gross margin** | **25.1%** → ✅ ผ่าน |
| **ผู้อนุมัติ (เข้มสุดของ margin + ส่วนลด)** | **MD (md-somchai)** |
| ส่วนลด | 769,000 บาท = 17.8% ของยอดที่ลดได้ → MD เท่านั้น และ margin หลังลดต้อง ≥ 15% |
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
| MA-PREM | Maintenance Premium 24x7 (per system) | 1 | 1 | year | 720,000 | 720,000 | 450,000 | 450,000 | 37.5% | ปีแรก 24x7 ตรง TOR Sev 1 30 นาที |
| — | ส่วนลดพิเศษ | | | | | −769,000 | | | | ปิดส่วนต่างให้พอดีงบ 4.8M · > 10% → MD เท่านั้น |
| | **รวม** | | | | | **4,800,000** | | **3,595,700** | **25.1%** | |

## สมมติฐาน

- man-day ก่อน buffer ตาม deal-001-internal-notes.md ข้อ 2 (sa-ice) · script บวก buffer 10% ปัดขึ้น
- สมมติ reuse ฐานระบบจากงานเกษตรไทย 2025 จึงใกล้ benchmark 4 เดือน 225 man-day แม้งานนี้ใหญ่กว่า (120 สาขา, mTLS, Entra ID, Q-Matic, ML) — เสี่ยง under-estimate
- ค่า pentest, SMS/OTP, อุปกรณ์สาขา ไม่รวม (ธนาคารจ่าย) — ถ้าไม่ใช่ต้องเพิ่มบรรทัด external

## จุดที่ตัดสินใจเอง (ให้ Sales/MD ยืนยัน)

- ส่วนลด > 10% → MD (md-somchai) เท่านั้น ผ่าน deal-approval
