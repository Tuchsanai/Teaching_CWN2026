// workers/lib/amqp.js — เชื่อม RabbitMQ (ลองซ้ำจนสำเร็จ) + assert topology เดียวกับ web (shared/topology.js)
//
//   import { connectAmqp, replyTo, publishJson, Q, EX } from './lib/amqp.js';
//   const { conn, ch } = await connectAmqp({ prefetch: 4, onReconnect: setup });
//   ch.consume(Q.CHAT_REQUEST, async (msg) => { ...; replyTo(ch, msg, { messageId, type: 'done', text }); ch.ack(msg); });
//
// ถ้า connection หลุด: ถ้าให้ onReconnect มา จะเชื่อมใหม่แล้วเรียก onReconnect({conn, ch}) ให้ consume ใหม่
// ไม่ให้ onReconnect → process.exit(1) ให้ docker restart (restart: unless-stopped)
import amqp from 'amqplib';
import { assertTopology, EX, Q } from '../../shared/topology.js';

export { Q, EX, assertTopology };

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

export async function connectAmqp({ prefetch, name = process.argv[1]?.split(/[\\/]/).pop(), onReconnect, retries = 120 } = {}) {
  const url = process.env.AMQP_URL || 'amqp://guest:guest@localhost:5672';
  let delay = 500;
  for (let i = 0; ; i++) {
    try {
      const conn = await amqp.connect(url, { clientProperties: { connection_name: name } });
      const ch = await conn.createChannel();
      await assertTopology(ch);
      if (prefetch) await ch.prefetch(prefetch);
      let closing = false;
      const lost = async (why) => {
        if (closing) return;
        closing = true;
        console.error(`[amqp] connection lost (${why})`);
        conn.close().catch(() => {});
        if (!onReconnect) process.exit(1);
        const again = await connectAmqp({ prefetch, name, onReconnect, retries });
        await onReconnect(again);
      };
      conn.on('error', (e) => console.error('[amqp] error', e.message));
      conn.on('close', () => lost('close'));
      ch.on('close', () => lost('channel close'));
      ch.on('error', (e) => console.error('[amqp] channel error', e.message));
      console.log(`[amqp] connected (${name})`);
      return { conn, ch };
    } catch (e) {
      if (i >= retries) throw e;
      console.warn(`[amqp] connect failed (${e.message}) retry in ${delay}ms`);
      await sleep(delay);
      delay = Math.min(delay * 2, 5000);
    }
  }
}

export const toBuf = (body) => Buffer.from(JSON.stringify(body));

/** อ่าน body JSON ของ message (ผิดรูป → null) */
export function parseJson(msg) {
  try {
    return JSON.parse(msg.content.toString('utf8'));
  } catch {
    return null;
  }
}

/**
 * ตอบกลับ RPC: publish ไป exchange `chat.reply` (direct) routing key = msg.properties.replyTo
 * correlation_id = ของ request เดิม · ใช้ทั้ง chat (status/delta/done/error) และ tts
 */
export function replyTo(ch, msg, body) {
  const rk = msg.properties.replyTo;
  if (!rk) return false;
  return ch.publish(EX.CHAT_REPLY, rk, toBuf(body), {
    correlationId: msg.properties.correlationId || body?.messageId,
    contentType: 'application/json',
  });
}

/** publish JSON (exchange '' = ส่งเข้าคิวชื่อ routingKey) */
export function publishJson(ch, exchange, routingKey, body, opts = {}) {
  return ch.publish(exchange, routingKey, toBuf(body), { persistent: true, contentType: 'application/json', ...opts });
}
