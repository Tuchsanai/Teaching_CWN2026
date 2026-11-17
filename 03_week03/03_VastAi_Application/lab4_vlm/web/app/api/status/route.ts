import { NextResponse } from "next/server";
import { listModels, modelName } from "@/lib/vlm";

export const dynamic = "force-dynamic";

// สถานะการเชื่อมต่อ AI server และโมเดลที่เปิดอยู่
export async function GET() {
  try {
    const models = await listModels();
    return NextResponse.json({ ok: true, base: models.includes(modelName("base")), ft: models.includes(modelName("ft")) });
  } catch (e) {
    return NextResponse.json({ ok: false, error: (e as Error).message });
  }
}
