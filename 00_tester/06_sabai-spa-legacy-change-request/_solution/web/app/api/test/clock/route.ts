import { config } from "@/lib/config.ts";
import { handle, json, readJson } from "@/lib/server/http.ts";
import { setTestClock } from "@/lib/server/testmode.ts";

export const dynamic = "force-dynamic";

/** POST /api/test/clock {now} — เปลี่ยน "วันนี้" ของระบบโดยไม่ล้างข้อมูล (test seam · เงื่อนไขเดียวกับ /api/test/reset) */
export async function POST(req: Request) {
  if (!config.allowTestReset) return new Response("Not Found", { status: 404 });
  return handle(async () => {
    const body = await readJson(req);
    return json(await setTestClock(body.now));
  });
}
