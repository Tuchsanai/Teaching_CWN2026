// GET /api/chat/history → { messages: [{id, role, content, cites, createdAt}] } ของ session ปัจจุบัน (ล่าสุด 100 ข้อความ) — C1
import { query } from '@/lib/db';
import { peekSessionId } from '@/lib/session';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function GET() {
  const sid = peekSessionId();
  if (!sid) return Response.json({ messages: [] });
  const r = await query<{ id: number; role: string; content: string; cites: unknown; created_at: string }>(
    `SELECT * FROM (
       SELECT id, role, content, cites, created_at FROM chat_messages
        WHERE session_id = $1 ORDER BY id DESC LIMIT 100
     ) t ORDER BY id ASC`,
    [sid],
  );
  return Response.json(
    {
      messages: r.rows.map((m) => ({
        id: m.id,
        role: m.role,
        content: m.content,
        cites: Array.isArray(m.cites) ? m.cites : [],
        createdAt: m.created_at,
      })),
    },
    { headers: { 'Cache-Control': 'no-store' } },
  );
}
