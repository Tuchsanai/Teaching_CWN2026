import { gw, errorJson } from "@/lib/gateway";
export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const { status, body } = await gw("/stats");
    return Response.json(body, { status });
  } catch (e) { return errorJson(e); }
}
