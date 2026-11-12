// components/three/util.ts (v3) — ตัวช่วยเล็ก ๆ ของฉาก 3D (ไม่ import three ที่นี่ ให้ไฟล์นี้เบา)
export type MascotState = 'idle' | 'listening' | 'thinking' | 'talking';

let webglCache: boolean | null = null;
/** เบราว์เซอร์สร้าง WebGL ได้ไหม (ตรวจครั้งเดียว) · ?nowebgl=1 บังคับใช้ภาพนิ่ง (ไว้ทดสอบ) */
export function hasWebGL(): boolean {
  if (typeof window === 'undefined') return false;
  if (webglCache !== null) return webglCache;
  try {
    if (new URLSearchParams(window.location.search).has('nowebgl')) return (webglCache = false);
    const c = document.createElement('canvas');
    const gl = (c.getContext('webgl2') || c.getContext('webgl')) as WebGLRenderingContext | null;
    webglCache = !!gl;
    gl?.getExtension('WEBGL_lose_context')?.loseContext();
  } catch {
    webglCache = false;
  }
  return webglCache;
}

export function prefersReducedMotion(): boolean {
  return typeof window !== 'undefined' && !!window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
}

/** ค่าที่เปลี่ยนทุกเฟรมโดยไม่ re-render React (เช่น ความดังเสียง 0..1) */
export type Live = { current: number };

export const damp = (a: number, b: number, lambda: number, dt: number) => a + (b - a) * (1 - Math.exp(-lambda * dt));
