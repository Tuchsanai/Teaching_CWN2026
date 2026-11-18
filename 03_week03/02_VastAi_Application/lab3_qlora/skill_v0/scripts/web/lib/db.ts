import { Pool } from "pg";

// ใช้ Pool เดียวทั้งแอป (กันการเปิด connection ซ้ำตอน dev hot-reload)
const g = globalThis as unknown as { _pgPool?: Pool };

export const pool =
  g._pgPool ??
  new Pool({
    connectionString: process.env.DATABASE_URL,
    max: 5,
  });
g._pgPool = pool;

export type Service = {
  id: number;
  name_th: string;
  duration_min: number;
  price_thb: number;
  description_th: string;
};

export async function getServices(): Promise<Service[]> {
  const r = await pool.query<Service>(
    "SELECT id, name_th, duration_min, price_thb, description_th FROM services ORDER BY id"
  );
  return r.rows;
}

export async function getShopInfo(): Promise<Record<string, string>> {
  const r = await pool.query<{ key: string; value: string }>("SELECT key, value FROM shop_info");
  return Object.fromEntries(r.rows.map((x) => [x.key, x.value]));
}

export async function getHistory(sessionId: string, limit = 20) {
  const r = await pool.query<{ role: "user" | "assistant"; content: string }>(
    `SELECT role, content FROM (
       SELECT id, role, content FROM chat_messages
       WHERE session_id = $1 AND role IN ('user','assistant')
       ORDER BY id DESC LIMIT $2
     ) t ORDER BY id ASC`,
    [sessionId, limit]
  );
  return r.rows;
}

export async function saveMessage(sessionId: string, role: "user" | "assistant", content: string) {
  await pool.query("INSERT INTO chat_messages (session_id, role, content) VALUES ($1, $2, $3)", [
    sessionId,
    role,
    content,
  ]);
}
