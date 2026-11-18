import { gw } from "@/lib/gateway";
export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const r = await gw("/stats", {}, 8000);
    if (!r.ok) return Response.json({ error: `gateway ตอบ ${r.status}` }, { status: 502 });
    const s = await r.json();
    // ส่งเฉพาะที่หน้าเว็บใช้
    return Response.json({
      waiting: s.waiting, running: s.running, done: s.done, rejected: s.rejected_429,
      dead: s.dead?.jobs ?? 0, cap: s.cap_normal_now, live_workers: s.live_workers,
      sec_per_image: s.sec_per_image,
      workers: (s.workers || []).map((w) => ({
        name: w.worker, alive: w.alive, state: w.state, working: w.working || 0,
        done: w.done, last_seen_sec_ago: w.last_seen_sec_ago,
      })),
      recent: (s.recent_done || []).map((j) => ({
        id: j.id, prompt: j.prompt, priority: j.priority, worker: j.worker,
        seconds: j.seconds, total_seconds: j.total_seconds,
      })),
      ts: Date.now(),
    });
  } catch (e) {
    return Response.json({ error: "ติดต่อ gateway ไม่ได้: " + e.message }, { status: 502 });
  }
}
