import { pool, ready } from "@/lib/db";

export const runtime = "nodejs";

export async function GET(_: Request, { params }: { params: { id: string } }) {
  await ready();
  const r = await pool.query("SELECT image FROM expenses WHERE id = $1", [Number(params.id)]);
  if (!r.rows[0]?.image) return new Response("not found", { status: 404 });
  return new Response(r.rows[0].image, { headers: { "Content-Type": "image/jpeg", "Cache-Control": "private, max-age=3600" } });
}
