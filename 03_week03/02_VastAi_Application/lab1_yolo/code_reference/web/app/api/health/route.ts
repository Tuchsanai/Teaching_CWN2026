import { AI_URL } from "@/lib/ai";
export const dynamic = "force-dynamic";

export async function GET() {
  if (!AI_URL) return Response.json({ ready: false, error: "ยังไม่ได้ตั้ง YOLO_BASE_URL" });
  const t0 = Date.now();
  try {
    const r = await fetch(`${AI_URL}/health`, { cache: "no-store", signal: AbortSignal.timeout(5000) });
    const j = await r.json();
    return Response.json({ ready: r.ok && j.ready === true, model: j.model, ms: Date.now() - t0 });
  } catch {
    return Response.json({ ready: false, error: "ติดต่อ AI server ไม่ได้" });
  }
}
