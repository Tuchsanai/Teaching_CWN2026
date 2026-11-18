// GET /api/voice/status → {enabled} — มี consumer ที่คิว stt.request ไหม (stt-worker เปิดอยู่) · v3
import { checkQueue } from '@/lib/amqp';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function GET() {
  let enabled = false;
  try {
    const q = await checkQueue('stt.request');
    enabled = !!q && q.consumerCount > 0;
  } catch {}
  return Response.json({ enabled }, { headers: { 'Cache-Control': 'no-store' } });
}
