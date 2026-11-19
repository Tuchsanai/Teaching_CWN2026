'use client';
/**
 * รายการค้างเกินกำหนด (W11 GET /api/receipts?overdue=true) — การตัดสิน BR-13 อยู่ที่ server (rules.ts)
 * testid: overdue-table · overdue-count · overdue-row-{id} · overdue-minutes-{id} (จำนวนนาทีที่รอ เป็นตัวเลขล้วน)
 */
import Link from 'next/link';
import { useCallback, useEffect, useState } from 'react';
import { api, errorText } from '../_ui/api';
import { dateTime } from '../_ui/format';

interface Row {
  id: string;
  batchId: string;
  clientName: string;
  fileName: string;
  status: string;
  statusLabel: string;
  acceptedAt: string;
  minutesWaiting?: number;
}

export default function OverdueView() {
  const [rows, setRows] = useState<Row[] | null>(null);
  const [count, setCount] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    const r = await api<{ count: number; receipts: Row[] }>('/api/receipts?overdue=true&limit=1000');
    if (r.ok) {
      setRows(r.data.receipts);
      setCount(r.data.count);
      setError(null);
    } else setError(errorText(r.error));
  }, []);

  useEffect(() => {
    load();
    const t = setInterval(load, 30_000);
    return () => clearInterval(t);
  }, [load]);

  return (
    <>
      {error ? <div className="notice error">{error}</div> : null}
      {count ? (
        <div className="notice warn" role="status">
          มีงานปกติค้างเกินกำหนด {count} ใบ
        </div>
      ) : null}
      <p>
        ค้างเกินกำหนด <strong data-testid="overdue-count">{count ?? '…'}</strong> ใบ
      </p>
      <table data-testid="overdue-table">
        <thead>
          <tr>
            <th>รับเมื่อ</th>
            <th>ลูกค้า</th>
            <th>ไฟล์</th>
            <th>สถานะ</th>
            <th className="num">รอมาแล้ว (นาที)</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {rows?.map((r) => (
            <tr key={r.id} data-testid={`overdue-row-${r.id}`}>
              <td>{dateTime(r.acceptedAt)}</td>
              <td>{r.clientName}</td>
              <td>{r.fileName}</td>
              <td>{r.statusLabel}</td>
              <td className="num" data-testid={`overdue-minutes-${r.id}`}>
                {r.minutesWaiting ?? '—'}
              </td>
              <td>
                <Link href={`/batches/${r.batchId}`}>เปิดชุด</Link>
              </td>
            </tr>
          ))}
          {rows && rows.length === 0 ? (
            <tr>
              <td colSpan={6} className="muted">
                ไม่มีงานค้างเกินกำหนด
              </td>
            </tr>
          ) : null}
        </tbody>
      </table>
    </>
  );
}
