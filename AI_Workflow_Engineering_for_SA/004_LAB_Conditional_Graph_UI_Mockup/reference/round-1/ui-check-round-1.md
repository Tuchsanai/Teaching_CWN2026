# ผลตรวจ UI รอบ 1

ตรวจด้วย tests/ui-check.py ทั้งชุด ผ่าน 19/19 ข้อ, ตก 0, raw edge=`pass`, exit code=0, browser=`launch`

การตัดสิน: หยุดแก้และส่งผู้ตรวจ AI; ไม่มีรอบแก้ เพราะผ่านตั้งแต่ครั้งแรก ไม่สร้างภาพก่อน–หลังหรือ prompt แก้สมมติ

| check ID | US | ผล | หลักฐาน |
|---|---|---|---|
| roles | US-01, US-25 | ผ่าน | [ภาพ](shots/roles.png) |
| table-menu | US-01, US-02 | ผ่าน | [ภาพ](shots/table-menu.png) |
| option-price | US-04 | ผ่าน | [ภาพ](shots/option-price.png) |
| queue-order | US-10 | ผ่าน | [ภาพ](shots/queue-order.png) |
| status-sync | US-05, US-11 | ผ่าน | [ภาพ](shots/status-sync.png) |
| stock-whole | US-06, US-12 | ผ่าน | [ภาพ](shots/stock-whole.png) |
| stock-option | US-06, US-12 | ผ่าน | [ภาพ](shots/stock-option.png) |
| restock | US-13 | ผ่าน | [ภาพ](shots/restock.png) |
| promptpay-slip | US-08, US-15 | ผ่าน | [ภาพ](shots/promptpay-slip.png) |
| promptpay-disabled | US-08 | ผ่าน | [ภาพ](shots/promptpay-disabled.png) |
| promptpay-timeout-cash | US-08, US-15 | ผ่าน | [ภาพ](shots/promptpay-timeout-cash.png) |
| takeaway-slot | US-03, US-15 | ผ่าน | [ภาพ](shots/takeaway-slot.png) |
| close-table | US-16 | ผ่าน | [ภาพ](shots/close-table.png) |
| menu-management | US-19 | ผ่าน | [ภาพ](shots/menu-management.png) |
| ingredient-mapping | US-20, US-12, US-13 | ผ่าน | [ภาพ](shots/ingredient-mapping.png) |
| pin-lock | US-25 | ผ่าน | [ภาพ](shots/pin-lock.png) |
| permission-denied | US-25 | ผ่าน | [ภาพ](shots/permission-denied.png) |
| account-create | US-25 | ผ่าน | [ภาพ](shots/account-create.png) |
| reset | US-02, US-16, US-25 | ผ่าน | [ภาพ](shots/reset.png) |

ผลนี้ครอบคลุม mock smoke checks เท่านั้น ไม่ปิดข้อค้าง MC-01–MC-03, A-02, A-03, A-05 และไม่รับรอง LAN/load/ความปลอดภัยจริง
