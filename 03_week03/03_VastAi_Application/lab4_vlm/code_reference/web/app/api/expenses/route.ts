import { NextResponse } from "next/server";
import { pool, ready } from "@/lib/db";
import { loadImage } from "@/lib/server-image";
import { parseReply, MODEL_LABEL, type ModelKey } from "@/lib/receipt";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  await ready();
  const list = await pool.query(
    `SELECT id, title, model, items, subtotal::float8 AS subtotal, tax::float8 AS tax, total::float8 AS total,
            seconds, created_at FROM expenses ORDER BY created_at DESC`);
  return NextResponse.json(list.rows);
}

export async function POST(req: Request) {
  try {
    await ready();
    const form = await req.formData();
    const data = parseReply(String(form.get("receipt") ?? ""));
    if (!data) return NextResponse.json({ error: "ข้อมูลใบเสร็จไม่ถูกต้อง" }, { status: 400 });
    const model = (form.get("model") === "base" ? "base" : "ft") as ModelKey;
    const { jpeg, title } = await loadImage(form);
    const name = String(form.get("title") || title);
    const r = await pool.query(
      `INSERT INTO expenses (title, model, items, subtotal, tax, total, seconds, image)
       VALUES ($1,$2,$3,$4,$5,$6,$7,$8) RETURNING id`,
      [name, MODEL_LABEL[model], JSON.stringify(data.items), data.subtotal, data.tax, data.total,
       Number(form.get("seconds")) || null, jpeg]);
    return NextResponse.json({ id: r.rows[0].id });
  } catch (e: any) {
    return NextResponse.json({ error: e?.message ?? "บันทึกไม่สำเร็จ" }, { status: 500 });
  }
}
