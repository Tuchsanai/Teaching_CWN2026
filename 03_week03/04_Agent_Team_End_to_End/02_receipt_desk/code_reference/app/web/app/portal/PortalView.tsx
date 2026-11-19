'use client';
/**
 * หน้าลูกค้า
 * - ส่งใบ (W7 POST /api/batches ไม่ส่ง clientId · server ผูกกับร้านของบัญชีเอง · FR-26)
 *   testid: portal-file-input · portal-upload-button · portal-accepted-count · portal-upload-error
 * - ใบของร้าน (W11 GET /api/receipts · FR-27): ชื่อไฟล์ · เวลาที่รับ · สถานะ "รับแล้ว รอสำนักงานตรวจ"
 *   testid: portal-receipt-row-{id} · portal-receipt-status-{id} · portal-receipt-total-{id} (มีเฉพาะใบที่ยืนยันแล้ว · FR-25)
 * - สรุปแยกหมวด (W19 GET /api/reports/categories?month=YYYY-MM · FR-29)
 *   testid: portal-month-input · portal-summary-total · portal-category-total-{categoryId}
 */
import { useCallback, useEffect, useRef, useState } from 'react';
import type { FormEvent } from 'react';
import { api, errorText } from '../_ui/api';
import type { ApiErrorBody } from '../_ui/api';
import { currentBangkokMonth, dateTime, money } from '../_ui/format';

interface PortalReceipt {
  id: string;
  fileName: string;
  acceptedAt: string;
  status: 'received' | 'confirmed';
  statusLabel: string;
  merchant?: string | null;
  receiptDate?: string | null;
  total?: string | null;
  categoryName?: string | null;
}

interface Categories {
  month: string;
  count: number;
  total: string;
  categories: { id: string; name: string; count: number; total: string }[];
  uncategorized?: string;
}

const MONTH_RE = /^\d{4}-(0[1-9]|1[0-2])$/;

function uploadErrorText(e: ApiErrorBody): string {
  if (e.error === 'queue_full') {
    return `ตอนนี้ระบบเต็ม กรุณาลองใหม่ในอีก ${e.retryAfterMinutes ?? '?'} นาที`;
  }
  const base = errorText(e);
  if (!e.files?.length) return base;
  return `${base} — ${e.files.map((f) => `ไฟล์ที่ ${f.index + 1} “${f.name}”: ${f.message}`).join(' · ')}`;
}

export default function PortalView() {
  const [files, setFiles] = useState<File[]>([]);
  const [busy, setBusy] = useState(false);
  const [accepted, setAccepted] = useState<number | null>(null);
  const [uploadError, setUploadError] = useState<ApiErrorBody | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const [receipts, setReceipts] = useState<PortalReceipt[] | null>(null);
  const [listError, setListError] = useState<string | null>(null);

  const [month, setMonth] = useState('');
  const [summary, setSummary] = useState<Categories | null>(null);
  const [summaryError, setSummaryError] = useState<string | null>(null);

  const loadReceipts = useCallback(async () => {
    const r = await api<{ receipts: PortalReceipt[] }>('/api/receipts?limit=1000');
    if (r.ok) {
      setReceipts(r.data.receipts);
      setListError(null);
    } else setListError(errorText(r.error));
  }, []);

  useEffect(() => {
    loadReceipts();
    const t = setInterval(loadReceipts, 30_000);
    return () => clearInterval(t);
  }, [loadReceipts]);

  useEffect(() => setMonth((m) => m || currentBangkokMonth()), []);

  useEffect(() => {
    if (!MONTH_RE.test(month)) {
      setSummary(null);
      return;
    }
    let alive = true;
    api<Categories>(`/api/reports/categories?month=${encodeURIComponent(month)}`).then((r) => {
      if (!alive) return;
      if (r.ok) {
        setSummary(r.data);
        setSummaryError(null);
      } else {
        setSummary(null);
        setSummaryError(errorText(r.error));
      }
    });
    return () => {
      alive = false;
    };
  }, [month]);

  async function onUpload(e: FormEvent) {
    e.preventDefault();
    setAccepted(null);
    setUploadError(null);
    const form = new FormData();
    for (const f of files) form.append('files', f, f.name);
    setBusy(true);
    const r = await api<{ accepted: number }>('/api/batches', { method: 'POST', body: form });
    setBusy(false);
    if (r.ok) {
      setAccepted(r.data.accepted);
      setFiles([]);
      if (fileRef.current) fileRef.current.value = '';
      loadReceipts();
    } else {
      setAccepted(0);
      setUploadError(r.error);
    }
  }

  return (
    <>
      <section className="card">
        <h2 style={{ fontSize: 16, marginTop: 0 }}>ส่งใบเสร็จ</h2>
        <form className="row" onSubmit={onUpload} noValidate>
          <label className="field">
            ไฟล์ (JPG · PNG · PDF 1 หน้า · ไม่เกิน 10 MB ต่อไฟล์ · 1–100 ไฟล์)
            <input
              ref={fileRef}
              type="file"
              multiple
              data-testid="portal-file-input"
              onChange={(e) => setFiles(Array.from(e.target.files ?? []))}
            />
          </label>
          <button type="submit" data-testid="portal-upload-button" disabled={busy}>
            {busy ? 'กำลังส่ง…' : 'ส่งใบเสร็จ'}
          </button>
        </form>
        {accepted !== null ? (
          <p>
            รับแล้ว <strong data-testid="portal-accepted-count">{accepted}</strong> ใบ
            {accepted > 0 ? ' — สำนักงานจะตรวจและยืนยันให้' : ''}
          </p>
        ) : null}
        {uploadError ? (
          <div className="notice error" role="alert" data-testid="portal-upload-error">
            {uploadErrorText(uploadError)}
          </div>
        ) : null}
      </section>

      <section className="card">
        <h2 style={{ fontSize: 16, marginTop: 0 }}>ใบเสร็จของร้าน</h2>
        {listError ? <div className="notice error">{listError}</div> : null}
        <table>
          <thead>
            <tr>
              <th>ไฟล์</th>
              <th>รับเมื่อ</th>
              <th>สถานะ</th>
              <th>ร้านบนใบ</th>
              <th>วันที่บนใบ</th>
              <th>หมวด</th>
              <th className="num">ยอดรวม (บาท)</th>
            </tr>
          </thead>
          <tbody>
            {receipts?.map((r) => (
              <tr key={r.id} data-testid={`portal-receipt-row-${r.id}`}>
                <td>{r.fileName}</td>
                <td>{dateTime(r.acceptedAt)}</td>
                <td>
                  <span data-testid={`portal-receipt-status-${r.id}`} data-status={r.status}>
                    {r.statusLabel}
                  </span>
                </td>
                {r.status === 'confirmed' ? (
                  <>
                    <td>{r.merchant ?? '—'}</td>
                    <td>{r.receiptDate ?? '—'}</td>
                    <td>{r.categoryName ?? '—'}</td>
                    <td className="num" data-testid={`portal-receipt-total-${r.id}`}>
                      {money(r.total)}
                    </td>
                  </>
                ) : (
                  <td colSpan={4} className="muted">
                    แสดงตัวเลขเมื่อสำนักงานยืนยันแล้ว
                  </td>
                )}
              </tr>
            ))}
            {receipts && receipts.length === 0 ? (
              <tr>
                <td colSpan={7} className="muted">
                  ยังไม่มีใบเสร็จ
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </section>

      <section className="card">
        <h2 style={{ fontSize: 16, marginTop: 0 }}>รายจ่ายแยกหมวด (เฉพาะใบที่ยืนยันแล้ว · ตามวันที่บนใบ)</h2>
        <label className="field" style={{ maxWidth: 240 }}>
          เดือน
          <input type="month" data-testid="portal-month-input" value={month} onChange={(e) => setMonth(e.target.value)} />
        </label>
        {summaryError ? <div className="notice error">{summaryError}</div> : null}
        {summary ? (
          <>
            <p>
              ยอดรวมทั้งเดือน <strong data-testid="portal-summary-total">{money(summary.total)}</strong> บาท ·{' '}
              {summary.count} ใบ
            </p>
            <table>
              <thead>
                <tr>
                  <th>หมวด</th>
                  <th className="num">ใบ</th>
                  <th className="num">ยอด (บาท)</th>
                </tr>
              </thead>
              <tbody>
                {summary.categories.map((c) => (
                  <tr key={c.id}>
                    <td>{c.name}</td>
                    <td className="num">{c.count}</td>
                    <td className="num" data-testid={`portal-category-total-${c.id}`}>
                      {money(c.total)}
                    </td>
                  </tr>
                ))}
                {summary.uncategorized ? (
                  <tr>
                    <td>ไม่ระบุหมวด</td>
                    <td></td>
                    <td className="num">{money(summary.uncategorized)}</td>
                  </tr>
                ) : null}
              </tbody>
            </table>
          </>
        ) : null}
      </section>
    </>
  );
}
