// รวมผลของทุกเคส (out/answers/case<N>.json) -> out/results.json + out/TEST_REPORT.md (ภาษาไทย)
// ใช้:  node make-report.mjs
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const outDir = path.join(here, "out");
const { cases } = JSON.parse(fs.readFileSync(path.join(here, "cases.json"), "utf8"));

// ---- ชื่อโมเดลและที่อยู่ LLM: อ่านจาก environment ก่อน แล้วจึงอ่าน ../frontend/.env ----
function readEnvFile(file) {
  const env = {};
  if (!fs.existsSync(file)) return env;
  for (const line of fs.readFileSync(file, "utf8").split(/\r?\n/)) {
    const m = line.match(/^\s*([A-Z_]+)\s*=\s*(.*?)\s*$/);
    if (m) env[m[1]] = m[2].replace(/^["']|["']$/g, "");
  }
  return env;
}
const fileEnv = readEnvFile(path.join(here, "..", "frontend", ".env"));
const model = process.env.LLM_MODEL || fileEnv.LLM_MODEL || "mock-thai-massage";
const baseUrl = process.env.LLM_BASE_URL || fileEnv.LLM_BASE_URL || "http://mock-llm:8000";

/** ซ่อนชื่อเครื่อง/IP ของ LLM (เหลือแค่ scheme และ port) — ยกเว้น mock ที่ไม่ใช่ความลับ */
function hideHost(url) {
  try {
    const u = new URL(url);
    if (u.hostname === "mock-llm") return url;
    return `${u.protocol}//<ซ่อน>${u.port ? ":" + u.port : ""}`;
  } catch {
    return "<ซ่อน>";
  }
}

// ---- รวมผล ----
const results = cases.map((c) => {
  const file = path.join(outDir, "answers", `case${c.id}.json`);
  const r = fs.existsSync(file)
    ? JSON.parse(fs.readFileSync(file, "utf8"))
    : { passed: false, failures: ["ไม่มีผล (เคสนี้ไม่ได้รัน)"], turns: [], booking: null };
  return {
    id: c.id,
    name: `case${c.id}-${c.slug}`,
    group: c.group,
    action: c.action,
    must: c.must,
    baseline: c.baseline,
    passed: r.passed,
    failures: r.failures,
    turns: r.turns,
    booking: r.booking,
    gif: `gifs/case${c.id}-${c.slug}.gif`,
  };
});
const passed = results.filter((r) => r.passed).length;

fs.mkdirSync(outDir, { recursive: true });
fs.writeFileSync(
  path.join(outDir, "results.json"),
  JSON.stringify({ passed, total: results.length, model, llm_base_url: hideHost(baseUrl), results }, null, 2)
);

// ---- ตาราง Markdown ----
const cell = (s) => String(s).replace(/\|/g, "\\|").replace(/\r?\n+/g, "<br>").trim();
const short = (s, max = 500) => (s.length > max ? s.slice(0, max) + "…" : s);

function actual(r) {
  // เคสถามต่อเนื่อง: แสดงคำตอบจริงครบทุกข้อความ
  const lines = r.turns.map((t, i) => (r.turns.length > 1 ? `${i + 1}) ` : "") + short(t.bot || "(ไม่มีข้อความ)"));
  if (r.booking) {
    const b = r.booking;
    lines.push(`การ์ดจองสำเร็จ #${b.id}: ${b.name} · ${b.phone} · ${b.service} · ${b.time}`);
  }
  return lines.join("\n") || "(ไม่มีคำตอบ)";
}

const md = [
  "# รายงานผลทดสอบแชทบอท",
  "",
  `**ผ่าน ${passed}/${results.length} เคส** · โมเดล: \`${model}\` · LLM: \`${hideHost(baseUrl)}\``,
  "",
  "| # | กลุ่ม | ลูกค้าทำอะไร | ต้องมี | คำตอบที่ควรได้ (baseline) | คำตอบจริง | ผล |",
  "|---|---|---|---|---|---|---|",
  ...results.map((r) =>
    `| ${r.id} | ${cell(r.group)} | ${cell(r.action)} | ${cell(r.must)} | ${cell(r.baseline)} | ${cell(actual(r))} | ` +
    `${r.passed ? "✅ ผ่าน" : "❌ ไม่ผ่าน: " + cell(r.failures.join("; "))} |`
  ),
  "",
  "วิดีโอของแต่ละเคสอยู่ที่ `gifs/case<N>-<ชื่อ>.gif` · ผลแบบละเอียดอยู่ที่ `results.json`",
  "",
].join("\n");
fs.writeFileSync(path.join(outDir, "TEST_REPORT.md"), md);

console.log(`ผ่าน ${passed}/${results.length} เคส (โมเดล ${model})`);
const failed = results.filter((r) => !r.passed);
for (const r of failed) console.log(`  ไม่ผ่าน เคส ${r.id}: ${r.failures.join("; ")}`);
console.log(`รายงาน: ${path.join(outDir, "TEST_REPORT.md")}`);
