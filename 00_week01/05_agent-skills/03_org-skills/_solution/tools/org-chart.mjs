import { readFileSync } from 'node:fs';
import { chromium } from 'playwright-core';
const [,, json, out, exe] = process.argv;
const d = JSON.parse(readFileSync(json, 'utf8'));
const P = Object.fromEntries(d.people.map(p => [p.user, p]));
const dep = Object.fromEntries(d.departments.map(x => [x.team, x.name]));
const icon = { exec:'👔', sales:'💼', sa:'🧩', product:'📦', dev:'💻', qa:'🧪', devops:'⚙️', mlops:'🤖', hr:'🤝', finance:'🧾', platform:'🏛️' };
const tint = { business:'#eff6ff', tech:'#f0fdf4', corporate:'#fdf2f8' }, edge = { business:'#3b82f6', tech:'#16a34a', corporate:'#db2777' };
const box = (p, cls='') => `<div class="b ${cls} ${p.lead?'lead':''} ${p.skill?'':'new'}"><div class="n">${p.name.split(' ')[0]}${p.lead?' 👑':''}${p.skill?'':' 🆕'}</div><div class="u">${p.user}</div><div class="r">${p.role.replace(/ ดูแล .*/,'')}</div><div class="s">${p.skill ?? 'น้องใหม่ · ยังไม่มี skill'}</div></div>`;
const total = d.divisions.reduce((a, v) => a + v.teams.length, 0);
let acc = 0; const centers = d.divisions.map(v => { const c = (acc + v.teams.length / 2) / total * 100; acc += v.teams.length; return c; });
const divs = d.divisions.map(v => {
  const cols = v.teams.map(t => {
    const ps = d.people.filter(p => p.team === t), h = ps.find(p => p.lead), ms = ps.filter(p => !p.lead);
    return `<div class="col"><div class="tick"></div><div class="dep">${icon[t]} ${dep[t]}</div>${box(h)}${ms.map(m => `<div class="down"></div>${box(m,'mem')}`).join('')}</div>`;
  }).join('');
  const n = v.teams.length;
  return `<div class="div" style="flex:${n};background:${tint[v.id]};border-color:${edge[v.id]}">
    <div class="dname" style="color:${edge[v.id]}">${v.name}</div>
    <div class="dhead"><div class="tick"></div>${box(P[v.head],'dir')}</div>
    <div class="tick"></div><div class="bar" style="margin:0 calc(100%/${n}/2)"></div>
    <div class="cols" style="grid-template-columns:repeat(${n},1fr)">${cols}</div></div>`;
}).join('');
const html = `<html><head><meta charset="utf-8"><style>
body{margin:0;width:2100px;font-family:'Leelawadee UI','Segoe UI',sans-serif;background:#f8fafc;color:#1d2433}
h1{font-size:44px;margin:24px 40px 2px} .sub{margin:0 40px 12px;font-size:22px;color:#4a5568}
.lv{position:absolute;left:14px;font-size:15px;font-weight:700;color:#64748b;writing-mode:vertical-rl;transform:rotate(180deg)}
.top{display:flex;justify-content:center;position:relative}
.asst{display:flex;align-items:center;gap:10px;position:absolute;left:calc(50% + 140px);top:10px}
.dash{width:60px;border-top:3px dashed #94a3b8}
.trunk{width:3px;height:22px;background:#475569;margin:0 auto}
.topbar{height:3px;background:#475569;margin:0 40px}
.wrap{display:flex;gap:14px;padding:0 40px 16px}
.div{border:2px solid;border-radius:16px;padding:0 8px 10px;display:flex;flex-direction:column;align-items:center;position:relative}
.dname{font-size:22px;font-weight:800;margin:8px 0 0}
.dhead{display:flex;flex-direction:column;align-items:center;width:260px}
.bar{height:3px;background:#475569;align-self:stretch}
.cols{display:grid;gap:8px;width:100%}
.col{display:flex;flex-direction:column;align-items:center}
.tick{width:3px;height:14px;background:#475569}
.down{width:3px;height:12px;background:#94a3b8}
.dep{font-size:16px;font-weight:700;white-space:nowrap;margin:2px 0 4px}
.b{background:#fff;border-radius:12px;padding:7px 6px;box-shadow:0 2px 5px #0001;border:2px solid #cbd5e1;width:100%;box-sizing:border-box;text-align:center}
.b.lead{border-color:#f59e0b;background:#fffbeb} .b.dir{border-color:#475569;background:#f1f5f9;border-width:3px}
.b.top0{border-color:#1d4ed8;background:#dbeafe;border-width:3px} .b.new{border-style:dashed;border-color:#22c55e;background:#f0fdf4}
.n{font-size:18px;font-weight:700} .u{font-family:Consolas,monospace;font-size:14.5px;color:#1e40af}
.r{font-size:13px;color:#475569;line-height:1.3} .s{font-family:Consolas,monospace;font-size:12.5px;color:#64748b;margin-top:3px;border-top:1px dashed #e2e8f0;padding-top:3px}
.legend{margin:2px 40px 26px;font-size:19px;color:#334155;line-height:1.7}
.levels{display:flex;gap:26px;margin:0 40px 8px;font-size:18px;color:#334155}
.levels span b{color:#1d4ed8}
</style></head><body>
<h1>ผังองค์กรโนวาเทค · 4 ชั้น ${d.people.length} คน</h1>
<div class="sub">ใครรายงานต่อใคร: MD → ผู้บริหาร 3 สาย → หัวหน้าแผนก 👑 → พนักงาน (รวมน้องใหม่ 🆕)</div>
<div class="levels"><span><b>ชั้น 1</b> MD</span><span><b>ชั้น 2</b> ผู้บริหารสาย 3 คน + ผู้ช่วยผู้บริหาร</span><span><b>ชั้น 3</b> หัวหน้าแผนก 10 คน</span><span><b>ชั้น 4</b> พนักงาน ${d.people.filter(p=>p.team!=='exec'&&!p.lead).length} คน</span></div>
<div class="top"><div style="width:270px">${box(P['md-somchai'],'top0')}</div><div class="asst"><div class="dash"></div><div style="width:230px">${box(P['exec-ploy'])}</div></div></div>
<div class="trunk"></div><div class="topbar" style="margin:0 calc(40px + ${100-centers[centers.length-1]}% * 0.96) 0 calc(40px + ${centers[0]}% * 0.96)"></div>
<div class="wrap">${divs}</div>
<div class="legend">👑 = หัวหน้าแผนก / ผู้ดูแล skill (ทีม <b>leads</b>) · 🆕 กรอบเขียวประ = น้องใหม่ ยังไม่มี skill · <span style="border-bottom:3px dashed #94a3b8">เส้นประ</span> = ผู้ช่วยผู้บริหาร ขึ้นตรงกับ MD · บรรทัดล่างในกล่อง = skill ที่คนนั้นสร้าง<br>🏛️ ทีมกลาง (platform) = ทีมภายในที่ดูแลเครื่องมือกลางและคลัง skill ของทั้งบริษัท</div>
</body></html>`;
const b = await chromium.launch({ executablePath: exe });
const pg = await b.newPage({ viewport: { width: 2100, height: 400 } });
await pg.setContent(html); await pg.screenshot({ path: out, fullPage: true }); await b.close();
