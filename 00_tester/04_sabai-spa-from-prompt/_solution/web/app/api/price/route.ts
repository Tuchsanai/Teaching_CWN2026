import { clock } from "@/lib/clock.ts";
import { getPool } from "@/lib/db.ts";
import { buildQuote, parseBookingInput, quoteJson } from "@/lib/server/booking.ts";
import { getLang, handle, json, readJson } from "@/lib/server/http.ts";
import { getSession } from "@/lib/session.ts";

export const dynamic = "force-dynamic";

/** POST /api/price — ใบสรุปราคาก่อนจ่าย (คิดที่เซิร์ฟเวอร์ ไม่บันทึก) */
export async function POST(req: Request) {
  return handle(async () => {
    const body = await readJson(req);
    const lang = await getLang(body.lang);
    const input = parseBookingInput(body);
    const { today } = await clock();
    const q = await buildQuote(getPool(), input, await getSession(), today, lang);
    return json(quoteJson(q, lang));
  });
}
