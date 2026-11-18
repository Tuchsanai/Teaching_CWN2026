"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

type Tag = { status: "none" | "ok" | "bad"; reason: string };
type Answer = {
  key: "base" | "ft";
  label: string;
  model: string;
  answer?: string;
  raw?: string;
  ms?: number;
  tokens?: number;
  tps?: number;
  tag?: Tag;
  error?: string;
};
type Run = { id: number; question: string; created_at: string; result: { answers: Answer[] } };

const EXAMPLES = [
  "นวดน้ำมันอโรมา 1 ชั่วโมงราคาเท่าไหร่คะ",
  "จองนวดคอบ่าไหล่พรุ่งนี้ 15:00 ชื่อสมศรี เบอร์ 0812345678",
  "Do you have hot stone massage?",
];

const TAG_TEXT: Record<Tag["status"], string> = {
  ok: "✅ แท็กจองถูกรูปแบบ",
  bad: "❌ แท็กจองผิดรูปแบบ",
  none: "➖ ไม่มีแท็กจอง",
};

function AnswerCard({ a }: { a: Answer }) {
  return (
    <div className={`card cmpcard ${a.key}`} data-testid={`compare-${a.key}`}>
      <div className="cmphead">
        <span className={`modeltag ${a.key}`}>{a.label}</span>
        <code>{a.model}</code>
      </div>
      {a.error ? (
        <p className="error">เรียกโมเดลไม่สำเร็จ: {a.error}</p>
      ) : (
        <>
          <div className="bubble assistant cmpanswer" data-testid="compare-answer">
            {a.answer || "(ตอบเป็นแท็กจองอย่างเดียว)"}
          </div>
          <dl className="cmpstats">
            <dt>เวลาที่ใช้</dt>
            <dd data-testid="compare-seconds">{((a.ms ?? 0) / 1000).toFixed(2)} วินาที</dd>
            <dt>ความเร็ว</dt>
            <dd data-testid="compare-tps">
              {a.tps} token/วินาที <span className="muted">({a.tokens} token)</span>
            </dd>
            <dt>แท็กจอง</dt>
            <dd data-testid="compare-tag" data-tag={a.tag?.status}>
              <span className={`tagcheck ${a.tag?.status}`}>{a.tag ? TAG_TEXT[a.tag.status] : "-"}</span>
              {a.tag?.status === "bad" && <span className="muted"> · {a.tag.reason}</span>}
            </dd>
          </dl>
          {a.tag && a.tag.status !== "none" && (
            <details className="rawtag">
              <summary>ดูคำตอบดิบ (มีแท็กจอง)</summary>
              <pre>{a.raw}</pre>
            </details>
          )}
        </>
      )}
    </div>
  );
}

export default function Compare() {
  const [q, setQ] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const [current, setCurrent] = useState<Run | null>(null);
  const [history, setHistory] = useState<Run[]>([]);

  async function loadHistory() {
    try {
      const r = await fetch("/api/compare", { cache: "no-store" });
      const j = await r.json();
      setHistory(j.runs || []);
      return (j.runs || []) as Run[];
    } catch {
      return [];
    }
  }

  useEffect(() => {
    loadHistory().then((runs) => runs[0] && setCurrent((c) => c ?? runs[0]));
  }, []);

  async function ask(text: string) {
    const question = text.trim();
    if (!question || busy) return;
    setBusy(true);
    setErr("");
    try {
      const r = await fetch("/api/compare", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const j = await r.json();
      if (!r.ok) throw new Error(j.error || `HTTP ${r.status}`);
      setCurrent(j);
      setQ("");
      loadHistory();
    } catch (e) {
      setErr((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="page wide">
      <header className="topbar">
        <div className="brand">
          <span className="logo">🌿</span>
          <div>
            <h1>เทียบคำตอบ 2 โมเดล</h1>
            <p>ถามคำถามเดียวกัน · Base (โมเดลเดิม) เทียบ Fine-tuned (โมเดลที่เทรนแล้ว)</p>
          </div>
        </div>
        <nav className="navs">
          <Link href="/" className="navlink ghost" data-testid="nav-chat">
            ← หน้าแชท
          </Link>
          <Link href="/bookings" className="navlink">
            รายการจอง
          </Link>
        </nav>
      </header>

      <section className="card cmpform">
        <form
          className="composer"
          onSubmit={(e) => {
            e.preventDefault();
            ask(q);
          }}
        >
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="พิมพ์คำถาม 1 ข้อ เช่น นวดไทยราคาเท่าไหร่"
            data-testid="compare-input"
            aria-label="คำถาม"
            maxLength={2000}
            autoComplete="off"
          />
          <button type="submit" data-testid="compare-button" disabled={busy || !q.trim()}>
            {busy ? "กำลังถาม…" : "เทียบคำตอบ"}
          </button>
        </form>
        <div className="chips">
          {EXAMPLES.map((ex) => (
            <button key={ex} type="button" className="chip" disabled={busy} onClick={() => ask(ex)}>
              {ex}
            </button>
          ))}
        </div>
        <p className="muted small">ถามทีละโมเดลด้วย system prompt เดียวกับหน้าแชท (ไม่มีประวัติแชท) · หน้านี้ไม่บันทึกการจองจริง</p>
      </section>

      {err && <p className="error">ถามไม่สำเร็จ: {err}</p>}
      {busy && <p className="muted center">กำลังถามโมเดล Base แล้วตามด้วย Fine-tuned…</p>}

      {current && (
        <section data-testid="compare-result">
          <div className="cmpq">
            <span className="muted">คำถาม #{current.id} · {current.created_at}</span>
            <div className="bubble user">{current.question}</div>
          </div>
          <div className="cmpgrid">
            {current.result.answers.map((a) => (
              <AnswerCard key={a.key} a={a} />
            ))}
          </div>
        </section>
      )}

      <section className="card tablecard">
        <h2 className="cardtitle">คำถามล่าสุด (เก็บใน PostgreSQL)</h2>
        {history.length === 0 ? (
          <p className="empty">ยังไม่มีคำถาม ลองพิมพ์ด้านบนดูนะคะ</p>
        ) : (
          <div className="tablewrap">
            <table data-testid="compare-history">
              <thead>
                <tr>
                  <th>#</th>
                  <th>คำถาม</th>
                  <th>Base</th>
                  <th>Fine-tuned</th>
                  <th>เวลา</th>
                </tr>
              </thead>
              <tbody>
                {history.map((r) => {
                  const [b, f] = ["base", "ft"].map((k) => r.result.answers.find((a) => a.key === k));
                  const cell = (a?: Answer) =>
                    !a || a.error ? "ผิดพลาด" : `${((a.ms ?? 0) / 1000).toFixed(1)} วิ · ${a.tps} tok/s`;
                  return (
                    <tr key={r.id} className="clickrow" onClick={() => setCurrent(r)}>
                      <td>{r.id}</td>
                      <td>{r.question}</td>
                      <td>{cell(b)}</td>
                      <td>{cell(f)}</td>
                      <td className="muted">{r.created_at}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </main>
  );
}
