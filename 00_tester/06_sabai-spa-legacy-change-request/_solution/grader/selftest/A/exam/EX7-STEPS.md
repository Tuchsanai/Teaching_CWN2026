# EX7 แตกงานเป็นขั้น

1. อ่าน `point_txn` (reason earn/redeem/refund/opening) และ `customer.points_balance`
2. API `GET /api/me/points` (`pointsHistory` ใน `web/lib/server/customer.ts`) · balanceAfter สะสมจากเก่าไปใหม่แล้วกลับลำดับ
3. เทสต์ API (`tests/exam7/points-history.mjs`)
4. หน้า `/account` ส่วน `points-history` + ป้าย 3 ภาษาใน i18n
5. เทสต์ Playwright (`tests/exam7/points-history.spec.ts`) · check-rules ไม่เปลี่ยน
