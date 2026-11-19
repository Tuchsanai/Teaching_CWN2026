'use client';

// Multi-photo upload (FR-01–FR-03). Flow (DESIGN 3):
//   1) POST /api/uploads {count} → batch_id (BR-06 is decided there)
//   2) POST /api/uploads/{batch_id}/photos — one file per request, at most 3 in flight
//   3) each file shows "รับแล้ว" or the reason it was rejected
// Limits/messages arrive as props from the Server Component (lib/rules); this file
// holds no threshold of its own.

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useEffect, useRef, useState, type ChangeEvent, type FormEvent } from 'react';

const MAX_PARALLEL = 3;

export type UploadLimits = {
  min_photos: number;
  max_photos: number;
  max_file_bytes: number;
  max_file_mb: number;
  accepted_types: string[];
};

type Messages = { tooFew: string; tooMany: string; tooLarge: string };

type ItemState = 'waiting' | 'sending' | 'accepted' | 'rejected';
type Item = { name: string; size: number; state: ItemState; message?: string };

const STATE_TEXT: Record<ItemState, string> = {
  waiting: 'รอส่ง',
  sending: 'กำลังส่ง…',
  accepted: 'รับแล้ว',
  rejected: 'ไม่รับ',
};

function formatSize(bytes: number): string {
  if (bytes >= 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  return `${Math.max(1, Math.round(bytes / 1024))} KB`;
}

async function errorMessage(res: Response): Promise<string> {
  const body = (await res.json().catch(() => null)) as { message?: string } | null;
  if (body?.message) return body.message;
  if (res.status === 401) return 'กรุณาเข้าสู่ระบบใหม่';
  if (res.status === 403) return 'บัญชีนี้ไม่มีสิทธิ์อัปโหลดรูป';
  return `ส่งไม่สำเร็จ (รหัส ${res.status})`;
}

export default function UploadForm({ limits, messages }: { limits: UploadLimits; messages: Messages }) {
  const router = useRouter();
  const inputRef = useRef<HTMLInputElement>(null);
  const [files, setFiles] = useState<File[]>([]);
  const [items, setItems] = useState<Item[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [batchId, setBatchId] = useState<string | null>(null);

  useEffect(() => {
    if (!busy) return;
    const warn = (e: BeforeUnloadEvent) => {
      e.preventDefault();
    };
    window.addEventListener('beforeunload', warn);
    return () => window.removeEventListener('beforeunload', warn);
  }, [busy]);

  function onChange(e: ChangeEvent<HTMLInputElement>) {
    const list = e.target.files ? Array.from(e.target.files) : [];
    setFiles(list);
    setItems([]);
    setError(null);
    setBatchId(null);
  }

  function clear() {
    setFiles([]);
    setItems([]);
    setError(null);
    setBatchId(null);
    if (inputRef.current) inputRef.current.value = '';
  }

  function update(index: number, patch: Partial<Item>) {
    setItems((prev) => prev.map((it, i) => (i === index ? { ...it, ...patch } : it)));
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (busy) return;
    setError(null);
    setBatchId(null);

    // Early check on the screen (BR-06); the API decides again.
    if (files.length < limits.min_photos) {
      setError(messages.tooFew);
      return;
    }
    if (files.length > limits.max_photos) {
      setError(messages.tooMany);
      return;
    }

    setBusy(true);
    const selected = files.slice();
    try {
      const res = await fetch('/api/uploads', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'same-origin',
        body: JSON.stringify({ count: selected.length }),
      });
      if (!res.ok) {
        setError(await errorMessage(res));
        setBusy(false);
        return;
      }
      const created = (await res.json()) as { batch_id: string; upload_url?: string };
      const id = created.batch_id;
      const uploadUrl = created.upload_url ?? `/api/uploads/${id}/photos`;

      // Early size check per file (BR-05): an oversized file is not sent at all.
      const initial: Item[] = selected.map((f) =>
        f.size > limits.max_file_bytes
          ? { name: f.name, size: f.size, state: 'rejected', message: messages.tooLarge }
          : { name: f.name, size: f.size, state: 'waiting' },
      );
      setItems(initial);
      const toSend = initial.map((it, i) => (it.state === 'waiting' ? i : -1)).filter((i) => i >= 0);
      let rejected = initial.length - toSend.length;

      let next = 0;
      const worker = async () => {
        while (next < toSend.length) {
          const index = toSend[next++];
          update(index, { state: 'sending' });
          try {
            const fd = new FormData();
            fd.append('file', selected[index], selected[index].name);
            const r = await fetch(uploadUrl, { method: 'POST', body: fd, credentials: 'same-origin' });
            if (r.status === 201) {
              update(index, { state: 'accepted', message: undefined });
            } else {
              rejected += 1;
              update(index, { state: 'rejected', message: await errorMessage(r) });
            }
          } catch {
            rejected += 1;
            update(index, { state: 'rejected', message: 'ส่งไม่สำเร็จ กรุณาตรวจการเชื่อมต่อแล้วลองใหม่' });
          }
        }
      };
      await Promise.all(Array.from({ length: Math.min(MAX_PARALLEL, toSend.length) }, worker));

      setBusy(false);
      if (rejected === 0) {
        router.push(`/uploads/${id}`);
      } else {
        setBatchId(id);
      }
    } catch {
      setError('เชื่อมต่อระบบไม่ได้ กรุณาลองใหม่');
      setBusy(false);
    }
  }

  const accepted = items.filter((i) => i.state === 'accepted').length;
  const rejectedCount = items.filter((i) => i.state === 'rejected').length;
  const showFiles: Item[] = items.length
    ? items
    : files.map((f) => ({ name: f.name, size: f.size, state: 'waiting' as const }));

  return (
    <form className="card" onSubmit={onSubmit}>
      <div className="filters">
        <label>
          เลือกรูป (เลือกได้หลายรูป)
          <input
            ref={inputRef}
            data-testid="upload-file-input"
            type="file"
            name="files"
            multiple
            accept={limits.accepted_types.join(',')}
            onChange={onChange}
            disabled={busy}
          />
        </label>
        <div>
          เลือกแล้ว <strong data-testid="upload-selected-count">{files.length}</strong> รูป
        </div>
        <div className="row-actions">
          <button data-testid="upload-submit" type="submit" disabled={busy}>
            {busy ? 'กำลังส่ง…' : 'ส่งรูป'}
          </button>
          <button data-testid="upload-clear" type="button" className="secondary" onClick={clear} disabled={busy}>
            ล้างรายการ
          </button>
        </div>
      </div>

      {error && (
        <p className="error" role="alert" data-testid="upload-error">
          {error}
        </p>
      )}

      {items.length > 0 && (
        <p data-testid="upload-summary">
          รับแล้ว {accepted} รูป · ไม่รับ {rejectedCount} รูป · จาก {items.length} รูป
        </p>
      )}

      {batchId && (
        <p>
          <Link href={`/uploads/${batchId}`} data-testid="upload-open-batch">
            ดูสถานะการตรวจของรูปที่รับแล้ว
          </Link>
        </p>
      )}

      {showFiles.length > 0 && (
        <ul className="file-list">
          {showFiles.map((it, i) => (
            <li key={`${i}-${it.name}`} data-testid={`upload-file-${i}`} data-state={it.state}>
              <span className="name">{it.name}</span>
              <span className="muted">{formatSize(it.size)}</span>
              <span data-testid={`upload-file-state-${i}`}>{STATE_TEXT[it.state]}</span>
              {it.state === 'rejected' && it.message && (
                <span className="error" data-testid={`upload-file-error-${i}`}>
                  {it.message}
                </span>
              )}
            </li>
          ))}
        </ul>
      )}
    </form>
  );
}
