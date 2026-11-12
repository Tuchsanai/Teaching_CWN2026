// node shared/selftest.mjs — ตรวจตัวเลขเกณฑ์ W05–W10, C05, C09, C13 ของ BUILDMART
import assert from 'node:assert/strict';
import { tierPrice, computeTotals, formatBaht, shippingFor, tierTable } from './pricing.js';
import { calculate } from './calc.js';

const P = {
  'CEM-001': { price: 145, weight_kg: 50 },
  'STL-003': { price: 195, weight_kg: 8.88 },
  'AGG-003': { price: 650, weight_kg: 1600 },
  'PNT-001': { price: 890, weight_kg: 5 },
};
const item = (sku, qty) => ({ sku, qty, ...P[sku] });
const qtys = (r) => Object.fromEntries(r.rows.map((x) => [x.sku, x.qty]));
let n = 0;
const ok = (name, fn) => { fn(); n++; console.log('  ok', name); };

ok('W03 tier table STL-003', () => assert.deepEqual(tierTable(195).map((t) => t.price), [195, 185.25, 175.5]));
ok('W05 concrete 3 m3', () => assert.deepEqual(qtys(calculate('concrete', { volume: 3 })), { 'CEM-001': 21, 'AGG-001': 2, 'AGG-003': 3 }));
ok('W06 tile 50 m2', () => assert.deepEqual(qtys(calculate('tile', { area: 50 })), { 'TIL-001': 39, 'CEM-004': 13, 'TIL-003': 10 }));
ok('W07 paint 120 m2 x2 exterior', () =>
  assert.deepEqual(qtys(calculate('paint', { area: 120, coats: 2, paintType: 'exterior' })), { 'PNT-001': 8, 'PNT-003': 3 }));
ok('wall brick / light', () => {
  assert.deepEqual(qtys(calculate('wall', { area: 10 })), { 'BRK-001': 1400, 'CEM-002': 3 });
  assert.deepEqual(qtys(calculate('wall', { area: 10, wallType: 'light' })), { 'BRK-002': 84, 'CEM-002': 2 });
});
ok('rebar DB12 100 m', () => {
  const r = calculate('rebar', { size: 'DB12', length: 100 });
  assert.equal(r.bars, 10);
  assert.equal(r.weightKg, 88.8);
  assert.deepEqual(qtys(r), { 'STL-003': 10 });
});
ok('W08/C05 STL-003 x60 = 185.25', () => {
  assert.equal(tierPrice(195, 60), 185.25);
  assert.equal(computeTotals({ items: [item('STL-003', 60)] }).lines[0].unitPrice, 185.25);
});
ok('W09 CEM-001 x100 + BUILD5', () => {
  const t = computeTotals({ items: [item('CEM-001', 100)], coupon: 'BUILD5' });
  assert.equal(t.lines[0].unitPrice, 137.75);
  assert.equal(t.subtotal, 13775);
  assert.equal(t.discount, 688.75);
  assert.equal(t.afterDiscount, 13086.25);
  assert.equal(t.weight, 5000);
  assert.equal(t.vehicle, '6wheel');
  assert.equal(t.vehicleLabel, 'รถ 6 ล้อ');
  assert.equal(t.shipping, 1500);
  assert.equal(t.vat, 1021.04);
  assert.equal(t.total, 15607.29);
  assert.equal(formatBaht(t.total), '15,607.29');
  assert.equal(formatBaht(t.subtotal), '13,775.00');
});
ok('W10 AGG-003 x4 → 10 wheel 3,500', () => {
  const t = computeTotals({ items: [item('AGG-003', 4)] });
  assert.equal(t.weight, 6400);
  assert.equal(t.vehicle, '10wheel');
  assert.equal(t.shipping, 3500);
});
ok('C09 5 ton → 6 wheel 1,500', () => assert.deepEqual(shippingFor(5000), { vehicle: '6wheel', vehicleLabel: 'รถ 6 ล้อ', shipping: 1500 }));
ok('C13 paint 120 exterior → 8 gal, 7,120', () => {
  const g = qtys(calculate('paint', { area: 120, paintType: 'exterior' }))['PNT-001'];
  assert.equal(g, 8);
  assert.equal(computeTotals({ items: [item('PNT-001', g)] }).subtotal, 7120);
});
ok('coupon rules', () => {
  assert.ok(computeTotals({ items: [item('CEM-001', 10)], coupon: 'BUILD5' }).couponError);
  assert.ok(computeTotals({ items: [item('CEM-001', 10)], coupon: 'NOPE' }).couponError);
  assert.equal(computeTotals({ items: [item('CEM-001', 300)], coupon: 'CONTRACTOR10' }).discount, 3915);
});
ok('free pickup ≥ 20,000', () => {
  assert.equal(shippingFor(500, 20000).shipping, 0);
  assert.equal(shippingFor(500, 19999.99).shipping, 500);
  assert.equal(computeTotals({ items: [] }).total, 0);
});
console.log(`selftest OK (${n} checks)`);
