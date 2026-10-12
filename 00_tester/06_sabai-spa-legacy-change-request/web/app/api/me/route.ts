import { clock } from "@/lib/clock.ts";
import { getPool } from "@/lib/db.ts";
import { accountSummary } from "@/lib/server/customer.ts";
import { ApiError, getLang, handle, json } from "@/lib/server/http.ts";
import { getSession } from "@/lib/session.ts";

export const dynamic = "force-dynamic";

/** GET /api/me — ระดับ ข้อความ "อีก ฿X" แต้ม เดือนเกิด (FR-09, FR-11, FR-12) */
export async function GET() {
  return handle(async () => {
    const s = await getSession();
    if (!s) throw new ApiError(401, "LOGIN_REQUIRED");
    const { today } = await clock();
    const me = await accountSummary(getPool(), s.uid, today, await getLang());
    if (!me) throw new ApiError(401, "LOGIN_REQUIRED");
    return json(me);
  });
}
