"use client";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";

const STATUS_TH = { queued: "รอคิว", running: "กำลังอ่าน", done: "เสร็จ", failed: "ล้มเหลว" };
const COPY_CHOICES = [1, 5, 10, 20];
const fmtS = (v) => (v == null ? "–" : `${Number(v).toFixed(1)}`);
const fmtN = (v) => (v == null ? "–" : Number(v).toLocaleString("th-TH"));
const fmtTime = (t) => new Date(t * 1000).toLocaleTimeString("th-TH", { hour12: false });
const shortWorker = (w) => (w ? w.replace(/^.*-(gpu\d+)$/, "$1").toUpperCase() : "–");

export default function Page() {
  const [stats, setStats] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [err, setErr] = useState("");
  const [tick, setTick] = useState(0);
  const [samples, setSamples] = useState([]);
  const [picked, setPicked] = useState(new Set());
  const [uploads, setUploads] = useState([]); // {file, url}
  const [copies, setCopies] = useState(1);
  const [sending, setSending] = useState(false);
  const [batch, setBatch] = useState(null); // {ids: Map(id -> file), at, failed}
  const [filter, setFilter] = useState("all");
  const [detail, setDetail] = useState(null);
  const busy = useRef(false);

  const batchSize = batch?.ids.size || 0;
  const limit = Math.min(500, Math.max(40, batchSize + 10));

  const poll = useCallback(async () => {
    if (busy.current) return;
    busy.current = true;
    try {
      const [s, j] = await Promise.all([
        fetch("/api/stats", { cache: "no-store" }).then((r) => r.json()),
        fetch(`/api/jobs?limit=${limit}`, { cache: "no-store" }).then((r) => r.json()),
      ]);
      if (s.error || j.error) throw new Error(s.error || j.error);
      setStats(s);
      setJobs(j.jobs || []);
      setErr("");
      setTick((t) => t + 1);
    } catch (e) {
      setErr(`ติดต่อ gateway ไม่ได้: ${e.message}`);
    } finally {
      busy.current = false;
    }
  }, [limit]);

  useEffect(() => {
    poll();
    const t = setInterval(poll, 1000);
    return () => clearInterval(t);
  }, [poll]);

  useEffect(() => {
    fetch("/api/samples").then((r) => r.json()).then((d) => {
      setSamples(d.samples || []);
      setPicked(new Set(d.samples || []));
    });
  }, []);

  const jobById = useMemo(() => new Map(jobs.map((j) => [j.job_id, j])), [jobs]);
  const nowS = Date.now() / 1000;

  const nImages = picked.size + uploads.length;
  const nJobs = nImages * copies;

  async function submit() {
    if (!nImages || sending) return;
    setSending(true);
    const fd = new FormData();
    picked.forEach((n) => fd.append("sample", n));
    uploads.forEach((u) => fd.append("file", u.file, u.file.name));
    fd.append("copies", String(copies));
    try {
      const r = await fetch("/api/jobs", { method: "POST", body: fd });
      const d = await r.json();
      if (d.error) throw new Error(d.error);
      setBatch({
        ids: new Map(d.submitted.map((x) => [x.job_id, x.file])),
        at: Date.now(),
        failed: d.failed.length,
        firstError: d.failed[0]?.error,
      });
      poll();
    } catch (e) {
      setErr(`ส่งงานไม่สำเร็จ: ${e.message}`);
    } finally {
      setSending(false);
    }
  }

  function addUploads(files) {
    const next = [...files].filter((f) => f.type.startsWith("image/")).map((f) => ({ file: f, url: URL.createObjectURL(f) }));
    setUploads((u) => [...u, ...next]);
  }

  // batch progress
  let bDone = 0, bRun = 0, bFail = 0;
  if (batch) for (const id of batch.ids.keys()) {
    const s = jobById.get(id)?.status;
    if (s === "done") bDone++; else if (s === "running") bRun++; else if (s === "failed") bFail++;
  }
  const batchFinished = batch && bDone + bFail === batchSize;

  const shown = jobs.filter((j) => filter === "all" || (filter === "mine" ? batch?.ids.has(j.job_id) : j.status === filter)).slice(0, filter === "mine" ? 500 : 40);

  const q = stats?.queue_length ?? 0;
  const qMax = stats?.queue_max ?? 1000;
  const running = stats?.jobs?.running ?? 0;

  return (
    <>
      <div className="topbar">
        <div className="logo">฿</div>
        <div>
          <h1>คิวอ่านใบเสร็จ</h1>
          <div className="sub">Gateway → RabbitMQ → GPU Worker · เครื่อง vapp-lab8</div>
        </div>
        <div className="live">
          <span key={tick} className={`dot ${err ? "off" : "pulse"}`} />
          {err ? "ขาดการเชื่อมต่อ" : "สด · อัปเดตทุก 1 วินาที"}
        </div>
      </div>

      <main>
        {err && <div className="banner">{err}</div>}

        <section className="stats">
          <div className="stat hl">
            <div className="label">ความยาวคิว</div>
            <div className="value">{fmtN(stats?.queue_length)} <small>/ {fmtN(qMax)}</small></div>
            <div className="bar"><span style={{ width: `${Math.min(100, (q / qMax) * 100)}%` }} /></div>
          </div>
          <div className="stat">
            <div className="label">Worker ที่เชื่อมต่อ</div>
            <div className="value">{fmtN(stats?.workers_connected)} <small>ตัว</small></div>
          </div>
          <div className="stat">
            <div className="label">กำลังอ่าน</div>
            <div className="value">{fmtN(running)} <small>งาน</small></div>
          </div>
          <div className="stat">
            <div className="label">งานเสร็จทั้งหมด</div>
            <div className="value">{fmtN(stats?.jobs?.done)}</div>
          </div>
          <div className="stat">
            <div className="label">ใบเสร็จที่อ่านแล้ว</div>
            <div className="value">{fmtN(stats?.receipts_done)}</div>
          </div>
          <div className="stat">
            <div className="label">ล้มเหลว / Dead-letter</div>
            <div className="value">{fmtN(stats?.jobs?.failed)} <small>/ {fmtN(stats?.dead_letter_queue)}</small></div>
          </div>
        </section>

        <div className="grid2">
          <section className="panel">
            <h2>ส่งใบเสร็จเข้าคิว <span className="hint">ใบละ 1 งาน</span></h2>
            <div className="row toolbar">
              <span className="note" style={{ margin: 0 }}>ใบเสร็จตัวอย่าง {picked.size}/{samples.length}</span>
              <button className="link" onClick={() => setPicked(new Set(samples))}>เลือกทั้งหมด</button>
              <button className="link" onClick={() => setPicked(new Set())}>ล้าง</button>
            </div>
            <div className="samples">
              {samples.map((n) => {
                const on = picked.has(n);
                return (
                  <button key={n} className={`thumb ${on ? "on" : ""}`} onClick={() => {
                    const s = new Set(picked); on ? s.delete(n) : s.add(n); setPicked(s);
                  }}>
                    <img src={`/api/samples/${n}`} alt={n} loading="lazy" />
                    {on && <span className="check">✓</span>}
                    <span className="name mono">{n}</span>
                  </button>
                );
              })}
              {uploads.map((u, i) => (
                <div key={u.url} className="thumb on">
                  <img src={u.url} alt={u.file.name} />
                  <button className="x" title="เอาออก" onClick={() => setUploads(uploads.filter((_, k) => k !== i))}>✕</button>
                  <span className="name">อัปโหลด · {u.file.name}</span>
                </div>
              ))}
            </div>

            <label className="upload" style={{ marginTop: 12 }}
              onDragOver={(e) => e.preventDefault()}
              onDrop={(e) => { e.preventDefault(); addUploads(e.dataTransfer.files); }}>
              <input type="file" accept="image/*" multiple onChange={(e) => { addUploads(e.target.files); e.target.value = ""; }} />
              ⬆ อัปโหลดใบเสร็จของคุณเอง (คลิกหรือลากไฟล์มาวาง)
            </label>

            <div className="row" style={{ marginTop: 14 }}>
              <span>ส่งซ้ำชุดละ</span>
              <div className="copies">
                {COPY_CHOICES.map((c) => (
                  <button key={c} className={`chip ${copies === c ? "on" : ""}`} onClick={() => setCopies(c)}>×{c}</button>
                ))}
              </div>
              <input className="num" type="number" min={1} max={50} value={copies}
                onChange={(e) => setCopies(Math.max(1, Math.min(50, Number(e.target.value) || 1)))} />
            </div>

            <button className="primary" disabled={!nImages || sending || nJobs > 300} onClick={submit}>
              {sending ? "กำลังส่ง…" : `ส่ง ${fmtN(nJobs)} งาน`}
            </button>
            <div className="note">{nImages} ใบ × {copies} รอบ = {nJobs} งาน {nJobs > 300 && "· เกิน 300 งานต่อครั้ง"}</div>

            {batch && (
              <div className="progress">
                <div className="row" style={{ justifyContent: "space-between" }}>
                  <b>{batchFinished ? "✓ ชุดล่าสุดเสร็จครบ" : "ชุดล่าสุด"}</b>
                  <span>{bDone}/{batchSize} เสร็จ · {bRun} กำลังอ่าน{bFail ? ` · ${bFail} ล้มเหลว` : ""}</span>
                </div>
                <div className="bar"><span style={{ width: `${batchSize ? (bDone / batchSize) * 100 : 0}%` }} /></div>
                {batch.failed > 0 && <div className="note" style={{ color: "var(--bad)" }}>ส่งไม่เข้า {batch.failed} งาน: {batch.firstError}</div>}
                <button className="link" style={{ marginTop: 6 }} onClick={() => setFilter("mine")}>ดูเฉพาะงานชุดนี้ในตาราง →</button>
              </div>
            )}
          </section>

          <section className="panel">
            <h2>GPU Worker <span className="hint">{fmtN(stats?.amqp_consumers)} consumer ต่อคิวอยู่</span></h2>
            <div className="workers">
              {(stats?.workers || []).map((w) => {
                const cur = w.current_job ? jobById.get(w.current_job) : null;
                const started = cur && cur.queue_wait_seconds != null ? cur.created + cur.queue_wait_seconds : null;
                return (
                  <div key={w.worker} className={`worker ${!w.connected ? "gone" : w.current_job ? "busy" : ""}`}>
                    <div className="head">
                      <div className="gpu">GPU{w.gpu ?? "?"}</div>
                      <div>
                        <div className="wname mono">{w.worker}</div>
                        <div className="meta">{w.connected ? `ส่งสัญญาณล่าสุด ${w.last_seen_seconds_ago} วินาทีก่อน` : "ขาดการเชื่อมต่อ"}</div>
                      </div>
                    </div>
                    <div className="now">
                      {!w.connected ? <span className="badge failed">ออฟไลน์</span>
                        : w.current_job ? (
                          <>
                            <span className="badge running"><span className="spin" />กำลังอ่าน</span>{" "}
                            <span className="mono">{w.current_job}</span>
                            <div className="meta">{cur?.files?.join(", ") || ""}{started ? ` · ${Math.max(0, nowS - started).toFixed(1)} วินาที` : ""}</div>
                          </>
                        ) : <span className="badge done">ว่าง · รองานถัดไป</span>}
                    </div>
                    <div className="done"><span>ทำเสร็จแล้ว</span><span><b>{fmtN(w.jobs_done)}</b> งาน</span></div>
                  </div>
                );
              })}
              {stats && !stats.workers?.length && <div className="empty">ยังไม่มี Worker ต่อเข้ามา</div>}
            </div>

            <h2 style={{ marginTop: 22 }}>
              งานล่าสุด <span className="hint">กดงานที่เสร็จแล้วเพื่อดูรายการที่อ่านได้</span>
              <div className="filter">
                {[["all", "ทั้งหมด"], ["mine", "ชุดที่ส่ง"], ["queued", "รอคิว"], ["running", "กำลังอ่าน"], ["done", "เสร็จ"]].map(([k, t]) => (
                  <button key={k} className={`chip ${filter === k ? "on" : ""}`} onClick={() => setFilter(k)} disabled={k === "mine" && !batch}>{t}</button>
                ))}
              </div>
            </h2>
            <div className="tablewrap">
              <table>
                <thead>
                  <tr>
                    <th>งาน</th><th>ใบเสร็จ</th><th>สถานะ</th><th>Worker</th><th>ส่งเมื่อ</th>
                    <th className="r">รอคิว (วิ)</th><th className="r">อ่าน (วิ)</th><th className="r">รวม (วิ)</th>
                  </tr>
                </thead>
                <tbody>
                  {shown.map((j) => {
                    const wait = j.status === "queued" ? Math.max(0, nowS - j.created) : j.queue_wait_seconds;
                    const read = j.status === "running" && j.queue_wait_seconds != null
                      ? Math.max(0, nowS - j.created - j.queue_wait_seconds) : j.gpu_seconds;
                    return (
                      <tr key={j.job_id}
                        className={`${j.status === "done" ? "click" : ""} ${batch?.ids.has(j.job_id) ? "mine" : ""}`}
                        onClick={() => j.status === "done" && setDetail(j.job_id)}>
                        <td className="mono">{j.job_id}</td>
                        <td className="mono">{j.files.join(", ")}</td>
                        <td><span className={`badge ${j.status}`}>{j.status === "running" && <span className="spin" />}{STATUS_TH[j.status] || j.status}</span></td>
                        <td>{shortWorker(j.worker)}</td>
                        <td>{fmtTime(j.created)}</td>
                        <td className="r">{fmtS(wait)}</td>
                        <td className="r">{fmtS(read)}</td>
                        <td className="r">{fmtS(j.total_seconds)}</td>
                      </tr>
                    );
                  })}
                  {!shown.length && <tr><td colSpan={8} className="empty">ยังไม่มีงาน</td></tr>}
                </tbody>
              </table>
            </div>
          </section>
        </div>
      </main>

      {detail && <JobDetail id={detail} samples={samples} onClose={() => setDetail(null)} />}
    </>
  );
}

function JobDetail({ id, samples, onClose }) {
  const [job, setJob] = useState(null);
  const [err, setErr] = useState("");
  useEffect(() => {
    fetch(`/api/jobs/${id}`).then((r) => r.json()).then((d) => (d.error || d.detail ? setErr(d.error || d.detail) : setJob(d)));
    const esc = (e) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", esc);
    return () => window.removeEventListener("keydown", esc);
  }, [id, onClose]);

  return (
    <div className="overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <header>
          <h3>งาน <span className="mono">{id}</span></h3>
          {job && <span className={`badge ${job.status}`}>{STATUS_TH[job.status]}</span>}
          <button className="close" onClick={onClose}>ปิด ✕</button>
        </header>
        <div className="body">
          {err && <div className="banner">{err}</div>}
          {!job && !err && <div className="empty">กำลังโหลด…</div>}
          {job && (
            <>
              <div className="kv">
                <div><span>Worker</span><b className="mono">{job.worker}</b></div>
                <div><span>รอคิว</span><b>{fmtS(job.queue_wait_seconds)} วินาที</b></div>
                <div><span>อ่านบน GPU</span><b>{fmtS(job.gpu_seconds)} วินาที</b></div>
                <div><span>รวมตั้งแต่ส่ง</span><b>{fmtS(job.total_seconds)} วินาที</b></div>
              </div>
              {(job.receipts || []).map((r) => (
                <div key={r.file} className="receipt">
                  {samples.includes(r.file)
                    ? <img src={`/api/samples/${r.file}`} alt={r.file} />
                    : <div className="empty">ไฟล์อัปโหลด<br /><span className="mono">{r.file}</span></div>}
                  <div>
                    <div className="row" style={{ justifyContent: "space-between" }}>
                      <b className="mono">{r.file}</b>
                      <span className="meta">อ่าน {fmtS(r.seconds)} วินาที</span>
                    </div>
                    {!r.ok ? <div className="banner" style={{ marginTop: 8 }}>อ่านไม่สำเร็จ: {r.error || "รูปแบบผลลัพธ์ไม่ถูกต้อง"}</div> : (
                      <>
                        <table style={{ marginTop: 8 }}>
                          <thead><tr><th>#</th><th>รายการ</th><th className="r">จำนวน</th><th className="r">ราคา</th></tr></thead>
                          <tbody>
                            {r.data.items.map((it, i) => (
                              <tr key={i}><td>{i + 1}</td><td>{it.name}</td><td className="r">{fmtN(it.qty)}</td><td className="r">{fmtN(it.price)}</td></tr>
                            ))}
                            {!r.data.items.length && <tr><td colSpan={4} className="empty">ไม่พบรายการ</td></tr>}
                          </tbody>
                        </table>
                        <div className="totals">
                          <span>ก่อนภาษี {fmtN(r.data.subtotal)}</span>
                          <span>ภาษี {fmtN(r.data.tax)}</span>
                          <span>ยอดรวม <b>{fmtN(r.data.total)}</b></span>
                        </div>
                      </>
                    )}
                  </div>
                </div>
              ))}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
