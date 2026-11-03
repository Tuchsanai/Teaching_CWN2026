// ภาพประกอบ LAB 1 (กว้าง 1200px ให้อ่านออกบน GitHub): แผนที่โฟลเดอร์ · พรอมต์เดียวทุกโต๊ะ · ตัวอย่าง 3 โต๊ะจากผลรันจริง
// node lab1-diagrams.mjs <img-dir> <chromium.exe>
import { join } from 'node:path';
import { chromium } from 'playwright-core';
const [,, dir, exe] = process.argv;

const css = `body{margin:0;width:1200px;font-family:'Leelawadee UI','Segoe UI',sans-serif;background:#f8fafc;color:#1d2433}
h1{font-size:44px;margin:26px 36px 4px} .sub{margin:0 36px 18px;font-size:23px;color:#4a5568}
code,.m{font-family:Consolas,monospace} .read{color:#1d4ed8} .write{color:#15803d}
.tag{display:inline-block;border-radius:999px;padding:2px 12px;font-size:19px;font-weight:700;margin-left:8px;vertical-align:middle}
.tr{background:#dbeafe;color:#1e40af} .tw{background:#dcfce7;color:#166534} .tg{background:#f1f5f9;color:#475569}
.foot{margin:18px 36px 28px;font-size:21px;color:#334155;line-height:1.7}`;

// ① แผนที่โฟลเดอร์: อ่านจากไหน เขียนลงไหน
const row = (indent, name, tag, note, cls = '') => `<div class="row ${cls}" style="padding-left:${24 + indent * 34}px"><span class="m nm">${name}</span>${tag}<span class="note">${note}</span></div>`;
const R = '<span class="tag tr">📖 อ่าน</span>', W = '<span class="tag tw">✍️ เขียน</span>', G = '<span class="tag tg">ไม่แตะ</span>';
const folders = `<html><head><meta charset="utf-8"><style>${css}
.tree{margin:0 36px;background:#fff;border:2px solid #cbd5e1;border-radius:18px;padding:12px 0}
.row{display:flex;align-items:center;gap:6px;min-height:52px;font-size:22px;border-bottom:1px dashed #e2e8f0}
.row:last-child{border-bottom:0} .nm{font-size:24px;font-weight:700;min-width:300px}
.note{color:#475569;margin-left:14px;font-size:20px}
.desk{background:#fefce8} .here{background:#fef9c3;border-left:8px solid #f59e0b}
.real{margin:18px 36px 0;display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px}
.real div{background:#fff;border:2px solid #cbd5e1;border-radius:14px;padding:10px 14px;font-size:19px;line-height:1.5}
.real b{font-size:21px}
</style></head><body>
<h1>LAB 1 · ของแต่ละคนอยู่ที่ไหน</h1>
<div class="sub">ตัวอย่าง: เปิด Claude Code ที่โต๊ะของนิดา <code>novatech/desks/sales-nida/</code></div>
<div class="tree">
${row(0, 'novatech/', '', 'บริษัททั้งหมด (อยู่ในเครื่องเราเครื่องเดียว)')}
${row(1, 'people/', R, 'การ์ดพนักงาน: อ่านแค่ใบของตัวเอง <code>people/sales/sales-nida.md</code>')}
${row(1, 'company-kit/', R, 'ไดรฟ์กลาง: TOR ลูกค้า ราคา กติกา (ทุกคนอ่านที่เดียวกัน)')}
${row(1, 'desks/', '', 'โต๊ะ 1 โฟลเดอร์ต่อ 1 คน')}
${row(2, 'sales-nida/', '<span class="tag" style="background:#f59e0b;color:#fff">▶ เปิด Claude Code ที่นี่</span>', '= คอมพิวเตอร์ของนิดา', 'here')}
${row(3, 'notes/', R, 'โน้ตส่วนตัว (มีแค่ MD · นิดาไม่มี)', 'desk')}
${row(3, 'work/', W, '② ผลงานจริง 1 ชิ้น เช่น proposal', 'desk')}
${row(3, '.claude/skills/', W, '③ skill ส่วนตัว <code>sales-proposal/</code> อยู่ที่นี่', 'desk')}
${row(3, '.gitea-token', G, 'บัตรผ่านของนิดา (ใช้ตั้งแต่ LAB 2)', 'desk')}
${row(2, 'md-somchai/ · fin-joy/ · …', G, 'โต๊ะของคนอื่น ห้ามแตะ', '')}
</div>
<div class="real">
<div><b>💻 desks/&lt;ชื่อ&gt;/</b><br>ในบริษัทจริง = คอมของคนนั้น</div>
<div><b>📁 .claude/skills/</b> ในโต๊ะ<br>ในบริษัทจริง = <code>~/.claude/skills/</code> ในเครื่องตัวเอง</div>
<div><b>🗄️ company-kit/</b><br>ในบริษัทจริง = ไดรฟ์กลางของบริษัท</div>
</div>
<div class="foot">💡 skill อยู่ใน <b>โต๊ะของเจ้าของเท่านั้น</b> คนอื่นมองไม่เห็นและใช้ไม่ได้ → นี่คือ "ต่างคนต่างเก็บ" ที่ LAB 2 จะรวมเป็นคลังกลาง</div>
</body></html>`;

// ② พรอมต์เดียว ใช้ได้ทุกโต๊ะ
const prompt = `<html><head><meta charset="utf-8"><style>${css}
.p{margin:0 36px;display:flex;flex-direction:column;gap:12px}
.blk{display:grid;grid-template-columns:200px 1fr;border-radius:16px;overflow:hidden;border:3px solid}
.lab{display:flex;flex-direction:column;justify-content:center;align-items:center;font-size:30px;font-weight:800;color:#fff;text-align:center;line-height:1.2}
.lab small{font-size:19px;font-weight:600}
.txt{background:#fff;padding:12px 18px;font-size:21px;line-height:1.55}
.txt .q{font-family:'Leelawadee UI';background:#f8fafc;border-radius:8px;padding:6px 10px;display:block;color:#334155;margin-bottom:6px}
.desks{margin:20px 36px 0;display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
.d{background:#fff;border:2px solid #f59e0b;border-radius:14px;padding:10px 14px;font-size:20px;line-height:1.5}
.d b{font-size:22px}
</style></head><body>
<h1>LAB 1 · พรอมต์เดียว วางได้ทุกโต๊ะ</h1>
<div class="sub">พรอมต์มี 3 ส่วน = 3 ขั้นที่ทุกคนทำ · Claude รู้ว่าเราเป็นใครจาก <b>ชื่อโฟลเดอร์</b> ที่เปิดอยู่</div>
<div class="p">
<div class="blk" style="border-color:#2563eb"><div class="lab" style="background:#2563eb">① อ่าน<small>รู้ว่าเราเป็นใคร</small></div><div class="txt"><span class="q">"ผมเป็นเจ้าของโต๊ะนี้ (ชื่อโฟลเดอร์ = user ของผม) อ่านการ์ดของผมใน ../../people/ ก่อน"</span>📖 อ่านการ์ดตัวเอง → รู้ว่าเก่งอะไร ทำอะไรซ้ำ ชอบพิมพ์ว่าอะไร</div></div>
<div class="blk" style="border-color:#ea580c"><div class="lab" style="background:#ea580c">② ทำงาน<small>จริง 1 ชิ้น</small></div><div class="txt"><span class="q">"ลงมือทำงานที่ผมทำซ้ำ 1 ชิ้นจริง ๆ ด้วยข้อมูลใน ../../company-kit/ … แล้วเก็บผลงานไว้ใน work/"</span>📖 ใช้ข้อมูลบริษัทจริง → ✍️ ผลงานลง <code>work/</code> · ทำก่อนแล้วค่อยเก็บ ไม่ให้ AI เดา</div></div>
<div class="blk" style="border-color:#16a34a"><div class="lab" style="background:#16a34a">③ เก็บ<small>เป็น skill</small></div><div class="txt"><span class="q">"เก็บวิธีทำงานนี้เป็น skill ส่วนตัวที่ .claude/skills/&lt;ชื่อ skill ในการ์ด&gt;/"</span>✍️ <code>SKILL.md</code> + ความรู้ที่ต้องใช้สรุปไว้ใน <code>references/</code> (ให้ใช้ที่เครื่องอื่นได้)</div></div>
</div>
<div class="desks">
<div class="d"><b>💼 desks/sales-nida/</b><br>→ ทำ proposal ธนาคาร<br>→ skill <code>sales-proposal</code></div>
<div class="d"><b>👔 desks/md-somchai/</b><br>→ พิจารณาดีล รพ.<br>→ skill <code>deal-approval</code></div>
<div class="d"><b>🧾 desks/fin-joy/</b><br>→ คิดราคาและกำไร<br>→ skill <code>pricing-calc</code></div>
</div>
<div class="foot">พรอมต์เดียวกันทุกตัวอักษร × 24 โต๊ะ · <b>1 โต๊ะ = 1 แชตใหม่</b> · แต่ละคนได้งานและ skill ของตัวเอง</div>
</body></html>`;

// ③ ตัวอย่าง 1 โต๊ะ: อ่าน → ทำงาน → skill (ข้อมูลจาก _solution/desks-after-lab1 และ lab1/claude-summaries.md)
const brk = f => f.replace(/([/-])/g, '$1<wbr>');
const desk = (p) => `<html><head><meta charset="utf-8"><style>${css}
.cols{margin:0 36px;display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px}
.c{background:#fff;border:3px solid;border-radius:18px;padding:0 0 12px}
.h{font-size:27px;font-weight:800;color:#fff;padding:10px 16px;border-radius:14px 14px 0 0}
.it{padding:8px 16px 0;font-size:19px;line-height:1.45} .it code{font-size:18px;color:#1e40af}
.it .d{color:#64748b;font-size:18px}
.res{margin:8px 12px 0;background:#fff7ed;border-radius:10px;padding:8px 10px;font-size:20px;font-weight:700}
.tree{font-family:Consolas,monospace;font-size:18px;line-height:1.55;padding:8px 16px 0;white-space:pre;color:#14532d}
.note{margin:16px 36px 0;padding:12px 18px;border-radius:14px;font-size:22px;border:2px dashed #94a3b8;background:#fff}
</style></head><body>
<h1>${p.icon} ${p.title}</h1>
<div class="sub">เปิด Claude Code ที่ <code>desks/${p.user}/</code> · ${p.time} · ผลรันจริง</div>
<div class="cols">
<div class="c" style="border-color:#2563eb"><div class="h" style="background:#2563eb">① อ่าน</div>${p.reads.map(([f, d]) => `<div class="it"><code>${brk(f)}</code><br><span class="d">${d}</span></div>`).join('')}</div>
<div class="c" style="border-color:#ea580c"><div class="h" style="background:#ea580c">② ทำงานจริง → work/</div>${p.work.map(f => `<div class="it"><code>${brk(f)}</code></div>`).join('')}<div class="res">${p.result}</div></div>
<div class="c" style="border-color:#16a34a"><div class="h" style="background:#16a34a">③ skill ที่ได้</div><div class="tree">${p.skill}</div></div>
</div>
<div class="note">${p.note}</div>
<div class="foot"></div>
</body></html>`;

const people = [
  { file: 'lab1-desk-sales-nida.png', icon: '💼', title: 'นิดา หัวหน้าทีมขาย → skill sales-proposal', user: 'sales-nida', time: '4 นาที 4 วินาที',
    reads: [['people/sales/sales-nida.md', 'การ์ดของตัวเอง'], ['company-kit/deal-001/tor-bank-queue.md', 'TOR ธนาคาร 120 สาขา'], ['company-kit/won-proposals/', 'proposal 2 ฉบับที่เคยชนะ'], ['company-kit/price-list.csv · margin-rules.md', 'ราคาและกฎกำไร']],
    work: ['deal-001-proposal-nakhonluang-queue.md', 'deal-001-pricing-output.md', 'deal-001-internal-notes.md'],
    result: 'proposal 9 หัวข้อ · 4,780,000 บาท · margin 31.6%',
    skill: '.claude/skills/\n└─ sales-proposal/\n   ├─ SKILL.md\n   ├─ references/\n   │  ├─ proposal-template.md\n   │  ├─ winning-patterns.md\n   │  ├─ pricing-rules.md\n   │  ├─ pdpa-rules.md\n   │  ├─ checklist.md\n   │  └─ price-list.csv\n   └─ scripts/\n      └─ price.py',
    note: '⚠️ proposal นี้ <b>ไม่มี "ภาคผนวก PDPA"</b> เพราะกฎนี้อยู่ในโน้ตของ MD คนเดียว นิดาไม่เคยเห็น → ไปเจอกันใน LAB 4' },
  { file: 'lab1-desk-md-somchai.png', icon: '👔', title: 'สมชาย MD → skill deal-approval', user: 'md-somchai', time: '2 นาที 37 วินาที',
    reads: [['people/exec/md-somchai.md', 'การ์ดของตัวเอง'], ['notes/deal-rules.md', '🔒 โน้ตลับในโต๊ะ MD (มีคนเดียว)'], ['company-kit/deal-summaries/DS-2026-034-…', 'สรุปดีลพอร์ทัล รพ.เมืองใหม่'], ['company-kit/margin-rules.md · price-list.csv', 'กฎกำไรและราคา']],
    work: ['DS-2026-034/approval.md', 'DS-2026-034/deal-input.json'],
    result: '❌ ตีกลับ · margin หลังบวก buffer เหลือ 11.8% (เกณฑ์ ≥ 15%)',
    skill: '.claude/skills/\n└─ deal-approval/\n   ├─ SKILL.md\n   ├─ references/\n   │  ├─ approval-rules.md\n   │  ├─ approval-template.md\n   │  └─ price-list.csv\n   └─ scripts/\n      └─ deal_check.py',
    note: '🔒 กฎ "ภาคผนวก PDPA ของลูกค้าธนาคาร" จากโน้ตลับ ถูกเก็บไว้ใน <code>approval-rules.md</code> ของ skill นี้ <b>ที่เดียว</b> คนอื่นไม่รู้' },
  { file: 'lab1-desk-fin-joy.png', icon: '🧾', title: 'จอย หัวหน้าบัญชี → skill pricing-calc', user: 'fin-joy', time: '3 นาที 51 วินาที',
    reads: [['people/finance/fin-joy.md', 'การ์ดของตัวเอง'], ['company-kit/price-list.csv', 'ตารางราคา'], ['company-kit/margin-rules.md', 'กฎกำไรและส่วนลด'], ['company-kit/deal-001/ · won-proposals/', 'TOR และดีลที่ชนะไว้เทียบ']],
    work: ['deal-001-pricing-internal.md', 'deal-001-quotation-draft.md', '(+ ฉบับเข้างบ deal-001-B-*)'],
    result: 'ฉบับเข้างบ 4,800,000 บาท · margin 27.1% · ต้องให้ MD อนุมัติ',
    skill: '.claude/skills/\n└─ pricing-calc/\n   ├─ SKILL.md\n   ├─ references/\n   │  ├─ margin-rules.md\n   │  ├─ estimate-benchmarks.md\n   │  └─ price-list.csv\n   ├─ assets/\n   │  └─ example-deal.json\n   └─ scripts/\n      └─ price_calc.py',
    note: '📋 <code>price-list.csv</code> ถูกคัดลอกไว้ใน skill ของ <b>ทั้ง 3 คน</b> (นิดา · MD · จอย) และนิดาเขียนสคริปต์คิดราคาซ้ำกับจอย → ปัญหา "สำเนาซ้ำ" ท้าย LAB นี้' },
];

const b = await chromium.launch({ executablePath: exe });
const shots = [[folders, 'lab1-folders.png'], [prompt, 'lab1-prompt.png'], ...people.map(p => [desk(p), p.file])];
for (const [html, out] of shots) {
  const pg = await b.newPage({ viewport: { width: 1200, height: 400 } });
  await pg.setContent(html); await pg.screenshot({ path: join(dir, out), fullPage: true });
}
await b.close();
