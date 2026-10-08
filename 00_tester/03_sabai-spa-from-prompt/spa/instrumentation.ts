// Runs once when the Next.js server starts (never during `next build`):
// create tables + seed if empty, retrying while Postgres is still starting.
export async function register() {
  if (process.env.NEXT_RUNTIME !== "nodejs" || !process.env.DATABASE_URL) return;
  const { ensureDb } = await import("./lib/server/db");
  for (let attempt = 1; attempt <= 30; attempt++) {
    try {
      await ensureDb();
      console.log("[startup] database ready");
      return;
    } catch (e) {
      console.warn(`[startup] database not ready (attempt ${attempt}): ${(e as Error).message}`);
      await new Promise((r) => setTimeout(r, 2000));
    }
  }
}
