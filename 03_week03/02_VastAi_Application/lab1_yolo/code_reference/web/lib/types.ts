export type Detection = { class: string; confidence: number; box: [number, number, number, number] };
export type DetectResult = {
  model: string; width: number; height: number; inference_ms: number; detections: Detection[];
};
export type Summary = { persons: number; hardhat: number; noHardhat: number; noVest: number; passed: boolean };

export function summarize(dets: Detection[]): Summary {
  const n = (c: string) => dets.filter((d) => d.class === c).length;
  const noHardhat = n("NO-Hardhat");
  return { persons: n("Person"), hardhat: n("Hardhat"), noHardhat, noVest: n("NO-Safety Vest"), passed: noHardhat === 0 };
}

export const CLASS_TH: Record<string, string> = {
  Hardhat: "สวมหมวก", "NO-Hardhat": "ไม่สวมหมวก", "Safety Vest": "เสื้อสะท้อนแสง", "NO-Safety Vest": "ไม่สวมเสื้อสะท้อนแสง",
  Person: "คน", Mask: "หน้ากาก", "NO-Mask": "ไม่สวมหน้ากาก", "Safety Cone": "กรวยจราจร", machinery: "เครื่องจักร", vehicle: "ยานพาหนะ",
};
export const CLASS_COLOR: Record<string, string> = {
  Hardhat: "#16a34a", "NO-Hardhat": "#dc2626", "Safety Vest": "#0d9488", "NO-Safety Vest": "#ea580c",
  Person: "#2563eb", Mask: "#7c3aed", "NO-Mask": "#db2777", "Safety Cone": "#ca8a04", machinery: "#475569", vehicle: "#64748b",
};
