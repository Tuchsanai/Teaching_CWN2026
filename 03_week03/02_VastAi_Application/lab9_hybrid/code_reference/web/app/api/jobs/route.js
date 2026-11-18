import { submitJob } from "@/lib/gateway";
export const dynamic = "force-dynamic";

export async function POST(req) {
  const { prompt, priority } = await req.json().catch(() => ({}));
  const text = String(prompt || "").trim();
  if (!text) return Response.json({ error: "กรุณาพิมพ์คำบรรยายภาพ" }, { status: 400 });
  try {
    const r = await submitJob(text.slice(0, 500), priority === "express" ? "express" : "normal");
    return Response.json(r, { status: r.ok ? 202 : r.status });
  } catch (e) {
    return Response.json({ error: "ติดต่อ gateway ไม่ได้: " + e.message }, { status: 502 });
  }
}
