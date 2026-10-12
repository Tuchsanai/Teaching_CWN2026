// โหมดทดสอบ: รีเซ็ตกลับเป็น seed (NFR-14) และล็อก "วันนี้" (NFR-13)
import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { parseClockValue } from "../clock.ts";
import { withTx } from "../db.ts";
import { BKK_OFFSET_MS } from "../rules/time.ts";
import { ApiError } from "./http.ts";

export const DEFAULT_TEST_NOW = "2026-10-10T10:00:00+07:00";

const TABLES = [
  "point_txn", "gift_card_txn", "birthday_use", "waist_measurement", "body_photo", "review", "booking_slot", "booking",
  "course_purchase", "gift_card", "service_herb", "therapist_service", "herb", "hotel", "room", "therapist", "service",
  "customer", "app_setting", "shop_holiday",
];

let seedCache: string | null = null;

function seedSql(): string {
  if (seedCache) return seedCache;
  const candidates = [
    process.env.SEED_SQL_PATH,
    join(process.cwd(), "sql", "02-seed.sql"),
    join(process.cwd(), "..", "db", "init", "02-seed.sql"),
  ].filter(Boolean) as string[];
  const found = candidates.find((p) => existsSync(p));
  if (!found) throw new Error("seed SQL not found");
  seedCache = readFileSync(found, "utf8");
  return seedCache;
}

/** Date → "2026-10-10T10:00:00+07:00" */
export function bangkokIso(d: Date): string {
  return new Date(d.getTime() + BKK_OFFSET_MS).toISOString().replace(/\.\d{3}Z$/, "+07:00");
}

export async function resetTestData(nowInput: unknown): Promise<{ ok: true; now: string }> {
  const raw = nowInput === undefined || nowInput === null || nowInput === "" ? DEFAULT_TEST_NOW : String(nowInput);
  const at = parseClockValue(raw);
  if (!at) throw new ApiError(422, "BAD_REQUEST", { field: "now" });
  const iso = bangkokIso(at);
  const sql = seedSql();
  await withTx(async (c) => {
    await c.query("LOCK TABLE booking IN ACCESS EXCLUSIVE MODE");
    await c.query(`TRUNCATE ${TABLES.join(", ")} RESTART IDENTITY CASCADE`);
    await c.query(sql);
    await c.query("UPDATE app_setting SET value = $1 WHERE key = 'test_today'", [iso]);
  });
  return { ok: true, now: iso };
}

/** เปลี่ยน "วันนี้" ของระบบ (test seam) — แก้แค่ app_setting.test_today ไม่ล้างข้อมูลตารางอื่น */
export async function setTestClock(nowInput: unknown): Promise<{ ok: true; now: string }> {
  const raw = nowInput === undefined || nowInput === null ? "" : String(nowInput);
  const at = parseClockValue(raw);
  if (!at) throw new ApiError(422, "BAD_REQUEST", { field: "now" });
  const iso = bangkokIso(at);
  await withTx(async (c) => {
    await c.query("UPDATE app_setting SET value = $1 WHERE key = 'test_today'", [iso]);
  });
  return { ok: true, now: iso };
}
