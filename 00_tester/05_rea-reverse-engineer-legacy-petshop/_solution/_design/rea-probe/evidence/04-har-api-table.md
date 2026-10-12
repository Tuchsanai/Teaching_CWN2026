| # | method | path | status | request body keys | response keys |
|---|---|---|---|---|---|
| 1 | POST | `/api/coupons/validate` | 200 | code, items | ok, code, discount, freeShipping, message |
| 2 | POST | `/api/auth/login` | 200 | email, password | user |
| 3 | POST | `/api/orders` | 201 | items, coupon, shipping, payment, address | order, id |
| 4 | GET | `/api/products` | 200 | - | items, total |
