"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";

type Booking = {
  id: number;
  customer_name: string;
  phone: string;
  service_name: string;
  duration_min: number;
  price_thb: number;
  booking_time: string;
  status: string;
};

type Msg = {
  id: number;
  role: "user" | "assistant";
  text: string;
  booking?: Booking;
  bookingError?: string;
  error?: boolean;
};

const QUICK_REPLIES = [
  { key: "price", label: "💰 ดูราคา", text: "ขอดูราคาบริการทั้งหมดหน่อยค่ะ" },
  { key: "hours", label: "🕙 เวลาเปิดปิด", text: "ร้านเปิดปิดกี่โมงคะ" },
  { key: "backpain", label: "🌿 แนะนำนวดแก้ปวดหลัง", text: "ปวดหลังมาก แนะนำนวดแบบไหนดีคะ" },
  { key: "promo", label: "🎁 โปรโมชัน", text: "ตอนนี้มีโปรโมชันอะไรบ้างคะ" },
  { key: "book", label: "📅 จองคิว", text: "อยากจองคิวนวดค่ะ" },
];

const WELCOME: Msg = {
  id: 0,
  role: "assistant",
  text: "สวัสดีค่ะ ยินดีต้อนรับสู่ “สบายใจ นวดแผนไทย” 🌿\nสอบถามราคา เวลาเปิดปิด หรือจองคิวกับน้องสบายใจได้เลยนะคะ",
};

/** แสดง **ตัวหนา** แบบปลอดภัย (สร้าง React element เอง ไม่ใช้ HTML ดิบ) และตัด # หัวข้อ markdown */
function renderText(text: string) {
  const clean = text.replace(/^#{1,6}\s+/gm, "");
  return clean.split(/(\*\*[^*\n]+\*\*)/g).map((part, i) =>
    /^\*\*[^*\n]+\*\*$/.test(part) ? <strong key={i}>{part.slice(2, -2)}</strong> : part.replace(/\*\*/g, "")
  );
}

function newSessionId() {
  try {
    return crypto.randomUUID();
  } catch {
    return "s-" + Date.now().toString(36) + "-" + Math.random().toString(36).slice(2, 10);
  }
}

export default function Chat() {
  const [messages, setMessages] = useState<Msg[]>([WELCOME]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [waitingFirstToken, setWaitingFirstToken] = useState(false);
  const sessionRef = useRef<string>("");
  const idRef = useRef(1);
  const listRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    sessionRef.current = newSessionId();
  }, []);

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, waitingFirstToken]);

  function patch(id: number, p: Partial<Msg>) {
    setMessages((ms) => ms.map((m) => (m.id === id ? { ...m, ...p } : m)));
  }

  async function send(text: string) {
    const msg = text.trim();
    if (!msg || busy) return;
    setInput("");
    setBusy(true);
    setWaitingFirstToken(true);
    const userId = idRef.current++;
    const botId = idRef.current++;
    setMessages((ms) => [...ms, { id: userId, role: "user", text: msg }]);

    let botAdded = false;
    const upsertBot = (p: Partial<Msg>) => {
      if (!botAdded) {
        botAdded = true;
        setWaitingFirstToken(false);
        setMessages((ms) => [...ms, { id: botId, role: "assistant", text: "", ...p }]);
      } else patch(botId, p);
    };

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionRef.current, message: msg }),
      });
      if (!res.ok || !res.body) throw new Error(`HTTP ${res.status}`);
      const reader = res.body.getReader();
      const dec = new TextDecoder();
      let buf = "";
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buf += dec.decode(value, { stream: true });
        let idx: number;
        while ((idx = buf.indexOf("\n\n")) !== -1) {
          const chunk = buf.slice(0, idx).trim();
          buf = buf.slice(idx + 2);
          if (!chunk.startsWith("data:")) continue;
          const ev = JSON.parse(chunk.slice(5).trim());
          if (ev.type === "text" && ev.text) upsertBot({ text: ev.text });
          else if (ev.type === "done") upsertBot({ text: ev.text || "" });
          else if (ev.type === "booking") upsertBot({ booking: ev.booking });
          else if (ev.type === "booking_error") upsertBot({ bookingError: ev.message });
          else if (ev.type === "error") upsertBot({ text: ev.message, error: true });
        }
      }
      if (!botAdded) upsertBot({ text: "ขออภัยค่ะ ไม่ได้รับคำตอบจากระบบ", error: true });
    } catch {
      upsertBot({ text: "ขออภัยค่ะ เชื่อมต่อเซิร์ฟเวอร์ไม่ได้ ลองใหม่อีกครั้งนะคะ", error: true });
    } finally {
      setBusy(false);
      setWaitingFirstToken(false);
      inputRef.current?.focus();
    }
  }

  function resetChat() {
    sessionRef.current = newSessionId();
    setMessages([WELCOME]);
  }

  return (
    <main className="page chatpage">
      <header className="topbar">
        <div className="brand">
          <span className="logo">🌿</span>
          <div>
            <h1>สบายใจ นวดแผนไทย</h1>
            <p>Sabaijai Thai Massage · เปิดทุกวัน 10:00–22:00</p>
          </div>
        </div>
        <nav className="navs">
          <button className="navlink ghost" onClick={resetChat} data-testid="reset-chat" type="button">
            เริ่มแชทใหม่
          </button>
          <Link href="/bookings" className="navlink" data-testid="nav-bookings">
            รายการจอง
          </Link>
        </nav>
      </header>

      <section className="card chatcard">
        <div className="messages" ref={listRef} data-testid="message-list">
          {messages.map((m) => (
            <div key={m.id} className={`row ${m.role}`}>
              {m.role === "assistant" && <div className="avatar">🙏</div>}
              <div className="stack">
                {(m.text || !m.booking) && (
                  <div
                    className={`bubble ${m.role}${m.error ? " error" : ""}`}
                    data-testid="message-bubble"
                    data-role={m.role}
                  >
                    {m.role === "assistant" ? renderText(m.text) : m.text}
                  </div>
                )}
                {m.booking && (
                  <div className="booking-card" data-testid="booking-card" data-booking-id={m.booking.id}>
                    <div className="booking-head">✅ จองคิวสำเร็จ · หมายเลข #{m.booking.id}</div>
                    <dl>
                      <dt>ชื่อ</dt>
                      <dd data-testid="booking-card-name">{m.booking.customer_name}</dd>
                      <dt>เบอร์โทร</dt>
                      <dd data-testid="booking-card-phone">{m.booking.phone}</dd>
                      <dt>บริการ</dt>
                      <dd data-testid="booking-card-service">
                        {m.booking.service_name} ({m.booking.duration_min} นาที · {m.booking.price_thb} บาท)
                      </dd>
                      <dt>วันเวลา</dt>
                      <dd data-testid="booking-card-time">{m.booking.booking_time} น.</dd>
                    </dl>
                    <Link href="/bookings" className="booking-link">
                      ดูรายการจองทั้งหมด →
                    </Link>
                  </div>
                )}
                {m.bookingError && (
                  <div className="booking-card failed" data-testid="booking-error">
                    ⚠️ บันทึกการจองไม่สำเร็จ: {m.bookingError}
                  </div>
                )}
              </div>
            </div>
          ))}
          {waitingFirstToken && (
            <div className="row assistant">
              <div className="avatar">🙏</div>
              <div className="bubble assistant typing" data-testid="typing-indicator" aria-label="กำลังพิมพ์">
                <span />
                <span />
                <span />
              </div>
            </div>
          )}
        </div>

        <div className="chips" data-testid="quick-replies">
          {QUICK_REPLIES.map((q) => (
            <button
              key={q.key}
              type="button"
              className="chip"
              data-testid="quick-reply-chip"
              data-chip={q.key}
              disabled={busy}
              onClick={() => send(q.text)}
            >
              {q.label}
            </button>
          ))}
        </div>

        <form
          className="composer"
          onSubmit={(e) => {
            e.preventDefault();
            send(input);
          }}
        >
          <input
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="พิมพ์ข้อความ เช่น อยากจองนวดไทยพรุ่งนี้บ่าย 2"
            data-testid="chat-input"
            aria-label="ข้อความ"
            autoComplete="off"
            maxLength={2000}
          />
          <button type="submit" data-testid="send-button" disabled={busy || !input.trim()}>
            ส่ง
          </button>
        </form>
      </section>
    </main>
  );
}
