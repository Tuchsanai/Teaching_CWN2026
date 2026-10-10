import { ensureDb, pool } from "@/lib/server/db";
import { json } from "@/lib/server/http";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

export async function GET() {
  try {
    await ensureDb();
    await pool().query("SELECT 1");
    return json({ ok: true, db: true });
  } catch {
    return json({ ok: false, db: false }, 503);
  }
}
