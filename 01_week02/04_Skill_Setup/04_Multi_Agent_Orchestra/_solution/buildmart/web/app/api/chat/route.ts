// POST /api/chat {text} → SSE (text/event-stream) — C1
// web ไม่เรียก LLM ตรง: ส่งงานเข้าคิว `chat.request` (persistent · reply_to = instanceId · correlation_id = messageId)
// แล้วส่งต่อข้อความจาก exchange `chat.reply` ให้เบราว์เซอร์ทีละ event:
//   queued {messageId} (ทันที) → status {status:'thinking'} → delta {text สะสม} → done {text, cites, cartCount, quoteNo, retrieved, products} | error {error}
// รอได้นาน 240 วิ — ถ้า chat-worker ดับ ข้อความจะค้างอยู่ในคิว (durable) จนกว่า worker กลับมา (เคส Q02)
import { randomUUID } from 'node:crypto';
import { rpc } from '@/lib/amqp';
import { query } from '@/lib/db';
import { getSessionId } from '@/lib/session';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const TIMEOUT_MS = 240_000;
const MAX_LEN = 2000;

type Reply = {
  messageId?: string;
  type: 'status' | 'delta' | 'done' | 'error';
  status?: string;
  text?: string;
  cites?: { filename: string; page: number; snippet?: string }[];
  cartCount?: number;
  quoteNo?: string;
  error?: string;
  retrieved?: { filename: string; page: number; score?: number }[];
  products?: string[];
  usage?: { completion_tokens: number; prompt_tokens: number; decode_ms?: number; decode_tok_s?: number; source?: string };
};

export async function POST(req: Request) {
  let text = '';
  try {
    const body = await req.json();
    text = String(body?.text ?? '').trim();
  } catch {
    /* body ไม่ใช่ JSON */
  }
  if (!text) return Response.json({ error: 'กรุณาพิมพ์คำถาม' }, { status: 400 });
  if (text.length > MAX_LEN) text = text.slice(0, MAX_LEN);

  const sessionId = getSessionId();
  const messageId = randomUUID();
  const lang = /[฀-๿]/.test(text) ? 'th' : 'en';
  query('INSERT INTO chat_sessions (id) VALUES ($1) ON CONFLICT DO NOTHING', [sessionId]).catch(() => {});

  const enc = new TextEncoder();
  let closed = false;
  let heartbeat: ReturnType<typeof setInterval> | undefined;
  let cancelRpc: (() => void) | undefined;

  const stream = new ReadableStream<Uint8Array>({
    start(controller) {
      const write = (chunk: string) => {
        if (closed) return;
        try {
          controller.enqueue(enc.encode(chunk));
        } catch {
          closed = true;
        }
      };
      const send = (event: string, data: unknown) => write(`event: ${event}\ndata: ${JSON.stringify(data)}\n\n`);
      const close = () => {
        if (heartbeat) clearInterval(heartbeat);
        if (closed) return;
        closed = true;
        try {
          controller.close();
        } catch {
          /* ปิดไปแล้ว */
        }
      };

      send('queued', { messageId });
      // comment ทุก 15 วิ กัน proxy/เบราว์เซอร์ตัดการเชื่อมต่อระหว่างรอคิวนาน ๆ
      heartbeat = setInterval(() => write(': ping\n\n'), 15_000);

      const call = rpc<Reply>(
        'chat.request',
        { sessionId, messageId, text, lang },
        {
          correlationId: messageId,
          timeoutMs: TIMEOUT_MS,
          onMessage: (m) => {
            switch (m?.type) {
              case 'status':
                send('status', { status: m.status || 'thinking' });
                break;
              case 'delta':
                send('delta', { text: m.text ?? '' });
                break;
              case 'done':
                send('done', {
                  text: m.text ?? '',
                  cites: Array.isArray(m.cites) ? m.cites : [],
                  cartCount: typeof m.cartCount === 'number' ? m.cartCount : undefined,
                  quoteNo: m.quoteNo || undefined,
                  // v3: เอกสาร top 4 ที่ใส่ในพรอมต์ (ประเมิน Hit@4/MRR) + SKU ที่ดึงจาก DB
                  retrieved: Array.isArray(m.retrieved) ? m.retrieved : [],
                  products: Array.isArray(m.products) ? m.products : [],
                  usage: m.usage || undefined, // token จริงจาก LLM (load test)
                });
                break;
              case 'error':
                send('error', { error: m.error || m.text || 'chat-worker error' });
                break;
            }
          },
        },
      );
      cancelRpc = call.cancel;
      call.result
        .then(() => close())
        .catch((e: Error) => {
          if (e?.message !== 'cancelled') {
            const timeout = e?.message === 'timeout';
            send('error', {
              error: timeout ? 'timeout' : 'queue_error',
              message: timeout ? 'รอคำตอบนานเกิน 240 วินาที' : 'ส่งข้อความเข้าคิวไม่สำเร็จ',
            });
          }
          close();
        });
    },
    cancel() {
      // ผู้ใช้ปิดหน้า/ยกเลิก — เลิกฟังคำตอบ (งานในคิวยังทำต่อและบันทึกประวัติตามปกติ)
      closed = true;
      if (heartbeat) clearInterval(heartbeat);
      cancelRpc?.();
    },
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream; charset=utf-8',
      'Cache-Control': 'no-cache, no-transform',
      Connection: 'keep-alive',
      'X-Accel-Buffering': 'no',
      'X-Message-Id': messageId,
    },
  });
}
