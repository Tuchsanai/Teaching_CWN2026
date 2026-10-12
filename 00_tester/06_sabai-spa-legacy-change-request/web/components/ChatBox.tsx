"use client";

import { useEffect, useRef, useState } from "react";
import { useI18n } from "./I18nProvider.tsx";

interface Msg {
  from: "me" | "bot";
  text: string;
}

/** FR-25/26 แชทตอบเวลา/ราคา และจองผ่าน API เดียวกับเว็บ (สถานะการคุยเก็บในหน่วยความจำหน้าเว็บ) */
export function ChatBox({ greeting }: { greeting: string }) {
  const { t } = useI18n();
  const [msgs, setMsgs] = useState<Msg[]>([{ from: "bot", text: greeting }]);
  const [text, setText] = useState("");
  const [state, setState] = useState<unknown>(null);
  const [busy, setBusy] = useState(false);
  const logRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    logRef.current?.scrollTo({ top: logRef.current.scrollHeight });
  }, [msgs]);

  const send = async (e: React.FormEvent) => {
    e.preventDefault();
    const m = text.trim();
    if (!m || busy) return;
    setMsgs((x) => [...x, { from: "me", text: m }]);
    setText("");
    setBusy(true);
    try {
      const r = await fetch("/api/chat", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ message: m, state }) });
      const j = await r.json();
      setMsgs((x) => [...x, { from: "bot", text: r.ok ? j.reply : j.message }]);
      if (r.ok) setState(j.state);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="card chat-box">
      <div className="chat-log" ref={logRef} aria-live="polite" data-testid="chat-log">
        {msgs.map((m, i) => (
          <div key={i} className={`msg ${m.from}`} data-testid={m.from === "bot" ? "chat-bot-msg" : "chat-user-msg"}>
            {m.text}
          </div>
        ))}
      </div>
      <form className="chat-form" onSubmit={send}>
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder={t("chat.placeholder")}
          aria-label={t("chat.input")}
          data-testid="chat-input"
        />
        <button type="submit" className="btn" disabled={busy} data-testid="chat-send">
          {t("chat.send")}
        </button>
      </form>
    </div>
  );
}
