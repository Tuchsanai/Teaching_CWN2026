// LAB 8 step 5: POST /api/orders per TC table (new user, no UI) then GET /api/orders/[id] and compare.
// usage: node rea\scratch\lab8-api.mjs  (resets test data first)
const BASE = process.env.BASE ?? 'http://localhost:4000';
const L = (slug, size, qty = 1) => ({ slug, size, qty });
const B = {
  B1499: [L('kitten-salmon-dry', '400 g'), L('cat-fountain', '2 ลิตร'), L('small-breed-chicken-dry', '1.5 kg')],
  B1500: [L('dog-slow-bowl', '1 ใบ'), L('adult-lamb-dry', '3 kg'), L('small-breed-chicken-dry', '1.5 kg')],
  B189: [L('kitten-salmon-dry', '400 g')],
  B378: [L('kitten-salmon-dry', '400 g', 2)],
  B999: [L('small-breed-chicken-dry', '1.5 kg'), L('cat-tunnel', '1 ชิ้น'), L('kitten-salmon-dry', '400 g')],
  B998: [L('adult-chicken-dry', '3 kg'), L('dog-squeaky-ball', 'แพ็ค 3 ลูก')],
  B590: [L('kitten-salmon-dry', '1.5 kg')],
  B489: [L('kitten-chicken-mousse', 'แพ็ค 12 ซอง'), L('lickable-salmon-treat', '4 ซอง')],
};
const ADDRESS = { name: 'นักทดสอบ API', phone: '0812345678', address: '99/9 ถนนสุขุมวิท', province: 'กรุงเทพมหานคร', postcode: '10110' };
// [id, basket, extra body, expected {giftWrap, giftWrapFee, discount, shipping, total}]
const CASES = [
  ['TC-GIFT-03', 'B1499', { giftWrap: true }, { giftWrap: true, giftWrapFee: 30, discount: 0, shipping: 0, total: 1529 }],
  ['TC-GIFT-04', 'B1500', { giftWrap: true }, { giftWrap: true, giftWrapFee: 0, discount: 0, shipping: 0, total: 1500 }],
  ['TC-GIFT-05', 'B1500', { giftWrap: true, coupon: 'PAW10' }, { giftWrap: true, giftWrapFee: 0, discount: 150, shipping: 0, total: 1350 }],
  ['TC-GIFT-06', 'B189', { giftWrap: true, coupon: 'FREESHIP' }, { giftWrap: true, giftWrapFee: 30, discount: 0, shipping: 0, total: 219 }],
  ['TC-GIFT-07', 'B590', { giftWrap: true, shipping: 'express' }, { giftWrap: true, giftWrapFee: 30, discount: 0, shipping: 120, total: 740 }],
  ['TC-GIFT-08', 'B998', { giftWrap: true }, { giftWrap: true, giftWrapFee: 30, discount: 0, shipping: 50, total: 1078 }],
  ['TC-GIFT-09', 'B999', { giftWrap: true }, { giftWrap: true, giftWrapFee: 30, discount: 0, shipping: 0, total: 1029 }],
  ['TC-GIFT-10', 'B189', { giftWrap: true }, { giftWrap: true, giftWrapFee: 30, discount: 0, shipping: 50, total: 269 }],
  ['TC-GIFT-11', 'B189', { giftWrap: false }, { giftWrap: false, giftWrapFee: 0, discount: 0, shipping: 50, total: 239 }],
  ['TC-GIFT-12 "true"', 'B189', { giftWrap: 'true' }, { giftWrap: false, giftWrapFee: 0, discount: 0, shipping: 50, total: 239 }],
  ['TC-GIFT-12 1', 'B189', { giftWrap: 1 }, { giftWrap: false, giftWrapFee: 0, discount: 0, shipping: 50, total: 239 }],
  ['TC-GIFT-12 "yes"', 'B189', { giftWrap: 'yes' }, { giftWrap: false, giftWrapFee: 0, discount: 0, shipping: 50, total: 239 }],
  ['TC-GIFT-12 null', 'B189', { giftWrap: null }, { giftWrap: false, giftWrapFee: 0, discount: 0, shipping: 50, total: 239 }],
  ['TC-GIFT-14', 'B378', { giftWrap: true }, { giftWrap: true, giftWrapFee: 30, discount: 0, shipping: 50, total: 458 }],
  ['TC-GIFT-15', 'B189', { giftWrap: true, coupon: 'PAW10' }, { giftWrap: true, giftWrapFee: 30, discount: 18, shipping: 50, total: 251 }],
  ['TC-GIFT-16', 'B489', { giftWrap: true, coupon: 'NEWCAT50' }, { giftWrap: true, giftWrapFee: 30, discount: 0, shipping: 50, total: 569 }],
  ['TC-GIFT-18', 'B189', {}, { giftWrap: false, giftWrapFee: 0, discount: 0, shipping: 50, total: 239 }],
  ['extra · ปลอม fee/total ใน body', 'B189', { giftWrap: true, giftWrapFee: 0, total: 1, shippingFee: 0 }, { giftWrap: true, giftWrapFee: 30, discount: 0, shipping: 50, total: 269 }],
];

const reset = await fetch(`${BASE}/api/test/reset`, { method: 'POST' });
if (!reset.ok) throw new Error(`reset ${reset.status}`);
const email = `lab8-api-${Date.now()}@example.test`;
const reg = await fetch(`${BASE}/api/auth/register`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ name: 'นักทดสอบ API', email, password: 'Test1234', confirm: 'Test1234', pet: 'cat', terms: true }),
});
if (!reg.ok) throw new Error(`register ${reg.status} ${await reg.text()}`);
const cookie = (reg.headers.getSetCookie?.() ?? [reg.headers.get('set-cookie')]).map((c) => c.split(';')[0]).join('; ');

const keys = ['giftWrap', 'giftWrapFee', 'discount', 'shipping', 'total'];
let pass = 0;
const rows = [];
for (const [id, basket, extra, exp] of CASES) {
  const res = await fetch(`${BASE}/api/orders`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', cookie },
    body: JSON.stringify({ items: B[basket], shipping: 'standard', payment: 'cod', address: ADDRESS, ...extra }),
  });
  const body = await res.json();
  const o = body.order ?? {};
  const g = await (await fetch(`${BASE}/api/orders/${o.id}`, { headers: { cookie } })).json();
  const got = Object.fromEntries(keys.map((k) => [k, o[k]]));
  const gotGet = Object.fromEntries(keys.map((k) => [k, g.order?.[k]]));
  const ok = res.status === 201 && keys.every((k) => got[k] === exp[k] && gotGet[k] === exp[k]);
  if (ok) pass++;
  rows.push(`| ${id} | ${basket} | \`${JSON.stringify(extra)}\` | ${res.status} | ${got.giftWrap}/${got.giftWrapFee}/${got.discount}/${got.shipping}/**${got.total}** | ${gotGet.total} | ${exp.giftWrap}/${exp.giftWrapFee}/${exp.discount}/${exp.shipping}/**${exp.total}** | ${ok ? '✅' : '❌'} |`);
}
console.log('| TC | ตะกร้า | body เพิ่ม | HTTP | response giftWrap/fee/ส่วนลด/ค่าส่ง/total | GET total | คาด | ผล |');
console.log('|---|---|---|---|---|---|---|---|');
console.log(rows.join('\n'));
console.log(`\n${pass}/${CASES.length} ตรงตาราง (response และ GET /api/orders/[id])`);
