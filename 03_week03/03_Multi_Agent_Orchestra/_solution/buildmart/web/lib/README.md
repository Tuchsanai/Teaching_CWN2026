# web/lib (A)

- `@/shared/*` = ROOT/shared — `web/Dockerfile` คัดลอก `ROOT/shared/` ไปไว้ที่ `web/shared/` ก่อน `next build`
  ใช้: `import { computeTotals, tierPrice, tierTable, formatBaht } from '@/shared/pricing.js'` · `import { calculate } from '@/shared/calc.js'`
  (รัน `next dev` นอก docker: `cp -r ../shared ./shared` ก่อน — `web/shared/` อยู่ใน .gitignore)
- `@/lib/db` — `pool`, `query(sql, params)`, `tx(fn)` · numeric / int8 คืนเป็น number
- `@/lib/amqp` — `rpc`, `sendToQueue`, `publish`, `onReply`, `checkQueue`, `getChannel`, `instanceId`, `Q`, `EX`
- `@/lib/session` — `getSessionId()`, `peekSessionId()` (cookie `bm_sid` สร้างโดย `middleware.ts`)
- `@/lib/categories` — `CATEGORIES` 11 หมวด
- ตัวเลขตะกร้าบน header: `window.dispatchEvent(new CustomEvent('bm:cart', { detail: { count } }))` (ไม่ใส่ detail = ให้ header ดึง `/api/cart/count` ใหม่)
