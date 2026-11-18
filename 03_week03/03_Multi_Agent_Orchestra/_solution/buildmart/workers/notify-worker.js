// workers/notify-worker.js (B3) — ผู้ฟังของ exchange `order.events` (fanout) ผ่านคิว `notify.orders`
//
// รับ {type:'order.created', orderNo, items:[{sku,qty}], branch} (web publish หลังตัดสต็อกสำเร็จ) แล้วเขียนตาราง notifications:
//   ① kind 'order'     "คำสั่งซื้อใหม่ BM-… · N รายการ · ยอด ฿… · ส่งจากสาขา…"   ref = orderNo
//   ② kind 'low_stock' "สต็อกต่ำ: <ชื่อ> (SKU) สาขา… คงเหลือ n หน่วย (จุดสั่งซื้อซ้ำ m)"  ref = SKU:BRANCH
//      — เฉพาะสินค้าในคำสั่งซื้อนั้นที่สต็อกสาขานั้นเหลือ < reorder_point
// ack หลังเขียน DB สำเร็จ · ล้มครั้งแรก → requeue 1 ครั้ง · ล้มซ้ำ → ทิ้ง (log) · ข้อความซ้ำ (redelivery) ไม่สร้างแจ้งเตือนซ้ำ
import { waitForDb, pool, tx } from './lib/db.js';
import { connectAmqp, parseJson, Q } from './lib/amqp.js';
import { markReady, markNotReady } from './lib/ready.js';
import { formatBaht } from '../shared/pricing.js';

const BRANCH_NAME = { LKB: 'ลาดกระบัง', BNA: 'บางนา', RST: 'รังสิต' };

async function handleOrderCreated(evt) {
  const orderNo = String(evt.orderNo || '');
  if (!orderNo) throw new Error('missing orderNo');
  const items = Array.isArray(evt.items) ? evt.items.filter((i) => i && i.sku) : [];

  return tx(async (c) => {
    // กันซ้ำ: ล็อกตามเลขคำสั่งซื้อ แล้วเช็คว่ามีแจ้งเตือนของ order นี้แล้วหรือยัง
    await c.query('SELECT pg_advisory_xact_lock(hashtext($1))', [`notify:${orderNo}`]);
    const dup = await c.query(`SELECT 1 FROM notifications WHERE kind = 'order' AND ref = $1 LIMIT 1`, [orderNo]);
    if (dup.rowCount) return { duplicate: true, low: 0 };

    // ข้อมูลเสริมจากตาราง orders (ถ้ามี) — event อาจมาก่อน/ไม่มีแถว (เช่นทดสอบ) ก็ยังแจ้งเตือนได้
    const o = await c.query(`SELECT branch, (totals->>'total')::numeric AS total FROM orders WHERE order_no = $1`, [orderNo]);
    const branch = evt.branch || o.rows[0]?.branch || null;
    const parts = [`คำสั่งซื้อใหม่ ${orderNo}`];
    if (items.length) parts.push(`${items.length} รายการ`);
    if (o.rows[0]?.total != null) parts.push(`ยอด ฿${formatBaht(Number(o.rows[0].total))}`);
    if (branch) parts.push(`ส่งจากสาขา${BRANCH_NAME[branch] || branch}`);
    await c.query(`INSERT INTO notifications (kind, message, ref) VALUES ('order', $1, $2)`, [parts.join(' · '), orderNo]);

    // เช็คสต็อกต่ำของสินค้าในคำสั่งซื้อ ณ สาขาที่ตัดสต็อก
    let low = 0;
    if (branch && items.length) {
      const r = await c.query(
        `SELECT p.sku, p.name, p.unit, p.reorder_point, s.qty
           FROM products p JOIN stock s ON s.sku = p.sku AND s.branch = $2
          WHERE p.sku = ANY($1::text[]) AND s.qty < p.reorder_point
          ORDER BY p.sku`,
        [[...new Set(items.map((i) => String(i.sku)))], branch],
      );
      for (const p of r.rows) {
        const msg =
          `สต็อกต่ำ: ${p.name} (${p.sku}) สาขา${BRANCH_NAME[branch] || branch} (${branch}) ` +
          `คงเหลือ ${Number(p.qty).toLocaleString('en-US')} ${p.unit} (จุดสั่งซื้อซ้ำ ${Number(p.reorder_point).toLocaleString('en-US')})`;
        await c.query(`INSERT INTO notifications (kind, message, ref) VALUES ('low_stock', $1, $2)`, [msg, `${p.sku}:${branch}`]);
        low++;
      }
    }
    return { duplicate: false, low };
  });
}

async function setup({ ch }) {
  await ch.consume(Q.NOTIFY_ORDERS, async (msg) => {
    if (!msg) return;
    const evt = parseJson(msg);
    if (!evt || evt.type !== 'order.created') {
      console.warn('[notify-worker] ข้ามข้อความที่ไม่รู้จัก', msg.content.toString('utf8').slice(0, 200));
      ch.ack(msg);
      return;
    }
    try {
      const r = await handleOrderCreated(evt);
      console.log(`[notify-worker] ${evt.orderNo} → ${r.duplicate ? 'ซ้ำ (ข้าม)' : `order + low_stock ${r.low}`}`);
      ch.ack(msg);
    } catch (e) {
      const requeue = !msg.fields.redelivered;
      console.error(`[notify-worker] ${evt.orderNo} ล้มเหลว (${e.message}) → ${requeue ? 'requeue' : 'ทิ้ง'}`);
      ch.nack(msg, false, requeue);
    }
  });
  console.log(`[notify-worker] consuming ${Q.NOTIFY_ORDERS}`);
}

await waitForDb();
const first = await connectAmqp({ prefetch: 10, onReconnect: setup });
await setup(first);
markReady('notify-worker');

const stop = async () => {
  markNotReady();
  await pool.end().catch(() => {});
  process.exit(0);
};
process.on('SIGTERM', stop);
process.on('SIGINT', stop);
