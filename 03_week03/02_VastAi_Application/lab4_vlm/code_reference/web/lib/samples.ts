import data from "./samples.json";
import type { Receipt } from "./receipt";
export type Sample = { id: string; image: string; answer: Receipt };
export const SAMPLES = data as Sample[];
