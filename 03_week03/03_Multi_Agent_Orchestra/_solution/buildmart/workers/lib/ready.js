// workers/lib/ready.js — healthcheck ของ worker ใน compose คือ `test -f /tmp/ready`
import { writeFileSync, rmSync } from 'node:fs';

export function markReady(info = '') {
  try {
    writeFileSync('/tmp/ready', `${new Date().toISOString()} ${info}\n`);
  } catch {
    /* นอก docker (Windows) ไม่มี /tmp ก็ไม่เป็นไร */
  }
}
export function markNotReady() {
  try {
    rmSync('/tmp/ready', { force: true });
  } catch {}
}

/** ค้าง process ไว้ (placeholder) + ปิดอย่างสุภาพเมื่อได้ SIGTERM */
export function idleForever(cleanup) {
  const stop = async () => {
    markNotReady();
    try {
      await cleanup?.();
    } catch {}
    process.exit(0);
  };
  process.on('SIGTERM', stop);
  process.on('SIGINT', stop);
  setInterval(() => {}, 1 << 30);
}
