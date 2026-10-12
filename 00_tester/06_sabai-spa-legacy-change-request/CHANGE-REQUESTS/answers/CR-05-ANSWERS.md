# คำตอบข้อซักถาม CR-05 · รายงานยอด

## ① คำตอบของร้าน
- นับตาม **วันนัด** (เวลาไทย) ไม่ใช่วันที่จอง · ช่วงวันรวมวันแรกและวันสุดท้าย
- "ยอดขาย" นับเฉพาะนัดที่ใช้บริการแล้ว · "ยอดของนัดที่ยังไม่มา" = นัดสถานะยืนยัน
- ส่วนลดแยก 3 แบบ: กลุ่ม · ระดับสมาชิก · เดือนเกิด
- 3 เดือน = ไม่เกิน 92 วันต่อครั้ง · วันเริ่มต้องไม่เกินวันสิ้นสุด
- ไฟล์ Excel: 1 แถวต่อ 1 นัด เรียงตามเวลา

## ② สิ่งที่ตกลงร่วมกัน
| เรื่อง | ตกลง |
|---|---|
| API | `GET /api/admin/report?from=YYYY-MM-DD&to=YYYY-MM-DD` → `{ counts: {confirmed, completed, cancelled}, revenue, giftcardPaid, otherPaid, transportFee, discounts: {group, tier, birthday}, pointsEarned, courseSessions, pendingValue, byTherapist: [{code, completed}] }` (เงินเป็นบาท) |
| CSV | `&format=csv` → `text/csv; charset=utf-8` ขึ้นต้นด้วย BOM · หัวคอลัมน์ `date,code,status,type,people,service,total,giftcard_paid,other_paid,discount_kind,discount_amount,points_earned` |
| ช่วงผิด | เกิน 92 วัน หรือ from > to → 422 |
| สิทธิ์ | เจ้าของร้านเท่านั้น · สมาชิก 403 · ไม่ล็อกอิน 401 |
| หน้า | `/admin/report` · `report-from` `report-to` `report-run` `report-revenue` `report-count-{confirmed|completed|cancelled}` `report-csv` · ลิงก์เมนู `nav-admin-report` |

## ③ ตัวอย่างที่ร้านยืนยัน
| # | ช่วง | ผลที่ต้องได้ |
|---|---|---|
| 1 | 6–9 ต.ค. 2569 | ทุกค่าเป็น 0 (ไม่ใช่ error) |
| 2 | 1 ส.ค. – 31 ต.ค. 2569 (92 วัน) | ดูได้ · 1 ส.ค. – 1 พ.ย. 2569 (93 วัน) ดูไม่ได้ |

## ④ นอกขอบเขต
กราฟ · ส่งอีเมลรายงานอัตโนมัติ · ภาษีมูลค่าเพิ่ม
