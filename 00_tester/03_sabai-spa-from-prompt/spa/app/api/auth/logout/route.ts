import { endSession } from "@/lib/server/auth";
import { handle, json } from "@/lib/server/http";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

export async function POST() {
  return handle(async () => {
    await endSession();
    return json({ ok: true });
  });
}
