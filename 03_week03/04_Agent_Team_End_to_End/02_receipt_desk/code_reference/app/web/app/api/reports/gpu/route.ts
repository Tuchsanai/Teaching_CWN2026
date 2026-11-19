/**
 * W22 · GET /api/reports/gpu — เทียบ GPU 1 กับ 2 ใบ · เจ้าของเท่านั้น (FR-30 · NFR-08)
 * ใช้ผลวัดล่าสุดของแต่ละจำนวน GPU ในตาราง gpu_benchmarks
 *   ใบ/นาที = receipt_count ÷ (seconds ÷ 60) · Speedup = อัตรา 2 ใบ ÷ อัตรา 1 ใบ · Efficiency = Speedup ÷ 2
 *   บาทต่อ 100 ใบ = cost_baht ÷ receipt_count × 100 · คุ้มเมื่อ Speedup ≥ 1.6 (เกณฑ์ SLO ข้อสองต้องดูจากผลทดสอบ NFR-02/05)
 */
import { requireUser } from '../../_lib/auth';
import { query } from '../../_lib/db';
import { handle, json } from '../../_lib/http';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const WORTH_SPEEDUP = 1.6;

interface BenchRow {
  id: string;
  gpu_count: number;
  receipt_count: number;
  seconds: string;
  cost_baht: string;
  measured_at: Date;
}

function r2(n: number | null): number | null {
  return n === null || !Number.isFinite(n) ? null : Math.round(n * 100) / 100;
}

function view(b: BenchRow) {
  const seconds = Number(b.seconds);
  const cost = Number(b.cost_baht);
  const rate = seconds > 0 ? b.receipt_count / (seconds / 60) : null;
  return {
    id: b.id,
    gpuCount: b.gpu_count,
    receipts: b.receipt_count,
    seconds: r2(seconds),
    minutes: r2(seconds / 60),
    receiptsPerMinute: r2(rate),
    costBaht: r2(cost),
    costPer100: b.receipt_count > 0 ? r2((cost / b.receipt_count) * 100) : null,
    measuredAt: new Date(b.measured_at).toISOString(),
    _rate: rate,
  };
}

export const GET = handle(async (request: Request) => {
  await requireUser(request, ['owner']);
  const rows = await query<BenchRow>(
    `SELECT id, gpu_count, receipt_count, seconds, cost_baht, measured_at FROM gpu_benchmarks ORDER BY measured_at DESC, id`,
  );
  const all = rows.map(view);
  const one = all.find((b) => b.gpuCount === 1) ?? null;
  const two = all.find((b) => b.gpuCount === 2) ?? null;
  const speedup = one?._rate && two?._rate ? two._rate / one._rate : null;
  const strip = (b: ReturnType<typeof view> | null) => {
    if (!b) return null;
    const { _rate, ...rest } = b;
    void _rate;
    return rest;
  };
  return json({
    oneGpu: strip(one),
    twoGpu: strip(two),
    speedup: r2(speedup),
    efficiency: speedup === null ? null : r2(speedup / 2),
    worthSpeedup: WORTH_SPEEDUP,
    worth: speedup === null ? null : speedup >= WORTH_SPEEDUP,
    verdict:
      speedup === null
        ? 'ยังไม่มีผลวัดครบทั้ง 1 และ 2 GPU'
        : speedup >= WORTH_SPEEDUP
          ? `คุ้ม: 2 GPU เร็วขึ้น ${r2(speedup)} เท่า (ไม่น้อยกว่า ${WORTH_SPEEDUP} เท่า)`
          : `ไม่คุ้มตามเกณฑ์ความเร็ว: 2 GPU เร็วขึ้น ${r2(speedup)} เท่า (ต่ำกว่า ${WORTH_SPEEDUP} เท่า) เว้นแต่ 1 GPU ทำ SLO ไม่ได้`,
    history: all.map(strip),
  });
});
