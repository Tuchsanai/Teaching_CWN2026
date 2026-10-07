// mcp-smoke-test.mjs — ทดสอบ Playwright MCP โดยไม่ต้องพึ่ง Claude: spawn server แล้วคุย JSON-RPC ผ่าน stdio
// ใช้:  node mcp-smoke-test.mjs [--browser chrome|msedge|chromium] [--headed]
// ผล:   เปิด https://example.com แล้วบันทึกภาพไว้ที่ ./mcp-output/mcp-example.png
import { spawn } from 'node:child_process';
import { mkdirSync } from 'node:fs';
import { resolve } from 'node:path';

const args = process.argv.slice(2);
const browser = args.includes('--browser') ? args[args.indexOf('--browser') + 1] : 'chrome';
const outDir = resolve('mcp-output');
mkdirSync(outDir, { recursive: true });

const serverArgs = ['-y', '@playwright/mcp@latest', '--browser', browser, '--isolated', '--output-dir', outDir];
if (!args.includes('--headed')) serverArgs.push('--headless');
console.log(`spawn: npx ${serverArgs.join(' ')}`);
// Windows: npx เป็น .cmd จึงต้องรันผ่าน shell (ส่งเป็นสตริงเดียว)
const server = spawn(`npx ${serverArgs.map((a) => (a.includes(' ') ? `"${a}"` : a)).join(' ')}`, { shell: true, stdio: ['pipe', 'pipe', 'inherit'] });

let buf = '';
const waiting = new Map();
server.stdout.on('data', (chunk) => {
  buf += chunk;
  let i;
  while ((i = buf.indexOf('\n')) >= 0) {
    const line = buf.slice(0, i).trim();
    buf = buf.slice(i + 1);
    if (!line) continue;
    const msg = JSON.parse(line);
    if (msg.id !== undefined && waiting.has(msg.id)) { waiting.get(msg.id)(msg); waiting.delete(msg.id); }
  }
});

let nextId = 1;
function request(method, params = {}) {
  const id = nextId++;
  server.stdin.write(JSON.stringify({ jsonrpc: '2.0', id, method, params }) + '\n');
  return new Promise((res, rej) => {
    const t = setTimeout(() => rej(new Error(`${method} timeout`)), 60000);
    waiting.set(id, (m) => { clearTimeout(t); m.error ? rej(new Error(JSON.stringify(m.error))) : res(m.result); });
  });
}
const notify = (method) => server.stdin.write(JSON.stringify({ jsonrpc: '2.0', method }) + '\n');
const text = (r) => r.content.filter((c) => c.type === 'text').map((c) => c.text).join('\n');

try {
  const init = await request('initialize', { protocolVersion: '2025-06-18', capabilities: {}, clientInfo: { name: 'smoke-test', version: '1.0' } });
  console.log(`server: ${init.serverInfo.name} ${init.serverInfo.version}`);
  notify('notifications/initialized');
  const { tools } = await request('tools/list');
  console.log(`tools: ${tools.length} ตัว`);

  const nav = await request('tools/call', { name: 'browser_navigate', arguments: { url: 'https://example.com' } });
  if (nav.isError) throw new Error(text(nav));
  console.log(text(nav).split('\n').filter((l) => /Page URL|Page Title/.test(l)).join('\n'));

  const shot = await request('tools/call', { name: 'browser_take_screenshot', arguments: { filename: resolve(outDir, 'mcp-example.png'), scale: 'css' } });
  if (shot.isError) throw new Error(text(shot));
  console.log(`screenshot: ${resolve(outDir, 'mcp-example.png')}`);
  await request('tools/call', { name: 'browser_close', arguments: {} });
  console.log('RESULT: PASS');
} catch (e) {
  console.error('RESULT: FAIL', e.message);
  process.exitCode = 1;
} finally {
  server.stdin.end();
}
