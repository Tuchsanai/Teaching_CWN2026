// lib/amqp.ts — การเชื่อม RabbitMQ ของ web (singleton บน globalThis + เชื่อมใหม่อัตโนมัติ)
//
// ใช้งาน:
//   import { rpc, sendToQueue, publish, checkQueue, instanceId } from '@/lib/amqp';
//   const { result } = rpc('chat.request', { sessionId, messageId, text }, {
//     correlationId: messageId, timeoutMs: 240_000,
//     onMessage: (m) => { /* status / delta / done / error → ส่งต่อ SSE */ },
//   });
//   const last = await result;                  // resolve ด้วยข้อความสุดท้าย (type done|error|tts)
//   await publish('order.events', '', { type: 'order.created', orderNo, items, branch });
//   await sendToQueue('rag.ingest', { docId });
//   const q = await checkQueue('tts.request');  // { messageCount, consumerCount } | null
//
// คิวตอบกลับ: exclusive `chat.reply.<instanceId>` ผูกกับ exchange `chat.reply` (direct) routing key = instanceId
// ข้อความขาออกของ rpc มี reply_to = instanceId, correlation_id = message_id = correlationId, persistent
import amqp, { type Channel, type ChannelModel, type ConsumeMessage, type Options } from 'amqplib';
import { randomUUID } from 'node:crypto';
import { assertTopology, EX, Q } from '@/shared/topology.js';

export { Q, EX };

type Handler = (body: any, msg: ConsumeMessage) => void;
type State = {
  instanceId: string;
  conn?: ChannelModel;
  ch?: Channel;
  connecting?: Promise<Channel>;
  handlers: Map<string, Handler>;
};

const g = globalThis as unknown as { __bmAmqp?: State };
const S: State = g.__bmAmqp ?? (g.__bmAmqp = { instanceId: `web-${randomUUID().slice(0, 8)}`, handlers: new Map() });

export const instanceId = S.instanceId;
export const replyQueue = `chat.reply.${S.instanceId}`;

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

function onReplyMessage(msg: ConsumeMessage | null) {
  if (!msg) return;
  const cid = msg.properties.correlationId;
  let body: any;
  try {
    body = JSON.parse(msg.content.toString('utf8'));
  } catch {
    body = { raw: msg.content.toString('utf8') };
  }
  const h = (cid && S.handlers.get(cid)) || (body?.messageId && S.handlers.get(body.messageId));
  if (!h) return;
  try {
    h(body, msg);
  } catch (e) {
    console.error('[amqp] reply handler error', e);
  }
}

async function connectOnce(): Promise<Channel> {
  const url = process.env.AMQP_URL || 'amqp://guest:guest@localhost:5672';
  const conn = await amqp.connect(url, { clientProperties: { connection_name: S.instanceId } });
  const ch = await conn.createChannel();
  await assertTopology(ch);
  await ch.assertQueue(replyQueue, { exclusive: true, autoDelete: true, durable: false });
  await ch.bindQueue(replyQueue, EX.CHAT_REPLY, S.instanceId);
  await ch.consume(replyQueue, onReplyMessage, { noAck: true });
  const reset = () => {
    if (S.conn !== conn) return;
    S.conn = undefined;
    S.ch = undefined;
    console.warn('[amqp] connection lost — จะเชื่อมใหม่เมื่อมีการใช้งานครั้งถัดไป');
    conn.close().catch(() => {});
  };
  conn.on('close', reset);
  conn.on('error', (e: Error) => console.error('[amqp] connection error', e.message));
  ch.on('close', reset);
  ch.on('error', (e: Error) => console.error('[amqp] channel error', e.message));
  S.conn = conn;
  S.ch = ch;
  console.log(`[amqp] ready instance=${S.instanceId} replyQueue=${replyQueue}`);
  return ch;
}

/** channel หลัก (สร้าง/เชื่อมใหม่ให้อัตโนมัติ · ลองซ้ำราว 45 วิ ก่อน throw) */
export async function getChannel(): Promise<Channel> {
  if (S.ch) return S.ch;
  if (!S.connecting) {
    S.connecting = (async () => {
      let delay = 500;
      for (let i = 0; ; i++) {
        try {
          return await connectOnce();
        } catch (e: any) {
          if (i >= 12) throw e;
          console.warn(`[amqp] connect failed (${e?.message}) retry in ${delay}ms`);
          await sleep(delay);
          delay = Math.min(delay * 2, 5000);
        }
      }
    })().finally(() => {
      S.connecting = undefined;
    });
  }
  return S.connecting;
}

const json = (body: unknown) => Buffer.from(JSON.stringify(body));

/** ส่งเข้าคิวตรง (persistent, JSON) */
export async function sendToQueue(queue: string, body: unknown, opts: Options.Publish = {}) {
  const ch = await getChannel();
  return ch.sendToQueue(queue, json(body), { persistent: true, contentType: 'application/json', ...opts });
}

/** publish ไป exchange (เช่น 'order.events' fanout → routingKey '') */
export async function publish(exchange: string, routingKey: string, body: unknown, opts: Options.Publish = {}) {
  const ch = await getChannel();
  return ch.publish(exchange, routingKey, json(body), { persistent: true, contentType: 'application/json', ...opts });
}

/** ผูก handler กับ correlationId (คืนฟังก์ชันยกเลิก) — ใช้เองได้ถ้าไม่ใช้ rpc() */
export function onReply(correlationId: string, handler: Handler): () => void {
  S.handlers.set(correlationId, handler);
  return () => {
    if (S.handlers.get(correlationId) === handler) S.handlers.delete(correlationId);
  };
}

export type RpcOptions<T> = {
  correlationId?: string;
  timeoutMs?: number;
  /** ถูกเรียกทุกข้อความตอบกลับ (status/delta/done/error/tts) */
  onMessage?: (m: T) => void;
  /** ข้อความไหนคือข้อความสุดท้าย (ค่าเริ่มต้น: type ∈ done|error|tts) */
  isFinal?: (m: T) => boolean;
  headers?: Record<string, unknown>;
};

/**
 * RPC แบบ streaming ผ่านคิว: ส่ง body เข้า queue แล้วรับข้อความตอบกลับหลายครั้งจนถึงข้อความสุดท้าย
 * คืน { correlationId, result, cancel } — result reject ด้วย Error('timeout') เมื่อเกิน timeoutMs (ค่าเริ่มต้น 240 วิ)
 */
export function rpc<T = any>(queue: string, body: unknown, opts: RpcOptions<T> = {}) {
  const correlationId = opts.correlationId || randomUUID();
  const isFinal = opts.isFinal || ((m: any) => ['done', 'error', 'tts'].includes(m?.type));
  let off = () => {};
  let timer: ReturnType<typeof setTimeout> | undefined;
  let rejectFn: (e: Error) => void = () => {};
  const cleanup = () => {
    if (timer) clearTimeout(timer);
    off();
  };
  const result = new Promise<T>((resolve, reject) => {
    rejectFn = reject;
    off = onReply(correlationId, (m: T) => {
      opts.onMessage?.(m);
      if (isFinal(m)) {
        cleanup();
        resolve(m);
      }
    });
    timer = setTimeout(() => {
      cleanup();
      reject(new Error('timeout'));
    }, opts.timeoutMs ?? 240_000);
    sendToQueue(queue, body, {
      replyTo: S.instanceId,
      correlationId,
      messageId: correlationId,
      headers: opts.headers,
    }).catch((e) => {
      cleanup();
      reject(e);
    });
  });
  return {
    correlationId,
    result,
    cancel: () => {
      cleanup();
      rejectFn(new Error('cancelled'));
    },
  };
}

/** ตรวจคิวด้วย channel ชั่วคราว (checkQueue กับคิวที่ไม่มีจะปิด channel — จึงไม่ใช้ channel หลัก) */
export async function checkQueue(name: string): Promise<{ messageCount: number; consumerCount: number } | null> {
  await getChannel();
  const conn = S.conn;
  if (!conn) return null;
  let ch: Channel | undefined;
  try {
    ch = await conn.createChannel();
    ch.on('error', () => {});
    const r = await ch.checkQueue(name);
    return { messageCount: r.messageCount, consumerCount: r.consumerCount };
  } catch {
    return null;
  } finally {
    ch?.close().catch(() => {});
  }
}
