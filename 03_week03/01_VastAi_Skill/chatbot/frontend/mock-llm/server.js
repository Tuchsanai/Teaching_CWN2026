// Mock LLM แบบ OpenAI-compatible (ไม่ต้องใช้ GPU) — ใช้ทดสอบระบบแบบ offline
// รองรับ: GET /v1/models, POST /v1/chat/completions (stream และ non-stream)
// ไม่มี dependency ใด ๆ (ใช้ http ของ Node ล้วน ๆ)
const http = require("http");

const PORT = Number(process.env.PORT || 8000);
const MODEL = "mock-thai-massage";

// คำสำคัญ -> ชื่อบริการ (สำรอง ถ้าอ่านจาก system prompt ไม่ได้)
const KEYWORDS = [
  ["ประคบ", "ประคบสมุนไพร"],
  ["น้ำมัน", "นวดน้ำมันอโรมา"],
  ["อโรมา", "นวดน้ำมันอโรมา"],
  ["เท้า", "นวดเท้าสะท้อนจุด"],
  ["คอ", "นวดคอบ่าไหล่"],
  ["บ่า", "นวดคอบ่าไหล่"],
  ["หลัง", "นวดแก้ปวดหลัง"],
  ["หน้า", "นวดหน้าและศีรษะ"],
  ["ศีรษะ", "นวดหน้าและศีรษะ"],
  ["นวดไทย", "นวดไทยแผนโบราณ"],
];

// อ่านรายการบริการจาก system prompt (บรรทัดรูปแบบ "- ชื่อ | 60 นาที | 350 บาท | ...")
function parseServices(system) {
  const out = [];
  const re = /^-\s*(.+?)\s*\|\s*(\d+)\s*นาที\s*\|\s*(\d+)\s*บาท/gm;
  let m;
  while ((m = re.exec(system))) out.push({ name: m[1], min: m[2], price: m[3] });
  return out;
}

function lineAfter(system, label) {
  const m = system.match(new RegExp(label + "\\s*:\\s*(.+)"));
  return m ? m[1].trim() : "";
}

function findService(text, services) {
  const sorted = [...services].sort((a, b) => b.name.length - a.name.length);
  for (const s of sorted) if (text.includes(s.name)) return s.name;
  for (const [k, name] of KEYWORDS) if (text.includes(k)) return name;
  return null;
}

function pad(n) {
  return String(n).padStart(2, "0");
}

function findDateTime(text, today) {
  let date = null;
  const iso = text.match(/(\d{4})-(\d{1,2})-(\d{1,2})/);
  const dmy = text.match(/(\d{1,2})\/(\d{1,2})\/(\d{4})/);
  if (iso) {
    date = `${iso[1]}-${pad(iso[2])}-${pad(iso[3])}`;
  } else if (dmy) {
    let y = Number(dmy[3]);
    if (y > 2400) y -= 543; // พ.ศ. -> ค.ศ.
    date = `${y}-${pad(dmy[2])}-${pad(dmy[1])}`;
  } else if (/มะรืน|พรุ่งนี้|วันนี้/.test(text)) {
    const base = today ? new Date(today + "T00:00:00Z") : new Date();
    const add = /มะรืน/.test(text) ? 2 : /พรุ่งนี้/.test(text) ? 1 : 0;
    base.setUTCDate(base.getUTCDate() + add);
    date = base.toISOString().slice(0, 10);
  }
  // เวลา: 14:00 / 14.30 / บ่าย 2 / 14 โมง
  let time = null;
  const hm = text.match(/(?:^|[^\d-])(\d{1,2})[:.](\d{2})(?!\d)/);
  const bai = text.match(/บ่าย\s*(\d{1,2})/);
  const mong = text.match(/(\d{1,2})\s*โมง/);
  if (hm) time = `${pad(hm[1])}:${hm[2]}`;
  else if (bai) time = `${pad(Number(bai[1]) + 12)}:00`;
  else if (mong) time = `${pad(mong[1])}:00`;
  return { date, time };
}

function buildReply(messages) {
  const system = messages.filter((m) => m.role === "system").map((m) => String(m.content || "")).join("\n");
  const users = messages.filter((m) => m.role === "user").map((m) => String(m.content || ""));
  const last = users[users.length - 1] || "";
  const services = parseServices(system);
  const today = (system.match(/(\d{4}-\d{2}-\d{2})/) || [])[1];

  // ---------- การจอง ----------
  // นับข้อความตั้งแต่ครั้งล่าสุดที่ผู้ใช้พิมพ์คำว่า "จอง"
  let startIdx = -1;
  users.forEach((u, i) => {
    if (u.includes("จอง")) startIdx = i;
  });
  if (startIdx >= 0) {
    const convo = users.slice(startIdx).join(" \n ");
    const phone = (convo.match(/0\d{1,2}[- ]?\d{3}[- ]?\d{3,4}/) || [])[0];
    const nameM = convo.match(/ชื่อ\s*(?:คุณ)?\s*([^\s,]+)/);
    const name = nameM ? nameM[1].replace(/(เบอร์|โทร).*$/, "").trim() : null;
    const service = findService(convo, services);
    const { date, time } = findDateTime(convo, today);
    const missing = [];
    if (!name) missing.push("ชื่อ");
    if (!phone) missing.push("เบอร์โทรศัพท์");
    if (!service) missing.push("บริการที่ต้องการ");
    if (!date || !time) missing.push("วันและเวลา (เช่น 2026-10-20 14:00)");
    if (missing.length === 0) {
      const tag = JSON.stringify({
        customer_name: name,
        phone: phone.replace(/\s/g, ""),
        service,
        booking_time: `${date} ${time}`,
      });
      return `ได้เลยค่ะ คุณ${name} 🙏 ทางร้านบันทึกการจอง "${service}" วันที่ ${date} เวลา ${time} น. เรียบร้อยแล้วค่ะ กรุณามาก่อนเวลานัด 10 นาทีนะคะ\n[BOOKING]${tag}`;
    }
    return `ยินดีรับจองค่ะ 😊 รบกวนขอข้อมูลเพิ่มเติม: ${missing.join(", ")}\n(ตัวอย่าง: จอง นวดไทย ชื่อสมชาย เบอร์ 081-234-5678 วันที่ 2026-10-20 เวลา 14:00)`;
  }

  // ---------- คำถามทั่วไป ----------
  if (/ปวดหลัง|แนะนำ/.test(last)) {
    return 'ถ้าปวดหลัง แนะนำ "นวดแก้ปวดหลัง" (60 นาที) หรือ "ประคบสมุนไพร" (60 นาที) ช่วยคลายกล้ามเนื้อได้ดีค่ะ หากปวดมากหรือมีอาการชา ควรปรึกษาแพทย์ก่อนนะคะ';
  }
  if (/ราคา|บริการ|เมนู|กี่บาท/.test(last)) {
    if (services.length) {
      const list = services.map((s) => `• ${s.name} ${s.min} นาที ${s.price} บาท`).join("\n");
      return `รายการบริการและราคาของร้านค่ะ\n${list}\nสนใจบริการไหน พิมพ์ "จองคิว" ได้เลยนะคะ`;
    }
    return "ขออภัยค่ะ ตอนนี้ยังไม่มีข้อมูลราคาในระบบ";
  }
  if (/เปิด|ปิด|เวลา|กี่โมง/.test(last)) {
    const h = lineAfter(system, "เวลาเปิด-ปิด");
    return `ร้าน${h || "เปิดทุกวัน"} ค่ะ 🕙`;
  }
  if (/ที่อยู่|ที่ไหน|แผนที่/.test(last)) {
    return `ร้านตั้งอยู่ที่ ${lineAfter(system, "ที่อยู่") || "-"} ค่ะ โทร ${lineAfter(system, "โทรศัพท์") || "-"}`;
  }
  if (/โปร|ส่วนลด/.test(last)) {
    return `โปรโมชันตอนนี้ค่ะ: ${lineAfter(system, "โปรโมชัน") || "ยังไม่มีโปรโมชันค่ะ"}`;
  }
  if (/สวัสดี|หวัดดี|hello|hi/i.test(last)) {
    return "สวัสดีค่ะ ยินดีต้อนรับสู่ร้านสบายใจ นวดแผนไทย 🌿 สอบถามราคา เวลาเปิดปิด หรือจองคิวได้เลยค่ะ";
  }
  return '(mock) ขอบคุณที่สอบถามค่ะ 🙏 ลองถามเรื่อง ราคา, เวลาเปิดปิด, โปรโมชัน, ที่อยู่ร้าน หรือพิมพ์ "จองคิว" ได้เลยนะคะ';
}

function send(res, code, obj) {
  res.writeHead(code, { "Content-Type": "application/json; charset=utf-8" });
  res.end(JSON.stringify(obj));
}

const server = http.createServer((req, res) => {
  const url = req.url.split("?")[0];
  if (req.method === "GET" && (url === "/v1/models" || url === "/models")) {
    return send(res, 200, { object: "list", data: [{ id: MODEL, object: "model", owned_by: "mock" }] });
  }
  if (req.method === "GET" && (url === "/" || url === "/health")) {
    return send(res, 200, { ok: true, model: MODEL });
  }
  if (req.method === "POST" && (url === "/v1/chat/completions" || url === "/chat/completions")) {
    let body = "";
    req.on("data", (c) => (body += c));
    req.on("end", () => {
      let data;
      try {
        data = JSON.parse(body || "{}");
      } catch {
        return send(res, 400, { error: { message: "invalid JSON" } });
      }
      const messages = Array.isArray(data.messages) ? data.messages : [];
      // ใส่ <think> ไว้ด้วย เพื่อทดสอบว่าฝั่ง web ตัดส่วนนี้ทิ้งได้จริง
      const text = "<think>ผู้ใช้ถามเรื่องร้านนวด ต้องตอบสุภาพ</think>" + buildReply(messages);
      const id = "chatcmpl-mock-" + Date.now();
      const created = Math.floor(Date.now() / 1000);
      console.log(`[mock-llm] ${messages.length} msgs, stream=${!!data.stream}`);

      if (!data.stream) {
        return send(res, 200, {
          id,
          object: "chat.completion",
          created,
          model: MODEL,
          choices: [{ index: 0, message: { role: "assistant", content: text }, finish_reason: "stop" }],
          usage: { prompt_tokens: 0, completion_tokens: 0, total_tokens: 0 },
        });
      }

      res.writeHead(200, {
        "Content-Type": "text/event-stream; charset=utf-8",
        "Cache-Control": "no-cache",
        Connection: "keep-alive",
      });
      const chars = Array.from(text);
      const pieces = [];
      for (let i = 0; i < chars.length; i += 4) pieces.push(chars.slice(i, i + 4).join(""));
      const chunk = (delta, finish = null) =>
        `data: ${JSON.stringify({ id, object: "chat.completion.chunk", created, model: MODEL, choices: [{ index: 0, delta, finish_reason: finish }] })}\n\n`;
      res.write(chunk({ role: "assistant", content: "" }));
      let i = 0;
      const timer = setInterval(() => {
        if (i < pieces.length) {
          res.write(chunk({ content: pieces[i++] }));
          return;
        }
        clearInterval(timer);
        res.write(chunk({}, "stop"));
        res.write("data: [DONE]\n\n");
        res.end();
      }, 15);
      res.on("close", () => clearInterval(timer));
    });
    return;
  }
  send(res, 404, { error: { message: "not found" } });
});

server.listen(PORT, "0.0.0.0", () => console.log(`[mock-llm] listening on :${PORT}`));
