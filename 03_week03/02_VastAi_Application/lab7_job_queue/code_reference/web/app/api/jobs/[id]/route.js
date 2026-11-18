import { gw, errorJson } from "@/lib/gateway";
export const dynamic = "force-dynamic";

export async function GET(_req, { params }) {
  const { id } = await params;
  if (!/^[a-f0-9]{6,32}$/.test(id)) return errorJson(new Error("รหัสงานไม่ถูกต้อง"), 400);
  try {
    const { status, body } = await gw(`/jobs/${id}`);
    return Response.json(body, { status });
  } catch (e) { return errorJson(e); }
}
