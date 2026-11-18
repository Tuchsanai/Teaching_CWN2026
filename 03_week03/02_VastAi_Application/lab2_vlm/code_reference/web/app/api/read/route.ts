// Server-side only: the AI server URL and key come from receipt.env and never reach the browser.
import { NextResponse } from "next/server";
import { loadImage } from "@/lib/server-image";
import { PROMPT } from "@/lib/prompt";
import { parseReply, type ModelKey } from "@/lib/receipt";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(req: Request) {
  try {
    const form = await req.formData();
    const model = (form.get("model") === "base" ? "base" : "ft") as ModelKey;
    const modelName = model === "base" ? process.env.RECEIPT_MODEL_BASE : process.env.RECEIPT_MODEL_FT;
    const base = process.env.RECEIPT_BASE_URL, key = process.env.RECEIPT_API_KEY;
    if (!base || !key || !modelName) return NextResponse.json({ error: "ยังไม่ได้ตั้งค่า AI server (receipt.env)" }, { status: 500 });

    const { jpeg } = await loadImage(form);
    const body = {
      model: modelName, temperature: 0, max_tokens: 2048,
      messages: [{ role: "user", content: [
        { type: "image_url", image_url: { url: "data:image/jpeg;base64," + jpeg.toString("base64") } },
        { type: "text", text: PROMPT },
      ] }],
    };
    const t0 = Date.now();
    const r = await fetch(base.replace(/\/$/, "") + "/chat/completions", {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${key}` },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(180_000),
    });
    const seconds = (Date.now() - t0) / 1000;
    if (!r.ok) return NextResponse.json({ error: `AI server ตอบกลับ ${r.status}` }, { status: 502 });
    const out = await r.json();
    const raw: string = out?.choices?.[0]?.message?.content ?? "";
    return NextResponse.json({ model, raw, parsed: parseReply(raw), seconds });
  } catch (e: any) {
    const msg = e?.name === "TimeoutError" ? "AI server ไม่ตอบภายใน 180 วินาที" : (e?.message ?? "เกิดข้อผิดพลาด");
    return NextResponse.json({ error: msg }, { status: 500 });
  }
}
