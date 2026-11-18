// Shared types + helpers (used on both server and browser; no secrets here).
export type Item = { name: string | null; qty: number | null; price: number | null };
export type Receipt = { items: Item[]; subtotal: number | null; tax: number | null; total: number | null };
export type ModelKey = "base" | "ft";
export const MODEL_LABEL: Record<ModelKey, string> = { base: "Base", ft: "Fine-tuned" };

/** Same rule as to_int() in receipt_data.py: '25,000' -> 25000, '30.000,00' -> 30000. */
export function toInt(v: unknown): number | null {
  if (Array.isArray(v)) v = v[0];
  if (v === null || v === undefined) return null;
  if (typeof v === "number") return Number.isFinite(v) ? Math.round(v) : null;
  let s = String(v).trim();
  s = s.replace(/[.,]\d{1,2}$/, "");
  const digits = s.replace(/\D/g, "");
  if (!digits) return null;
  const n = parseInt(digits, 10);
  return /^\s*[-(]/.test(s) ? -n : n;
}

/** Model reply -> Receipt, or null when it is not a readable JSON object. */
export function parseReply(text: string): Receipt | null {
  let s = text.trim();
  const m = s.match(/^```(?:json)?\s*([\s\S]*?)\s*```$/);
  if (m) s = m[1];
  let d: any;
  try { d = JSON.parse(s); } catch { return null; }
  if (!d || typeof d !== "object" || Array.isArray(d)) return null;
  const items: Item[] = (Array.isArray(d.items) ? d.items : [])
    .filter((it: any) => it && typeof it === "object")
    .map((it: any) => ({ name: it.name == null ? null : String(it.name), qty: toInt(it.qty), price: toInt(it.price) }));
  return { items, subtotal: toInt(d.subtotal), tax: toInt(d.tax), total: toInt(d.total) };
}

/** Same rule as eval.py: an item is correct when name (lower-case, letters/digits only) and price match the answer. */
export const normName = (n: string | null) => String(n ?? "").toLowerCase().replace(/[\W_]+/g, "");
const key = (it: Item) => `${normName(it.name)}|${it.price}`;

export type Score = { itemOk: boolean[]; missed: Item[]; tp: number; nGt: number; totalOk: boolean | null };
export function score(gt: Receipt, pred: Receipt | null): Score {
  const left = new Map<string, number>();
  gt.items.forEach((it) => left.set(key(it), (left.get(key(it)) ?? 0) + 1));
  const itemOk = (pred?.items ?? []).map((it) => {
    const k = key(it), c = left.get(k) ?? 0;
    if (c > 0) { left.set(k, c - 1); return true; }
    return false;
  });
  const missed: Item[] = [];
  const left2 = new Map(left);
  gt.items.forEach((it) => {
    const c = left2.get(key(it)) ?? 0;
    if (c > 0) { missed.push(it); left2.set(key(it), c - 1); }
  });
  const totalOk = gt.total === null ? null : pred !== null && pred.total === gt.total;
  return { itemOk, missed, tp: itemOk.filter(Boolean).length, nGt: gt.items.length, totalOk };
}

export const rp = (n: number | null | undefined) =>
  n === null || n === undefined ? "–" : "Rp " + n.toLocaleString("id-ID");
