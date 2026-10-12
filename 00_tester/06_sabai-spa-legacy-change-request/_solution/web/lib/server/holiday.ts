// CR-04 วันหยุดร้าน: ปิดทั้งวันทุกช่องทาง (รอบเวลา ราคา จองทุกแบบ แชท) · ตาราง shop_holiday (db/migrations/001_shop_holiday.sql)
import { getPool, query, type Db } from "../db.ts";
import { pickName, type Lang } from "../i18n.ts";
import { ApiError } from "./http.ts";

export interface HolidayRow {
  holiday_date: string; // DATE → "YYYY-MM-DD" (db.ts setTypeParser 1082)
  name_th: string;
  name_en: string;
  name_zh: string;
}

export async function listHolidays(db: Db = getPool()): Promise<HolidayRow[]> {
  const r = await query<HolidayRow>("SELECT holiday_date, name_th, name_en, name_zh FROM shop_holiday ORDER BY holiday_date", [], db);
  return r.rows;
}

export async function findHoliday(db: Db, date: string): Promise<HolidayRow | null> {
  const r = await query<HolidayRow>("SELECT holiday_date, name_th, name_en, name_zh FROM shop_holiday WHERE holiday_date = $1", [date], db);
  return r.rows[0] ?? null;
}

export function holidayName(h: HolidayRow, lang: Lang): string {
  return pickName(h, lang);
}

/** วันหยุดร้าน → 422 SHOP_CLOSED {date, name} · เรียกหลังตรวจช่วงวันจอง (DATE_OUT_OF_RANGE มาก่อน · CR-04-ANSWERS ①) */
export async function assertShopOpen(db: Db, date: string, lang: Lang): Promise<void> {
  const h = await findHoliday(db, date);
  if (h) throw new ApiError(422, "SHOP_CLOSED", { date, name: holidayName(h, lang) });
}
