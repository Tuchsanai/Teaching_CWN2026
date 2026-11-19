'use client';

// Detail of one photo from GET /api/photos/{id}; history from GET /api/photos/{id}/overrides;
// override through POST /api/photos/{id}/overrides (the API validates everything).

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useCallback, useEffect, useState, type FormEvent } from 'react';
import type { PhotoStatus, Result } from '@/lib/rules';
import PhotoWithBoxes, { type Detection } from '@/components/PhotoWithBoxes';

type Option = { value: string; label: string };

type Photo = {
  id: string;
  site: { code: string; name: string };
  upload_date: string;
  original_filename: string;
  status: PhotoStatus;
  status_label: string;
  fail_reason: string | null;
  h: number | null;
  v: number | null;
  model_result: Result | null;
  model_result_label: string | null;
  current_result: Result | null;
  current_result_label: string | null;
  is_overridden: boolean;
  model_version: string | null;
  conf_threshold: number | null;
  image_w: number | null;
  image_h: number | null;
  accepted_at: string;
  finished_at: string | null;
  image_url: string;
  detections: Detection[];
  override_count: number;
  can_override: boolean;
  can_view_history: boolean;
};

type Override = {
  id: number;
  edited_by: { full_name: string };
  edited_at: string;
  result_before: Result;
  result_before_label: string;
  result_after: Result;
  result_after_label: string;
  reason: string;
};

function thaiTime(iso: string | null): string {
  if (!iso) return '–';
  return new Date(iso).toLocaleString('th-TH', { timeZone: 'Asia/Bangkok', dateStyle: 'medium', timeStyle: 'medium' });
}

async function messageOf(res: Response, fallback: string): Promise<string> {
  const body = (await res.json().catch(() => null)) as { message?: string } | null;
  return body?.message ?? `${fallback} (รหัส ${res.status})`;
}

export default function PhotoDetail({ photoId, resultOptions }: { photoId: string; resultOptions: Option[] }) {
  const router = useRouter();
  const [photo, setPhoto] = useState<Photo | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [history, setHistory] = useState<Override[] | null>(null);
  const [historyOpen, setHistoryOpen] = useState(false);
  const [historyError, setHistoryError] = useState<string | null>(null);
  const [result, setResult] = useState('');
  const [reason, setReason] = useState('');
  const [formError, setFormError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const base = `/api/photos/${encodeURIComponent(photoId)}`;

  const loadPhoto = useCallback(async () => {
    try {
      const res = await fetch(base, { cache: 'no-store', credentials: 'same-origin' });
      if (res.status === 401) {
        window.location.assign('/login');
        return;
      }
      if (!res.ok) {
        setLoadError(await messageOf(res, 'โหลดรูปไม่สำเร็จ'));
        return;
      }
      const body = (await res.json()) as { photo: Photo };
      setPhoto(body.photo);
      setLoadError(null);
    } catch {
      setLoadError('เชื่อมต่อระบบไม่ได้ กรุณาลองใหม่');
    }
  }, [base]);

  const loadHistory = useCallback(async () => {
    try {
      const res = await fetch(`${base}/overrides`, { cache: 'no-store', credentials: 'same-origin' });
      if (!res.ok) {
        setHistoryError(await messageOf(res, 'โหลดประวัติไม่สำเร็จ'));
        return;
      }
      const body = (await res.json()) as { overrides: Override[] };
      setHistory(body.overrides);
      setHistoryError(null);
    } catch {
      setHistoryError('เชื่อมต่อระบบไม่ได้ กรุณาลองใหม่');
    }
  }, [base]);

  useEffect(() => {
    void loadPhoto();
  }, [loadPhoto]);

  // While the photo is still being checked, keep it fresh (same 2 s as the status page).
  useEffect(() => {
    if (!photo || photo.status === 'DONE' || photo.status === 'FAILED') return;
    const t = window.setInterval(() => void loadPhoto(), 2000);
    return () => window.clearInterval(t);
  }, [photo, loadPhoto]);

  function toggleHistory() {
    const open = !historyOpen;
    setHistoryOpen(open);
    if (open) void loadHistory();
  }

  function resetForm() {
    setResult('');
    setReason('');
    setFormError(null);
    setSaved(false);
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setSaving(true);
    setFormError(null);
    setSaved(false);
    try {
      const res = await fetch(`${base}/overrides`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'same-origin',
        body: JSON.stringify({ result, reason }),
      });
      if (res.status === 201) {
        setResult('');
        setReason('');
        setSaved(true);
        await loadPhoto();
        if (historyOpen) await loadHistory();
        else setHistory(null);
        router.refresh();
      } else {
        setFormError(await messageOf(res, 'แก้ผลไม่สำเร็จ'));
      }
    } catch {
      setFormError('เชื่อมต่อระบบไม่ได้ กรุณาลองใหม่');
    }
    setSaving(false);
  }

  function back() {
    if (window.history.length > 1) router.back();
    else router.push('/photos');
  }

  const backButton = (
    <button type="button" className="secondary" data-testid="photo-back" onClick={back}>
      ← กลับ
    </button>
  );

  if (loadError && !photo) {
    return (
      <div className="card">
        <p className="error" role="alert" data-testid="photo-error">
          {loadError}
        </p>
        {backButton}
      </div>
    );
  }
  if (!photo) {
    return (
      <div className="card">
        <p className="muted">กำลังโหลด…</p>
        {backButton}
      </div>
    );
  }

  return (
    <>
      <div className="row-actions" style={{ marginBottom: 12 }}>
        {backButton}
      </div>
      <div className="photo-layout">
        <div className="card">
          <PhotoWithBoxes
            src={photo.image_url}
            alt={photo.original_filename}
            imageW={photo.image_w}
            imageH={photo.image_h}
            detections={photo.detections}
          />
          {photo.status === 'DONE' && photo.detections.length === 0 && (
            <p className="muted" data-testid="photo-no-box">
              ไม่พบคนที่ไม่ใส่หมวกหรือเสื้อสะท้อนแสง
            </p>
          )}
        </div>

        <div>
          <div className="card">
            <dl className="facts">
              <dt>ไฟล์</dt>
              <dd style={{ wordBreak: 'break-all' }}>{photo.original_filename}</dd>
              <dt>ไซต์</dt>
              <dd>{photo.site.name}</dd>
              <dt>วันที่อัปโหลด</dt>
              <dd>{photo.upload_date}</dd>
              <dt>สถานะ</dt>
              <dd className={`status-${photo.status}`} data-testid="photo-status" data-status={photo.status}>
                {photo.status_label}
                {photo.fail_reason && <div className="muted">{photo.fail_reason}</div>}
              </dd>
              <dt>ไม่ใส่หมวก (H)</dt>
              <dd data-testid="photo-h">{photo.h ?? '–'}</dd>
              <dt>ไม่ใส่เสื้อสะท้อนแสง (V)</dt>
              <dd data-testid="photo-v">{photo.v ?? '–'}</dd>
              <dt>ผลของโมเดล</dt>
              <dd
                className={photo.model_result ? `result-${photo.model_result}` : 'muted'}
                data-testid="photo-model-result"
                data-result={photo.model_result ?? ''}
              >
                {photo.model_result_label ?? 'ยังไม่มีผล'}
              </dd>
              <dt>ผลล่าสุด</dt>
              <dd>
                <span
                  className={photo.current_result ? `result-${photo.current_result}` : 'muted'}
                  data-testid="photo-current-result"
                  data-result={photo.current_result ?? ''}
                >
                  {photo.current_result_label ?? 'ยังไม่มีผล'}
                </span>
                {photo.is_overridden && (
                  <span className="badge edited" data-testid="photo-edited-badge" style={{ marginLeft: 8 }}>
                    แก้ผลโดยคน
                  </span>
                )}
              </dd>
              <dt>ตรวจเสร็จเมื่อ</dt>
              <dd>{thaiTime(photo.finished_at)}</dd>
              {photo.model_version && (
                <>
                  <dt>รุ่นโมเดล</dt>
                  <dd>{photo.model_version}</dd>
                </>
              )}
            </dl>
          </div>

          {photo.can_override && (
            <form className="card override-form" onSubmit={onSubmit}>
              <h2>แก้ผล</h2>
              <label>
                ผลใหม่
                <br />
                <select
                  data-testid="override-result-select"
                  value={result}
                  onChange={(e) => setResult(e.target.value)}
                >
                  <option value="">– เลือกผล –</option>
                  {resultOptions.map((o) => (
                    <option key={o.value} value={o.value}>
                      {o.label}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                เหตุผล (ต้องใส่)
                <br />
                <textarea
                  data-testid="override-reason"
                  rows={3}
                  style={{ width: '100%' }}
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                />
              </label>
              {formError && (
                <p className="error" role="alert" data-testid="override-error">
                  {formError}
                </p>
              )}
              {saved && (
                <p className="muted" data-testid="override-saved">
                  บันทึกการแก้ผลแล้ว
                </p>
              )}
              <div className="row-actions">
                <button type="submit" data-testid="override-submit" disabled={saving}>
                  {saving ? 'กำลังบันทึก…' : 'บันทึกการแก้ผล'}
                </button>
                <button type="button" className="secondary" data-testid="override-cancel" onClick={resetForm}>
                  ยกเลิก
                </button>
              </div>
            </form>
          )}

          {photo.can_view_history && (
            <div className="card">
              <div className="row-actions" style={{ alignItems: 'center' }}>
                <h2 style={{ margin: 0 }}>ประวัติการแก้ผล ({photo.override_count})</h2>
                <button
                  type="button"
                  className="secondary"
                  data-testid="history-toggle"
                  aria-expanded={historyOpen}
                  onClick={toggleHistory}
                >
                  {historyOpen ? 'ซ่อนประวัติ' : 'แสดงประวัติ'}
                </button>
              </div>
              {historyOpen && (
                <>
                  {historyError && <p className="error">{historyError}</p>}
                  {history === null && !historyError && <p className="muted">กำลังโหลด…</p>}
                  {history && history.length === 0 && <p className="muted">ยังไม่มีการแก้ผล</p>}
                  {history && history.length > 0 && (
                    <table className="data" style={{ marginTop: 8 }}>
                      <thead>
                        <tr>
                          <th>วันและเวลา</th>
                          <th>ผู้แก้</th>
                          <th>ผลก่อนแก้</th>
                          <th>ผลหลังแก้</th>
                          <th>เหตุผล</th>
                        </tr>
                      </thead>
                      <tbody>
                        {history.map((o) => (
                          <tr key={o.id} data-testid={`history-row-${o.id}`}>
                            <td>{thaiTime(o.edited_at)}</td>
                            <td>{o.edited_by.full_name}</td>
                            <td className={`result-${o.result_before}`} data-result={o.result_before}>
                              {o.result_before_label}
                            </td>
                            <td className={`result-${o.result_after}`} data-result={o.result_after}>
                              {o.result_after_label}
                            </td>
                            <td style={{ wordBreak: 'break-word' }}>{o.reason}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  )}
                </>
              )}
            </div>
          )}
        </div>
      </div>
    </>
  );
}
