import { pool } from "@/lib/db";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

// POST /api/reset -> ล้างตารางจองและประวัติแชท (ให้ชุดทดสอบเริ่มจากฐานข้อมูลว่างทุกรอบ)
// ใช้เมื่อสคริปต์ทดสอบรันจากที่ที่เข้า PostgreSQL ตรง ๆ ไม่ได้ (เช่นใน container อื่น)
export async function POST() {
  await pool.query("TRUNCATE bookings, chat_messages RESTART IDENTITY");
  const r = await pool.query<{ b: string; c: string }>(
    "SELECT (SELECT count(*) FROM bookings) AS b, (SELECT count(*) FROM chat_messages) AS c"
  );
  return Response.json({ ok: true, bookings: Number(r.rows[0].b), chat_messages: Number(r.rows[0].c) });
}
