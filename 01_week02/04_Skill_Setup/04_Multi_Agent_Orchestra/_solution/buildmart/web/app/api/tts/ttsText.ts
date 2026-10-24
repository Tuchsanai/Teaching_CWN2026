// ตัวช่วยของ /api/tts — ทำข้อความ markdown ให้เป็นข้อความพูดล้วน + ตรวจว่ามี tts-worker ไหม (C1)
import { checkQueue } from '@/lib/amqp';

export function speakable(raw: string): string {
  return raw
    .replace(/\[(CALC|ADD_TO_CART|QUOTE)\][^\n]*/g, '')
    .replace(/\[\d+\]/g, '')
    .replace(/\*\*(.+?)\*\*/g, '$1')
    .replace(/^\s*(?:[-*•]|\d+[.)])\s+/gm, '')
    .replace(/[*_`#>|]/g, ' ')
    .replace(/[ \t]+/g, ' ')
    .replace(/\n{2,}/g, '\n')
    .trim()
    .slice(0, 1500);
}

export const langOf = (t: string) => (/[฀-๿]/.test(t) ? 'th' : 'en');

let cache: { at: number; enabled: boolean } | null = null;

/** TTS_ENABLED=false/0/off → ปิด · true/1/on → เปิด · auto (ค่าเริ่มต้น) → ดูว่ามี consumer ที่คิว tts.request */
export async function ttsEnabled(): Promise<boolean> {
  const flag = (process.env.TTS_ENABLED || 'auto').toLowerCase();
  if (['false', '0', 'off', 'no'].includes(flag)) return false;
  if (['true', '1', 'on', 'yes'].includes(flag)) return true;
  if (cache && Date.now() - cache.at < 3000) return cache.enabled;
  let enabled = false;
  try {
    const q = await checkQueue('tts.request');
    enabled = !!q && q.consumerCount > 0;
  } catch {
    enabled = false;
  }
  cache = { at: Date.now(), enabled };
  return enabled;
}
