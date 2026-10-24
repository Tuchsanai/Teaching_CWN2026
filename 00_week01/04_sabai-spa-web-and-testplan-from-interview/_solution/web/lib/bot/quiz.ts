// FR-28 แบบทดสอบ 4 ข้อพอดี → แพ็กเกจแนะนำ 1 รายการ + เหตุผล · กฎตายตัว (NFR-15)
import type { Lang } from "../i18n.ts";

type Tx = Record<Lang, string>;

export interface QuizQuestion {
  id: string;
  text: Tx;
  options: { value: string; label: Tx }[];
}

export const QUIZ: QuizQuestion[] = [
  {
    id: "goal",
    text: { th: "เป้าหมายหลักของคุณวันนี้คืออะไร?", en: "What is your main goal today?", zh: "你今天的主要目标是什么？" },
    options: [
      { value: "relax", label: { th: "ผ่อนคลายความเครียด", en: "Relieve stress", zh: "缓解压力" } },
      { value: "pain", label: { th: "คลายปวดเมื่อย", en: "Ease aches", zh: "缓解酸痛" } },
      { value: "beauty", label: { th: "ผิวสวยสดใส", en: "Glowing skin", zh: "肌肤亮丽" } },
      { value: "shape", label: { th: "กระชับสัดส่วน", en: "Body contouring", zh: "塑形紧致" } },
    ],
  },
  {
    id: "time",
    text: { th: "คุณมีเวลาประมาณเท่าไร?", en: "How much time do you have?", zh: "你大约有多少时间？" },
    options: [
      { value: "60", label: { th: "ประมาณ 1 ชั่วโมง", en: "About 1 hour", zh: "约1小时" } },
      { value: "90", label: { th: "ประมาณ 1 ชั่วโมงครึ่ง", en: "About 1.5 hours", zh: "约1.5小时" } },
      { value: "120", label: { th: "2 ชั่วโมงขึ้นไป", en: "2 hours or more", zh: "2小时以上" } },
    ],
  },
  {
    id: "pressure",
    text: { th: "ชอบแรงนวดแบบไหน?", en: "What massage pressure do you like?", zh: "你喜欢什么力度？" },
    options: [
      { value: "soft", label: { th: "เบา ๆ", en: "Gentle", zh: "轻柔" } },
      { value: "medium", label: { th: "กลาง ๆ", en: "Medium", zh: "适中" } },
      { value: "strong", label: { th: "หนักมือ", en: "Firm", zh: "有力" } },
    ],
  },
  {
    id: "stay",
    text: { th: "ตอนนี้คุณพักอยู่ที่ไหน?", en: "Where are you staying?", zh: "你现在住在哪里？" },
    options: [
      { value: "home", label: { th: "บ้าน / ที่ทำงานในกรุงเทพฯ", en: "Home / office in Bangkok", zh: "曼谷的家或公司" } },
      { value: "hotel", label: { th: "โรงแรม (มาเที่ยว)", en: "A hotel (visiting)", zh: "酒店（旅游）" } },
    ],
  },
];

const RESULTS: Record<string, { code: string; reason: Tx }> = {
  K01: {
    code: "K01",
    reason: {
      th: "คุณอยากกระชับสัดส่วน คอร์ส 10 แถม 1 ใช้ได้ 180 วัน พร้อมกราฟรอบเอวติดตามผล",
      en: "You want body contouring: the 10+1 course lasts 180 days with a waist chart to track progress.",
      zh: "你想塑形：买10送1疗程有效期180天，并有腰围图追踪效果。",
    },
  },
  S07: {
    code: "S07",
    reason: {
      th: "คุณอยากได้ผิวสวย ทรีตเมนต์หน้าสมุนไพรว่านหางจระเข้ ขมิ้น ทานาคา เหมาะที่สุด",
      en: "You want glowing skin: the herbal facial with aloe vera, turmeric and thanaka suits you best.",
      zh: "你想要亮丽肌肤：芦荟、姜黄、黄香楝草药面部护理最适合你。",
    },
  },
  P01: {
    code: "P01",
    reason: {
      th: "คุณมีเวลาหรือพักโรงแรม แพ็กเกจ Bangkok Relax ได้ทั้งนวดไทย ประคบสมุนไพร และรถรับส่งโรงแรม",
      en: "You have time or stay at a hotel: Bangkok Relax includes Thai massage, herbal compress and hotel shuttle.",
      zh: "你时间充裕或住酒店：曼谷放松套餐包含泰式按摩、草药热敷和酒店接送。",
    },
  },
  S02: {
    code: "S02",
    reason: {
      th: "คุณปวดเมื่อยและชอบแรงนวด นวดไทย 90 นาทีลงลึกได้เต็มที่",
      en: "You have aches and like firm pressure: a 90-minute Thai massage goes deep.",
      zh: "你有酸痛并喜欢有力按摩：90分钟泰式按摩可深入放松。",
    },
  },
  S03: {
    code: "S03",
    reason: {
      th: "คุณปวดเมื่อยแต่ชอบแรงเบา ประคบสมุนไพรอุ่น ๆ ช่วยคลายโดยไม่ต้องลงน้ำหนัก",
      en: "You have aches but prefer gentle pressure: a warm herbal compress relieves without force.",
      zh: "你有酸痛但喜欢轻柔：温热草药敷无需用力即可舒缓。",
    },
  },
  S04: {
    code: "S04",
    reason: {
      th: "คุณอยากผ่อนคลาย นวดน้ำมันอโรมากลิ่นมะลิช่วยให้ใจสงบ",
      en: "You want to relax: an aroma oil massage with jasmine calms the mind.",
      zh: "你想放松：茉莉香薰精油按摩让心情平静。",
    },
  },
};

export type QuizAnswers = Record<string, string>;

export function validateAnswers(a: unknown): a is QuizAnswers {
  if (!a || typeof a !== "object") return false;
  return QUIZ.every((q) => q.options.some((o) => o.value === (a as Record<string, unknown>)[q.id]));
}

/** กฎตายตัวตามลำดับ */
export function quizResult(a: QuizAnswers, lang: Lang): { code: string; reason: string } {
  let key: string;
  if (a.goal === "shape") key = "K01";
  else if (a.goal === "beauty") key = "S07";
  else if (a.stay === "hotel" || a.time === "120") key = "P01";
  else if (a.goal === "pain") key = a.pressure === "soft" ? "S03" : "S02";
  else key = "S04";
  return { code: RESULTS[key].code, reason: RESULTS[key].reason[lang] };
}
