'use client';

// List of photos from GET /api/photos (FR-11, FR-12).
//   mode "all"      → /photos          : filters date, site, result, status + paging
//   mode "problems" → /photos/problems : problems=1 (only FAIL and WARN), filters date, site
// Filters live in the URL; the Server Component page re-renders with the new
// searchParams and remounts this component (key = query string).

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useEffect, useState, type FormEvent } from 'react';
import type { PhotoStatus, Result } from '@/lib/rules';

export type Filters = { date: string; site: string; result: string; status: string; page: number };
export type Option = { value: string; label: string };

type ListPhoto = {
  id: string;
  site: { code: string; name: string };
  upload_date: string;
  original_filename: string;
  status: PhotoStatus;
  status_label: string;
  fail_reason: string | null;
  h: number | null;
  v: number | null;
  current_result: Result | null;
  current_result_label: string | null;
  is_overridden: boolean;
  accepted_at: string;
};

type ListResponse = {
  page: number;
  page_size: number;
  total: number;
  pages: number;
  counts: { pass: number; warn: number; fail: number };
  photos: ListPhoto[];
};

function toQuery(f: Filters, mode: 'all' | 'problems'): URLSearchParams {
  const q = new URLSearchParams();
  if (f.date) q.set('date', f.date);
  if (f.site) q.set('site', f.site);
  if (mode === 'all' && f.result) q.set('result', f.result);
  if (mode === 'all' && f.status) q.set('status', f.status);
  if (f.page > 1) q.set('page', String(f.page));
  return q;
}

export default function PhotoList({
  mode,
  initial,
  sites,
  resultOptions,
  statusOptions,
  resultLabels,
}: {
  mode: 'all' | 'problems';
  initial: Filters;
  sites: Option[];
  resultOptions: Option[];
  statusOptions: Option[];
  resultLabels: Record<Result, string>;
}) {
  const router = useRouter();
  const basePath = mode === 'problems' ? '/photos/problems' : '/photos';
  const prefix = mode === 'problems' ? 'problems' : 'photos';
  const [form, setForm] = useState<Filters>(initial);
  const [data, setData] = useState<ListResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let alive = true;
    const q = toQuery(initial, mode);
    if (mode === 'problems') q.set('problems', '1');
    (async () => {
      try {
        const res = await fetch(`/api/photos?${q.toString()}`, { cache: 'no-store', credentials: 'same-origin' });
        if (!alive) return;
        if (res.status === 401) {
          window.location.assign('/login');
          return;
        }
        if (!res.ok) {
          const body = (await res.json().catch(() => null)) as { message?: string } | null;
          setError(body?.message ?? `โหลดรายการไม่สำเร็จ (รหัส ${res.status})`);
          setData(null);
        } else {
          setData((await res.json()) as ListResponse);
          setError(null);
        }
      } catch {
        if (alive) setError('เชื่อมต่อระบบไม่ได้ กรุณาลองใหม่');
      } finally {
        if (alive) setLoading(false);
      }
    })();
    return () => {
      alive = false;
    };
  }, [initial, mode]);

  function go(f: Filters) {
    const qs = toQuery(f, mode).toString();
    router.push(qs ? `${basePath}?${qs}` : basePath);
  }

  function onApply(e: FormEvent) {
    e.preventDefault();
    go({ ...form, page: 1 });
  }

  const page = data?.page ?? initial.page;
  const pages = data?.pages ?? 1;

  return (
    <>
      <form className="card filters" onSubmit={onApply}>
        <label>
          วันที่อัปโหลด
          <input
            type="date"
            data-testid={`${prefix}-filter-date`}
            value={form.date}
            onChange={(e) => setForm({ ...form, date: e.target.value })}
          />
        </label>
        <label>
          ไซต์
          <select
            data-testid={`${prefix}-filter-site`}
            value={form.site}
            onChange={(e) => setForm({ ...form, site: e.target.value })}
          >
            {sites.length > 1 && <option value="">ทุกไซต์</option>}
            {sites.map((s) => (
              <option key={s.value} value={s.value}>
                {s.label}
              </option>
            ))}
          </select>
        </label>
        {mode === 'all' && (
          <>
            <label>
              ผล
              <select
                data-testid="photos-filter-result"
                value={form.result}
                onChange={(e) => setForm({ ...form, result: e.target.value })}
              >
                <option value="">ทุกผล</option>
                {resultOptions.map((o) => (
                  <option key={o.value} value={o.value}>
                    {o.label}
                  </option>
                ))}
              </select>
            </label>
            <label>
              สถานะ
              <select
                data-testid="photos-filter-status"
                value={form.status}
                onChange={(e) => setForm({ ...form, status: e.target.value })}
              >
                <option value="">ทุกสถานะ</option>
                {statusOptions.map((o) => (
                  <option key={o.value} value={o.value}>
                    {o.label}
                  </option>
                ))}
              </select>
            </label>
          </>
        )}
        <button type="submit" data-testid={`${prefix}-filter-apply`}>
          กรอง
        </button>
      </form>

      <div className="counts" style={{ marginBottom: 12 }}>
        <div className="count">
          {mode === 'problems' ? 'รูปที่มีปัญหาทั้งหมด' : 'จำนวนรูป'}
          <span className="n" data-testid={`${prefix}-total-count`}>
            {data ? data.total : '–'}
          </span>
        </div>
        {mode === 'problems' && (
          <>
            <div className="count result-FAIL">
              {resultLabels.FAIL}
              <span className="n" data-testid="problems-count-fail">
                {data ? data.counts.fail : '–'}
              </span>
            </div>
            <div className="count result-WARN">
              {resultLabels.WARN}
              <span className="n" data-testid="problems-count-warn">
                {data ? data.counts.warn : '–'}
              </span>
            </div>
          </>
        )}
      </div>

      {error && (
        <p className="error" role="alert" data-testid={`${prefix}-error`}>
          {error}
        </p>
      )}
      {loading && !data && <p className="muted">กำลังโหลด…</p>}

      {data && (
        <table className="data">
          <thead>
            <tr>
              <th>วันที่</th>
              <th>ไซต์</th>
              <th>ไฟล์</th>
              <th>สถานะ</th>
              <th>ผลล่าสุด</th>
              <th className="num">H</th>
              <th className="num">V</th>
              <th>การแก้ผล</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {data.photos.length === 0 && (
              <tr>
                <td colSpan={9} className="muted" data-testid={`${prefix}-empty`}>
                  ไม่มีรูปตามเงื่อนไขที่เลือก
                </td>
              </tr>
            )}
            {data.photos.map((p) => (
              <tr key={p.id} data-testid={`photo-row-${p.id}`} data-result={p.current_result ?? ''}>
                <td>{p.upload_date}</td>
                <td>{p.site.name}</td>
                <td style={{ wordBreak: 'break-all' }}>{p.original_filename}</td>
                <td className={`status-${p.status}`}>
                  {p.status_label}
                  {p.fail_reason && <div className="muted">{p.fail_reason}</div>}
                </td>
                <td
                  className={p.current_result ? `result-${p.current_result}` : 'muted'}
                  data-testid={`photo-row-result-${p.id}`}
                  data-result={p.current_result ?? ''}
                >
                  {p.current_result_label ?? '–'}
                </td>
                <td className="num">{p.h ?? '–'}</td>
                <td className="num">{p.v ?? '–'}</td>
                <td data-testid={`photo-row-edited-${p.id}`} data-edited={p.is_overridden ? 'true' : 'false'}>
                  {p.is_overridden ? <span className="badge edited">แก้ผลโดยคน</span> : '–'}
                </td>
                <td>
                  <Link href={`/photos/${p.id}`} data-testid={`photo-open-${p.id}`}>
                    เปิดรูป
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {data && (
        <div className="pager">
          {mode === 'all' ? (
            <>
              <button
                type="button"
                className="secondary"
                data-testid="photos-page-prev"
                disabled={page <= 1}
                onClick={() => go({ ...initial, page: page - 1 })}
              >
                ก่อนหน้า
              </button>
              <span data-testid="photos-page">
                หน้า {page} / {pages}
              </span>
              <button
                type="button"
                className="secondary"
                data-testid="photos-page-next"
                disabled={page >= pages}
                onClick={() => go({ ...initial, page: page + 1 })}
              >
                ถัดไป
              </button>
            </>
          ) : (
            pages > 1 && (
              <>
                <button
                  type="button"
                  className="secondary"
                  data-testid="problems-page-prev"
                  disabled={page <= 1}
                  onClick={() => go({ ...initial, page: page - 1 })}
                >
                  ก่อนหน้า
                </button>
                <span>
                  หน้า {page} / {pages}
                </span>
                <button
                  type="button"
                  className="secondary"
                  data-testid="problems-page-next"
                  disabled={page >= pages}
                  onClick={() => go({ ...initial, page: page + 1 })}
                >
                  ถัดไป
                </button>
              </>
            )
          )}
        </div>
      )}
    </>
  );
}
