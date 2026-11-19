/**
 * แก้ค่าของใบ (W14 · และส่วนแก้ใน W15) — FR-11 · FR-14 · FR-17 · NFR-10
 *
 * - ค่า `ai_*` ไม่ถูกแตะ ค่าที่คนแก้อยู่ในคอลัมน์ที่ไม่มี `ai_`
 * - ทุกช่องที่เปลี่ยนจริงบันทึก 1 แถวใน `receipt_edits` (ผู้แก้ + เวลา)
 * - การตรวจรูปแบบที่นี่เป็นแค่รูปแบบข้อมูล กฎยอดรวม BR-06 ตรวจตอนยืนยันด้วย rules.checkConfirmTotal
 *   (บันทึกยอด −5.00 ได้ แต่ยืนยันไม่ได้ ตาม TD-BR06-d)
 */
import type { PoolClient } from 'pg';
import { satangToBaht, toSatang } from '../../../lib/rules';
import type { SessionUser } from './auth';
import { isUuid } from './db';
import { ApiError, badRequest } from './http';
import type { ItemRow, ReceiptRow } from './receipts';

const MAX_ABS_SATANG = 99_999_999_999; // numeric(12,2)
const MAX_TEXT = 500;
const MAX_ITEMS = 200;

export const EDITABLE_STATUSES = ['review', 'unreadable'] as const;

export function assertEditable(row: ReceiptRow): void {
  if (row.status !== 'review' && row.status !== 'unreadable') {
    throw new ApiError(
      409,
      'not_editable',
      row.status === 'confirmed'
        ? 'ใบนี้ยืนยันแล้ว แก้ไม่ได้ ต้องให้หัวหน้าทีมเปิดใบกลับก่อน'
        : 'ใบนี้ยังอ่านไม่เสร็จ ยังแก้ไม่ได้',
      { status: row.status },
    );
  }
}

function parseText(value: unknown, field: string): string | null {
  if (value === null) return null;
  if (typeof value !== 'string') throw badRequest(`${field} ต้องเป็นข้อความ`);
  const v = value.trim();
  if (v.length > MAX_TEXT) throw badRequest(`${field} ยาวเกิน ${MAX_TEXT} ตัวอักษร`);
  return v === '' ? null : v;
}

export function parseMoney(value: unknown, field: string): string | null {
  if (value === null || value === '') return null;
  if (typeof value !== 'string' && typeof value !== 'number') throw badRequest(`${field} ต้องเป็นจำนวนเงิน`);
  if (typeof value === 'string' && !/^\s*[+-]?[\d,]*(\.\d{0,2})?\s*$/.test(value)) {
    throw badRequest(`${field} ต้องเป็นจำนวนเงินทศนิยมไม่เกิน 2 ตำแหน่ง`);
  }
  const s = toSatang(value);
  if (s === null || Math.abs(s) > MAX_ABS_SATANG) throw badRequest(`${field} ไม่ใช่จำนวนเงินที่ถูกต้อง`);
  return satangToBaht(s);
}

function parseDate(value: unknown, field: string): string | null {
  if (value === null || value === '') return null;
  if (typeof value !== 'string') throw badRequest(`${field} ต้องเป็นวันที่ YYYY-MM-DD`);
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value.trim());
  if (!m) throw badRequest(`${field} ต้องเป็นวันที่ YYYY-MM-DD`);
  const [y, mo, d] = [+m[1], +m[2], +m[3]];
  const dt = new Date(Date.UTC(y, mo - 1, d));
  if (dt.getUTCFullYear() !== y || dt.getUTCMonth() !== mo - 1 || dt.getUTCDate() !== d) {
    throw badRequest(`${field} ไม่ใช่วันที่ที่มีจริง`);
  }
  return m[0];
}

function sameMoney(a: string | null, b: string | null): boolean {
  if (a === null || b === null) return a === b;
  return toSatang(a) === toSatang(b);
}

interface EditLog {
  field: string;
  oldValue: string | null;
  newValue: string | null;
}

export interface EditResult {
  changes: EditLog[];
}

/**
 * ใช้ค่าจาก body กับใบ (ต้องล็อกแถวแล้ว) · คืนรายการช่องที่เปลี่ยน
 * body: { merchant?, receiptDate?, total?, categoryId?, items?: [{ lineNo?, name?, price?, removed? }] }
 * - items ที่มี lineNo → แก้บรรทัดนั้น · ไม่มี lineNo → เพิ่มบรรทัดใหม่ · ลบด้วย removed=true (ไม่ลบจริง)
 */
export async function applyEdits(
  client: PoolClient,
  row: ReceiptRow,
  items: ItemRow[],
  body: Record<string, unknown>,
  user: SessionUser,
): Promise<EditResult> {
  const changes: EditLog[] = [];
  const sets: string[] = [];
  const params: unknown[] = [row.id];

  const setField = (column: string, field: string, oldValue: string | null, newValue: string | null) => {
    params.push(newValue);
    sets.push(`${column} = $${params.length}`);
    changes.push({ field, oldValue, newValue });
  };

  if ('merchant' in body) {
    const v = parseText(body.merchant, 'merchant');
    if (v !== row.merchant) setField('merchant', 'merchant', row.merchant, v);
  }
  if ('receiptDate' in body) {
    const v = parseDate(body.receiptDate, 'receiptDate');
    if (v !== row.receipt_date) setField('receipt_date', 'receipt_date', row.receipt_date, v);
  }
  if ('total' in body) {
    const v = parseMoney(body.total, 'total');
    if (!sameMoney(v, row.total)) setField('total', 'total', row.total, v);
  }
  if ('categoryId' in body) {
    const raw = body.categoryId;
    let v: string | null = null;
    if (raw !== null && raw !== '') {
      if (!isUuid(raw)) throw badRequest('categoryId ไม่ถูกต้อง');
      const found = await client.query('SELECT 1 FROM categories WHERE id = $1', [raw]);
      if (!found.rowCount) throw badRequest('ไม่พบหมวดรายจ่ายนี้');
      v = raw;
    }
    if (v !== row.category_id) setField('category_id', 'category_id', row.category_id, v);
  }

  const itemChanges: Array<() => Promise<void>> = [];
  if ('items' in body) {
    if (!Array.isArray(body.items)) throw badRequest('items ต้องเป็นรายการ');
    if (body.items.length > MAX_ITEMS) throw badRequest(`items มีได้ไม่เกิน ${MAX_ITEMS} บรรทัด`);
    let nextLine = items.reduce((m, i) => Math.max(m, i.line_no), 0);
    const byLine = new Map(items.map((i) => [i.line_no, i]));
    for (const [idx, rawItem] of body.items.entries()) {
      if (!rawItem || typeof rawItem !== 'object' || Array.isArray(rawItem)) throw badRequest(`items[${idx}] ไม่ถูกต้อง`);
      const it = rawItem as Record<string, unknown>;
      const lineNo = it.lineNo;
      if (lineNo !== undefined && lineNo !== null) {
        if (typeof lineNo !== 'number' || !Number.isInteger(lineNo)) throw badRequest(`items[${idx}].lineNo ไม่ถูกต้อง`);
        const existing = byLine.get(lineNo);
        if (!existing) throw badRequest(`ไม่มีรายการบรรทัดที่ ${lineNo}`);
        const updates: Array<[string, unknown]> = [];
        if ('name' in it) {
          const v = parseText(it.name, `items[${idx}].name`);
          if (v !== existing.name) {
            updates.push(['name', v]);
            changes.push({ field: `item[${lineNo}].name`, oldValue: existing.name, newValue: v });
          }
        }
        if ('price' in it) {
          const v = parseMoney(it.price, `items[${idx}].price`);
          if (!sameMoney(v, existing.price)) {
            updates.push(['price', v]);
            changes.push({ field: `item[${lineNo}].price`, oldValue: existing.price, newValue: v });
          }
        }
        if ('removed' in it) {
          if (typeof it.removed !== 'boolean') throw badRequest(`items[${idx}].removed ต้องเป็น true/false`);
          if (it.removed !== existing.removed) {
            updates.push(['removed', it.removed]);
            changes.push({ field: `item[${lineNo}].removed`, oldValue: String(existing.removed), newValue: String(it.removed) });
          }
        }
        if (updates.length) {
          itemChanges.push(async () => {
            const cols = updates.map(([c], i) => `${c} = $${i + 2}`).join(', ');
            await client.query(`UPDATE receipt_items SET ${cols} WHERE id = $1`, [existing.id, ...updates.map(([, v]) => v)]);
          });
        }
      } else {
        if (it.removed === true) continue;
        const name = 'name' in it ? parseText(it.name, `items[${idx}].name`) : null;
        const price = 'price' in it ? parseMoney(it.price, `items[${idx}].price`) : null;
        const line = ++nextLine;
        changes.push({ field: `item[${line}]`, oldValue: null, newValue: `${name ?? ''} ${price ?? ''}`.trim() || null });
        itemChanges.push(async () => {
          await client.query(
            `INSERT INTO receipt_items (receipt_id, line_no, name, price) VALUES ($1, $2, $3, $4)`,
            [row.id, line, name, price],
          );
        });
      }
    }
  }

  if (changes.length === 0) return { changes };

  // ใบอ่านไม่ได้ที่คนพิมพ์เอง (FR-17)
  if (row.status === 'unreadable' && !row.entered_manually) sets.push('entered_manually = true');
  if (sets.length) await client.query(`UPDATE receipts SET ${sets.join(', ')} WHERE id = $1`, params);
  for (const run of itemChanges) await run();
  for (const c of changes) {
    await client.query(
      `INSERT INTO receipt_edits (receipt_id, field, old_value, new_value, edited_by, edited_at)
       VALUES ($1, $2, $3, $4, $5, clock_timestamp())`,
      [row.id, c.field, c.oldValue, c.newValue, user.id],
    );
  }
  return { changes };
}

export function hasEditFields(body: Record<string, unknown>): boolean {
  return ['merchant', 'receiptDate', 'total', 'categoryId', 'items'].some((k) => k in body);
}
