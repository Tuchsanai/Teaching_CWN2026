// Client สำหรับ LLM แบบ OpenAI-compatible (ninfer / vLLM / mock)
// - ลอง stream ก่อน ถ้าไม่สำเร็จจะ fallback เป็น non-stream อัตโนมัติ
// - ตัด <think>...</think> ออกจากคำตอบ

export type ChatMsg = { role: "system" | "user" | "assistant"; content: string };

function endpoint(): string {
  const base = (process.env.LLM_BASE_URL || "http://mock-llm:8000").trim().replace(/\/+$/, "");
  // รองรับทั้งกรณีใส่ /v1 และไม่ใส่
  return base.endsWith("/v1") ? `${base}/chat/completions` : `${base}/v1/chat/completions`;
}

function headers(): Record<string, string> {
  const h: Record<string, string> = { "Content-Type": "application/json" };
  const key = (process.env.LLM_API_KEY || "").trim();
  if (key) h["Authorization"] = `Bearer ${key}`;
  return h;
}

function payload(messages: ChatMsg[], stream: boolean) {
  return JSON.stringify({
    model: process.env.LLM_MODEL || "mock-thai-massage",
    messages,
    stream,
    temperature: 0.3,
    max_tokens: 1024,
  });
}

const TIMEOUT = () => Number(process.env.LLM_TIMEOUT_MS || 120000);

/** ตัดส่วนความคิดของโมเดล (<think>) ออก — ใช้ได้กับข้อความที่ยังมาไม่ครบด้วย */
export function stripThink(raw: string): string {
  let s = raw;
  // กรณีมีแค่ </think> (template ใส่ <think> ให้เอง) -> ตัดทุกอย่างก่อนหน้า
  const lastClose = s.lastIndexOf("</think>");
  if (lastClose !== -1 && s.slice(0, lastClose).indexOf("<think>") === -1) {
    s = s.slice(lastClose + "</think>".length);
  }
  s = s.replace(/<think>[\s\S]*?<\/think>/g, "");
  const open = s.indexOf("<think>");
  if (open !== -1) s = s.slice(0, open); // ยังคิดไม่จบ
  // ตัด "<thi" ที่ค้างท้ายข้อความ
  const tail = s.match(/<\/?t?h?i?n?k?$/);
  if (tail && "<think>".startsWith(tail[0].replace("/", ""))) s = s.slice(0, tail.index);
  return s.replace(/^\s+/, "");
}

/**
 * เรียก LLM แล้วคืนข้อความเต็ม (raw ยังไม่ตัด think)
 * onDelta จะถูกเรียกทุกครั้งที่ได้ข้อความใหม่ (ส่ง raw สะสมทั้งหมด)
 */
export async function callLLM(messages: ChatMsg[], onDelta?: (rawSoFar: string) => void): Promise<string> {
  // ---- 1) ลองแบบ stream ----
  let raw = "";
  try {
    const res = await fetch(endpoint(), {
      method: "POST",
      headers: headers(),
      body: payload(messages, true),
      signal: AbortSignal.timeout(TIMEOUT()),
    });
    const ctype = res.headers.get("content-type") || "";
    if (res.ok && res.body && ctype.includes("text/event-stream")) {
      const reader = res.body.getReader();
      const dec = new TextDecoder();
      let buf = "";
      outer: while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buf += dec.decode(value, { stream: true });
        let nl: number;
        while ((nl = buf.indexOf("\n")) !== -1) {
          const line = buf.slice(0, nl).trim();
          buf = buf.slice(nl + 1);
          if (!line.startsWith("data:")) continue;
          const data = line.slice(5).trim();
          if (data === "[DONE]") break outer;
          try {
            const j = JSON.parse(data);
            const piece = j?.choices?.[0]?.delta?.content ?? j?.choices?.[0]?.message?.content ?? "";
            if (piece) {
              raw += piece;
              onDelta?.(raw);
            }
          } catch {
            /* ข้ามบรรทัดที่ parse ไม่ได้ */
          }
        }
      }
      if (raw.trim()) return raw;
    } else if (res.ok && ctype.includes("application/json")) {
      // server ไม่รองรับ stream แต่ตอบเป็น JSON มาเลย
      const j = await res.json();
      const text = j?.choices?.[0]?.message?.content ?? "";
      if (text) {
        onDelta?.(text);
        return text;
      }
    } else {
      console.warn(`[llm] stream failed: HTTP ${res.status}`);
    }
  } catch (e) {
    console.warn("[llm] stream error, falling back to non-stream:", (e as Error).message);
    if (raw.trim()) return raw; // ได้ข้อความมาบางส่วนแล้ว ใช้ส่วนนั้น
  }

  // ---- 2) fallback: non-stream ----
  const res = await fetch(endpoint(), {
    method: "POST",
    headers: headers(),
    body: payload(messages, false),
    signal: AbortSignal.timeout(TIMEOUT()),
  });
  if (!res.ok) {
    const t = await res.text().catch(() => "");
    throw new Error(`LLM HTTP ${res.status}: ${t.slice(0, 200)}`);
  }
  const j = await res.json();
  const text: string = j?.choices?.[0]?.message?.content ?? "";
  onDelta?.(text);
  return text;
}
