// ส่งรูปที่บันทึกไว้ในประวัติ
import { pool } from "@/lib/db";

export const dynamic = "force-dynamic";

export async function GET(_req: Request, { params }: { params: { id: string } }) {
  const r = await pool.query<{ mime: string; image: Buffer }>("SELECT mime, image FROM inspections WHERE id = $1", [
    Number(params.id),
  ]);
  if (!r.rows[0]) return new Response("not found", { status: 404 });
  return new Response(new Uint8Array(r.rows[0].image), {
    headers: { "content-type": r.rows[0].mime, "cache-control": "private, max-age=86400" },
  });
}
