// Server-only helper: every call to the LAB 8 gateway goes through here, so the API key
// never leaves the Next.js server process.
import "server-only";

const BASE = (process.env.GATEWAY_URL || "").replace(/\/+$/, "");
const KEY = process.env.GATEWAY_API_KEY || "";

export async function gw(path, init = {}) {
  if (!BASE || !KEY) throw new Error("GATEWAY_URL / GATEWAY_API_KEY ยังไม่ได้ตั้งใน .env");
  const res = await fetch(BASE + path, {
    ...init,
    headers: { ...(init.headers || {}), "X-API-Key": KEY },
    cache: "no-store",
    signal: AbortSignal.timeout(init.timeoutMs || 15000),
  });
  let body;
  try { body = await res.json(); } catch { body = { detail: res.statusText }; }
  return { status: res.status, body };
}

export function errorJson(e, status = 502) {
  return Response.json({ error: e?.message || String(e) }, { status });
}
