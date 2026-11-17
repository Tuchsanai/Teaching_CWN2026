import { NextResponse } from "next/server";
import { readReceipt, modelName, type ModelKey } from "@/lib/vlm";

export const dynamic = "force-dynamic";

// POST {image: data URL, model: "base" | "ft"} -> ผลอ่านใบเสร็จ
export async function POST(req: Request) {
  const { image, model } = (await req.json()) as { image?: string; model?: ModelKey };
  if (!image?.startsWith("data:image/")) return NextResponse.json({ error: "ไม่พบภาพใบเสร็จ" }, { status: 400 });
  const key: ModelKey = model === "ft" ? "ft" : "base";
  try {
    const r = await readReceipt(image, key);
    return NextResponse.json({ model: key, modelName: modelName(key), ...r });
  } catch (e) {
    return NextResponse.json({ error: `เรียก AI server ไม่สำเร็จ: ${(e as Error).message}` }, { status: 502 });
  }
}
