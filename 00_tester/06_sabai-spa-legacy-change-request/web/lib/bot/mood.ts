// FR-27 อารมณ์วันนี้ 4 แบบ → บริการแนะนำ 1–3 รายการ · ตารางตายตัว ไม่สุ่ม (NFR-15)
import type { Lang } from "../i18n.ts";

export const MOODS = ["stressed", "tired", "aches", "insomnia"] as const;
export type Mood = (typeof MOODS)[number];

type Tx = Record<Lang, string>;

export const MOOD_TABLE: Record<Mood, { services: string[]; reason: Tx }> = {
  stressed: {
    services: ["S04", "S01"],
    reason: {
      th: "กลิ่นมะลิและตะไคร้หอมช่วยให้ใจสงบ นวดไทยช่วยคลายความตึงจากความเครียด",
      en: "Jasmine and citronella aromas calm the mind; Thai massage releases stress tension.",
      zh: "茉莉与亚香茅香气让心情平静，泰式按摩舒缓压力带来的紧绷。",
    },
  },
  tired: {
    services: ["S01", "S03"],
    reason: {
      th: "นวดไทยฟื้นพลัง ประคบสมุนไพรอุ่น ๆ ช่วยให้ร่างกายสดชื่น",
      en: "Thai massage restores energy and a warm herbal compress refreshes the body.",
      zh: "泰式按摩恢复活力，温热草药敷让身体焕然一新。",
    },
  },
  aches: {
    services: ["S02", "S03", "S05"],
    reason: {
      th: "นวดไทย 90 นาทีลงลึกจุดปวด ประคบไพลลดอาการเมื่อย นวดเท้าคลายขาที่ล้า",
      en: "A 90-minute Thai massage works deep into sore spots, plai compress eases aches and foot massage relaxes tired legs.",
      zh: "90分钟泰式按摩深入酸痛部位，泰国姜热敷缓解酸痛，足部按摩放松疲惫双腿。",
    },
  },
  insomnia: {
    services: ["S04", "S05"],
    reason: {
      th: "อโรมาช่วยให้หลับลึก นวดเท้าช่วยให้ร่างกายพร้อมพักผ่อน",
      en: "Aromatherapy helps deeper sleep and a foot massage prepares the body for rest.",
      zh: "香薰有助深度睡眠，足部按摩让身体准备好休息。",
    },
  },
};

export function isMood(v: unknown): v is Mood {
  return typeof v === "string" && (MOODS as readonly string[]).includes(v);
}

export function recommendForMood(mood: Mood, lang: Lang) {
  const row = MOOD_TABLE[mood];
  return { mood, services: row.services, reason: row.reason[lang] };
}
