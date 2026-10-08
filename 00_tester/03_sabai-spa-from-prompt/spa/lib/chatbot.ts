// FR-27 / FR-28: rule-based chatbot (NFR-12). Keyword tables per language, fixed replies, no randomness.
import type { Lang } from "./i18n";

export type Intent = "book" | "price" | "hours" | "transfer" | "herbs" | "cancel" | "contact" | "greeting" | "unknown";

/** reply in the language the customer typed in */
export function detectLang(text: string): Lang | null {
  if (/[一-鿿]/.test(text)) return "zh";
  if (/[฀-๿]/.test(text)) return "th";
  if (/[a-z]/i.test(text)) return "en";
  return null;
}

/** first matching row wins */
export const KEYWORDS: [Intent, string[]][] = [
  ["book", ["预约", "预订", "订位", "จอง", "book", "reserve", "appointment"]],
  ["cancel", ["取消", "ยกเลิก", "cancel"]],
  ["price", ["多少钱", "价格", "价钱", "费用", "收费", "价目", "ราคา", "เท่าไร", "เท่าไหร่", "กี่บาท", "ค่าบริการ", "price", "cost", "how much", "rate", "fee"]],
  ["hours", ["营业时间", "几点", "开门", "关门", "营业", "เวลาเปิด", "เปิดกี่โมง", "ปิดกี่โมง", "เวลาทำการ", "เปิดวันไหน", "เปิดไหม", "เปิด", "ปิด", "hour", "open", "close", "opening", "what time"]],
  ["transfer", ["接送", "酒店", "รถรับส่ง", "รับส่ง", "โรงแรม", "transfer", "pickup", "pick up", "pick-up", "hotel", "shuttle"]],
  ["herbs", ["过敏", "草药", "แพ้", "สมุนไพร", "allerg", "herb"]],
  ["contact", ["地址", "在哪", "电话", "ที่อยู่", "อยู่ที่ไหน", "เบอร์", "โทร", "address", "where", "location", "phone", "call"]],
  ["greeting", ["你好", "您好", "สวัสดี", "hello", "hi", "hey"]],
];

export function detectIntent(text: string): Intent {
  const s = text.toLowerCase();
  for (const [intent, words] of KEYWORDS) {
    for (const w of words) {
      if (/^[a-z ]+$/.test(w) && w.length <= 3) {
        if (new RegExp(`(^|[^a-z])${w}([^a-z]|$)`).test(s)) return intent;
      } else if (s.includes(w)) return intent;
    }
  }
  return "unknown";
}

const NO_WORDS = ["ไม่ต้อง", "ไม่", "no", "nope", "不需要", "不要", "不用", "不", "取消", "cancel", "ยกเลิก"];
const YES_WORDS = ["ใช่", "ยืนยัน", "ตกลง", "ต้องการ", "เอา", "ok", "okay", "yes", "yep", "y", "sure", "confirm", "是", "确认", "好", "要", "需要", "对"];

export function yesNo(text: string): "yes" | "no" | null {
  const s = text.trim().toLowerCase();
  for (const w of NO_WORDS) if (s === w || s.startsWith(w)) return "no";
  for (const w of YES_WORDS) if (s === w || s.startsWith(w)) return "yes";
  return null;
}

type Msg = Record<Lang, string>;
export const CHAT: Record<string, Msg> = {
  greeting: {
    th: "สวัสดีค่ะ ยินดีต้อนรับสู่สบายใจ สปา ถามเรื่องเวลาเปิด ราคา หรือพิมพ์ \"จอง\" เพื่อจองคิวได้เลยค่ะ",
    en: "Hello! Welcome to Sabai Jai Spa. Ask about opening hours or prices, or type \"book\" to make a booking.",
    zh: "您好！欢迎光临 Sabai Jai 水疗。可以询问营业时间、价格，或输入“预约”开始预约。",
  },
  hours: {
    th: "ร้านเปิดทุกวัน 10:00–22:00 ไม่มีวันหยุด รอบจองทุก 30 นาที และบริการต้องเสร็จไม่เกิน 22:00 ค่ะ",
    en: "We are open every day 10:00–22:00 with no holidays. Bookings start every 30 minutes and must finish by 22:00.",
    zh: "我们每天营业 10:00–22:00，全年无休。每 30 分钟一个预约时段，服务须在 22:00 前结束。",
  },
  priceHead: { th: "ราคาบริการหลัก (ต่อคน):", en: "Main prices (per person):", zh: "主要服务价格（每人）：" },
  priceFoot: {
    th: "กลุ่ม 4 คนขึ้นไปลด 10% ค่ะ",
    en: "Groups of 4 or more get 10% off.",
    zh: "4 人及以上团体享 9 折。",
  },
  transfer: {
    th: "รถรับส่งจากโรงแรม: ไม่เกิน 5 กม. ฟรี · มากกว่า 5–15 กม. ฿300/คัน · เกิน 15 กม. ไม่มีบริการ · รถ 1 คันนั่งได้ 4 คน",
    en: "Hotel transfer: up to 5 km free · over 5–15 km ฿300 per car · over 15 km not available · 4 guests per car.",
    zh: "酒店接送：5 公里内免费 · 5–15 公里每车 ฿300 · 超过 15 公里不提供 · 每车最多 4 人。",
  },
  herbs: {
    th: "ทุกบริการแสดงรายชื่อสมุนไพรไว้ในหน้าบริการ ถ้าแพ้สมุนไพรชนิดใด กรุณาแจ้งร้านก่อนรับบริการ",
    en: "Every treatment lists its herbs on the treatments page. If you are allergic to any herb, please tell the spa before your treatment.",
    zh: "每项护理的草药都列在护理项目页面。如对任何草药过敏，请在护理前告知本店。",
  },
  cancelInfo: {
    th: "ยกเลิกเองได้ที่หน้าบัญชีสมาชิก เมื่อเหลือเวลาอย่างน้อย 24 ชั่วโมงก่อนนัด ถ้าน้อยกว่านั้นกรุณาโทร 02-123-4567",
    en: "You can cancel on your account page if the appointment is at least 24 hours away. Otherwise please call 02-123-4567.",
    zh: "距离预约 24 小时以上可在会员中心自行取消，否则请致电 02-123-4567。",
  },
  contact: {
    th: "ร้านอยู่ที่ 123 ถนนสุขุมวิท กรุงเทพฯ โทร 02-123-4567",
    en: "We are at 123 Sukhumvit Road, Bangkok. Phone 02-123-4567.",
    zh: "地址：曼谷素坤逸路 123 号，电话 02-123-4567。",
  },
  unknown: {
    th: "ขออภัยค่ะ ยังไม่เข้าใจคำถาม ลองพิมพ์ \"เวลาเปิด\" \"ราคา\" หรือ \"จอง\" หรือโทร 02-123-4567",
    en: "Sorry, I didn't catch that. Try \"opening hours\", \"price\" or \"book\", or call 02-123-4567.",
    zh: "抱歉，我没有理解。可以试试“营业时间”、“多少钱”或“预约”，或致电 02-123-4567。",
  },
  askService: { th: "ต้องการจองบริการไหนคะ? (พิมพ์หมายเลขหรือกดเลือก)", en: "Which treatment would you like? (type a number or tap one)", zh: "您想预约哪项服务？（输入编号或点选）" },
  badService: { th: "ไม่พบบริการนี้ กรุณาเลือกจากรายการค่ะ", en: "I couldn't find that treatment — please choose from the list.", zh: "未找到该服务，请从列表中选择。" },
  askDate: {
    th: "ต้องการวันไหนคะ? จองได้ {from} ถึง {to} (พิมพ์ YYYY-MM-DD หรือกดเลือก)",
    en: "Which date? You can book {from} to {to} (type YYYY-MM-DD or tap one).",
    zh: "请选择日期：可预约 {from} 至 {to}（输入 YYYY-MM-DD 或点选）。",
  },
  badDate: {
    th: "จองได้ตั้งแต่พรุ่งนี้ถึง 30 วันข้างหน้าเท่านั้น ({from} ถึง {to}) ค่ะ",
    en: "You can book from tomorrow up to 30 days ahead only ({from} to {to}).",
    zh: "仅可预约明天至 30 天内的日期（{from} 至 {to}）。",
  },
  askPeople: { th: "มากี่คนคะ? (1–6 คน)", en: "How many guests? (1–6)", zh: "请问几位？（1–6 人）" },
  badPeople: { th: "กรุณาพิมพ์จำนวนคนเป็นตัวเลข 1–6 ค่ะ", en: "Please type a number from 1 to 6.", zh: "请输入 1–6 的数字。" },
  askTime: { th: "รอบที่ว่าง (กดเลือก หรือพิมพ์ เช่น 14:30):", en: "Open times (tap one or type e.g. 14:30):", zh: "可预约时间（点选或输入如 14:30）：" },
  noTime: { th: "วันนี้รอบเต็มแล้ว กรุณาเลือกวันอื่นค่ะ", en: "That day is fully booked — please pick another date.", zh: "当天已约满，请选择其他日期。" },
  badTime: { th: "รอบเวลานี้ไม่เปิดให้จอง (10:00–22:00 ทุก 30 นาที และต้องเสร็จไม่เกิน 22:00)", en: "That time is not bookable (10:00–22:00 every 30 min, must finish by 22:00).", zh: "该时间不可预约（10:00–22:00 每 30 分钟一场，须在 22:00 前结束）。" },
  askTransfer: { th: "ต้องการรถรับส่งจากโรงแรมไหมคะ?", en: "Do you need a hotel transfer?", zh: "需要酒店接送吗？" },
  askHotel: { th: "พักโรงแรมไหนคะ?", en: "Which hotel are you staying at?", zh: "您住在哪家酒店？" },
  badHotel: { th: "ไม่พบโรงแรมนี้ กรุณาเลือกจากรายการค่ะ", en: "I couldn't find that hotel — please choose from the list.", zh: "未找到该酒店，请从列表中选择。" },
  askName: { th: "ขอชื่อผู้จองด้วยค่ะ", en: "May I have your name?", zh: "请问您的姓名？" },
  askPhone: { th: "ขอเบอร์โทรติดต่อด้วยค่ะ", en: "And your phone number?", zh: "请留下您的电话号码。" },
  badPhone: { th: "กรุณาพิมพ์เบอร์โทรอย่างน้อย 9 หลักค่ะ", en: "Please type a phone number with at least 9 digits.", zh: "请输入至少 9 位数字的电话号码。" },
  summary: {
    th: "สรุปการจอง: {service} · {date} {time} · {people} คน\nค่าบริการ {subtotal}{discounts}\nค่ารถรับส่ง {transport}\nยอดสุทธิ {total}\nยืนยันการจองไหมคะ?",
    en: "Summary: {service} · {date} {time} · {people} guest(s)\nTreatment {subtotal}{discounts}\nHotel transfer {transport}\nNet total {total}\nShall I confirm?",
    zh: "预约摘要：{service} · {date} {time} · {people} 人\n服务费用 {subtotal}{discounts}\n酒店接送 {transport}\n应付总额 {total}\n确认预约吗？",
  },
  discounts: { th: "\nส่วนลด −{amount}", en: "\nDiscounts −{amount}", zh: "\n折扣 −{amount}" },
  noTransfer: { th: "ไม่ใช้", en: "not needed", zh: "不需要" },
  transferLine: { th: "{fee} ({cars} คัน · {km} กม.)", en: "{fee} ({cars} car(s) · {km} km)", zh: "{fee}（{cars} 辆车 · {km} 公里）" },
  booked: {
    th: "จองสำเร็จแล้วค่ะ! รหัสการจอง {code} แล้วพบกันนะคะ",
    en: "Booked! Your booking code is {code}. See you soon.",
    zh: "预约成功！预约编号 {code}，期待您的光临。",
  },
  aborted: { th: "ยกเลิกขั้นตอนการจองแล้วค่ะ", en: "OK, I've stopped the booking.", zh: "好的，已取消本次预约流程。" },
  yesNoHint: { th: "กรุณาตอบ ใช่ หรือ ไม่", en: "Please answer yes or no.", zh: "请回答“是”或“不”。" },
  yes: { th: "ใช่", en: "Yes", zh: "是" },
  no: { th: "ไม่", en: "No", zh: "不" },
  confirm: { th: "ยืนยัน", en: "Confirm", zh: "确认" },
  stop: { th: "ยกเลิก", en: "Cancel", zh: "取消" },
  tomorrow: { th: "พรุ่งนี้", en: "Tomorrow", zh: "明天" },
};

export function chatText(lang: Lang, key: keyof typeof CHAT, vars?: Record<string, string | number>): string {
  let s = CHAT[key][lang];
  if (vars) for (const [k, v] of Object.entries(vars)) s = s.split(`{${k}}`).join(String(v));
  return s;
}

/** "พรุ่งนี้" / "tomorrow" / "明天" and "มะรืน" / "后天" → offset in days */
export function relativeDay(text: string): number | null {
  const s = text.trim().toLowerCase();
  if (["พรุ่งนี้", "tomorrow", "明天"].some((w) => s.includes(w))) return 1;
  if (["มะรืน", "day after tomorrow", "后天"].some((w) => s.includes(w))) return 2;
  return null;
}

export function parseTime(text: string): string | null {
  const m = text.match(/(\d{1,2})[:.](\d{2})/);
  if (!m) return null;
  const h = Number(m[1]);
  const mi = Number(m[2]);
  if (h > 23 || mi > 59) return null;
  return `${String(h).padStart(2, "0")}:${String(mi).padStart(2, "0")}`;
}
