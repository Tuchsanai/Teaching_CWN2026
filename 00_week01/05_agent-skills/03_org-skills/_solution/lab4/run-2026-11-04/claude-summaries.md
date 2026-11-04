# LAB 4 · ผลรันจริง 2026-11-04 (บริษัท 28 คน · ทีละโต๊ะแบบแยกเครื่อง)

แต่ละขั้นรันด้วย claude -p ที่โต๊ะของคนนั้น ระหว่างรันย้ายโต๊ะคนอื่นและ plugin ที่คนนั้นไม่มีออกชั่วคราว ให้เหมือนเครื่องของเขาจริง

## 1-sales-nida · 08:52:59–08:58:40 · skill ที่หยิบเอง: sales:sales-proposal

พรอมต์: เปิดดีลใหม่: TOR อยู่ที่ ../../company-kit/deal-001/tor-bank-queue.md ช่วยทำ proposal แล้ววางไว้ในโฟลเดอร์กลางของดีล ../../deals/deal-001/

ร่าง proposal เสร็จแล้วครับ แต่ยังยื่นไม่ได้จนกว่าจะเคาะเรื่อง SLA และราคาด้านล่าง ต้องยื่นภายใน **13 พ.ย. 2026 16:00 น.** ผมสร้างโฟลเดอร์ `deals/deal-001/` ใหม่ (เดิมยังไม่มี) แล้ววางไว้ 4 ไฟล์:

- `deal-001-proposal-nlpbank.md` — ฉบับส่งลูกค้า 9 หัวข้อตามโครงที่เคยชนะ
- `deal-001-pricing-input.json` และ `deal-001-pricing-output.md` — ราคาที่ได้จากสคริปต์ราคา
- `deal-001-internal-notes.md` — ตัวเลขภายในและเรื่องที่ต้องตัดสิน ห้ามส่งลูกค้า

**ราคา:** รวม **4,800,000 บาท ไม่รวม VAT** เท่ากับงบพอดี margin 29.9% ซึ่งหัวหน้าทีมขายอนุมัติเองได้
- ราคาเต็มเกินงบ 409,000 บาท ผมลด man-day ไปแล้วรอบหนึ่ง โดยสมมติว่าใช้ระบบจองจากงานเกษตรไทยเป็นฐาน ส่วนที่เหลือใส่เป็นส่วนลดพิเศษ 9.5% (คิดจากยอดที่ลดได้) ไม่ได้ลด MA หรือ cloud
- ส่วนลดนี้ชิดเพดาน 10% ของคุณแล้ว ถ้าลูกค้าต่อรองอีกต้องให้ MD อนุมัติ
- ยังไม่ได้ให้บัญชีตรวจตัวเลข เพราะเครื่องนี้ไม่มีแพ็ก finance ต้องส่งไฟล์ input ให้ `fin-joy` ตรวจ
- สคริปต์ราคารันบนเครื่องนี้ไม่ได้ เพราะ Windows ใช้ encoding cp874 แสดงอักษรบางตัวไม่ได้ ผมต้องรันโดยตั้ง `PYTHONIOENCODING=utf-8`
- สคริปต์คิด % ส่วนลดจากราคาเต็ม ได้ 7.9% แต่กฎ margin เขียนว่าคิดจากยอดที่ลดได้ ได้ 9.5% ดีลนี้ตกขั้นผู้อนุมัติเดียวกันจึงไม่กระทบ แต่ควรแจ้ง `fin-joy` ให้แก้

**เรื่องที่ผมเลือกแทนไว้ ต้องเคาะก่อนยื่น**
1. **SLA:** ผมใส่ MA แบบ 8x5 และเสนอ 24x7 เป็นตัวเลือกเสริม (+360,000 บาท/ปี) แต่ TOR เขียนว่า Sev 1 ต้องตอบรับใน 30 นาที โดยไม่บอกชั่วโมง กรรมการอาจตีความว่าต้อง 24x7 อีกทางคือรวม 24x7 ไว้ในราคา 4.8M เลย margin จะเหลือ 25.1% แต่ส่วนลดขึ้นเป็น 17.8% ต้องให้ MD อนุมัติ
2. **ใช้โค้ดงานเกษตรไทย (NovaQueue v2) เป็นฐาน:** man-day ทั้งดีลตั้งอยู่บนข้อสมมตินี้ ต้องเช็กกับ `pm-beam` ว่าสิทธิ์ในโค้ดเป็นของเราหรือของเกษตรไทย ถ้าใช้ไม่ได้ ราคาที่ประมาณไว้จะต่ำเกินจริง
3. **ผลทดลองพยากรณ์:** ผมไม่ได้ใส่ตัวเลข MAPE 15.2% ในเอกสาร เพราะเป็นผลทดลองบนข้อมูลเกษตรไทยและยังเทียบกันไม่แฟร์ proposal ผูกไว้แค่เกณฑ์ ≤ 20% ตาม TOR ทดสอบบนข้อมูลของธนาคารเอง

**ที่ยังค้าง**
- เลขที่เอกสาร: ผมหาทะเบียนเลขไม่เจอ ใส่ไว้ว่า `NVT-PRP-2026-[รอเลขจากทะเบียนเอกสาร]` ต้องขอเลขก่อนยื่น
- ภาคผนวก PDPA สำหรับลูกค้าธนาคาร: ยังไม่ได้แนบ เป็นกติกาของ MD
- ไฟล์เป็น Markdown: ตอนแปลงเป็น PDF/Word ต้องจัดฟอนต์ โลโก้ สีตาราง และเลขหน้าท้ายกระดาษตามคู่มือแบรนด์

**ตรวจข้อมูลส่วนบุคคล:** สแกนแล้วไม่พบ และอ่านซ้ำทั้งฉบับแล้ว ไม่มีเบอร์มือถือผู้ประสานงานจาก TOR และไม่มีมูลค่าสัญญาของลูกค้าที่อ้างอิง

ใน proposal ยังมีรายการ "สิ่งที่ขอยืนยันก่อนเริ่มงาน" 8 ข้อที่ต้องถามธนาคาร เช่น ช่องทางส่ง OTP (API ของธนาคารไม่คืนเบอร์โทร) และมีสาขาที่เปิดเสาร์-อาทิตย์หรือไม่ รายละเอียดทั้งหมดอยู่ใน internal-notes

## 2-fin-joy · 08:58:44–09:00:18 · skill ที่หยิบเอง: finance:pricing-calc

พรอมต์: ตรวจราคาและกำไรของดีล ../../deals/deal-001/ แล้ววางผลไว้ในโฟลเดอร์เดียวกัน

I re-ran deal-001's pricing through the finance pricing script. The price and profit come out exactly as the internal notes and the proposal say. The proposal's price table matches line by line, the 10% buffer is applied, there's no discount on MA or cloud hosting, and the script raised no errors.

| | A: 8x5 support (in the proposal) | B: 24x7 support |
|---|--:|--:|
| Before VAT | **4,800,000** (exactly the customer's budget) | **4,800,000** |
| VAT / total | 336,000 / 5,136,000 | 336,000 / 5,136,000 |
| Margin | **29.9%**, passes | **25.1%**, passes (0.1 points above the 25% line) |
| Discount (share of the discountable amount) | 9.5%, head of sales can approve | 17.8%, MD only |

**Approval:** under the margin and discount rules alone, option A only needs the head of sales. But this is a bank customer and the deal is over 1M, so both options must go to the MD through `deal-approval`.

**Things to watch:**
- **The original input file gives the wrong answer in the finance script.** `deal-001-pricing-input.json` uses the keys `budget` and `discount`, but the script reads `budget_thb` and `discount_thb`. Run as-is, it ignores the discount and returns 5,209,000. I made new input files for both options instead.
- **The discount-percentage question in the notes is settled.** The finance script divides by the discountable amount (9.5%), which is what the margin rules say. The 7.9% figure comes from sales' `price.py`, so use 9.5%.
- **There is almost no room to negotiate.** Option A can only give about 21,900 baht more discount before it needs the MD. On option B, an extra discount of about 5,700 baht drops the margin below 25%.
- **8x5 support may not meet the TOR.** The TOR asks for a 30-minute response to the most severe issues without saying which hours. Our pricing benchmarks call for the 24x7 package in that case.
- **The man-day estimate is at risk:**
  - QA is fine at 32% of developer time.
  - PM time is low: 40 days over 6 months is about a third, where the benchmark is about half (~60 days) for a 120-branch rollout.
  - Labour excluding ML is only about 20% above the previous bank job (40 branches), even though this one is bigger. That only works if the old code can be reused and we own the rights to it.
- The quotation drafts end with an internal italic note that mentions margin. Delete that line before it goes into anything sent to the customer.

Next steps: `deal-approval` with the MD. If you switch to option B, update the price table in the proposal through `sales-proposal`.

Files are in `C:\t\org05p\novatech\deals\deal-001\`:
- `deal-001-pricing-check-fin.md` (summary of this check)
- `deal-001-optA-input.json`
- `deal-001-optB-input.json`
- `deal-001-optA-pricing-internal.md` (internal: includes cost and margin)
- `deal-001-optB-pricing-internal.md` (internal: includes cost and margin)
- `deal-001-optA-quotation-draft.md`
- `deal-001-optB-quotation-draft.md`

## 3-md-somchai · 09:00:22–09:01:37 · skill ที่หยิบเอง: exec:deal-approval

พรอมต์: ดีล ../../deals/deal-001/ อนุมัติได้ไหม เขียนผลไว้ในโฟลเดอร์ดีล

**ผล: ❌ ตีกลับ Sales (`sales-nida`)**

**ตัวเลข:** margin 29.9% ผมรันสคริปต์คิดซ้ำได้ตรงกับฝ่ายบัญชี ราคาขาย 4,800,000 ต้นทุน 3,365,700 รวม buffer 10% แล้ว ส่วนลด 9.5% กำไรจึงไม่มีปัญหา

**เหตุผลหลัก**
1. **ข้อ 5 ไม่ผ่าน:** proposal ที่จะยื่นธนาคารไม่มี "ภาคผนวก PDPA" ซึ่งต้องมี 3 ข้อ คือ DPA, เก็บข้อมูลในไทยเท่านั้น และแจ้งเหตุภายใน 72 ชม. checklist ใน internal notes ก็ยังเขียนว่ายังไม่ได้แนบ กฎของลูกค้าธนาคารให้ตีกลับทันที ผมจึงยังไม่ได้ตรวจข้อ 2, 3, 4, 6 และ 7
2. หัวข้อ 4.2 ใน proposal เขียนแค่ "แจ้งเหตุภายในเวลาที่กฎหมายกำหนด" ใช้แทนภาคผนวกไม่ได้
3. ถ้าเพิ่มภาคผนวกแล้วส่งกลับมา ยังทันกำหนดยื่น 13 พ.ย.

ระหว่างอ่านเอกสาร ผมเจอเรื่องที่น่าจะต้องตรวจในรอบหน้า และจดไว้ใน approval.md แล้ว:
- ยังไม่ได้เลือกระหว่าง MA-STD 8x5 กับ MA-PREM 24x7 ถ้าเลือก PREM ส่วนลดจะเป็น 17.8% และ margin เหลือ 25.1%
- ยังไม่เห็นเครดิตเทอม และค่าปรับหรือเพดานความรับผิด
- `sa-ice` รับ deal-002 อยู่ด้วย
- PM 40 วันน้อยไปสำหรับ rollout 120 สาขา
- สิทธิ์ในโค้ดที่ reuse จากงานเกษตรไทยยังรอ `pm-beam` ยืนยัน

ผลอยู่ที่ `../../deals/deal-001/approval.md` ส่วน input ที่ใช้คิดตัวเลขซ้ำอยู่ใน `deal-input.json` โฟลเดอร์เดียวกัน
