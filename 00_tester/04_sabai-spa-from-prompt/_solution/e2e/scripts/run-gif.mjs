// npm run test:gif → ตั้ง GIF=1 แล้วรันเฉพาะ chromium (+ TC API ที่เขียน log) — ใช้ได้ทั้ง PowerShell/bash
import { spawnSync } from 'node:child_process';
const args = ['playwright', 'test', '--project=chromium', '--project=api', ...process.argv.slice(2)];
const r = spawnSync('npx', args, { stdio: 'inherit', shell: true, env: { ...process.env, GIF: '1' } });
process.exit(r.status ?? 1);
