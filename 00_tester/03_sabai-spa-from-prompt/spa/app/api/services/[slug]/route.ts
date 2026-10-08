import { getService } from "@/lib/server/booking";
import { fail, handle, json } from "@/lib/server/http";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

export async function GET(_req: Request, ctx: { params: Promise<{ slug: string }> }) {
  return handle(async () => {
    const { slug } = await ctx.params;
    const s = await getService(slug);
    return s ? json({ ok: true, service: s }) : fail("NOT_FOUND", 404);
  });
}
