# สาธิตเส้นทาง fix ของ Conditional Graph

ข้อบกพร่องถูกฉีดโดยผู้จัดทำเพื่อสาธิต edge=fix ไม่ใช่ผลของลูปหลัก; UI ส่งต่อยังคงเป็น reference/final/ui-mockup.html

ลูปหลักผ่าน 19/19 ตั้งแต่รอบแรก ชุดนี้คัดลอก HTML มาเป็น seed แล้วจงใจทำให้เสียสองจุดเพื่อการสอน ไม่ใช่ข้อบกพร่องที่ AI สร้างขึ้น และไม่เปลี่ยนผลลูปหลักหรือผลผู้ตรวจเดิม
ผลสาธิตจริงวันที่ 2026-09-14 UTC: baseline **17/19, edge=fix → แก้ด้วย Codex หนึ่งครั้ง → 19/19, edge=pass**; ไม่มี regression ของ 17 checks ที่เคยผ่าน
`round-1` ในโฟลเดอร์นี้หมายถึง baseline หลังฉีด; `round-2` คือผลหลังแก้ครั้งแรก (`current-round.txt` = 1) เทียบกับกิจกรรมผู้เรียนคือ baseline 0 → แก้ 1 ไม่ใช่แก้สองครั้ง

## ขั้นตอนและหลักฐาน

| ขั้น | Prompt | ผล | อ้างอิง | ผลตรวจ | ข้อบกพร่อง | การแก้ไข | ขั้นถัดไป |
|---|---|---|---|---|---|---|---|
| เตรียม seed | ผู้จัดทำคัดลอกและฉีดข้อบกพร่อง ไม่เรียก AI | HTML จำลองข้อบกพร่อง | [seed](seed/ui-mockup-broken.html), [diff ที่ฉีดและ hash](seed/injected-defects.md) | ต้นฉบับมี [ผล 19/19](../round-1/ui-check.json) | ยอดตัวเลือกหาย; ปุ่มสลิปปิดตลอด | ฉีดเฉพาะสองนิพจน์เพื่อสร้างสถานการณ์ | ตรวจ baseline |
| ตรวจรอบก่อน | tests/ui-check.py | 17 ผ่าน / 2 ตก | [JSON](round-1/ui-check.json), [คำสั่ง/เวลา](round-1/check-run.json), [ภาพและลำดับคลิก](round-1/screenshots.json) | edge=fix, exit 1 | option-price และ promptpay-slip | ยังไม่แก้; เก็บ snapshot เดิม | ส่ง failed checks จริงเข้า Prompt 02 |
| แก้ครั้งแรก | [Prompt ที่ใช้จริง](round-2/prompt-used.md) จาก [แม่แบบ](../../prompts/02-fix-screen.md) | [HTML หลังแก้](round-2/ui-mockup-fixed.html) | [log](round-2/log.jsonl), [run-meta](round-2/run-meta.json), [รายงาน AI](round-2/fix-report.md), [diff ซ่อม](round-2/fix.diff) | turn.completed 1, turn.failed 0; รายงาน AI ณ จบ session ระบุรอตรวจซ้ำ | สองจุดใน customerHTML และ frontHTML | รวมราคาตัวเลือก; คืนเงื่อนไข disabled ตาม state เดิม | ตรวจทั้งชุดพร้อม --prev |
| ตรวจหลังแก้ | tests/ui-check.py --prev round-1/ui-check.json | 19 ผ่าน / 0 ตก | [JSON](round-2/ui-check.json), [คำสั่งจริง/เวลา](round-2/check-run.json), [ภาพและลำดับคลิก](round-2/screenshots.json) | edge=pass, exit 0; regression 0 | สอง check เดิมผ่านแล้ว | หยุดแก้ตามกราฟ | เก็บชุดสาธิต; ใช้ UI ส่งต่อเดิม |

## ผล checks ก่อน–หลังครบชุด

| Check ID | US | ก่อนแก้ | หลังแก้ |
|---|---|---|---|
| roles | US-01, US-25 | ผ่าน | ผ่าน |
| table-menu | US-01, US-02 | ผ่าน | ผ่าน |
| option-price | US-04 | **ตก** | ผ่าน |
| queue-order | US-10 | ผ่าน | ผ่าน |
| status-sync | US-05, US-11 | ผ่าน | ผ่าน |
| stock-whole | US-06, US-12 | ผ่าน | ผ่าน |
| stock-option | US-06, US-12 | ผ่าน | ผ่าน |
| restock | US-13 | ผ่าน | ผ่าน |
| promptpay-slip | US-08, US-15 | **ตก** | ผ่าน |
| promptpay-disabled | US-08 | ผ่าน | ผ่าน |
| promptpay-timeout-cash | US-08, US-15 | ผ่าน | ผ่าน |
| takeaway-slot | US-03, US-15 | ผ่าน | ผ่าน |
| close-table | US-16 | ผ่าน | ผ่าน |
| menu-management | US-19 | ผ่าน | ผ่าน |
| ingredient-mapping | US-20, US-12, US-13 | ผ่าน | ผ่าน |
| pin-lock | US-25 | ผ่าน | ผ่าน |
| permission-denied | US-25 | ผ่าน | ผ่าน |
| account-create | US-25 | ผ่าน | ผ่าน |
| reset | US-02, US-16, US-25 | ผ่าน | ผ่าน |

เซตข้อที่ตกเปลี่ยนจาก `{option-price, promptpay-slip}` เป็นเซตว่าง จึงตัดสิน pass ก่อนพิจารณาการวนซ้ำ
ใช้ `--prev reference/demo-fix-path/round-1/ui-check.json` ซึ่งเป็นรอบก่อนของ seed ชุดเดียวกัน ไม่ใช้รายงานรอบแรกของลูปหลักเป็น prev
ทุก check เดิมถูกตรวจซ้ำครบ 19 ข้อ แต่ละ check ใช้ browser context ใหม่และรีเซ็ตข้อมูล มีภาพอัตโนมัติ 19 ภาพต่อรอบ เช่น [ยอดก่อนแก้](round-1/shots/option-price.png), [ยอดหลังแก้](round-2/shots/option-price.png), [สลิปก่อนแก้](round-1/shots/promptpay-slip.png), [ผลหลังยืนยัน](round-2/shots/promptpay-slip.png)
ผลนี้ไม่ได้ทดลอง edge=cancel: ถ้าชุดข้อที่ตกซ้ำต้องหยุดตามกฎ; หากยัง fix หลังแก้ครบ 3 ครั้งต้องหยุดตามเพดาน ห้ามรีเซ็ตประวัติหรือลบ --prev

## ภาพก่อน–หลังในสถานะเดียวกัน

ภาพทั้งสี่ถ่ายใหม่จาก Playwright/Chromium ผ่าน file://, viewport 1280×900, device scale factor 1, full-page; ความสูงไฟล์จึงเกิน 900 ได้ ภาพไม่มีการตกแต่ง
ลำดับแรก: รีเซ็ต → โต๊ะ 01 → เมนู m01 ราคา 50 → เลือกไข่ดาว +10 → ถ่ายรายละเอียดจาน
ลำดับที่สอง: เพิ่มตะกร้า → ส่งออเดอร์ → เลือก PromptPay → เข้าหน้าร้านด้วยผู้ใช้จำลอง → ถ่ายขณะยังค้างจ่าย เพื่อเทียบปุ่ม ณ state เดียวกัน

| กรณี | ก่อนแก้ | หลังแก้ |
|---|---|---|
| เลือกไข่ดาวแล้ว ยอดจานต้องเป็น 60 บาท | [ภาพ: ยังแสดง 50 บาท](../../img/demo-fix-option-before.png) | [ภาพ: รวมเป็น 60 บาท](../../img/demo-fix-option-after.png) |
| ออเดอร์ 60 บาทค้างจ่ายผ่าน PromptPay | [ภาพ: ยืนยันสลิปไม่ได้](../../img/demo-fix-slip-before.png) | [ภาพ: ปุ่มยืนยันสลิปเปิดให้กด](../../img/demo-fix-slip-after.png) |

หลังถ่ายภาพหลังแก้ได้กดยืนยันจริง พบสถานะจ่ายแล้วทั้งหน้าร้านและลูกค้า พร้อมชื่อผู้ใช้จำลองใน payment-log และปุ่มยืนยันถูกปิดหลังจ่ายแล้ว
ตรวจเพิ่มแบบเจาะจง: ยกเลิกไข่ดาวแล้วราคากลับ 50 และเลือกใหม่เป็น 60; ก่อนขอ PromptPay ปุ่มสลิปยังปิดอยู่ ดู [บันทึกผลที่สังเกตและ hash ภาพ](round-2/screenshots.json)

## เวลาและโทเคนจริง

- เครื่องมือ Codex CLI 0.154.0; บัญชี `<บัญชี>`; โมเดล `gpt-6-astra (ตาม flag ที่สั่ง CLI ไม่ยืนยันกลับ)`; effort `high`
- เริ่ม 2026-09-14T12:32:53.367543+00:00; จบ 2026-09-14T12:34:19.202930+00:00; wall time **85.839 วินาที** จาก [บันทึกเวลาครอบ process จริง](round-2/execution-timing.jsonl)
- [log.jsonl](round-2/log.jsonl): `turn.completed.usage` มี input **270,348**, cached input **225,152**, cache write input **0**, output **3,895**, reasoning output **419** tokens
- เก็บค่าตาม field ใน log ไม่บวก cached/reasoning ซ้ำเป็นยอดใหม่; ไม่มีข้อมูลค่าใช้จ่ายเป็นเงิน
- เรียก Codex 1 ครั้ง, completed 1, failed 0, exit 0; [คำตอบ CLI](round-2/response.md) และ [stderr](round-2/stderr.txt) คงไว้เป็นหลักฐาน
- ตัวตรวจก่อนแก้ใช้ 21.122 วินาที; หลังแก้ใช้ 15.927 วินาที วัดครอบ process แยกจากเวลาโมเดล

## ขอบเขตและสมมติฐาน

ใช้ข้อมูลจำลองเดิมและ seed HTML เป็น snapshot โดยไม่สร้าง work/ เพิ่ม แม่แบบ Prompt 02 คงข้อความเดิมหลังแทน FAILED_CHECKS; เพิ่มคำอธิบายแมป path และอนุญาตให้เขียนเฉพาะ HTML/report ในชุดสาธิตไว้ก่อนแม่แบบ เพื่อไม่ให้ข้อห้าม reference/ ของกิจกรรมผู้เรียนขัดกับปลายทางสาธิต
ผู้แก้ได้รับเฉพาะ seed และหลักฐานที่ตก ไม่ให้คัดลอก HTML ที่ผ่านจากลูปหลัก; diff หลังแก้มีเพียงสองบรรทัด และผลสุดท้ายเท่ากับต้นฉบับตามการเปรียบเทียบหลังจบ
ค่า `html` ใน JSON ผลตรวจทั้งสองรอบถูกเปลี่ยนเฉพาะจาก path เครื่องจริงเป็น path สัมพัทธ์จากโฟลเดอร์ LAB เพื่อเผยแพร่; ไม่แก้ checks, detail, counts หรือ edge ดูหมายเหตุใน check-run.json แต่ละรอบ
รายงาน AI ที่เขียนว่า “รอตรวจซ้ำ” เป็นหลักฐาน ณ เวลาจบ session; ผลผ่านหลังจากนั้นอยู่ใน round-2/ui-check.json ไม่เขียนทับคำตอบเดิม
ภาพชุดนี้ตรวจเฉพาะ desktop; ไม่อ้างว่าได้ตรวจ mobile, ระบบจ่ายเงินจริง, LAN, load หรือความปลอดภัยจริง ไม่เปลี่ยนข้อค้างธุรกิจของลูปหลัก
ชุดสาธิตไม่ถูกส่งไป LAB 005; [UI ส่งต่อเดิม](../final/ui-mockup.html) ยังคงตรงกับ [HTML รอบแรกของลูปหลัก](../round-1/ui-mockup.html)
