import { pool, ready } from "@/lib/db";
export const dynamic = "force-dynamic";

export async function GET(_: Request, { params }: { params: { id: string } }) {
  const id = Number(params.id);
  if (!Number.isInteger(id)) return new Response("not found", { status: 404 });
  await ready();
  const { rows } = await pool.query("SELECT image, mime FROM inspections WHERE id=$1", [id]);
  if (!rows.length) return new Response("not found", { status: 404 });
  return new Response(rows[0].image, { headers: { "Content-Type": rows[0].mime, "Cache-Control": "private, max-age=86400" } });
}
