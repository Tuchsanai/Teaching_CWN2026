import { PROMPT } from "./prompt";

export type Item = { name: string; qty: number | null; price: number | null };
export type Receipt = { items: Item[]; subtotal: number | null; tax: number | null; total: number | null };
export type ModelKey = "base" | "ft";

const baseUrl = () => (process.env.RECEIPT_BASE_URL ?? "").replace(/\/+$/, "").replace(/\/v1$/, "");
const headers = () => ({ "Content-Type": "application/json", Authorization: `Bearer ${process.env.RECEIPT_API_KEY ?? ""}` });

export function modelName(key: ModelKey) {
  return key === "ft" ? process.env.RECEIPT_MODEL_FT ?? "receipt-ft" : process.env.RECEIPT_MODEL_BASE ?? "receipt-base";
}

// "Rp. 25,000" -> 25000 · ไม่มีตัวเลข -> null
function toInt(v: unknown): number | null {
  if (typeof v === "number" && Number.isFinite(v)) return Math.round(v);
  if (typeof v !== "string") return null;
  const digits = v.trim().replace(/[.,]\d{2}$/, "").replace(/\D/g, "");
  return digits ? parseInt(digits, 10) : null;
}

// ดึง JSON จากคำตอบของโมเดล · คืน null ถ้าอ่านเป็น JSON ตาม schema ไม่ได้
export function parseReceipt(text: string): Receipt | null {
  const t = text.trim().replace(/^```(?:json)?\s*|\s*```$/g, "");
  const a = t.indexOf("{");
  const b = t.lastIndexOf("}");
  if (a < 0 || b <= a) return null;
  try {
    const o = JSON.parse(t.slice(a, b + 1));
    if (!o || !Array.isArray(o.items)) return null;
    return {
      items: o.items
        .filter((x: unknown) => x && typeof x === "object")
        .map((x: Record<string, unknown>) => ({ name: String(x.name ?? ""), qty: toInt(x.qty), price: toInt(x.price) })),
      subtotal: toInt(o.subtotal),
      tax: toInt(o.tax),
      total: toInt(o.total),
    };
  } catch {
    return null;
  }
}

// ส่งภาพใบเสร็จ (data URL) ให้ VLM บน AI server แล้วคืนคำตอบดิบ + เวลา
export async function readReceipt(image: string, key: ModelKey) {
  const t0 = Date.now();
  const res = await fetch(`${baseUrl()}/v1/chat/completions`, {
    method: "POST",
    headers: headers(),
    body: JSON.stringify({
      model: modelName(key),
      temperature: 0,
      max_tokens: 1024,
      messages: [{ role: "user", content: [{ type: "image_url", image_url: { url: image } }, { type: "text", text: PROMPT }] }],
    }),
    signal: AbortSignal.timeout(120000),
  });
  if (!res.ok) throw new Error(`AI server ตอบ ${res.status}`);
  const j = await res.json();
  const raw: string = j.choices?.[0]?.message?.content ?? "";
  return { raw, seconds: (Date.now() - t0) / 1000, receipt: parseReceipt(raw) };
}

// รายชื่อโมเดลที่ AI server เปิดอยู่ (ใช้แสดงสถานะการเชื่อมต่อ)
export async function listModels(): Promise<string[]> {
  const res = await fetch(`${baseUrl()}/v1/models`, { headers: headers(), signal: AbortSignal.timeout(8000), cache: "no-store" });
  if (!res.ok) throw new Error(`AI server ตอบ ${res.status}`);
  const j = await res.json();
  return (j.data ?? []).map((m: { id: string }) => m.id);
}
