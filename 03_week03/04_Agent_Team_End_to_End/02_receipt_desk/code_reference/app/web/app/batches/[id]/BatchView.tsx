'use client';
/**
 * ชุด 1 ชุด (W9 GET /api/batches/{id}) + ปุ่มงานด่วนของหัวหน้า (W10 POST /api/batches/{id}/urgent)
 * testid: batch-priority · batch-count-accepted · batch-count-{queued|processing|review|confirmed|unreadable}
 *         batch-urgent-button (หัวหน้าเท่านั้น · FR-19) · batch-urgent-error
 *         receipt-row-{id} · receipt-status-{id} · receipt-flag-{id} · receipt-open-link-{id}
 * สถานะรีเฟรชเองทุก 5 วินาทีขณะยังมีใบรออ่าน/กำลังอ่าน (FR-07)
 */
import Link from 'next/link';
import { useCallback, useEffect, useState } from 'react';
import { api, errorText } from '../../_ui/api';
import { STATUS_OPTIONS, dateTime, money } from '../../_ui/format';
import { FlagCell, StatusCell } from '../../_ui/ReceiptBits';
import type { Flags } from '../../_ui/ReceiptBits';

interface BatchDetail {
  batch: {
    id: string;
    clientCode: string;
    clientName: string;
    uploadedBy: string;
    priority: 'normal' | 'urgent';
    urgentSetAt: string | null;
    urgentSetBy: string | null;
    acceptedAt: string;
    accepted: number;
    counts: Record<string, number>;
    sum: number;
    diff: number;
    canSetUrgent: boolean;
  };
  receipts: {
    id: string;
    fileName: string;
    status: string;
    statusLabel: string;
    merchant: string | null;
    total: string | null;
    flags: Flags;
    overdue: boolean;
    minutesWaiting?: number;
    unreadableReason: string | null;
  }[];
}

export default function BatchView({ id, isLead }: { id: string; isLead: boolean }) {
  const [data, setData] = useState<BatchDetail | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [urgentError, setUrgentError] = useState<string | null>(null);
  const [urgentMsg, setUrgentMsg] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    const r = await api<BatchDetail>(`/api/batches/${encodeURIComponent(id)}`);
    if (r.ok) {
      setData(r.data);
      setLoadError(null);
    } else setLoadError(r.status === 404 ? 'ไม่พบชุดนี้' : errorText(r.error));
  }, [id]);

  const active = data ? (data.batch.counts.queued ?? 0) + (data.batch.counts.processing ?? 0) > 0 : true;

  useEffect(() => {
    load();
    if (!active) return;
    const t = setInterval(load, 5_000);
    return () => clearInterval(t);
  }, [load, active]);

  async function setUrgent() {
    setUrgentError(null);
    setUrgentMsg(null);
    setBusy(true);
    const r = await api<{ message: string }>(`/api/batches/${encodeURIComponent(id)}/urgent`, { method: 'POST' });
    setBusy(false);
    if (r.ok) setUrgentMsg(r.data.message);
    else setUrgentError(errorText(r.error));
    load();
  }

  if (loadError && !data) {
    return (
      <div className="notice error" role="alert">
        {loadError}
      </div>
    );
  }
  if (!data) return <p className="muted">กำลังโหลด…</p>;
  const b = data.batch;

  return (
    <>
      <p>
        <Link href="/batches">← ชุดใบเสร็จทั้งหมด</Link>
      </p>
      <h1>
        ชุดของ {b.clientCode} · {b.clientName}
      </h1>
      <p className="muted">
        รับเมื่อ {dateTime(b.acceptedAt)} · อัปโหลดโดย {b.uploadedBy} · ประเภท{' '}
        <span data-testid="batch-priority" data-priority={b.priority} className={b.priority === 'urgent' ? 'badge urgent' : 'badge'}>
          {b.priority === 'urgent' ? 'ด่วน' : 'ปกติ'}
        </span>
        {b.urgentSetAt ? ` (ตั้งด่วนโดย ${b.urgentSetBy ?? '—'} เมื่อ ${dateTime(b.urgentSetAt)})` : ''}
      </p>

      <div className="stats" style={{ marginBottom: 16 }}>
        <div className="stat">
          <div className="label">รับเข้า</div>
          <div className="value" data-testid="batch-count-accepted">{b.accepted}</div>
        </div>
        {STATUS_OPTIONS.map((s) => (
          <div className="stat" key={s.value}>
            <div className="label">{s.label}</div>
            <div className="value" data-testid={`batch-count-${s.value}`}>
              {b.counts[s.value] ?? 0}
            </div>
          </div>
        ))}
        <div className="stat">
          <div className="label">ผลต่าง (รับเข้า − รวมทุกสถานะ)</div>
          <div className="value" style={{ color: b.diff !== 0 ? 'var(--bad)' : undefined }}>
            {b.diff}
          </div>
        </div>
      </div>

      {isLead ? (
        <div className="card">
          <button
            type="button"
            data-testid="batch-urgent-button"
            onClick={setUrgent}
            disabled={busy || b.priority === 'urgent'}
          >
            {b.priority === 'urgent' ? 'เป็นงานด่วนแล้ว' : 'ตั้งเป็นงานด่วน'}
          </button>{' '}
          <span className="muted">ไม่เกิน 10 ใบต่อชุด · ไม่เกิน 5 งานต่อวัน</span>
          {urgentError ? (
            <div className="notice error" role="alert" data-testid="batch-urgent-error">
              {urgentError}
            </div>
          ) : null}
          {urgentMsg ? <div className="notice ok">{urgentMsg}</div> : null}
        </div>
      ) : null}

      <table>
        <thead>
          <tr>
            <th>ไฟล์</th>
            <th>สถานะ</th>
            <th>ธง</th>
            <th>ร้านที่อ่านได้</th>
            <th className="num">ยอดรวม</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {data.receipts.map((r) => (
            <tr key={r.id} data-testid={`receipt-row-${r.id}`}>
              <td>{r.fileName}</td>
              <td>
                <StatusCell id={r.id} status={r.status} label={r.statusLabel} />
                {r.overdue ? <span className="badge bad">ค้าง {r.minutesWaiting} นาที</span> : null}
                {r.status === 'unreadable' && r.unreadableReason ? (
                  <div className="muted" style={{ fontSize: 12 }}>{r.unreadableReason}</div>
                ) : null}
              </td>
              <td>
                <FlagCell id={r.id} flags={r.flags} />
              </td>
              <td>{r.merchant ?? '—'}</td>
              <td className="num">{money(r.total)}</td>
              <td>
                <Link href={`/receipts/${r.id}`} data-testid={`receipt-open-link-${r.id}`}>
                  เปิดใบ
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  );
}
