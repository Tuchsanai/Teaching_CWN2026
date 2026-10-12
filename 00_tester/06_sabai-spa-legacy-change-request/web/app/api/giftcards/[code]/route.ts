import { getLang, handle, json } from "@/lib/server/http.ts";
import { giftCardInfo } from "@/lib/server/store.ts";

export const dynamic = "force-dynamic";

/** GET /api/giftcards/:code — ยอดคงเหลือ วันหมดอายุ สถานะ (FR-20, BR-16) */
export async function GET(req: Request, ctx: { params: Promise<{ code: string }> }) {
  return handle(async () => {
    const { code } = await ctx.params;
    const lang = await getLang(new URL(req.url).searchParams.get("lang"));
    return json(await giftCardInfo(decodeURIComponent(code), lang));
  });
}
