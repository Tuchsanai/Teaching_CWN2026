import { submitJob } from "@/lib/gateway";
import { PROMPTS } from "@/lib/prompts";
export const dynamic = "force-dynamic";

// ส่งงานเป็นชุดจากฝั่ง server (ยิงพร้อมกันครั้งละ 25 คำขอ) แล้วนับว่ารับกี่งาน ปฏิเสธกี่งาน
export async function POST(req) {
  const { count, priority } = await req.json().catch(() => ({}));
  const n = Math.min(Math.max(parseInt(count, 10) || 0, 1), 500);
  const pr = priority === "express" ? "express" : "normal";
  const t0 = Date.now();
  let next = 0, accepted = 0, rejected = 0, errors = 0, retryMax = 0;
  async function lane() {
    while (next < n) {
      const i = next++;
      try {
        const r = await submitJob(PROMPTS[i % PROMPTS.length], pr);
        if (r.ok) accepted++;
        else if (r.status === 429) { rejected++; retryMax = Math.max(retryMax, r.retry_after_seconds || 0); }
        else errors++;
      } catch { errors++; }
    }
  }
  await Promise.all(Array.from({ length: Math.min(25, n) }, lane));
  return Response.json({ sent: n, priority: pr, accepted, rejected, errors,
    retry_after_seconds: retryMax || null, seconds: +((Date.now() - t0) / 1000).toFixed(1) });
}
