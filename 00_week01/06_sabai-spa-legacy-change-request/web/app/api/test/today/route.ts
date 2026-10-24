import { clock } from "@/lib/clock.ts";
import { config } from "@/lib/config.ts";
import { bangkokIso } from "@/lib/server/testmode.ts";
import { json } from "@/lib/server/http.ts";

export const dynamic = "force-dynamic";

/** GET /api/test/today — "ตอนนี้" ของระบบ (โหมดทดสอบ) */
export async function GET() {
  if (!config.allowTestReset) return new Response("Not Found", { status: 404 });
  const { now, today } = await clock();
  return json({ now: bangkokIso(now), today });
}
