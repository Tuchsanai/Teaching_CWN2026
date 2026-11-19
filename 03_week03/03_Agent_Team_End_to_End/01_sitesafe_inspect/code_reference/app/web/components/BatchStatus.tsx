'use client';

// Polls GET /api/uploads/{batchId} every 2 seconds while the page is open.
// Status and result texts come from the API response (status_label, current_result_label).

import Link from 'next/link';
import { useCallback, useEffect, useRef, useState } from 'react';
import type { PhotoStatus, Result } from '@/lib/rules';

const POLL_MS = 2000;

type BatchPhoto = {
  id: string;
  original_filename: string;
  status: PhotoStatus;
  status_label: string;
  fail_reason: string | null;
  h: number | null;
  v: number | null;
  current_result: Result | null;
  current_result_label: string | null;
  is_overridden: boolean;
};

type BatchResponse = {
  batch: {
    id: string;
    site: { code: string; name: string };
    declared_count: number;
    created_at: string;
    uploaded_by: { full_name: string };
  };
  accepted_count: number;
  counts: { queued: number; processing: number; done: number; failed: number };
  photos: BatchPhoto[];
};

export default function BatchStatus({
  batchId,
  statusLabels,
}: {
  batchId: string;
  statusLabels: Record<PhotoStatus, string>;
}) {
  const [data, setData] = useState<BatchResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [notFound, setNotFound] = useState(false);
  const [updatedAt, setUpdatedAt] = useState<Date | null>(null);
  const inFlight = useRef(false);

  const load = useCallback(async () => {
    if (inFlight.current) return;
    inFlight.current = true;
    try {
      const res = await fetch(`/api/uploads/${encodeURIComponent(batchId)}`, {
        cache: 'no-store',
        credentials: 'same-origin',
      });
      if (res.status === 401) {
        window.location.assign('/login');
        return;
      }
      if (res.status === 404) {
        setNotFound(true);
        return;
      }
      if (!res.ok) {
        const body = (await res.json().catch(() => null)) as { message?: string } | null;
        setError(body?.message ?? `โหลดสถานะไม่สำเร็จ (รหัส ${res.status})`);
        return;
      }
      setData((await res.json()) as BatchResponse);
      setError(null);
      setUpdatedAt(new Date());
    } catch {
      setError('เชื่อมต่อระบบไม่ได้ จะลองใหม่อัตโนมัติ');
    } finally {
      inFlight.current = false;
    }
  }, [batchId]);

  useEffect(() => {
    void load();
    const t = window.setInterval(() => void load(), POLL_MS);
    return () => window.clearInterval(t);
  }, [load]);

  if (notFound) {
    return (
      <div className="card" data-testid="batch-not-found">
        ไม่พบการอัปโหลดนี้ หรือบัญชีนี้ไม่มีสิทธิ์เห็นข้อมูลนี้
      </div>
    );
  }

  const c = data?.counts ?? { queued: 0, processing: 0, done: 0, failed: 0 };

  return (
    <>
      <div className="card">
        {data && (
          <p className="muted">
            ไซต์ {data.batch.site.name} · ผู้อัปโหลด {data.batch.uploaded_by.full_name} · แจ้งจำนวนไว้{' '}
            {data.batch.declared_count} รูป
          </p>
        )}
        <div className="counts">
          <div className="count">
            รูปที่ระบบรับแล้ว
            <span className="n" data-testid="batch-accepted-count">
              {data ? data.accepted_count : '–'}
            </span>
          </div>
          <div className="count status-QUEUED">
            {statusLabels.QUEUED}
            <span className="n" data-testid="batch-count-queued">{c.queued}</span>
          </div>
          <div className="count status-PROCESSING">
            {statusLabels.PROCESSING}
            <span className="n" data-testid="batch-count-processing">{c.processing}</span>
          </div>
          <div className="count status-DONE">
            {statusLabels.DONE}
            <span className="n" data-testid="batch-count-done">{c.done}</span>
          </div>
          <div className="count status-FAILED">
            {statusLabels.FAILED}
            <span className="n" data-testid="batch-count-failed">{c.failed}</span>
          </div>
        </div>
        <div className="pager">
          <button type="button" className="secondary" data-testid="batch-refresh" onClick={() => void load()}>
            โหลดใหม่
          </button>
          <span className="muted">
            อัปเดตอัตโนมัติทุก 2 วินาที
            {updatedAt && ` · ล่าสุด ${updatedAt.toLocaleTimeString('th-TH', { timeZone: 'Asia/Bangkok' })}`}
          </span>
        </div>
        {error && (
          <p className="error" role="alert" data-testid="batch-error">
            {error}
          </p>
        )}
      </div>

      {data && (
        <table className="data">
          <thead>
            <tr>
              <th>#</th>
              <th>ไฟล์</th>
              <th>สถานะ</th>
              <th>ผล</th>
              <th className="num">H</th>
              <th className="num">V</th>
              <th>เหตุผล</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {data.photos.length === 0 && (
              <tr>
                <td colSpan={8} className="muted">
                  ยังไม่มีรูปที่ระบบรับ
                </td>
              </tr>
            )}
            {data.photos.map((p, i) => (
              <tr key={p.id} data-testid={`batch-row-${p.id}`} data-status={p.status}>
                <td>{i + 1}</td>
                <td style={{ wordBreak: 'break-all' }}>{p.original_filename}</td>
                <td className={`status-${p.status}`} data-testid={`batch-row-status-${p.id}`} data-status={p.status}>
                  {p.status_label}
                </td>
                <td>
                  <span
                    className={p.current_result ? `result-${p.current_result}` : 'muted'}
                    data-testid={`batch-row-result-${p.id}`}
                    data-result={p.current_result ?? ''}
                  >
                    {p.current_result_label ?? '–'}
                  </span>
                  {p.is_overridden && (
                    <span className="badge edited" style={{ marginLeft: 6 }}>
                      แก้ผลแล้ว
                    </span>
                  )}
                </td>
                <td className="num">{p.h ?? '–'}</td>
                <td className="num">{p.v ?? '–'}</td>
                <td data-testid={`batch-row-reason-${p.id}`}>{p.fail_reason ?? ''}</td>
                <td>
                  <Link href={`/photos/${p.id}`} data-testid={`batch-open-photo-${p.id}`}>
                    เปิดรูป
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </>
  );
}
