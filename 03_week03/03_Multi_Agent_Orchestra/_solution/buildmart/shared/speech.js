// shared/speech.js — ทำข้อความคำตอบบอทให้เป็น "ข้อความพูด" ก่อนส่งไป TTS (VoxCPM2 บน ai-box)
// ใช้ทั้ง workers/tts-worker.js และ e2e/make-tts-cache.mjs → sha256(speechText(x)) ตรงกัน = mock เล่นไฟล์ที่อัดไว้ได้
//
//   speechText(raw)  → ตัด <think>, tag [CALC]{..} [ADD_TO_CART]{..} [QUOTE]{}, [n], markdown, URL, /api/..., emoji
//                      ขึ้นบรรทัด → เว้นวรรค · ตัดเหลือ 600 ตัวอักษร
//   speechLang(text) → 'th' ถ้ามีอักษรไทย ไม่งั้น 'en'
//   sha256Hex(text)  → ชื่อไฟล์ใน e2e/voice-fixtures/tts-cache/<sha>.wav (node:crypto)
import { createHash } from 'node:crypto';

export const MAX_SPEECH_CHARS = 600;
const EMOJI_RE = /[\u{1F000}-\u{1FAFF}\u{2600}-\u{27BF}\u{1F1E6}-\u{1F1FF}\u{2B00}-\u{2BFF}\u{FE00}-\u{FE0F}\u{200D}\u{20E3}]+/gu;

export function speechText(raw) {
  let t = String(raw || '');
  t = t.replace(/<think>[\s\S]*?(<\/think>|$)/g, ' ');
  t = t.replace(/\[(?:CALC|ADD_TO_CART|QUOTE|[A-Z_]{3,})\]\s*(\{[^{}]*\})?/g, ' ');
  t = t.replace(/!?\[([^\]]*)\]\([^)]*\)/g, '$1');
  t = t.replace(/(https?:\/\/|www\.)\S+/g, ' ');
  t = t.replace(/\/api\/\S+/g, ' ');
  t = t.replace(/\[\d+(?:\s*,\s*\d+)*\]/g, ' ');
  t = t.replace(EMOJI_RE, ' ');
  t = t.replace(/`{1,3}/g, '');
  t = t.replace(/(\*\*|__|~~|\*)/g, '');
  t = t.replace(/^\s{0,3}#{1,6}\s*/gm, '');
  t = t.replace(/^\s*[-+•>]\s+/gm, '');
  t = t.replace(/^\s*\|?[-:| ]{3,}\|?\s*$/gm, '');
  t = t.replace(/\|/g, ' ');
  t = t.replace(/\s*\n+\s*/g, ' ');
  t = t.replace(/[ \t]{2,}/g, ' ').trim();
  return t.length > MAX_SPEECH_CHARS ? t.slice(0, MAX_SPEECH_CHARS) : t;
}

export const speechLang = (t) => (/[฀-๿]/.test(String(t || '')) ? 'th' : 'en');

export const sha256Hex = (s) => createHash('sha256').update(String(s), 'utf8').digest('hex');

/** ความยาว WAV (ms) จาก header (PCM/float ทุกแบบ) · ไม่ใช่ WAV → null */
export function wavDurationMs(buf) {
  if (!buf || buf.length < 44 || buf.toString('ascii', 0, 4) !== 'RIFF' || buf.toString('ascii', 8, 12) !== 'WAVE') return null;
  let off = 12;
  let byteRate = 0;
  while (off + 8 <= buf.length) {
    const id = buf.toString('ascii', off, off + 4);
    let size = buf.readUInt32LE(off + 4);
    if (id === 'fmt ') byteRate = buf.readUInt32LE(off + 16);
    if (id === 'data') {
      if (size === 0 || size === 0xffffffff || off + 8 + size > buf.length) size = buf.length - off - 8; // stream WAV
      return byteRate ? Math.round((size / byteRate) * 1000) : null;
    }
    off += 8 + size + (size % 2);
  }
  return null;
}
