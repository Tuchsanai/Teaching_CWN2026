// รอให้เว็บพร้อม (GET /api/health) ก่อนเริ่มเพลย์ลิสต์ — กันกรณีเพิ่ง docker compose up / rebuild
export default async function globalSetup() {
  const url = (process.env.BM_URL || 'http://localhost:3400').replace(/\/$/, '');
  const until = Date.now() + 180_000;
  for (;;) {
    try {
      const r = await fetch(`${url}/api/health`);
      if (r.ok) return;
    } catch {}
    if (Date.now() > until) throw new Error(`เว็บ ${url} ยังไม่พร้อม (ลอง docker compose -p buildmart --profile mock up -d)`);
    await new Promise((r) => setTimeout(r, 2000));
  }
}
