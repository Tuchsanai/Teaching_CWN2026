import { NextResponse } from "next/server";
import { pool } from "@/lib/db";

export const dynamic = "force-dynamic";

export async function GET() {
  const r = await pool.query(
    "SELECT id, created_at, model, source, items, subtotal, tax, total, thumb FROM expenses ORDER BY id DESC LIMIT 200"
  );
  return NextResponse.json({ expenses: r.rows });
}

export async function POST(req: Request) {
  const b = await req.json();
  if (!Array.isArray(b.items)) return NextResponse.json({ error: "ข้อมูลไม่ครบ" }, { status: 400 });
  const r = await pool.query(
    `INSERT INTO expenses (model, source, items, subtotal, tax, total, thumb)
     VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING id`,
    [b.model === "ft" ? "ft" : "base", String(b.source ?? "").slice(0, 120), JSON.stringify(b.items), b.subtotal ?? null, b.tax ?? null, b.total ?? null, String(b.thumb ?? "")]
  );
  return NextResponse.json({ id: r.rows[0].id });
}

export async function DELETE(req: Request) {
  const id = Number(new URL(req.url).searchParams.get("id"));
  await pool.query("DELETE FROM expenses WHERE id = $1", [id]);
  return NextResponse.json({ ok: true });
}
