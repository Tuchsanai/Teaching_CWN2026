"use client";

import { useEffect, useRef, useState } from "react";
import { api, useApp } from "./AppProvider";
import { Icon } from "./Ornament";
import { chatText, detectIntent, detectLang, parseTime, relativeDay, yesNo } from "@/lib/chatbot";
import { errorText, type Lang } from "@/lib/i18n";
import { addDays, formatBaht, formatDate, isDateStr } from "@/lib/time";
import { transportQuote } from "@/lib/rules";

type Svc = { slug: string; duration: number; price: number; name_th: string; name_en: string; name_zh: string; is_package: boolean };
type Option = { label: string; value: string };
type Line = { from: "bot" | "user"; text: string };
type Step = "service" | "date" | "people" | "time" | "transfer" | "hotel" | "name" | "phone" | "confirm";
type Flow = {
  step: Step;
  service?: Svc;
  date?: string;
  people?: number;
  time?: string;
  hotelId?: number | null;
  guestName?: string;
  guestPhone?: string;
};

const STOP = ["ยกเลิก", "cancel", "取消", "stop"];
const PER_PERSON: Record<Lang, string> = { th: "/คน", en: "/person", zh: "/人" };

export function ChatBot() {
  const { lang, config, refreshConfig, user, refreshUser, t } = useApp();
  const [open, setOpen] = useState(false);
  const [lines, setLines] = useState<Line[]>([]);
  const [options, setOptions] = useState<Option[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const chatLang = useRef<Lang>(lang);
  const flow = useRef<Flow | null>(null);
  const services = useRef<Svc[]>([]);
  const listRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (open && lines.length === 0) {
      chatLang.current = lang;
      setLines([{ from: "bot", text: chatText(lang, "greeting") }]);
    }
  }, [open, lines.length, lang]);

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: "smooth" });
  }, [lines, options]);

  const say = (text: string, opts: Option[] = []) => {
    setLines((l) => [...l, { from: "bot", text }]);
    setOptions(opts);
  };

  const loadServices = async () => {
    if (!services.current.length) {
      const r = await api<{ ok: boolean; services: Svc[] }>("/api/services");
      if (r.ok) services.current = r.services;
    }
    return services.current;
  };

  const svcName = (s: Svc, l: Lang) => (l === "th" ? s.name_th : l === "zh" ? s.name_zh : s.name_en);
  const yesNoOpts = (l: Lang): Option[] => [
    { label: chatText(l, "yes"), value: chatText(l, "yes") },
    { label: chatText(l, "no"), value: chatText(l, "no") },
  ];

  const askService = async (l: Lang) => {
    const list = await loadServices();
    const text = chatText(l, "askService") + "\n" + list.map((s, i) => `${i + 1}. ${svcName(s, l)} — ${formatBaht(s.price)}`).join("\n");
    say(text, list.map((s, i) => ({ label: `${i + 1}. ${svcName(s, l)}`, value: String(i + 1) })));
  };

  const askDate = async (l: Lang) => {
    const c = (await refreshConfig()) ?? config;
    if (!c) return say(errorText(l, "SERVER"));
    const opts = [1, 2, 3].map((n) => {
      const d = addDays(c.today, n);
      return { label: n === 1 ? `${chatText(l, "tomorrow")} · ${formatDate(d, l)}` : formatDate(d, l, true), value: d };
    });
    say(chatText(l, "askDate", { from: c.bookable.from, to: c.bookable.to }), opts);
  };

  const askTime = async (l: Lang, f: Flow) => {
    const qs = new URLSearchParams({ service: f.service!.slug, date: f.date!, people: String(f.people) });
    const r = await api<{ ok: boolean; slots: { time: string; status: string }[]; error?: string }>(`/api/availability?${qs}`);
    if (!r.ok) return say(errorText(l, r.error ?? "SERVER"));
    const free = r.slots.filter((s) => s.status === "free");
    if (!free.length) {
      f.step = "date";
      say(chatText(l, "noTime"));
      return askDate(l);
    }
    say(chatText(l, "askTime"), free.map((s) => ({ label: s.time, value: s.time })));
  };

  const askHotel = (l: Lang) => {
    const hs = config?.hotels ?? [];
    say(
      chatText(l, "askHotel") + "\n" + hs.map((h, i) => `${i + 1}. ${l === "zh" ? h.nameZh : h.name} (${h.distanceKm.toFixed(1)} km)`).join("\n"),
      [...hs.map((h, i) => ({ label: `${i + 1}. ${l === "zh" ? h.nameZh : h.name}`, value: String(i + 1) })), { label: chatText(l, "noTransfer"), value: chatText(l, "no") }],
    );
  };

  const params = (f: Flow) => ({
    service: f.service!.slug,
    date: f.date,
    time: f.time,
    people: f.people,
    transport: !!f.hotelId,
    hotelId: f.hotelId ?? null,
    guestName: f.guestName,
    guestPhone: f.guestPhone,
    source: "chatbot",
  });

  const askConfirm = async (l: Lang, f: Flow) => {
    const r = await api<{ ok: boolean; quote: any; issues: { code: string }[]; error?: string }>("/api/quote", { method: "POST", json: params(f) });
    if (!r.ok) return say(errorText(l, r.error ?? "SERVER"));
    if (r.issues.length) {
      say(errorText(l, r.issues[0].code));
      if (r.issues[0].code === "TRANSPORT_TOO_FAR") {
        f.step = "hotel";
        return askHotel(l);
      }
      return;
    }
    const q = r.quote;
    const disc = q.groupDiscount + q.tierDiscount + q.birthdayDiscount + q.pointsDiscount;
    const transport = f.hotelId ? chatText(l, "transferLine", { fee: q.transportFee === 0 ? t("free") : formatBaht(q.transportFee), cars: q.cars, km: q.distanceKm }) : chatText(l, "noTransfer");
    f.step = "confirm";
    say(
      chatText(l, "summary", {
        service: svcName(f.service!, l), date: formatDate(f.date!, l), time: f.time!, people: f.people!,
        subtotal: formatBaht(q.subtotal), discounts: disc > 0 ? chatText(l, "discounts", { amount: formatBaht(disc) }) : "",
        transport, total: formatBaht(q.total),
      }),
      [{ label: chatText(l, "confirm"), value: chatText(l, "confirm") }, { label: chatText(l, "stop"), value: chatText(l, "stop") }],
    );
  };

  const afterTransfer = async (l: Lang, f: Flow) => {
    if (!user) {
      f.step = "name";
      return say(chatText(l, "askName"));
    }
    return askConfirm(l, f);
  };

  const handleFlow = async (text: string, l: Lang, f: Flow) => {
    const raw = text.trim();
    const lower = raw.toLowerCase();
    if (f.step !== "confirm" && STOP.includes(lower)) {
      flow.current = null;
      return say(chatText(l, "aborted"));
    }
    switch (f.step) {
      case "service": {
        const list = await loadServices();
        const n = Number(raw.replace(/[^\d]/g, ""));
        const s =
          (n >= 1 && n <= list.length && /^\D*\d+\D*$/.test(raw) ? list[n - 1] : undefined) ??
          list.find((x) => [x.slug, x.name_th, x.name_en, x.name_zh].some((v) => v.toLowerCase().includes(lower) || lower.includes(v.toLowerCase())));
        if (!s) return say(chatText(l, "badService"), options);
        f.service = s;
        f.step = "date";
        return askDate(l);
      }
      case "date": {
        const c = config;
        let d: string | null = null;
        const rel = relativeDay(raw);
        if (rel !== null && c) d = addDays(c.today, rel);
        const m = raw.match(/\d{4}-\d{2}-\d{2}/);
        if (!d && m && isDateStr(m[0])) d = m[0];
        if (!d || !c || d < c.bookable.from || d > c.bookable.to) {
          return say(chatText(l, "badDate", { from: c?.bookable.from ?? "", to: c?.bookable.to ?? "" }), options);
        }
        f.date = d;
        f.step = "people";
        return say(chatText(l, "askPeople"), ["1", "2", "3", "4", "5", "6"].map((v) => ({ label: v, value: v })));
      }
      case "people": {
        const m = raw.match(/\d+/);
        const n = m ? Number(m[0]) : NaN;
        if (n >= 7) return say(errorText(l, "GROUP_TOO_LARGE"), options);
        if (!(n >= 1 && n <= 6)) return say(chatText(l, "badPeople"), options);
        f.people = n;
        f.step = "time";
        return askTime(l, f);
      }
      case "time": {
        const tm = parseTime(raw);
        const qs = new URLSearchParams({ service: f.service!.slug, date: f.date!, people: String(f.people) });
        const r = await api<{ ok: boolean; slots: { time: string; status: string }[] }>(`/api/availability?${qs}`);
        const slot = r.ok && tm ? r.slots.find((s) => s.time === tm) : undefined;
        if (!slot || slot.status === "closed") return say(chatText(l, "badTime"), options);
        if (slot.status === "booked") return say(errorText(l, "SLOT_TAKEN"), options); // same rule as the booking page
        f.time = tm!;
        f.step = "transfer";
        return say(chatText(l, "askTransfer"), yesNoOpts(l));
      }
      case "transfer": {
        const yn = yesNo(raw);
        if (!yn) return say(chatText(l, "yesNoHint"), yesNoOpts(l));
        if (yn === "yes") {
          f.step = "hotel";
          return askHotel(l);
        }
        f.hotelId = null;
        return afterTransfer(l, f);
      }
      case "hotel": {
        const hs = config?.hotels ?? [];
        if (yesNo(raw) === "no") {
          f.hotelId = null;
          return afterTransfer(l, f);
        }
        const n = /^\D*\d+\D*$/.test(raw) ? Number(raw.replace(/\D/g, "")) : NaN;
        const h = (n >= 1 && n <= hs.length ? hs[n - 1] : undefined) ?? hs.find((x) => x.name.toLowerCase().includes(lower) || x.nameZh.includes(raw));
        if (!h) return say(chatText(l, "badHotel"), options);
        const tq = transportQuote(h.distanceKm, f.people ?? 1);
        if (!tq.ok) return say(errorText(l, "TRANSPORT_TOO_FAR"), options);
        f.hotelId = h.id;
        return afterTransfer(l, f);
      }
      case "name": {
        if (raw.length < 1) return say(chatText(l, "askName"));
        f.guestName = raw.slice(0, 60);
        f.step = "phone";
        return say(chatText(l, "askPhone"));
      }
      case "phone": {
        if (raw.replace(/\D/g, "").length < 9) return say(chatText(l, "badPhone"));
        f.guestPhone = raw;
        return askConfirm(l, f);
      }
      case "confirm": {
        const yn = yesNo(raw);
        if (yn === "no" || STOP.includes(lower)) {
          flow.current = null;
          return say(chatText(l, "aborted"));
        }
        if (yn !== "yes") return say(chatText(l, "yesNoHint"), options);
        const r = await api<{ ok: boolean; booking?: { code: string }; error?: string }>("/api/bookings", { method: "POST", json: params(f) });
        if (r.ok && r.booking) {
          flow.current = null;
          if (user) refreshUser();
          return say(chatText(l, "booked", { code: r.booking.code }));
        }
        say(errorText(l, r.error ?? "SERVER"));
        if (r.error === "SLOT_TAKEN") {
          f.step = "time";
          return askTime(l, f);
        }
        flow.current = null;
        return;
      }
    }
  };

  const send = async (text: string) => {
    const msg = text.trim();
    if (!msg || busy) return;
    setInput("");
    setLines((l) => [...l, { from: "user", text: msg }]);
    setOptions([]);
    const detected = detectLang(msg);
    // names / phone numbers / hotel names don't tell us the customer's language
    const freeText = flow.current && ["name", "phone", "hotel"].includes(flow.current.step);
    if (detected && !freeText) chatLang.current = detected;
    const l = chatLang.current;
    setBusy(true);
    try {
      if (flow.current) return await handleFlow(msg, l, flow.current);
      const intent = detectIntent(msg);
      switch (intent) {
        case "book":
          flow.current = { step: "service" };
          return await askService(l);
        case "price": {
          const list = await loadServices();
          const rows = list.map((s) => `• ${svcName(s, l)} (${s.duration} ${l === "th" ? "นาที" : l === "zh" ? "分钟" : "min"}) ${formatBaht(s.price)}${s.is_package ? PER_PERSON[l] : ""}`);
          return say([chatText(l, "priceHead"), ...rows, chatText(l, "priceFoot")].join("\n"));
        }
        case "hours":
          return say(chatText(l, "hours"));
        case "transfer":
          return say(chatText(l, "transfer"));
        case "herbs":
          return say(chatText(l, "herbs"));
        case "cancel":
          return say(chatText(l, "cancelInfo"));
        case "contact":
          return say(chatText(l, "contact"));
        case "greeting":
          return say(chatText(l, "greeting"));
        default:
          return say(chatText(l, "unknown"));
      }
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className={`chatbot ${open ? "is-open" : ""}`}>
      {open && (
        <section className="chatbot__panel" role="dialog" aria-label={t("chat_title")} data-testid="chat-panel">
          <header className="chatbot__head">
            <img src="/assets/brand/chatbot-avatar.png" alt={t("chat_title")} width={40} height={40} />
            <div>
              <p className="chatbot__title">{t("chat_title")}</p>
              <p className="chatbot__note">{t("chat_rules_note")}</p>
            </div>
            <button type="button" className="icon-btn" onClick={() => setOpen(false)} aria-label={t("close")} data-testid="chat-close">
              <Icon name="close" />
            </button>
          </header>
          <div className="chatbot__msgs" ref={listRef} data-testid="chat-messages" aria-live="polite">
            {lines.map((m, i) => (
              <p key={i} className={`chatbot__msg chatbot__msg--${m.from}`} data-testid={`chat-msg-${i}`} data-from={m.from}>
                {m.text}
              </p>
            ))}
            {busy && <p className="chatbot__typing" aria-label={t("loading")}><i /><i /><i /></p>}
          </div>
          {options.length > 0 && (
            <div className="chatbot__options" data-testid="chat-options">
              {options.map((o, i) => (
                <button key={i} type="button" className="chip" onClick={() => send(o.value)} data-testid={`chat-option-${i}`} data-value={o.value}>
                  {o.label}
                </button>
              ))}
            </div>
          )}
          {lines.length <= 1 && (
            <div className="chatbot__options">
              <button type="button" className="chip" onClick={() => send(t("chat_quick_hours"))} data-testid="chat-quick-hours">{t("chat_quick_hours")}</button>
              <button type="button" className="chip" onClick={() => send(t("chat_quick_price"))} data-testid="chat-quick-price">{t("chat_quick_price")}</button>
              <button type="button" className="chip" onClick={() => send(t("chat_quick_book"))} data-testid="chat-quick-book">{t("chat_quick_book")}</button>
            </div>
          )}
          <form
            className="chatbot__form"
            onSubmit={(e) => {
              e.preventDefault();
              send(input);
            }}
          >
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={t("chat_placeholder")}
              aria-label={t("chat_placeholder")}
              data-testid="chat-input"
              maxLength={200}
            />
            <button type="submit" className="btn btn--green btn--icon" aria-label={t("chat_send")} data-testid="chat-send" disabled={busy}>
              <Icon name="send" />
            </button>
          </form>
        </section>
      )}
      <button
        type="button"
        className="chatbot__fab"
        onClick={() => setOpen((o) => !o)}
        aria-expanded={open}
        aria-label={open ? t("close") : t("chat_open")}
        data-testid="chat-toggle"
      >
        {open ? <Icon name="close" size={26} /> : <img src="/assets/brand/chatbot-avatar.png" alt={t("chat_title")} width={60} height={60} />}
      </button>
    </div>
  );
}
