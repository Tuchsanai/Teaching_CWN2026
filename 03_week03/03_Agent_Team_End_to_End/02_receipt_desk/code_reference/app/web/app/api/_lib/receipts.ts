/**
 * อ่าน/แปลงใบเสร็จสำหรับ API (W11 · W12 · W13 · W14 · W15 · W16 · W17)
 *
 * กฎความเป็นส่วนตัว (DESIGN 8 · FR-24 · FR-25 · FR-27 · NFR-07):
 * - ลูกค้าเห็นเฉพาะใบของร้านตัวเอง (กรองด้วย client_id ของ session ที่ SQL) · ใบร้านอื่น → 404
 * - ใบที่ยังไม่ confirmed ส่งให้ลูกค้าเฉพาะ ชื่อไฟล์ · เวลาที่รับ · สถานะ — ไม่มีตัวเลขหรือธงใด ๆ ออกจาก server
 */
import type { PoolClient } from 'pg';
import rules, { satangToBaht, toSatang } from '../../../lib/rules';
import type { SessionUser } from './auth';
import { isUuid, query, queryOne } from './db';
import { notFound } from './http';

export type ReceiptStatus = 'queued' | 'processing' | 'review' | 'confirmed' | 'unreadable';

export const STATUSES: readonly ReceiptStatus[] = ['queued', 'processing', 'review', 'confirmed', 'unreadable'];

export const STATUS_LABEL: Record<ReceiptStatus, string> = {
  queued: 'รออ่าน',
  processing: 'กำลังอ่าน',
  review: 'รอตรวจ',
  confirmed: 'ยืนยันแล้ว',
  unreadable: 'อ่านไม่ได้',
};

/** ข้อความสถานะที่ลูกค้าเห็นก่อนยืนยัน (FR-27) */
export const CLIENT_PENDING_LABEL = 'รับแล้ว รอสำนักงานตรวจ';

export interface ReceiptRow {
  id: string;
  batch_id: string;
  client_id: string;
  client_name: string;
  client_code: string;
  priority: 'normal' | 'urgent';
  file_name: string;
  file_path: string;
  mime_type: string;
  size_bytes: number;
  status: ReceiptStatus;
  attempts: number;
  ai_merchant: string | null;
  ai_receipt_date: string | null;
  ai_total: string | null;
  total_confidence: string | null;
  merchant: string | null;
  receipt_date: string | null;
  total: string | null;
  flag_low_confidence: boolean;
  flag_mismatch: boolean;
  entered_manually: boolean;
  category_id: string | null;
  category_name: string | null;
  accepted_at: Date;
  result_at: Date | null;
  review_opened_at: Date | null;
  review_seconds: number | null;
  confirmed_by: string | null;
  confirmed_by_name: string | null;
  confirmed_at: Date | null;
  unreadable_reason: string | null;
}

export interface ItemRow {
  id: string;
  line_no: number;
  ai_name: string | null;
  ai_price: string | null;
  name: string | null;
  price: string | null;
  removed: boolean;
}

export const RECEIPT_SELECT = `
  SELECT r.id, r.batch_id, r.client_id, c.name AS client_name, c.code AS client_code, b.priority,
         r.file_name, r.file_path, r.mime_type, r.size_bytes, r.status, r.attempts,
         r.ai_merchant, r.ai_receipt_date, r.ai_total, r.total_confidence,
         r.merchant, r.receipt_date, r.total, r.flag_low_confidence, r.flag_mismatch,
         r.entered_manually, r.category_id, cat.name AS category_name,
         r.accepted_at, r.result_at, r.review_opened_at, r.review_seconds,
         r.confirmed_by, cu.display_name AS confirmed_by_name, r.confirmed_at, r.unreadable_reason
    FROM receipts r
    JOIN batches b ON b.id = r.batch_id
    JOIN clients c ON c.id = r.client_id
    LEFT JOIN categories cat ON cat.id = r.category_id
    LEFT JOIN users cu ON cu.id = r.confirmed_by`;

/**
 * โหลดใบ 1 ใบตามสิทธิ์ของผู้ใช้ — ไม่พบ / ร้านอื่น / id ผิดรูป → 404 not_found
 * ส่ง `client` + `forUpdate` เพื่อล็อกแถวในธุรกรรม
 */
export async function loadReceipt(
  user: SessionUser,
  id: string,
  opts: { client?: PoolClient; forUpdate?: boolean } = {},
): Promise<ReceiptRow> {
  if (!isUuid(id)) throw notFound();
  const params: unknown[] = [id];
  let sql = `${RECEIPT_SELECT} WHERE r.id = $1`;
  if (user.role === 'client') {
    params.push(user.clientId);
    sql += ` AND r.client_id = $2`;
  }
  if (opts.forUpdate) sql += ' FOR UPDATE OF r';
  const row = opts.client
    ? (await opts.client.query<ReceiptRow>(sql, params)).rows[0]
    : await queryOne<ReceiptRow>(sql, params);
  if (!row) throw notFound();
  return row;
}

export async function loadItems(receiptId: string, client?: PoolClient): Promise<ItemRow[]> {
  const sql = `SELECT id, line_no, ai_name, ai_price, name, price, removed
                 FROM receipt_items WHERE receipt_id = $1 ORDER BY line_no`;
  return client ? (await client.query<ItemRow>(sql, [receiptId])).rows : query<ItemRow>(sql, [receiptId]);
}

/** เหตุผลของธงที่บันทึกไว้ (FR-09) — ข้อความและผลต่างคิดด้วย rules.ts */
export function flagInfo(row: ReceiptRow, items: ItemRow[] | null) {
  const reasons: string[] = [];
  if (row.flag_low_confidence) reasons.push('ไม่แน่ใจยอดรวม: ความมั่นใจของยอดรวมต่ำกว่า 0.90');
  let diff: string | null = null;
  if (items) {
    const diffSatang = rules.itemsDiffSatang(
      items.map((i) => i.ai_price),
      row.ai_total,
    );
    diff = satangToBaht(diffSatang);
  }
  if (row.flag_mismatch) {
    reasons.push(`ยอดไม่ตรงรายการ: ผลรวมรายการต่างจากยอดรวม${diff ? ` ${diff} บาท` : ''} (เกิน 1.00 บาท)`);
  }
  return {
    lowConfidence: row.flag_low_confidence,
    mismatch: row.flag_mismatch,
    flagged: row.flag_low_confidence || row.flag_mismatch,
    reasons,
  };
}

/** ผลรวมราคาของรายการที่ไม่ถูกลบ (สตางค์ → บาท) */
export function itemsSum(items: ItemRow[]): string {
  let s = 0;
  for (const i of items) if (!i.removed) s += toSatang(i.price) ?? 0;
  return satangToBaht(s);
}

function iso(d: Date | null): string | null {
  return d ? new Date(d).toISOString() : null;
}

/** มุมมองของลูกค้า — ตัวเลขมีเฉพาะใบที่ยืนยันแล้ว (FR-25 · FR-27) */
export function clientView(row: ReceiptRow, items: ItemRow[] | null = null) {
  const base = {
    id: row.id,
    fileName: row.file_name,
    acceptedAt: iso(row.accepted_at),
    status: row.status === 'confirmed' ? 'confirmed' : 'received',
    statusLabel: row.status === 'confirmed' ? STATUS_LABEL.confirmed : CLIENT_PENDING_LABEL,
  };
  if (row.status !== 'confirmed') return base;
  return {
    ...base,
    merchant: row.merchant,
    receiptDate: row.receipt_date,
    total: row.total,
    categoryId: row.category_id,
    categoryName: row.category_name,
    confirmedAt: iso(row.confirmed_at),
    ...(items
      ? { items: items.filter((i) => !i.removed).map((i) => ({ lineNo: i.line_no, name: i.name, price: i.price })) }
      : {}),
  };
}

/** มุมมองของสำนักงาน (staff · lead · owner) */
export function officeListView(row: ReceiptRow, now: Date) {
  const overdue = rules.isOverdue({ priority: row.priority, status: row.status, acceptedAt: row.accepted_at }, now);
  return {
    id: row.id,
    batchId: row.batch_id,
    clientId: row.client_id,
    clientName: row.client_name,
    priority: row.priority,
    fileName: row.file_name,
    status: row.status,
    statusLabel: STATUS_LABEL[row.status],
    attempts: row.attempts,
    merchant: row.merchant,
    receiptDate: row.receipt_date,
    total: row.total,
    flags: flagInfo(row, null),
    enteredManually: row.entered_manually,
    acceptedAt: iso(row.accepted_at),
    resultAt: iso(row.result_at),
    confirmedBy: row.confirmed_by_name,
    confirmedAt: iso(row.confirmed_at),
    unreadableReason: row.unreadable_reason,
    overdue,
    minutesWaiting: overdue ? rules.minutesWaiting(row.accepted_at, now) : undefined,
  };
}

export function officeDetailView(row: ReceiptRow, items: ItemRow[], user: SessionUser, now: Date) {
  const canEdit = (user.role === 'staff' || user.role === 'lead') && (row.status === 'review' || row.status === 'unreadable');
  return {
    ...officeListView(row, now),
    flags: flagInfo(row, items),
    mimeType: row.mime_type,
    sizeBytes: row.size_bytes,
    imageUrl: `/api/receipts/${row.id}/image`,
    totalConfidence: row.total_confidence,
    categoryId: row.category_id,
    categoryName: row.category_name,
    items: items.map((i) => ({ id: i.id, lineNo: i.line_no, name: i.name, price: i.price, removed: i.removed })),
    itemsSum: itemsSum(items),
    reviewOpenedAt: iso(row.review_opened_at),
    reviewSeconds: row.review_seconds,
    // ค่าเดิมที่ระบบอ่าน (FR-14 · FR-15) — ใช้แสดง original-* บนหน้าตรวจ
    original: {
      merchant: row.ai_merchant,
      receiptDate: row.ai_receipt_date,
      total: row.ai_total,
      items: items.map((i) => ({ lineNo: i.line_no, name: i.ai_name, price: i.ai_price })),
    },
    permissions: {
      canEdit,
      canConfirm: canEdit,
      canReopen: user.role === 'lead' && row.status === 'confirmed',
    },
  };
}

/** บันทึกการเปลี่ยนสถานะ 1 แถว (DESIGN 4: ทุกเส้นบันทึกใน receipt_events) */
export async function addEvent(client: PoolClient, receiptId: string, from: ReceiptStatus | null, to: ReceiptStatus, actorId: string | null) {
  await client.query(
    `INSERT INTO receipt_events (receipt_id, from_status, to_status, actor_id, created_at)
     VALUES ($1, $2, $3, $4, clock_timestamp())`,
    [receiptId, from, to, actorId],
  );
}
