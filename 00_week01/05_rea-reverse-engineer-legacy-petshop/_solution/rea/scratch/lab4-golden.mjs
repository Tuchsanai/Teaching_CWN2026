// LAB 4: record API golden files from the running web (characterization · [E]).
// usage: node rea\scratch\lab4-golden.mjs   → e2e-legacy\tests\new\golden\products.json + coupons-validate.json
import { writeFileSync, mkdirSync } from 'node:fs';
const B = process.env.BASE_URL ?? 'http://localhost:4000';
const dir = new URL('../../e2e-legacy/tests/new/golden/', import.meta.url);
mkdirSync(dir, { recursive: true });
const save = (name, data) => writeFileSync(new URL(name, dir), JSON.stringify(data, null, 2) + '\n', 'utf8');

// 1) GET /api/products — stock changes with every order, so it is removed
const products = await (await fetch(`${B}/api/products`)).json();
save('products.json', {
  _source: `[E] GET ${B}/api/products · recorded ${new Date().toISOString()} · field "stock" removed`,
  total: products.total,
  items: products.items.map(({ stock, ...rest }) => rest),
});

// 2) POST /api/coupons/validate — same carts the spec uses
const carts = {
  'treat-69': [{ slug: 'lickable-salmon-treat', size: '4 ซอง', qty: 1 }],
  'mixed-998': [{ slug: 'kitten-salmon-dry', size: '1.5 kg', qty: 1 }, { slug: 'dental-chew-treat', size: '7 ชิ้น', qty: 1 }, { slug: 'cat-scratcher', size: '1 ชิ้น', qty: 1 }],
  'nocatfood-999': [{ slug: 'cat-feather-wand', size: '1 ชิ้น', qty: 1 }, { slug: 'dog-slow-bowl', size: '1 ใบ', qty: 3 }],
  'catfood-499': [{ slug: 'tuna-pouch', size: 'แพ็ค 12 ซอง', qty: 1 }, { slug: 'tuna-pouch', size: 'ซอง 85 g', qty: 2 }, { slug: 'kitten-chicken-mousse', size: 'ซอง 85 g', qty: 1 }],
  'catfood-520': [{ slug: 'hairball-control-dry', size: '1.5 kg', qty: 1 }],
};
const codes = ['PAW10', 'paw10', 'FREESHIP', 'NEWCAT50', 'SUMMER20', 'XYZ'];
const cases = [];
for (const [cart, items] of Object.entries(carts)) {
  for (const code of codes) {
    const r = await fetch(`${B}/api/coupons/validate`, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ code, items }) });
    cases.push({ cart, code, items, status: r.status, response: await r.json() });
  }
}
save('coupons-validate.json', { _source: `[E] POST ${B}/api/coupons/validate · recorded ${new Date().toISOString()}`, cases });
console.log('products', products.items.length, 'coupon cases', cases.length);
