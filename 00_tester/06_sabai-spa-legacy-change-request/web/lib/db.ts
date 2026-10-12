// ต่อ PostgreSQL ด้วย pg Pool แบบ lazy (ไม่ต่อ db ตอน build) · SQL ตรง ๆ ไม่ใช้ ORM
import pg from "pg";

let pool: pg.Pool | null = null;

export function getPool(): pg.Pool {
  if (!pool) {
    // DATE → สตริง YYYY-MM-DD (ไม่แปลงเป็น Date ตามโซนเครื่อง)
    pg.types.setTypeParser(1082, (v: string) => v);
    pool = new pg.Pool({
      connectionString: process.env.DATABASE_URL ?? "postgres://sabai:sabai@localhost:5433/sabai",
      max: 10,
      connectionTimeoutMillis: 3000,
    });
    pool.on("error", () => {});
  }
  return pool;
}

export type Db = pg.Pool | pg.PoolClient;

export async function query<T extends pg.QueryResultRow = pg.QueryResultRow>(text: string, params: unknown[] = [], db: Db = getPool()) {
  return db.query<T>(text, params);
}

/** รันใน transaction เดียว · error ใด ๆ → ROLLBACK */
export async function withTx<T>(fn: (c: pg.PoolClient) => Promise<T>): Promise<T> {
  const client = await getPool().connect();
  try {
    await client.query("BEGIN");
    const out = await fn(client);
    await client.query("COMMIT");
    return out;
  } catch (e) {
    await client.query("ROLLBACK").catch(() => {});
    throw e;
  } finally {
    client.release();
  }
}

/** NUMERIC(10,2) จาก pg (สตริง) → สตางค์ (จำนวนเต็ม) */
export function toSatang(v: string | number | null | undefined): number {
  if (v === null || v === undefined) return 0;
  const s = String(v);
  const neg = s.startsWith("-");
  const [i, f = ""] = s.replace("-", "").split(".");
  const n = Number(i) * 100 + Number((f + "00").slice(0, 2));
  return neg ? -n : n;
}

/** สตางค์ → สตริง NUMERIC สำหรับส่งเข้า SQL */
export function fromSatang(n: number): string {
  const neg = n < 0;
  const a = Math.abs(n);
  return `${neg ? "-" : ""}${Math.floor(a / 100)}.${String(a % 100).padStart(2, "0")}`;
}
