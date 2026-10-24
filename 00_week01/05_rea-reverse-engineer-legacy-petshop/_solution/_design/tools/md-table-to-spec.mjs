#!/usr/bin/env node
// md-table-to-spec.mjs · ดึงตาราง markdown ตัวที่ N จากไฟล์ .md (เช่น results/LAB0_RESULT.md) → spec JSON สำหรับ render-result.mjs
//
// ใช้:   node md-table-to-spec.mjs <file.md> [N=1] [--title "LAB 0 · ตรวจเครื่อง"] [--summary "สรุป: …"]
//                                 [--subtitle "…"] [--theme 05|06] [--cols 0,1,3] [--rows 0-5] [--out spec.json]
//        node md-table-to-spec.mjs <file.md> --list      # แสดงรายการตารางทั้งหมด (เลข · บรรทัด · หัวคอลัมน์ · จำนวนแถว)
//
// - N นับจาก 1 · ข้ามตารางที่อยู่ในบล็อก ``` ``` · รองรับ \| และ | ที่อยู่ใน `code`
// - --cols เลือกคอลัมน์ (นับจาก 0) · --rows เลือกแถว เช่น 0-5 หรือ 0,2,7 (นับจาก 0 ไม่รวมหัวตาราง)
// - ข้อความในช่องคงรูป markdown ไว้ (`code` **bold** <br>) เพราะ render-result.mjs แปลงให้เอง
// - ไม่ใส่ --out → พิมพ์ JSON ออก stdout (PowerShell: ใช้ --out แทน > เพื่อให้ได้ UTF-8 ไม่มี BOM)
// - แถวที่ช่องแรกเริ่มด้วย … (เช่น "… อีก 13 แถว") ถูกเก็บไว้ตามเดิม · highlight ใส่เองใน JSON ทีหลัง

import fs from 'node:fs';

const args = process.argv.slice(2);
const takeOpt = (name) => {
  const i = args.indexOf(name);
  if (i < 0) return undefined;
  const v = args[i + 1];
  args.splice(i, 2);
  return v;
};
const listOnly = args.includes('--list');
if (listOnly) args.splice(args.indexOf('--list'), 1);
const title = takeOpt('--title');
const summary = takeOpt('--summary');
const subtitle = takeOpt('--subtitle');
const theme = takeOpt('--theme');
const colsOpt = takeOpt('--cols');
const rowsOpt = takeOpt('--rows');
const out = takeOpt('--out');
const [file, nArg] = args;
if (!file) {
  console.error('ใช้: node md-table-to-spec.mjs <file.md> [N=1] [--title …] [--summary …] [--theme 05|06] [--cols 0,1] [--rows 0-5] [--out spec.json] | --list');
  process.exit(1);
}

// แยกช่องของแถวตาราง: ไม่ตัดที่ \| และไม่ตัด | ที่อยู่ใน `…`
function splitRow(line) {
  let s = line.trim();
  if (s.startsWith('|')) s = s.slice(1);
  if (s.endsWith('|') && !s.endsWith('\\|')) s = s.slice(0, -1);
  const cells = [];
  let cur = '';
  let inCode = false;
  for (let i = 0; i < s.length; i++) {
    const ch = s[i];
    if (ch === '\\' && s[i + 1] === '|') { cur += '|'; i++; continue; }
    if (ch === '`') inCode = !inCode;
    if (ch === '|' && !inCode) { cells.push(cur.trim()); cur = ''; continue; }
    cur += ch;
  }
  cells.push(cur.trim());
  return cells;
}
const isSep = (line) => /^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$/.test(line);

const lines = fs.readFileSync(file, 'utf8').replace(/^﻿/, '').split(/\r?\n/);
const tables = [];
let fence = false;
for (let i = 0; i < lines.length; i++) {
  if (/^\s*(```|~~~)/.test(lines[i])) { fence = !fence; continue; }
  if (fence) continue;
  if (lines[i].includes('|') && i + 1 < lines.length && isSep(lines[i + 1])) {
    const header = splitRow(lines[i]);
    const align = splitRow(lines[i + 1]).map((c) => (/^:-+:$/.test(c) ? 'center' : /-+:$/.test(c) ? 'right' : 'left'));
    const rows = [];
    let j = i + 2;
    for (; j < lines.length && lines[j].trim().startsWith('|'); j++) rows.push(splitRow(lines[j]));
    tables.push({ line: i + 1, header, align, rows });
    i = j - 1;
  }
}

if (listOnly) {
  tables.forEach((t, k) => console.log(`${k + 1}. บรรทัด ${t.line} · ${t.rows.length} แถว · ${t.header.join(' | ')}`));
  process.exit(0);
}
const n = Number(nArg ?? 1);
const t = tables[n - 1];
if (!t) {
  console.error(`ไม่พบตารางที่ ${n} (ไฟล์นี้มี ${tables.length} ตาราง · ดูด้วย --list)`);
  process.exit(1);
}

const parseList = (s, max) => s.split(',').flatMap((p) => {
  const m = p.match(/^(\d+)-(\d+)$/);
  if (m) return Array.from({ length: Math.min(+m[2], max - 1) - +m[1] + 1 }, (_, k) => +m[1] + k);
  return [+p];
}).filter((x) => x >= 0 && x < max);

const cols = colsOpt ? parseList(colsOpt, t.header.length) : t.header.map((_, k) => k);
const rowIdx = rowsOpt ? parseList(rowsOpt, t.rows.length) : t.rows.map((_, k) => k);
const pick = (r) => cols.map((c) => r[c] ?? '');

const spec = {
  title: title ?? `LAB ? · (ใส่หัวเรื่อง) — จาก ${file.split(/[\\/]/).pop()} ตารางที่ ${n}`,
  ...(subtitle ? { subtitle } : {}),
  theme: theme ?? '05',
  columns: pick(t.header),
  rows: rowIdx.map((k) => pick(t.rows[k])),
  summary: summary ?? 'สรุป: (ใส่บรรทัดสรุปจากตัวเลขจริงใน RESULT)',
  highlight: [],
};
// เก็บการจัดกลางจาก :---: ของ markdown ถ้ามี
const al = pick(t.align);
if (al.some((a) => a !== 'left')) spec.align = al;

const json = JSON.stringify(spec, null, 2) + '\n';
if (out) {
  fs.writeFileSync(out, json, 'utf8');
  console.error(`${out} · ตารางที่ ${n} (บรรทัด ${t.line}) · ${spec.columns.length} คอลัมน์ × ${spec.rows.length} แถว`);
} else {
  process.stdout.write(json);
}
