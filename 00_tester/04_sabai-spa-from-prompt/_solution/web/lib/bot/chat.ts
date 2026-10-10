// FR-25 ผู้ช่วยแชทตอบเวลาเปิด/ราคา 3 ภาษา · FR-26 จองผ่านแชทด้วยบริการจองเดียวกับหน้าเว็บ
// กฎ/ตารางตายตัว ไม่สุ่ม ไม่เรียก API ภายนอก (NFR-15) · สถานะการคุยเก็บฝั่งผู้ใช้แล้วส่งกลับมาทุกครั้ง
import { clock } from "../clock.ts";
import { query, toSatang } from "../db.ts";
import { formatDate, pickName, SHOP_PHONE, type Lang } from "../i18n.ts";
import { formatBaht } from "../money.ts";
import { bookableRange, isBookableDate } from "../rules/dates.ts";
import { isDateString } from "../rules/time.ts";
import type { Session } from "../session.ts";
import { availableSlots, buildQuote, createBooking, parseBookingInput } from "../server/booking.ts";
import { getPool } from "../db.ts";
import { ApiError, errorBody } from "../server/http.ts";

export interface ChatState {
  step: "idle" | "service" | "date" | "time" | "contact" | "confirm";
  serviceCode?: string;
  date?: string;
  time?: string;
  name?: string;
  phone?: string;
  total?: number;
}

type Tx = Record<Lang, string>;

export function detectLang(text: string, fallback: Lang): Lang {
  if (/[฀-๿]/.test(text)) return "th";
  if (/[㐀-鿿]/.test(text)) return "zh";
  if (/[A-Za-z]{2,}/.test(text)) return "en";
  return fallback;
}

const has = (text: string, words: string[]) => words.some((w) => text.includes(w));

const W = {
  hours: ["เปิด", "ปิด", "กี่โมง", "เวลาทำการ", "open", "close", "hour", "what time", "营业", "几点", "开门", "关门", "时间"],
  price: ["ราคา", "เท่าไร", "เท่าไหร่", "กี่บาท", "price", "cost", "how much", "价格", "多少钱", "价钱", "费用"],
  book: ["จอง", "book", "reserve", "appointment", "预约", "预订", "订"],
  cancel: ["ยกเลิก", "cancel", "stop", "取消"],
  yes: ["ยืนยัน", "ใช่", "ตกลง", "yes", "ok", "confirm", "确认", "是", "好"],
};

/** คำค้นบริการ → รหัส (ตรวจคำที่เจาะจงก่อน) */
const SERVICE_WORDS: [string, string[]][] = [
  ["P01", ["bangkok relax", "แพ็กเกจ", "แพคเกจ", "package", "套餐", "p01"]],
  ["K01", ["คอร์ส", "course", "疗程", "塑形", "k01"]],
  ["S03", ["ประคบ", "compress", "热敷", "s03"]],
  ["S04", ["อโรมา", "น้ำมัน", "aroma", "oil", "香薰", "精油", "s04"]],
  ["S05", ["เท้า", "foot", "足", "s05"]],
  ["S06", ["ขัดผิว", "scrub", "磨砂", "s06"]],
  ["S07", ["หน้า", "facial", "face", "面部", "s07"]],
  ["S02", ["90", "s02"]],
  ["S01", ["นวดไทย", "thai massage", "thai", "泰式", "按摩", "massage", "นวด", "s01"]],
];

export function detectService(text: string): string | null {
  const s = text.toLowerCase();
  for (const [code, words] of SERVICE_WORDS) if (words.some((w) => s.includes(w))) return code;
  return null;
}

const R = {
  hours: {
    th: "สบายใจ สปา เปิดทุกวัน 10:00–22:00 น. ค่ะ (บริการต้องจบไม่เกิน 22:00) โทร " + SHOP_PHONE,
    en: "Sabai Jai Spa is open every day 10:00–22:00 (sessions must end by 22:00). Call " + SHOP_PHONE,
    zh: "舒心水疗每天营业 10:00–22:00（服务须在 22:00 前结束）。电话 " + SHOP_PHONE,
  },
  help: {
    th: "สอบถามได้เลยค่ะ เช่น \"ร้านเปิดกี่โมง\" \"นวดไทยราคาเท่าไหร่\" หรือพิมพ์ \"จอง\" เพื่อจองคิว",
    en: "Ask me e.g. \"What time do you open?\", \"How much is Thai massage?\" or type \"book\" to make a booking.",
    zh: "可以问我：\"几点营业？\"、\"泰式按摩多少钱？\"，或输入\"预约\"开始预约。",
  },
  askService: {
    th: "ต้องการบริการอะไรคะ? พิมพ์ชื่อหรือรหัส เช่น นวดไทย 60 (S01), นวดเท้า (S05)",
    en: "Which service would you like? Type a name or code, e.g. Thai Massage 60 (S01), Foot Massage (S05).",
    zh: "您想要哪项服务？请输入名称或代码，例如 泰式按摩 60分钟 (S01)、足部按摩 (S05)。",
  },
  webOnly: {
    th: "แพ็กเกจและคอร์สจองได้ที่หน้า \"จองคิว\" บนเว็บค่ะ แชทจองได้เฉพาะบริการเดี่ยว",
    en: "Packages and courses can be booked on the Book page. Chat booking is for single services.",
    zh: "套餐和疗程请在网站\"预约\"页面预订，聊天仅可预约单项服务。",
  },
  askDate: {
    th: "จองวันไหนคะ? พิมพ์วันที่แบบ YYYY-MM-DD (จองได้ {min} ถึง {max})",
    en: "Which date? Type it as YYYY-MM-DD (available {min} to {max}).",
    zh: "预约哪一天？请按 YYYY-MM-DD 格式输入（可预约 {min} 至 {max}）。",
  },
  slots: {
    th: "{date} รอบที่ว่าง: {times} · พิมพ์เวลาที่ต้องการ เช่น {first}",
    en: "Free times on {date}: {times} · Type the time you want, e.g. {first}",
    zh: "{date} 可选时段：{times} · 请输入时间，例如 {first}",
  },
  noSlots: {
    th: "{date} ไม่มีรอบว่างแล้วค่ะ กรุณาเลือกวันอื่น",
    en: "There are no free times on {date}. Please choose another date.",
    zh: "{date} 已无空闲时段，请选择其他日期。",
  },
  taken: {
    th: "เวลานี้ถูกจองแล้ว รอบที่ยังว่าง: {times}",
    en: "This time is already booked. Still free: {times}",
    zh: "该时段已被预订。仍可选：{times}",
  },
  askContact: {
    th: "กรุณาพิมพ์ชื่อและเบอร์โทร เช่น สมชาย 0812345678",
    en: "Please type your name and phone, e.g. John 0812345678",
    zh: "请输入姓名和电话，例如 李伟 0812345678",
  },
  confirm: {
    th: "สรุป: {service} {date} {time} ยอด {total} · พิมพ์ \"ยืนยัน\" เพื่อจอง หรือ \"ยกเลิก\"",
    en: "Summary: {service} {date} {time}, total {total} · Type \"confirm\" to book or \"cancel\".",
    zh: "汇总：{service} {date} {time}，金额 {total} · 输入\"确认\"预约，或\"取消\"。",
  },
  done: {
    th: "จองสำเร็จ! รหัสการจอง {code} · {service} {date} {time} นักบำบัด {therapist}",
    en: "Booking confirmed! Code {code} · {service} {date} {time} with {therapist}",
    zh: "预约成功！预约号 {code} · {service} {date} {time} 理疗师 {therapist}",
  },
  cancelled: {
    th: "ยกเลิกการจองผ่านแชทแล้วค่ะ",
    en: "Chat booking cancelled.",
    zh: "已取消聊天预约。",
  },
  notConfirmed: {
    th: "พิมพ์ \"ยืนยัน\" เพื่อจอง หรือ \"ยกเลิก\" เพื่อเริ่มใหม่",
    en: "Type \"confirm\" to book or \"cancel\" to start over.",
    zh: "输入\"确认\"预约，或\"取消\"重新开始。",
  },
} satisfies Record<string, Tx>;

function fill(s: string, vars: Record<string, string | number>): string {
  for (const [k, v] of Object.entries(vars)) s = s.split(`{${k}}`).join(String(v));
  return s;
}

async function priceReply(code: string | null, lang: Lang): Promise<string> {
  const r = await query("SELECT * FROM service ORDER BY id", [], getPool());
  const row = (s: Record<string, unknown>) => {
    const name = pickName(s, lang);
    const price = formatBaht(toSatang(s.price as string));
    if (s.kind === "package") {
      return { th: `${name} ${price} ต่อคน (นวดไทย + ประคบสมุนไพร + รถรับส่งโรงแรม)`, en: `${name} ${price} per person (Thai massage + herbal compress + hotel shuttle)`, zh: `${name} 每人 ${price}（泰式按摩 + 草药热敷 + 酒店接送）` }[lang];
    }
    if (s.kind === "course") {
      return { th: `${name} ${price} (11 ครั้ง ใช้ได้ 180 วัน)`, en: `${name} ${price} (11 sessions, valid 180 days)`, zh: `${name} ${price}（11次，有效期180天）` }[lang];
    }
    return { th: `${name} ${s.duration_min} นาที ${price} ต่อคน`, en: `${name} ${s.duration_min} min ${price} per person`, zh: `${name} ${s.duration_min}分钟 每人 ${price}` }[lang];
  };
  if (code) {
    const s = r.rows.find((x) => x.code === code);
    if (s) return row(s);
  }
  return r.rows.map(row).join(" · ");
}

/** "2026-10-11" หรือ "11/10" หรือ "11/10/2026" → YYYY-MM-DD */
function parseDate(text: string, today: string): string | null {
  const iso = text.match(/(\d{4})-(\d{1,2})-(\d{1,2})/);
  if (iso) {
    const d = `${iso[1]}-${iso[2].padStart(2, "0")}-${iso[3].padStart(2, "0")}`;
    return isDateString(d) ? d : null;
  }
  const dm = text.match(/(\d{1,2})\/(\d{1,2})(?:\/(\d{4}))?/);
  if (dm) {
    let y = dm[3] ? Number(dm[3]) : Number(today.slice(0, 4));
    const d = `${y}-${dm[2].padStart(2, "0")}-${dm[1].padStart(2, "0")}`;
    if (!dm[3] && isDateString(d) && d < today) y += 1;
    const out = `${y}-${dm[2].padStart(2, "0")}-${dm[1].padStart(2, "0")}`;
    return isDateString(out) ? out : null;
  }
  return null;
}

function parseTime(text: string): string | null {
  const m = text.match(/(\d{1,2})[:.](\d{2})/);
  if (!m) return null;
  return `${m[1].padStart(2, "0")}:${m[2]}`;
}

export interface ChatReply {
  reply: string;
  lang: Lang;
  state: ChatState;
  booking?: { bookingId: number; code: string; total: number };
}

export async function chat(message: string, prev: ChatState | null, session: Session | null, fallbackLang: Lang): Promise<ChatReply> {
  const text = message.trim();
  const lower = text.toLowerCase();
  const lang = detectLang(text, fallbackLang);
  const state: ChatState = prev && prev.step ? { ...prev } : { step: "idle" };
  const { today } = await clock();
  const range = bookableRange(today);
  const out = (reply: string, s: ChatState, extra?: Partial<ChatReply>): ChatReply => ({ reply, lang, state: s, ...extra });

  if (state.step !== "idle" && has(lower, W.cancel)) return out(R.cancelled[lang], { step: "idle" });

  const freeTimes = async (serviceCode: string, date: string) => {
    const r = await availableSlots({ serviceCode, date, type: "single", people: 1 }, lang);
    return r.slots.filter((s) => s.available).map((s) => s.time);
  };
  const askDate = (s: ChatState) => out(fill(R.askDate[lang], { min: range.min, max: range.max }), { ...s, step: "date" });

  // ── อยู่ระหว่างจอง: ตีความข้อความเป็นคำตอบของขั้นนั้น ──
  if (state.step === "service") {
    const code = detectService(lower);
    if (!code) return out(R.askService[lang], state);
    if (code === "P01" || code === "K01") return out(R.webOnly[lang], { step: "idle" });
    return askDate({ ...state, serviceCode: code });
  }
  if (state.step === "date") {
    const d = parseDate(text, today);
    if (!d || !isBookableDate(today, d)) {
      return out(errorBody(lang, "DATE_OUT_OF_RANGE").message + " · " + fill(R.askDate[lang], { min: range.min, max: range.max }), state);
    }
    const times = await freeTimes(state.serviceCode!, d);
    if (!times.length) return out(fill(R.noSlots[lang], { date: formatDate(d, lang) }), state);
    return out(fill(R.slots[lang], { date: formatDate(d, lang), times: times.join(", "), first: times[0] }), { ...state, date: d, step: "time" });
  }
  if (state.step === "time") {
    const tm = parseTime(text);
    const times = await freeTimes(state.serviceCode!, state.date!);
    if (!tm || !times.includes(tm)) {
      return out(fill(R.taken[lang], { times: times.join(", ") || "-" }), state);
    }
    const next: ChatState = { ...state, time: tm };
    if (!session) return out(R.askContact[lang], { ...next, step: "contact" });
    return confirmStep(next);
  }
  if (state.step === "contact") {
    const phone = text.match(/\+?\d[\d\s-]{7,}\d/)?.[0]?.replace(/\s/g, "");
    const name = text.replace(/\+?\d[\d\s-]{7,}\d/, "").replace(/[,，]/g, " ").trim();
    if (!phone || !name) return out(R.askContact[lang], state);
    return confirmStep({ ...state, name, phone });
  }
  if (state.step === "confirm") {
    if (!has(lower, W.yes)) return out(R.notConfirmed[lang], state);
    try {
      const res = await createBooking(
        parseBookingInput({
          type: "single",
          serviceCode: state.serviceCode,
          people: 1,
          date: state.date,
          time: state.time,
          contactName: state.name ?? "",
          contactPhone: state.phone ?? "",
          quotedTotal: state.total,
        }),
        session,
        lang,
      );
      return out(
        fill(R.done[lang], { code: res.code, service: res.quote.service.name, date: formatDate(state.date!, lang), time: state.time!, therapist: res.therapistNames.join(", ") }),
        { step: "idle" },
        { booking: { bookingId: res.bookingId, code: res.code, total: res.total } },
      );
    } catch (e) {
      if (e instanceof ApiError || (e as { code?: string })?.code === "23P01") {
        const code = e instanceof ApiError ? e.code : "SLOT_TAKEN";
        if (code === "SLOT_TAKEN") {
          const times = await freeTimes(state.serviceCode!, state.date!);
          return out(fill(R.taken[lang], { times: times.join(", ") || "-" }), { ...state, step: "time", time: undefined });
        }
        return out(errorBody(lang, code).message, { step: "idle" });
      }
      throw e;
    }
  }

  // ── คำถามทั่วไป ──
  if (has(lower, W.book)) {
    const code = detectService(lower);
    if (code === "P01" || code === "K01") return out(R.webOnly[lang], { step: "idle" });
    if (code) return askDate({ step: "date", serviceCode: code });
    return out(R.askService[lang], { step: "service" });
  }
  if (has(lower, W.price)) return out(await priceReply(detectService(lower), lang), { step: "idle" });
  if (has(lower, W.hours)) return out(R.hours[lang], { step: "idle" });
  return out(R.help[lang], { step: "idle" });

  async function confirmStep(s: ChatState): Promise<ChatReply> {
    try {
      const q = await buildQuote(
        getPool(),
        parseBookingInput({ type: "single", serviceCode: s.serviceCode, people: 1, date: s.date, time: s.time }),
        session,
        today,
        lang,
      );
      const total = q.price.total / 100;
      return out(fill(R.confirm[lang], { service: q.serviceName, date: formatDate(s.date!, lang), time: s.time!, total: formatBaht(q.price.total) }), {
        ...s,
        total,
        step: "confirm",
      });
    } catch (e) {
      if (e instanceof ApiError) return out(errorBody(lang, e.code).message, { step: "idle" });
      throw e;
    }
  }
}
