"use client";
import { useState } from "react";
import { SAMPLES, type Sample } from "@/lib/samples";
import { MODEL_LABEL, rp, score, type ModelKey, type Receipt } from "@/lib/receipt";

type Mode = ModelKey | "both";
type Result = { model: ModelKey; parsed?: Receipt | null; raw?: string; seconds?: number; error?: string; loading?: boolean; saved?: number | "saving" };

export default function ReadPage() {
  const [sample, setSample] = useState<Sample | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [mode, setMode] = useState<Mode>("both");
  const [results, setResults] = useState<Result[]>([]);
  const busy = results.some((r) => r.loading);

  const pickSample = (s: Sample) => { setSample(s); setFile(null); setPreview(s.image); setResults([]); };
  const pickFile = (f: File | undefined) => {
    if (!f) return;
    setFile(f); setSample(null); setPreview(URL.createObjectURL(f)); setResults([]);
  };
  const source = () => {
    const fd = new FormData();
    if (sample) fd.append("sample", sample.id); else if (file) fd.append("file", file);
    return fd;
  };

  async function read() {
    const models: ModelKey[] = mode === "both" ? ["base", "ft"] : [mode];
    let cur: Result[] = models.map((m) => ({ model: m, loading: true }));
    setResults(cur);
    for (const m of models) { // one at a time, so each model's time is measured alone
      const fd = source(); fd.append("model", m);
      let r: Result;
      try {
        const res = await fetch("/api/read", { method: "POST", body: fd });
        const j = await res.json();
        r = res.ok ? { model: m, ...j } : { model: m, error: j.error ?? "อ่านไม่สำเร็จ" };
      } catch { r = { model: m, error: "เชื่อมต่อเว็บเซิร์ฟเวอร์ไม่ได้" }; }
      cur = cur.map((x) => (x.model === m ? r : x));
      setResults(cur);
    }
  }

  async function save(r: Result) {
    if (!r.parsed) return;
    setResults((rs) => rs.map((x) => (x.model === r.model ? { ...x, saved: "saving" } : x)));
    const fd = source();
    fd.append("model", r.model);
    fd.append("receipt", JSON.stringify(r.parsed));
    fd.append("seconds", String(r.seconds ?? ""));
    const res = await fetch("/api/expenses", { method: "POST", body: fd });
    const j = await res.json();
    setResults((rs) => rs.map((x) => (x.model === r.model ? { ...x, saved: res.ok ? j.id : undefined, error: res.ok ? x.error : j.error } : x)));
  }

  return (
    <>
      <h1>อ่านใบเสร็จ</h1>
      <p className="sub">ถ่ายรูปหรืออัปโหลดใบเสร็จ ให้ AI แยกรายการและยอดรวมออกมา แล้วบันทึกเป็นรายจ่าย</p>

      <section className="card">
        <h2><span className="step">1</span>เลือกใบเสร็จ</h2>
        <div className="samples">
          {SAMPLES.map((s) => (
            <button key={s.id} className={"sample" + (sample?.id === s.id ? " on" : "")} onClick={() => pickSample(s)}>
              <img src={s.image} alt={s.id} />
              <span>{s.id}</span>
            </button>
          ))}
        </div>
        <div className="upload">
          <label className="btn ghost">
            📷 อัปโหลดรูปใบเสร็จ
            <input type="file" accept="image/*" hidden onChange={(e) => pickFile(e.target.files?.[0])} />
          </label>
          <span className="time">
            {file ? `ไฟล์: ${file.name}` : sample ? `ใบเสร็จตัวอย่าง ${sample.id} (มีเฉลย)` : "ยังไม่ได้เลือก · ตัวอย่าง 6 ใบมาจาก Test Set ของ CORD-v2 พร้อมเฉลย"}
          </span>
        </div>
      </section>

      <section className="card">
        <h2><span className="step">2</span>เลือกโมเดล</h2>
        <div className="row">
          <div className="seg">
            {(["base", "ft", "both"] as Mode[]).map((m) => (
              <button key={m} className={mode === m ? "on" : ""} onClick={() => setMode(m)}>
                {m === "both" ? "เทียบสองโมเดล" : MODEL_LABEL[m]}
              </button>
            ))}
          </div>
          <button className="btn" disabled={!preview || busy} onClick={read}>
            {busy ? <><span className="spinner" />กำลังอ่าน…</> : "อ่านใบเสร็จ"}
          </button>
        </div>
      </section>

      {preview && results.length > 0 && (
        <section className="result">
          <div className="card pic"><img src={preview} alt="ใบเสร็จ" /></div>
          <div className={"models" + (results.length === 2 ? " two" : "")}>
            {results.map((r) => <ModelCard key={r.model} r={r} gt={sample?.answer ?? null} onSave={() => save(r)} />)}
          </div>
        </section>
      )}
    </>
  );
}

function ModelCard({ r, gt, onSave }: { r: Result; gt: Receipt | null; onSave: () => void }) {
  const head = (
    <div className="mhead">
      <span className={"badge " + r.model}>{MODEL_LABEL[r.model]}</span>
      {r.seconds !== undefined && <span className="time">⏱ {r.seconds.toFixed(1)} วินาที</span>}
    </div>
  );
  if (r.loading) return <div className="card">{head}<span className="spinner" />กำลังส่งรูปให้ AI server…</div>;
  if (r.error && !r.parsed) return <div className="card">{head}<div className="err">{r.error}</div></div>;
  const p = r.parsed;
  if (!p) return <div className="card">{head}<div className="err">โมเดลตอบกลับมาไม่ใช่ JSON ที่อ่านได้</div><Raw raw={r.raw} /></div>;
  const s = gt ? score(gt, p) : null;
  const mark = (ok: boolean) => <span className={"mark " + (ok ? "ok" : "bad")}>{ok ? "✓" : "✗"}</span>;

  return (
    <div className="card">
      {head}
      <table>
        <thead><tr>{s && <th></th>}<th>รายการ</th><th className="num">จำนวน</th><th className="num">ราคา</th></tr></thead>
        <tbody>
          {p.items.map((it, i) => (
            <tr key={i} className={s ? (s.itemOk[i] ? "ok" : "bad") : ""}>
              {s && <td>{mark(s.itemOk[i])}</td>}
              <td>{it.name ?? "–"}</td><td className="num">{it.qty ?? "–"}</td><td className="num">{rp(it.price)}</td>
            </tr>
          ))}
          {p.items.length === 0 && <tr><td colSpan={4} className="time">ไม่พบรายการ</td></tr>}
        </tbody>
      </table>
      <table className="sum" style={{ marginTop: 10 }}>
        <tbody>
          <tr><td>ยอดก่อนภาษี</td><td className="num">{rp(p.subtotal)}</td></tr>
          <tr><td>ภาษี</td><td className="num">{rp(p.tax)}</td></tr>
          <tr className="grand"><td>ยอดรวม {s && s.totalOk !== null && mark(s.totalOk)}</td><td className="num">{rp(p.total)}</td></tr>
        </tbody>
      </table>
      {s && (
        <>
          <span className={"pill " + (s.tp === s.nGt && s.tp === p.items.length ? "ok" : "bad")}>รายการตรงเฉลย {s.tp}/{s.nGt}</span>
          {s.totalOk !== null && <span className={"pill " + (s.totalOk ? "ok" : "bad")}>ยอดรวม{s.totalOk ? "ถูก" : `ผิด (เฉลย ${rp(gt!.total)})`}</span>}
          {s.missed.length > 0 && (
            <div className="missed">เฉลยที่อ่านไม่ตรง: {s.missed.map((m) => `${m.name} ${rp(m.price)}`).join(" · ")}</div>
          )}
        </>
      )}
      <div className="row" style={{ marginTop: 14 }}>
        {typeof r.saved === "number"
          ? <span className="saved">✓ บันทึกแล้ว · <a href="/expenses" style={{ textDecoration: "underline" }}>ดูรายจ่าย</a></span>
          : <button className="btn" disabled={r.saved === "saving"} onClick={onSave}>{r.saved === "saving" ? "กำลังบันทึก…" : "บันทึกเป็นรายจ่าย"}</button>}
        {r.error && <span className="err">{r.error}</span>}
      </div>
      <Raw raw={r.raw} />
    </div>
  );
}

const Raw = ({ raw }: { raw?: string }) =>
  raw ? <details><summary>คำตอบดิบจากโมเดล</summary><pre>{raw}</pre></details> : null;
