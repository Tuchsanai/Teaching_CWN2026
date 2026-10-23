// shared/topology.js — ชื่อคิว/exchange ของ RabbitMQ (CONTRACT ข้อ RabbitMQ) · ใช้ assert ให้เหมือนกันทุก service
// ถ้าพารามิเตอร์ไม่ตรงกันระหว่าง service RabbitMQ จะตอบ PRECONDITION_FAILED — ห้ามแก้ที่อื่น ให้แก้ที่ไฟล์นี้ไฟล์เดียว

export const Q = {
  CHAT_REQUEST: 'chat.request',
  CHAT_DLQ: 'chat.dlq',
  RAG_INGEST: 'rag.ingest',
  TTS_REQUEST: 'tts.request',
  STT_REQUEST: 'stt.request', // v3: เสียงพูด → ข้อความ (stt-worker)
  NOTIFY_ORDERS: 'notify.orders',
};
export const EX = {
  CHAT_REPLY: 'chat.reply',
  ORDER_EVENTS: 'order.events',
};

export const QUEUES = [
  {
    name: Q.CHAT_REQUEST,
    options: { durable: true, arguments: { 'x-dead-letter-exchange': '', 'x-dead-letter-routing-key': Q.CHAT_DLQ } },
  },
  { name: Q.CHAT_DLQ, options: { durable: true } },
  { name: Q.RAG_INGEST, options: { durable: true } },
  { name: Q.TTS_REQUEST, options: { durable: true } },
  { name: Q.STT_REQUEST, options: { durable: true } },
  { name: Q.NOTIFY_ORDERS, options: { durable: true } },
];
export const EXCHANGES = [
  { name: EX.CHAT_REPLY, type: 'direct', options: { durable: false } },
  { name: EX.ORDER_EVENTS, type: 'fanout', options: { durable: true } },
];
export const BINDINGS = [{ queue: Q.NOTIFY_ORDERS, exchange: EX.ORDER_EVENTS, routingKey: '' }];

/** assert ทุกคิว/exchange/binding บน channel ของ amqplib */
export async function assertTopology(ch) {
  for (const e of EXCHANGES) await ch.assertExchange(e.name, e.type, e.options);
  for (const q of QUEUES) await ch.assertQueue(q.name, q.options);
  for (const b of BINDINGS) await ch.bindQueue(b.queue, b.exchange, b.routingKey);
}
