'use client';
/**
 * รายการใบอ่านไม่ได้ (W11 GET /api/receipts?status=unreadable)
 * testid: unreadable-table · unreadable-count · unreadable-row-{id} · unreadable-reason-{id} · unreadable-open-link-{id}
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
  attempts: number | null;
  acceptedAt: string;
  resultAt: string | null;
  unreadableReason: string | null;
}

export default function UnreadableView() {
  const [rows, setRows] = useState<Row[] | null>(null);
  const [count, setCount] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    const r = await api<{ count: number; receipts: Row[] }>('/api/receipts?status=unreadable&limit=1000');
    if (r.ok) {
      setRows(r.data.receipts);
      setCount(r.data.count);
      setError(null);
    } else setError(errorText(r.error));
  }, []);

  useEffect(() => {
    load();
    const t = setInterval(load, 15_000);
    return () => clearInterval(t);
  }, [load]);

  return (
    <>
      {error ? <div className="notice error">{error}</div> : null}
      <p>
        รอพิมพ์เอง <strong data-testid="unreadable-count">{count ?? '…'}</strong> ใบ
      </p>
      <table data-testid="unreadable-table">
        <thead>
          <tr>
            <th>รับเมื่อ</th>
            <th>ลูกค้า</th>
            <th>ไฟล์</th>
            <th className="num">อ่านไปแล้ว (ครั้ง)</th>
            <th>เหตุผล</th>
            <th>ย้ายมาเมื่อ</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {rows?.map((r) => (
            <tr key={r.id} data-testid={`unreadable-row-${r.id}`}>
              <td>{dateTime(r.acceptedAt)}</td>
              <td>{r.clientName}</td>
              <td>{r.fileName}</td>
              <td className="num">{r.attempts ?? '—'}</td>
              <td data-testid={`unreadable-reason-${r.id}`}>{r.unreadableReason ?? 'อ่านไม่สำเร็จครบ 3 ครั้ง'}</td>
              <td>{dateTime(r.resultAt)}</td>
              <td>
                <Link href={`/receipts/${r.id}`} data-testid={`unreadable-open-link-${r.id}`}>
                  เปิดใบเพื่อพิมพ์เอง
                </Link>
              </td>
            </tr>
          ))}
          {rows && rows.length === 0 ? (
            <tr>
              <td colSpan={7} className="muted">
                ไม่มีใบที่อ่านไม่ได้
              </td>
            </tr>
          ) : null}
        </tbody>
      </table>
    </>
  );
}
