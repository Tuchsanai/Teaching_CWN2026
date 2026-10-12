import { NextResponse } from "next/server";
import { getPool } from "@/lib/db.ts";

export const dynamic = "force-dynamic";

export async function GET() {
  let db = false;
  try {
    const r = await Promise.race([
      getPool().query("SELECT 1 AS ok"),
      new Promise<never>((_, rej) => setTimeout(() => rej(new Error("timeout")), 3000)),
    ]);
    db = r.rows[0]?.ok === 1;
  } catch {
    db = false;
  }
  return NextResponse.json({ ok: true, db });
}
