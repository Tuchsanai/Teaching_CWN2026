import { pool, ensureDb } from "@/lib/server/db";
import { ALL_TABLES } from "@/lib/server/schema";
import { seedAll } from "@/lib/server/seed";
import { testResetAllowed } from "@/lib/server/env";
import { body, json } from "@/lib/server/http";
import { bookableRange } from "@/lib/time";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

/** NFR-13 / NFR-14: wipe everything back to the seed data, optionally locking "now". */
export async function POST(req: Request) {
  if (!testResetAllowed()) return json({ ok: false, error: "NOT_FOUND" }, 404);
  const b = await body<{ now?: string }>(req);
  let fixed: Date | null = null;
  if (b.now !== undefined && b.now !== null && b.now !== "") {
    fixed = new Date(String(b.now));
    if (Number.isNaN(fixed.getTime())) {
      return json({ ok: false, error: "BAD_NOW", message: "now must be an ISO date-time, e.g. 2027-01-15T10:00:00+07:00" }, 400);
    }
  }
  await ensureDb();
  const c = await pool().connect();
  try {
    await c.query("BEGIN");
    await c.query("SELECT pg_advisory_xact_lock(727002)");
    await c.query(`TRUNCATE ${ALL_TABLES.join(", ")} RESTART IDENTITY CASCADE`);
    if (fixed) await c.query("INSERT INTO settings (key, value) VALUES ('fixed_now', $1)", [fixed.toISOString()]);
    const now = fixed ?? new Date();
    await seedAll(c, now);
    await c.query("COMMIT");
    const r = bookableRange(now);
    return json({ ok: true, now: now.toISOString(), locked: !!fixed, today: r.today, bookable: { from: r.min, to: r.max } });
  } catch (e) {
    await c.query("ROLLBACK").catch(() => undefined);
    console.error("[reset]", e);
    return json({ ok: false, error: "SERVER" }, 500);
  } finally {
    c.release();
  }
}

export async function GET() {
  if (!testResetAllowed()) return json({ ok: false, error: "NOT_FOUND" }, 404);
  return json({ ok: false, error: "METHOD", message: "Use POST" }, 405);
}
