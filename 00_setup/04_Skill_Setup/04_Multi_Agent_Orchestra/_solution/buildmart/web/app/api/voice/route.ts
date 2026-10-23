// POST /api/voice (multipart: `audio` = webm/ogg/wav/mp3 · `lang` = th|en ไม่บังคับ) → {text, language, durationMs, engine}
// ส่งงานเข้าคิว stt.request {audioB64, mime, lang} (reply_to/correlation_id แบบเดียวกับ tts) รอ reply type 'stt' ≤ 60 วิ (v3 · CONTRACT_V3 §4–§5)
// ข้อความที่ได้ → widget ส่งต่อเข้า /api/chat เหมือนพิมพ์เอง
import { rpc } from '@/lib/amqp';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const MAX_BYTES = 15 * 1024 * 1024;

export async function POST(req: Request) {
  let file: File | null = null;
  let lang = '';
  try {
    const fd = await req.formData();
    const f = fd.get('audio') ?? fd.get('file');
    if (f && typeof f !== 'string') file = f as File;
    lang = String(fd.get('lang') || '');
  } catch {
    return Response.json({ error: 'ต้องส่ง multipart/form-data ที่มีไฟล์ audio' }, { status: 400 });
  }
  if (!file || !file.size) return Response.json({ error: 'ไม่มีไฟล์เสียง (field audio)' }, { status: 400 });
  if (file.size > MAX_BYTES) return Response.json({ error: 'ไฟล์เสียงใหญ่เกิน 15 MB' }, { status: 413 });

  const buf = Buffer.from(await file.arrayBuffer());
  const mime = file.type || 'audio/webm';
  try {
    const r: any = await rpc(
      'stt.request',
      { audioB64: buf.toString('base64'), mime, lang: lang === 'th' || lang === 'en' ? lang : undefined },
      { timeoutMs: 60_000, isFinal: (m: any) => m?.type === 'stt' || m?.type === 'error' },
    ).result;
    if (r?.error) return Response.json({ error: r.error }, { status: 502 });
    return Response.json({
      text: String(r?.text || ''),
      language: r?.language || null,
      durationMs: r?.durationMs ?? null,
      engine: r?.engine,
      tookMs: r?.tookMs,
    });
  } catch (e: any) {
    const timeout = e?.message === 'timeout';
    return Response.json({ error: timeout ? 'timeout' : 'queue_error' }, { status: timeout ? 504 : 502 });
  }
}
