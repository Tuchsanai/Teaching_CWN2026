// GET /api/tts/[id] → audio/wav จากตาราง tts_audio (รองรับ Range ให้ <audio> seek ได้) · C1
import { query } from '@/lib/db';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export async function GET(req: Request, { params }: { params: { id: string } }) {
  const id = String(params.id || '').replace(/\.wav$/i, '');
  if (!UUID.test(id)) return new Response('not found', { status: 404 });
  const r = await query<{ wav: Buffer | null }>('SELECT wav FROM tts_audio WHERE id = $1', [id]);
  const wav = r.rows[0]?.wav;
  if (!wav || !wav.length) return new Response('not found', { status: 404 });

  const total = wav.length;
  const base: Record<string, string> = {
    'Content-Type': 'audio/wav',
    'Accept-Ranges': 'bytes',
    'Cache-Control': 'public, max-age=86400, immutable',
    'Content-Disposition': `inline; filename="${id}.wav"`,
  };
  const m = /^bytes=(\d*)-(\d*)$/.exec(req.headers.get('range') || '');
  if (m && (m[1] || m[2])) {
    const start = m[1] ? Number(m[1]) : Math.max(0, total - Number(m[2]));
    const end = Math.min(m[1] && m[2] ? Number(m[2]) : total - 1, total - 1);
    if (start > end || start >= total) {
      return new Response(null, { status: 416, headers: { ...base, 'Content-Range': `bytes */${total}` } });
    }
    const part = wav.subarray(start, end + 1);
    return new Response(part as unknown as BodyInit, {
      status: 206,
      headers: { ...base, 'Content-Range': `bytes ${start}-${end}/${total}`, 'Content-Length': String(part.length) },
    });
  }
  return new Response(wav as unknown as BodyInit, { headers: { ...base, 'Content-Length': String(total) } });
}
