'use client';
// /admin/load (v3) — ผล load test: GET /api/admin/load → {runs, latest} (?id=N)
// latest.items (หรือ stages) = [{users,n,errors,p50,p95,ttft_p50,ttft_p95,rtf,tokens_per_s,queue_max,ok?}]
// latest.summary = {mode, max_users_ok, thresholds:{p95_s, error_rate}}
// testid: load-run-select · load-chart · load-max-users(data-mode) · load-queue-chart · load-empty
import { useCallback, useEffect, useMemo, useState } from 'react';
import { Legend, LineChart, SERIES } from '../charts';

type Stage = {
  users: number;
  n?: number;
  errors?: number;
  p50?: number | null;
  p95?: number | null;
  ttft_p50?: number | null;
  ttft_p95?: number | null;
  rtf?: number | null;
  tokens_per_s?: number | null;
  queue_max?: number | null;
  ok?: boolean;
};
type Run = { id: number; label: string; createdAt?: string; created_at?: string; config: any; summary: any; mode?: string; max_users_ok?: number; thresholds?: any };
type Full = Run & { items?: Stage[]; stages?: Stage[] };

const MODES: { key: string; label: string; icon: string; desc: string }[] = [
  { key: 'chat', label: 'แชท', icon: '💬', desc: '/api/chat SSE' },
  { key: 'stt', label: 'ฟังเสียง', icon: '👂', desc: '/api/voice (Whisper)' },
  { key: 'tts', label: 'พูด', icon: '🗣️', desc: '/api/tts (VoxCPM2)' },
  { key: 'voice', label: 'เสียง→เสียง', icon: '🎙', desc: 'ฟัง + คิด + พูด' },
];
const modeOf = (r?: Run | null) => r?.summary?.mode || r?.config?.mode || r?.mode || '';
const maxOf = (r?: Run | null): number | null => {
  const v = r?.summary?.max_users_ok ?? r?.max_users_ok;
  return typeof v === 'number' ? v : null;
};
const thrOf = (r?: Run | null) => r?.summary?.thresholds || r?.thresholds || r?.config?.thresholds || null;
const when = (r: Run) => {
  const d = r.createdAt || r.created_at;
  return d ? new Date(d).toLocaleString('th-TH', { dateStyle: 'medium', timeStyle: 'short' }) : '';
};
const num = (v: number | null | undefined, d = 2) => (v == null || Number.isNaN(v) ? '–' : Number(v).toFixed(d));

export default function LoadDashboard() {
  const [data, setData] = useState<{ runs: Run[]; latest: Full | null } | null>(null);
  const [sel, setSel] = useState<number | null>(null);
  const [err, setErr] = useState('');
  const [loading, setLoading] = useState(true);

  const load = useCallback(async (id?: number | null) => {
    setLoading(true);
    setErr('');
    try {
      const r = await fetch(`/api/admin/load${id ? `?id=${id}` : ''}`, { cache: 'no-store' });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const j = await r.json();
      setData({ runs: j.runs || [], latest: j.latest || null });
      setSel(j.latest?.id ?? null);
    } catch (e: any) {
      setErr(`โหลดผล load test ไม่ได้ (${e?.message || e})`);
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
  const stages = useMemo(() => [...((run?.items?.length ? run.items : run?.stages) || [])].sort((a, b) => a.users - b.users), [run]);
  const thr = thrOf(run);
  const mode = modeOf(run);
  const latestByMode = useMemo(() => {
    const m: Record<string, Run> = {};
    for (const r of runs) {
      const k = modeOf(r);
      if (k && !m[k]) m[k] = r; // runs เรียงใหม่ → เก่า
    }
    if (run && mode && run.id && !m[mode]) m[mode] = run;
    return m;
  }, [runs, run, mode]);

  if (loading && !data) return <div className="ev-page"><div className="card ev-skeleton">กำลังโหลดผล load test…</div></div>;

  if (!run) {
    return (
      <div className="ev-page">
        {err && <div className="adm-error">{err}</div>}
        <div className="card ev-empty" data-testid="load-empty">
          <div className="ev-empty-ico" aria-hidden>
            ⚡
          </div>
          <h2>ยังไม่มีผล load test</h2>
          <p className="muted">ยิงผู้ใช้จำลองพร้อมกัน 1 → 32 คน ผ่าน API จริง แล้วดูว่ารับได้กี่คนก่อนช้าเกินเกณฑ์</p>
          <pre className="ev-code">{`cd loadtest
node run_load.mjs --mode chat --users 1,2,4,8,16,32 --stage-sec 120`}</pre>
          <select className="select" data-testid="load-run-select" disabled>
            <option>ยังไม่มี run</option>
          </select>
        </div>
      </div>
    );
  }

  const qMax = Math.max(1, ...stages.map((s) => s.queue_max || 0));
  const hasTtft = stages.some((s) => s.ttft_p50 != null);
  const series = [
    { name: 'p50 ทั้งคำตอบ', color: SERIES[0], points: stages.map((s) => ({ x: s.users, y: s.p50 ?? null })) },
    { name: 'p95 ทั้งคำตอบ', color: '#ff6b6b', points: stages.map((s) => ({ x: s.users, y: s.p95 ?? null })) },
    ...(hasTtft
      ? [
          { name: 'TTFT p50', color: SERIES[1], points: stages.map((s) => ({ x: s.users, y: s.ttft_p50 ?? null })) },
          { name: 'TTFT p95', color: SERIES[2], points: stages.map((s) => ({ x: s.users, y: s.ttft_p95 ?? null })), dashed: true },
        ]
      : []),
  ];

  return (
    <div className="ev-page">
      {err && <div className="adm-error">{err}</div>}
      <section className="card ev-head">
        <div className="ev-head-main">
          <h1>ทดสอบรับโหลด · ผู้ใช้พร้อมกันได้กี่คน</h1>
          <p className="muted">
            {run.label} · {when(run)}
            {thr && (
              <>
                {' '}
                · เกณฑ์ p95 ≤ <b>{thr.p95_s ?? '–'} วิ</b>
                {thr.error_rate != null && <> · error ≤ {(thr.error_rate * 100).toFixed(0)}%</>}
              </>
            )}
          </p>
          <div className="ev-chips">
            {Object.entries(run.config || {})
              .filter(([, v]) => typeof v !== 'object')
              .map(([k, v]) => (
                <span key={k} className="ev-chip">
                  <small>{k}</small> {String(v)}
                </span>
              ))}
          </div>
        </div>
        <label className="ev-run">
          <span>เลือกรอบทดสอบ</span>
          <select
            className="select"
            data-testid="load-run-select"
            value={sel ?? ''}
            onChange={(e) => {
              const id = Number(e.target.value);
              setSel(id);
              load(id);
            }}
          >
            {runs.map((r) => (
              <option key={r.id} value={r.id}>
                #{r.id} · {modeOf(r) || '?'} · {r.label} · {when(r)}
              </option>
            ))}
          </select>
          {loading && <span className="adm-spin" aria-hidden />}
        </label>
      </section>

      <div className="ld-max">
        {MODES.map((m) => {
          const r = latestByMode[m.key];
          const v = maxOf(r);
          return (
            <button
              key={m.key}
              type="button"
              className={`ld-max-card${m.key === mode ? ' on' : ''}${r ? '' : ' none'}`}
              data-testid="load-max-users"
              data-mode={m.key}
              data-value={v ?? ''}
              disabled={!r}
              onClick={() => r && r.id !== run.id && load(r.id)}
            >
              <span className="ld-max-ico" aria-hidden>
                {m.icon}
              </span>
              <span className="ld-max-num">{v ?? '–'}</span>
              <span className="ld-max-lbl">
                <b>{m.label}</b> คนพร้อมกัน
              </span>
              <small>{r ? m.desc : 'ยังไม่ได้ทดสอบ'}</small>
            </button>
          );
        })}
      </div>

      <div className="ev-grid-2 ld-grid">
        <section className="card">
          <div className="adm-card-head">
            <h2>เวลาตอบ เทียบจำนวนผู้ใช้ ({mode || '–'})</h2>
            <span className="muted small">วินาที · แกน x สเกล log</span>
          </div>
          <Legend items={[...series.map((s) => ({ name: s.name, color: s.color, dashed: s.dashed })), ...(thr?.p95_s ? [{ name: `เกณฑ์ p95 ${thr.p95_s} วิ`, color: '#ff6b6b', dashed: true }] : [])]} />
          <LineChart
            testId="load-chart"
            series={series}
            threshold={thr?.p95_s ? { y: Number(thr.p95_s), label: `เกณฑ์ ${thr.p95_s} วิ` } : null}
            dep={run.id}
          />
        </section>
        <section className="card">
          <div className="adm-card-head">
            <h2>ความยาวคิวสูงสุด</h2>
            <span className="muted small">RabbitMQ · ข้อความที่รออยู่</span>
          </div>
          <div className="ld-queue" data-testid="load-queue-chart">
            {stages.map((s) => (
              <div key={s.users} className="ld-q-col">
                <span className="ld-q-val">{s.queue_max ?? 0}</span>
                <div className="ld-q-track">
                  <QBar v={(s.queue_max || 0) / qMax} ok={s.ok !== false} dep={run.id} />
                </div>
                <span className="ld-q-x">{s.users}</span>
              </div>
            ))}
          </div>
          <p className="small muted" style={{ margin: '8px 0 0' }}>
            คิวเริ่มสะสมเมื่อผู้ใช้มากกว่า prefetch ของ worker → เวลารอเพิ่มขึ้น (scale worker หรือเพิ่ม GPU)
          </p>
        </section>
      </div>

      <section className="card">
        <div className="adm-card-head">
          <h2>รายขั้น</h2>
          <span className="muted small">✓ = ผ่านเกณฑ์</span>
        </div>
        <div className="adm-table-wrap">
          <table className="adm-table">
            <thead>
              <tr>
                <th className="num">ผู้ใช้</th>
                <th className="num">คำขอ</th>
                <th className="num">error</th>
                <th className="num">p50 (วิ)</th>
                <th className="num">p95 (วิ)</th>
                <th className="num">TTFT p50/p95</th>
                <th className="num">RTF</th>
                <th className="num">token/วิ</th>
                <th className="num">คิวสูงสุด</th>
                <th>ผล</th>
              </tr>
            </thead>
            <tbody>
              {stages.map((s) => {
                const ok = s.ok ?? (thr?.p95_s ? (s.p95 ?? 0) <= thr.p95_s : true);
                return (
                  <tr key={s.users} data-testid="load-stage" data-users={s.users} data-ok={ok ? 'true' : 'false'}>
                    <td className="num">
                      <b>{s.users}</b>
                    </td>
                    <td className="num">{s.n ?? '–'}</td>
                    <td className="num">{s.errors ? <span className="adm-danger-text">{s.errors}</span> : 0}</td>
                    <td className="num">{num(s.p50)}</td>
                    <td className="num">{num(s.p95)}</td>
                    <td className="num">
                      {num(s.ttft_p50)} / {num(s.ttft_p95)}
                    </td>
                    <td className="num">{num(s.rtf, 3)}</td>
                    <td className="num">{num(s.tokens_per_s, 1)}</td>
                    <td className="num">{s.queue_max ?? '–'}</td>
                    <td>
                      <span className={`ev-pass ${ok ? 'ok' : 'no'}`}>{ok ? '✓' : '✗ เกินเกณฑ์'}</span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

function QBar({ v, ok, dep }: { v: number; ok: boolean; dep: unknown }) {
  // ใช้ Bar แนวนอนแล้วหมุน 90° ผ่าน CSS ไม่ได้สวย → ทำแท่งตั้งเอง
  const [on, setOn] = useState(false);
  useEffect(() => {
    setOn(false);
    const id = requestAnimationFrame(() => requestAnimationFrame(() => setOn(true)));
    return () => cancelAnimationFrame(id);
  }, [dep]);
  return <span className={`ld-q-bar${ok ? '' : ' bad'}`} style={{ height: on ? `${Math.max(2, v * 100)}%` : '0%' }} />;
}

