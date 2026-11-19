/**
 * W1 · GET /api/health — ทุกคน ไม่ต้องเข้าสู่ระบบ (DESIGN 9.3)
 * 200 เมื่อเว็บต่อฐานข้อมูลได้ · 503 เมื่อต่อไม่ได้ · สถานะฝั่ง AI รายงานแยก ไม่ทำให้เว็บเป็น 503
 * ไม่มีข้อมูลใบเสร็จ และไม่บอกโหมดฝึกทดสอบ
 */
import { LIMITS } from '../../../lib/rules';
import { queryOne } from '../_lib/db';
import { json } from '../_lib/http';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const VERSION = '1.0.0';

export async function GET(): Promise<Response> {
  const mode = process.env.AI_MODE === 'mock' ? 'mock' : 'gateway';
  try {
    const row = await queryOne<{ now: Date; value: string | null; updated_at: Date | null }>(
      `SELECT clock_timestamp() AS now, s.value, s.updated_at
         FROM (SELECT 1) one LEFT JOIN system_state s ON s.key = 'workers_alive'`,
    );
    const raw = row?.value != null ? Number(row.value) : null;
    const workersAlive = raw !== null && Number.isFinite(raw) ? raw : null;
    // ค่าเดียวกับที่ BR-12 ใช้: เก่ากว่า 30 วินาทีถือว่าไม่ทราบ
    const fresh =
      row?.updated_at != null &&
      new Date(row.now).getTime() - new Date(row.updated_at).getTime() <= LIMITS.WORKERS_STALE_MS;
    return json({
      status: 'ok',
      db: 'ok',
      ai: { mode, reachable: mode === 'mock' ? true : fresh && (workersAlive ?? 0) > 0, workersAlive },
      version: VERSION,
    });
  } catch {
    return json({ status: 'error', db: 'down', ai: { mode, reachable: false, workersAlive: null }, version: VERSION }, 503);
  }
}
