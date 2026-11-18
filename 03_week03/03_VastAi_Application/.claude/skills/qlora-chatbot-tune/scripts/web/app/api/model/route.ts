import { asModelKey, modelInfo, setDefaultModel } from "@/lib/models";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

// GET  /api/model                      -> โมเดลเริ่มต้นตอนนี้ + รายชื่อโมเดล
// PUT  /api/model  {"model":"base"|"ft"} -> สลับโมเดลเริ่มต้นของเว็บ (มีผลกับข้อความถัดไปทันที)
export async function GET() {
  return Response.json(await modelInfo());
}

export async function PUT(req: Request) {
  const body = await req.json().catch(() => ({}));
  const k = asModelKey((body as { model?: string }).model);
  if (!k) return Response.json({ error: 'model ต้องเป็น "base" หรือ "ft"' }, { status: 400 });
  await setDefaultModel(k);
  return Response.json(await modelInfo());
}

export const POST = PUT;
