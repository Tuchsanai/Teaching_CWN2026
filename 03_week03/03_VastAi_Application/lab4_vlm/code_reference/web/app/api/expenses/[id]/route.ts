import { NextResponse } from "next/server";
import { pool, ready } from "@/lib/db";

export const runtime = "nodejs";

export async function DELETE(_: Request, { params }: { params: { id: string } }) {
  await ready();
  await pool.query("DELETE FROM expenses WHERE id = $1", [Number(params.id)]);
  return NextResponse.json({ ok: true });
}
