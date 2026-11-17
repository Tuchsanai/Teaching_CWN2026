// ตรวจว่าเว็บต่อ AI server ได้ไหม (ไม่ส่ง URL หรือ key กลับไปที่เบราว์เซอร์)
import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function GET() {
  const base = (process.env.YOLO_BASE_URL || "").replace(/\/$/, "");
  try {
    const r = await fetch(`${base}/health`, { signal: AbortSignal.timeout(5000), cache: "no-store" });
    const j = await r.json();
    return NextResponse.json({ ok: r.ok, model: j.model ?? process.env.YOLO_MODEL });
  } catch {
    return NextResponse.json({ ok: false, model: process.env.YOLO_MODEL ?? null });
  }
}
