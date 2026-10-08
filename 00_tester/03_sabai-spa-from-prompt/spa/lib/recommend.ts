// Fixed-rule "AI" helpers (NFR-12). Same input → same output, no randomness, no external API.

export const MOODS = ["relax", "stressed", "tired", "sore"] as const;
export type Mood = (typeof MOODS)[number];

export const MOOD_IMAGES: Record<Mood, string> = {
  relax: "/assets/moods/mood-relax.png",
  stressed: "/assets/moods/mood-stressed.png",
  tired: "/assets/moods/mood-tired.png",
  sore: "/assets/treatments/thai-massage.jpg",
};

/** FR-25 / BR-23: every mood → 1–3 services (order = priority) */
export const MOOD_RULES: Record<Mood, string[]> = {
  relax: ["aroma-oil", "foot-reflexology"],
  stressed: ["aroma-oil", "herbal-compress", "coconut-rice-scrub"],
  tired: ["foot-reflexology", "thai-massage", "bangkok-relax"],
  sore: ["thai-massage", "herbal-compress"],
};

export function recommendForMood(mood: Mood): string[] {
  return MOOD_RULES[mood].slice(0, 3);
}

// ---------------- Quiz (FR-26 / BR-24) ----------------
export const QUIZ = [
  { id: "goal", options: ["relax", "pain", "skin", "shape"] },
  { id: "time", options: ["60", "90", "120"] },
  { id: "pressure", options: ["soft", "medium", "strong"] },
  { id: "transfer", options: ["yes", "no"] },
] as const;

export type QuizAnswers = { goal?: string; time?: string; pressure?: string; transfer?: string };
export type QuizResult = { service: string; reason: string };

/**
 * Rule table (first match wins):
 * 1. transfer = yes                       → bangkok-relax   (reason: transfer)
 * 2. goal = skin  & pressure = soft       → aloe-hydrating-facial (skinSoft)
 * 3. goal = skin                          → turmeric-facial (skinBright)
 * 4. goal = shape                         → body-contouring (shape)
 * 5. goal = pain  & pressure = strong     → thai-massage    (painStrong)
 * 6. goal = pain                          → herbal-compress (painHerbal)
 * 7. goal = relax & time = 60             → foot-reflexology (relaxShort)
 * 8. goal = relax (90 / 120)              → aroma-oil       (relaxLong)
 */
export function quizResult(a: QuizAnswers): QuizResult | null {
  if (!a.goal || !a.time || !a.pressure || !a.transfer) return null; // BR-24: needs all 4
  if (a.transfer === "yes") return { service: "bangkok-relax", reason: "transfer" };
  if (a.goal === "skin") return a.pressure === "soft" ? { service: "aloe-hydrating-facial", reason: "skinSoft" } : { service: "turmeric-facial", reason: "skinBright" };
  if (a.goal === "shape") return { service: "body-contouring", reason: "shape" };
  if (a.goal === "pain") return a.pressure === "strong" ? { service: "thai-massage", reason: "painStrong" } : { service: "herbal-compress", reason: "painHerbal" };
  if (a.time === "60") return { service: "foot-reflexology", reason: "relaxShort" };
  return { service: "aroma-oil", reason: "relaxLong" };
}

// ---------------- Skin check (FR-29) ----------------
export type SkinType = "sensitive" | "dull" | "dry" | "balanced";

/** brightness = 0.299R + 0.587G + 0.114B, redness = R − G (average colour of the image) */
export function skinMetrics(r: number, g: number, b: number) {
  const brightness = Math.round(0.299 * r + 0.587 * g + 0.114 * b);
  const redness = Math.round(r - g);
  return { brightness, redness };
}

/**
 * Rule table (first match wins):
 * 1. redness ≥ 45            → sensitive → aloe-hydrating-facial
 * 2. brightness < 120        → dull      → turmeric-facial, coconut-rice-scrub
 * 3. brightness ≥ 170        → dry       → aloe-hydrating-facial, turmeric-facial
 * 4. otherwise (120–169)     → balanced  → turmeric-facial, aroma-oil
 */
export const SKIN_RULES: Record<SkinType, string[]> = {
  sensitive: ["aloe-hydrating-facial"],
  dull: ["turmeric-facial", "coconut-rice-scrub"],
  dry: ["aloe-hydrating-facial", "turmeric-facial"],
  balanced: ["turmeric-facial", "aroma-oil"],
};

export function classifySkin(r: number, g: number, b: number): { type: SkinType; brightness: number; redness: number; services: string[] } {
  const { brightness, redness } = skinMetrics(r, g, b);
  let type: SkinType;
  if (redness >= 45) type = "sensitive";
  else if (brightness < 120) type = "dull";
  else if (brightness >= 170) type = "dry";
  else type = "balanced";
  return { type, brightness, redness, services: SKIN_RULES[type] };
}

/** FR-30: before/after simulation = CSS filter on the same image */
export const SIM_FILTERS: Record<string, string> = {
  "turmeric-facial": "brightness(1.10) saturate(1.06) contrast(1.03)",
  "aloe-hydrating-facial": "brightness(1.06) saturate(0.90) contrast(0.97) blur(0.4px)",
  "coconut-rice-scrub": "brightness(1.12) contrast(1.05) saturate(1.02)",
};
