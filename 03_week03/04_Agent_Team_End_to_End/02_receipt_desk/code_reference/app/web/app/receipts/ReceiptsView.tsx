'use client';
/**
 * รายการใบ (W11 GET /api/receipts?status=&flagged=true&clientId=)
 * testid: filter-status-select · filter-flagged-checkbox · filter-client-select · filter-apply-button
 *         receipts-table · receipts-count · receipt-row-{id} · receipt-status-{id} · receipt-flag-{id}
 *         (+ receipt-open-link-{id} แบบเดียวกับหน้า /batches/[id])
 * ตัวกรองมีผลเมื่อกด filter-apply-button และถูกเก็บใน URL (?status=&flagged=&clientId=)
 */
import Link from 'next/link';
import { useCallback, useEffect, useState } from 'react';
import { api, errorText } from '../_ui/api';
import { STATUS_OPTIONS, dateTime, money } from '../_ui/format';
import { FlagCell, StatusCell } from '../_ui/ReceiptBits';
import type { Flags } from '../_ui/ReceiptBits';
import { useClients } from '../_ui/useClients';

interface Filter {
  status: string;
  flagged: boolean;
  clientId: string;
}

interface Row {
  id: string;
  batchId: string;
  clientName: string;
  priority: 'normal' | 'urgent';
  fileName: string;
  status: string;
  statusLabel: string;
  merchant: string | null;
  receiptDate: string | null;
  total: string | null;
  flags: Flags;
  acceptedAt: string;
  confirmedBy: string | null;
  overdue: boolean;
  minutesWaiting?: number;
}

function query(f: Filter): string {
  const p = new URLSearchParams();
  if (f.status) p.set('status', f.status);
  if (f.flagged) p.set('flagged', 'true');
  if (f.clientId) p.set('clientId', f.clientId);
  return p.toString();
}

export default function ReceiptsView({ initial }: { initial: Filter }) {
  const { clients } = useClients();
  const [draft, setDraft] = useState<Filter>(initial);
  const [applied, setApplied] = useState<Filter>(initial);
  const [rows, setRows] = useState<Row[] | null>(null);
  const [count, setCount] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const load = useCallback(async (f: Filter) => {
    setLoading(true);
    const qs = query(f);
    const r = await api<{ count: number; receipts: Row[] }>(`/api/receipts?limit=1000${qs ? `&${qs}` : ''}`);
    setLoading(false);
    if (r.ok) {
      setRows(r.data.receipts);
      setCount(r.data.count);
      setError(null);
    } else setError(errorText(r.error));
  }, []);

  useEffect(() => {
    load(applied);
  }, [load, applied]);

  function apply() {
    const qs = query(draft);
    window.history.replaceState(null, '', `/receipts${qs ? `?${qs}` : ''}`);
    setApplied({ ...draft });
  }

  return (
    <>
      <div className="card row">
        <label className="field">
          สถานะ
          <select
            data-testid="filter-status-select"
            value={draft.status}
            onChange={(e) => setDraft({ ...draft, status: e.target.value })}
          >
            <option value="">ทุกสถานะ</option>
            {STATUS_OPTIONS.map((s) => (
              <option key={s.value} value={s.value}>
                {s.label}
              </option>
            ))}
          </select>
        </label>
        <label className="field">
          ลูกค้า
          <select
            data-testid="filter-client-select"
            value={draft.clientId}
            onChange={(e) => setDraft({ ...draft, clientId: e.target.value })}
          >
            <option value="">ทุกลูกค้า</option>
            {clients.map((c) => (
              <option key={c.id} value={c.id}>
                {c.code} · {c.name}
              </option>
            ))}
          </select>
        </label>
        <label style={{ paddingBottom: 6 }}>
          <input
            type="checkbox"
            data-testid="filter-flagged-checkbox"
            checked={draft.flagged}
            onChange={(e) => setDraft({ ...draft, flagged: e.target.checked })}
          />{' '}
          เฉพาะใบติดธง “ระบบไม่แน่ใจ”
        </label>
        <button type="button" data-testid="filter-apply-button" onClick={apply} disabled={loading}>
          กรอง
        </button>
      </div>

      {error ? <div className="notice error">{error}</div> : null}
      <p>
        พบ <strong data-testid="receipts-count">{count ?? '…'}</strong> ใบ
      </p>

      <table data-testid="receipts-table">
        <thead>
          <tr>
            <th>รับเมื่อ</th>
            <th>ลูกค้า</th>
            <th>ไฟล์</th>
            <th>สถานะ</th>
            <th>ธง</th>
            <th>ร้าน</th>
            <th>วันที่บนใบ</th>
            <th className="num">ยอดรวม</th>
            <th>ยืนยันโดย</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {rows?.map((r) => (
            <tr key={r.id} data-testid={`receipt-row-${r.id}`}>
              <td>{dateTime(r.acceptedAt)}</td>
              <td>
                {r.clientName}
                {r.priority === 'urgent' ? <span className="badge urgent">ด่วน</span> : null}
              </td>
              <td>{r.fileName}</td>
              <td>
                <StatusCell id={r.id} status={r.status} label={r.statusLabel} />
                {r.overdue ? <span className="badge bad">ค้าง {r.minutesWaiting} นาที</span> : null}
              </td>
              <td>
                <FlagCell id={r.id} flags={r.flags} />
              </td>
              <td>{r.merchant ?? '—'}</td>
              <td>{r.receiptDate ?? '—'}</td>
              <td className="num">{money(r.total)}</td>
              <td>{r.confirmedBy ?? '—'}</td>
              <td>
                <Link href={`/receipts/${r.id}`} data-testid={`receipt-open-link-${r.id}`}>
                  เปิดใบ
                </Link>
              </td>
            </tr>
          ))}
          {rows && rows.length === 0 ? (
            <tr>
              <td colSpan={10} className="muted">
                ไม่มีใบตามตัวกรองนี้
              </td>
            </tr>
          ) : null}
        </tbody>
      </table>
    </>
  );
}
