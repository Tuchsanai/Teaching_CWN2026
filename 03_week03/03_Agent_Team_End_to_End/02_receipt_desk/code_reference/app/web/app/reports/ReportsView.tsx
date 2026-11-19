'use client';
/**
 * สรุปรายเดือน (W18 GET /api/reports/monthly?clientId=&month=YYYY-MM[&format=json])
 * testid: report-client-select · report-month-input · report-preview-button · report-total · report-receipt-count
 *         report-export-button (ลิงก์ดาวน์โหลด CSV ตรงจาก W18 · ยอดใน CSV = report-total)
 * report-total แสดงค่าดิบจาก server เช่น `1340.00` · หน่วย "บาท" อยู่นอกองค์ประกอบ
 */
import { useEffect, useState } from 'react';
import { api, errorText } from '../_ui/api';
import { currentBangkokMonth, money } from '../_ui/format';
import { useClients } from '../_ui/useClients';

interface Preview {
  clientId: string;
  month: string;
  count: number;
  total: string;
  byCategory: Record<string, { name?: string; count: number; total: string }>;
  receipts: {
    id: string;
    receiptDate: string;
    merchant: string | null;
    categoryName: string | null;
    total: string;
    fileName: string;
    confirmedBy: string | null;
  }[];
}

const MONTH_RE = /^\d{4}-(0[1-9]|1[0-2])$/;

export default function ReportsView() {
  const { clients } = useClients();
  const [clientId, setClientId] = useState('');
  const [month, setMonth] = useState('');
  const [preview, setPreview] = useState<Preview | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  // ตั้งเดือนปัจจุบัน (เวลาไทย) หลัง mount เพื่อไม่ให้ค่าจาก server กับ browser ต่างกัน
  useEffect(() => setMonth((m) => m || currentBangkokMonth()), []);

  const ready = Boolean(clientId) && MONTH_RE.test(month);
  const exportUrl = ready
    ? `/api/reports/monthly?clientId=${encodeURIComponent(clientId)}&month=${encodeURIComponent(month)}`
    : undefined;

  async function onPreview() {
    setError(null);
    setPreview(null);
    if (!clientId) return setError('กรุณาเลือกลูกค้า');
    if (!MONTH_RE.test(month)) return setError('กรุณาเลือกเดือนในรูป YYYY-MM');
    setBusy(true);
    const r = await api<Preview>(`${exportUrl}&format=json`);
    setBusy(false);
    if (r.ok) setPreview(r.data);
    else setError(errorText(r.error));
  }

  return (
    <>
      <div className="card row">
        <label className="field">
          ลูกค้า
          <select
            data-testid="report-client-select"
            value={clientId}
            onChange={(e) => {
              setClientId(e.target.value);
              setPreview(null);
            }}
          >
            <option value="">— เลือกลูกค้า —</option>
            {clients.map((c) => (
              <option key={c.id} value={c.id}>
                {c.code} · {c.name}
              </option>
            ))}
          </select>
        </label>
        <label className="field">
          เดือน
          <input
            type="month"
            data-testid="report-month-input"
            value={month}
            onChange={(e) => {
              setMonth(e.target.value);
              setPreview(null);
            }}
          />
        </label>
        <button type="button" className="secondary" data-testid="report-preview-button" onClick={onPreview} disabled={busy}>
          ดูตัวอย่าง
        </button>
        <a
          className="button"
          data-testid="report-export-button"
          href={exportUrl}
          download
          aria-disabled={!ready}
          onClick={(e) => {
            if (!ready) e.preventDefault();
          }}
        >
          ออกไฟล์ CSV
        </a>
      </div>

      {error ? (
        <div className="notice error" role="alert">
          {error}
        </div>
      ) : null}

      {preview ? (
        <section className="card">
          <div className="stats">
            <div className="stat">
              <div className="label">ยอดรวมของเดือน {preview.month}</div>
              <div className="value">
                <span data-testid="report-total">{money(preview.total)}</span>{' '}
                <span className="muted" style={{ fontSize: 14 }}>บาท</span>
              </div>
            </div>
            <div className="stat">
              <div className="label">จำนวนใบที่ยืนยันแล้ว</div>
              <div className="value" data-testid="report-receipt-count">
                {preview.count}
              </div>
            </div>
          </div>
          {preview.receipts.length === 0 ? (
            <p className="muted">เดือนนี้ไม่มีใบที่ยืนยันแล้ว ไฟล์ CSV จะมีเฉพาะหัวตาราง</p>
          ) : (
            <table style={{ marginTop: 12 }}>
              <thead>
                <tr>
                  <th>วันที่บนใบ</th>
                  <th>ร้าน</th>
                  <th>หมวด</th>
                  <th className="num">ยอดรวม</th>
                  <th>ไฟล์</th>
                  <th>ยืนยันโดย</th>
                </tr>
              </thead>
              <tbody>
                {preview.receipts.map((r) => (
                  <tr key={r.id}>
                    <td>{r.receiptDate}</td>
                    <td>{r.merchant ?? '—'}</td>
                    <td>{r.categoryName ?? '—'}</td>
                    <td className="num">{money(r.total)}</td>
                    <td>{r.fileName}</td>
                    <td>{r.confirmedBy ?? '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>
      ) : null}
    </>
  );
}
