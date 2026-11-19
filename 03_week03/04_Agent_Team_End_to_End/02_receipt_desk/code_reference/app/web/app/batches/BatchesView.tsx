'use client';
/**
 * รายการชุด (W8 GET /api/batches) + ยอดตรวจนับทั้งสำนักงาน (W20 GET /api/reports/reconcile)
 * testid: batches-table · batch-row-{id} · batch-open-link-{id} · reconcile-accepted · reconcile-sum · reconcile-diff
 * FR-08: รับเข้า = ผลรวมทุกสถานะ · ผลต่างต้องเป็น 0
 */
import Link from 'next/link';
import { useCallback, useEffect, useState } from 'react';
import { api, errorText } from '../_ui/api';
import { PRIORITY_LABEL, STATUS_OPTIONS, dateTime } from '../_ui/format';

interface BatchItem {
  id: string;
  clientCode: string;
  clientName: string;
  uploadedBy: string;
  priority: 'normal' | 'urgent';
  acceptedAt: string;
  accepted: number;
  counts: Record<string, number>;
  sum: number;
  diff: number;
  flagged: number;
}

interface Reconcile {
  accepted: number;
  sum: number;
  diff: number;
  counts: Record<string, number>;
}

export default function BatchesView() {
  const [batches, setBatches] = useState<BatchItem[] | null>(null);
  const [rec, setRec] = useState<Reconcile | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    const [b, r] = await Promise.all([
      api<{ batches: BatchItem[] }>('/api/batches?limit=500'),
      api<Reconcile>('/api/reports/reconcile'),
    ]);
    if (b.ok) setBatches(b.data.batches);
    else setError(errorText(b.error));
    if (r.ok) setRec(r.data);
    else setError(errorText(r.error));
  }, []);

  useEffect(() => {
    load();
    const t = setInterval(load, 10_000);
    return () => clearInterval(t);
  }, [load]);

  return (
    <>
      <section className="card">
        <h2 style={{ fontSize: 16, marginTop: 0 }}>ยอดตรวจนับทั้งสำนักงาน</h2>
        <div className="stats">
          <div className="stat">
            <div className="label">รับเข้า (ใบ)</div>
            <div className="value" data-testid="reconcile-accepted">{rec ? rec.accepted : '…'}</div>
          </div>
          <div className="stat">
            <div className="label">รวมทุกสถานะ (ใบ)</div>
            <div className="value" data-testid="reconcile-sum">{rec ? rec.sum : '…'}</div>
          </div>
          <div className="stat">
            <div className="label">ผลต่าง</div>
            <div
              className="value"
              data-testid="reconcile-diff"
              style={{ color: rec && rec.diff !== 0 ? 'var(--bad)' : undefined }}
            >
              {rec ? rec.diff : '…'}
            </div>
          </div>
        </div>
        {rec ? (
          <p className="muted" style={{ marginBottom: 0 }}>
            {STATUS_OPTIONS.map((s) => `${s.label} ${rec.counts[s.value] ?? 0}`).join(' · ')}
          </p>
        ) : null}
      </section>

      {error ? <div className="notice error">{error}</div> : null}

      <table data-testid="batches-table">
        <thead>
          <tr>
            <th>รับเมื่อ</th>
            <th>ลูกค้า</th>
            <th>ผู้อัปโหลด</th>
            <th>ประเภท</th>
            <th className="num">รับเข้า</th>
            {STATUS_OPTIONS.map((s) => (
              <th key={s.value} className="num">
                {s.label}
              </th>
            ))}
            <th className="num">ผลต่าง</th>
            <th className="num">ติดธง</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {batches?.map((b) => (
            <tr key={b.id} data-testid={`batch-row-${b.id}`}>
              <td>{dateTime(b.acceptedAt)}</td>
              <td>
                {b.clientCode} · {b.clientName}
              </td>
              <td>{b.uploadedBy}</td>
              <td>
                {b.priority === 'urgent' ? <span className="badge urgent">ด่วน</span> : PRIORITY_LABEL[b.priority]}
              </td>
              <td className="num">{b.accepted}</td>
              {STATUS_OPTIONS.map((s) => (
                <td key={s.value} className="num">
                  {b.counts[s.value] ?? 0}
                </td>
              ))}
              <td className="num" style={{ color: b.diff !== 0 ? 'var(--bad)' : undefined }}>
                {b.diff}
              </td>
              <td className="num">{b.flagged ? <span className="badge warn">{b.flagged}</span> : 0}</td>
              <td>
                <Link href={`/batches/${b.id}`} data-testid={`batch-open-link-${b.id}`}>
                  เปิด
                </Link>
              </td>
            </tr>
          ))}
          {batches && batches.length === 0 ? (
            <tr>
              <td colSpan={13} className="muted">
                ยังไม่มีชุดใบเสร็จ
              </td>
            </tr>
          ) : null}
        </tbody>
      </table>
    </>
  );
}
