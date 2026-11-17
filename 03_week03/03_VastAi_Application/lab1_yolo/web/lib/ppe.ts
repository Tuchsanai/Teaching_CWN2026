// คลาสของโมเดล PPE: ชื่อภาษาไทย สี และการสรุปผลตรวจ

export type Detection = { class: string; confidence: number; box: [number, number, number, number] };

export type DetectResult = {
  model: string;
  width: number;
  height: number;
  inference_ms: number;
  detections: Detection[];
};

export type Summary = {
  persons: number;
  hardhat: number;
  no_hardhat: number;
  no_vest: number;
  passed: boolean;
};

export const CLASS_STYLE: Record<string, { th: string; color: string }> = {
  Hardhat: { th: "สวมหมวกนิรภัย", color: "#16a34a" },
  "NO-Hardhat": { th: "ไม่สวมหมวกนิรภัย", color: "#dc2626" },
  "Safety Vest": { th: "สวมเสื้อสะท้อนแสง", color: "#0d9488" },
  "NO-Safety Vest": { th: "ไม่สวมเสื้อสะท้อนแสง", color: "#ea580c" },
  Mask: { th: "สวมหน้ากาก", color: "#0891b2" },
  "NO-Mask": { th: "ไม่สวมหน้ากาก", color: "#d97706" },
  Person: { th: "คน", color: "#2563eb" },
  "Safety Cone": { th: "กรวยจราจร", color: "#a855f7" },
  machinery: { th: "เครื่องจักร", color: "#64748b" },
  vehicle: { th: "ยานพาหนะ", color: "#475569" },
};

export const styleOf = (cls: string) => CLASS_STYLE[cls] ?? { th: cls, color: "#6b7280" };

export function summarize(dets: Detection[]): Summary {
  const n = (c: string) => dets.filter((d) => d.class === c).length;
  const no_hardhat = n("NO-Hardhat");
  return { persons: n("Person"), hardhat: n("Hardhat"), no_hardhat, no_vest: n("NO-Safety Vest"), passed: no_hardhat === 0 };
}

export const SAMPLES = [
  { file: "sample-1.jpg", title: "งานสายไฟฟ้า" },
  { file: "sample-2.jpg", title: "ห้องปั๊ม" },
  { file: "sample-3.jpg", title: "งานบนบันได" },
  { file: "sample-4.jpg", title: "ทีมตรวจหน้างาน" },
  { file: "sample-5.jpg", title: "งานนั่งร้าน" },
  { file: "sample-6.jpg", title: "งานติดตั้งผนัง" },
];
