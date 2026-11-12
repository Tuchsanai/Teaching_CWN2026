// GET /api/tts/status → {enabled} — มี consumer ที่คิว tts.request ไหม (เปิด profile tts หรือยัง) · C1
import { ttsEnabled } from '../ttsText';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function GET() {
  return Response.json({ enabled: await ttsEnabled() }, { headers: { 'Cache-Control': 'no-store' } });
}
