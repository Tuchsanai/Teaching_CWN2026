import { Pool } from "pg";
import type { Detection } from "./ppe";

// ใช้ Pool เดียวทั้งแอป
const g = globalThis as unknown as { _pgPool?: Pool };
export const pool = g._pgPool ?? new Pool({ connectionString: process.env.DATABASE_URL, max: 5 });
g._pgPool = pool;

export type Inspection = {
  id: number;
  created_at: string;
  file_name: string;
  width: number;
  height: number;
  model: string;
  detections: Detection[];
  persons: number;
  hardhat: number;
  no_hardhat: number;
  no_vest: number;
  passed: boolean;
  inference_ms: number;
  roundtrip_ms: number;
};

const COLS = `id, to_char(created_at AT TIME ZONE 'Asia/Bangkok', 'DD/MM/YYYY HH24:MI:SS') AS created_at,
  file_name, width, height, model, detections, persons, hardhat, no_hardhat, no_vest, passed, inference_ms, roundtrip_ms`;

export async function listInspections(limit = 100): Promise<Inspection[]> {
  const r = await pool.query<Inspection>(`SELECT ${COLS} FROM inspections ORDER BY id DESC LIMIT $1`, [limit]);
  return r.rows;
}

export async function getInspection(id: number): Promise<Inspection | null> {
  const r = await pool.query<Inspection>(`SELECT ${COLS} FROM inspections WHERE id = $1`, [id]);
  return r.rows[0] ?? null;
}

export async function stats() {
  const r = await pool.query<{ total: string; passed: string; avg_ms: number | null }>(
    "SELECT count(*) AS total, count(*) FILTER (WHERE passed) AS passed, avg(inference_ms) AS avg_ms FROM inspections"
  );
  const s = r.rows[0];
  return { total: Number(s.total), passed: Number(s.passed), avg_ms: s.avg_ms };
}
