// ผังองค์กร 2 ภาพ กว้าง 1200px ให้อ่านออกบน GitHub: ภาพ 1 ภาพรวม 4 ชั้น · ภาพ 2 รายชื่อทุกคนตามสาย
// node org-chart.mjs <people.json> <out-overview.png> <out-people.png> <chromium.exe>
import { readFileSync } from 'node:fs';
import { chromium } from 'playwright-core';
const [,, json, outA, outB, exe] = process.argv;
const d = JSON.parse(readFileSync(json, 'utf8'));
const P = Object.fromEntries(d.people.map(p => [p.user, p]));
const dep = Object.fromEntries(d.departments.map(x => [x.team, x.name]));
const icon = { exec:'👔', sales:'💼', sa:'🧩', product:'📦', dev:'💻', qa:'🧪', devops:'⚙️', mlops:'🤖', hr:'🤝', finance:'🧾', platform:'🏛️' };
const tint = { business:'#eff6ff', tech:'#f0fdf4', corporate:'#fdf2f8' }, edge = { business:'#2563eb', tech:'#16a34a', corporate:'#db2777' };
const first = p => p.name.split(' ')[0];
const role = p => p.role.replace(/ ดูแล .*/, '');
const team = t => d.people.filter(p => p.team === t);
const staff = d.people.filter(p => p.team !== 'exec' && !p.lead).length;

const css = `body{margin:0;width:1200px;font-family:'Leelawadee UI','Segoe UI',sans-serif;background:#f8fafc;color:#1d2433}
h1{font-size:46px;margin:26px 36px 4px} .sub{margin:0 36px 18px;font-size:24px;color:#4a5568}
.b{background:#fff;border-radius:14px;padding:10px 8px;box-shadow:0 2px 6px #0001;border:2px solid #cbd5e1;box-sizing:border-box;text-align:center}
.b.lead{border-color:#f59e0b;background:#fffbeb} .b.new{border-style:dashed;border-color:#22c55e;background:#f0fdf4}
.b.md{border:4px solid #1d4ed8;background:#dbeafe} .b.dir{border:3px solid #475569;background:#f1f5f9}
.n{font-size:26px;font-weight:800} .u{font-family:Consolas,monospace;font-size:20px;color:#1e40af}
.r{font-size:18px;color:#475569;line-height:1.3} .s{font-family:Consolas,monospace;font-size:17px;color:#64748b;margin-top:5px;border-top:1px dashed #e2e8f0;padding-top:4px}
.v{width:4px;background:#475569;margin:0 auto} .legend{margin:18px 36px 28px;font-size:21px;color:#334155;line-height:1.7}`;
const box = (p, cls = '') => `<div class="b ${cls} ${p.lead ? 'lead' : ''} ${p.skill ? '' : 'new'}"><div class="n">${first(p)}${p.lead ? ' 👑' : ''}${p.skill ? '' : ' 🆕'}</div><div class="u">${p.user}</div><div class="r">${role(p)}</div><div class="s">${p.skill ?? 'น้องใหม่ · ยังไม่มี skill'}</div></div>`;

// ภาพ 1: MD → 3 สาย → หัวหน้าแผนก (ชั้น 4 สรุปเป็นจำนวนคน)
const deptCard = t => {
  const ps = team(t), h = ps.find(p => p.lead), nw = ps.filter(p => !p.skill).length;
  return `<div class="dc"><div class="dt">${icon[t]} ${dep[t]}</div><div class="dh">👑 ${first(h)} <span>${h.user}</span></div><div class="dn">${ps.length} คน${nw ? ` · 🆕 ${nw}` : ''}</div></div>`;
};
const overview = `<html><head><meta charset="utf-8"><style>${css}
.row{display:flex;align-items:center;margin:0 36px} .lv{width:92px;font-size:22px;font-weight:800;color:#1d4ed8;flex:none}
.top{display:flex;align-items:center;gap:14px;margin-left:calc(50% - 92px - 170px)} .dash{width:44px;border-top:4px dashed #94a3b8}
.bar{height:4px;background:#475569;margin:0 calc(36px + (1200px - 72px - 92px)/6) 0 calc(36px + 92px + (1200px - 72px - 92px)/6)}
.cols{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;flex:1}
.col{border:3px solid;border-radius:18px;padding:0 12px 14px;display:flex;flex-direction:column;align-items:stretch}
.cn{font-size:26px;font-weight:800;text-align:center;margin:10px 0 8px}
.dc{background:#fff;border:2px solid #f59e0b;border-radius:12px;padding:8px 12px;margin-top:10px}
.dt{font-size:24px;font-weight:800} .dh{font-size:21px} .dh span{font-family:Consolas,monospace;font-size:18px;color:#1e40af}
.dn{font-size:19px;color:#475569}
.foot{margin:16px 36px 0 128px;padding:14px 18px;border:2px dashed #94a3b8;border-radius:14px;font-size:23px;background:#fff}
</style></head><body>
<h1>ผังองค์กรโนวาเทค (1/2) · ภาพรวม</h1>
<div class="sub">4 ชั้น ${d.people.length} คน · สั่งงานไล่จากบนลงล่าง: MD → ผู้บริหาร 3 สาย → หัวหน้าแผนก 👑 → พนักงาน</div>
<div class="row"><div class="lv">ชั้น 1</div><div class="top"><div style="width:340px">${box(P['md-somchai'], 'md')}</div><div class="dash"></div><div style="width:280px">${box(P['exec-ploy'])}</div></div></div>
<div class="v" style="height:22px;margin-left:calc(36px + 92px + (1200px - 72px - 92px)/2 - 2px)"></div>
<div class="bar"></div>
<div class="row" style="align-items:flex-start"><div class="lv" style="margin-top:70px">ชั้น 2<br><br><br><br><br>ชั้น 3</div><div class="cols">${d.divisions.map(v => `
  <div class="col" style="background:${tint[v.id]};border-color:${edge[v.id]}"><div class="cn" style="color:${edge[v.id]}">${v.name}</div>${box(P[v.head], 'dir')}${v.teams.map(deptCard).join('')}</div>`).join('')}
</div></div>
<div class="foot"><b>ชั้น 4</b> พนักงาน ${staff} คน (รวมน้องใหม่ 🆕 ${d.people.filter(p => !p.skill).length} คน) → ดูทุกคนใน <b>ภาพ 2/2</b></div>
<div class="legend">👑 = หัวหน้าแผนก / ผู้ดูแล skill ของแผนก (ทีม <b>leads</b>) · <span style="border-bottom:4px dashed #94a3b8">เส้นประ</span> = ผู้ช่วยผู้บริหาร ขึ้นตรงกับ MD<br>บรรทัดล่างในกล่อง = skill ที่คนนั้นสร้างใน LAB 1</div>
</body></html>`;

// ภาพ 2: ทุกคน แยกเป็น 3 แถบตามสาย แต่ละแผนกเป็น 1 คอลัมน์
const band = v => `<div class="band" style="background:${tint[v.id]};border-color:${edge[v.id]}">
  <div class="bh"><span style="color:${edge[v.id]}">${v.name}</span> · ผู้บริหารสาย ${first(P[v.head])} <code>${v.head}</code></div>
  <div class="grid" style="grid-template-columns:repeat(${Math.max(v.teams.length, 3)},1fr)">${v.teams.map(t => {
    const ps = team(t), h = ps.find(p => p.lead);
    return `<div class="col"><div class="dt">${icon[t]} ${dep[t]}</div>${[h, ...ps.filter(p => p !== h)].map(p => box(p)).join('<div class="v" style="height:10px;background:#94a3b8"></div>')}</div>`;
  }).join('')}</div></div>`;
const people = `<html><head><meta charset="utf-8"><style>${css}
.band{border:3px solid;border-radius:18px;margin:0 36px 18px;padding:10px 12px 14px}
.bh{font-size:27px;font-weight:800;margin:0 4px 10px} .bh code{font-size:21px;color:#1e40af;font-weight:400}
.grid{display:grid;gap:10px} .col{display:flex;flex-direction:column}
.dt{font-size:22px;font-weight:800;text-align:center;margin-bottom:6px;white-space:nowrap}
.n{font-size:24px} .u{font-size:18px} .r{font-size:16px} .s{font-size:15px}
</style></head><body>
<h1>ผังองค์กรโนวาเทค (2/2) · ทุกคนตามสาย</h1>
<div class="sub">แต่ละคอลัมน์ = 1 แผนก · กล่องบนสุด 👑 = หัวหน้าแผนก · 🆕 กรอบเขียวประ = น้องใหม่ ยังไม่มี skill</div>
${d.divisions.map(band).join('')}
<div class="legend" style="margin-top:4px">ไม่อยู่ในภาพนี้: MD <code>md-somchai</code> และผู้ช่วยผู้บริหาร <code>exec-ploy</code> (ดูภาพ 1/2)<br>🏛️ ทีมกลาง (platform) = ทีมภายในที่ดูแลเครื่องมือกลางและคลัง skill ของทั้งบริษัท</div>
</body></html>`;

const b = await chromium.launch({ executablePath: exe });
for (const [html, out] of [[overview, outA], [people, outB]]) {
  const pg = await b.newPage({ viewport: { width: 1200, height: 400 } });
  await pg.setContent(html); await pg.screenshot({ path: out, fullPage: true });
}
await b.close();
