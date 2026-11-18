// เทียบผล 26 เคสของโมเดล Base กับ Fine-tuned -> compare.json + COMPARE.md (+ GIF ของเคสที่ผลต่างกันไม่เกิน 4 เคส ใน diff-gifs/)
// อ่าน: out-base/results.json, out-ft/results.json (รอบเบราว์เซอร์) และ repeat.json (รันซ้ำผ่าน API ถ้ามี)
//   node compare.mjs
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const MODELS = { base: "Base", ft: "Fine-tuned" };
const MAX_GIFS = 4;
const BIG = { label: "โมเดลใหญ่ Qwen3.8 27B บน RTX 5090 (บทที่แล้ว)", passed: 26, total: 26 };

const load = (f) => (fs.existsSync(path.join(here, f)) ? JSON.parse(fs.readFileSync(path.join(here, f), "utf8")) : null);
const ui = { base: load("out-base/results.json"), ft: load("out-ft/results.json") };
if (!ui.base || !ui.ft) {
  console.error("ไม่พบ out-base/results.json หรือ out-ft/results.json — รัน run-both.sh ก่อน");
  process.exit(1);
}
const rep = load("repeat.json");

const answerText = (r) => {
  const lines = r.turns.map((t, i) => (r.turns.length > 1 ? `${i + 1}) ` : "") + (t.bot || "(ไม่มีข้อความ)"));
  if (r.booking) lines.push(`การ์ดจอง: ${r.booking.name} · ${r.booking.phone} · ${r.booking.service} · ${r.booking.time}`);
  return lines.join("\n");
};

const rows = ui.base.results.map((b) => {
  const f = ui.ft.results.find((x) => x.id === b.id);
  const row = {
    id: b.id,
    name: b.name,
    group: b.group,
    action: b.action,
    must: b.must,
    base: { passed: b.passed, failures: b.failures },
    ft: { passed: f.passed, failures: f.failures },
    differs: b.passed !== f.passed,
  };
  if (rep) for (const m of Object.keys(MODELS)) row[m].repeat_pass = rep.models[m].per_case.find((p) => p.id === b.id).pass_count;
  if (row.differs) row.answers = { base: answerText(b), ft: answerText(f) };
  return row;
});

const diffs = rows.filter((r) => r.differs);
// GIF: เคสที่ผลต่างกัน (ไม่เกิน 4 เคส) ทั้งของ Base และ Fine-tuned
const gifDir = path.join(here, "diff-gifs");
fs.rmSync(gifDir, { recursive: true, force: true });
fs.mkdirSync(gifDir, { recursive: true });
const gifs = [];
for (const r of diffs.slice(0, MAX_GIFS)) {
  for (const m of Object.keys(MODELS)) {
    const src = path.join(here, `out-${m}`, "gifs", `${r.name}.gif`);
    if (!fs.existsSync(src)) continue;
    const dst = `${r.name}-${m}.gif`;
    fs.copyFileSync(src, path.join(gifDir, dst));
    gifs.push(`diff-gifs/${dst}`);
  }
}

const summary = {
  big_27b: { ...BIG },
  ...Object.fromEntries(
    Object.entries(MODELS).map(([m, label]) => [
      m,
      {
        label,
        model: ui[m].model,
        passed: ui[m].passed,
        total: ui[m].total,
        failed_cases: rows.filter((r) => !r[m].passed).map((r) => r.id),
        repeat: rep && { scores: rep.models[m].scores, mean: rep.models[m].mean, sd: rep.models[m].sd, min: rep.models[m].min, max: rep.models[m].max, always_fail: rep.models[m].always_fail, flaky: rep.models[m].flaky },
      },
    ])
  ),
};
fs.writeFileSync(
  path.join(here, "compare.json"),
  JSON.stringify({ summary, differing_cases: diffs.map((r) => r.id), gifs, cases: rows }, null, 2)
);

// ---- COMPARE.md ----
const cell = (s) => String(s).replace(/\|/g, "\\|").replace(/\r?\n+/g, "<br>").trim();
const mark = (p) => (p ? "✅" : "❌");
const R = rep?.repeat ?? 0;
const md = [
  "# เทียบผล 26 เคส: Base vs Fine-tuned",
  "",
  `| โมเดล | ผ่าน (รอบเบราว์เซอร์) | ${rep ? `รันซ้ำ ${R} รอบผ่าน API (แต่ละรอบ) | เฉลี่ย ± SD |` : ""} เคสที่ไม่ผ่าน |`,
  `|---|---|${rep ? "---|---|" : ""}---|`,
  `| ${BIG.label} | ${BIG.passed}/${BIG.total} |${rep ? " – | – |" : ""} – |`,
  ...Object.keys(MODELS).map((m) => {
    const s = summary[m];
    const r = s.repeat;
    return `| ${s.label} (\`${s.model}\`) | ${s.passed}/${s.total} |${r ? ` ${r.scores.join(", ")} | ${r.mean} ± ${r.sd} |` : ""} ${s.failed_cases.join(", ") || "–"} |`;
  }),
  "",
  "## รายเคส",
  "",
  `| เคส | กลุ่ม | ต้องมี | Base | Fine-tuned |${rep ? ` Base ผ่าน/${R} | FT ผ่าน/${R} |` : ""}`,
  `|---|---|---|---|---|${rep ? "---|---|" : ""}`,
  ...rows.map(
    (r) =>
      `| ${r.differs ? "**" + r.name + "**" : r.name} | ${cell(r.group)} | ${cell(r.must)} | ${mark(r.base.passed)} | ${mark(r.ft.passed)} |` +
      (rep ? ` ${r.base.repeat_pass} | ${r.ft.repeat_pass} |` : "")
  ),
  "",
  `## เคสที่ผลต่างกัน (${diffs.length} เคส) พร้อมคำตอบจริง`,
  "",
  ...(diffs.length
    ? diffs.flatMap((r) => [
        `### ${r.name} · ${cell(r.action)}`,
        "",
        `ต้องมี: ${r.must}`,
        "",
        "| | ผล | คำตอบจริง | เหตุผลที่ไม่ผ่าน |",
        "|---|---|---|---|",
        ...Object.entries(MODELS).map(
          ([m, label]) => `| ${label} | ${mark(r[m].passed)} | ${cell(r.answers[m])} | ${cell(r[m].failures.join("\n") || "–")} |`
        ),
        "",
        ...gifs.filter((g) => g.includes(`/${r.name}-`)).map((g) => `![${path.basename(g)}](${g})`),
        "",
      ])
    : ["ไม่มี — ทั้ง 2 โมเดลผ่าน/ไม่ผ่านเคสเดียวกัน", ""]),
];
fs.writeFileSync(path.join(here, "COMPARE.md"), md.join("\n"));
console.log(
  `Base ${ui.base.passed}/26 · Fine-tuned ${ui.ft.passed}/26 · ผลต่างกัน ${diffs.length} เคส (${diffs.map((r) => r.id).join(", ") || "-"}) · GIF ${gifs.length} ไฟล์`
);
