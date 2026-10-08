import { q } from "@/lib/server/db";
import { handle, json } from "@/lib/server/http";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

export async function GET() {
  return handle(async () => json({ ok: true, rooms: await q("SELECT * FROM rooms ORDER BY sort") }));
}
