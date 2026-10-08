import { q } from "@/lib/server/db";
import { handle, json } from "@/lib/server/http";
import type { ServiceRow } from "@/lib/server/booking";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

export async function GET() {
  return handle(async () => json({ ok: true, services: await q<ServiceRow>("SELECT * FROM services ORDER BY sort") }));
}
