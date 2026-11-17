"use client";

import { useEffect, useRef, useState } from "react";
import { MAX_SIDE } from "@/lib/prompt";

type Item = { name: string; qty: number | null; price: number | null };
type Receipt = { items: Item[]; subtotal: number | null; tax: number | null; total: number | null };
type ModelKey = "base" | "ft";
type Result = { seconds: number; raw: string; receipt: Receipt | null; error?: string; saved?: boolean };
type Sample = { id: string; file: string; target: Receipt };
type Mode = ModelKey | "both";

const LABEL: Record<ModelKey, string> = { base: "Base", ft: "Fine-tuned" };
const num = (v: number | null) => (v === null || v === undefined ? "–" : v.toLocaleString("en-US"));
const norm = (s: string) => s.toLowerCase().replace(/[^a-z0-9]/g, "");

// ย่อภาพในเบราว์เซอร์ให้ด้านยาวไม่เกิน maxSide แล้วคืน data URL (JPEG)
function resize(src: string, maxSide: number, quality = 0.9): Promise<string> {
  return new Promise((ok, fail) => {
    const img = new Image();
    img.onload = () => {
      const k = Math.min(1, maxSide / Math.max(img.width, img.height));
      const c = document.createElement("canvas");
      c.width = Math.round(img.width * k);
      c.height = Math.round(img.height * k);
      c.getContext("2d")!.drawImage(img, 0, 0, c.width, c.height);
      ok(c.toDataURL("image/jpeg", quality));
    };
    img.onerror = () => fail(new Error("เปิดไฟล์ภาพไม่ได้"));
    img.src = src;
  });
}

// เทียบรายการกับเฉลย: รายการถูกเมื่อ ชื่อ และ ราคา ตรงกับเฉลย (นับทีละบรรทัด)
function checkItems(items: Item[], target: Receipt) {
  const left = new Map<string, number>();
  for (const t of target.items) {
    const k = `${norm(t.name)}|${t.price}`;
    left.set(k, (left.get(k) ?? 0) + 1);
  }
  return items.map((it) => {
    const k = `${norm(it.name)}|${it.price}`;
    const n = left.get(k) ?? 0;
    if (n > 0) left.set(k, n - 1);
    return n > 0;
  });
}

export default function Page() {
  const [image, setImage] = useState("");
  const [source, setSource] = useState("");
  const [target, setTarget] = useState<Receipt | null>(null);
  const [mode, setMode] = useState<Mode>("both");
  const [results, setResults] = useState<Partial<Record<ModelKey, Result>>>({});
  const [busy, setBusy] = useState(false);
  const [samples, setSamples] = useState<Sample[]>([]);
  const [status, setStatus] = useState<{ ok: boolean; base?: boolean; ft?: boolean } | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    fetch("/samples/samples.json").then((r) => r.json()).then(setSamples).catch(() => {});
    fetch("/api/status").then((r) => r.json()).then(setStatus).catch(() => setStatus({ ok: false }));
  }, []);

  async function choose(src: string, name: string, t: Receipt | null) {
    setImage(await resize(src, MAX_SIDE));
    setSource(name);
    setTarget(t);
    setResults({});
  }

  function onFile(f?: File) {
    if (!f) return;
    const reader = new FileReader();
    reader.onload = () => choose(String(reader.result), f.name, null);
    reader.readAsDataURL(f);
  }

  async function read() {
    if (!image || busy) return;
    setBusy(true);
    setResults({});
    const keys: ModelKey[] = mode === "both" ? ["base", "ft"] : [mode];
    for (const key of keys) {
      try {
        const res = await fetch("/api/read", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ image, model: key }),
        });
        const j = await res.json();
        setResults((r) => ({ ...r, [key]: res.ok ? j : { seconds: 0, raw: "", receipt: null, error: j.error } }));
      } catch {
        setResults((r) => ({ ...r, [key]: { seconds: 0, raw: "", receipt: null, error: "เชื่อมต่อเว็บไม่ได้" } }));
      }
    }
    setBusy(false);
  }

  async function save(key: ModelKey) {
    const r = results[key];
    if (!r?.receipt) return;
    const thumb = await resize(image, 120, 0.7);
    const res = await fetch("/api/expenses", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...r.receipt, model: key, source, thumb }),
    });
    if (res.ok) setResults((x) => ({ ...x, [key]: { ...r, saved: true } }));
  }

  const shown: ModelKey[] = mode === "both" ? ["base", "ft"] : [mode];

  return (
    <div className="reader">
      <section className="panel left">
        <h2>1 · เลือกใบเสร็จ</h2>
        <div
          className="drop"
          onClick={() => fileRef.current?.click()}
          onDragOver={(e) => e.preventDefault()}
          onDrop={(e) => {
            e.preventDefault();
            onFile(e.dataTransfer.files[0]);
          }}
        >
          <b>อัปโหลดรูปใบเสร็จ</b>
          <span>คลิกเพื่อเลือกไฟล์ หรือลากรูปมาวาง (JPG / PNG)</span>
          <input ref={fileRef} id="file" type="file" accept="image/*" hidden onChange={(e) => onFile(e.target.files?.[0])} />
        </div>
        <p className="hint">หรือกดเลือกตัวอย่างจาก Test Set (มีเฉลยให้ตรวจ)</p>
        <div className="samples">
          {samples.map((s, i) => (
            <button
              key={s.id}
              className={source === s.id ? "sample on" : "sample"}
              title={s.id}
              data-testid={`sample-${i + 1}`}
              onClick={() => choose(`/samples/${s.file}`, s.id, s.target)}
            >
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={`/samples/${s.file}`} alt={`ตัวอย่างใบเสร็จ ${i + 1}`} />
            </button>
          ))}
        </div>

        <h2>2 · เลือกโมเดล</h2>
        <div className="switch" role="radiogroup" aria-label="โมเดล">
          {(["base", "ft", "both"] as Mode[]).map((m) => (
            <button key={m} role="radio" aria-checked={mode === m} data-testid={`mode-${m}`} className={mode === m ? "on" : ""} onClick={() => setMode(m)}>
              {m === "both" ? "เทียบสองโมเดล" : LABEL[m]}
            </button>
          ))}
        </div>
        <p className="hint">Base = โมเดลเดิม · Fine-tuned = โมเดลเดิม + LoRA ที่เทรนด้วยใบเสร็จ 800 ใบ</p>

        <button className="primary" data-testid="read" disabled={!image || busy} onClick={read}>
          {busy ? "กำลังอ่าน…" : "อ่านใบเสร็จ"}
        </button>
        <div className={status?.ok ? "status ok" : "status bad"} data-testid="status">
          {status === null
            ? "กำลังตรวจ AI server…"
            : status.ok
              ? `AI server พร้อม · Base ${status.base ? "✓" : "✗"} · Fine-tuned ${status.ft ? "✓" : "✗"}`
              : "ต่อ AI server ไม่ได้ — ตรวจไฟล์ receipt.env"}
        </div>
      </section>

      <section className="panel right">
        {!image ? (
          <div className="empty">เลือกรูปใบเสร็จทางซ้าย แล้วกด “อ่านใบเสร็จ”</div>
        ) : (
          <div className={`work cols-${shown.length}`}>
            <figure className="receipt">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={image} alt="ใบเสร็จที่เลือก" />
              <figcaption>{source}</figcaption>
            </figure>
            {shown.map((key) => (
              <ResultCard key={key} model={key} result={results[key]} busy={busy} target={target} onSave={() => save(key)} />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

function ResultCard({ model, result, busy, target, onSave }: { model: ModelKey; result?: Result; busy: boolean; target: Receipt | null; onSave: () => void }) {
  const r = result?.receipt;
  const marks = r && target ? checkItems(r.items, target) : null;
  const right = marks ? marks.filter(Boolean).length : 0;
  const cls = (ok: boolean | null) => (ok === null ? "" : ok ? "good" : "bad");
  const sums: [string, keyof Omit<Receipt, "items">][] = [["ยอดก่อนภาษี (subtotal)", "subtotal"], ["ภาษี (tax)", "tax"], ["ยอดรวม (total)", "total"]];

  return (
    <div className={`card ${model}`} data-testid={`card-${model}`}>
      <div className="card-head">
        <span className={`badge ${model}`}>{LABEL[model]}</span>
        {result && !result.error && <span className="time">{result.seconds.toFixed(1)} วินาที</span>}
      </div>
      {!result ? (
        <div className="wait">{busy ? "กำลังอ่าน…" : "ยังไม่ได้อ่าน"}</div>
      ) : result.error ? (
        <div className="err">{result.error}</div>
      ) : !r ? (
        <div className="err">
          โมเดลตอบไม่เป็น JSON ตาม schema
          <pre>{result.raw.slice(0, 600)}</pre>
        </div>
      ) : (
        <>
          <table>
            <thead>
              <tr>
                <th>รายการ</th>
                <th className="n">จำนวน</th>
                <th className="n">ราคา</th>
                {marks && <th></th>}
              </tr>
            </thead>
            <tbody>
              {r.items.map((it, i) => (
                <tr key={i} className={cls(marks ? marks[i] : null)}>
                  <td>{it.name}</td>
                  <td className="n">{num(it.qty)}</td>
                  <td className="n">{num(it.price)}</td>
                  {marks && <td className="mark">{marks[i] ? "✓" : "✗"}</td>}
                </tr>
              ))}
            </tbody>
            <tfoot>
              {sums.map(([label, k]) => (
                <tr key={k} className={`${k} ${cls(target ? r[k] === target[k] : null)}`}>
                  <td colSpan={2}>{label}</td>
                  <td className="n">{num(r[k])}</td>
                  {marks && <td className="mark">{r[k] === target![k] ? "✓" : "✗"}</td>}
                </tr>
              ))}
            </tfoot>
          </table>
          {marks && target && (
            <div className={right === target.items.length && right === r.items.length && r.total === target.total ? "verdict good" : "verdict bad"} data-testid={`verdict-${model}`}>
              เทียบเฉลย: รายการถูก {right} จาก {target.items.length} · ยอดรวม{r.total === target.total ? "ถูก" : "ผิด"}
            </div>
          )}
          <button className="save" data-testid={`save-${model}`} disabled={result.saved} onClick={onSave}>
            {result.saved ? "บันทึกแล้ว ✓" : "บันทึกเป็นรายจ่าย"}
          </button>
        </>
      )}
    </div>
  );
}
