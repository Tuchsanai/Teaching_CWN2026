// POST /api/tts {text, lang?} → {audioId, durationMs} — C1
// ส่งงานเข้าคิว `tts.request` (reply_to/correlation_id เหมือนแชท) แล้วรอ reply {type:'tts', audioId, durationMs} ≤ 60 วิ
// ข้อความเดิมที่เคยสร้างเสียงแล้ว (ตาราง tts_audio) ใช้ไฟล์เดิมทันที ไม่ต้องเข้าคิวซ้ำ
import { rpc } from '@/lib/amqp';
import { query } from '@/lib/db';
import { langOf, speakable, ttsEnabled } from './ttsText';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function POST(req: Request) {
  let raw = '';
  let lang = '';
  try {
    const b = await req.json();
    raw = String(b?.text ?? '');
    lang = String(b?.lang ?? '');
  } catch {
    /* ignore */
  }
  const text = speakable(raw);
  if (!text) return Response.json({ error: 'ไม่มีข้อความให้อ่าน' }, { status: 400 });
  if (lang !== 'th' && lang !== 'en') lang = langOf(text);

  try {
    const hit = await query<{ id: string; duration_ms: number }>(
      `SELECT id, duration_ms FROM tts_audio
        WHERE text = $1 AND lang = $2 AND wav IS NOT NULL AND duration_ms > 0
        ORDER BY created_at DESC LIMIT 1`,
      [text, lang],
    );
    if (hit.rows[0]) return Response.json({ audioId: hit.rows[0].id, durationMs: hit.rows[0].duration_ms, cached: true });
  } catch {
    /* ตารางยังไม่พร้อม — ไปสร้างใหม่ */
  }

  if (!(await ttsEnabled())) return Response.json({ error: 'tts_disabled' }, { status: 503 });

  try {
    const r: any = await rpc(
      'tts.request',
      { text, lang },
      { timeoutMs: 60_000, isFinal: (m: any) => m?.type === 'tts' || m?.type === 'error' },
    ).result;
    if (!r?.audioId || r.error) return Response.json({ error: r?.error || 'tts_failed' }, { status: 502 });
    return Response.json({ audioId: r.audioId, durationMs: r.durationMs ?? null });
  } catch (e: any) {
    const timeout = e?.message === 'timeout';
    return Response.json({ error: timeout ? 'timeout' : 'queue_error' }, { status: timeout ? 504 : 502 });
  }
}
