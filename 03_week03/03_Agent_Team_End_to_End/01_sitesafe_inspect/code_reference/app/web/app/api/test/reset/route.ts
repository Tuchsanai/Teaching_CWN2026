// 14 · POST /api/test/reset — no session; header X-Test-Key (DESIGN §7.2)
//      Enabled only when ENABLE_TEST_RESET=1, otherwise 404.
import { createHash, timingSafeEqual } from 'node:crypto';
import type { NextRequest } from 'next/server';
import { canAccess, deny } from '@/lib/access';
import { nowIso, parseInstant, setNow } from '@/lib/clock';
import { apiError, isRecord, json, readJson, serverError } from '@/lib/http';
import { resetAndSeed } from '@/db/seed';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

function keyMatches(given: string | null, expected: string | undefined): boolean {
  if (!given || !expected) return false;
  const a = createHash('sha256').update(given).digest();
  const b = createHash('sha256').update(expected).digest();
  return timingSafeEqual(a, b);
}

export async function POST(req: NextRequest) {
  if (process.env.ENABLE_TEST_RESET !== '1') return deny(404);
  const d = canAccess(null, 'test.reset');
  if (!d.ok) return deny(d.status);
  if (!keyMatches(req.headers.get('x-test-key'), process.env.TEST_RESET_KEY)) {
    return apiError(401, 'UNAUTHORIZED', 'X-Test-Key ไม่ถูกต้อง');
  }

  const body = await readJson(req);
  if (!isRecord(body)) return apiError(400, 'BAD_REQUEST', 'รูปแบบคำขอไม่ถูกต้อง');
  let instant: Date | null = null;
  if (body.now !== undefined && body.now !== null) {
    instant = parseInstant(body.now);
    if (!instant) return apiError(400, 'BAD_REQUEST', 'now ต้องเป็นเวลา ISO 8601 พร้อม offset เช่น 2026-11-18T17:59:00+07:00');
  }

  try {
    const counts = await resetAndSeed(instant ?? new Date());
    setNow(instant); // null → real time
    return json({ reset: true, ...counts, now: nowIso() });
  } catch (e) {
    return serverError('test/reset POST', e);
  }
}
