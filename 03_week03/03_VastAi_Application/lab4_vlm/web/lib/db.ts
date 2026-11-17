import { Pool } from "pg";

// ใช้ Pool เดียวทั้งแอป
const g = globalThis as unknown as { _pgPool?: Pool };
export const pool = g._pgPool ?? new Pool({ connectionString: process.env.DATABASE_URL, max: 5 });
g._pgPool = pool;
