/**
 * W2 · POST /api/test/reset — ผู้ทดสอบที่มี token (DESIGN 9.4)
 * - ENABLE_TEST_RESET ไม่ใช่ "1" → 404 (เหมือนไม่มีเส้นนี้)
 * - header X-Test-Token ต้องตรง TEST_RESET_TOKEN → ไม่ตรง/ไม่ได้ตั้ง → 403
 * - เนื้อหา (ไม่ใส่ก็ได้): {"pendingNormal","urgentToday","urgentYesterday","workersAlive","overdue"}
 * งานจริงอยู่ในฟังก์ชัน SQL reset_test_data() ของ B02
 */
import { timingSafeEqual } from 'node:crypto';
import { queryOne } from '../../_lib/db';
import { ApiError, forbidden, handle, json, notFound, readJson } from '../../_lib/http';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

function tokenMatches(given: string | null, expected: string | undefined): boolean {
  if (!given || !expected) return false;
  const a = Buffer.from(given);
  const b = Buffer.from(expected);
  return a.length === b.length && timingSafeEqual(a, b);
}

export const POST = handle(async (request: Request) => {
  if (process.env.ENABLE_TEST_RESET !== '1') throw notFound();
  if (!tokenMatches(request.headers.get('x-test-token'), process.env.TEST_RESET_TOKEN)) throw forbidden();
  const options = await readJson(request, true);
  try {
    const row = await queryOne<{ result: unknown }>('SELECT reset_test_data($1::jsonb, $2::text) AS result', [
      JSON.stringify(options),
      process.env.ENABLE_TEST_RESET,
    ]);
    return json(row?.result ?? { ok: true });
  } catch (error) {
    const e = error as { code?: string; message?: string };
    if (e.code === '22023') throw new ApiError(400, 'bad_request', e.message ?? 'ตัวเลือกไม่ถูกต้อง');
    throw error;
  }
});
