// เรียก gateway บน Vast.ai จากฝั่ง server เท่านั้น — key อยู่ใน process.env ไม่เคยถูกส่งไปเบราว์เซอร์
import "server-only";

function cfg() {
  const base = (process.env.T2I_BASE_URL || "").replace(/\/+$/, "");
  const key = process.env.T2I_API_KEY || "";
  if (!base || !key) throw new Error("ยังไม่ได้ตั้ง T2I_BASE_URL / T2I_API_KEY ใน .env");
  return { base, key };
}

export async function gw(path, init = {}, timeoutMs = 20000) {
  const { base, key } = cfg();
  const headers = { "X-API-Key": key, ...(init.headers || {}) };
  return fetch(base + path, { ...init, headers, cache: "no-store", signal: AbortSignal.timeout(timeoutMs) });
}

export async function submitJob(prompt, priority = "normal") {
  const r = await gw("/jobs", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt, priority }),
  });
  const body = await r.json().catch(() => ({}));
  if (r.status === 429) {
    const retry = Number(r.headers.get("retry-after")) || body.retry_after_seconds || 1;
    return { ok: false, status: 429, retry_after_seconds: retry, cap: body.cap, normal_waiting: body.normal_waiting };
  }
  return { ok: r.ok, status: r.status, ...body };
}
