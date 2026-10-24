// LAB 4 probe: ask the running web (API only) what it charges for boundary carts.
// usage: node rea\scratch\lab4-probe.mjs   (web at http://localhost:4000 · creates 1 random user + a few orders)
const B = process.env.BASE_URL ?? 'http://localhost:4000';
const j = (r) => r.json();
const post = (path, body, cookie) =>
  fetch(B + path, { method: 'POST', headers: { 'content-type': 'application/json', ...(cookie ? { cookie } : {}) }, body: JSON.stringify(body) });

const carts = {
  s998: [{ slug: 'kitten-salmon-dry', size: '1.5 kg', qty: 1 }, { slug: 'dental-chew-treat', size: '7 ชิ้น', qty: 1 }, { slug: 'cat-scratcher', size: '1 ชิ้น', qty: 1 }],
  s999: [{ slug: 'cat-feather-wand', size: '1 ชิ้น', qty: 1 }, { slug: 'dog-slow-bowl', size: '1 ใบ', qty: 3 }],
  cat499: [{ slug: 'tuna-pouch', size: 'แพ็ค 12 ซอง', qty: 1 }, { slug: 'tuna-pouch', size: 'ซอง 85 g', qty: 2 }, { slug: 'kitten-chicken-mousse', size: 'ซอง 85 g', qty: 1 }],
  cat520: [{ slug: 'hairball-control-dry', size: '1.5 kg', qty: 1 }],
  treat69: [{ slug: 'lickable-salmon-treat', size: '4 ซอง', qty: 1 }],
  s999mixCat: [{ slug: 'kitten-salmon-dry', size: '1.5 kg', qty: 1 }, { slug: 'duck-jerky-treat', size: '100 g', qty: 1 }, { slug: 'puppy-lamb-wet', size: '100 g', qty: 1 }, { slug: 'puppy-lamb-wet', size: '100 g', qty: 1 }],
};
const codes = ['PAW10', 'FREESHIP', 'NEWCAT50', 'SUMMER20', 'XYZ', 'paw10'];

for (const [name, items] of Object.entries(carts)) {
  const sub = 0;
  for (const code of codes) {
    const r = await post('/api/coupons/validate', { code, items });
    console.log(name, code, r.status, JSON.stringify(await j(r)));
  }
}

if (process.argv.includes('--order')) {
  const email = `probe-${Date.now()}-${Math.floor(Math.random() * 1e6)}@test.dev`;
  const reg = await post('/api/auth/register', { name: 'นักทดสอบ ใจเย็น', email, password: 'Test1234', confirm: 'Test1234', pet: 'cat', terms: true });
  const cookie = (reg.headers.get('set-cookie') ?? '').split(';')[0];
  console.log('register', reg.status);
  const address = { name: 'นักทดสอบ ใจเย็น', phone: '0812345678', address: '99/9 ถนนสุขุมวิท แขวงคลองเตย', province: 'กรุงเทพมหานคร', postcode: '10110' };
  for (const [name, items, shipping, coupon] of [
    ['s998', carts.s998, 'standard', null], ['s999', carts.s999, 'standard', null], ['s999', carts.s999, 'express', null],
    ['s998', carts.s998, 'express', null], ['s999', carts.s999, 'standard', 'PAW10'],
  ]) {
    const r = await post('/api/orders', { items, coupon, shipping, payment: 'cod', address }, cookie);
    const o = (await j(r)).order ?? {};
    console.log('ORDER', name, shipping, coupon, r.status, JSON.stringify({ subtotal: o.subtotal, discount: o.discount, shipping: o.shipping, total: o.total, coupon: o.coupon, shippingMethod: o.shippingMethod }));
  }
}
