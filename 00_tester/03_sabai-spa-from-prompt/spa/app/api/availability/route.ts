import { availability, normalizeParams } from "@/lib/server/booking";
import { handle, json } from "@/lib/server/http";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

/** FR-01: GET /api/availability?service=thai-massage&date=2027-01-16&people=1&therapistId=1 */
export async function GET(req: Request) {
  return handle(async () => {
    const sp = Object.fromEntries(new URL(req.url).searchParams.entries());
    return json({ ok: true, ...(await availability(normalizeParams(sp))) });
  });
}
