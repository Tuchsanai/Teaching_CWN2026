'use client';
/**
 * ฟอร์มอัปโหลดชุด (W7 POST /api/batches · W6 GET /api/clients · W23 GET /api/queue)
 * testid: upload-client-select · upload-file-input · upload-urgent-checkbox (หัวหน้าเท่านั้น) · upload-submit-button
 *         upload-accepted-count · upload-error · upload-file-error-{ลำดับเริ่ม 0} · upload-full-message · upload-retry-minutes
 *         upload-queue-pending
 *
 * การตัดสิน BR-01 – BR-03 · BR-08 · BR-09 · BR-11 · BR-12 ทำที่ server (rules.ts) หน้านี้แสดงผลตามคำตอบเท่านั้น
 */
import Link from 'next/link';
import { useCallback, useEffect, useRef, useState } from 'react';
import type { FormEvent } from 'react';
import { api, errorText } from '../_ui/api';
import type { ApiErrorBody } from '../_ui/api';
import QueueFull from '../_ui/QueueFull';
import { useClients } from '../_ui/useClients';

interface QueueInfo {
  normal: { pending: number; limit: number; room: number; full: boolean; retryAfterMinutesIfFull: number | null };
  urgent: { usedToday: number; limitPerDay: number; remainingToday: number; canSetMore: boolean; maxReceipts: number };
}

interface UploadOk {
  batchId: string;
  accepted: number;
  priority: 'normal' | 'urgent';
  queue: { pendingNormal: number; limit: number };
  urgentUsedToday?: number;
  message: string;
}

type Outcome =
  | { kind: 'ok'; data: UploadOk; sent: number }
  | { kind: 'full'; error: ApiErrorBody }
  | { kind: 'error'; error: ApiErrorBody };

export default function UploadForm({ canSetUrgent }: { canSetUrgent: boolean }) {
  const { clients, error: clientsError } = useClients();
  const [clientId, setClientId] = useState('');
  const [files, setFiles] = useState<File[]>([]);
  const [urgent, setUrgent] = useState(false);
  const [busy, setBusy] = useState(false);
  const [outcome, setOutcome] = useState<Outcome | null>(null);
  const [queue, setQueue] = useState<QueueInfo | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const loadQueue = useCallback(async () => {
    const r = await api<QueueInfo>('/api/queue');
    if (r.ok) setQueue(r.data);
  }, []);

  useEffect(() => {
    loadQueue();
    const t = setInterval(loadQueue, 15_000);
    return () => clearInterval(t);
  }, [loadQueue]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setOutcome(null);
    if (!clientId) {
      setOutcome({ kind: 'error', error: { error: 'client_required', message: 'กรุณาเลือกลูกค้าของชุดนี้' } });
      return;
    }
    const form = new FormData();
    form.set('clientId', clientId);
    if (canSetUrgent && urgent) form.set('urgent', 'true');
    for (const f of files) form.append('files', f, f.name);
    setBusy(true);
    const r = await api<UploadOk>('/api/batches', { method: 'POST', body: form });
    setBusy(false);
    if (r.ok) {
      setOutcome({ kind: 'ok', data: r.data, sent: files.length });
      setFiles([]);
      setUrgent(false);
      if (fileRef.current) fileRef.current.value = '';
    } else if (r.status === 429 || r.error.error === 'queue_full') {
      setOutcome({ kind: 'full', error: r.error });
    } else {
      setOutcome({ kind: 'error', error: r.error });
    }
    loadQueue();
  }

  const urgentBlocked = queue ? !queue.urgent.canSetMore : false;

  return (
    <>
      <div className="stats" style={{ marginBottom: 16 }}>
        <div className="stat">
          <div className="label">ใบงานปกติที่ค้างในคิว</div>
          <div className="value">
            <span data-testid="upload-queue-pending">{queue ? queue.normal.pending : '…'}</span>
            <span className="muted" style={{ fontSize: 14 }}> / {queue ? queue.normal.limit : 400}</span>
          </div>
        </div>
        {canSetUrgent && queue ? (
          <div className="stat">
            <div className="label">งานด่วนที่ใช้ไปวันนี้</div>
            <div className="value">
              {queue.urgent.usedToday}
              <span className="muted" style={{ fontSize: 14 }}> / {queue.urgent.limitPerDay}</span>
            </div>
          </div>
        ) : null}
      </div>

      <form className="card" onSubmit={onSubmit} noValidate>
        <div className="row">
          <label className="field">
            ลูกค้า (ร้าน)
            <select data-testid="upload-client-select" value={clientId} onChange={(e) => setClientId(e.target.value)}>
              <option value="">— เลือกลูกค้า —</option>
              {clients.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.code} · {c.name}
                </option>
              ))}
            </select>
          </label>
          <label className="field">
            ไฟล์ใบเสร็จ (JPG · PNG · PDF 1 หน้า · ไม่เกิน 10 MB ต่อไฟล์ · 1–100 ไฟล์)
            <input
              ref={fileRef}
              type="file"
              multiple
              data-testid="upload-file-input"
              onChange={(e) => setFiles(Array.from(e.target.files ?? []))}
            />
          </label>
        </div>
        {clientsError ? <div className="notice error">{clientsError}</div> : null}
        <p className="muted">เลือกแล้ว {files.length} ไฟล์</p>
        {canSetUrgent ? (
          <label style={{ display: 'block', margin: '8px 0' }}>
            <input
              type="checkbox"
              data-testid="upload-urgent-checkbox"
              checked={urgent}
              onChange={(e) => setUrgent(e.target.checked)}
            />{' '}
            งานด่วน (ไม่เกิน {queue?.urgent.maxReceipts ?? 10} ใบต่อชุด · ไม่เกิน {queue?.urgent.limitPerDay ?? 5} งานต่อวัน)
            {urgentBlocked ? <span className="badge bad">วันนี้ใช้ครบแล้ว</span> : null}
          </label>
        ) : null}
        <button type="submit" data-testid="upload-submit-button" disabled={busy}>
          {busy ? 'กำลังส่ง…' : 'ส่งชุดนี้'}
        </button>
      </form>

      {outcome?.kind === 'ok' ? (
        <div className="notice ok" role="status">
          รับแล้ว <strong data-testid="upload-accepted-count">{outcome.data.accepted}</strong> ใบ (ส่ง {outcome.sent} ไฟล์)
          {outcome.data.priority === 'urgent' ? <span className="badge urgent">ด่วน</span> : null}
          {' · '}
          <Link href={`/batches/${outcome.data.batchId}`}>ดูสถานะชุดนี้</Link>
          <div className="muted" style={{ fontSize: 13 }}>ระบบอ่านต่อเบื้องหลัง ออกจากหน้านี้ได้ทันที</div>
        </div>
      ) : null}

      {outcome?.kind === 'full' ? (
        <>
          <QueueFull
            minutes={outcome.error.retryAfterMinutes}
            testId="upload-full-message"
            minutesTestId="upload-retry-minutes"
          />
          <p className="muted">
            รับแล้ว <span data-testid="upload-accepted-count">0</span> ใบ
          </p>
        </>
      ) : null}

      {outcome?.kind === 'error' ? (
        <div className="notice error" role="alert">
          <div data-testid="upload-error">{errorText(outcome.error)}</div>
          {outcome.error.files?.length ? (
            <ul className="file-errors">
              {outcome.error.files.map((f) => (
                <li key={f.index} data-testid={`upload-file-error-${f.index}`}>
                  ไฟล์ที่ {f.index + 1} “{f.name}”: {f.message}
                </li>
              ))}
            </ul>
          ) : null}
          <div className="muted" style={{ fontSize: 13, marginTop: 4 }}>
            รับแล้ว <span data-testid="upload-accepted-count">0</span> ใบ — ทั้งชุดไม่ถูกรับ แก้ไฟล์แล้วส่งใหม่ทั้งชุด
          </div>
        </div>
      ) : null}
    </>
  );
}
