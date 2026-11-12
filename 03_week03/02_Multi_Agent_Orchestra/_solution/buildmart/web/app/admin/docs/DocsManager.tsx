'use client';
// จัดการเอกสาร RAG: อัปโหลด PDF → คิว rag.ingest → rag-worker ตัด chunk + ทำเวกเตอร์ · ตารางอัปเดตเองทุก 2 วิ
import { useCallback, useEffect, useRef, useState } from 'react';

type Doc = {
  id: number;
  filename: string;
  pages: number | null;
  chunks: number;
  status: 'queued' | 'processing' | 'ready' | 'failed';
  error: string | null;
  size: number;
  createdAt: string;
  updatedAt: string;
};

const STATUS_TH: Record<string, string> = {
  queued: 'รอคิว',
  processing: 'กำลังประมวลผล',
  ready: 'พร้อมใช้',
  failed: 'ล้มเหลว',
};
const MAX = 10 * 1024 * 1024;
const kb = (n: number) => (n >= 1024 * 1024 ? `${(n / 1024 / 1024).toFixed(1)} MB` : `${Math.max(1, Math.round(n / 1024))} KB`);
const thTime = (iso: string) =>
  new Date(iso).toLocaleString('th-TH', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit', second: '2-digit' });

export default function DocsManager() {
  const [docs, setDocs] = useState<Doc[] | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<{ ok: boolean; text: string } | null>(null);
  const [confirmId, setConfirmId] = useState<number | null>(null);
  const [drag, setDrag] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const load = useCallback(async () => {
    const r = await fetch('/api/admin/docs', { cache: 'no-store' });
    if (r.status === 401) return window.location.reload();
    if (r.ok) setDocs((await r.json()).items);
  }, []);

  useEffect(() => {
    load().catch(() => {});
    const t = setInterval(() => load().catch(() => {}), 2000);
    return () => clearInterval(t);
  }, [load]);

  function pick(f: File | null | undefined) {
    setMsg(null);
    if (!f) return setFile(null);
    if (!/\.pdf$/i.test(f.name)) {
      setMsg({ ok: false, text: 'รับเฉพาะไฟล์ .pdf' });
      return setFile(null);
    }
    if (f.size > MAX) {
      setMsg({ ok: false, text: `ไฟล์ใหญ่เกิน 10MB (${kb(f.size)})` });
      return setFile(null);
    }
    setFile(f);
  }

  async function upload() {
    if (!file) return;
    setBusy(true);
    setMsg(null);
    const fd = new FormData();
    fd.append('file', file);
    try {
      const r = await fetch('/api/admin/docs', { method: 'POST', body: fd });
      const j = await r.json().catch(() => ({}));
      if (r.ok) {
        setMsg({
          ok: true,
          text: `${j.replaced ? 'แทนที่' : 'อัปโหลด'} ${j.filename} แล้ว — เข้าคิว rag.ingest รอ rag-worker ทำ RAG`,
        });
        setFile(null);
        if (inputRef.current) inputRef.current.value = '';
        load();
      } else {
        setMsg({ ok: false, text: j.error || `อัปโหลดไม่สำเร็จ (${r.status})` });
      }
    } catch {
      setMsg({ ok: false, text: 'เชื่อมต่อเซิร์ฟเวอร์ไม่ได้' });
    }
    setBusy(false);
  }

  async function remove(d: Doc) {
    setConfirmId(null);
    const r = await fetch(`/api/admin/docs/${d.id}`, { method: 'DELETE' });
    setMsg(r.ok ? { ok: true, text: `ลบ ${d.filename} แล้ว (chunk ทั้งหมดถูกลบด้วย)` } : { ok: false, text: 'ลบไม่สำเร็จ' });
    load();
  }

  async function reindex(d: Doc) {
    const r = await fetch(`/api/admin/docs/${d.id}`, { method: 'POST' });
    setMsg(r.ok ? { ok: true, text: `ส่ง ${d.filename} เข้าคิวทำใหม่แล้ว` } : { ok: false, text: 'ส่งเข้าคิวไม่สำเร็จ' });
    load();
  }

  const total = docs?.reduce((n, d) => n + d.chunks, 0) ?? 0;
  const ready = docs?.filter((d) => d.status === 'ready').length ?? 0;

  return (
    <div className="adm-page">
      <section className="adm-grid-2 docs-top">
        <div className="card">
          <div className="adm-card-head">
            <h2>📤 อัปโหลดเอกสาร PDF</h2>
            <span className="muted">≤ 10MB · เฉพาะ .pdf</span>
          </div>
          <label
            className={`adm-drop ${drag ? 'drag' : ''} ${file ? 'has-file' : ''}`}
            onDragOver={(e) => {
              e.preventDefault();
              setDrag(true);
            }}
            onDragLeave={() => setDrag(false)}
            onDrop={(e) => {
              e.preventDefault();
              setDrag(false);
              pick(e.dataTransfer.files?.[0]);
            }}
          >
            <input
              ref={inputRef}
              type="file"
              accept=".pdf,application/pdf"
              data-testid="doc-upload-input"
              onChange={(e) => pick(e.target.files?.[0])}
            />
            <span className="adm-drop-icon" aria-hidden>
              📄
            </span>
            {file ? (
              <span>
                <b>{file.name}</b> <span className="muted">({kb(file.size)})</span>
              </span>
            ) : (
              <span>
                ลากไฟล์มาวาง หรือ <u>คลิกเพื่อเลือกไฟล์</u>
              </span>
            )}
          </label>
          <div className="adm-upload-row">
            <button type="button" className="btn" data-testid="doc-upload-btn" disabled={!file || busy} onClick={upload}>
              {busy ? 'กำลังอัปโหลด…' : 'อัปโหลดและทำ RAG'}
            </button>
            <span className="muted small">ชื่อไฟล์ซ้ำ = แทนที่ของเดิมและทำ chunk ใหม่</span>
          </div>
          {msg && <div className={msg.ok ? 'adm-ok' : 'adm-error'}>{msg.text}</div>}
        </div>
        <div className="card adm-howto">
          <h2>ทำงานอย่างไร</h2>
          <ol>
            <li>web บันทึกไฟล์ลงตาราง <code>docs</code> (bytea) สถานะ <b>queued</b></li>
            <li>
              ส่งข้อความ <code>{'{docId}'}</code> เข้าคิว <code>rag.ingest</code> (RabbitMQ)
            </li>
            <li>
              <b>rag-worker</b> อ่าน PDF → ตัด chunk → ขอเวกเตอร์จาก embedder → บันทึก <code>doc_chunks</code> แล้วเป็น{' '}
              <b>ready</b>
            </li>
            <li>แชทบอทค้นแบบ Hybrid (เวกเตอร์ + คำค้น) แล้วแสดงป้ายอ้างอิงเอกสาร</li>
          </ol>
          <p className="muted small">
            เอกสาร {docs?.length ?? 0} ไฟล์ · พร้อมใช้ {ready} · รวม {total.toLocaleString()} chunk
          </p>
        </div>
      </section>

      <section className="card">
        <div className="adm-card-head">
          <h2>📚 เอกสารทั้งหมด</h2>
          <span className="muted small">อัปเดตอัตโนมัติทุก 2 วินาที</span>
        </div>
        <div className="adm-table-wrap">
          <table className="adm-table">
            <thead>
              <tr>
                <th>ชื่อไฟล์</th>
                <th className="num">หน้า</th>
                <th className="num">chunk</th>
                <th>สถานะ</th>
                <th>อัปเดตล่าสุด</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {docs === null && (
                <tr>
                  <td colSpan={6} className="muted adm-empty">
                    กำลังโหลด…
                  </td>
                </tr>
              )}
              {docs?.length === 0 && (
                <tr>
                  <td colSpan={6} className="muted adm-empty">
                    ยังไม่มีเอกสาร — อัปโหลด PDF ด้านบน
                  </td>
                </tr>
              )}
              {docs?.map((d) => (
                <tr key={d.id} data-testid="doc-row" data-filename={d.filename} data-status={d.status}>
                  <td>
                    <a href={`/api/docs/${encodeURIComponent(d.filename)}`} target="_blank" rel="noreferrer" className="mono">
                      {d.filename}
                    </a>
                    <div className="muted small">{kb(d.size)}</div>
                  </td>
                  <td className="num">{d.pages ?? '–'}</td>
                  <td className="num" data-testid="doc-chunks">
                    {d.chunks}
                  </td>
                  <td>
                    <span className={`adm-doc-st ds-${d.status}`}>
                      {(d.status === 'queued' || d.status === 'processing') && <span className="adm-spin" aria-hidden />}
                      <span data-testid="doc-status" data-status={d.status}>
                        {d.status}
                      </span>
                    </span>
                    <span className="muted small"> {STATUS_TH[d.status]}</span>
                    {d.error && <div className="adm-doc-err small">{d.error}</div>}
                  </td>
                  <td className="small muted">{thTime(d.updatedAt)}</td>
                  <td className="adm-actions">
                    {confirmId === d.id ? (
                      <>
                        <button type="button" className="btn adm-danger" data-testid="doc-delete-confirm" onClick={() => remove(d)}>
                          ยืนยันลบ
                        </button>
                        <button type="button" className="btn secondary" onClick={() => setConfirmId(null)}>
                          ยกเลิก
                        </button>
                      </>
                    ) : (
                      <>
                        <button type="button" className="btn secondary" data-testid="doc-reindex" onClick={() => reindex(d)}
                          disabled={d.status === 'queued' || d.status === 'processing'} title="ทำ chunk + เวกเตอร์ใหม่">
                          ↻ ทำใหม่
                        </button>
                        <button type="button" className="btn secondary adm-danger-text" data-testid="doc-delete"
                          onClick={() => setConfirmId(d.id)}>
                          🗑 ลบ
                        </button>
                      </>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
