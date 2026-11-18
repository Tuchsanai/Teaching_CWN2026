import { gw } from "@/lib/gateway";
export const dynamic = "force-dynamic";

// ภาพที่เสร็จแล้วไม่เปลี่ยน — เก็บไว้ในหน่วยความจำของเว็บ 300 ภาพล่าสุด ไม่ต้องดึงข้าม Vast.ai ซ้ำ
const cache = globalThis.__pqImages || (globalThis.__pqImages = new Map());
const MAX = 300;

function jpeg(buf) {
  return new Response(buf, {
    headers: { "Content-Type": "image/jpeg", "Cache-Control": "public, max-age=86400, immutable" },
  });
}

export async function GET(_req, { params }) {
  const id = String(params.id).replace(/[^a-f0-9]/gi, "");
  if (cache.has(id)) return jpeg(cache.get(id));
  try {
    const r = await gw(`/jobs/${id}/image`, {}, 15000);
    if (!r.ok) return new Response("image not ready", { status: r.status });
    const buf = Buffer.from(await r.arrayBuffer());
    cache.set(id, buf);
    if (cache.size > MAX) cache.delete(cache.keys().next().value);
    return jpeg(buf);
  } catch {
    return new Response("gateway error", { status: 502 });
  }
}
