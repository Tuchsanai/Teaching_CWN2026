// e2e/make-report.mjs — results.json (+ media.json) → TEST_REPORT.<mode>.md + report-data.<mode>.json
// แล้วรวมทุกโหมดที่เคยรันเป็น TEST_REPORT.md (ตาราง "โหมด | ผ่าน / ทั้งหมด" แยกกลุ่ม + ตารางทุกเคส)
import { existsSync, readFileSync, writeFileSync, readdirSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const DIR = path.dirname(fileURLToPath(import.meta.url));
const RESULTS = path.join(DIR, process.argv[2] || 'results.json');
const PLAYLIST = JSON.parse(readFileSync(path.join(DIR, 'playlist.json'), 'utf8'));
const MEDIA = existsSync(path.join(DIR, 'media.json')) ? JSON.parse(readFileSync(path.join(DIR, 'media.json'), 'utf8')) : {};
const GROUPS = [...new Set(PLAYLIST.map((p) => p.group))];
const ICON = { passed: '✅', failed: '❌', timedOut: '❌', interrupted: '❌', skipped: '⏭️' };

const body = (a) => {
  try {
    return a.body ? Buffer.from(a.body, 'base64').toString('utf8') : a.path && existsSync(a.path) ? readFileSync(a.path, 'utf8') : '';
  } catch {
    return '';
  }
};

function collect(suites, out = []) {
  for (const s of suites || []) {
    for (const spec of s.specs || [])
      for (const t of spec.tests || []) {
        const r = t.results?.[t.results.length - 1];
        if (r) out.push({ spec, r });
      }
    collect(s.suites, out);
  }
  return out;
}

// ---------- render ----------
function cell(s, max = 260) {
  s = String(s ?? '').replace(/\r/g, '').trim();
  if (s.length > max) s = s.slice(0, max) + '…';
  return s.replace(/\|/g, '\\|').replace(/\n+/g, '<br>');
}
const sec = (ms) => (ms == null ? '' : `${(ms / 1000).toFixed(1)} วิ`);

function counts(rows, group) {
  const rs = rows.filter((r) => !group || r.group === group);
  const ran = rs.filter((r) => r.status !== 'skipped');
  return { pass: ran.filter((r) => r.status === 'passed').length, ran: ran.length, skip: rs.length - ran.length, total: rs.length };
}
const fmtCount = (c) => (c.total === 0 ? '–' : c.ran === 0 ? `ข้าม ${c.skip}` : `${c.pass} / ${c.ran}${c.skip ? ` (ข้าม ${c.skip})` : ''}${c.pass === c.ran ? ' ✅' : ' ❌'}`);

function summaryTable(datas) {
  const head = `| โหมด | ${GROUPS.join(' | ')} | รวม ผ่าน / ทั้งหมด |\n|---|${GROUPS.map(() => '---').join('|')}|---|`;
  const lines = datas.map((d) => `| **${d.mode}**${d.tts ? ' + tts' : ''} | ${GROUPS.map((g) => fmtCount(counts(d.rows, g))).join(' | ')} | **${fmtCount(counts(d.rows))}** |`);
  return [head, ...lines].join('\n');
}

const ok = (b) => (b ? '✓' : '✗');
function answerOf(r) {
  const parts = [];
  // เคสเสียง V: ทุกรอบ = ไฟล์ · ข้อความถอด · CER · engine · หยุดพูด→ได้ยิน · คำตอบ · ผล 5 ข้อ
  if (r.voice?.length) {
    for (const t of r.voice)
      parts.push(
        `[รอบ ${t.n} ${t.file}] 🎙 “${t.transcript}” (CER ${t.cer ?? '–'}${t.engine ? ` · ${t.engine}` : ''}` +
          `${t.stopToAudioMs != null ? ` · หยุดพูด→ได้ยิน ${(t.stopToAudioMs / 1000).toFixed(1)} วิ` : ''}) → ${t.answer}` +
          `${t.cites?.length ? ` 📄 ${t.cites.join(', ')}` : ''}${t.cart ? ` 🛒 ${t.cart.join(', ')}` : ''}` +
          ` [ถอด${ok(t.ok?.transcript)} ตอบ${ok(t.ok?.answer)} เสียง${ok(t.ok?.audio)} มาสคอต${ok(t.ok?.mascot)}]`,
      );
    if (r.error) parts.push(`⚠ ${r.error}`);
    return parts.join('\n');
  }
  // เคสหลายรอบ M: ทุกรอบ = คำถาม → คำตอบ (+ cite · ตะกร้า · QT) ✓/✗
  if (r.turns?.length) {
    for (const t of r.turns)
      parts.push(`[รอบ ${t.n}] ${t.q} → ${t.answer}${t.cites?.length ? ` 📄 ${t.cites.join(', ')}` : ''}${t.cart ? ` 🛒 ${t.cart.join(', ')}` : ''}${t.quoteNo ? ` 🧾 ${t.quoteNo}` : ''} ${ok(t.ok)}`);
    if (r.error) parts.push(`⚠ ${r.error}`);
    return parts.join('\n');
  }
  for (const a of r.answers) parts.push((r.answers.length > 1 ? `[${a.name}] ` : '') + a.text);
  if (r.cites?.length) parts.push(`อ้างอิง: ${r.cites.join(', ')}`);
  if (r.audio?.length) parts.push(`เสียง: ${r.audio.map((a) => `${a.audioId.slice(0, 8)}… ${(a.durationMs / 1000).toFixed(1)} วิ @${(a.offsetMs / 1000).toFixed(1)} วิ`).join(', ')}`);
  if (!r.answers.length && r.checked) parts.push(r.checked.replace(/\s+/g, ' '));
  if (r.error) parts.push(`⚠ ${r.error}`);
  if (r.skipReason) parts.push(`ข้าม: ${r.skipReason}`);
  return parts.join('\n');
}

function mediaLinks(id) {
  const m = MEDIA[id];
  if (!m?.mp4) return '';
  const v = m.mics?.length ? ` · เสียงถาม+ตอบ ${m.voicedOk ? '✓' : '✗'} (${m.voiced?.segments ?? '?'} ช่วง/${m.mics.length} รอบ)` : '';
  return `[GIF](${m.gif}) · [MP4](${m.mp4})${m.hasAudio ? ' 🔊' : ''}${v}`;
}

function renderMode(d) {
  const rows = d.rows
    .map((r) => `| ${r.id} | ${r.group} | ${cell(r.title, 80)} | ${ICON[r.status] || r.status} | ${sec(r.durationMs)} | ${cell(answerOf(r), r.turns?.length || r.voice?.length ? 2600 : 420)} | ${mediaLinks(r.id)} |`)
    .join('\n');
  return `# TEST_REPORT (${d.mode}) — บ้านช่าง BuildMart

รันเมื่อ ${d.startTime ?? '-'} · ${d.url ?? ''} · ใช้เวลา ${sec(d.durationMs)}

${summaryTable([d])}

| เคส | กลุ่ม | ทดสอบ | ผล | เวลา | คำตอบจริง / ค่าที่ตรวจ | สื่อ |
|---|---|---|---|---|---|---|
${rows}
`;
}

function renderAll(datas) {
  const ids = PLAYLIST.map((p) => p.id);
  const byMode = Object.fromEntries(datas.map((d) => [d.mode, Object.fromEntries(d.rows.map((r) => [r.id, r]))]));
  const modes = datas.map((d) => d.mode);
  const media = Object.values(MEDIA).filter((m) => m.mp4);
  const avg = media.reduce((s, m) => s + (m.durationSec || 0), 0) / (media.length || 1);
  const voiced = media.filter((m) => m.hasAudio).map((m) => `${m.id} (${m.audio})`);
  const rows = ids
    .map((id) => {
      const pl = PLAYLIST.find((p) => p.id === id);
      const res = modes.map((m) => {
        const r = byMode[m][id];
        return r ? `${ICON[r.status] || r.status} ${r.status === 'skipped' ? '' : sec(r.durationMs)}` : '–';
      });
      // คำตอบจริง: เอาจากโหมดล่าสุดที่มีข้อมูล (ai ก่อน ถ้ารันแล้ว)
      const src = [...modes].reverse().map((m) => byMode[m][id]).find((r) => r && r.status !== 'skipped') || modes.map((m) => byMode[m][id]).find(Boolean);
      return `| ${id} | ${pl.group} | ${cell(pl.title, 80)} | ${res.join(' | ')} | ${src ? cell(answerOf(src), src.turns?.length || src.voice?.length ? 2600 : 360) : ''} | ${mediaLinks(id)} |`;
    })
    .join('\n');
  return `# TEST_REPORT — บ้านช่าง BuildMart (Playwright เพลย์ลิสต์)

${summaryTable(datas)}

- รายงานแยกโหมด: ${modes.map((m) => `[TEST_REPORT.${m}.md](TEST_REPORT.${m}.md)`).join(' · ') || '-'}
- วิดีโอ ${media.length} เคส · ยาวเฉลี่ย ${avg.toFixed(1)} วิ · MP4 ที่มีเสียงพูดจริง: ${voiced.join(', ') || '-'}
- ✅ ผ่าน · ❌ ไม่ผ่าน · ⏭️ ข้าม (กลุ่ม V ข้ามเมื่อยังไม่มีไฟล์เสียง \`voice-fixtures/\` · \`BM_TTS=0\` ปิดกลุ่ม T)
- กลุ่ม M/V แสดงทุกรอบ · V แสดงข้อความถอด + CER + engine + เวลาหยุดพูด→ได้ยินคำตอบ · MP4 ของ T/V มีเสียงจริง (V = เสียงคำถาม + เสียงตอบ ตรวจด้วย silencedetect)

| เคส | กลุ่ม | ทดสอบ | ${modes.map((m) => `ผล ${m}`).join(' | ')} | คำตอบจริง / ค่าที่ตรวจ | สื่อ |
|---|---|---|${modes.map(() => '---').join('|')}|---|---|
${rows}
`;
}

// ---------- 1) รอบล่าสุด → report-data.<mode>.json ----------
if (existsSync(RESULTS)) {
  const rep = JSON.parse(readFileSync(RESULTS, 'utf8'));
  const mode = rep.config?.metadata?.mode || 'mock';
  const rows = collect(rep.suites).map(({ spec, r }) => {
    const id = spec.title.split(' ')[0];
    const pl = PLAYLIST.find((p) => p.id === id) || {};
    const atts = r.attachments || [];
    const answers = atts.filter((a) => /^answer/.test(a.name)).map((a) => ({ name: a.name, text: body(a) }));
    const checked = atts.filter((a) => a.name === 'checked').map(body).join('\n');
    const cites = atts.filter((a) => a.name === 'cites').flatMap((a) => JSON.parse(body(a) || '[]'));
    const audio = atts.filter((a) => a.name === 'audio').map((a) => JSON.parse(body(a) || 'null')).filter(Boolean);
    const turns = atts.filter((a) => a.name === 'turns').flatMap((a) => JSON.parse(body(a) || '[]'));
    const voice = atts.filter((a) => a.name === 'voice-turns').flatMap((a) => JSON.parse(body(a) || '[]'));
    const err = (r.errors?.[0]?.message || r.error?.message || '').replace(/\u001b\[[0-9;]*m/g, '').split('\n').filter(Boolean).slice(0, 3).join(' ');
    return {
      id,
      group: pl.group,
      title: pl.title || spec.title,
      expect: pl.expect,
      status: r.status,
      durationMs: r.duration,
      answers,
      checked,
      cites,
      audio,
      turns,
      voice,
      error: r.status === 'passed' ? '' : err,
      skipReason: r.status === 'skipped' ? (r.annotations || []).find((a) => a.type === 'skip')?.description || '' : '',
    };
  });
  const order = (id) => PLAYLIST.findIndex((p) => p.id === id);
  rows.sort((a, b) => order(a.id) - order(b.id));
  const data = { mode, tts: !!rep.config?.metadata?.tts, url: rep.config?.metadata?.url, startTime: rep.stats?.startTime, durationMs: rep.stats?.duration, rows };
  writeFileSync(path.join(DIR, `report-data.${mode}.json`), JSON.stringify(data, null, 2));
  writeFileSync(path.join(DIR, `TEST_REPORT.${mode}.md`), renderMode(data));
  console.log(`เขียน TEST_REPORT.${mode}.md`);
}

// ---------- 2) รวมทุกโหมด → TEST_REPORT.md ----------
const all = readdirSync(DIR)
  .filter((f) => /^report-data\.(mock|ai)\.json$/.test(f))
  .map((f) => JSON.parse(readFileSync(path.join(DIR, f), 'utf8')))
  .sort((a, b) => (a.mode === 'mock' ? -1 : 1));
writeFileSync(path.join(DIR, 'TEST_REPORT.md'), renderAll(all));
console.log(`เขียน TEST_REPORT.md (โหมด: ${all.map((d) => d.mode).join(', ') || '-'})`);

