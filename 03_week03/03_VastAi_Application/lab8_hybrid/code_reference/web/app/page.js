"use client";
import { useCallback, useEffect, useRef, useState } from "react";

const HISTORY = 120; // จุดบนกราฟ (1 จุดต่อวินาที = 2 นาทีล่าสุด)
const BATCHES = [
  { count: 20, priority: "normal", label: "ส่ง 20 งาน" },
  { count: 60, priority: "normal", label: "ส่ง 60 งาน" },
  { count: 500, priority: "normal", label: "ส่ง 500 งาน" },
  { count: 5, priority: "express", label: "งานด่วน 5 งาน" },
];

const fmtSec = (s) => (s == null ? "–" : s < 60 ? `${(+s).toFixed(1)} วินาที` : `${Math.floor(s / 60)} นาที ${Math.round(s % 60)} วินาที`);
const clock = () => new Date().toLocaleTimeString("th-TH", { hour12: false });

function QueueChart({ points }) {
  const W = 600, H = 190, P = { l: 38, r: 10, t: 12, b: 22 };
  const caps = points.map((p) => p.cap || 0);
  const vals = points.map((p) => p.q);
  const maxY = Math.max(10, ...vals, ...caps.map((c) => c * 1.15));
  const x = (i) => P.l + (i / Math.max(1, HISTORY - 1)) * (W - P.l - P.r);
  const y = (v) => H - P.b - (v / maxY) * (H - P.t - P.b);
  const off = HISTORY - points.length;
  const path = (arr) => arr.map((v, i) => `${i ? "L" : "M"}${x(i + off).toFixed(1)},${y(v).toFixed(1)}`).join(" ");
  const ticks = [0, 0.25, 0.5, 0.75, 1].map((f) => Math.round(maxY * f));
  const lastCap = caps[caps.length - 1];
  return (
    <svg className="chart" viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="none" role="img" aria-label="กราฟความยาวคิว">
      {ticks.map((t) => (
        <g key={t}>
          <line x1={P.l} x2={W - P.r} y1={y(t)} y2={y(t)} stroke="#2a2f40" strokeWidth="1" />
          <text x={P.l - 6} y={y(t) + 4} fill="#9097ad" fontSize="11" textAnchor="end">{t}</text>
        </g>
      ))}
      <text x={P.l} y={H - 5} fill="#9097ad" fontSize="11">−2 นาที</text>
      <text x={W - P.r} y={H - 5} fill="#9097ad" fontSize="11" textAnchor="end">ตอนนี้</text>
      {points.length > 1 && (
        <>
          <path d={`${path(vals)} L${x(HISTORY - 1)},${y(0)} L${x(off)},${y(0)} Z`} fill="rgba(108,184,255,.15)" />
          <path d={path(vals)} fill="none" stroke="#6cb8ff" strokeWidth="2" vectorEffect="non-scaling-stroke" />
          <path d={path(caps)} fill="none" stroke="#ff6b6b" strokeWidth="1.5" strokeDasharray="6 4" vectorEffect="non-scaling-stroke" />
        </>
      )}
      {lastCap ? (
        <text x={W - P.r - 4} y={y(lastCap) - 5} fill="#ff6b6b" fontSize="11" textAnchor="end">เพดานคิว {lastCap}</text>
      ) : null}
    </svg>
  );
}

function WorkerCard({ w }) {
  const busy = w.alive && (w.working > 0 || w.state === "busy");
  const cls = !w.alive ? "down" : busy ? "busy" : "idle";
  const st = !w.alive ? "หยุดทำงาน" : busy ? `กำลังสร้าง ${Math.max(1, w.working)} ภาพ` : "ว่าง";
  return (
    <div className={`worker ${cls}`}>
      <div className="name"><span className="gpu-ico" /> GPU Worker · {w.name}</div>
      <div className="st"><span className={`dot ${w.alive ? "ok" : "bad"}`} /> {st}</div>
      <div className="meta">สร้างเสร็จแล้ว {w.done?.toLocaleString() ?? 0} ภาพ · สัญญาณล่าสุด {w.last_seen_sec_ago} วินาทีก่อน</div>
      {busy && <div className="bar" style={{ width: "100%" }} />}
    </div>
  );
}

export default function Page() {
  const [stats, setStats] = useState(null);
  const [connErr, setConnErr] = useState("");
  const [hist, setHist] = useState([]);
  const [prompt, setPrompt] = useState("a white lighthouse on a rocky coast at sunset, photo");
  const [express, setExpress] = useState(false);
  const [job, setJob] = useState(null); // {phase, id, ahead, eta, priority, startedAt, status, seconds, worker, image, error, retry}
  const [now, setNow] = useState(Date.now());
  const [retryUntil, setRetryUntil] = useState(0);
  const [batchBusy, setBatchBusy] = useState(null);
  const [batchLog, setBatchLog] = useState([]);
  const polling = useRef(0);

  // ตัวเลขสด: ดึง /api/stats ทุก 1 วินาที
  useEffect(() => {
    let alive = true;
    async function tick() {
      try {
        const r = await fetch("/api/stats", { cache: "no-store" });
        const s = await r.json();
        if (!alive) return;
        if (!r.ok) throw new Error(s.error || r.status);
        setStats(s); setConnErr("");
        const q = (s.waiting?.normal || 0) + (s.waiting?.express || 0);
        setHist((h) => [...h, { q, cap: s.cap }].slice(-HISTORY));
      } catch (e) {
        if (alive) setConnErr(String(e.message || e));
      }
    }
    tick();
    const t = setInterval(tick, 1000);
    return () => { alive = false; clearInterval(t); };
  }, []);

  useEffect(() => { const t = setInterval(() => setNow(Date.now()), 200); return () => clearInterval(t); }, []);

  const follow = useCallback(async (id) => {
    const token = ++polling.current;
    for (let i = 0; i < 60 && token === polling.current; i++) {
      try {
        const r = await fetch(`/api/jobs/${id}`, { cache: "no-store" });
        const s = await r.json();
        if (token !== polling.current) return;
        if (s.status === "done") {
          setJob((j) => ({ ...j, phase: "done", status: "done", seconds: s.seconds, worker: s.worker, image: s.image_url, finishedAt: Date.now() }));
          return;
        }
        if (s.status === "dead") {
          setJob((j) => ({ ...j, phase: "error", error: "งานนี้สร้างไม่สำเร็จ (ย้ายไป Dead-letter queue)" }));
          return;
        }
        setJob((j) => ({ ...j, status: s.status, worker: s.worker }));
      } catch {
        await new Promise((res) => setTimeout(res, 1000));
      }
    }
  }, []);

  async function submit(e) {
    e?.preventDefault();
    if (!prompt.trim()) return;
    const priority = express ? "express" : "normal";
    setJob({ phase: "sending", priority, startedAt: Date.now() });
    try {
      const r = await fetch("/api/jobs", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt, priority }),
      });
      const s = await r.json();
      if (r.status === 429) {
        const sec = s.retry_after_seconds || 1;
        setRetryUntil(Date.now() + sec * 1000);
        setJob({ phase: "full", retry: sec, cap: s.cap, waiting: s.normal_waiting });
        return;
      }
      if (!r.ok) throw new Error(s.error || `HTTP ${r.status}`);
      setJob({ phase: "queued", id: s.job_id, ahead: s.jobs_ahead, eta: s.eta_seconds, priority, startedAt: Date.now(), status: "queued" });
      follow(s.job_id);
    } catch (err) {
      setJob({ phase: "error", error: String(err.message || err) });
    }
  }

  async function runBatch(b) {
    setBatchBusy(b.label);
    try {
      const r = await fetch("/api/batch", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ count: b.count, priority: b.priority }),
      });
      const s = await r.json();
      if (!r.ok) throw new Error(s.error || `HTTP ${r.status}`);
      setBatchLog((l) => [{ ...s, label: b.label, at: clock() }, ...l].slice(0, 20));
    } catch (err) {
      setBatchLog((l) => [{ label: b.label, at: clock(), error: String(err.message || err) }, ...l].slice(0, 20));
    } finally {
      setBatchBusy(null);
    }
  }

  const retryLeft = Math.max(0, Math.ceil((retryUntil - now) / 1000));
  const waiting = stats ? (stats.waiting?.normal || 0) + (stats.waiting?.express || 0) : 0;
  const elapsed = job?.startedAt ? ((job.finishedAt || now) - job.startedAt) / 1000 : 0;
  const workers = stats?.workers || [];
  const liveN = workers.filter((w) => w.alive).length;

  return (
    <main className="wrap">
      <header className="top">
        <div className="brand">
          <div className="logo">{Array.from({ length: 9 }, (_, i) => <i key={i} />)}</div>
          <div>
            <h1>PixelQueue</h1>
            <p>ห้องสร้างภาพจากข้อความ · ทุกงานเข้าคิวแล้วให้ GPU หยิบไปวาด</p>
          </div>
        </div>
        <div className="conn">
          <span className={`dot ${connErr ? "bad" : stats ? "ok" : ""}`} />
          {connErr ? "ติดต่อระบบคิวไม่ได้" : stats ? `เชื่อมต่อแล้ว · GPU พร้อม ${liveN}/${workers.length} ตัว · ${stats.sec_per_image} วินาที/ภาพ` : "กำลังเชื่อมต่อ…"}
        </div>
      </header>

      <div className="grid">
        {/* ---- สร้างภาพ 1 งาน ---- */}
        <section className="card">
          <h2>สร้างภาพ <small>คำบรรยายภาษาอังกฤษได้ผลดีที่สุด</small></h2>
          <form onSubmit={submit}>
            <textarea value={prompt} maxLength={500} onChange={(e) => setPrompt(e.target.value)}
              placeholder="เช่น a tabby cat sleeping on a windowsill in morning light, photo" />
            <div className="row">
              <label className="toggle">
                <input type="checkbox" checked={express} onChange={(e) => setExpress(e.target.checked)} />
                ⚡ งานด่วน (ลัดคิว)
              </label>
              <span className="spacer" />
              <button className="btn" type="submit"
                disabled={!prompt.trim() || job?.phase === "sending" || job?.phase === "queued" || (retryLeft > 0 && !express)}>
                {retryLeft > 0 && !express ? `คิวเต็ม · ลองใหม่ใน ${retryLeft} วิ` : job?.phase === "queued" ? "กำลังสร้าง…" : "สร้างภาพ"}
              </button>
            </div>
          </form>

          {job?.phase === "full" && (
            <div className="status full">
              คิวเต็มแล้ว (งานรอ {job.waiting} งาน จากเพดาน {job.cap}) · ควรลองใหม่ในอีก <b>{job.retry} วินาที</b>
              {retryLeft > 0 ? ` (เหลือ ${retryLeft} วินาที)` : " — ลองใหม่ได้แล้ว"} · หรือเลือกงานด่วนเพื่อลัดคิว
            </div>
          )}
          {job?.phase === "error" && <div className="status err">เกิดข้อผิดพลาด: {job.error}</div>}
          {job?.phase === "sending" && <div className="status">กำลังส่งงานเข้าคิว…</div>}

          {(job?.phase === "queued" || job?.phase === "done") && (
            <div className="result">
              {job.phase === "done" ? <img src={job.image} alt={prompt} /> :
                <div className="ph shimmer">{job.status === "running" ? `GPU ${job.worker || ""} กำลังวาด…` : "รอในคิว…"}</div>}
              <div>
                <div className="status" style={{ marginTop: 0 }}>
                  {job.phase === "done"
                    ? <>เสร็จแล้ว ✓ รอทั้งหมด <b>{fmtSec(elapsed)}</b></>
                    : <>ลำดับคิว <b>#{(job.ahead ?? 0) + 1}</b> · คาดว่ารอ <b>{fmtSec(job.eta)}</b></>}
                </div>
                <div className="kv" style={{ marginTop: 10 }}>
                  <span>สถานะ</span><span>{job.phase === "done" ? "เสร็จแล้ว" : job.status === "running" ? "กำลังสร้าง" : "รอในคิว"}</span>
                  <span>ประเภท</span><span>{job.priority === "express" ? "⚡ งานด่วน" : "งานปกติ"}</span>
                  <span>งานข้างหน้า</span><span>{job.ahead ?? 0} งาน</span>
                  <span>เวลาที่ผ่านไป</span><span>{fmtSec(elapsed)}</span>
                  {job.worker && <><span>GPU ที่วาด</span><span>{job.worker}</span></>}
                  {job.seconds != null && <><span>เวลาวาดบน GPU</span><span>{fmtSec(job.seconds)}</span></>}
                  <span>รหัสงาน</span><span style={{ fontFamily: "monospace" }}>{job.id}</span>
                </div>
              </div>
            </div>
          )}
        </section>

        {/* ---- ตัวเลขสด + กราฟ ---- */}
        <section className="card">
          <h2>สถานะคิวแบบสด <small>อัปเดตทุก 1 วินาที</small></h2>
          <div className="stats">
            <div className="stat q"><div className="n">{stats ? waiting.toLocaleString() : "–"}</div><div className="l">รอในคิว</div>
              <div className="s">ด่วน {stats?.waiting?.express ?? 0} · ปกติ {stats?.waiting?.normal ?? 0}</div></div>
            <div className="stat r"><div className="n">{stats?.running?.toLocaleString() ?? "–"}</div><div className="l">กำลังสร้าง</div></div>
            <div className="stat d"><div className="n">{stats?.done?.toLocaleString() ?? "–"}</div><div className="l">เสร็จแล้ว</div></div>
            <div className="stat x"><div className="n">{stats?.rejected?.toLocaleString() ?? "–"}</div><div className="l">ถูกปฏิเสธ</div><div className="s">คิวเต็ม (429)</div></div>
          </div>
          <QueueChart points={hist} />
          <div className="legend">
            <span><i style={{ background: "#6cb8ff" }} />ความยาวคิว</span>
            <span><i style={{ background: "#ff6b6b" }} />เพดานคิวงานปกติ (100 × GPU ที่ทำงาน)</span>
          </div>
        </section>

        {/* ---- ส่งงานเป็นชุด ---- */}
        <section className="card">
          <h2>ส่งงานเป็นชุด <small>ทดลองให้คิวยาวแล้วดูว่าระบบรับไหวแค่ไหน</small></h2>
          <div className="batch">
            {BATCHES.map((b) => (
              <button key={b.label} className={`btn ${b.priority === "express" ? "exp" : "ghost"}`}
                disabled={!!batchBusy} onClick={() => runBatch(b)}>
                {batchBusy === b.label ? "กำลังส่ง…" : b.label}
              </button>
            ))}
          </div>
          <ul className="log">
            {batchLog.length === 0 && <li className="when">ยังไม่ได้ส่งงานเป็นชุด</li>}
            {batchLog.map((l, i) => (
              <li key={i}>
                <span className="when">{l.at}</span>
                <b>{l.label}</b>
                {l.error ? <span className="bad-t">ส่งไม่สำเร็จ: {l.error}</span> : <>
                  <span>รับ <span className="ok-t">{l.accepted}</span> งาน</span>
                  <span>ปฏิเสธ <span className="bad-t">{l.rejected}</span> งาน</span>
                  {l.errors > 0 && <span>ผิดพลาด {l.errors}</span>}
                  <span className="when">ใช้เวลาส่ง {l.seconds} วินาที{l.retry_after_seconds ? ` · ระบบแนะนำให้ลองใหม่ใน ${l.retry_after_seconds} วินาที` : ""}</span>
                </>}
              </li>
            ))}
          </ul>
        </section>

        {/* ---- การ์ด GPU Worker ---- */}
        <section className="card">
          <h2>GPU Worker <small>{workers.length ? `${liveN} ตัวทำงานอยู่` : ""}</small></h2>
          <div className="workers">
            {workers.length === 0 && <div className="empty">ยังไม่พบ Worker</div>}
            {workers.map((w) => <WorkerCard key={w.name} w={w} />)}
          </div>
        </section>

        {/* ---- ภาพล่าสุด ---- */}
        <section className="card full-row">
          <h2>ภาพที่เสร็จล่าสุด <small>12 ภาพ · เวลารอนับจากส่งงานจนได้ภาพ</small></h2>
          <div className="gallery">
            {(!stats || stats.recent.length === 0) && <div className="empty">ยังไม่มีภาพ</div>}
            {stats?.recent.map((j) => (
              <div className="tile" key={j.id}>
                <div className="imgbox">
                  <img src={`/api/jobs/${j.id}/image`} alt={j.prompt} loading="lazy" />
                  {j.priority === "express" && <span className="badge">⚡ ด่วน</span>}
                </div>
                <div className="cap">
                  <p title={j.prompt}>{j.prompt}</p>
                  <div className="m"><span>รอ {fmtSec(j.total_seconds)}</span><span>{j.worker}</span></div>
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>
      <p className="foot">PixelQueue · เว็บคุยกับระบบคิวผ่านเซิร์ฟเวอร์ของเว็บเท่านั้น</p>
    </main>
  );
}
