'use client';

/**
 * หน้าตรวจแก้ใบเสร็จ (B12) · /review
 *
 * - /review                → คิวรอตรวจ: ใบติดธง (พร้อมเหตุผล) แยกจากใบปกติ
 * - /review?id=<receiptId> → ตรวจ 1 ใบ: รูปคู่ 5 ช่องแก้ไขได้ (ชื่อร้าน · วันที่ · รายการ · ราคา · ยอดรวม)
 *   ถ้านำหน้านี้ไปใช้ที่ /receipts/[id] (DESIGN 9.1) ด้วย `export { default } from '../../review/page'`
 *   หน้านี้จะอ่าน id จาก path ให้เอง
 *
 * กติกาที่หน้านี้ทำตาม
 * - FR-09 ธงแสดงพร้อมเหตุผล และแยกจากใบปกติทั้งในคิวและในหน้าตรวจ
 * - FR-11 / FR-17 แก้ทุกช่องได้เมื่อใบเป็น "รอตรวจ" หรือ "อ่านไม่ได้" (permissions.canEdit จาก W12)
 * - FR-12 / BR-06 ปุ่มยืนยันกดได้เมื่อยอดรวม ≥ 0.01 บาท และติ๊ก "เทียบยอดรวมกับรูปแล้ว"
 *   ใบติดธงต้องเปิดดูครบทุกช่องก่อน (โฟกัสช่องชื่อร้าน วันที่ ชื่อรายการ ราคา และยอดรวม อย่างน้อยช่องละครั้ง)
 *   ฝั่ง server ตรวจซ้ำด้วย review_opened_at ที่ W12 บันทึกตอนเปิดใบ (409 review_not_opened)
 * - FR-13 แสดงผู้ยืนยันและเวลา (confirmed-by)
 * - FR-14 / FR-15 / NFR-10 แสดงค่าที่ระบบอ่านเดิมข้างทุกช่อง (original-*) และประวัติการแก้ (W17 · history-row-{ลำดับ})
 *   ทุกการแก้ส่งผ่าน PATCH (W14) ก่อนยืนยันเสมอ server จึงบันทึกผู้แก้และเวลาครบ 1 แถวต่อช่อง
 * - NFR-09 ใบปกติโฟกัสช่องยอดรวมทันที · Enter = ไปช่องถัดไป · Ctrl/⌘+Enter = ยืนยัน · Ctrl/⌘+S = บันทึก
 *   Alt+→ = ใบถัดไป · หลังยืนยันกดใบถัดไปได้ทันที (ใบกลุ่มเดียวกันก่อน งานด่วนก่อน รอนานก่อน)
 *
 * API ที่ใช้ (web/app/api/README.md · B04): W5 /api/me · W11 /api/receipts · W12 GET /api/receipts/{id}
 *   · W13 รูป · W14 PATCH · W15 confirm · W16 reopen (หัวหน้า) · W17 history · W19 รายชื่อหมวด
 */

import { Suspense, useCallback, useEffect, useMemo, useRef, useState } from 'react';
import type { CSSProperties, FocusEvent, KeyboardEvent as ReactKeyboardEvent, ReactNode } from 'react';
import { usePathname, useRouter, useSearchParams } from 'next/navigation';
import { LIMITS, formatBaht, toSatang } from '../../lib/rules';

// ───────────────────────────── ชนิดข้อมูลจาก API ─────────────────────────────

type Role = 'staff' | 'lead' | 'owner' | 'client';
type Status = 'queued' | 'processing' | 'review' | 'confirmed' | 'unreadable';

interface Me {
  id: string;
  displayName: string;
  role: Role;
  roleLabel?: string;
}

interface Flags {
  lowConfidence: boolean;
  mismatch: boolean;
  flagged: boolean;
  reasons: string[];
}

interface ApiItem {
  id: string;
  lineNo: number;
  name: string | null;
  price: string | null;
  removed: boolean;
}

interface Receipt {
  id: string;
  batchId: string;
  clientId: string;
  clientName: string;
  priority: 'normal' | 'urgent';
  fileName: string;
  status: Status;
  statusLabel: string;
  merchant: string | null;
  receiptDate: string | null;
  total: string | null;
  flags: Flags;
  enteredManually: boolean;
  acceptedAt: string | null;
  confirmedBy: string | null;
  confirmedAt: string | null;
  unreadableReason: string | null;
  mimeType: string;
  imageUrl: string;
  totalConfidence: string | null;
  categoryId: string | null;
  categoryName: string | null;
  items: ApiItem[];
  itemsSum: string;
  reviewOpenedAt: string | null;
  reviewSeconds: number | null;
  original: {
    merchant: string | null;
    receiptDate: string | null;
    total: string | null;
    items: Array<{ lineNo: number; name: string | null; price: string | null }>;
  };
  permissions: { canEdit: boolean; canConfirm: boolean; canReopen: boolean };
}

interface ListRow {
  id: string;
  clientName: string;
  priority: 'normal' | 'urgent';
  fileName: string;
  status: Status;
  statusLabel: string;
  merchant: string | null;
  total: string | null;
  flags: Flags;
  enteredManually: boolean;
  acceptedAt: string | null;
}

interface Category {
  id: string;
  name: string;
}

interface HistoryEdit {
  seq: number;
  field: string;
  oldValue: string | null;
  newValue: string | null;
  editedBy: string;
  editedAt: string;
}

interface HistoryEvent {
  from: Status | null;
  to: Status;
  toLabel: string;
  actor: string;
  at: string;
}

interface HistoryResponse {
  edits: HistoryEdit[];
  events: HistoryEvent[];
  enteredManually: boolean;
  confirmedBy: string | null;
  confirmedAt: string | null;
}

// ───────────────────────────── ตัวช่วยเรียก API ─────────────────────────────

class HttpError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string,
    public body: Record<string, unknown> | null,
  ) {
    super(message);
  }
}

const FALLBACK_MESSAGES: Record<string, string> = {
  unauthenticated: 'กรุณาเข้าสู่ระบบ',
  forbidden: 'บัญชีนี้ไม่มีสิทธิ์ทำรายการนี้',
  not_found: 'ไม่พบใบเสร็จนี้',
  not_editable: 'ใบนี้แก้ไม่ได้แล้ว',
  total_not_checked: 'กรุณาติ๊ก "เทียบยอดรวมกับรูปแล้ว" ก่อนยืนยัน',
  total_invalid: 'ยืนยันไม่ได้: ยอดรวมต้องตั้งแต่ 0.01 บาทขึ้นไป',
  category_required: 'กรุณาเลือกหมวดรายจ่ายก่อนยืนยัน',
  date_required: 'กรุณากรอกวันที่บนใบเสร็จก่อนยืนยัน',
  review_not_opened: 'ใบติดธงต้องเปิดดูรายละเอียดทุกช่องก่อนยืนยัน',
  bad_request: 'ข้อมูลไม่ถูกต้อง',
};

async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers: Record<string, string> = { Accept: 'application/json' };
  if (init.body !== undefined) headers['Content-Type'] = 'application/json';
  let res: Response;
  try {
    res = await fetch(path, { credentials: 'same-origin', cache: 'no-store', ...init, headers });
  } catch {
    throw new HttpError(0, 'network', 'ติดต่อเซิร์ฟเวอร์ไม่ได้ กรุณาลองใหม่', null);
  }
  let body: Record<string, unknown> | null = null;
  try {
    body = (await res.json()) as Record<string, unknown>;
  } catch {
    body = null;
  }
  if (!res.ok) {
    const code = typeof body?.error === 'string' ? body.error : `http_${res.status}`;
    const message =
      typeof body?.message === 'string' && body.message
        ? body.message
        : FALLBACK_MESSAGES[code] ?? `ระบบตอบกลับผิดพลาด (${res.status})`;
    throw new HttpError(res.status, code, message, body);
  }
  return body as T;
}

function errorText(e: unknown): string {
  if (e instanceof HttpError) return e.message;
  if (e instanceof Error) return e.message;
  return 'เกิดข้อผิดพลาด';
}

// ───────────────────────────── ตัวช่วยเงิน / วันที่ ─────────────────────────────

/** รูปแบบเดียวกับที่ server รับ (web/app/api/_lib/edits.ts · parseMoney) */
const MONEY_RE = /^\s*[+-]?[\d,]*(\.\d{0,2})?\s*$/;

/** สตางค์ของข้อความเงิน · ว่าง → null · ผิดรูป → NaN */
function moneySatang(text: string): number | null {
  const t = text.trim();
  if (t === '') return null;
  if (!MONEY_RE.test(t)) return Number.NaN;
  const s = toSatang(t);
  return s === null ? Number.NaN : s;
}

function isBadMoney(text: string): boolean {
  return Number.isNaN(moneySatang(text) as number);
}

function sameMoneyText(text: string, apiValue: string | null): boolean {
  const a = moneySatang(text);
  const b = apiValue === null ? null : toSatang(apiValue);
  return a === b;
}

function showMoney(value: string | null | undefined): string {
  if (value === null || value === undefined || value === '') return '—';
  const s = toSatang(value);
  return s === null ? value : formatBaht(s);
}

const TH_DATE = new Intl.DateTimeFormat('th-TH', { timeZone: 'Asia/Bangkok', dateStyle: 'medium' });
const TH_DATETIME = new Intl.DateTimeFormat('th-TH', {
  timeZone: 'Asia/Bangkok',
  dateStyle: 'medium',
  timeStyle: 'short',
});

function showDate(ymd: string | null | undefined): string {
  if (!ymd) return '—';
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(ymd);
  if (!m) return ymd;
  return `${TH_DATE.format(new Date(Date.UTC(+m[1], +m[2] - 1, +m[3], 5)))} (${ymd})`;
}

function showDateTime(iso: string | null | undefined): string {
  if (!iso) return '—';
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? iso : TH_DATETIME.format(d);
}

function bangkokMonth(): string {
  return new Date(Date.now() + 7 * 60 * 60 * 1000).toISOString().slice(0, 7);
}

function clock(seconds: number): string {
  const s = Math.max(0, Math.floor(seconds));
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`;
}

const UUID_RE = /[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/i;

/** เรียงคิว: งานด่วนก่อน แล้วรอนานที่สุดก่อน */
function queueOrder(a: ListRow, b: ListRow): number {
  if (a.priority !== b.priority) return a.priority === 'urgent' ? -1 : 1;
  return (a.acceptedAt ?? '').localeCompare(b.acceptedAt ?? '');
}

function flagReason(flags: Flags, kind: 'low' | 'mismatch'): string {
  const hit = flags.reasons.find((r) => (kind === 'low' ? r.includes('ไม่แน่ใจ') : r.includes('ไม่ตรง')));
  if (hit) return hit;
  return kind === 'low'
    ? 'ไม่แน่ใจยอดรวม: ความมั่นใจของยอดรวมต่ำกว่า 0.90'
    : 'ยอดไม่ตรงรายการ: ผลรวมรายการต่างจากยอดรวมเกิน 1.00 บาท';
}

// ───────────────────────────── ฉบับร่างของฟอร์ม ─────────────────────────────

interface DraftItem {
  key: string;
  lineNo: number;
  name: string;
  price: string;
  removed: boolean;
  isNew: boolean;
}

interface Draft {
  merchant: string;
  receiptDate: string;
  total: string;
  categoryId: string;
  items: DraftItem[];
}

function draftFrom(r: Receipt): Draft {
  return {
    merchant: r.merchant ?? '',
    receiptDate: r.receiptDate ?? '',
    total: r.total ?? '',
    categoryId: r.categoryId ?? '',
    items: r.items.map((i) => ({
      key: `L${i.lineNo}`,
      lineNo: i.lineNo,
      name: i.name ?? '',
      price: i.price ?? '',
      removed: i.removed,
      isNew: false,
    })),
  };
}

/** body ของ PATCH (W14) เฉพาะช่องที่เปลี่ยนจริง · ไม่มีอะไรเปลี่ยน → null */
function buildPatch(r: Receipt, d: Draft): Record<string, unknown> | null {
  const body: Record<string, unknown> = {};
  if (d.merchant.trim() !== (r.merchant ?? '')) body.merchant = d.merchant.trim() || null;
  if (d.receiptDate !== (r.receiptDate ?? '')) body.receiptDate = d.receiptDate || null;
  if (!sameMoneyText(d.total, r.total)) body.total = d.total.trim() === '' ? null : d.total.trim();
  if (d.categoryId !== (r.categoryId ?? '')) body.categoryId = d.categoryId || null;

  const byLine = new Map(r.items.map((i) => [i.lineNo, i]));
  const items: Array<Record<string, unknown>> = [];
  for (const it of d.items) {
    if (it.isNew) {
      if (it.removed || (it.name.trim() === '' && it.price.trim() === '')) continue;
      items.push({ name: it.name.trim() || null, price: it.price.trim() === '' ? null : it.price.trim() });
      continue;
    }
    const orig = byLine.get(it.lineNo);
    if (!orig) continue;
    const change: Record<string, unknown> = { lineNo: it.lineNo };
    if (it.name.trim() !== (orig.name ?? '')) change.name = it.name.trim() || null;
    if (!sameMoneyText(it.price, orig.price)) change.price = it.price.trim() === '' ? null : it.price.trim();
    if (it.removed !== orig.removed) change.removed = it.removed;
    if (Object.keys(change).length > 1) items.push(change);
  }
  if (items.length) body.items = items;
  return Object.keys(body).length ? body : null;
}

// ส่วนของใบที่ใบติดธงต้องเปิดดูก่อนยืนยัน (FR-12 · 5 ช่องของ FR-03)
type Part = 'merchant' | 'date' | 'itemNames' | 'itemPrices' | 'total';
const PARTS: ReadonlyArray<{ key: Part; label: string }> = [
  { key: 'merchant', label: 'ชื่อร้าน' },
  { key: 'date', label: 'วันที่' },
  { key: 'itemNames', label: 'รายการสินค้า' },
  { key: 'itemPrices', label: 'ราคาแต่ละรายการ' },
  { key: 'total', label: 'ยอดรวม' },
];

const FIELD_LABEL: Record<string, string> = {
  merchant: 'ชื่อร้าน',
  receipt_date: 'วันที่',
  total: 'ยอดรวม',
  category_id: 'หมวดรายจ่าย',
  status: 'สถานะ',
};

function fieldLabel(field: string): string {
  if (FIELD_LABEL[field]) return FIELD_LABEL[field];
  const m = /^item\[(\d+)\](?:\.(name|price|removed))?$/.exec(field);
  if (m) {
    const part = m[2] === 'name' ? ' · ชื่อ' : m[2] === 'price' ? ' · ราคา' : m[2] === 'removed' ? ' · ลบ' : ' · เพิ่มใหม่';
    return `รายการบรรทัด ${m[1]}${part}`;
  }
  return field;
}

// ───────────────────────────── หน้าหลัก ─────────────────────────────

export default function ReviewPage() {
  return (
    <Suspense fallback={<p style={S.muted}>กำลังโหลด…</p>}>
      <ReviewRoot />
    </Suspense>
  );
}

function ReviewRoot() {
  const sp = useSearchParams();
  const pathname = usePathname() ?? '';
  const router = useRouter();
  const fromQuery = sp?.get('id') ?? sp?.get('receiptId') ?? null;
  const fromPath = /\/receipts\/([^/?#]+)/.exec(pathname)?.[1] ?? null;
  const id = fromQuery || (fromPath && UUID_RE.test(fromPath) ? fromPath : null);

  const [me, setMe] = useState<Me | null>(null);
  const [meError, setMeError] = useState<string | null>(null);

  const toLogin = useCallback(() => {
    const here = typeof window !== 'undefined' ? window.location.pathname + window.location.search : '/review';
    router.replace(`/login?next=${encodeURIComponent(here)}`);
  }, [router]);

  useEffect(() => {
    let alive = true;
    api<{ user: Me }>('/api/me')
      .then((r) => alive && setMe(r.user))
      .catch((e: unknown) => {
        if (!alive) return;
        if (e instanceof HttpError && e.status === 401) toLogin();
        else setMeError(errorText(e));
      });
    return () => {
      alive = false;
    };
  }, [toLogin]);

  if (meError) return <Shell><p style={S.errorBox} role="alert">{meError}</p></Shell>;
  if (!me) return <Shell><p style={S.muted}>กำลังโหลด…</p></Shell>;
  if (me.role === 'client') {
    return (
      <Shell>
        <p style={S.errorBox} role="alert" data-testid="review-forbidden">
          หน้านี้สำหรับสำนักงานบัญชีเท่านั้น ดูใบเสร็จของร้านได้ที่ <a href="/portal">หน้าลูกค้า</a>
        </p>
      </Shell>
    );
  }
  return (
    <Shell>
      {id ? <ReceiptReview key={id} id={id} me={me} onUnauthenticated={toLogin} /> : <ReviewQueue onUnauthenticated={toLogin} />}
    </Shell>
  );
}

function Shell({ children }: { children: ReactNode }) {
  return <main style={S.main}>{children}</main>;
}

// ───────────────────────────── คิวรอตรวจ ─────────────────────────────

function ReviewQueue({ onUnauthenticated }: { onUnauthenticated: () => void }) {
  const [flagged, setFlagged] = useState<ListRow[] | null>(null);
  const [normal, setNormal] = useState<ListRow[] | null>(null);
  const [counts, setCounts] = useState<{ flagged: number; normal: number; unreadable: number }>({
    flagged: 0,
    normal: 0,
    unreadable: 0,
  });
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setError(null);
    try {
      const [f, n, u] = await Promise.all([
        api<{ count: number; receipts: ListRow[] }>('/api/receipts?status=review&flagged=true&limit=1000'),
        api<{ count: number; receipts: ListRow[] }>('/api/receipts?status=review&flagged=false&limit=1000'),
        api<{ count: number }>('/api/receipts?status=unreadable&limit=1'),
      ]);
      setFlagged([...f.receipts].sort(queueOrder));
      setNormal([...n.receipts].sort(queueOrder));
      setCounts({ flagged: f.count, normal: n.count, unreadable: u.count });
    } catch (e) {
      if (e instanceof HttpError && e.status === 401) return onUnauthenticated();
      setError(errorText(e));
    }
  }, [onUnauthenticated]);

  useEffect(() => {
    void load();
  }, [load]);

  const first = flagged?.[0] ?? normal?.[0] ?? null;

  return (
    <section>
      <header style={S.headerRow}>
        <h1 style={S.h1}>ตรวจแก้ใบเสร็จ</h1>
        <div style={S.row}>
          <button type="button" style={S.btn} onClick={() => void load()} data-testid="review-refresh-button">
            รีเฟรช
          </button>
          {first && (
            <a href={`/review?id=${first.id}`} style={{ ...S.btn, ...S.btnPrimary }} data-testid="review-start-button">
              เริ่มตรวจใบแรก →
            </a>
          )}
        </div>
      </header>
      <p style={S.muted}>
        ใบติดธงต้องตรวจทุกช่อง · ใบปกติตรวจยอดรวมเทียบกับรูปช่องเดียว · อ่านไม่ได้{' '}
        <a href="/unreadable" data-testid="review-unreadable-link">
          {counts.unreadable} ใบ
        </a>
      </p>
      {error && (
        <p style={S.errorBox} role="alert">
          {error}
        </p>
      )}

      <QueueTable
        title="ใบติดธง ระบบไม่แน่ใจ"
        tone="flag"
        rows={flagged}
        count={counts.flagged}
        testid="review-flagged"
        showReasons
      />
      <QueueTable title="ใบปกติ" tone="ok" rows={normal} count={counts.normal} testid="review-normal" />
    </section>
  );
}

function QueueTable(props: {
  title: string;
  tone: 'flag' | 'ok';
  rows: ListRow[] | null;
  count: number;
  testid: string;
  showReasons?: boolean;
}) {
  const { title, tone, rows, count, testid, showReasons } = props;
  return (
    <div style={{ ...S.card, ...(tone === 'flag' ? S.cardFlag : S.cardOk) }}>
      <h2 style={S.h2}>
        {tone === 'flag' ? '⚑ ' : '✓ '}
        {title} <span data-testid={`${testid}-count`}>{count}</span> ใบ
      </h2>
      {rows === null ? (
        <p style={S.muted}>กำลังโหลด…</p>
      ) : rows.length === 0 ? (
        <p style={S.muted}>ไม่มีใบรอตรวจ</p>
      ) : (
        <table style={S.table} data-testid={`${testid}-table`}>
          <thead>
            <tr>
              <th style={S.th}>ไฟล์</th>
              <th style={S.th}>ลูกค้า</th>
              <th style={S.th}>ร้านที่อ่านได้</th>
              <th style={{ ...S.th, textAlign: 'right' }}>ยอดรวม</th>
              {showReasons && <th style={S.th}>เหตุผลของธง</th>}
              <th style={S.th}>รับเมื่อ</th>
              <th style={S.th} />
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id} data-testid={`review-row-${r.id}`}>
                <td style={S.td}>
                  {r.priority === 'urgent' && <span style={S.badgeUrgent}>ด่วน</span>} {r.fileName}
                </td>
                <td style={S.td}>{r.clientName}</td>
                <td style={S.td}>{r.merchant ?? '—'}</td>
                <td style={{ ...S.td, textAlign: 'right', fontVariantNumeric: 'tabular-nums' }}>{showMoney(r.total)}</td>
                {showReasons && (
                  <td style={S.td} data-testid={`review-flag-reasons-${r.id}`}>
                    {r.flags.reasons.join(' · ') || '—'}
                  </td>
                )}
                <td style={S.td}>{showDateTime(r.acceptedAt)}</td>
                <td style={S.td}>
                  <a href={`/review?id=${r.id}`} data-testid={`review-open-link-${r.id}`}>
                    ตรวจ →
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

// ───────────────────────────── ตรวจ 1 ใบ ─────────────────────────────

function ReceiptReview({ id, me, onUnauthenticated }: { id: string; me: Me; onUnauthenticated: () => void }) {
  const router = useRouter();
  const [receipt, setReceipt] = useState<Receipt | null>(null);
  const [draft, setDraft] = useState<Draft | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [categories, setCategories] = useState<Category[]>([]);
  const [visited, setVisited] = useState<Set<Part>>(() => new Set());
  const [totalChecked, setTotalChecked] = useState(false);
  const [busy, setBusy] = useState<null | 'save' | 'confirm' | 'reopen' | 'next'>(null);
  const [confirmError, setConfirmError] = useState<string | null>(null);
  const [saveNote, setSaveNote] = useState<string | null>(null);
  const [nextNote, setNextNote] = useState<string | null>(null);
  const [showHistory, setShowHistory] = useState(false);
  const [history, setHistory] = useState<HistoryResponse | null>(null);
  const [historyError, setHistoryError] = useState<string | null>(null);
  const [reopenReason, setReopenReason] = useState('');
  const [openedAt, setOpenedAt] = useState<number>(() => Date.now());
  const [now, setNow] = useState<number>(() => Date.now());
  const formRef = useRef<HTMLDivElement>(null);
  const totalRef = useRef<HTMLInputElement>(null);
  const merchantRef = useRef<HTMLInputElement>(null);
  const categoryRef = useRef<HTMLSelectElement>(null);
  const dateRef = useRef<HTMLInputElement>(null);

  /** รับใบจาก API แล้วตั้งฟอร์มใหม่ (หลังโหลด · บันทึก · ยืนยัน · เปิดกลับ) */
  const applyReceipt = useCallback((r: Receipt) => {
    setReceipt(r);
    setDraft(draftFrom(r));
  }, []);

  const handleAuth = useCallback(
    (e: unknown): boolean => {
      if (e instanceof HttpError && e.status === 401) {
        onUnauthenticated();
        return true;
      }
      return false;
    },
    [onUnauthenticated],
  );

  // W12: เปิดใบ — server บันทึก review_opened_at (เริ่มจับเวลา FR-31 · หลักฐาน FR-12)
  const loadReceipt = useCallback(async () => {
    const res = await api<{ receipt: Receipt }>(`/api/receipts/${encodeURIComponent(id)}`);
    return res.receipt;
  }, [id]);

  useEffect(() => {
    let alive = true;
    setLoadError(null);
    loadReceipt()
      .then((r) => {
        if (!alive) return;
        applyReceipt(r);
        setOpenedAt(Date.now());
        setVisited(new Set());
        setTotalChecked(false);
      })
      .catch((e: unknown) => {
        if (!alive || handleAuth(e)) return;
        setLoadError(errorText(e));
      });
    return () => {
      alive = false;
    };
  }, [loadReceipt, applyReceipt, handleAuth]);

  // รายชื่อหมวด (W19 คืนทุกหมวดแม้ยอด 0.00)
  const clientId = receipt?.clientId ?? null;
  useEffect(() => {
    if (!clientId) return;
    let alive = true;
    api<{ categories: Category[] }>(
      `/api/reports/categories?clientId=${encodeURIComponent(clientId)}&month=${bangkokMonth()}`,
    )
      .then((r) => alive && setCategories(r.categories.map((c) => ({ id: c.id, name: c.name }))))
      .catch(() => undefined);
    return () => {
      alive = false;
    };
  }, [clientId]);

  const editable = !!receipt?.permissions.canEdit;
  const flagged = !!receipt?.flags.flagged;
  const confirmed = receipt?.status === 'confirmed';

  // นาฬิกาเวลาตรวจ (NFR-09)
  useEffect(() => {
    if (!editable) return;
    const t = window.setInterval(() => setNow(Date.now()), 1000);
    return () => window.clearInterval(t);
  }, [editable]);

  // โฟกัสแรก: ใบปกติ → ยอดรวม (ตรวจช่องเดียว) · ใบติดธง → ชื่อร้าน (ไล่ตรวจทุกช่อง)
  const focusedFor = useRef<string | null>(null);
  useEffect(() => {
    if (!receipt || !editable || focusedFor.current === receipt.id) return;
    focusedFor.current = receipt.id;
    window.setTimeout(() => (receipt.flags.flagged ? merchantRef.current : totalRef.current)?.focus(), 0);
  }, [receipt, editable]);

  const patch = useMemo(() => (receipt && draft ? buildPatch(receipt, draft) : null), [receipt, draft]);
  const dirty = patch !== null;

  // เตือนก่อนออกจากหน้าเมื่อยังไม่บันทึก
  useEffect(() => {
    if (!dirty || !editable) return;
    const h = (e: BeforeUnloadEvent) => {
      e.preventDefault();
      e.returnValue = '';
    };
    window.addEventListener('beforeunload', h);
    return () => window.removeEventListener('beforeunload', h);
  }, [dirty, editable]);

  // ── ค่าที่คำนวณจากฉบับร่าง ──
  const activeItems = draft ? draft.items.filter((i) => !i.removed) : [];
  const itemsSumSatang = activeItems.reduce((n, i) => {
    const s = moneySatang(i.price);
    return n + (s === null || Number.isNaN(s) ? 0 : s);
  }, 0);
  const totalSatang = draft ? moneySatang(draft.total) : null;
  const totalBad = totalSatang !== null && Number.isNaN(totalSatang);
  const totalOk = totalSatang !== null && !Number.isNaN(totalSatang) && totalSatang >= LIMITS.MIN_CONFIRM_TOTAL_SATANG;
  const anyBadMoney = !!draft && (totalBad || draft.items.some((i) => !i.removed && isBadMoney(i.price)));
  const liveDiff =
    totalSatang !== null && !Number.isNaN(totalSatang) && activeItems.length > 0 ? itemsSumSatang - totalSatang : null;
  const liveMismatch = liveDiff !== null && Math.abs(liveDiff) > LIMITS.MAX_ITEMS_DIFF_SATANG;

  const effectiveVisited = useMemo(() => {
    const v = new Set(visited);
    if (activeItems.length === 0) {
      v.add('itemNames');
      v.add('itemPrices');
    }
    return v;
  }, [visited, activeItems.length]);
  const unviewed = flagged ? PARTS.filter((p) => !effectiveVisited.has(p.key)) : [];

  const canPressConfirm =
    editable && !!receipt?.permissions.canConfirm && totalOk && totalChecked && unviewed.length === 0 && !anyBadMoney && busy === null;

  const blockers: string[] = [];
  if (editable) {
    if (totalBad) blockers.push('ยอดรวมต้องเป็นตัวเลข ทศนิยมไม่เกิน 2 ตำแหน่ง');
    else if (!totalOk) blockers.push('ยอดรวมต้องตั้งแต่ 0.01 บาทขึ้นไป (BR-06)');
    if (!totalChecked) blockers.push('ติ๊ก "เทียบยอดรวมกับรูปแล้ว"');
    if (unviewed.length) blockers.push(`ใบติดธง: เปิดดูให้ครบทุกช่อง (ยังไม่ได้ดู: ${unviewed.map((p) => p.label).join(' · ')})`);
    if (anyBadMoney && !totalBad) blockers.push('ราคารายการต้องเป็นตัวเลข ทศนิยมไม่เกิน 2 ตำแหน่ง');
    if (draft && !draft.categoryId) blockers.push('เลือกหมวดรายจ่าย');
    if (draft && !draft.receiptDate) blockers.push('กรอกวันที่บนใบ');
  }

  const markVisited = useCallback((p: Part) => {
    setVisited((prev) => (prev.has(p) ? prev : new Set(prev).add(p)));
  }, []);

  const update = useCallback((fn: (d: Draft) => Draft) => {
    setDraft((d) => (d ? fn(d) : d));
    setSaveNote(null);
    setConfirmError(null);
  }, []);

  const refreshHistory = useCallback(async () => {
    setHistoryError(null);
    try {
      setHistory(await api<HistoryResponse>(`/api/receipts/${encodeURIComponent(id)}/history`));
    } catch (e) {
      if (handleAuth(e)) return;
      setHistoryError(errorText(e));
    }
  }, [id, handleAuth]);

  // ── บันทึก (W14) ──
  const save = useCallback(async (): Promise<boolean> => {
    if (!receipt || !draft || !patch) return true;
    if (anyBadMoney) {
      setSaveNote('บันทึกไม่ได้: จำนวนเงินต้องเป็นตัวเลข ทศนิยมไม่เกิน 2 ตำแหน่ง');
      return false;
    }
    const res = await api<{ changed: string[]; receipt: Receipt }>(`/api/receipts/${encodeURIComponent(receipt.id)}`, {
      method: 'PATCH',
      body: JSON.stringify(patch),
    });
    applyReceipt(res.receipt);
    setSaveNote(res.changed.length ? `บันทึกแล้ว ${res.changed.length} ช่อง` : 'ไม่มีช่องที่เปลี่ยน');
    if (showHistory) void refreshHistory();
    return true;
  }, [receipt, draft, patch, anyBadMoney, applyReceipt, showHistory, refreshHistory]);

  const onSave = useCallback(async () => {
    if (busy) return;
    setBusy('save');
    setConfirmError(null);
    try {
      await save();
    } catch (e) {
      if (!handleAuth(e)) setSaveNote(`บันทึกไม่สำเร็จ: ${errorText(e)}`);
    } finally {
      setBusy(null);
    }
  }, [busy, save, handleAuth]);

  // ── ยืนยัน (PATCH ก่อน แล้ว W15) ──
  const onConfirm = useCallback(async () => {
    if (!receipt || !draft || !canPressConfirm) return;
    setConfirmError(null);
    if (!draft.categoryId) {
      setConfirmError(FALLBACK_MESSAGES.category_required);
      categoryRef.current?.focus();
      return;
    }
    if (!draft.receiptDate) {
      setConfirmError(FALLBACK_MESSAGES.date_required);
      dateRef.current?.focus();
      return;
    }
    setBusy('confirm');
    try {
      // บันทึกค่าที่แก้ก่อน เพื่อให้ร่องรอยการแก้ (NFR-10) อยู่แม้การยืนยันไม่ผ่าน
      if (!(await save())) return;
      const res = await api<{ ok: boolean; receipt: Receipt }>(
        `/api/receipts/${encodeURIComponent(receipt.id)}/confirm`,
        { method: 'POST', body: JSON.stringify({ totalChecked: true, categoryId: draft.categoryId }) },
      );
      applyReceipt(res.receipt);
      setSaveNote(null);
      if (showHistory) void refreshHistory();
    } catch (e) {
      if (handleAuth(e)) return;
      setConfirmError(errorText(e));
      if (e instanceof HttpError && e.code === 'review_not_opened') {
        // เปิดใบใหม่ให้ server บันทึกการเปิดดู แล้วให้พนักงานกดยืนยันอีกครั้ง
        try {
          applyReceipt(await loadReceipt());
        } catch {
          /* แสดงข้อความเดิม */
        }
      } else if (e instanceof HttpError && e.code === 'not_editable') {
        try {
          applyReceipt(await loadReceipt());
        } catch {
          /* แสดงข้อความเดิม */
        }
      }
    } finally {
      setBusy(null);
    }
  }, [receipt, draft, canPressConfirm, save, applyReceipt, showHistory, refreshHistory, handleAuth, loadReceipt]);

  // ── เปิดใบกลับ (W16 · หัวหน้าเท่านั้น) ──
  const onReopen = useCallback(async () => {
    if (!receipt || busy) return;
    setBusy('reopen');
    setConfirmError(null);
    try {
      await api(`/api/receipts/${encodeURIComponent(receipt.id)}/reopen`, {
        method: 'POST',
        body: JSON.stringify(reopenReason.trim() ? { reason: reopenReason.trim() } : {}),
      });
      setReopenReason('');
      applyReceipt(await loadReceipt()); // เปิดใหม่ = เริ่มจับเวลาตรวจใหม่
      setOpenedAt(Date.now());
      setVisited(new Set());
      setTotalChecked(false);
      focusedFor.current = null;
      if (showHistory) void refreshHistory();
    } catch (e) {
      if (!handleAuth(e)) setConfirmError(errorText(e));
    } finally {
      setBusy(null);
    }
  }, [receipt, busy, reopenReason, applyReceipt, loadReceipt, showHistory, refreshHistory, handleAuth]);

  // ── ใบถัดไป: กลุ่มเดียวกันก่อน (ธง/ปกติ) · ด่วนก่อน · รอนานก่อน ──
  const onNext = useCallback(async () => {
    if (busy) return;
    if (dirty && editable && !window.confirm('ยังไม่ได้บันทึกค่าที่แก้ ต้องการข้ามไปใบถัดไปหรือไม่')) return;
    setBusy('next');
    setNextNote(null);
    try {
      const groups = flagged ? ['true', 'false'] : ['false', 'true'];
      for (const g of groups) {
        const res = await api<{ receipts: ListRow[] }>(`/api/receipts?status=review&flagged=${g}&limit=1000`);
        const next = [...res.receipts].sort(queueOrder).find((r) => r.id !== id);
        if (next) {
          router.push(`/review?id=${next.id}`);
          return;
        }
      }
      setNextNote('ไม่มีใบรอตรวจแล้ว');
    } catch (e) {
      if (!handleAuth(e)) setNextNote(errorText(e));
    } finally {
      setBusy(null);
    }
  }, [busy, dirty, editable, flagged, id, router, handleAuth]);

  // ── คีย์ลัด ──
  const keys = useRef({ onConfirm, onSave, onNext, canPressConfirm, editable, confirmed });
  keys.current = { onConfirm, onSave, onNext, canPressConfirm, editable, confirmed };
  useEffect(() => {
    const h = (e: KeyboardEvent) => {
      const k = keys.current;
      const mod = e.ctrlKey || e.metaKey;
      if (mod && e.key === 'Enter') {
        e.preventDefault();
        if (k.canPressConfirm) void k.onConfirm();
      } else if (mod && (e.key === 's' || e.key === 'S')) {
        e.preventDefault();
        if (k.editable) void k.onSave();
      } else if (e.altKey && e.key === 'ArrowRight') {
        e.preventDefault();
        void k.onNext();
      }
    };
    window.addEventListener('keydown', h);
    return () => window.removeEventListener('keydown', h);
  }, []);

  /** Enter ในช่องกรอก = ไปช่องถัดไปตามลำดับตรวจ */
  const flowKey = useCallback((e: ReactKeyboardEvent<HTMLElement>) => {
    if (e.key !== 'Enter' || e.ctrlKey || e.metaKey || e.altKey || e.shiftKey) return;
    const root = formRef.current;
    if (!root) return;
    const list = Array.from(root.querySelectorAll<HTMLElement>('[data-flow]:not([disabled])'));
    const i = list.indexOf(e.currentTarget);
    if (i >= 0 && i + 1 < list.length) {
      e.preventDefault();
      list[i + 1].focus();
      if (list[i + 1] instanceof HTMLInputElement) (list[i + 1] as HTMLInputElement).select?.();
    }
  }, []);

  const selectOnFocus = (e: FocusEvent<HTMLInputElement>) => {
    if (e.currentTarget.type !== 'date') e.currentTarget.select();
  };

  // ───────────── แสดงผล ─────────────

  if (loadError) {
    return (
      <section>
        <BackLink />
        <p style={S.errorBox} role="alert" data-testid="review-load-error">
          {loadError}
        </p>
      </section>
    );
  }
  if (!receipt || !draft) return <p style={S.muted}>กำลังเปิดใบเสร็จ…</p>;

  const origItems = new Map(receipt.original.items.map((i) => [i.lineNo, i]));
  const reviewSecondsLive = Math.round((now - openedAt) / 1000);
  const nextLineNo = draft.items.reduce((m, i) => Math.max(m, i.lineNo), 0) + 1;
  const changedMark = (changed: boolean) => (changed ? <span style={S.changed}>แก้แล้ว</span> : null);
  const inputStyle = (highlight: boolean, bad = false): CSSProperties => ({
    ...S.input,
    ...(highlight ? S.inputFocusTarget : null),
    ...(bad ? S.inputBad : null),
  });

  return (
    <section>
      <header style={S.headerRow}>
        <div>
          <BackLink />
          <h1 style={S.h1}>
            ตรวจใบเสร็จ <span style={S.fileName}>{receipt.fileName}</span>
          </h1>
          <p style={S.muted}>
            {receipt.clientName}
            {receipt.priority === 'urgent' && <span style={{ ...S.badgeUrgent, marginLeft: 8 }}>งานด่วน</span>} · รับเมื่อ{' '}
            {showDateTime(receipt.acceptedAt)} · สถานะ{' '}
            <strong data-testid="receipt-status" data-status={receipt.status}>
              {receipt.statusLabel}
            </strong>
            {receipt.enteredManually && ' · พิมพ์เอง'}
          </p>
        </div>
        <div style={S.timerBox} title="NFR-09: เฉลี่ยต้องน้อยกว่า 120 วินาทีต่อใบ · เป้าหมายทีม ≤ 40 วินาที">
          {confirmed && receipt.reviewSeconds !== null ? (
            <span data-testid="review-seconds">ใช้เวลาตรวจ {clock(receipt.reviewSeconds)} นาที</span>
          ) : editable ? (
            <span
              data-testid="review-timer"
              style={{ color: reviewSecondsLive > 120 ? '#b42318' : reviewSecondsLive > 40 ? '#b54708' : '#067647' }}
            >
              เวลาตรวจ {clock(reviewSecondsLive)}
            </span>
          ) : null}
        </div>
      </header>

      {/* ── ธง (FR-09) แยกให้เห็นจากใบปกติ ── */}
      {flagged ? (
        <div style={{ ...S.card, ...S.cardFlag }} role="note" data-testid="flag-panel">
          <strong>⚑ ใบติดธง ระบบไม่แน่ใจ — ตรวจทุกช่องเทียบกับรูป</strong>
          <ul style={S.flagList}>
            {receipt.flags.lowConfidence && (
              <li data-testid="flag-low-confidence">
                {flagReason(receipt.flags, 'low')}
                {receipt.totalConfidence !== null && ` (ความมั่นใจ ${Number(receipt.totalConfidence).toFixed(4)})`}
              </li>
            )}
            {receipt.flags.mismatch && <li data-testid="flag-mismatch">{flagReason(receipt.flags, 'mismatch')}</li>}
          </ul>
          {editable && (
            <p style={S.small} data-testid="flag-viewed">
              ดูแล้ว:{' '}
              {PARTS.map((p) => (
                <span key={p.key} style={effectiveVisited.has(p.key) ? S.chipDone : S.chipTodo}>
                  {effectiveVisited.has(p.key) ? '✓ ' : '○ '}
                  {p.label}
                </span>
              ))}
            </p>
          )}
        </div>
      ) : receipt.status === 'unreadable' ? (
        <div style={{ ...S.card, ...S.cardFlag }} role="note" data-testid="unreadable-panel">
          <strong>อ่านไม่ได้ ให้คนพิมพ์เอง</strong>
          {receipt.unreadableReason && <span> — {receipt.unreadableReason}</span>}
          <p style={S.small}>พิมพ์ 5 ช่องจากรูป แล้วยืนยันด้วยกฎเดียวกับใบปกติ</p>
        </div>
      ) : (
        <div style={{ ...S.card, ...S.cardOk }} data-testid="flag-none">
          ✓ ใบปกติ — ตรวจยอดรวมเทียบกับรูปช่องเดียวแล้วยืนยันได้
          {receipt.totalConfidence !== null && (
            <span style={S.small}> · ความมั่นใจยอดรวม {Number(receipt.totalConfidence).toFixed(4)}</span>
          )}
        </div>
      )}

      <div style={S.split}>
        {/* ── รูป ── */}
        <ReceiptImage receipt={receipt} />

        {/* ── 5 ช่อง ── */}
        <div ref={formRef} style={S.formCol}>
          <Field label="ชื่อร้าน" original={receipt.original.merchant ?? '—'} originalTestId="original-merchant" mark={changedMark(draft.merchant.trim() !== (receipt.original.merchant ?? ''))}>
            <input
              ref={merchantRef}
              data-testid="field-merchant-input"
              data-flow
              style={inputStyle(flagged)}
              value={draft.merchant}
              disabled={!editable}
              onFocus={() => markVisited('merchant')}
              onKeyDown={flowKey}
              onChange={(e) => update((d) => ({ ...d, merchant: e.target.value }))}
              aria-label="ชื่อร้าน"
              autoComplete="off"
            />
          </Field>

          <Field label="วันที่บนใบ" original={showDate(receipt.original.receiptDate)} originalTestId="original-date" mark={changedMark(draft.receiptDate !== (receipt.original.receiptDate ?? ''))}>
            <input
              ref={dateRef}
              type="date"
              data-testid="field-date-input"
              data-flow
              style={inputStyle(flagged)}
              value={draft.receiptDate}
              disabled={!editable}
              onFocus={() => markVisited('date')}
              onKeyDown={flowKey}
              onChange={(e) => update((d) => ({ ...d, receiptDate: e.target.value }))}
              aria-label="วันที่บนใบ"
            />
          </Field>

          <div style={S.fieldBlock}>
            <div style={S.fieldHead}>
              <span style={S.label}>รายการสินค้าและราคา</span>
              <span style={S.small}>
                ผลรวมรายการ{' '}
                <strong data-testid="items-sum" style={{ fontVariantNumeric: 'tabular-nums' }}>
                  {formatBaht(itemsSumSatang)}
                </strong>{' '}
                บาท
                {liveDiff !== null && (
                  <span style={liveMismatch ? S.warnText : S.okText} data-testid="items-diff">
                    {' '}
                    · ต่างจากยอดรวม {formatBaht(liveDiff)}
                    {liveMismatch ? ' (เกิน 1.00 บาท)' : ''}
                  </span>
                )}
              </span>
            </div>
            <table style={S.table}>
              <thead>
                <tr>
                  <th style={{ ...S.th, width: 36 }}>#</th>
                  <th style={S.th}>รายการ</th>
                  <th style={{ ...S.th, width: 120, textAlign: 'right' }}>ราคา</th>
                  <th style={{ ...S.th, width: 72 }} />
                </tr>
              </thead>
              <tbody>
                {draft.items.length === 0 && (
                  <tr>
                    <td colSpan={4} style={{ ...S.td, ...S.muted }}>
                      ไม่มีรายการ
                    </td>
                  </tr>
                )}
                {draft.items.map((it) => {
                  const o = origItems.get(it.lineNo);
                  const priceBad = !it.removed && isBadMoney(it.price);
                  return (
                    <tr key={it.key} style={it.removed ? S.rowRemoved : undefined} data-testid={`item-row-${it.lineNo}`}>
                      <td style={S.td}>{it.lineNo}</td>
                      <td style={S.td}>
                        <input
                          data-testid={`item-name-input-${it.lineNo}`}
                          data-flow
                          style={inputStyle(flagged)}
                          value={it.name}
                          disabled={!editable || it.removed}
                          onFocus={() => markVisited('itemNames')}
                          onKeyDown={flowKey}
                          onChange={(e) => {
                            const v = e.target.value;
                            update((d) => ({ ...d, items: d.items.map((x) => (x.key === it.key ? { ...x, name: v } : x)) }));
                          }}
                          aria-label={`ชื่อรายการบรรทัด ${it.lineNo}`}
                          autoComplete="off"
                        />
                        {o && (o.name ?? '') !== it.name.trim() && (
                          <div style={S.orig}>ระบบอ่าน: {o.name ?? '—'}</div>
                        )}
                        {it.isNew && <div style={S.orig}>บรรทัดใหม่ (ยังไม่บันทึก)</div>}
                      </td>
                      <td style={S.td}>
                        <input
                          data-testid={`item-price-input-${it.lineNo}`}
                          data-flow
                          inputMode="decimal"
                          style={{ ...inputStyle(flagged, priceBad), textAlign: 'right' }}
                          value={it.price}
                          disabled={!editable || it.removed}
                          onFocus={(e) => {
                            markVisited('itemPrices');
                            selectOnFocus(e);
                          }}
                          onKeyDown={flowKey}
                          onChange={(e) => {
                            const v = e.target.value;
                            update((d) => ({ ...d, items: d.items.map((x) => (x.key === it.key ? { ...x, price: v } : x)) }));
                          }}
                          aria-label={`ราคาบรรทัด ${it.lineNo}`}
                          autoComplete="off"
                        />
                        {o && !sameMoneyText(it.price, o.price) && (
                          <div style={{ ...S.orig, textAlign: 'right' }}>ระบบอ่าน: {showMoney(o.price)}</div>
                        )}
                      </td>
                      <td style={S.td}>
                        {editable && (
                          <button
                            type="button"
                            style={S.btnSmall}
                            data-testid={`item-remove-button-${it.lineNo}`}
                            onClick={() =>
                              update((d) => ({
                                ...d,
                                items: it.isNew
                                  ? d.items.filter((x) => x.key !== it.key)
                                  : d.items.map((x) => (x.key === it.key ? { ...x, removed: !x.removed } : x)),
                              }))
                            }
                          >
                            {it.removed ? 'คืน' : 'ลบ'}
                          </button>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
            {editable && (
              <button
                type="button"
                style={{ ...S.btnSmall, marginTop: 6 }}
                data-testid="item-add-button"
                onClick={() => {
                  const key = `N${Date.now()}${Math.random().toString(36).slice(2, 6)}`;
                  update((d) => ({
                    ...d,
                    items: [...d.items, { key, lineNo: nextLineNo, name: '', price: '', removed: false, isNew: true }],
                  }));
                  window.setTimeout(() => {
                    formRef.current?.querySelector<HTMLInputElement>(`[data-testid="item-name-input-${nextLineNo}"]`)?.focus();
                  }, 0);
                }}
              >
                + เพิ่มรายการ
              </button>
            )}
          </div>

          <Field
            label="ยอดรวม (บาท)"
            original={showMoney(receipt.original.total)}
            originalTestId="original-total"
            mark={changedMark(!sameMoneyText(draft.total, receipt.original.total))}
            emphasis
          >
            <input
              ref={totalRef}
              data-testid="field-total-input"
              data-flow
              inputMode="decimal"
              style={{ ...inputStyle(true, totalBad), ...S.totalInput }}
              value={draft.total}
              disabled={!editable}
              onFocus={(e) => {
                markVisited('total');
                selectOnFocus(e);
              }}
              onKeyDown={flowKey}
              onChange={(e) => update((d) => ({ ...d, total: e.target.value }))}
              aria-label="ยอดรวม"
              aria-invalid={totalBad || (editable && !totalOk)}
              autoComplete="off"
            />
            {editable && draft.total.trim() !== '' && !totalBad && !totalOk && (
              <div style={S.warnText}>ยอดรวมต้องตั้งแต่ 0.01 บาทขึ้นไปจึงยืนยันได้</div>
            )}
          </Field>

          <Field label="หมวดรายจ่าย">
            <select
              ref={categoryRef}
              data-testid="category-select"
              data-flow
              style={S.input}
              value={draft.categoryId}
              disabled={!editable}
              onKeyDown={flowKey}
              onChange={(e) => update((d) => ({ ...d, categoryId: e.target.value }))}
              aria-label="หมวดรายจ่าย"
            >
              <option value="">— เลือกหมวด —</option>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
              {receipt.categoryId && !categories.some((c) => c.id === receipt.categoryId) && (
                <option value={receipt.categoryId}>{receipt.categoryName ?? 'หมวดเดิม'}</option>
              )}
            </select>
          </Field>

          {/* ── ยืนยัน (FR-12 · BR-06) ── */}
          {editable && (
            <div style={S.actionBox}>
              <label style={S.checkLabel}>
                <input
                  type="checkbox"
                  data-testid="total-checked-checkbox"
                  data-flow
                  checked={totalChecked}
                  onChange={(e) => {
                    setTotalChecked(e.target.checked);
                    setConfirmError(null);
                  }}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.ctrlKey && !e.metaKey) {
                      e.preventDefault();
                      setTotalChecked((v) => !v);
                    }
                  }}
                  style={{ width: 18, height: 18 }}
                />
                เทียบยอดรวมกับรูปแล้ว
              </label>
              <div style={S.row}>
                <button
                  type="button"
                  data-testid="save-button"
                  style={S.btn}
                  disabled={!dirty || busy !== null}
                  onClick={() => void onSave()}
                  title="Ctrl/⌘ + S"
                >
                  {busy === 'save' ? 'กำลังบันทึก…' : 'บันทึก'}
                </button>
                <button
                  type="button"
                  data-testid="confirm-button"
                  style={{ ...S.btn, ...S.btnPrimary, ...(canPressConfirm ? null : S.btnDisabled) }}
                  disabled={!canPressConfirm}
                  onClick={() => void onConfirm()}
                  title="Ctrl/⌘ + Enter"
                >
                  {busy === 'confirm' ? 'กำลังยืนยัน…' : 'ยืนยัน'}
                </button>
                <button type="button" style={S.btnGhost} onClick={() => void onNext()} disabled={busy !== null} data-testid="next-button">
                  ข้าม → ใบถัดไป
                </button>
              </div>
              {saveNote && (
                <p style={S.small} role="status" data-testid="save-status">
                  {saveNote}
                </p>
              )}
              {confirmError && (
                <p style={S.errorBox} role="alert" data-testid="confirm-error">
                  {confirmError}
                </p>
              )}
              {blockers.length > 0 && (
                <ul style={S.blockers} data-testid="confirm-blockers">
                  {blockers.map((b) => (
                    <li key={b}>{b}</li>
                  ))}
                </ul>
              )}
              <p style={S.hint}>Enter = ช่องถัดไป · Ctrl/⌘+Enter = ยืนยัน · Ctrl/⌘+S = บันทึก · Alt+→ = ใบถัดไป</p>
            </div>
          )}

          {!editable && !confirmed && (
            <p style={S.noteBox} data-testid="review-readonly">
              {me.role === 'owner'
                ? 'เจ้าของสำนักงานดูได้อย่างเดียว'
                : receipt.status === 'queued' || receipt.status === 'processing'
                  ? 'ใบนี้ยังอ่านไม่เสร็จ ยังตรวจไม่ได้'
                  : 'ใบนี้แก้ไม่ได้'}
            </p>
          )}

          {/* ── ยืนยันแล้ว (FR-13) ── */}
          {confirmed && (
            <div style={{ ...S.card, ...S.cardOk }}>
              <p data-testid="confirmed-by" style={{ margin: 0 }}>
                ยืนยันโดย <strong>{receipt.confirmedBy ?? '—'}</strong> เมื่อ {showDateTime(receipt.confirmedAt)}
              </p>
              <div style={{ ...S.row, marginTop: 8 }}>
                {me.role !== 'owner' && (
                  <button type="button" style={{ ...S.btn, ...S.btnPrimary }} onClick={() => void onNext()} disabled={busy !== null} data-testid="next-button">
                    {busy === 'next' ? 'กำลังหา…' : 'ตรวจใบถัดไป →'}
                  </button>
                )}
                {receipt.permissions.canReopen && (
                  <>
                    <input
                      style={{ ...S.input, maxWidth: 260 }}
                      placeholder="เหตุผลที่เปิดกลับ (ไม่ใส่ก็ได้)"
                      value={reopenReason}
                      onChange={(e) => setReopenReason(e.target.value)}
                      data-testid="reopen-reason-input"
                    />
                    <button type="button" style={S.btn} onClick={() => void onReopen()} disabled={busy !== null} data-testid="reopen-button">
                      {busy === 'reopen' ? 'กำลังเปิดกลับ…' : 'เปิดใบกลับเป็นรอตรวจ'}
                    </button>
                  </>
                )}
              </div>
              {confirmError && (
                <p style={S.errorBox} role="alert" data-testid="confirm-error">
                  {confirmError}
                </p>
              )}
            </div>
          )}
          {nextNote && (
            <p style={S.noteBox} role="status" data-testid="next-status">
              {nextNote} · <a href="/review">กลับคิวรอตรวจ</a>
            </p>
          )}

          {/* ── ประวัติการแก้ (FR-14 · FR-15 · NFR-10) ── */}
          <div style={{ marginTop: 16 }}>
            <button
              type="button"
              style={S.btnGhost}
              data-testid="history-button"
              onClick={() => {
                const open = !showHistory;
                setShowHistory(open);
                if (open) void refreshHistory();
              }}
            >
              {showHistory ? 'ซ่อนประวัติการแก้' : 'ดูค่าเดิมและประวัติการแก้'}
            </button>
            {showHistory && (
              <HistoryPanel history={history} error={historyError} categories={categories} receipt={receipt} />
            )}
          </div>
        </div>
      </div>
    </section>
  );
}

function BackLink() {
  return (
    <a href="/review" style={S.back} data-testid="review-back-link">
      ← คิวรอตรวจ
    </a>
  );
}

function Field(props: {
  label: string;
  original?: string;
  originalTestId?: string;
  mark?: ReactNode;
  emphasis?: boolean;
  children: ReactNode;
}) {
  return (
    <div style={{ ...S.fieldBlock, ...(props.emphasis ? S.fieldEmphasis : null) }}>
      <div style={S.fieldHead}>
        <span style={S.label}>
          {props.label} {props.mark}
        </span>
        {props.originalTestId && (
          <span style={S.small}>
            ระบบอ่าน: <span data-testid={props.originalTestId}>{props.original}</span>
          </span>
        )}
      </div>
      {props.children}
    </div>
  );
}

function ReceiptImage({ receipt }: { receipt: Receipt }) {
  const [zoom, setZoom] = useState(1);
  const [rotate, setRotate] = useState(0);
  const [missing, setMissing] = useState(false);
  const isPdf = receipt.mimeType === 'application/pdf';
  return (
    <div style={S.imageCol}>
      <div style={S.imageTools}>
        {!isPdf && (
          <>
            <button type="button" style={S.btnSmall} onClick={() => setZoom((z) => Math.max(0.5, +(z - 0.25).toFixed(2)))} aria-label="ย่อรูป">
              −
            </button>
            <span style={S.small}>{Math.round(zoom * 100)}%</span>
            <button type="button" style={S.btnSmall} onClick={() => setZoom((z) => Math.min(4, +(z + 0.25).toFixed(2)))} aria-label="ขยายรูป">
              +
            </button>
            <button type="button" style={S.btnSmall} onClick={() => setZoom(1)}>
              พอดี
            </button>
            <button type="button" style={S.btnSmall} onClick={() => setRotate((r) => (r + 90) % 360)} aria-label="หมุนรูป">
              ⟳
            </button>
          </>
        )}
        <a href={receipt.imageUrl} target="_blank" rel="noreferrer" style={{ ...S.small, marginLeft: 'auto' }}>
          เปิดรูปในแท็บใหม่ ↗
        </a>
      </div>
      <div style={S.imageFrame}>
        {isPdf ? (
          <object data={receipt.imageUrl} type="application/pdf" data-testid="receipt-image" style={S.pdf} aria-label={`รูปใบเสร็จ ${receipt.fileName}`}>
            <p style={S.muted}>
              เบราว์เซอร์แสดง PDF ไม่ได้ <a href={receipt.imageUrl}>เปิดไฟล์</a>
            </p>
          </object>
        ) : (
          // eslint-disable-next-line @next/next/no-img-element -- รูปมาจาก API ที่ต้องมี session ไม่ผ่าน next/image
          <img
            src={receipt.imageUrl}
            alt={`รูปใบเสร็จ ${receipt.fileName}`}
            data-testid="receipt-image"
            onError={() => setMissing(true)}
            onLoad={() => setMissing(false)}
            style={{
              ...S.img,
              width: `${zoom * 100}%`,
              transform: rotate ? `rotate(${rotate}deg)` : undefined,
            }}
          />
        )}
        {missing && (
          <p style={S.imageMissing} role="status">
            ไม่พบไฟล์รูปของใบนี้ — ตรวจจากต้นฉบับกระดาษ หรือแจ้งผู้ดูแลระบบ
          </p>
        )}
      </div>
    </div>
  );
}

function HistoryPanel(props: {
  history: HistoryResponse | null;
  error: string | null;
  categories: Category[];
  receipt: Receipt;
}) {
  const { history, error, categories, receipt } = props;
  const catName = (v: string | null) => (v ? categories.find((c) => c.id === v)?.name ?? v : '—');
  const show = (field: string, v: string | null) => {
    if (v === null || v === '') return '—';
    if (field === 'category_id') return catName(v);
    if (field === 'total' || /\.price$/.test(field)) return showMoney(v);
    if (/\.removed$/.test(field)) return v === 'true' ? 'ลบ' : 'ไม่ลบ';
    return v;
  };
  if (error) {
    return (
      <p style={S.errorBox} role="alert">
        {error}
      </p>
    );
  }
  if (!history) return <p style={S.muted}>กำลังโหลดประวัติ…</p>;
  return (
    <div style={S.card} data-testid="history-panel">
      <p style={S.small}>
        ค่าที่ระบบอ่านเดิม: ร้าน {receipt.original.merchant ?? '—'} · วันที่ {receipt.original.receiptDate ?? '—'} · ยอดรวม{' '}
        {showMoney(receipt.original.total)}
        {history.enteredManually && ' · ใบนี้พิมพ์เองทั้งใบ'}
      </p>
      {history.edits.length === 0 ? (
        <p style={S.muted} data-testid="history-empty">
          ยังไม่มีการแก้ค่า
        </p>
      ) : (
        <table style={S.table} data-testid="history-table">
          <thead>
            <tr>
              <th style={S.th}>#</th>
              <th style={S.th}>ช่อง</th>
              <th style={S.th}>ค่าเดิม</th>
              <th style={S.th}>ค่าใหม่</th>
              <th style={S.th}>ผู้แก้</th>
              <th style={S.th}>เวลา</th>
            </tr>
          </thead>
          <tbody>
            {history.edits.map((e) => (
              <tr key={e.seq} data-testid={`history-row-${e.seq}`}>
                <td style={S.td}>{e.seq}</td>
                <td style={S.td}>{fieldLabel(e.field)}</td>
                <td style={S.td}>{show(e.field, e.oldValue)}</td>
                <td style={S.td}>{show(e.field, e.newValue)}</td>
                <td style={S.td}>{e.editedBy}</td>
                <td style={S.td}>{showDateTime(e.editedAt)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      {history.events.length > 0 && (
        <details style={{ marginTop: 8 }}>
          <summary style={S.small}>การเปลี่ยนสถานะ {history.events.length} ครั้ง</summary>
          <ul style={S.flagList}>
            {history.events.map((ev, i) => (
              <li key={i} style={S.small}>
                {showDateTime(ev.at)} · {ev.toLabel} · {ev.actor}
              </li>
            ))}
          </ul>
        </details>
      )}
    </div>
  );
}

// ───────────────────────────── สไตล์ ─────────────────────────────

const S = {
  main: { maxWidth: 1360, margin: '0 auto', padding: '16px 20px 48px', fontFamily: 'system-ui, sans-serif', color: '#1d2939' },
  h1: { fontSize: 22, margin: '4px 0' },
  h2: { fontSize: 17, margin: '0 0 8px' },
  fileName: { fontSize: 15, fontWeight: 400, color: '#475467' },
  muted: { color: '#667085', margin: '4px 0' },
  small: { fontSize: 13, color: '#475467' },
  hint: { fontSize: 12, color: '#98a2b3', margin: '6px 0 0' },
  back: { fontSize: 13, color: '#1849a9', textDecoration: 'none' },
  headerRow: { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 12, flexWrap: 'wrap', marginBottom: 8 },
  row: { display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' },
  card: { border: '1px solid #d0d5dd', borderRadius: 8, padding: '10px 14px', margin: '10px 0', background: '#fff' },
  cardFlag: { borderColor: '#f79009', background: '#fffaeb' },
  cardOk: { borderColor: '#75e0a7', background: '#f6fef9' },
  flagList: { margin: '6px 0', paddingLeft: 20 },
  chipDone: { display: 'inline-block', margin: '2px 4px', padding: '1px 8px', borderRadius: 10, background: '#d1fadf', color: '#05603a' },
  chipTodo: { display: 'inline-block', margin: '2px 4px', padding: '1px 8px', borderRadius: 10, background: '#fef0c7', color: '#93370d' },
  split: { display: 'grid', gridTemplateColumns: 'minmax(320px, 1fr) minmax(380px, 1fr)', gap: 20, alignItems: 'start' },
  imageCol: { position: 'sticky', top: 8 },
  imageTools: { display: 'flex', gap: 6, alignItems: 'center', marginBottom: 6 },
  imageFrame: { position: 'relative', border: '1px solid #d0d5dd', borderRadius: 8, background: '#f2f4f7', height: '78vh', overflow: 'auto' },
  img: { display: 'block', minHeight: 240, objectFit: 'contain', transformOrigin: 'center center', margin: '0 auto' },
  pdf: { width: '100%', height: '100%', minHeight: 400 },
  imageMissing: { position: 'absolute', top: 12, left: 12, right: 12, background: '#fef3f2', color: '#b42318', padding: 8, borderRadius: 6, margin: 0 },
  formCol: { minWidth: 0 },
  fieldBlock: { marginBottom: 12 },
  fieldEmphasis: { padding: 10, borderRadius: 8, background: '#eff8ff', border: '1px solid #b2ddff' },
  fieldHead: { display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', gap: 8, marginBottom: 4, flexWrap: 'wrap' },
  label: { fontWeight: 600, fontSize: 14 },
  changed: { marginLeft: 6, fontSize: 11, fontWeight: 600, color: '#6941c6', background: '#f4ebff', borderRadius: 8, padding: '1px 6px' },
  input: { width: '100%', boxSizing: 'border-box', padding: '7px 9px', fontSize: 15, border: '1px solid #d0d5dd', borderRadius: 6, background: '#fff' },
  inputFocusTarget: { borderColor: '#84adff' },
  inputBad: { borderColor: '#f04438', background: '#fef3f2' },
  totalInput: { fontSize: 22, fontWeight: 700, textAlign: 'right', fontVariantNumeric: 'tabular-nums' },
  orig: { fontSize: 11, color: '#667085', marginTop: 2 },
  table: { width: '100%', borderCollapse: 'collapse', fontSize: 14 },
  th: { textAlign: 'left', borderBottom: '1px solid #d0d5dd', padding: '4px 6px', fontWeight: 600, fontSize: 13, color: '#475467' },
  td: { borderBottom: '1px solid #eaecf0', padding: '4px 6px', verticalAlign: 'top' },
  rowRemoved: { opacity: 0.5, textDecoration: 'line-through' },
  actionBox: { borderTop: '1px solid #eaecf0', paddingTop: 12, marginTop: 8 },
  checkLabel: { display: 'flex', alignItems: 'center', gap: 8, fontSize: 16, fontWeight: 600, marginBottom: 10, cursor: 'pointer' },
  btn: { padding: '8px 16px', fontSize: 15, borderRadius: 6, border: '1px solid #d0d5dd', background: '#fff', cursor: 'pointer', textDecoration: 'none', color: '#1d2939', display: 'inline-block' },
  btnPrimary: { background: '#155eef', borderColor: '#155eef', color: '#fff', fontWeight: 600 },
  btnDisabled: { background: '#b2ccff', borderColor: '#b2ccff', cursor: 'not-allowed' },
  btnGhost: { padding: '6px 10px', fontSize: 14, borderRadius: 6, border: '1px solid transparent', background: 'transparent', color: '#1849a9', cursor: 'pointer' },
  btnSmall: { padding: '3px 8px', fontSize: 13, borderRadius: 5, border: '1px solid #d0d5dd', background: '#fff', cursor: 'pointer' },
  badgeUrgent: { display: 'inline-block', fontSize: 11, fontWeight: 700, color: '#fff', background: '#d92d20', borderRadius: 6, padding: '1px 6px' },
  errorBox: { background: '#fef3f2', color: '#b42318', border: '1px solid #fecdca', borderRadius: 6, padding: '8px 10px', margin: '8px 0' },
  noteBox: { background: '#f9fafb', border: '1px solid #eaecf0', borderRadius: 6, padding: '8px 10px', margin: '8px 0' },
  blockers: { margin: '8px 0 0', paddingLeft: 20, fontSize: 13, color: '#b54708' },
  warnText: { fontSize: 13, color: '#b54708' },
  okText: { fontSize: 13, color: '#067647' },
  timerBox: { fontSize: 14, fontWeight: 600, fontVariantNumeric: 'tabular-nums', padding: '6px 10px', border: '1px solid #eaecf0', borderRadius: 6 },
} satisfies Record<string, CSSProperties>;
