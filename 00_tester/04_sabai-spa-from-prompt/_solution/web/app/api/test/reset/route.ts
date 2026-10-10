import { flags } from "@/lib/flags.ts";
import { handle, json, readJson } from "@/lib/server/http.ts";
import { resetTestData } from "@/lib/server/testmode.ts";

export const dynamic = "force-dynamic";

/** POST /api/test/reset {now?} — ล้างทุกตารางกลับเป็น seed ใน transaction เดียว (NFR-14) + ล็อกวันนี้ (NFR-13) */
export async function POST(req: Request) {
  if (!flags.allowTestReset) return new Response("Not Found", { status: 404 });
  return handle(async () => {
    const body = await readJson(req);
    return json(await resetTestData(body.now));
  });
}
