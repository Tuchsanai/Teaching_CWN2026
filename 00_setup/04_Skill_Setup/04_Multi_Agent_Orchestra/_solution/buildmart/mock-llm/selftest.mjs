// selftest ของ mock-llm: node selftest.mjs  (สตาร์ตเซิร์ฟเวอร์เองบน port สุ่ม แล้วยิง fixture จริงผ่าน HTTP)
import { createRequire } from 'node:module';
import assert from 'node:assert/strict';
const require = createRequire(import.meta.url);
process.env.MOCK_DELAY_MS = '0';
const { createServer } = require('./server.js');

// ---------------- fixtures (เลียนแบบสิ่งที่ chat-worker ส่ง) ----------------
const P = {
  'CEM-001': ['ปูนซีเมนต์ปอร์ตแลนด์ ประเภท 1 (50 กก.)', 145, 'ถุง', [800, 500, 300]],
  'CEM-002': ['ปูนก่อ สำเร็จรูป (50 กก.)', 120, 'ถุง', [400, 300, 0]],
  'CEM-003': ['ปูนฉาบ สำเร็จรูป (50 กก.)', 125, 'ถุง', [350, 250, 150]],
  'CEM-004': ['ปูนกาวซีเมนต์ ปูกระเบื้อง (20 กก.)', 185, 'ถุง', [200, 120, 80]],
  'AGG-001': ['ทรายหยาบ', 450, 'ลบ.ม.', [60, 40, 30]],
  'AGG-003': ['หิน 3/4 (หินเบอร์ 1)', 650, 'ลบ.ม.', [70, 50, 40]],
  'STL-003': ['เหล็กข้ออ้อย DB12 ยาว 10 ม.', 195, 'เส้น', [700, 500, 400]],
  'STL-004': ['เหล็กข้ออ้อย DB16 ยาว 10 ม.', 340, 'เส้น', [400, 300, 200]],
  'STL-005': ['ลวดผูกเหล็ก (1 กก.)', 55, 'ม้วน', [300, 200, 100]],
  'TIL-001': ['กระเบื้องพื้น 60x60 ลายหินอ่อน (กล่อง 4 แผ่น = 1.44 ตร.ม.)', 389, 'กล่อง', [400, 300, 200]],
  'TIL-002': ['กระเบื้องผนัง 30x60 ขาวเงา (กล่อง 8 แผ่น = 1.44 ตร.ม.)', 299, 'กล่อง', [300, 200, 150]],
  'ROF-001': ['กระเบื้องหลังคาลอนคู่ สีแดง (แผ่น)', 68, 'แผ่น', [3000, 2000, 1500]],
  'PNT-001': ['สีน้ำอะคริลิก ภายนอก สีขาว (แกลลอน 3.785 ล.)', 890, 'แกลลอน', [120, 80, 60]],
  'PNT-002': ['สีน้ำอะคริลิก ภายใน สีขาว (แกลลอน 3.785 ล.)', 590, 'แกลลอน', [150, 100, 80]],
  'PNT-003': ['สีรองพื้นปูนใหม่ (แกลลอน)', 650, 'แกลลอน', [100, 60, 40]],
  'ELC-001': ['สายไฟ THW 2.5 ตร.มม. (ม้วน 100 ม.)', 1650, 'ม้วน', [60, 40, 30]],
  'ELC-002': ['เบรกเกอร์ลูกย่อย 16A', 145, 'ตัว', [300, 200, 150]],
  'BRK-003': ['บล็อกประสาน (ก้อน)', 9, 'ก้อน', [5000, 3000, 0]],
};
const row = (s) => `- ${s} | ${P[s][0]} | ${P[s][1]} บาท/${P[s][2]} | สต็อก LKB ${P[s][3][0]} · BNA ${P[s][3][1]} · RST ${P[s][3][2]}`;

const D = {
  CEM: ['BM-DS-CEM.pdf', 1, 'BuildMart เอกสารข้อมูลสินค้า ปูนและคอนกรีต\nCEM-001 ปูนซีเมนต์ปอร์ตแลนด์ ประเภท 1 ผ่านมาตรฐาน มอก.15 กำลังอัดที่ 28 วัน ไม่น้อยกว่า 325 กก./ตร.ซม.\nการเก็บรักษา: เก็บได้ 3 เดือน นับจากวันผลิต วางบนพาเลทสูงจากพื้น 10 ซม. ซ้อนไม่เกิน 10 ถุง\nคอนกรีตต้องบ่มชื้นอย่างน้อย 7 วัน'],
  CEM2: ['BM-DS-CEM.pdf', 2, 'CEM-004 ปูนกาวซีเมนต์ ใช้ให้หมดภายใน 2 ชั่วโมงหลังผสม เดินได้หลัง 24 ชม. ผสมน้ำตามสัดส่วนที่ระบุข้างถุง'],
  STL: ['BM-DS-STL.pdf', 1, 'BuildMart เอกสารข้อมูลสินค้า เหล็กเสริม\nDB12/DB16 ชั้นคุณภาพ SD40 มาตรฐาน มอก.24-2559 กำลังครากไม่ต่ำกว่า 4,000 กก./ตร.ซม.\nRB6/RB9 ชั้น SR24 มอก.20-2559\nระยะทาบเหล็ก อย่างน้อย 40 เท่าของเส้นผ่านศูนย์กลาง (DB12 → 48 ซม., DB16 → 64 ซม.)\nเก็บเหล็กยกจากพื้น ไม่ให้โดนฝน'],
  PNT: ['BM-DS-PNT.pdf', 1, 'BuildMart เอกสารข้อมูลสินค้า สี\nPNT-001 สีน้ำอะคริลิกภายนอก รับประกัน 8 ปี · PNT-002 ภายใน รับประกัน 5 ปี\nทาเที่ยวที่ 2 ห่างจากเที่ยวแรก 2 ชั่วโมง ผสมน้ำไม่เกิน 10%\nผนังปูนใหม่ต้องรอ 28 วัน ก่อนทารองพื้น PNT-003'],
  TIL: ['BM-DS-TIL.pdf', 1, 'BuildMart เอกสารข้อมูลสินค้า กระเบื้อง\nTIL-001 กระเบื้องพอร์ซเลนเกรด A ดูดซึมน้ำ < 0.5% ปูพื้นภายนอกได้ ค่ากันลื่น R10\nTIL-002 สำหรับผนังเท่านั้น ห้ามปูพื้น\nเว้นร่องยาแนว 2–3 มม. ยาแนว TIL-003 รอ 24 ชม. ก่อนโดนน้ำ'],
  ELC: ['BM-DS-ELC-PIP.pdf', 1, 'BuildMart เอกสารข้อมูลสินค้า ไฟฟ้าและประปา\nสาย THW 2.5 ตร.มม. รับกระแสได้ 21 A ใช้คู่เบรกเกอร์ 16–20 A\nเบรกเกอร์ ELC-002 รับประกัน 2 ปี\nท่อ PVC ชั้น 13.5 ใช้น้ำดี/น้ำประปา ชั้น 8.5 ใช้น้ำทิ้ง กาวทาท่อ รอ 1 ชั่วโมง ก่อนเปิดน้ำ'],
  POL: ['BM-POLICY.pdf', 1, 'BuildMart นโยบายร้าน\nคืนสินค้าได้ภายใน 7 วัน สภาพเดิมพร้อมใบเสร็จ\nปูนที่เปิดถุงแล้วคืนไม่ได้ เหล็กที่สั่งตัดคืนไม่ได้\nสมาชิก BuildMart Pro ได้ 1 แต้มต่อทุก 100 บาท (100 แต้ม = ส่วนลด 50 บาท)\nรับประกันสินค้าไฟฟ้าตามผู้ผลิต'],
  PROMO: ['BM-PROMO-NOV.pdf', 1, 'โปรเดือนพฤศจิกายน: ซื้อปูน CEM-001 ครบ 100 ถุง แถมลวดผูกเหล็ก STL-005 2 ม้วน'],
};

function system(skus, docKeys, en = false) {
  const prod = skus.length ? skus.map(row).join('\n') : '- (ไม่พบสินค้าที่เกี่ยวข้อง)';
  const docs = docKeys.length ? docKeys.map((k, i) => `[${i + 1}] ${D[k][0]} หน้า ${D[k][1]}: ${D[k][2]}`).join('\n') : '(ไม่มีเอกสารที่เกี่ยวข้อง)';
  return `คุณคือ "น้องช่าง" ผู้ช่วยร้านวัสดุก่อสร้าง พูดสุภาพ ลงท้าย "ครับ"
## ข้อมูลร้าน
ชื่อร้าน: บ้านช่าง BuildMart
เวลาเปิด: จันทร์–เสาร์ 07:00–18:00 · อาทิตย์ 08:00–12:00
สาขา: LKB ลาดกระบัง โทร 02-111-0001 · BNA บางนา โทร 02-111-0002 · RST รังสิต โทร 02-111-0003
LINE: @buildmart-demo
ราคาสินค้ายังไม่รวม VAT · VAT 7% คิดตอนสรุปยอด
ราคาส่ง: 1–49 ชิ้น ราคาปกติ · 50–199 ชิ้น ลด 5% · 200 ชิ้นขึ้นไป ลด 10% (ต่อรายการ)
ค่าส่ง: ≤ 1,000 กก. กระบะ 500 บาท (ฟรีถ้ายอดก่อน VAT หลังส่วนลด ≥ 20,000) · 1,000.01–6,000 กก. รถ 6 ล้อ 1,500 บาท · > 6,000 กก. รถ 10 ล้อ 3,500 บาท
คูปอง: BUILD5 ลด 5% เมื่อยอดก่อน VAT ≥ 5,000 · CONTRACTOR10 ลด 10% เมื่อยอดก่อน VAT ≥ 30,000 (ใช้ได้ทีละ 1 ใบ)

## สินค้าที่เกี่ยวข้อง
${prod}

## เอกสารอ้างอิง
${docs}

## กฎ
- ตอบจากข้อมูลข้างบนเท่านั้น ห้ามแต่งราคา/สินค้า/สเปก · อ้างอิงเอกสารด้วย [n]
- คำนวณวัสดุ: [CALC]{"type":"concrete","volume":3} · ใส่ตะกร้า: [ADD_TO_CART]{"sku":"CEM-001","qty":21} · ใบเสนอราคา: [QUOTE]{}
${en ? '- ผู้ใช้พิมพ์ภาษาอังกฤษ ให้ตอบเป็นภาษาอังกฤษ (Answer in English)' : '- ตอบภาษาไทย'}`;
}
const msgs = (sys, ...rest) => [{ role: 'system', content: sys }, ...rest.map(([role, content]) => ({ role, content }))];

// ---------------- HTTP helpers ----------------
const srv = createServer();
await new Promise((r) => srv.listen(0, '127.0.0.1', r));
const BASE = `http://127.0.0.1:${srv.address().port}`;
async function ask(messages, stream = true) {
  const r = await fetch(`${BASE}/v1/chat/completions`, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ model: 'x', messages, stream, enable_thinking: false }) });
  assert.equal(r.status, 200);
  if (!stream) return (await r.json()).choices[0].message.content;
  const raw = await r.text();
  const lines = raw.split('\n').filter((l) => l.startsWith('data: '));
  assert.equal(lines.at(-1), 'data: [DONE]', 'stream must end with [DONE]');
  const deltas = lines.slice(0, -1).map((l) => JSON.parse(l.slice(6)).choices[0].delta.content || '');
  assert.ok(deltas.filter(Boolean).length >= 2, 'stream should have several deltas');
  return deltas.join('');
}

let pass = 0, fail = 0;
async function t(name, messages, checks, stream = true) {
  const out = await ask(messages, stream);
  const errs = [];
  for (const c of checks) {
    if (c instanceof RegExp ? !c.test(out) : !out.includes(c)) errs.push(String(c));
  }
  if (errs.length) {
    fail++;
    console.log(`FAIL ${name}: missing ${errs.join(', ')}\n----\n${out}\n----`);
  } else {
    pass++;
    console.log(`ok   ${name}: ${out.replace(/\n/g, ' ⏎ ').slice(0, 150)}`);
  }
  return out;
}
const not = (re) => new RegExp(`^(?![\\s\\S]*${re.source})`);
const noCite = not(/\[\d\]/);
const thEnd = /ครับ\s*(\n\[[A-Z_]+\].*)*$/;
const distract = ['CEM', 'POL', 'STL', 'PNT'];

// ---------------- endpoints ----------------
{
  const h = await (await fetch(`${BASE}/health`)).json();
  assert.equal(h.status, 'ok');
  const m = await (await fetch(`${BASE}/v1/models`)).json();
  assert.ok(m.data.length >= 1);
  console.log('ok   /health /v1/models');
}

// ---------------- C ----------------
await t('C01', msgs(system([], distract), ['user', 'ร้านเปิดกี่โมงครับ']), ['07:00', '18:00', noCite, thEnd]);
await t('C02', msgs(system([], distract), ['user', 'วันอาทิตย์เปิดไหม']), ['08:00', '12:00', noCite, thEnd]);
await t('C03', msgs(system(['CEM-001', 'CEM-002', 'CEM-003', 'CEM-004'], distract), ['user', 'ปูนซีเมนต์ถุงละเท่าไร']), ['145', 'CEM-001', noCite, thEnd]);
await t('C03-nonstream', msgs(system(['CEM-001', 'CEM-004'], distract), ['user', 'ปูนซีเมนต์ถุงละเท่าไร']), ['145'], false);
await t('C04', msgs(system(['STL-003', 'STL-004'], ['STL', 'CEM']), ['user', 'เหล็ก DB12 มีกี่สาขาที่มีของ']), ['3 สาขา', 'STL-003', noCite]);
await t('C05', msgs(system(['STL-003', 'STL-004'], ['STL']), ['user', 'ถ้าซื้อเหล็ก DB12 60 เส้น ได้ราคาเท่าไร']), ['185.25', '11,115']);
const c06a = await t('C06a', msgs(system(['CEM-001', 'AGG-001', 'AGG-003'], ['CEM']), ['user', 'เทพื้นคอนกรีต 3 คิว ต้องใช้ปูนกี่ถุง']), ['[CALC]{"type":"concrete","volume":3}']);
const calc6 = 'ผลคำนวณ: ' + JSON.stringify({ type: 'concrete', input: { volume: 3 }, rows: [{ sku: 'CEM-001', qty: 21, unit: 'ถุง', label: 'ปูนซีเมนต์ปอร์ตแลนด์ ประเภท 1 (50 กก.)' }, { sku: 'AGG-001', qty: 2, unit: 'ลบ.ม.', label: 'ทรายหยาบ' }, { sku: 'AGG-003', qty: 3, unit: 'ลบ.ม.', label: 'หิน 3/4 (หินเบอร์ 1)' }], extra: { volume: 3, mix: '1:2:4' } });
const c06 = await t('C06b', msgs(system(['CEM-001', 'AGG-001', 'AGG-003'], ['CEM']), ['user', 'เทพื้นคอนกรีต 3 คิว ต้องใช้ปูนกี่ถุง'], ['assistant', c06a], ['user', calc6]), ['21', 'CEM-001', thEnd, not(/\[CALC\]/)]);
// C07: history = ข้อความที่ chat-worker เก็บไว้ (คำตอบสุดท้ายแบบตัด tag แล้ว) ไม่มี ผลคำนวณ
await t('C07', msgs(system(['CEM-001', 'AGG-001', 'AGG-003'], ['CEM']), ['user', 'เทพื้นคอนกรีต 3 คิว ต้องใช้ปูนกี่ถุง'], ['assistant', c06], ['user', 'ใส่ตะกร้าให้เลย']), ['[ADD_TO_CART]{"sku":"CEM-001","qty":21}', '[ADD_TO_CART]{"sku":"AGG-001","qty":2}', '[ADD_TO_CART]{"sku":"AGG-003","qty":3}']);
await t('C07-withcalc', msgs(system([], []), ['user', 'เทพื้นคอนกรีต 3 คิว'], ['assistant', c06a], ['user', calc6], ['assistant', c06], ['user', 'ใส่ตะกร้าให้เลย']), ['[ADD_TO_CART]{"sku":"CEM-001","qty":21}']);
await t('C08', msgs(system([], distract), ['user', 'ขอใบเสนอราคาหน่อย']), ['[QUOTE]{}']);
await t('C08b', msgs(system([], []), ['user', 'ขอใบเสนอราคาหน่อย'], ['assistant', 'กำลังสร้างใบเสนอราคา\n[QUOTE]{}'], ['user', 'ผลคำสั่ง: {"quoteNo":"QT-20261023-0001","total":15607.29}']), ['QT-20261023-0001', '15,607.29', thEnd]);
await t('C09', msgs(system([], distract), ['user', 'ส่งของน้ำหนัก 5 ตันใช้รถอะไร ค่าส่งเท่าไร']), ['6 ล้อ', '1,500', noCite]);
await t('C10', msgs(system([], ['POL', 'CEM', 'PNT', 'STL']), ['user', 'มีโค้ดส่วนลดไหม']), ['BUILD5', 'CONTRACTOR10', thEnd]);
await t('C11', msgs(system(['TIL-001', 'TIL-002', 'ROF-001'], ['TIL', 'CEM2', 'POL', 'PNT']), ['user', 'มีกระเบื้องยางขายไหม']), ['ไม่มี', 'กระเบื้องยาง', noCite]);
await t('C12', msgs(system([], distract), ['user', 'ช่วยเขียนโค้ด Python ให้หน่อย']), ['ขออภัย', 'วัสดุก่อสร้าง', noCite, thEnd]);
const c13a = await t('C13a', msgs(system(['PNT-001', 'PNT-002', 'PNT-003'], ['PNT']), ['user', 'ทาสีบ้านภายนอก 120 ตร.ม. ใช้สีกี่แกลลอน']), ['[CALC]{"type":"paint","area":120,"coats":2,"paintType":"exterior"}']);
const calc13 = 'ผลคำนวณ: ' + JSON.stringify({ type: 'paint', input: { area: 120, coats: 2, paintType: 'exterior' }, rows: [{ sku: 'PNT-001', qty: 8, unit: 'แกลลอน', label: 'สีน้ำอะคริลิก ภายนอก สีขาว' }, { sku: 'PNT-003', qty: 3, unit: 'แกลลอน', label: 'สีรองพื้นปูนใหม่' }], extra: { area: 120, coats: 2, paintType: 'exterior' } });
const c13b = await t('C13b', msgs(system(['PNT-001', 'PNT-003'], ['PNT']), ['user', 'ทาสีบ้านภายนอก 120 ตร.ม. ใช้สีกี่แกลลอน'], ['assistant', c13a], ['user', calc13]), ['8 แกลลอน', 'PNT-001']);
await t('C13c', msgs(system(['PNT-001', 'PNT-003', 'PNT-002'], ['PNT']), ['user', 'ทาสีบ้านภายนอก 120 ตร.ม. ใช้สีกี่แกลลอน'], ['assistant', c13b], ['user', 'แล้วราคารวมเท่าไร']), ['7,120', '890', thEnd]);
await t('C14', msgs(system([], distract), ['user', 'สาขาบางนาเบอร์อะไร']), ['02-111-0002', noCite, thEnd]);

// ---------------- R ----------------
await t('R01', msgs(system(['CEM-001'], ['CEM', 'CEM2', 'POL', 'STL']), ['user', 'ปูนซีเมนต์เก็บได้นานแค่ไหนครับ']), ['3 เดือน', /\[1\]/, thEnd]);
await t('R02', msgs(system(['PNT-001', 'PNT-002'], ['TIL', 'PNT', 'POL', 'ELC']), ['user', 'สีทาภายนอกรับประกันกี่ปี']), ['8 ปี', /\[2\]/]);
await t('R03', msgs(system(['TIL-001'], ['TIL', 'CEM2', 'PNT', 'POL']), ['user', 'กระเบื้อง TIL-001 ปูพื้นนอกบ้านได้ไหม']), [/^ได้ครับ/, /0\.5%|R10/, /\[1\]/, not(/ห้ามปูพื้น/)]);
await t('R04', msgs(system(['CEM-001'], ['CEM', 'POL', 'CEM2', 'STL']), ['user', 'ซื้อปูนไปแล้วเปิดถุง ขอคืนได้ไหม']), ['คืนไม่ได้', /\[2\]/, /^ไม่ได้ครับ/]);
await t('R05', msgs(system(['STL-003'], ['CEM', 'STL', 'POL', 'PNT']), ['user', 'ทาบเหล็ก DB12 ต้องยาวเท่าไร']), ['48', /\[2\]/]);
await t('R06', msgs(system(['ELC-001', 'ELC-002'], ['ELC', 'POL', 'STL', 'CEM']), ['user', 'สาย THW 2.5 ใช้กับเบรกเกอร์กี่แอมป์ แล้วเบรกเกอร์ 16A ราคาเท่าไร']), ['16', '145', 'ELC-002', /\[1\]/]);
await t('R07', msgs(system(['CEM-001', 'STL-005'], ['CEM', 'PROMO', 'POL', 'STL']), ['user', 'เดือนพฤศจิกายนมีโปรอะไร']), ['ลวดผูกเหล็ก', /\[2\]/]);

// ---------------- Q / T / misc ----------------
await t('Q02', msgs(system(['CEM-001', 'CEM-004'], ['CEM', 'CEM2', 'POL', 'STL']), ['user', 'ปูนซีเมนต์ถุงละเท่าไร']), ['145']);
await t('Q-price', msgs(system(['PNT-002'], ['PNT']), ['user', 'สีน้ำอะคริลิกภายในราคาเท่าไร']), ['590', 'PNT-002']);
await t('T01', msgs(system([], distract), ['user', 'ร้านเปิดกี่โมงครับ']), ['07:00']);
await t('T02', msgs(system(['CEM-001', 'CEM-004'], ['CEM', 'POL'], true), ['user', 'How much is Portland cement?']), ['145', /baht/i, /^[^฀-๿]+$/, noCite]);
await t('T02-stock', msgs(system(['STL-003'], ['STL'], true), ['user', 'Is DB12 rebar in stock?']), ['3 branch', /^[^฀-๿]+$/]);
await t('T03', msgs(system([], distract), ['user', 'มีโค้ดส่วนลดไหม']), ['BUILD5']);
await t('fallback', msgs(system([], distract), ['user', 'สวัสดีครับ']), ['BuildMart', noCite, thEnd]);
await t('no-product', msgs(system([], ['POL']), ['user', 'กระเบื้องยางราคาเท่าไร']), ['ไม่พบสินค้า', noCite]);

// concurrency (Q01)
const many = await Promise.all(Array.from({ length: 8 }, () => ask(msgs(system(['CEM-001'], distract), ['user', 'ปูนซีเมนต์ถุงละเท่าไร']))));
assert.ok(many.every((x) => x.includes('145')));
console.log('ok   8 concurrent streams');

srv.close();
console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
