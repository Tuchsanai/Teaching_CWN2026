import { currentUser, memberSummary } from "@/lib/server/auth";
import { handle, json } from "@/lib/server/http";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

export async function GET() {
  return handle(async () => {
    const u = await currentUser();
    return json({ ok: true, user: u ? await memberSummary(u) : null });
  });
}
