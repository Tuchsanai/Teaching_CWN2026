'use client';
// /admin/eval (v3) — แดชบอร์ดผลประเมิน RAG: GET /api/admin/eval → {runs, latest} (?id=N เลือก run)
// testid: eval-run-select · eval-metric(data-metric,data-set) · eval-compare · eval-item(data-id,data-pass) · eval-empty
import { Fragment, useCallback, useEffect, useMemo, useState } from 'react';
import { Bar, Gauge, Legend, SERIES, pct } from '../charts';

type Summary = Record<string, Record<string, number>>;
type Run = { id: number; label: string; createdAt?: string; created_at?: string; config: Record<string, any>; summary: Summary };
type Src = { filename: string; page: number; score?: number };
type Item = {
  id: string;
  set: 'rag' | 'qa' | 'conv' | string; // 'sql' = ชื่อเดิม (แปลงเป็น qa ตอนโหลด)
  question?: string;
  turns?: { q?: string; a?: string; text?: string; audio?: string }[];
  expected?: any;
  answer?: string;
  retrieved?: Src[];
  cites?: Src[];
  metrics?: Record<string, number>;
  pass?: boolean;
  reason?: string;
  doc?: string;
  qtype?: string;
  type?: string;
  sources?: Src[];
};
type Full = Run & { items: Item[] };

const SETS: { key: string; title: string; sub: string; icon: string; metrics: string[] }[] = [
  { key: 'rag', title: 'A · RAG จากเอกสาร', sub: 'ค้นหน้า PDF ถูก + ตอบตรงเอกสาร', icon: '📄', metrics: ['hit_at_4', 'mrr', 'citation_acc', 'faithfulness', 'correctness'] },
  { key: 'qa', title: 'B · คำถามปกติ (ข้อมูลร้าน/SQL)', sub: 'ราคา · ราคาส่ง · สต็อก · คูปอง · ค่าส่ง', icon: '🗄️', metrics: ['exact_value', 'sql_correct', 'correctness'] },
  { key: 'conv', title: 'C · บทสนทนาหลายรอบ', sub: 'จำบริบท "อันนั้น" · บางบทเป็นเสียง', icon: '💬', metrics: ['context_retention', 'correctness', 'stt_cer'] },
];
const LABEL: Record<string, string> = {
  hit_at_4: 'Hit@4',
  mrr: 'MRR',
  citation_acc: 'อ้างอิงถูก',
  faithfulness: 'ยึดตามเอกสาร',
  correctness: 'ตอบถูก',
  exact_value: 'ตัวเลขตรง',
  sql_correct: 'SQL ถูกตาราง',
  context_retention: 'จำบริบท',
  stt_cer: 'CER ถอดเสียง',
  pass_rate: 'ผ่าน',
};
const HINT: Record<string, string> = {
  hit_at_4: 'หน้าที่ถูกอยู่ใน 4 ย่อหน้าที่ค้นได้',
  mrr: 'ค่าเฉลี่ย 1/อันดับของหน้าที่ถูก',
  citation_acc: 'ป้าย 📄 ไฟล์/หน้า ตรงคำตอบที่คาด',
  faithfulness: 'ทุกข้อความอ้างจากย่อหน้าที่ค้นได้ (LLM judge)',
  correctness: 'ข้อเท็จจริงหลัก/ตัวเลขตรง',
  exact_value: 'ตัวเลขตรงฐานข้อมูลเป๊ะ',
  sql_correct: 'เรียกข้อมูลถูกตาราง/ถูกเงื่อนไข',
  context_retention: 'รอบหลังเข้าใจคำอ้างถึงรอบก่อน',
  stt_cer: 'อัตราตัวอักษรผิดของ Whisper (ยิ่งน้อยยิ่งดี)',
};
const LOWER_BETTER = new Set(['stt_cer']);
const QTYPE: Record<string, string> = {
  text: 'ข้อความ',
  'table-2level': 'ตารางหัว 2 ชั้น',
  'merged-cell': 'เซลล์รวม',
  footnote: 'เชิงอรรถ',
  'cross-page': 'ข้ามหน้า',
  price: 'ราคา',
  wholesale: 'ราคาส่ง',
  'branch-stock': 'สต็อกสาขา',
  coupon: 'คูปอง',
  shipping: 'ค่าส่ง',
  'multi-turn': 'หลายรอบ',
  voice: 'เสียง',
};

const when = (r: Run) => {
  const d = r.createdAt || r.created_at;
  return d ? new Date(d).toLocaleString('th-TH', { dateStyle: 'medium', timeStyle: 'short' }) : '';
};
const rerankOf = (r?: Run) => {
  const v = r?.config?.rerank;
  if (v == null) return '';
  return v === false || v === 'off' ? 'rerank off' : 'rerank on';
};
const docOf = (it: Item) =>
  it.doc || it.sources?.[0]?.filename || it.expected?.sources?.[0]?.filename || it.expected?.source?.filename || '(ไม่ระบุ)';
const typeOf = (it: Item) => it.qtype || it.type || (it.set === 'conv' ? 'multi-turn' : '(อื่น ๆ)');
const expectedSrc = (it: Item): Src[] => it.expected?.sources || it.sources || [];
const isHit = (s: Src, exp: Src[]) => exp.some((e) => e.filename === s.filename && Number(e.page) === Number(s.page));
const metricVal = (s: Summary | undefined, set: string, m: string) => {
  const v = s?.[set]?.[m];
  return typeof v === 'number' ? v : null;
};

function expectedText(e: any): string {
  if (e == null) return '–';
  if (typeof e === 'string') return e;
  const parts: string[] = [];
  if (e.answer) parts.push(String(e.answer));
  if (Array.isArray(e.values)) parts.push(`ค่า: ${e.values.join(' · ')}`);
  if (Array.isArray(e.key_facts) && e.key_facts.length && !e.answer) parts.push(e.key_facts.join(' · '));
  return parts.join('\n') || JSON.stringify(e);
}

const PAGE = 50;

/** ชุด 'sql' (ชื่อเดิม) → 'qa' ตาม CONTRACT_V3 §7 */
function normSummary<T extends { summary?: Summary }>(r: T): T {
  const s = r?.summary;
  if (s && s.sql && !s.qa) return { ...r, summary: { ...s, qa: s.sql } };
  return r;
}
function normRun(r: Full | null): Full | null {
  if (!r) return r;
  const n = normSummary(r);
  return { ...n, items: (n.items || []).map((it) => (it.set === 'sql' ? { ...it, set: 'qa' } : it)) };
}

export default function EvalDashboard() {
  const [data, setData] = useState<{ runs: Run[]; latest: Full | null } | null>(null);
  const [sel, setSel] = useState<number | null>(null);
  const [err, setErr] = useState('');
  const [loading, setLoading] = useState(true);
  const [setFilter, setSetFilter] = useState<string>('all');
  const [failOnly, setFailOnly] = useState(false);
  const [q, setQ] = useState('');
  const [open, setOpen] = useState<string | null>(null);
  const [page, setPage] = useState(0);

  const load = useCallback(async (id?: number | null) => {
    setLoading(true);
    setErr('');
    try {
      const r = await fetch(`/api/admin/eval${id ? `?id=${id}` : ''}`, { cache: 'no-store' });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const j = await r.json();
      setData({ runs: (j.runs || []).map((r: Run) => normSummary(r)), latest: normRun(j.latest || null) });
      setSel(j.latest?.id ?? null);
    } catch (e: any) {
      setErr(`โหลดผลประเมินไม่ได้ (${e?.message || e})`);
      setData((d) => d || { runs: [], latest: null });
    } finally {
      setLoading(false);
    }
  }, []);
  useEffect(() => {
    load();
  }, [load]);

  const run = data?.latest || null;
  const runs = data?.runs || [];
  const items = useMemo(() => run?.items || [], [run]);

  // run ที่เอามาเทียบ: run ที่เลือก + อีกสูงสุด 3 run ล่าสุด
  const compareRuns = useMemo(() => {
    if (!run) return [] as Run[];
    const others = runs.filter((r) => r.id !== run.id).slice(0, 3);
    return [run as Run, ...others];
  }, [run, runs]);
  // run อ้างอิงสำหรับ ▲▼: เลือก run ที่ตั้งค่า rerank ต่างจากรอบนี้ก่อน (มี/ไม่มี reranker) ไม่งั้นรอบก่อนหน้า
  const baseline = compareRuns.slice(1).find((r) => rerankOf(r) && rerankOf(r) !== rerankOf(run as Run)) || compareRuns[1];

  const groups = useMemo(() => {
    const by = (keyf: (it: Item) => string, set?: string) => {
      const m = new Map<string, Item[]>();
      for (const it of items) {
        if (set && it.set !== set) continue;
        const k = keyf(it);
        m.set(k, [...(m.get(k) || []), it]);
      }
      return Array.from(m.entries())
        .map(([k, its]) => {
          const avg = (mk: string) => {
            const vs = its.map((x) => x.metrics?.[mk]).filter((v): v is number => typeof v === 'number');
            return vs.length ? vs.reduce((a, b) => a + b, 0) / vs.length : null;
          };
          return { key: k, n: its.length, pass: its.filter((x) => x.pass).length / its.length, hit: avg('hit_at_4'), mrr: avg('mrr'), corr: avg('correctness') };
        })
        .sort((a, b) => a.key.localeCompare(b.key));
    };
    return { doc: by(docOf, 'rag'), type: by(typeOf) };
  }, [items]);

  const shown = useMemo(() => {
    const s = q.trim().toLowerCase();
    return items.filter(
      (it) =>
        (setFilter === 'all' || it.set === setFilter) &&
        (!failOnly || !it.pass) &&
        (!s || `${it.id} ${it.question || ''} ${it.answer || ''} ${it.reason || ''} ${docOf(it)}`.toLowerCase().includes(s)),
    );
  }, [items, setFilter, failOnly, q]);
  useEffect(() => setPage(0), [setFilter, failOnly, q, run?.id]);
  const pages = Math.max(1, Math.ceil(shown.length / PAGE));
  const pg = Math.min(page, pages - 1);
  const pageItems = shown.slice(pg * PAGE, pg * PAGE + PAGE);

  const failCount = items.filter((i) => !i.pass).length;

  if (loading && !data) return <div className="ev-page"><div className="card ev-skeleton">กำลังโหลดผลประเมิน…</div></div>;

  if (!run) {
    return (
      <div className="ev-page">
        {err && <div className="adm-error">{err}</div>}
        <div className="card ev-empty" data-testid="eval-empty">
          <div className="ev-empty-ico" aria-hidden>
            🧪
          </div>
          <h2>ยังไม่มีผลประเมิน RAG</h2>
          <p className="muted">รันชุดคำถาม 60–70 ข้อ (เอกสาร · ข้อมูลร้าน · บทสนทนา) แล้วส่งผลเข้าระบบ ผลจะแสดงที่หน้านี้</p>
          <pre className="ev-code">
            {`cd eval
node run_eval.mjs        # ถามผ่าน /api/chat → answers.json
node score.mjs           # รวมคะแนน → results.json → POST /api/admin/eval`}
          </pre>
          <select className="select" data-testid="eval-run-select" disabled>
            <option>ยังไม่มี run</option>
          </select>
        </div>
      </div>
    );
  }

  return (
    <div className="ev-page">
      {err && <div className="adm-error">{err}</div>}

      <section className="card ev-head">
        <div className="ev-head-main">
          <h1>ผลประเมินคุณภาพผู้ช่วย AI</h1>
          <p className="muted">
            {items.length} ข้อ · ผ่าน <b className="ev-ok">{items.length - failCount}</b> · ตก <b className="ev-bad">{failCount}</b> · {when(run)}
          </p>
          <div className="ev-chips">
            {Object.entries(run.config || {})
              .filter(([, v]) => typeof v !== 'object')
              .map(([k, v]) => (
                <span key={k} className={`ev-chip${k === 'rerank' ? (v === 'off' || v === false ? ' off' : ' on') : ''}`}>
                  <small>{k}</small> {String(v)}
                </span>
              ))}
          </div>
        </div>
        <label className="ev-run">
          <span>เลือกรอบประเมิน</span>
          <select
            className="select"
            data-testid="eval-run-select"
            value={sel ?? ''}
            onChange={(e) => {
              const id = Number(e.target.value);
              setSel(id);
              setOpen(null);
              load(id);
            }}
          >
            {runs.map((r) => (
              <option key={r.id} value={r.id}>
                #{r.id} · {r.label} · {when(r)}
              </option>
            ))}
          </select>
          {loading && <span className="adm-spin" aria-hidden />}
        </label>
      </section>

      {SETS.map((st) => {
        const n = run.summary?.[st.key]?.n ?? items.filter((i) => i.set === st.key).length;
        const metrics = st.metrics.filter((m) => metricVal(run.summary, st.key, m) != null || m !== 'stt_cer');
        return (
          <section key={st.key} className="ev-set">
            <div className="ev-set-head">
              <h2>
                <span aria-hidden>{st.icon}</span> {st.title}
              </h2>
              <span className="muted small">
                {st.sub} · {n} ข้อ
                {run.summary?.[st.key]?.pass_rate != null && <> · ผ่าน {pct(run.summary[st.key].pass_rate)}</>}
              </span>
            </div>
            <div className="ev-metrics">
              {metrics.map((m) => {
                const v = metricVal(run.summary, st.key, m);
                const b = metricVal(baseline?.summary, st.key, m);
                const d = v != null && b != null ? v - b : null;
                const better = d != null && (LOWER_BETTER.has(m) ? d < 0 : d > 0);
                return (
                  <div key={m} className="ev-metric" data-testid="eval-metric" data-metric={m} data-set={st.key} data-value={v ?? ''} title={HINT[m]}>
                    <Gauge value={v} lowerBetter={LOWER_BETTER.has(m)} dep={run.id} />
                    <div className="ev-metric-txt">
                      <b>{LABEL[m] || m}</b>
                      <small>{HINT[m]}</small>
                      {d != null && Math.abs(d) >= 0.0005 && (
                        <span className={`ev-delta ${better ? 'up' : 'down'}`} title={`เทียบกับ #${baseline?.id} ${baseline?.label}`}>
                          {d > 0 ? '▲' : '▼'} {Math.abs(d * 100).toFixed(1)} จุด
                        </span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </section>
        );
      })}

      <div className="ev-grid-2">
        <section className="card" data-testid="eval-compare">
          <div className="adm-card-head">
            <h2>เทียบระหว่างรอบ</h2>
            <span className="muted small">{compareRuns.length > 1 ? 'เช่น มี/ไม่มี reranker' : 'มีรอบเดียว — รันอีกรอบ (เช่น RERANK=off) เพื่อเทียบ'}</span>
          </div>
          <Legend items={compareRuns.map((r, i) => ({ name: `#${r.id} ${r.label}${rerankOf(r) && !r.label.includes('rerank') ? ` (${rerankOf(r)})` : ''}`, color: SERIES[i] }))} />
          <div className="ev-compare">
            {SETS.flatMap((st) =>
              st.metrics
                .filter((m) => compareRuns.some((r) => metricVal(r.summary, st.key, m) != null))
                .map((m) => (
                  <div key={`${st.key}.${m}`} className="ev-cmp-row">
                    <div className="ev-cmp-lbl">
                      <b>{LABEL[m]}</b>
                      <small>{st.key.toUpperCase()}</small>
                    </div>
                    <div className="ev-cmp-bars">
                      {compareRuns.map((r, i) => {
                        const v = metricVal(r.summary, st.key, m);
                        return (
                          <div key={r.id} className="ev-cmp-bar">
                            <Bar value={v == null ? 0 : LOWER_BETTER.has(m) ? Math.min(1, v * 5) : v} color={SERIES[i]} dep={`${run.id}-${r.id}`} height={9} />
                            <span>{v == null ? '–' : LOWER_BETTER.has(m) ? `${(v * 100).toFixed(1)}%` : pct(v)}</span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )),
            )}
          </div>
        </section>

        <section className="card">
          <div className="adm-card-head">
            <h2>แยกตามเอกสาร (ชุด A)</h2>
            <span className="muted small">ผ่าน · Hit@4 · MRR</span>
          </div>
          <div className="ev-break">
            {groups.doc.map((g) => (
              <div key={g.key} className="ev-break-row" data-testid="eval-by-doc">
                <div className="ev-break-lbl">
                  <span className="mono">{g.key.replace(/\.pdf$/, '')}</span>
                  <small>{g.n} ข้อ</small>
                </div>
                <Bar value={g.pass} color={g.pass >= 0.85 ? '#3ddc97' : g.pass >= 0.65 ? '#fbbf24' : '#ff6b6b'} dep={run.id} height={10} />
                <span className="ev-break-num">{pct(g.pass)}</span>
                <span className="ev-break-sub">
                  {pct(g.hit)} · {g.mrr == null ? '–' : g.mrr.toFixed(2)}
                </span>
              </div>
            ))}
          </div>
          <div className="adm-card-head" style={{ marginTop: 18 }}>
            <h2>แยกตามประเภทคำถาม</h2>
            <span className="muted small">อัตราผ่าน</span>
          </div>
          <div className="ev-break">
            {groups.type.map((g) => (
              <div key={g.key} className="ev-break-row" data-testid="eval-by-type">
                <div className="ev-break-lbl">
                  <span>{QTYPE[g.key] || g.key}</span>
                  <small>{g.n} ข้อ</small>
                </div>
                <Bar value={g.pass} color={SERIES[1]} dep={run.id} height={10} />
                <span className="ev-break-num">{pct(g.pass)}</span>
                <span className="ev-break-sub">ตอบถูก {pct(g.corr)}</span>
              </div>
            ))}
          </div>
        </section>
      </div>

      <section className="card">
        <div className="adm-card-head">
          <h2>รายข้อ</h2>
          <div className="adm-tools">
            <div className="ev-seg" role="tablist">
              {['all', 'rag', 'qa', 'conv'].map((s) => (
                <button key={s} type="button" className={setFilter === s ? 'on' : ''} onClick={() => setSetFilter(s)} data-testid={`eval-set-${s}`}>
                  {s === 'all' ? 'ทั้งหมด' : s.toUpperCase()}
                </button>
              ))}
            </div>
            <label className="adm-check">
              <input type="checkbox" checked={failOnly} onChange={(e) => setFailOnly(e.target.checked)} data-testid="eval-filter-fail" /> เฉพาะข้อที่ตก ({failCount})
            </label>
            <input className="input" placeholder="ค้นคำถาม / เหตุผล / เอกสาร" value={q} onChange={(e) => setQ(e.target.value)} />
          </div>
        </div>
        <div className="adm-table-wrap">
          <table className="adm-table ev-table">
            <thead>
              <tr>
                <th>ข้อ</th>
                <th>คำถาม</th>
                <th>ประเภท</th>
                <th>ค้นเจอ (top 4)</th>
                <th className="num">คะแนน</th>
                <th>ผล</th>
              </tr>
            </thead>
            <tbody>
              {shown.length === 0 && (
                <tr>
                  <td colSpan={6} className="adm-empty muted">
                    ไม่มีข้อที่ตรงกับตัวกรอง
                  </td>
                </tr>
              )}
              {pageItems.map((it) => {
                const exp = expectedSrc(it);
                const ms = Object.entries(it.metrics || {});
                const avg = ms.length ? ms.filter(([k]) => !LOWER_BETTER.has(k)).reduce((a, [, v]) => a + v, 0) / Math.max(1, ms.filter(([k]) => !LOWER_BETTER.has(k)).length) : null;
                const isOpen = open === it.id;
                return (
                  <Fragment key={it.id}>
                    <tr
                      className={`ev-row${it.pass ? '' : ' fail'}${isOpen ? ' open' : ''}`}
                      data-testid="eval-item"
                      data-id={it.id}
                      data-pass={it.pass ? 'true' : 'false'}
                      onClick={() => setOpen(isOpen ? null : it.id)}
                    >
                      <td className="mono">{it.id}</td>
                      <td className="ev-q">
                        {it.question || it.turns?.map((t) => t.q || t.text).join(' → ')}
                        {it.set === 'conv' && it.turns?.some((t) => t.audio) && <span className="ev-voice">🎙</span>}
                      </td>
                      <td>
                        <span className={`ev-set-chip ${it.set}`}>{it.set.toUpperCase()}</span> <span className="small muted">{QTYPE[typeOf(it)] || typeOf(it)}</span>
                      </td>
                      <td>
                        <div className="ev-srcs">
                          {(it.retrieved || []).slice(0, 4).map((s, i) => (
                            <span key={i} className={`ev-src${isHit(s, exp) ? ' hit' : ''}`} title={`${s.filename} หน้า ${s.page}${s.score != null ? ` · ${s.score}` : ''}`}>
                              {i + 1}. {s.filename.replace(/^BM-(DS-)?|\.pdf$/g, '')} p{s.page}
                            </span>
                          ))}
                          {!it.retrieved?.length && <span className="muted small">–</span>}
                        </div>
                      </td>
                      <td className="num">{avg == null ? '–' : pct(avg)}</td>
                      <td>
                        <span className={`ev-pass ${it.pass ? 'ok' : 'no'}`}>{it.pass ? '✓ ผ่าน' : '✗ ตก'}</span>
                      </td>
                    </tr>
                    {isOpen && (
                      <tr className="ev-detail">
                        <td colSpan={6}>
                          <div className="ev-detail-grid">
                            <div>
                              <h4>คำตอบที่คาด</h4>
                              <p className="ev-pre">{expectedText(it.expected)}</p>
                              {exp.length > 0 && (
                                <p className="small muted">
                                  แหล่ง: {exp.map((e) => `${e.filename} หน้า ${e.page}`).join(' · ')}
                                </p>
                              )}
                            </div>
                            <div>
                              <h4>คำตอบของน้องช่าง</h4>
                              {it.turns?.length ? (
                                <ol className="ev-turns">
                                  {it.turns.map((t, i) => (
                                    <li key={i}>
                                      <b>{t.audio ? '🎙 ' : ''}{t.q || t.text}</b>
                                      {t.a && <div className="muted">{t.a}</div>}
                                    </li>
                                  ))}
                                </ol>
                              ) : (
                                <p className="ev-pre">{it.answer || '–'}</p>
                              )}
                              {!!it.cites?.length && (
                                <p className="small">
                                  อ้างอิง: {it.cites.map((c) => `📄 ${c.filename} · หน้า ${c.page}`).join('  ')}
                                </p>
                              )}
                            </div>
                            <div>
                              <h4>คะแนนรายตัว</h4>
                              <div className="ev-mini">
                                {Object.entries(it.metrics || {}).map(([k, v]) => (
                                  <span key={k} className={LOWER_BETTER.has(k) ? '' : v >= 0.999 ? 'ok' : v > 0 ? 'mid' : 'no'}>
                                    {LABEL[k] || k} <b>{LOWER_BETTER.has(k) ? `${(v * 100).toFixed(1)}%` : k === 'mrr' ? v.toFixed(2) : pct(v)}</b>
                                  </span>
                                ))}
                              </div>
                              {it.reason && (
                                <div className="ev-reason">
                                  <b>เหตุผล</b> {it.reason}
                                </div>
                              )}
                            </div>
                          </div>
                        </td>
                      </tr>
                    )}
                  </Fragment>
                );
              })}
            </tbody>
          </table>
        </div>
        <div className="ev-pager" data-testid="eval-pager">
          <span className="muted small">
            แสดง {shown.length ? pg * PAGE + 1 : 0}–{Math.min(shown.length, pg * PAGE + PAGE)} จาก {shown.length} ข้อ
          </span>
          {pages > 1 && (
            <div className="ev-pager-btns">
              <button type="button" className="btn secondary" disabled={pg === 0} onClick={() => setPage(pg - 1)} data-testid="eval-page-prev">
                ‹ ก่อนหน้า
              </button>
              {Array.from({ length: pages }, (_, i) => i).map((i) => (
                <button key={i} type="button" className={`ev-pg${i === pg ? ' on' : ''}`} onClick={() => setPage(i)}>
                  {i + 1}
                </button>
              ))}
              <button type="button" className="btn secondary" disabled={pg >= pages - 1} onClick={() => setPage(pg + 1)} data-testid="eval-page-next">
                ถัดไป ›
              </button>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
