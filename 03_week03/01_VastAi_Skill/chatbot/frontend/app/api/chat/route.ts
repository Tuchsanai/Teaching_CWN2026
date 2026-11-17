import { getHistory, getServices, getShopInfo, saveMessage } from "@/lib/db";
import { buildSystemPrompt } from "@/lib/prompt";
import { callLLM, stripThink, type ChatMsg } from "@/lib/llm";
import { createBooking, displayText, parseBookingTag, type BookingResult } from "@/lib/booking";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

type Result = { reply: string; booking: BookingResult | null; booking_error: string | null };

async function handle(sessionId: string, message: string, onText?: (t: string) => void): Promise<Result> {
  const [services, info, history] = await Promise.all([getServices(), getShopInfo(), getHistory(sessionId)]);
  await saveMessage(sessionId, "user", message);

  const messages: ChatMsg[] = [
    { role: "system", content: buildSystemPrompt(services, info) },
    ...history,
    { role: "user", content: message },
  ];

  let lastSent = "";
  const raw = await callLLM(messages, (rawSoFar) => {
    const t = displayText(stripThink(rawSoFar));
    if (t !== lastSent) {
      lastSent = t;
      onText?.(t);
    }
  });

  const full = stripThink(raw).trim();
  await saveMessage(sessionId, "assistant", full);

  let booking: BookingResult | null = null;
  let booking_error: string | null = null;
  const tag = parseBookingTag(full);
  if (tag) {
    const r = await createBooking(tag, services);
    if (r.ok) booking = r.booking;
    else booking_error = r.error;
  }
  return { reply: displayText(full), booking, booking_error };
}

export async function POST(req: Request) {
  let body: { session_id?: string; message?: string; stream?: boolean };
  try {
    body = await req.json();
  } catch {
    return Response.json({ error: "invalid JSON" }, { status: 400 });
  }
  const message = (body.message || "").toString().trim().slice(0, 2000);
  const sessionId = (body.session_id || "anonymous").toString().slice(0, 100);
  if (!message) return Response.json({ error: "message is required" }, { status: 400 });

  // ---- แบบไม่ stream (เหมาะกับทดสอบด้วย curl): {"stream": false} ----
  if (body.stream === false) {
    try {
      return Response.json(await handle(sessionId, message));
    } catch (e) {
      console.error("[chat]", e);
      return Response.json(
        { error: "ขออภัยค่ะ ระบบ AI ไม่พร้อมใช้งานชั่วคราว", detail: (e as Error).message },
        { status: 502 }
      );
    }
  }

  // ---- แบบ stream (SSE) ----
  const enc = new TextEncoder();
  const stream = new ReadableStream({
    async start(controller) {
      const send = (obj: unknown) => controller.enqueue(enc.encode(`data: ${JSON.stringify(obj)}\n\n`));
      try {
        const r = await handle(sessionId, message, (text) => send({ type: "text", text }));
        if (r.booking) send({ type: "booking", booking: r.booking });
        if (r.booking_error) send({ type: "booking_error", message: r.booking_error });
        send({ type: "done", text: r.reply });
      } catch (e) {
        console.error("[chat]", e);
        send({ type: "error", message: "ขออภัยค่ะ ระบบ AI ไม่พร้อมใช้งานชั่วคราว", detail: (e as Error).message });
      } finally {
        controller.close();
      }
    },
  });
  return new Response(stream, {
    headers: {
      "Content-Type": "text/event-stream; charset=utf-8",
      "Cache-Control": "no-cache, no-transform",
      Connection: "keep-alive",
      "X-Accel-Buffering": "no",
    },
  });
}
