// rea-input.mjs — ห่อผล REA (Evidence JSON) เป็นไฟล์ input ของคำสั่ง REA ถัดไป
// ใช้ (รันจากรากบท · path relative = จากโฟลเดอร์ที่รัน):
//   node rea\rea-input.mjs trace   <analyze.json> <seedKind string|api> <seedValue> <incoming|outgoing|both> <out.json>
//   node rea\rea-input.mjs s2b     <reference-source.json> <analyze.json> <out.json>
//   node rea\rea-input.mjs compare <left-analyze.json> <right-analyze.json> <out.json>
//   node rea\rea-input.mjs view    <analyze.json> <out.json>
// ผลเขียนเป็น JSON บรรทัดเดียว UTF-8 ไม่มี BOM (REA ไม่รับไฟล์ที่มี BOM)
import { readFileSync, writeFileSync, mkdirSync, statSync } from "node:fs";
import { dirname, resolve } from "node:path";

const USAGE = `usage:
  node rea/rea-input.mjs trace   <analyze.json> <seedKind: string|api> <seedValue> <direction: incoming|outgoing|both> <out.json>
  node rea/rea-input.mjs s2b     <reference-source.json> <analyze.json> <out.json>
  node rea/rea-input.mjs compare <left-analyze.json> <right-analyze.json> <out.json>
  node rea/rea-input.mjs view    <analyze.json> <out.json>`;
const fail = (msg) => {
  if (msg) console.error(msg);
  console.error(USAGE);
  process.exit(2);
};

const load = (file) => {
  let text;
  try {
    text = readFileSync(resolve(process.cwd(), file), "utf8");
  } catch (e) {
    fail(`อ่านไฟล์ไม่ได้: ${file} (${e.code ?? e.message})`);
  }
  try {
    return JSON.parse(text.replace(/^﻿/, ""));
  } catch (e) {
    fail(`ไม่ใช่ JSON: ${file} (${e.message})`);
  }
};
const analyze = (file) => {
  const ev = load(file);
  if (ev?.operation !== "analyze_javascript_application")
    fail(`${file} ต้องเป็นผล analyze-javascript-application --json (operation = ${ev?.operation})`);
  return ev;
};

const [mode, ...rest] = process.argv.slice(2);
let obj, out;
switch (mode) {
  case "trace": {
    if (rest.length !== 5) fail();
    const [file, seedKind, seedValue, direction, o] = rest;
    if (!["string", "api"].includes(seedKind)) fail(`seedKind ต้องเป็น string หรือ api (ได้ ${seedKind})`);
    if (!["incoming", "outgoing", "both"].includes(direction)) fail(`direction ต้องเป็น incoming outgoing หรือ both (ได้ ${direction})`);
    if (!seedValue) fail("seedValue ว่าง");
    obj = { application: analyze(file), seed: { kind: seedKind, value: seedValue }, direction };
    out = o;
    break;
  }
  case "s2b": {
    if (rest.length !== 3) fail();
    const [refFile, appFile, o] = rest;
    const ref = load(refFile);
    if (ref?.schema !== "HistoricalSourceGraph")
      fail(`${refFile} ต้องเป็นผล import-reference-source --json (schema HistoricalSourceGraph · ได้ ${ref?.schema ?? ref?.operation})`);
    obj = { reference: ref, application: analyze(appFile) };
    out = o;
    break;
  }
  case "compare": {
    if (rest.length !== 3) fail();
    const [l, r, o] = rest;
    obj = { left: analyze(l), right: analyze(r) };
    out = o;
    break;
  }
  case "view": {
    if (rest.length !== 2) fail();
    const [file, o] = rest;
    obj = { source: { kind: "inline", evidence: analyze(file) }, view: { kind: "summary" } };
    out = o;
    break;
  }
  default:
    fail(mode ? `ไม่รู้จักโหมด: ${mode}` : undefined);
}

const target = resolve(process.cwd(), out);
mkdirSync(dirname(target), { recursive: true });
writeFileSync(target, JSON.stringify(obj), "utf8");
console.log(`wrote ${out} (${statSync(target).size} bytes)`);
