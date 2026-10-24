| endpoint | ครั้ง | status | query | request body keys | response keys |
|---|---|---|---|---|---|
| `GET /api/slots` | 1 | 200 | service, date, type, people |  | date, service, durationMin, min, max, slots |
| `POST /api/price` | 2 | 200 |  | type, serviceCode, people, date, time, therapists, contactName, contactPhone, redeemBlocks, useBirthday, giftCardCode, hotelCode, distanceKm, coursePurchaseId | service, type, people, date, time, endTime, whenLabel, gross, discountKind, discountPct, discountAmount, pointsRedeemed, pointsDiscount, subtotal, distanceKm, vehicles, transportFee, total, totalLabel, giftcardPaid, otherPaid, pointsToEarn, lines, birthdayAvailable, maxRedeemBlocks, pointsBalance, loggedIn, course, giftCard, giftCardError |
| `POST /api/bookings` | 1 | 201 |  | type, serviceCode, people, date, time, therapists, contactName, contactPhone, redeemBlocks, useBirthday, giftCardCode, hotelCode, distanceKm, coursePurchaseId, quotedTotal | bookingId, code, status, total, totalLabel, therapists, therapistNames, message, detail, quote |
| `POST /api/auth/login` | 2 | 200 |  |  | ok, user |
| `POST /api/bookings/{id}/cancel` | 1 | 200 |  |  | ok, bookingId, code, status |
| `POST /api/auth/logout` | 1 | 200 |  |  | ok |
| `GET /api/admin/bookings` | 2 | 200 | date |  | date, today, bookings |
