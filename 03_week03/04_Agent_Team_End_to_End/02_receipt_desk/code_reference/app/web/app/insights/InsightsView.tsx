'use client';
/**
 * เวลาตรวจ (W21 GET /api/reports/review-time) · GPU 1 เทียบ 2 ใบ (W22 GET /api/reports/gpu · เจ้าของเท่านั้น)
 * testid: review-time-average · review-time-table · gpu-table · gpu-speedup · gpu-efficiency · gpu-cost-per-100 · gpu-verdict
 * - review-time-average = วินาทีเฉลี่ยต่อใบ (ตัวเลขล้วน) · เป้า < 120 วินาที (NFR-09)
 * - gpu-speedup = เท่า (เช่น 1.85) · gpu-efficiency = ร้อยละ (เช่น 92.5) · gpu-cost-per-100 = บาทต่อ 100 ใบของ 2 GPU
 *   (ค่าของ 1 GPU อยู่ใน gpu-table) · ถือว่าคุ้มเมื่อ Speedup ≥ 1.6 (NFR-08)
 */
import { useEffect, useState } from 'react';
import { api, errorText } from '../_ui/api';
import { dateTime, money } from '../_ui/format';

interface ReviewTime {
  averageSeconds: number | null;
  receipts: number;
  targetSeconds: number;
  meetsTarget: boolean | null;
  batches: {
    batchId: string;
    clientName: string;
    acceptedAt: string;
    receipts: number;
    averageSeconds: number | null;
    flaggedAverageSeconds: number | null;
    normalAverageSeconds: number | null;
  }[];
}

interface GpuRun {
  gpuCount: number;
  receipts: number;
  minutes: number | null;
  receiptsPerMinute: number | null;
  costBaht: number | null;
  costPer100: number | null;
  measuredAt: string;
}

interface Gpu {
  oneGpu: GpuRun | null;
  twoGpu: GpuRun | null;
  speedup: number | null;
  efficiency: number | null;
  worthSpeedup: number;
  worth: boolean | null;
  verdict: string;
}

const sec = (n: number | null | undefined) => (n === null || n === undefined ? '—' : String(n));

export default function InsightsView({ showGpu }: { showGpu: boolean }) {
  const [rt, setRt] = useState<ReviewTime | null>(null);
  const [gpu, setGpu] = useState<Gpu | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api<ReviewTime>('/api/reports/review-time').then((r) => (r.ok ? setRt(r.data) : setError(errorText(r.error))));
    if (showGpu) api<Gpu>('/api/reports/gpu').then((r) => (r.ok ? setGpu(r.data) : setError(errorText(r.error))));
  }, [showGpu]);

  return (
    <>
      {error ? <div className="notice error">{error}</div> : null}

      <section className="card">
        <h2 style={{ fontSize: 16, marginTop: 0 }}>เวลาตรวจต่อใบ (เปิดใบจนกดยืนยัน)</h2>
        <div className="stats">
          <div className="stat">
            <div className="label">เฉลี่ยต่อใบ (วินาที)</div>
            <div className="value" data-testid="review-time-average">
              {rt ? sec(rt.averageSeconds) : '…'}
            </div>
          </div>
          <div className="stat">
            <div className="label">จำนวนใบที่นับ</div>
            <div className="value">{rt ? rt.receipts : '…'}</div>
          </div>
          <div className="stat">
            <div className="label">เป้าหมาย</div>
            <div className="value">
              {'< '}
              {rt?.targetSeconds ?? 120}
              {rt && rt.meetsTarget !== null ? (
                <span className={rt.meetsTarget ? 'badge' : 'badge bad'}>{rt.meetsTarget ? 'ผ่าน' : 'ไม่ผ่าน'}</span>
              ) : null}
            </div>
          </div>
        </div>
        <table data-testid="review-time-table" style={{ marginTop: 12 }}>
          <thead>
            <tr>
              <th>ชุด (รับเมื่อ)</th>
              <th>ลูกค้า</th>
              <th className="num">ใบที่ยืนยัน</th>
              <th className="num">เฉลี่ย (วินาที)</th>
              <th className="num">ใบติดธง</th>
              <th className="num">ใบปกติ</th>
            </tr>
          </thead>
          <tbody>
            {rt?.batches.map((b) => (
              <tr key={b.batchId} data-testid={`review-time-row-${b.batchId}`}>
                <td>{dateTime(b.acceptedAt)}</td>
                <td>{b.clientName}</td>
                <td className="num">{b.receipts}</td>
                <td className="num">{sec(b.averageSeconds)}</td>
                <td className="num">{sec(b.flaggedAverageSeconds)}</td>
                <td className="num">{sec(b.normalAverageSeconds)}</td>
              </tr>
            ))}
            {rt && rt.batches.length === 0 ? (
              <tr>
                <td colSpan={6} className="muted">
                  ยังไม่มีใบที่ยืนยันพร้อมเวลาตรวจ
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </section>

      {showGpu ? (
        <section className="card">
          <h2 style={{ fontSize: 16, marginTop: 0 }}>GPU 1 ใบ เทียบ 2 ใบ (งานชุดเดียวกัน)</h2>
          <table data-testid="gpu-table">
            <thead>
              <tr>
                <th>จำนวน GPU</th>
                <th className="num">ใบ</th>
                <th className="num">เวลา (นาที)</th>
                <th className="num">ใบต่อนาที</th>
                <th className="num">ค่าเช่า (บาท)</th>
                <th className="num">บาทต่อ 100 ใบ</th>
                <th>วัดเมื่อ</th>
              </tr>
            </thead>
            <tbody>
              {[gpu?.oneGpu, gpu?.twoGpu].map((g, i) =>
                g ? (
                  <tr key={g.gpuCount} data-testid={`gpu-row-${g.gpuCount}`}>
                    <td>{g.gpuCount}</td>
                    <td className="num">{g.receipts}</td>
                    <td className="num">{sec(g.minutes)}</td>
                    <td className="num">{sec(g.receiptsPerMinute)}</td>
                    <td className="num">{money(g.costBaht)}</td>
                    <td className="num">{money(g.costPer100)}</td>
                    <td>{dateTime(g.measuredAt)}</td>
                  </tr>
                ) : (
                  <tr key={`none-${i}`}>
                    <td>{i + 1}</td>
                    <td colSpan={6} className="muted">
                      ยังไม่มีผลวัด
                    </td>
                  </tr>
                ),
              )}
            </tbody>
          </table>
          <div className="stats" style={{ marginTop: 12 }}>
            <div className="stat">
              <div className="label">Speedup (เท่า)</div>
              <div className="value" data-testid="gpu-speedup">
                {gpu ? sec(gpu.speedup) : '…'}
              </div>
            </div>
            <div className="stat">
              <div className="label">Efficiency (%)</div>
              <div className="value" data-testid="gpu-efficiency">
                {gpu ? (gpu.efficiency === null ? '—' : (Math.round(gpu.efficiency * 1000) / 10).toFixed(1)) : '…'}
              </div>
            </div>
            <div className="stat">
              <div className="label">บาทต่อ 100 ใบ (2 GPU)</div>
              <div className="value" data-testid="gpu-cost-per-100">
                {gpu ? money(gpu.twoGpu?.costPer100 ?? null) : '…'}
              </div>
            </div>
          </div>
          <div
            className={`notice ${gpu?.worth ? 'ok' : 'warn'}`}
            data-testid="gpu-verdict"
            data-worth={gpu?.worth === null || gpu?.worth === undefined ? '' : String(gpu.worth)}
          >
            {gpu ? gpu.verdict : '…'}
          </div>
        </section>
      ) : null}
    </>
  );
}
