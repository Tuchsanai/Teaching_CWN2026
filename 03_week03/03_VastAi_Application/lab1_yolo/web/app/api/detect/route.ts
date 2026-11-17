// รับรูปจากเบราว์เซอร์ → ส่งต่อไป AI server บน Vast.ai → สรุปผล → บันทึกประวัติลง PostgreSQL
import { NextResponse } from "next/server";
import { pool } from "@/lib/db";
import { summarize, type DetectResult } from "@/lib/ppe";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const MAX_BYTES = 8 * 1024 * 1024;

export async function POST(req: Request) {
  const form = await req.formData();
  const file = form.get("file");
  if (!(file instanceof Blob) || file.size === 0) {
    return NextResponse.json({ error: "กรุณาเลือกรูปภาพ" }, { status: 400 });
  }
  if (file.size > MAX_BYTES) return NextResponse.json({ error: "รูปใหญ่เกิน 8 MB" }, { status: 400 });
  const name = (file as File).name || "upload.jpg";
  const bytes = Buffer.from(await file.arrayBuffer());

  const base = (process.env.YOLO_BASE_URL || "").replace(/\/$/, "");
  const fd = new FormData();
  fd.append("file", new Blob([bytes], { type: file.type || "image/jpeg" }), name);

  const t0 = performance.now();
  let res: Response;
  try {
    res = await fetch(`${base}/v1/detect?conf=0.35`, {
      method: "POST",
      headers: { Authorization: `Bearer ${process.env.YOLO_API_KEY ?? ""}` },
      body: fd,
      signal: AbortSignal.timeout(30_000),
    });
  } catch {
    return NextResponse.json({ error: "เชื่อมต่อ AI server ไม่ได้ — ตรวจค่าใน yolo.env และสถานะเครื่องบน Vast.ai" }, { status: 502 });
  }
  const roundtrip_ms = Math.round((performance.now() - t0) * 10) / 10;
  if (res.status === 401) return NextResponse.json({ error: "API key ของ AI server ไม่ถูกต้อง" }, { status: 502 });
  if (!res.ok) return NextResponse.json({ error: `AI server ตอบกลับผิดพลาด (${res.status})` }, { status: 502 });

  const r = (await res.json()) as DetectResult;
  const s = summarize(r.detections);
  const row = await pool.query<{ id: number }>(
    `INSERT INTO inspections (file_name, mime, image, width, height, model, detections,
       persons, hardhat, no_hardhat, no_vest, passed, inference_ms, roundtrip_ms)
     VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14) RETURNING id`,
    [name, file.type || "image/jpeg", bytes, r.width, r.height, r.model, JSON.stringify(r.detections),
     s.persons, s.hardhat, s.no_hardhat, s.no_vest, s.passed, r.inference_ms, roundtrip_ms]
  );

  return NextResponse.json({ id: row.rows[0].id, ...r, summary: s, roundtrip_ms });
}
