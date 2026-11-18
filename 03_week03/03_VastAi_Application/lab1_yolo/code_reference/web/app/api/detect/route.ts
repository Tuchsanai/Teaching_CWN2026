import { AI_KEY, AI_URL } from "@/lib/ai";
import { pool, ready } from "@/lib/db";
import { summarize, type DetectResult } from "@/lib/types";
export const dynamic = "force-dynamic";

export async function POST(req: Request) {
  const form = await req.formData();
  const file = form.get("file");
  if (!(file instanceof File) || file.size === 0) return Response.json({ error: "กรุณาเลือกรูปภาพ" }, { status: 400 });
  if (file.size > 10 * 1024 * 1024) return Response.json({ error: "รูปใหญ่เกิน 10 MB" }, { status: 400 });

  const bytes = Buffer.from(await file.arrayBuffer());
  const out = new FormData();
  out.append("file", new Blob([bytes], { type: file.type || "image/jpeg" }), file.name || "image.jpg");

  const t0 = performance.now();
  let res: Response;
  try {
    res = await fetch(`${AI_URL}/v1/detect`, {
      method: "POST", body: out, headers: { Authorization: `Bearer ${AI_KEY}` },
      cache: "no-store", signal: AbortSignal.timeout(60000),
    });
  } catch {
    return Response.json({ error: "ติดต่อ AI server ไม่ได้" }, { status: 502 });
  }
  const roundtrip_ms = Math.round((performance.now() - t0) * 10) / 10;
  if (!res.ok) {
    const msg = res.status === 401 ? "AI server ปฏิเสธ key" : res.status === 400 ? "AI server อ่านรูปนี้ไม่ได้" : `AI server ตอบ ${res.status}`;
    return Response.json({ error: msg }, { status: 502 });
  }
  const r = (await res.json()) as DetectResult;
  const s = summarize(r.detections);

  await ready();
  const { rows } = await pool.query(
    `INSERT INTO inspections (filename, mime, image, model, width, height, passed, persons, hardhat, no_hardhat, no_vest, inference_ms, roundtrip_ms, detections)
     VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14) RETURNING id, created_at`,
    [file.name || "image.jpg", file.type || "image/jpeg", bytes, r.model, r.width, r.height, s.passed, s.persons, s.hardhat, s.noHardhat, s.noVest, r.inference_ms, roundtrip_ms, JSON.stringify(r.detections)],
  );
  return Response.json({ id: rows[0].id, created_at: rows[0].created_at, ...r, roundtrip_ms, summary: s });
}
