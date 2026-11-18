# ผลของ Training rollouts · iteration 2

คะแนนเฉลี่ย 89.5% · ผ่านครบทุกข้อ 2/12 Trace

| trace_id | ผล | คะแนน | ข้อตรวจที่ไม่ผ่าน |
|---|---|---|---|
| t1-cafe-bill-r1 | FAIL | 0.90 | tests |
| t1-cafe-bill-r2 | FAIL | 0.90 | tests |
| t1-cafe-bill-r3 | FAIL | 0.90 | tests |
| t2-split-bill-r1 | PASS | 1.00 | - |
| t2-split-bill-r2 | FAIL | 0.90 | tests |
| t2-split-bill-r3 | PASS | 1.00 | - |
| t3-shipping-fee-r1 | FAIL | 0.91 | policy |
| t3-shipping-fee-r2 | FAIL | 0.82 | tests policy |
| t3-shipping-fee-r3 | FAIL | 0.82 | tests policy |
| t4-cashback-r1 | FAIL | 0.90 | policy |
| t4-cashback-r2 | FAIL | 0.90 | policy |
| t4-cashback-r3 | FAIL | 0.80 | tests policy |

## รายละเอียดของข้อตรวจที่ไม่ผ่าน (คาดว่าอะไร · ได้อะไร)

- t1-cafe-bill-r1 · `tests`: unittest พบ 5 เทสต์ (ต้องมีอย่างน้อย 6)
- t1-cafe-bill-r2 · `tests`: unittest พบ 5 เทสต์ (ต้องมีอย่างน้อย 6)
- t1-cafe-bill-r3 · `tests`: unittest พบ 5 เทสต์ (ต้องมีอย่างน้อย 6)
- t2-split-bill-r2 · `tests`: unittest พบ 4 เทสต์ (ต้องมีอย่างน้อย 6)
- t3-shipping-fee-r1 · `policy`: shipping_fee(3000, 0, false) คาด 0 ได้ 8000 · พลาด 4 จาก 6 กรณี
- t3-shipping-fee-r2 · `tests`: unittest พบ 5 เทสต์ (ต้องมีอย่างน้อย 6)
- t3-shipping-fee-r2 · `policy`: shipping_fee(3000, 0, false) คาด 0 ได้ 8000 · พลาด 4 จาก 6 กรณี
- t3-shipping-fee-r3 · `tests`: unittest พบ 4 เทสต์ (ต้องมีอย่างน้อย 6)
- t3-shipping-fee-r3 · `policy`: shipping_fee(3000, 0, false) คาด 0 ได้ 8000 · พลาด 4 จาก 6 กรณี
- t4-cashback-r1 · `policy`: cashback(20000, "silver", true) คาด 300 ได้ 600 · พลาด 6 จาก 6 กรณี
- t4-cashback-r2 · `policy`: cashback(20000, "silver", true) คาด 300 ได้ 600 · พลาด 6 จาก 6 กรณี
- t4-cashback-r3 · `tests`: unittest พบ 5 เทสต์ (ต้องมีอย่างน้อย 6)
- t4-cashback-r3 · `policy`: cashback(20000, "silver", true) คาด 300 ได้ 600 · พลาด 6 จาก 6 กรณี
