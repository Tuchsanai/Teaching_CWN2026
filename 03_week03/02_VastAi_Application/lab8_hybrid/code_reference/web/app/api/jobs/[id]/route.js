import { gw } from "@/lib/gateway";
export const dynamic = "force-dynamic";

// long poll: gateway รอให้งานเสร็จได้สูงสุด 10 วินาทีต่อครั้ง
export async function GET(_req, { params }) {
  const id = String(params.id).replace(/[^a-f0-9]/gi, "");
  try {
    const r = await gw(`/jobs/${id}?wait=10`, {}, 15000);
    const body = await r.json().catch(() => ({}));
    if (body.image_url) body.image_url = `/api/jobs/${id}/image`;
    return Response.json(body, { status: r.status });
  } catch (e) {
    return Response.json({ error: e.message }, { status: 502 });
  }
}
