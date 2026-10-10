import { getLang, handle, json } from "@/lib/server/http.ts";
import { buyCourse } from "@/lib/server/store.ts";
import { getSession } from "@/lib/session.ts";

export const dynamic = "force-dynamic";

/** POST /api/courses — ซื้อคอร์สกระชับสัดส่วน 10 แถม 1 (FR-13, BR-14) */
export async function POST() {
  return handle(async () => json(await buyCourse(await getSession(), await getLang()), 201));
}
