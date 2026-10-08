import { findGift, giftProblem } from "@/lib/server/booking";
import { getNow } from "@/lib/server/clock";
import { handle, json, reqLang } from "@/lib/server/http";
import { bkkDate } from "@/lib/time";
import { errorText } from "@/lib/i18n";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

/** FR-17 / BR-18: check a gift card — valid until purchase date + 365 days */
export async function GET(_req: Request, ctx: { params: Promise<{ code: string }> }) {
  return handle(async () => {
    const code = decodeURIComponent((await ctx.params).code).trim().toUpperCase();
    const g = await findGift(code);
    const today = bkkDate(await getNow());
    const problem = giftProblem(g, today);
    const lang = await reqLang();
    if (!g) return json({ ok: false, error: "GIFT_NOT_FOUND", message: errorText(lang, "GIFT_NOT_FOUND") }, 404);
    return json({
      ok: true,
      giftCard: { code: g.code, amount: g.amount, balance: g.balance, design: g.design, purchasedOn: g.purchased_on, expiresOn: g.expires_on },
      usable: !problem,
      status: problem === "GIFT_EXPIRED" ? "expired" : problem === "GIFT_EMPTY" ? "empty" : "valid",
      ...(problem ? { error: problem, message: errorText(lang, problem) } : {}),
    });
  });
}
