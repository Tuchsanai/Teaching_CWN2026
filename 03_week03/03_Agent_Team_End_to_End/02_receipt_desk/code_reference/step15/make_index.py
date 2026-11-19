"""Build test/index.html + test/evidence/<round>/<TC>/... from the Playwright JSON results.
usage: python code_step15/make_index.py round1 [round2 ...]
- reads test/runs/<round>/shard-*.json (one per shard) — later rounds override earlier ones per TC
- reads test/triage.json  {"TC-x-yy": {"verdict": "web|plan|test|-", "note": "...", "ap": "..."}}
- writes test/evidence/<round>/<TC>/* (screenshots, JSON evidence, traces) and test/index.html
- writes test/runs/summary.json (final status per TC) for the report
"""
import base64, glob, html, json, os, re, shutil, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
T = os.path.join(ROOT, 'test')
rounds = sys.argv[1:] or ['round1']
triage = json.load(open(os.path.join(T, 'triage.json'), encoding='utf8')) if os.path.exists(os.path.join(T, 'triage.json')) else {}
PLAN = open(os.path.join(T, 'TEST-PLAN.md'), encoding='utf8').read()
GROUPS = {'1': '5.1 การรับชุดใบเสร็จ', '2': '5.2 ผลอ่านและธงไม่แน่ใจ', '3': '5.3 การตรวจแก้และยืนยัน', '4': '5.4 งานด่วน',
          '5': '5.5 สถานะงานในคิวและใบที่อ่านไม่ได้', '6': '5.6 รายงานรายเดือน', '7': '5.7 สิทธิ์ของแต่ละบทบาท', '8': '5.8 ลูกค้าภายนอก'}

def plan_row(tc):
    for line in PLAN.splitlines():
        if line.startswith(f'| {tc} ') or line.startswith(f'| {tc} ★'):
            cells = [c.strip() for c in line.strip('|').split('|')]
            return {'topic': cells[1], 'expected': cells[3], 'source': cells[4]}
    return {'topic': '', 'expected': '', 'source': ''}

def walk(suite, out):
    for sp in suite.get('specs', []):
        for t in sp['tests']:
            out.append((sp, t))
    for s in suite.get('suites', []):
        walk(s, out)

results = {}   # tc -> dict
for rnd in rounds:
    for f in sorted(glob.glob(os.path.join(T, 'runs', rnd, 'shard-*.json'))):
        j = json.load(open(f, encoding='utf8'))
        items = []
        for s in j['suites']:
            walk(s, items)
        for sp, t in items:
            m = re.match(r'(TC-\d-\d\d)', sp['title'])
            if not m:
                continue
            tc = m.group(1)
            r = t['results'][-1] if t['results'] else {}
            status = 'skipped' if t.get('status') == 'skipped' or r.get('status') == 'skipped' else r.get('status', 'unknown')
            ev_dir = os.path.join(T, 'evidence', rnd, tc)
            shutil.rmtree(ev_dir, ignore_errors=True)
            os.makedirs(ev_dir, exist_ok=True)
            files = []
            for i, a in enumerate(r.get('attachments', [])):
                name = re.sub(r'[^\w.\-ก-๙]+', '_', a['name'])[:60]
                ext = {'image/png': '.png', 'application/json': '.json', 'text/plain': '.txt', 'application/zip': '.zip', 'text/markdown': '.md'}.get(a.get('contentType'), '')
                if a['name'] == 'error-context':
                    ext = '.md'
                dst = os.path.join(ev_dir, f'{i:02d}_{name}{"" if name.endswith(ext) else ext}')
                if a.get('body'):
                    open(dst, 'wb').write(base64.b64decode(a['body']))
                elif a.get('path') and os.path.exists(a['path']):
                    shutil.copyfile(a['path'], dst)
                else:
                    continue
                files.append({'name': a['name'], 'type': a.get('contentType', ''), 'path': os.path.relpath(dst, T).replace('\\', '/')})
            errs = [e.get('message', '') for e in r.get('errors', [])] or ([r['error'].get('message', '')] if r.get('error') else [])
            ann = [{'type': a['type'], 'description': a.get('description', '')} for a in t.get('annotations', []) + r.get('annotations', [])]
            seen = set(); ann = [a for a in ann if not (json.dumps(a, ensure_ascii=False) in seen or seen.add(json.dumps(a, ensure_ascii=False)))]
            prev = results.get(tc, {}).get('history', [])
            results[tc] = {'tc': tc, 'title': sp['title'], 'tags': sp.get('tags', []), 'status': status, 'round': rnd,
                           'duration_s': round(r.get('duration', 0) / 1000, 1), 'errors': [re.sub(r'\x1b\[[0-9;]*m', '', e) for e in errs],
                           'annotations': ann, 'files': files, 'history': prev + [{'round': rnd, 'status': status}]}

def prio(r):
    return next((t.lstrip('@') for t in r['tags'] if t.lstrip('@') in ('P1', 'P2', 'P3')), '?')
def env(r):
    return next((t.lstrip('@') for t in r['tags'] if t.lstrip('@') in ('M', 'A', 'R')), '?')

def final_label(r):
    tri = triage.get(r['tc'], {})
    if r['status'] == 'skipped':
        return 'blocked'
    if r['status'] == 'passed':
        return 'pass'
    return 'fail'

summary = []
for tc in sorted(results, key=lambda x: (int(x[3]), int(x[5:]))):
    r = results[tc]
    r['priority'] = prio(r); r['env'] = env(r); r['final'] = final_label(r)
    r['triage'] = triage.get(tc, {})
    r['plan'] = plan_row(tc)
    summary.append(r)
json.dump(summary, open(os.path.join(T, 'runs', 'summary.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)

# ------------------------------------------------------------------ HTML
def e(s):
    return html.escape(str(s))
V = {'web': ('เว็บผิด', 'v-web'), 'plan': ('แผนผิด', 'v-plan'), 'test': ('เทสต์ผิด → แก้แล้ว', 'v-test')}
cnt = {g: {'pass': 0, 'fail': 0, 'blocked': 0} for g in GROUPS}
for r in summary:
    cnt[r['tc'][3]][r['final']] += 1
tot = {k: sum(c[k] for c in cnt.values()) for k in ('pass', 'fail', 'blocked')}
p1 = [r for r in summary if r['priority'] == 'P1' and r['final'] != 'blocked']
p1_pass = sum(r['final'] == 'pass' for r in p1)
ran = tot['pass'] + tot['fail']

rows = []
for g, gname in GROUPS.items():
    rows.append(f'<h2 id="g{g}">{e(gname)} <small>ผ่าน {cnt[g]["pass"]} · ล้ม {cnt[g]["fail"]} · บล็อก {cnt[g]["blocked"]}</small></h2>')
    for r in [x for x in summary if x['tc'][3] == g]:
        tri = r['triage']; vlab, vcls = V.get(tri.get('verdict', ''), ('', ''))
        imgs = [f for f in r['files'] if f['type'] == 'image/png']
        others = [f for f in r['files'] if f['type'] != 'image/png']
        hist = ' → '.join(f"{h['round']}: {h['status']}" for h in r['history'])
        ann = ''.join(f'<li><b>{e(a["type"])}</b> {e(a["description"])}</li>' for a in r['annotations'])
        err = ''.join(f'<pre>{e(x[:1500])}</pre>' for x in r['errors'])
        rows.append(f'''
<details class="tc s-{r['final']}" id="{r['tc']}">
<summary><span class="badge b-{r['final']}">{ {'pass':'ผ่าน','fail':'ล้ม','blocked':'บล็อก'}[r['final']] }</span>
<b>{e(r['tc'])}</b> {e(r['plan']['topic'] or r['title'])} <span class="tag">{e(r['priority'])}</span><span class="tag">{e(r['env'])}</span>
{f'<span class="badge {vcls}">{e(vlab)}</span>' if vlab else ''}</summary>
<div class="body">
<p><b>ผลที่คาดหวัง (แผน):</b> {e(r['plan']['expected'])}</p>
<p class="muted">ที่มา: {e(r['plan']['source'])} · เวลา {r['duration_s']} วินาที · รอบ: {e(hist)}</p>
{f'<p><b>คัดแยก:</b> {e(tri.get("note",""))}</p>' if tri.get('note') else ''}
{f'<ul class="ann">{ann}</ul>' if ann else ''}
{f'<details><summary>ข้อความที่ล้ม</summary>{err}</details>' if err else ''}
<div class="shots">{''.join(f'<a href="{e(f["path"])}" target="_blank"><img loading="lazy" src="{e(f["path"])}" alt="{e(f["name"])}"><span>{e(f["name"])}</span></a>' for f in imgs)}</div>
<ul class="files">{''.join(f'<li><a href="{e(f["path"])}" target="_blank">{e(f["name"])}</a> <span class="muted">{e(f["type"])}</span>{" · เปิดด้วย npx playwright show-trace" if f["type"]=="application/zip" else ""}</li>' for f in others)}</ul>
</div></details>''')

page = f'''<!doctype html><html lang="th"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ReceiptDesk Test Evidence</title>
<style>
:root{{--bg:#f7f7f5;--fg:#1d1d1b;--muted:#6b6b66;--card:#fff;--line:#e3e2dc;--pass:#1f7a3f;--fail:#b3261e;--blk:#8a6d00;--web:#b3261e;--plan:#5b4bb7;--test:#0b6e99}}
@media (prefers-color-scheme:dark){{:root:not([data-theme=light]){{--bg:#161615;--fg:#ecebe6;--muted:#a3a29b;--card:#20201e;--line:#34332f}}}}
body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.55 system-ui,"Segoe UI","Noto Sans Thai",sans-serif}}
main{{max-width:1100px;margin:auto;padding:16px}} h1{{margin:.2em 0}} h2{{margin-top:1.6em;font-size:1.15em}} h2 small{{color:var(--muted);font-weight:400}}
.kpi{{display:flex;flex-wrap:wrap;gap:10px;margin:12px 0}} .kpi div{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 14px;min-width:120px}}
.kpi b{{display:block;font-size:1.5em}} .verdict{{padding:12px 14px;border-radius:10px;border:2px solid var(--fail);background:var(--card)}}
details.tc{{background:var(--card);border:1px solid var(--line);border-left:5px solid var(--line);border-radius:8px;margin:6px 0}}
details.tc.s-pass{{border-left-color:var(--pass)}} details.tc.s-fail{{border-left-color:var(--fail)}} details.tc.s-blocked{{border-left-color:var(--blk)}}
summary{{cursor:pointer;padding:8px 10px}} .body{{padding:0 14px 12px}} .muted{{color:var(--muted)}}
.badge{{display:inline-block;border-radius:6px;padding:0 7px;color:#fff;font-size:.85em;margin-right:4px}}
.b-pass{{background:var(--pass)}} .b-fail{{background:var(--fail)}} .b-blocked{{background:var(--blk)}} .v-web{{background:var(--web)}} .v-plan{{background:var(--plan)}} .v-test{{background:var(--test)}}
.tag{{border:1px solid var(--line);border-radius:5px;padding:0 5px;margin-left:4px;font-size:.8em;color:var(--muted)}}
.shots{{display:flex;flex-wrap:wrap;gap:8px}} .shots a{{width:220px;text-decoration:none;color:var(--muted);font-size:.8em}} .shots img{{width:100%;height:140px;object-fit:cover;object-position:top;border:1px solid var(--line);border-radius:6px}}
pre{{white-space:pre-wrap;font-size:.8em;background:var(--bg);padding:8px;border-radius:6px;max-height:300px;overflow:auto}}
table{{border-collapse:collapse;width:100%;background:var(--card)}} td,th{{border:1px solid var(--line);padding:5px 8px;text-align:left}}
nav a{{margin-right:10px}} a{{color:var(--test)}}
</style></head><body><main>
<h1>ReceiptDesk · หลักฐานการทดสอบ</h1>
<p class="muted">Playwright Test บน Chromium · 4 shard · เว็บจำลอง :3421 (AI_MODE=mock) + เว็บจริง :3420 (โมเดลจริง) · รอบ: {e(', '.join(rounds))} · รายงานเต็ม <a href="TEST-REPORT.md">TEST-REPORT.md</a></p>
<div class="kpi"><div>ผ่าน<b>{tot['pass']}</b></div><div>ล้ม<b>{tot['fail']}</b></div><div>บล็อก<b>{tot['blocked']}</b></div>
<div>อัตราผ่านรวม<b>{tot['pass']}/{ran} = {100*tot['pass']/max(ran,1):.1f}%</b></div><div>อัตราผ่าน P1<b>{p1_pass}/{len(p1)} = {100*p1_pass/max(len(p1),1):.1f}%</b></div></div>
<table><tr><th>กลุ่ม</th><th>ผ่าน</th><th>ล้ม</th><th>บล็อก</th></tr>{''.join(f'<tr><td><a href="#g{g}">{e(n)}</a></td><td>{cnt[g]["pass"]}</td><td>{cnt[g]["fail"]}</td><td>{cnt[g]["blocked"]}</td></tr>' for g, n in GROUPS.items())}</table>
{''.join(rows)}
</main></body></html>'''
open(os.path.join(T, 'index.html'), 'w', encoding='utf8').write(page)
print(json.dumps({'pass': tot['pass'], 'fail': tot['fail'], 'blocked': tot['blocked'], 'p1': f'{p1_pass}/{len(p1)}'}))
for r in summary:
    print(r['tc'], r['priority'], r['env'], r['final'], r['round'], '|', (r['errors'][0].splitlines()[0][:150] if r['errors'] else ''))
