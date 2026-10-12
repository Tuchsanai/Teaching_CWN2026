import { clock } from "@/lib/clock.ts";
import { getPool } from "@/lib/db.ts";
import { wallet } from "@/lib/server/customer.ts";
import { ApiError, getLang, handle, json } from "@/lib/server/http.ts";
import { getSession } from "@/lib/session.ts";

export const dynamic = "force-dynamic";

/** GET /api/wallet — คอร์ส "เหลือ X จาก 11" รอบเอว รูป (FR-15, FR-16, FR-18) */
export async function GET() {
  return handle(async () => {
    const s = await getSession();
    if (!s) throw new ApiError(401, "LOGIN_REQUIRED");
    const { today } = await clock();
    return json(await wallet(getPool(), s.uid, today, await getLang()));
  });
}
