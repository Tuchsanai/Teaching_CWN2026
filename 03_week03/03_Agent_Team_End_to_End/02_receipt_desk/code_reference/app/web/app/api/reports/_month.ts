/**
 * ตัวช่วยร่วมของรายงานรายเดือน (W18 · W19) — BR-14 คิดด้วย rules.ts ทั้งใน SQL และในโค้ด
 * ไฟล์ขึ้นต้นด้วย `_` และไม่ชื่อ route.ts จึงไม่ใช่ route
 */
import type { PoolClient } from 'pg';
import rules, { isValidMonth } from '../../../lib/rules';
import { query } from '../_lib/db';
import { badRequest } from '../_lib/http';

export interface MonthRow {
  id: string;
  receipt_date: string;
  merchant: string | null;
  total: string;
  category_id: string | null;
  category_name: string | null;
  file_name: string;
  confirmed_by_name: string | null;
  confirmed_at: Date | null;
}

export function parseMonth(value: string | null): string {
  if (!value) throw badRequest('ต้องระบุ month รูปแบบ YYYY-MM');
  if (!isValidMonth(value)) throw badRequest('month ต้องเป็นรูปแบบ YYYY-MM');
  return value;
}

/** ใบที่ยืนยันแล้วของร้านในเดือน (ช่วงวันที่จาก rules.monthBounds และกรองซ้ำด้วย rules.isInMonth) */
export async function confirmedInMonth(clientId: string, month: string, client?: PoolClient): Promise<MonthRow[]> {
  const bounds = rules.monthBounds(month);
  const sql = `
    SELECT r.id, r.receipt_date, r.merchant, r.total, r.category_id, cat.name AS category_name,
           r.file_name, u.display_name AS confirmed_by_name, r.confirmed_at
      FROM receipts r
      LEFT JOIN categories cat ON cat.id = r.category_id
      LEFT JOIN users u ON u.id = r.confirmed_by
     WHERE r.client_id = $1 AND r.status = 'confirmed'
       AND r.receipt_date BETWEEN $2::date AND $3::date
     ORDER BY r.receipt_date, r.confirmed_at, r.id`;
  const params = [clientId, bounds.startDate, bounds.endDate];
  const rows = client ? (await client.query<MonthRow>(sql, params)).rows : await query<MonthRow>(sql, params);
  return rows.filter((r) => rules.isInMonth(r.receipt_date, month));
}

export function summarize(rows: MonthRow[], month: string) {
  return rules.summarizeMonth(
    rows.map((r) => ({ status: 'confirmed', receiptDate: r.receipt_date, total: r.total, categoryId: r.category_id })),
    month,
  );
}
