import { chat, type ChatState } from "@/lib/bot/chat.ts";
import { ApiError, getLang, handle, json, readJson } from "@/lib/server/http.ts";
import { getSession } from "@/lib/session.ts";

export const dynamic = "force-dynamic";

/** POST /api/chat {message, state?} — ตอบด้วยกฎตายตัว ภาษาเดียวกับที่ถาม (FR-25, FR-26) */
export async function POST(req: Request) {
  return handle(async () => {
    const body = await readJson(req);
    const message = typeof body.message === "string" ? body.message : "";
    if (!message.trim()) throw new ApiError(422, "BAD_REQUEST", { field: "message" });
    const state = body.state && typeof body.state === "object" ? (body.state as ChatState) : null;
    return json(await chat(message.slice(0, 500), state, await getSession(), await getLang(body.lang)));
  });
}
