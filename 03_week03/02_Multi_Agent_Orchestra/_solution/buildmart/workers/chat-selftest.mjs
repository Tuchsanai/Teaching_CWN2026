// workers/chat-selftest.mjs — ทดสอบ chat-worker ครบวงจร (C01–C14 · R01–R08 · Q01 · T02 · retry/DLQ)
//
// วิธีรัน (ใน container — มี amqplib/pg และเห็น rabbitmq/db/web ใน network):
//   docker compose -p buildmart exec -T chat-worker node chat-selftest.mjs            # auto: /api/chat ถ้ามี ไม่งั้น RPC คิวตรง
//   docker compose -p buildmart exec -T chat-worker node chat-selftest.mjs --rpc      # บังคับยิงคิว chat.request ตรง
//   docker compose -p buildmart exec -T chat-worker node chat-selftest.mjs --http     # บังคับผ่าน POST /api/chat (SSE)
//   เติม --dlq เพื่อทดสอบ retry 2 ครั้ง → chat.dlq (แล้วดึงข้อความทดสอบออกจาก DLQ ให้)
//   นอก docker: ตั้ง CHAT_BASE=http://localhost:3400 แล้วใช้ --http
import { randomUUID } from 'node:crypto';
import amqp from 'amqplib';
import pg from 'pg';
import { assertTopology, Q, EX } from '../shared/topology.js';

const args = new Set(process.argv.slice(2));
const BASE = process.env.CHAT_BASE || (process.env.DATABASE_URL ? 'http://web:3000' : 'http://localhost:3400');
const pool = new pg.Pool({ connectionString: process.env.DATABASE_URL || 'postgres://bm:bm@localhost:5432/buildmart', max: 3 });

// ---------------------------------------------------------------- transport
let mode = args.has('--rpc') ? 'rpc' : args.has('--http') ? 'http' : null;
if (!mode) {
  try {
    const r = await fetch(`${BASE}/api/chat/history`, { signal: AbortSignal.timeout(4000) });
    mode = r.status === 404 ? 'rpc' : 'http';
  } catch {
    mode = 'rpc';
  }
}

let conn, ch, replyKey;
const waiting = new Map(); // correlationId -> {events, resolve}
async function rpcSetup() {
  conn = await amqp.connect(process.env.AMQP_URL || 'amqp://guest:guest@localhost:5672');
  ch = await conn.createChannel();
  await assertTopology(ch);
  replyKey = 'selftest-' + randomUUID().slice(0, 8);
  const q = await ch.assertQueue(`chat.reply.${replyKey}`, { exclusive: true, autoDelete: true });
  await ch.bindQueue(q.queue, EX.CHAT_REPLY, replyKey);
  await ch.consume(q.queue, (m) => {
    const w = waiting.get(m.properties.correlationId);
    if (!w) return;
    const b = JSON.parse(m.content.toString());
    w.events.push(b);
    if (b.type === 'done' || b.type === 'error') {
      waiting.delete(m.properties.correlationId);
      w.resolve(b);
    }
  }, { noAck: true });
}

const sessions = new Map(); // ชื่อ session ทดสอบ → sessionId (rpc) / cookie (http)
async function ask(session, text, timeoutMs = 120000) {
  const t0 = Date.now();
  if (mode === 'rpc') {
    if (!sessions.has(session)) sessions.set(session, `selftest-${Date.now()}-${session}-${randomUUID().slice(0, 4)}`);
    const sessionId = sessions.get(session);
    const messageId = randomUUID();
    const events = [];
    const p = new Promise((resolve, reject) => {
      waiting.set(messageId, { events, resolve });
      setTimeout(() => reject(new Error('timeout')), timeoutMs);
    });
    ch.sendToQueue(Q.CHAT_REQUEST, Buffer.from(JSON.stringify({ sessionId, messageId, text })), {
      persistent: true, replyTo: replyKey, correlationId: messageId, contentType: 'application/json',
    });
    const done = await p;
    return { ...done, events, sessionId, ms: Date.now() - t0 };
  }
  // http: POST /api/chat → SSE
  const headers = { 'content-type': 'application/json' };
  if (sessions.get(session)) headers.cookie = sessions.get(session);
  const r = await fetch(`${BASE}/api/chat`, { method: 'POST', headers, body: JSON.stringify({ text }), signal: AbortSignal.timeout(timeoutMs) });
  const sc = r.headers.get('set-cookie');
  if (sc && !sessions.get(session)) sessions.set(session, sc.split(';')[0]);
  const raw = await r.text();
  const events = [];
  for (const block of raw.split(/\n\n/)) {
    const ev = (block.match(/^event:\s*(.+)$/m) || [])[1];
    const data = (block.match(/^data:\s*(.+)$/m) || [])[1];
    if (!ev) continue;
    let d = {};
    try { d = JSON.parse(data); } catch {}
    events.push({ type: ev.trim(), ...d });
  }
  const done = events.find((e) => e.type === 'done' || e.type === 'error') || { type: 'error', text: raw.slice(0, 200) };
  return { ...done, events, ms: Date.now() - t0 };
}

// ---------------------------------------------------------------- checks
let pass = 0, fail = 0, skip = 0;
const results = [];
function check(name, r, conds) {
  const errs = [];
  for (const [label, ok] of conds) if (!ok) errs.push(label);
  const line = (r?.text || '').replace(/\n/g, ' ⏎ ').slice(0, 140);
  if (errs.length) {
    fail++;
    console.log(`FAIL ${name} (${r?.ms}ms): ${errs.join(' · ')}\n     → ${line}  cites=${JSON.stringify(r?.cites || [])}`);
  } else {
    pass++;
    console.log(`ok   ${name} (${r?.ms}ms): ${line}${r?.cites?.length ? '  📄 ' + r.cites.map((c) => `${c.filename}#${c.page}`).join(', ') : ''}`);
  }
  results.push({ name, ok: !errs.length, ms: r?.ms, text: r?.text, cites: r?.cites });
}
const has = (r, s) => [`มี "${s}"`, (r.text || '').includes(s)];
const re = (r, x, label) => [label || String(x), x.test(r.text || '')];
const noCite = (r) => ['ไม่มี cite', !(r.cites || []).length];
const citeFile = (r, f) => [`cite ${f}`, (r.cites || []).some((c) => c.filename === f)];
const isDone = (r) => ['type done', r.type === 'done'];
const noTag = (r) => ['ไม่มี tag/[n] หลุด', !/\[(CALC|ADD_TO_CART|QUOTE)\]|\[\d\]|<think>/.test(r.text || '')];
const gotStatus = (r) => ['status thinking', mode === 'http' || r.events.some((e) => e.type === 'status' && e.status === 'thinking')];

async function cartQty(sessionId, sku) {
  const x = await pool.query(`SELECT ci.qty FROM carts c JOIN cart_items ci ON ci.cart_id = c.id WHERE c.session_id = $1 AND ci.sku = $2`, [sessionId, sku]);
  return x.rows[0]?.qty ?? 0;
}

// ---------------------------------------------------------------- run
if (mode === 'rpc') await rpcSetup();
console.log(`chat-selftest mode=${mode}${mode === 'http' ? ' base=' + BASE : ''}\n`);

const docCount = Number((await pool.query(`SELECT count(*)::int AS n FROM docs WHERE status = 'ready'`)).rows[0].n);

let r;
r = await ask('c01', 'ร้านเปิดกี่โมงครับ'); check('C01', r, [isDone(r), gotStatus(r), has(r, '07:00'), has(r, '18:00'), noCite(r), noTag(r)]);
r = await ask('c02', 'วันอาทิตย์เปิดไหม'); check('C02', r, [has(r, '08:00'), has(r, '12:00'), noCite(r)]);
r = await ask('c03', 'ปูนซีเมนต์ถุงละเท่าไร'); check('C03', r, [has(r, '145'), noCite(r), ['มี delta', mode === 'http' || r.events.some((e) => e.type === 'delta')]]);
r = await ask('c04', 'เหล็ก DB12 มีกี่สาขาที่มีของ'); check('C04', r, [has(r, '3 สาขา')]);
r = await ask('c05', 'ถ้าซื้อเหล็ก DB12 60 เส้น ได้ราคาเท่าไร'); check('C05', r, [has(r, '185.25')]);

r = await ask('c06', 'เทพื้นคอนกรีต 3 คิว ต้องใช้ปูนกี่ถุง'); check('C06', r, [has(r, '21'), noTag(r), noCite(r)]);
const before = r.cartCount ?? 0;
r = await ask('c06', 'ใส่ตะกร้าให้เลย');
check('C07', r, [isDone(r), ['cartCount เพิ่ม ≥ 21', (r.cartCount ?? 0) >= before + 21], ...(mode === 'rpc' ? [['DB: CEM-001 × 21', (await cartQty(r.sessionId, 'CEM-001')) === 21]] : []), noTag(r)]);
r = await ask('c06', 'ขอใบเสนอราคาหน่อย');
check('C08', r, [re(r, /QT-\d{8}-\d{4}/, 'มีเลข QT-'), ['done.quoteNo', /^QT-/.test(r.quoteNo || '')], noTag(r)]);
if (mode === 'rpc' && r.quoteNo) {
  const qt = await pool.query('SELECT totals FROM quotes WHERE quote_no = $1', [r.quoteNo]);
  check('C08-db', r, [['quote อยู่ใน DB', qt.rowCount === 1]]);
}
r = await ask('c08e', 'ขอใบเสนอราคาหน่อย'); check('C08-empty', r, [re(r, /ว่าง|เพิ่มสินค้า/, 'บอกว่าตะกร้าว่าง'), ['ไม่มี quoteNo', !r.quoteNo]]);

r = await ask('c09', 'ส่งของน้ำหนัก 5 ตันใช้รถอะไร ค่าส่งเท่าไร'); check('C09', r, [has(r, '6 ล้อ'), has(r, '1,500'), noCite(r)]);
r = await ask('c10', 'มีโค้ดส่วนลดไหม'); check('C10', r, [has(r, 'BUILD5'), has(r, 'CONTRACTOR10')]);
r = await ask('c11', 'มีกระเบื้องยางขายไหม'); check('C11', r, [has(r, 'ไม่มี'), noCite(r)]);
r = await ask('c12', 'ช่วยเขียนโค้ด Python ให้หน่อย'); check('C12', r, [re(r, /ขออภัย|ขอโทษ/, 'ปฏิเสธสุภาพ'), has(r, 'วัสดุ'), noCite(r)]);
r = await ask('c13', 'ทาสีบ้านภายนอก 120 ตร.ม. ใช้สีกี่แกลลอน'); check('C13a', r, [has(r, '8 แกลลอน'), noTag(r)]);
r = await ask('c13', 'แล้วราคารวมเท่าไร'); check('C13b', r, [has(r, '7,120')]);
r = await ask('c14', 'สาขาบางนาเบอร์อะไร'); check('C14', r, [has(r, '02-111-0002'), noCite(r)]);
r = await ask('t02', 'How much is Portland cement?'); check('T02', r, [has(r, '145'), ['ไม่มีอักษรไทย', !/[฀-๿]/.test(r.text || '')]]);

// R (ต้องมีเอกสาร ready)
const R = [
  ['R01', 'ปูนซีเมนต์เก็บได้นานแค่ไหนครับ', [/3 เดือน/], 'BM-DS-CEM.pdf'],
  ['R02', 'สีทาภายนอกรับประกันกี่ปี', [/8 ปี/], 'BM-DS-PNT.pdf'],
  ['R03', 'กระเบื้อง TIL-001 ปูพื้นนอกบ้านได้ไหม', [/ได้/, /0\.5%|R10/], 'BM-DS-TIL.pdf'],
  ['R04', 'ซื้อปูนไปแล้วเปิดถุง ขอคืนได้ไหม', [/คืนไม่ได้|ไม่ได้/], 'BM-POLICY.pdf'],
  ['R05', 'ทาบเหล็ก DB12 ต้องยาวเท่าไร', [/48/], 'BM-DS-STL.pdf'],
  ['R06', 'สาย THW 2.5 ใช้กับเบรกเกอร์กี่แอมป์ แล้วเบรกเกอร์ 16A ราคาเท่าไร', [/16/, /145/], 'BM-DS-ELC-PIP.pdf'],
  ['R08', 'ปูกระเบื้อง 60x60 ด้วยปูนกาว ต้องใช้เกรียงฟันกี่มิล และใช้ปูนกาวกี่กิโลต่อตารางเมตร', [/10/, /5.5/], 'BM-DS-CEM.pdf'], // ตารางหัว 2 ชั้น (D)
];
const promo = (await pool.query(`SELECT 1 FROM docs WHERE filename = 'BM-PROMO-NOV.pdf' AND status = 'ready'`)).rowCount;
if (promo) R.push(['R07', 'เดือนพฤศจิกายนมีโปรอะไร', [/ลวดผูกเหล็ก/], 'BM-PROMO-NOV.pdf']);
if (!docCount) {
  skip += R.length;
  console.log(`skip R01–R0${R.length}: ยังไม่มีเอกสาร status=ready ใน DB (รอ rag-worker ของ D)`);
} else {
  for (const [name, q, res, file] of R) {
    r = await ask(name.toLowerCase(), q);
    check(name, r, [...res.map((x) => re(r, x)), citeFile(r, file), noTag(r)]);
  }
  if (!promo) console.log('skip R07: ยังไม่ได้อัปโหลด BM-PROMO-NOV.pdf');
}

// Q01: 8 คำถามพร้อมกัน
{
  const t0 = Date.now();
  const many = await Promise.all(Array.from({ length: 8 }, (_, i) => ask(`q01-${i}`, 'ปูนซีเมนต์ถุงละเท่าไร')));
  const okAll = many.every((x) => x.type === 'done' && (x.text || '').includes('145'));
  check('Q01 (8 พร้อมกัน)', { text: `${many.filter((x) => (x.text || '').includes('145')).length}/8 ได้ 145`, ms: Date.now() - t0 }, [['ครบ 8 ไม่มี error', okAll]]);
}

// บันทึก chat_messages
if (mode === 'rpc') {
  const sid = sessions.get('c13');
  const m = await pool.query('SELECT role, content FROM chat_messages WHERE session_id = $1 ORDER BY id', [sid]);
  check('chat_messages', { text: `${m.rowCount} แถว`, ms: 0 }, [['user+assistant 4 แถว', m.rowCount === 4 && m.rows[0].role === 'user' && m.rows[1].role === 'assistant'], ['ไม่มี tag ใน DB', !m.rows.some((x) => /\[CALC\]/.test(x.content))]]);
}

// retry → DLQ (เฉพาะ --dlq · rpc)
if (args.has('--dlq') && mode === 'rpc') {
  const before = (await ch.checkQueue(Q.CHAT_DLQ)).messageCount;
  r = await ask('dlq', '__bm_test_fail__', 60000);
  await new Promise((s) => setTimeout(s, 500));
  const after = (await ch.checkQueue(Q.CHAT_DLQ)).messageCount;
  check('DLQ', r, [['reply type error', r.type === 'error'], [`chat.dlq +1 (${before}→${after})`, after === before + 1]]);
  // เก็บกวาด: ดึงข้อความทดสอบออกจาก DLQ
  const keep = [];
  for (let i = 0; i < after; i++) {
    const m = await ch.get(Q.CHAT_DLQ, { noAck: false });
    if (!m) break;
    if (m.content.toString().includes('__bm_test_fail__')) ch.ack(m);
    else keep.push(m);
  }
  for (const m of keep) ch.nack(m, false, true);
}

console.log(`\n${pass} passed, ${fail} failed, ${skip} skipped (mode=${mode})`);
await pool.end();
if (conn) await conn.close().catch(() => {});
process.exit(fail ? 1 : 0);
