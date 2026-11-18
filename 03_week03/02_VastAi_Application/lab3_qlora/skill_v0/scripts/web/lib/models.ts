import { pool } from "./db";

// โมเดล 2 ตัวบน AI server เดียวกัน (ชื่ออ่านจาก lab3_qlora/chatbot.env)
export type ModelKey = "base" | "ft";
export const MODEL_KEYS: ModelKey[] = ["base", "ft"];
export const MODEL_LABEL: Record<ModelKey, string> = { base: "Base", ft: "Fine-tuned" };

export function modelName(k: ModelKey): string {
  return k === "base"
    ? process.env.BASE_MODEL || "qwen3-4b-base"
    : process.env.FT_MODEL || "qwen3-4b-sabaijai";
}

export function asModelKey(v: unknown): ModelKey | null {
  const s = String(v ?? "").trim().toLowerCase();
  if (s === "base" || s === modelName("base")) return "base";
  if (s === "ft" || s === "fine-tuned" || s === "finetuned" || s === modelName("ft")) return "ft";
  return null;
}

// ตารางเสริมของ LAB นี้ สร้างเองถ้ายังไม่มี (volume เก่าที่ไม่ได้รัน init.sql ใหม่ก็ใช้ได้)
let ready: Promise<unknown> | null = null;
export function ensureTables() {
  ready ??= pool.query(`
    CREATE TABLE IF NOT EXISTS app_settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS compare_runs (
      id SERIAL PRIMARY KEY,
      question TEXT NOT NULL,
      result JSONB NOT NULL,
      created_at TIMESTAMPTZ NOT NULL DEFAULT now()
    );`).catch((e) => {
    ready = null;
    throw e;
  });
  return ready;
}

/** โมเดลเริ่มต้นของเว็บ: อ่านจากตาราง app_settings ทุกครั้ง จึงสลับได้ขณะเว็บเปิดอยู่ */
export async function getDefaultModel(): Promise<ModelKey> {
  await ensureTables();
  const r = await pool.query<{ value: string }>("SELECT value FROM app_settings WHERE key = 'default_model'");
  return asModelKey(r.rows[0]?.value) ?? asModelKey(process.env.DEFAULT_MODEL) ?? "ft";
}

export async function setDefaultModel(k: ModelKey) {
  await ensureTables();
  await pool.query(
    `INSERT INTO app_settings (key, value) VALUES ('default_model', $1)
     ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value`,
    [k]
  );
}

export async function modelInfo() {
  const def = await getDefaultModel();
  return {
    default: def,
    default_model: modelName(def),
    models: MODEL_KEYS.map((k) => ({ key: k, label: MODEL_LABEL[k], name: modelName(k) })),
  };
}
