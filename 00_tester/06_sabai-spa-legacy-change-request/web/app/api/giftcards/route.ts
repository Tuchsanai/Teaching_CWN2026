import { getLang, handle, json, readJson } from "@/lib/server/http.ts";
import { buyGiftCard } from "@/lib/server/store.ts";
import { getSession } from "@/lib/session.ts";

export const dynamic = "force-dynamic";

/** POST /api/giftcards — ซื้อ Gift Card (FR-19, BR-15) ส่ง LINE/email แบบจำลอง */
export async function POST(req: Request) {
  return handle(async () => {
    const body = await readJson(req);
    return json(await buyGiftCard(body, await getSession(), await getLang(body.lang)), 201);
  });
}
