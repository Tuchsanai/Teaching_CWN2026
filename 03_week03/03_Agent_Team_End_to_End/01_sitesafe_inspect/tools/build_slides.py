#!/usr/bin/env python3
"""สร้างสไลด์ SiteSafe_Inspect_Slides.html ของหัวข้อที่ 1 · SiteSafe Inspect

  python tools/build_slides.py            (รันจากโฟลเดอร์ของหัวข้อ)

หลักการจัดสไลด์: 1 สไลด์ = 1 ประเด็น · คำอธิบายอยู่ในภาพ แผนภาพ หรือกราฟ · ข้อความข้างภาพไม่เกิน 3-4 ข้อ
เนื้อหาชนิดเดียวกันใช้ layout เดียวกันทั้งเด็ค:
- ภาพถ่ายฉากเหตุการณ์ -> bleed(): ภาพเต็มหน้า + ประโยคเดียวบนแถบ
- ภาพอธิบาย / ภาพผลจริง -> px(): ภาพใหญ่ราว 2 ใน 3 ของหน้า + ประเด็นหรือตัวเลขด้านข้าง
- ก่อน/หลัง -> pair(): 2 ภาพเรียงกันพร้อมป้าย
- ตัวเลขผลจริง -> แผนภูมิที่วาดจากค่าใน README (hbars / stack / gauge / timeline / dag) หรือ tiles()

ที่มาของเนื้อหา
- ตาราง พรอมต์ ผลจริง และ "อ่านผลอย่างไร": อ่านจาก README.md ตอนสร้าง (พรอมต์ตรงตัวอักษร)
- ภาพใหม่: tools/slides_figures.py (FIGS, FIGS2, PHOTOS, PHOTOS2) · ภาพครอบตัดจากภาพจริง: img/cNN-*.jpg
- เครื่องมือเรนเดอร์: tools/slides_engine.py (ไม่แก้ไข · CSS และชิ้นส่วนเพิ่มเติมอยู่ในไฟล์นี้)
"""
import html as H
import os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import slides_engine as E
from slides_engine import (md, sec, walk, table, para, CTX, add, note, fig, explain, tiles, cards, tbl)
from slides_figures import FIGS

S = E.slide
SECS = E.load("README.md")
FIG = {f["img"]: f for f in FIGS}
OUT, TITLE = "SiteSafe_Inspect_Slides.html", "SiteSafe Inspect · Slides"
HOW = "วางใน Claude Code ที่เปิดไว้ที่โฟลเดอร์ `01_sitesafe_inspect`"

# ------------------------------------------------------------------ CSS ของเด็คนี้ (ต่อท้าย CSS ของ engine)
E.CSS += r"""
/* ภาพใหญ่ + ข้อความด้านข้าง */
.ex.big .fig{flex:2.1 1 0}
.ex.big .side{flex:1 1 0}
.ex.big .side .tiles{flex-direction:column;gap:12px}
.ex.big .side .tile{padding:.4em .8em .5em}
.ex.big .side .tile .num{font-size:1.6em}
.ex .side .pt{background:#fff;border-left:5px solid var(--teal);border-radius:10px;padding:.45em .75em;line-height:1.45;box-shadow:0 2px 6px rgba(18,48,94,.05)}
.ex .side .pt.bad{border-left-color:var(--red)}.ex .side .pt.warn{border-left-color:var(--orange)}
.ex .side .lead2{font-size:.86em;color:var(--muted);line-height:1.45}
.ex.chart .fig{display:block;align-self:center}
/* ภาพเต็มหน้า + แถบประโยค */
.slide.bleed{padding:0;background-size:cover;background-position:center}
.bleed .band{position:absolute;left:0;right:0;bottom:0;padding:34px 72px 40px;background:linear-gradient(0deg,rgba(6,13,26,.94) 0%,rgba(6,13,26,.82) 70%,rgba(6,13,26,0) 100%)}
.bleed .band .k{font-size:19px;font-weight:600;color:#8fe0dc;margin-bottom:6px}
.bleed .band .s{font-size:40px;font-weight:700;line-height:1.32;color:#fff;max-width:1380px}
.bleed .band .s2{font-size:22px;color:#cfe0ff;margin-top:10px;line-height:1.5}
.bleed .band a{color:#9fd8ff;border-bottom-color:rgba(159,216,255,.4)}
/* ก่อน/หลัง */
.pair{flex:1 1 0;min-height:0;display:flex;gap:22px}
.pair.rows{flex-direction:column}
.pair .pc{flex:1 1 0;min-width:0;min-height:0;display:flex;flex-direction:column;gap:8px}
.pair .pl{flex:none;font-weight:700;color:var(--navy);font-size:.92em}
.pair .pl span{display:inline-block;color:#fff;background:var(--navy);border-radius:7px;padding:.05em .55em;margin-right:.5em;font-size:.85em}
.pair .pc.after .pl span{background:var(--red)}
.pair .pc.good .pl span{background:var(--teal)}
.pair .fig{min-height:0}
/* แท่งที่กำหนดสีตามสถานะ */
.hb{display:flex;flex-direction:column;gap:.32em}
.hb .r{display:grid;grid-template-columns:minmax(0,1.25fr) minmax(0,1.6fr) 7.2em;gap:16px;align-items:center;background:#fff;border:1px solid var(--line);border-radius:10px;padding:.3em .8em}
.hb .lb{line-height:1.3;font-size:.92em}.hb .lb small{display:block;color:var(--muted);font-size:.8em}
.hb .tr{height:1.05em;background:#eef2f7;border-radius:999px;overflow:hidden;display:flex}
.hb .fl{height:100%;min-width:0}
.hb .vl{font-family:var(--mono);font-weight:700;color:var(--navy);text-align:right;font-size:.9em}
.hb .r.bad{border-color:#f1b3b3;background:#fff7f7}.hb .r.bad .vl{color:var(--red)}
.hb .r.grey .vl{color:var(--muted)}
.t-ok{background:var(--green)}.t-bad{background:var(--red)}.t-n{background:#5c7fae}.t-teal{background:var(--teal)}
.t-grey{background:repeating-linear-gradient(135deg,#aab6c6 0 6px,#c7d0dc 6px 12px)}.t-warn{background:var(--orange)}
.lgd{display:flex;gap:22px;flex-wrap:wrap;font-size:.8em;color:var(--muted)}
.lgd i{display:inline-block;width:.95em;height:.95em;border-radius:3px;margin-right:.35em;vertical-align:-.1em}
.hb.stack .tr{height:1.5em;border-radius:6px}
.hb.stack .fl{display:flex;align-items:center;justify-content:center;color:#fff;font-size:.72em;font-weight:700;font-family:var(--mono)}
.hb.stack .fl.t-grey{color:#24324a}
/* แท่งเทียบเกณฑ์ */
.gauge .r{grid-template-columns:minmax(0,1.1fr) minmax(0,1.6fr) 8.5em}
.gauge .tr{position:relative;overflow:visible;background:#eef2f7}
.gauge .fl{border-radius:999px}
.gauge .thr{position:absolute;top:-.45em;bottom:-.45em;width:3px;background:var(--navy)}
.gauge .thr b{position:absolute;top:-1.35em;left:50%;transform:translateX(-50%);white-space:nowrap;font-size:.62em;color:var(--navy)}
.verdict{border-radius:12px;padding:.5em .9em;font-weight:700;font-size:1.02em;background:var(--red-soft);color:var(--red);border:2px solid #f1b3b3;text-align:center}
.verdict.ok{background:var(--green-soft);color:var(--green);border-color:#a7dcb8}
/* DAG */
.dag{position:relative;width:100%;aspect-ratio:1400/620;flex:none}
.dag svg{position:absolute;inset:0;width:100%;height:100%}
.dag .nd{position:absolute;width:15.7%;height:21.8%;background:#fff;border:2px solid #9fb0c7;border-radius:10px;padding:.25em .45em;font-size:.56em;line-height:1.28;overflow:hidden;box-shadow:0 2px 6px rgba(18,48,94,.08)}
.dag .nd b{display:block;font-size:1.25em;color:var(--navy)}
.dag .nd .st{display:inline-block;margin-top:.15em;font-size:.9em;font-weight:700;border-radius:5px;padding:0 .4em;background:#eef2f7;color:var(--muted)}
.dag .nd.cp{border-color:var(--orange);border-width:3px}
.dag .nd.ok{border-color:var(--teal)}.dag .nd.ok .st{background:var(--teal-soft);color:var(--teal)}
.dag .nd.bad{border-color:var(--red);border-width:3px;background:#fff6f6}.dag .nd.bad .st{background:var(--red);color:#fff}
.dag .nd.grey{border-style:dashed;background:#f3f5f8;color:var(--muted)}.dag .nd.grey b{color:var(--muted)}.dag .nd.grey .st{background:#dde3eb}
.dag .nd.res{border-color:var(--green);border-width:3px}.dag .nd.res .st{background:var(--green);color:#fff}
/* แผนที่ 16 ขั้น */
.rm{display:flex;gap:14px;align-items:stretch}
.rm .ph{flex:var(--n) 1 0;min-width:0;display:flex;flex-direction:column;gap:10px}
.rm .ph .h{border-radius:10px;padding:.35em .6em;color:#fff;font-weight:700;font-size:.82em;line-height:1.3;background:var(--c)}
.rm .ph .h small{display:block;font-weight:500;opacity:.85;font-size:.85em}
.rm .dots{display:flex;gap:8px;justify-content:space-around}
.rm .dot{width:2.1em;height:2.1em;border-radius:50%;background:#fff;border:3px solid var(--c);color:var(--navy);font-weight:700;display:flex;align-items:center;justify-content:center;font-size:.95em}
.rm .nm{display:flex;flex-direction:column;gap:5px}
.rm .nm div{font-size:.64em;line-height:1.3;color:#2b3648;background:#fff;border:1px solid var(--line);border-radius:8px;padding:.25em .45em}
.rm .nm div b{color:var(--c)}
.rmline{height:6px;border-radius:3px;background:linear-gradient(90deg,#6b7f9a,var(--teal),var(--orange),#7c4dca,var(--green));margin:4px 0 2px}
.ptrow{display:grid;gap:14px;grid-template-columns:repeat(var(--n),minmax(0,1fr))}
.ptrow .pt{background:#fff;border-left:5px solid var(--teal);border-radius:10px;padding:.4em .7em;line-height:1.42;font-size:.86em;box-shadow:0 2px 6px rgba(18,48,94,.05)}
.ptrow .pt.bad{border-left-color:var(--red)}.ptrow .pt.warn{border-left-color:var(--orange)}
.dag.w{width:88%;margin:0 auto}
.pair.rows{flex:none}.pair.rows.tall{flex:1 1 0}
.pair.rows .pc{flex:none}
.pair.rows .fig{display:block;min-height:0;flex:none}
.pair.rows .fig img{width:100%;max-height:none}
.pair.rows.tall .pc{flex:1 1 0}
.pair.rows.tall .fig{display:flex;flex:1 1 0;min-height:0}
.pair.rows.tall .fig img{width:auto;max-height:100%}
/* แถบตำแหน่งบนหน้าคั่น */
.strip{display:flex;gap:7px;margin-top:6px;align-items:center}
.strip i{width:28px;height:10px;border-radius:5px;background:rgba(255,255,255,.22)}
.strip i.done{background:rgba(143,224,220,.6)}
.strip i.cur{background:var(--orange);width:46px}
.strip span{font-size:18px;color:#cfe0ff;margin-left:10px}
/* เส้นเวลา */
.tl{background:#fff;border:1px solid var(--line);border-radius:12px;padding:.8em 1em}
.tl .bar2{position:relative;height:2.2em;border-radius:8px;background:repeating-linear-gradient(135deg,#c3ccd8 0 8px,#d9dfe8 8px 16px);overflow:hidden}
.tl .seg{position:absolute;left:0;top:0;bottom:0;background:var(--teal)}
.tl .lbs{display:flex;justify-content:space-between;margin-top:.4em;font-size:.86em}
"""


# ------------------------------------------------------------------ ตัวช่วยอ่าน README
def st(n):
    return "ขั้นที่ %d ·" % n


def heading(n):
    for s in SECS:
        if s["text"].startswith(st(n)):
            return s["text"][len(st(n)):].strip()
    raise KeyError(n)


def real(n):
    return " ".join(para(st(n), "**ผลจริง**")["lines"])


def real_short(n):
    return real(n).replace("**ผลจริง**", "").strip(" :")


def howread(n):
    bl = sec(st(n))
    for k, b in enumerate(bl):
        if b["t"] == "p" and b["lines"][0].startswith("**อ่านผลอย่างไร**"):
            return bl[k + 1]["items"]
    raise KeyError(n)


def rows(prefix, head0):
    return table(prefix, head0)["rows"]


def ttag(n):
    m = re.search(r"\(([^)]*)\)", real(n))
    return m.group(1) if m else "README"


# ------------------------------------------------------------------ ชิ้นส่วนของเด็คนี้
def img(src, alt):
    return E.img_tag({"t": "img", "src": src, "alt": alt})


def side_html(points=None, tiles_=None, pre="", post="", tone=None):
    out = pre
    if tiles_:
        out += tiles(tiles_)
    for k, p in enumerate(points or []):
        t = (tone or {}).get(k, "")
        out += '<div class="pt %s">%s</div>' % (t, md(p))
    return out + post


def ptrow(points, tone=None):
    if not points:
        return ""
    return '<div class="ptrow" style="--n:%d">%s</div>' % (len(points), "".join(
        '<div class="pt %s">%s</div>' % ((tone or {}).get(k, ""), md(p)) for k, p in enumerate(points)))


def px(title, src, points=None, tiles_=None, pre="", post="", tag="", tone=None, cap="", wide=False):
    """ภาพใหญ่ราว 2 ใน 3 ของหน้า + ประเด็น/ตัวเลขด้านขวา · wide=True สำหรับภาพกว้าง: ภาพเต็มความกว้าง ตัวเลขและประเด็นเรียงด้านล่าง"""
    if wide:
        body = ('<div class="fig" style="--figmin:220px">%s</div>' % img(src, E.plain(title)) + pre + (tiles(tiles_) if tiles_ else "")
                + ptrow(points, tone) + post + ('<p class="cap">%s</p>' % md(cap) if cap else ""))
        return S(title, body, tag=tag, maxfs=1.2)
    body = '<div class="ex big"><div class="fig">%s</div><div class="side fitbox">%s</div></div>' % (
        img(src, E.plain(title)), side_html(points, tiles_, pre, post, tone))
    if cap:
        body += '<p class="cap">%s</p>' % md(cap)
    return S(title, body, tag=tag, maxfs=1.25)


def chart(title, chart_html, points=None, tag="", tone=None, post="", pre="", wide=False):
    """แผนภูมิที่วาดจากค่าใน README + ประเด็นด้านขวา · wide=True: แผนภูมิเต็มความกว้าง ประเด็นเรียงด้านล่าง"""
    if wide:
        return S(title, pre + chart_html + ptrow(points, tone) + post, tag=tag, maxfs=1.3)
    body = '<div class="ex chart"><div class="fig" style="flex:1.7 1 0;min-height:0">%s</div><div class="side fitbox">%s</div></div>' % (
        chart_html, side_html(points, None, pre, post, tone))
    return S(title, body, tag=tag, maxfs=1.3)


def chartw(*a, **k):
    return chart(*a, wide=True, **k)


def bleed(src, kick, sentence, sub=""):
    """ภาพถ่ายเต็มหน้า + ประโยคเดียวบนแถบล่าง"""
    raw = '<div class="band"><div class="k">%s</div><div class="s">%s</div>%s</div><div class="imgnote" style="bottom:auto;top:14px">ภาพจำลอง</div>' % (
        md(kick), md(sentence), '<div class="s2">%s</div>' % md(sub) if sub else "")
    return {"raw": raw, "cls": "bleed", "style": ' style="background-image:url(%s)"' % src,
            "title": E.plain(sentence)[:90], "kicker": "", "tag": "", "lead": ""}


def pair(title, a, b, cap="", tag="", rows_=False, cls=("", "after"), tall=False):
    """ก่อน/หลัง · a, b = (ป้ายสั้น, ป้ายยาว, ภาพ)"""
    def pc(d, c):
        return '<div class="pc %s"><div class="pl"><span>%s</span>%s</div><div class="fig">%s</div></div>' % (c, d[0], md(d[1]), img(d[2], E.plain(d[1])))
    body = '<div class="pair %s">%s%s</div>' % (("rows" if rows_ else "") + (" tall" if tall else ""), pc(a, cls[0]), pc(b, cls[1]))
    if cap:
        body += '<p class="cap">%s</p>' % md(cap)
    return S(title, body, tag=tag, maxfs=1.2)


def hbars(rws, legend=""):
    """แท่งแนวนอน สีตามสถานะ · rws = [(ป้าย, คำอธิบายย่อย, ค่า, ค่าสูงสุด, ข้อความขวา, โทน ok|bad|n|grey|teal)]"""
    out = []
    for lb, sub, v, mx, txt, tone in rws:
        w = 100.0 * v / mx if mx else 0
        rc = "bad" if tone == "bad" else "grey" if tone == "grey" else ""
        out.append('<div class="r %s"><div class="lb">%s%s</div><div class="tr"><div class="fl t-%s" style="width:%.1f%%"></div></div>'
                   '<div class="vl">%s</div></div>' % (rc, md(lb), "<small>%s</small>" % md(sub) if sub else "", tone, w, md(txt)))
    return '<div class="hb">%s</div>%s' % ("".join(out), legend)


def stack(rws, legend=""):
    """แท่งซ้อน · rws = [(ป้าย, คำอธิบายย่อย, [(จำนวน, โทน)], ข้อความขวา)] · ทุกส่วนมีตัวเลขในแท่ง"""
    out = []
    for lb, sub, parts_, txt in rws:
        tot = sum(p[0] for p in parts_)
        segs = "".join('<div class="fl t-%s" style="width:%.2f%%">%s</div>' % (t, 100.0 * n / tot, n) for n, t in parts_ if n)
        out.append('<div class="r"><div class="lb">%s%s</div><div class="tr">%s</div><div class="vl">%s</div></div>'
                   % (md(lb), "<small>%s</small>" % md(sub) if sub else "", segs, md(txt)))
    return '<div class="hb stack">%s</div>%s' % ("".join(out), legend)


def legend(items):
    return '<div class="lgd">%s</div>' % "".join('<span><i class="t-%s"></i>%s</span>' % (t, md(x)) for t, x in items)


def gauge(rws):
    """แท่งเทียบเกณฑ์ · rws = [(ป้าย, คำอธิบายย่อย, ค่า, ค่าสูงสุดของสเกล, เกณฑ์, ป้ายเกณฑ์, ข้อความขวา, โทน)]"""
    out = []
    for lb, sub, v, mx, thr, thl, txt, tone in rws:
        rc = "bad" if tone == "bad" else ""
        out.append('<div class="r %s"><div class="lb">%s<small>%s</small></div><div class="tr"><div class="fl t-%s" style="width:%.1f%%"></div>'
                   '<div class="thr" style="left:%.1f%%"><b>%s</b></div></div><div class="vl">%s</div></div>'
                   % (rc, md(lb), md(sub), tone, 100.0 * v / mx, 100.0 * thr / mx, thl, md(txt)))
    return '<div class="hb gauge" style="gap:1.05em;padding-top:.6em">%s</div>' % "".join(out)


# ---- DAG ของแผน sitesafe (ตำแหน่งในกรอบ 1400 x 560 · ความสัมพันธ์จากคอลัมน์ "รอบล็อกใด" ของ README)
POS = {"B01": (0, 165), "B09": (0, 475), "B05": (290, 10), "B02": (290, 165), "B06": (290, 320), "B07": (290, 475),
       "B03": (580, 165), "B08": (870, 165), "B04": (870, 360), "B10": (1160, 165)}
CP = ["B01", "B02", "B03", "B08", "B10"]
NW, NH = 220, 135


def plan_rows():
    return {r[0]: r for r in rows(st(4), "บล็อก")}


def deps(r):
    d = r[4].strip()
    if d in ("–", "-", ""):
        return []
    m = re.match(r"B(\d+)–B(\d+)$", d)
    if m:
        return ["B%02d" % k for k in range(int(m.group(1)), int(m.group(2)) + 1)]
    return re.findall(r"B\d+", d)


def dag(status=None, note_=None):
    """status = {บล็อก: (คลาส ok|bad|grey|res|"", ข้อความสถานะ)} · ไม่ส่ง = แผน (เน้น Critical Path)"""
    pr = plan_rows()
    lines = []
    for b, r in pr.items():
        for d in deps(r):
            if d not in POS:
                continue
            x1, y1 = POS[d][0] + NW, POS[d][1] + NH / 2
            x2, y2 = POS[b][0], POS[b][1] + NH / 2
            cp = d in CP and b in CP and CP.index(b) == CP.index(d) + 1
            col = "#e87f1c" if cp else "#a9b6c8"
            if status and status.get(d, ("",))[0] in ("bad", "grey"):
                col = "#c9d1dc" if not cp else "#e8b98c"
            mx = (x1 + x2) / 2
            ah = 14 if cp else 10
            lines.append('<path d="M%d %d C%d %d %d %d %d %d" fill="none" stroke="%s" stroke-width="%s"/>'
                         '<polygon points="%d,%d %d,%d %d,%d" fill="%s"/>'
                         % (x1, y1, mx, y1, mx, y2, x2 - ah, y2, col, 6 if cp else 2.5,
                            x2 - ah, y2 - ah / 2, x2, y2, x2 - ah, y2 + ah / 2, col))
    svg = ('<svg viewBox="0 0 1400 620" preserveAspectRatio="none">'
           '%s</svg>') % "".join(lines)
    nodes = []
    for b, (x, y) in POS.items():
        r = pr[b]
        if status:
            c, s = status.get(b, ("", ""))
        else:
            c = "cp" if b in CP else ""
            s = "%s · %s" % (r[2], r[3])
        nodes.append('<div class="nd %s" style="left:%.2f%%;top:%.2f%%"><b>%s</b>%s<br><span class="st">%s</span></div>'
                     % (c, 100.0 * x / 1400, 100.0 * y / 620, b, md(r[1]), md(s)))
    return '<div class="dag w">%s%s</div>%s' % (svg, "".join(nodes), note_ or "")


# ---- หน้าคั่นของขั้น พร้อมแถบตำแหน่ง
PHASE = {1: "ระยะ A · Requirement", 2: "ระยะ A · Requirement", 3: "ระยะ A · Requirement", 4: "ระยะ B · Planning",
         5: "ระยะ C · Build · Train · Deploy", 6: "ระยะ C · Build · Train · Deploy", 7: "ระยะ C · Build · Train · Deploy",
         8: "ระยะ C · Build · Train · Deploy", 9: "ระยะ C · Build · Train · Deploy", 10: "ระยะ D · Verification",
         11: "ระยะ D · Verification", 12: "ระยะ D · Verification", 13: "ระยะ D · Verification", 14: "ระยะ D · Verification",
         15: "ปิดท้าย · สกิลเวอร์ชัน 0", 16: "ปิดท้าย · สกิลเวอร์ชัน 0"}


def strip(n):
    return '<div class="strip">%s<span>%s · ขั้นที่ %d จาก 16</span></div>' % (
        "".join('<i class="%s"></i>' % ("cur" if k == n else "done" if k < n else "") for k in range(1, 17)), PHASE[n], n)


def divider(n, extra="", lead=""):
    res = real_short(n) + (" · " + extra if extra else "")
    sub = strip(n) + ("<p>%s</p>" % md(lead) if lead else "") + "<p>%s</p>" % md("ผลจริงของผู้สอน: " + res)
    return E.divider("ขั้นที่ %d" % n, heading(n), sub)


def prompt_slides(n, short):
    return E.prompt_slides(E.prompt_code(st(n), 0, HOW), CTX["kicker"], "ขั้นที่ %d · %s" % (n, short))


NOTE_AI = "ผลของคุณอาจต่างจากของผู้สอนได้ เพราะทีม AI เขียนเอกสารและโค้ดเองทุกครั้ง สิ่งที่ต้องตรงคือ **ไฟล์ที่ได้** และ **วิธีตัดสินผล**"


def check(n, short, items, ref, note_text=NOTE_AI):
    return E.check_slide("step%d" % n, items, "ผลของผู้สอน: " + ref, note_text, "ขั้นที่ %d · %s" % (n, short))


def step(n, kicker_phase):
    CTX.update(kicker="%s · ขั้นที่ %d จาก 16" % (kicker_phase, n), group="ขั้นที่ %d · %s" % (n, heading(n)))


def N2(key):
    return "img/%s.png" % key if os.path.exists("img/%s.png" % key) else "img/%s.jpg" % key


def roadmap():
    t = rows("16 ขั้น", "ระยะ")
    groups, cur = [], None
    for r in t:
        if r[0].strip():
            cur = [r[0], []]
            groups.append(cur)
        cur[1].append((r[1], r[2]))
    colors = ["#0f8f8c", "#e87f1c", "#7c4dca", "#15803d", "#12305e"]
    out = []
    for g, c in zip(groups, colors):
        nums = "".join('<div class="dot">%s</div>' % k for k, _ in g[1])
        names = "".join("<div><b>%s</b> %s</div>" % (k, md(x)) for k, x in g[1])
        out.append('<div class="ph" style="--n:%d;--c:%s"><div class="h">%s</div><div class="dots">%s</div><div class="nm">%s</div></div>'
                   % (max(len(g[1]), 2.6), c, md(g[0]), nums, names))
    return '<div class="rmline"></div><div class="rm">%s</div>' % "".join(out)


def build():
    # ===== 1 · เปิด
    CTX.update(kicker="", group="เริ่มต้น")
    add(E.cover("SiteSafe Inspect", "บริการตรวจอุปกรณ์ความปลอดภัยจากภาพหน้างาน ส่งมอบด้วย Agent Team ตั้งแต่บันทึกสัมภาษณ์ถึงรายงานส่งมอบ",
                "image/cover.jpg", small="สัปดาห์ที่ 3 · Agent Team End-to-End · หัวข้อที่ 1"))
    CTX["kicker"] = "ภาพรวมของหัวข้อ"
    f1 = FIG["n01-four-phases"]
    add(px("ทีม AI สร้างระบบครบ 10 บล็อก แต่ผลทดสอบตัดสินว่ายังส่งมอบไม่ได้", "img/n01-four-phases.jpg", [
        "งานเดินผ่าน 4 ระยะ ตั้งแต่บันทึกการสัมภาษณ์ไฟล์เดียวจนถึงรายงานส่งมอบ",
        "คนอนุมัติ 2 จุด คือ ก่อนรันทีมจริง และก่อนเช่าเครื่อง GPU",
        "ผลสุดท้ายคือ **ยังส่งมอบไม่ได้** พร้อมรายการที่ต้องแก้",
    ], tone={2: "bad"}))
    add(S("หัวข้อนี้มี 16 ขั้น และทุกขั้นคือ 1 พรอมต์", roadmap() +
          '<p class="cap">ก่อนเริ่ม LAB มีภาคพื้นฐาน: เรื่องราวของลูกค้า การสัมภาษณ์ Dataset โมเดล และระบบที่จะส่งมอบ</p>', cls="mid", maxfs=1.3))
    add(S("วิธีใช้สไลด์ชุดนี้", cards([
        ("เลื่อนหน้า", '<p>กด <span class="kbd">→</span> หรือ <span class="kbd">Space</span> เพื่อไปหน้าถัดไป และ <span class="kbd">←</span> เพื่อย้อนกลับ</p>'),
        ("สารบัญและเต็มจอ", '<p>กด <span class="kbd">O</span> เพื่อเปิดสารบัญ กด <span class="kbd">F</span> เพื่อเต็มจอ และคลิกภาพเพื่อขยาย</p>'),
        ("คัดลอกพรอมต์", "ปุ่ม **คัดลอกพรอมต์ทั้งหมด** คัดลอกพรอมต์ตรงตัวอักษรกับ README"),
        ("ตรวจผลของคุณ", "หน้า **ตรวจผลของคุณ** ติ๊กได้ และมีผลของผู้สอนให้เทียบ"),
    ], 2), cls="mid"))

    # ===== 2 · ภาคพื้นฐาน
    CTX.update(kicker="", group="เรื่องราวของลูกค้า")
    story = sec("1 · เรื่องราวของลูกค้า")
    ps = [b for b in story if b["t"] == "p"]
    add(E.divider("ปัญหา", "เรื่องราวของลูกค้า", "<p>%s</p><p>%s</p>" % (md(ps[0]["lines"][0]), md("เช้าและบ่าย: " + ps[2]["lines"][0])),
                  "image/s1-walk.jpg", small="ภาคพื้นฐาน"))
    add(bleed("image/s2-overload.jpg", "เย็น: ผู้จัดการความปลอดภัยเปิดดูทีละรูป", ps[4]["lines"][0]))
    add(bleed("image/s3-miss.jpg", "ผลที่ตามมา", ps[6]["lines"][0]))
    q = ps[7]["lines"][0].replace("**", "").replace("คำถามของหัวข้อนี้: ", "")
    add(bleed(N2("p21-question"), "คำถามของหัวข้อนี้", q))

    CTX.update(kicker="ภาคพื้นฐาน · การสัมภาษณ์ลูกค้า", group="การสัมภาษณ์ลูกค้า")
    add(bleed("image/s4-interview.jpg", "การสัมภาษณ์ลูกค้า", sec("2 · การสัมภาษณ์ลูกค้า")[1]["lines"][0],
              "บันทึกฉบับเต็ม: [INTERVIEW.md](INTERVIEW.md)"))
    t = table("2 · การสัมภาษณ์ลูกค้า", "")
    people = []
    for r in t["rows"]:
        src = re.search(r'src="([^"]+)"', r[0]).group(1)
        name, role = r[1].split("<br>")
        quotes = "".join("<li>%s</li>" % md(x) for x in r[2].split("<br>"))
        people.append((name.replace("**", ""), '<div class="who"><img src="%s" alt="%s" style="width:110px;height:110px;border-radius:50%%;'
                       'object-fit:cover;float:left;margin:0 14px 6px 0"><p><b>%s</b></p></div><ul style="clear:both">%s</ul>'
                       % (src, "ภาพจำลอง " + name.replace("**", ""), md(role), quotes)))
    add(S("ลูกค้า 3 คนพูดถึงระบบเดียวกันจากคนละมุม", cards(people, 3) + '<p class="cap">ภาพบุคคลเป็นภาพจำลอง</p>', tag="INTERVIEW.md"))
    obs = " ".join(para("2 · การสัมภาษณ์ลูกค้า", "**สังเกต:**")["lines"]).replace("**สังเกต:** ", "").split(" · บันทึกฉบับเต็ม")[0]
    add(px("ความต้องการ 3 ข้อดึงระบบเดียวไปคนละทาง", N2("n21-conflict"), [
        obs,
        "ขั้นที่ 1 และ 2 จะบันทึกความขัดกันนี้เป็นคำถามและข้อสมมติ ไม่ให้ AI ตัดสินแทนลูกค้า",
    ]))

    CTX.update(kicker="ภาคพื้นฐาน · ข้อมูลและโมเดล", group="Dataset และโมเดล")
    lab = para(st(7), "label 1 บรรทัด")["lines"][0]
    know = " ".join(para(st(7), "**รู้จัก Dataset**")["lines"]).replace("**รู้จัก Dataset** · ", "")
    add(px("Dataset คือภาพหน้างานก่อสร้างที่มีกรอบระบุวัตถุ 10 คลาส", "img/c01-dataset.jpg", [
        know,
        lab,
    ], cap="ส่วนหนึ่งของภาพตัวอย่างจริง · ภาพเต็ม: [results/dataset_samples.jpg](results/dataset_samples.jpg)", tag="ขั้นที่ 7"))
    model = " ".join(para(st(8), "**รู้จักโมเดล**")["lines"]).replace("**รู้จักโมเดล** · ", "").split(" · ")
    add(px("YOLO11s รับภาพ แล้วตอบเป็นกรอบ ชื่อคลาส และค่าความมั่นใจ", N2("n22-yolo-io"), [
        "%s เป็น%s" % (model[0], model[1]),
        "Requirement ใช้เพียง 2 คลาส: `NO-Hardhat` ให้ค่า H และ `NO-Safety Vest` ให้ค่า V",
        "เว็บนำค่า H และ V ของแต่ละรูปไปตัดสินผลตาม Business Rule",
    ], tag="ขั้นที่ 8"))

    CTX.update(kicker="ภาคพื้นฐาน · ระบบที่จะส่งมอบ", group="ระบบที่จะส่งมอบ")
    sysr = rows("ภาพรวมระบบ", "ส่วน")
    add(fig("ระบบมี 2 ฝั่ง: เว็บอยู่บนเครื่องของเรา งานตรวจภาพอยู่บนเครื่อง GPU ที่เช่า", "image/architecture.png",
            "แต่ละส่วนต่อยอดจากบทเรียนก่อนหน้า: " + " · ".join("%s จาก %s" % (r[0], r[2]) for r in sysr)))
    who = rows("ใครทำอะไร", "ผู้ทำ")
    add(px("คนตัดสินใจ หัวหน้าทีมสั่งงาน และทีม AI เขียนโค้ด", N2("n23-roles"),
           ["**%s**: %s" % (r[0], r[1]) for r in who], tone={0: "warn"}))

    # ===== 3 · ภาค LAB
    CTX.update(kicker="", group="ภาค LAB")
    add(E.divider("ภาค LAB", "16 ขั้น 16 พรอมต์", "<p>เริ่มจากบันทึกการสัมภาษณ์ไฟล์เดียว โค้ดทุกไฟล์ทีม AI เขียนเอง</p>", small="SiteSafe Inspect"))
    CTX["kicker"] = "ภาค LAB · ก่อนเริ่ม"
    add(px("ก่อนเริ่ม ให้เตรียมโฟลเดอร์ Claude Code container และเครื่องมือทดสอบ", N2("n24-setup"), [
        "เริ่มจากโฟลเดอร์ที่มีเพียง `INTERVIEW.md` และไฟล์ `.env` เอกสารและโค้ดทุกไฟล์เกิดจากพรอมต์",
        "เปิด Claude Code ที่โฟลเดอร์ `01_sitesafe_inspect` พรอมต์ทั้งหมดอยู่ใน [PROMPTS.md](PROMPTS.md)",
        "container `multi-account` มีบัญชี `yolo2` `yolo3` `cyolo1` (และ `yolo1` ในขั้นที่ 6) กับสกิล dag-planner, agent-team และ vastai",
    ]))

    # ---------- ระยะ A
    CTX.update(kicker="", group="ระยะ A · Requirement")
    add(E.divider("ระยะ A", "จากคำพูดเป็น Requirement", "<p>ขั้นที่ 1–3: ลูกค้าพูดว่าอะไร ใครต้องการอะไร ระบบต้องทำอะไร และระบบมีส่วนใดบ้าง</p>",
                  "image/s4-interview.jpg", small="ภาค LAB"))
    CTX["kicker"] = "ภาค LAB · ระยะ A · Requirement"
    tr = rows("3 · ระยะ A", "ลำดับ")
    add(px("ทุก Requirement ต้องย้อนกลับถึงคำพูดของลูกค้าได้", N2("n25-trace"),
           ["%s ตอบว่า%s: ผลจริง **%s**" % (re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", r[1]), r[2], r[3]) for r in tr]))
    add(pair("ตัวอย่างจริง 1 เส้นทาง: คำพูดของคุณวิชัยกลายเป็น BR-01 ถึง BR-03",
             ("① → ②", "คำพูดในการสัมภาษณ์ → User Story US-03", "img/c04a-trace.jpg"),
             ("③ → ④", "Requirement BR-01 ถึง BR-03 → สิ่งที่ System Design ต้องมี", "img/c04b-trace.jpg"),
             cap="แถวบนสุดของแผนภาพจริง ตัดเป็น 2 ช่วง · ภาพเต็ม 3 เส้นทาง: [image/trace.png](image/trace.png)",
             rows_=True, tall=True, cls=("", "")))

    # ขั้นที่ 1
    PA = "ภาค LAB · ระยะ A"
    step(1, PA)
    us = rows(st(1), "รายการ")
    add(divider(1, " · ".join("%s %s" % (r[0], r[1]) for r in us[:3])))
    ex = next(b for b in sec(st(1)) if b["t"] == "alert")
    exl = ex["blocks"][0]["lines"] if ex["blocks"][0]["t"] == "p" else []
    add(px("User Story ทุกข้ออ้างคำพูดของลูกค้า เช่น US-03 อ้างคำพูดของคุณวิชัยตรงตัว", "img/n02-user-story.jpg",
           pre='<div class="lead2">ตัวอย่างจริงจาก docs/USER-STORIES.md</div>' + E.render(ex), points=[
               "จุดที่ลูกค้าพูดขัดกัน และคำถามที่ต้องถามเพิ่ม แยกเป็น 2 ตารางท้ายไฟล์"]))
    add(prompt_slides(1, "User Story"))
    add(check(1, "User Story", [
        "มีไฟล์ `docs/USER-STORIES.md`",
        "ทุก User Story อยู่ในรูป **ในฐานะ… ฉันต้องการ… เพื่อ…** มีรหัส US-01… ระดับ Must / Should / Could และเกณฑ์ยอมรับ",
        "ทุกข้ออ้างคำพูดในบันทึกการสัมภาษณ์ที่เป็นที่มา",
        "ท้ายไฟล์มี 2 ตาราง: จุดที่ลูกค้าพูดขัดกันเอง และคำถามที่ต้องถามลูกค้าเพิ่ม",
        "มีหัวข้อ **นอกขอบเขต** และยังไม่มีการออกแบบระบบหรือโค้ด",
    ], " · ".join("%s %s" % (r[0], r[1]) for r in us)))
    h1 = howread(1)
    add(chart("ผลจริง: User Story 20 ข้อ ไม่มีข้อระดับ Could และพบคำถามถึงลูกค้า 14 ข้อ", hbars(
        [(r[0], "", int(r[1]), 20, r[1], "n") for r in us[:3]] + [(r[0], "", int(r[1]), 20, r[1], "warn") for r in us[3:]]),
        h1, tag=ttag(1)))

    # ขั้นที่ 2
    step(2, PA)
    add(divider(2))
    add(px("Business Rule ต้องมีเส้นแบ่งที่ตรวจได้ ทั้งต่ำกว่า เท่ากับ และสูงกว่า", "img/n03-boundary.jpg", [
        "กติกาเขียนเป็นตัวเลข: **H** = จำนวนคนไม่ใส่หมวก และ **V** = จำนวนคนไม่ใส่เสื้อสะท้อนแสง",
        "ลูกค้าไม่ได้บอกว่าพอดี 2 คนเป็นอะไร AI เลือกทางที่เสี่ยงน้อยที่สุด คือ V = 2 → **ไม่ผ่าน** และจดเป็นข้อสมมติ",
        "ข้อสมมติทุกข้อต้องให้ลูกค้ายืนยัน เช่น คุณวิชัยต้องยืนยัน BR-02",
    ]))
    add(prompt_slides(2, "Requirement"))
    add(check(2, "Requirement", [
        "มีไฟล์ `docs/REQUIREMENTS.md` แยก FR · BR · NFR และทุก FR อ้างรหัส User Story",
        "ทุก BR เป็นตัวเลข มีค่าตัวอย่าง **ต่ำกว่า / เท่ากับ / สูงกว่า** เส้นแบ่ง",
        "NFR มีอย่างน้อย 5 เรื่อง: เกณฑ์ของโมเดล · SLO ของเวลารอผล · ความจุ 3 ไซต์ · รูปห้ามหาย · ความเป็นส่วนตัวของรูป",
        "เกณฑ์ของโมเดลเขียนเป็นตัวชี้วัดที่วัดได้บน Test Set",
        "จุดที่ลูกค้าขัดกันถูกบันทึกเป็น **ข้อสมมติ** พร้อมเหตุผล",
    ], real_short(2)))
    m = re.findall(r"(FR|BR|NFR) (\d+) ข้อ|ข้อสมมติ (\d+) ข้อ", real(2))
    h2 = howread(2)
    add(px("ผลจริง: Requirement 3 ชนิด และข้อสมมติ 14 ข้อที่ต้องให้ลูกค้ายืนยัน", N2("n27-req-kinds"), tiles_=[
        ("FR · ระบบต้องทำอะไรได้", m[0][1], "ข้อ", ""), ("BR · กติกาเป็นตัวเลข", m[1][1], "ข้อ", ""),
        ("NFR · ต้องดีแค่ไหน", m[2][1], "ข้อ", ""), ("ข้อสมมติ", m[3][2], "ข้อ · ต้องให้ลูกค้ายืนยัน", "warn")],
        post=note(h2[2], label="ข้อสมมติ"), tag=ttag(2)))
    add(tbl("BR ทุกข้อมีค่าตัวอย่างต่ำกว่า เท่ากับ และสูงกว่าเส้นแบ่ง", next(b for b in walk(sec(st(2))) if b["t"] == "table" and len(b["head"]) == 5),
            pre='<p class="cap">H = จำนวนคนไม่ใส่หมวก · V = จำนวนคนไม่ใส่เสื้อสะท้อนแสง</p>'))
    nfr = next(b for b in walk(sec(st(2))) if b["t"] == "table" and b["head"][1] == "เรื่อง")
    add(px("คำว่า \"10 รูปต้องจับได้ 8 รูป\" กลายเป็น Image-level Recall ≥ 0.80", N2("n26-recall"), [
        h2[0],
        "**%s %s**: %s" % (nfr["rows"][0][0], nfr["rows"][0][1], nfr["rows"][0][2]),
    ], tag="docs/REQUIREMENTS.md"))
    fr = rows(st(2), "รหัส")
    add(S("ตัวอย่าง FR และ NFR: ระบบต้องทำอะไรได้ และต้องดีแค่ไหน", cards(
        [("%s · จาก %s" % (r[0], r[2]), r[1]) for r in fr] + [("%s · %s" % (r[0], r[1]), r[2], "navy") for r in nfr["rows"]], 3) +
        '<p class="cap">FR ตัวอย่าง 3 จาก 22 ข้อ (แถวบน) · NFR 3 จาก 8 ข้อ (แถวล่าง)</p>', tag="docs/REQUIREMENTS.md", cls="mid"))

    # ขั้นที่ 3
    step(3, PA)
    add(divider(3))
    rd = rows(st(3), "Requirement")
    add(px("System Design: Requirement แต่ละข้อมีส่วนของระบบที่รับผิดชอบ", "image/gen-arch.png",
           ["**%s**: %s" % (r[0], r[1]) for r in rd], tag="docs/DESIGN.md"))
    add(prompt_slides(3, "System Design และข้อมูลทดสอบ"))
    add(check(3, "System Design และข้อมูลทดสอบ", [
        "มีไฟล์ `docs/DESIGN.md` และ `docs/TEST-DATA.md`",
        "`DESIGN.md` มีแผนภาพ Mermaid 4 ภาพ: Architecture · ER Diagram · ลำดับการทำงาน · สถานะของงาน",
        "มี API Contract: ส่งรูป · ถามสถานะ · คิวเต็มตอบอย่างไร · ใช้ API key อย่างไร",
        "มีโหมด `BUG_MODE=1` และรายชื่อบั๊ก 3 ข้ออยู่ที่ `docs/BUGS-SECRET.md` ที่เดียว",
        "ข้อมูลทดสอบมีกรณีขอบของทุก Business Rule พร้อมผลที่คาดหวัง",
    ], real_short(3), NOTE_AI + " · อย่าเปิด `BUGS-SECRET.md` จนถึงขั้นที่ 13"))
    m = re.findall(r"(\d+)", real_short(3))
    h3 = howread(3)
    add(S("ผลจริง: ออกแบบเสร็จโดยยังไม่มีโค้ดสักบรรทัด และยังมีคำถาม 8 ข้อที่ต้องวัดจริง", tiles([
        ("ตารางในฐานข้อมูล", m[1], "", ""), ("API", m[2], "", ""), ("ข้อมูลทดสอบ", m[3], "แถว", ""),
        ("คำถามที่การออกแบบยังตอบไม่ได้", m[4], "ข้อ", "warn")]) + note(h3[2], label="ตัวอย่างคำถาม"), tag=ttag(3), cls="mid"))
    add(fig("งาน 1 งานมี 4 สถานะ และทุกเส้นทางจบที่ เสร็จแล้ว หรือ ตรวจไม่สำเร็จ", "image/gen-state.png",
            "ดูเส้นที่ย้อนกลับ: Worker ล่มกลางงาน งานกลับเข้าคิว · " + h3[0]))
    add(px("โหมดจำลองฝั่ง AI ทำให้ทดสอบ Business Rule ได้โดยไม่ต้องเช่า GPU", N2("n28-mock"), [
        h3[1],
        "ขั้นที่ 6 และ 12 จะแสดงว่าการทดสอบด้วยตัวจำลองยังไม่ใช่การพิสูจน์บน GPU จริง",
    ], tag="อ่านผล · README"))

    # ---------- ระยะ B
    PB = "ภาค LAB · ระยะ B"
    CTX.update(kicker="", group="ระยะ B · Planning")
    step(4, PB)
    add(divider(4, lead=para("4 · ระยะ B", "เอกสารของระยะ A")["lines"][0]))
    h4 = howread(4)
    add(chartw("DAG ของแผน: 10 บล็อก และ Critical Path ผ่าน B03 ที่ใช้สกิล review", dag(), [
        "เส้นสีส้มคือ " + h4[1],
        h4[0],
        "ขนาด S 15 นาที · M 30 นาที · L 45 นาที · บัญชี yolo2, yolo3, cyolo1 · **วางแผนเท่านั้น ห้ามรันจริง**",
    ], tag="plan/dag.png"))
    add(prompt_slides(4, "แตกงานเป็นบล็อก วาด DAG และ Gantt"))
    add(check(4, "DAG และ Gantt", [
        "โฟลเดอร์ `plan/` มีไฟล์บล็อก ภาพ DAG ภาพ Gantt และไฟล์แผน",
        "งานครอบคลุม: โครงโปรเจกต์ · ฐานข้อมูล · gateway กับคิว · GPU Worker · Training และ Evaluation · หน้าเว็บ · โลโก้ · รวมระบบ",
        "มี 1 บล็อกที่ใช้สกิล `review` และทุกบล็อกได้บัญชีที่อนุญาต",
        "รายงานบอก Critical Path และเวลารวมของแผน",
        "ยังไม่มีการรันทีมจริง",
    ], real_short(4)))
    m = re.findall(r"([\d.]+)", real_short(4))
    add(px("ผลจริง: แผน 10 บล็อก ใช้เวลารวมประมาณ 112.5 นาที และ yolo3 ไม่ได้งาน", "plan/gantt-plan.png", wide=True, tiles_=[
        ("จำนวนบล็อก", m[1], "", ""), ("Critical Path", m[2], "ล้านโทเคน", ""), ("เวลารวมของแผน", m[3], "นาที (ประมาณ)", "")],
        points=[h4[2], h4[3]], tag=ttag(4), cap="แต่ละแถวคือบัญชี และแต่ละแท่งคือบล็อก · ภาพจริง plan/gantt-plan.png"))

    # ---------- ระยะ C
    PC = "ภาค LAB · ระยะ C"
    CTX.update(kicker="", group="ระยะ C · Build · Train · Deploy")
    add(E.divider("ระยะ C", "สร้างระบบ เทรนโมเดล และเปิดบริการ", "<p>ขั้นที่ 5–9: ทีม AI เขียนโค้ด เช่า GPU เทรนโมเดล และ Deployment</p>",
                  "img/s01-build.jpg", small="ภาค LAB"))
    step(5, PC)
    add(divider(5))
    add(px("ทีม AI รันแผนเดิมจริง แล้วรายงานแผนเทียบของจริงตามจริง", N2("n30-run-team"), [
        "ใช้แผน sitesafe ที่มีอยู่แล้ว **ห้ามวางแผนใหม่** และคนอนุมัติให้รันจริง",
        "รันด้วยบัญชี yolo2, yolo3, cyolo1 แล้วคัดลอกโค้ดมาไว้ที่ `./app`",
        "บล็อกที่ล้มหรือถูกบล็อกต้อง **รายงานตามจริง ห้ามเขียนโค้ดแทนทีม**",
    ]))
    add(prompt_slides(5, "Agent Team สร้างระบบตามแผน"))
    add(check(5, "Agent Team สร้างระบบ", [
        "โฟลเดอร์ `app/` มีไฟล์ที่ทีมสร้าง",
        "`plan/REPORT.md` มีตาราง แผนเทียบของจริง ทุกบล็อก: บัญชี · นาที · โทเคน · สถานะ",
        "มีภาพ Gantt ของจริง และภาพเทียบแผนใน `plan/`",
        "บล็อกที่ล้มหรือถูกบล็อกถูกรายงานตามจริง ไม่มีโค้ดที่หัวหน้าทีมเขียนแทน",
    ], real_short(5)))
    r5 = rows(st(5), "บล็อก")
    m = re.findall(r"([\d,]+)", real_short(5))
    add(px("รอบแรกเสร็จ 6 จาก 10 บล็อก: B03 ไม่ผ่านการตรวจ และอีก 3 บล็อกที่รอ B03 ไม่ได้รัน", "image/compare-run1.png", wide=True, tiles_=[
        ("เสร็จ", "6/10", "บล็อก", ""), ("ไม่ผ่านการตรวจ", "1", "บล็อก (B03)", "bad"), ("ถูกบล็อก", "3", "บล็อก (B04 B08 B10)", "bad"),
        ("เวลาจริง · โทเคน", m[0] + " นาที", m[1] + " โทเคน", "")],
        cap="ซ้าย: แผน 112.5 นาที · ขวา: ของจริง 39.2 นาที · แถวที่ขึ้นคำว่า **blocked** คือบล็อกที่ไม่ได้รัน", tag="plan/REPORT.md"))
    tok = [(r[0], r[6].replace("**", ""), int(r[5].replace(",", "")), r[5]) for r in r5]
    mx = max(x[2] for x in tok)
    h5 = howread(5)

    def tone5(s, v):
        return "bad" if "ไม่ผ่าน" in s else "grey" if not v else "n"
    add(chart("B03 ที่ไม่ผ่านการตรวจ ใช้โทเคน 803,710 จาก 1,333,708 ของรอบแรก", hbars(
        [(a, s, v, mx, t if v else "0", tone5(s, v)) for a, s, v, t in tok],
        legend([("n", "เสร็จ"), ("bad", "ไม่ผ่านการตรวจ"), ("grey", "ถูกบล็อก · ไม่ได้รัน")])),
        [h5[2], h5[0]], tone={1: "bad"}, tag="โทเคนต่อบล็อก · README"))
    st5 = {}
    for r in r5:
        b = r[0].split()[0]
        s = r[6].replace("**", "")
        st5[b] = ("bad" if "ไม่ผ่าน" in s else "grey" if "บล็อก" in s else "ok", s)
    add(chartw("บล็อกเดียวที่ไม่ผ่าน หยุดงานท้ายแผนทั้งสาย", dag(st5), [
        h5[1], h5[4], h5[3]], tone={0: "bad"}, tag="อ่านผล · README"))

    step(6, PC)
    add(divider(6, lead=para(st(6), "ทำขั้นนี้เมื่อ")["lines"][0]))
    r6 = rows(st(6), "บล็อก")
    res = {r[0].split()[0] for r in r6 if r[0].startswith("B")}
    st6 = {b: (("res", "รันต่อ · เสร็จ") if b in res else ("ok", "เสร็จ (ไม่รันซ้ำ)")) for b in POS}
    add(chartw("รันต่อเฉพาะ 4 บล็อกที่ยังไม่เสร็จ และไม่รันซ้ำ 6 บล็อกที่เสร็จแล้ว", dag(st6), [
        "รันต่อ run เดิม ไม่เริ่ม run ใหม่",
        "B03 แก้ตามข้อที่ผู้ตรวจขอในรอบล่าสุดเท่านั้น และเพิ่มรอบตรวจเป็น 3",
        "บล็อกสีเขียวเข้มคือ 4 บล็อกที่รันต่อ",
    ]))
    add(prompt_slides(6, "รันต่อเฉพาะบล็อกที่ยังไม่เสร็จ"))
    add(check(6, "รันต่อ", [
        "เป็นการรันต่อ run เดิม ไม่ใช่ run ใหม่ และบล็อกที่เสร็จแล้วไม่ถูกรันซ้ำ",
        "บล็อกที่ไม่ผ่านการตรวจแก้ตามข้อที่ผู้ตรวจขอในรอบล่าสุดเท่านั้น",
        "`plan/REPORT.md` และภาพ Gantt ของจริงถูกอัปเดต",
        "รายงานโทเคนรวมของทั้งสองรอบ",
    ], real_short(6), NOTE_AI + " · ถ้าขั้นที่ 5 เสร็จครบทุกบล็อก ให้ข้ามขั้นนี้"))
    tot = para(st(6), "โทเคนรวมของทั้งสองรอบ")["lines"][0]
    m = re.findall(r"([\d,]+)", real_short(6))
    mt = re.findall(r"\*\*([\d,]+)\*\*|ได้ไฟล์ (\d+) ไฟล์", tot)
    add(px("ผลจริง: ครบ 10 จาก 10 บล็อก แต่โทเคนรวมของสองรอบเกือบ 2.5 ล้าน", "plan/gantt-actual.png", wide=True, tiles_=[
        ("บล็อกที่เสร็จ", "10/10", "", "ok"), ("เวลารันต่อ · ไฟล์ใน `app/`", "%s นาที" % m[0], "%s ไฟล์" % mt[1][1], ""),
        ("โทเคนรันต่อ", m[1], "", ""), ("โทเคนรวมทั้งสองรอบ", mt[0][0], "รอบแรก + รันต่อ", "warn")],
        cap="Gantt ของจริงหลังรันต่อ: บล็อกทั้ง 10 บล็อกบนบัญชี cyolo1, yolo2 และ yolo3", tag="plan/REPORT.md"))
    h6 = howread(6)
    add(S("4 บล็อกที่รันต่อ: สถานะก่อนและหลัง", cards([(r[0], "%s → **%s** · %s · %s นาที" % (r[1], r[2], r[3], r[4]),
                                                          "ok" if r[2].startswith("เสร็จ") else "") for r in r6[:4]], 2) +
          note(h6[1], label="B03"), tag="README", cls="mid"))
    add(px("B10 ผ่านเทสต์ด้วยตัวตรวจจำลอง แต่ยังไม่เคยรันบน GPU จริง", N2("n28-mock"), [h6[3], h6[2]], tone={0: "warn"},
           tag="อ่านผล · README"))

    step(7, PC)
    add(divider(7))
    add(px("เช่าเครื่อง GPU 1 ใบ ดาวน์โหลด Dataset แล้วแบ่งเป็น 3 ชุด", N2("n33-rent-dataset"), [
        "เช่า RTX 3090 1 ใบ ราคาไม่เกิน $0.30 ต่อชั่วโมง และติดป้าย `e2e-sitesafe`",
        "ดาวน์โหลด construction-site-safety รุ่น 28 แล้วนับภาพและกรอบของแต่ละชุด",
        "ทำภาพตัวอย่าง 8 รูปที่วาดกรอบตาม label จริง",
    ]))
    add(prompt_slides(7, "เช่า GPU และเตรียม Dataset"))
    ds = rows(st(7), "ชุด")
    add(check(7, "เช่า GPU และเตรียม Dataset", [
        "มีเครื่องป้าย `e2e-sitesafe` 1 เครื่อง ราคาไม่เกิน $0.30 ต่อชั่วโมง และยังเปิดอยู่",
        "รายงานจำนวนภาพของ Training / Validation / Test Set และจำนวนกรอบของแต่ละคลาส",
        "มีไฟล์ `results/dataset_samples.jpg` 8 รูป พร้อมกรอบและชื่อคลาส",
        "รายงานบอกคลาสที่ใช้ตัดสินตาม Requirement",
        "ไม่มีค่า key ในข้อความใดเลย",
    ], real_short(7) + " · " + " · ".join("%s %s ภาพ" % (r[0], r[1]) for r in ds),
        "ราคาและเครื่องที่ได้ขึ้นกับตลาดในวันที่เช่า · จำนวนภาพของ Dataset ต้องตรงกัน"))
    m7 = re.search(r"(RTX 3090 1 ใบ) ราคา (\S+) ต่อชั่วโมง", real(7))
    h7 = howread(7)
    add(px("ผลจริง: RTX 3090 ราคา $0.2215 ต่อชั่วโมง แต่ Test Set มีเพียง 82 ภาพ", "results/dataset_samples.jpg", wide=True, tiles_=[
        ("GPU", m7.group(1).replace(" 1 ใบ", ""), "1 ใบ · ราคา %s ต่อชั่วโมง" % m7.group(2), "")] + [(r[0], r[1], "ภาพ · %s กรอบ" % r[2], "bad" if r[0] == "Test Set" else "") for r in ds],
        post=note(h7[1] + " · " + h7[2], label="ข้อควรระวัง"), tag=ttag(7), cap="ภาพจริง results/dataset_samples.jpg"))

    step(8, PC)
    g8 = rows(st(8), "ตัวชี้วัด")
    add(divider(8, "Acceptance Gate " + g8[4][4]))
    add(px("Acceptance Gate ต้องมีรูปใน Test Set มากพอจึงตัดสินได้", "img/n04-acceptance-gate.jpg", [
        "เลือก Confidence Threshold บน Validation Set แล้วตรึงไว้ก่อนวัดบน Test Set",
        "วัด Image-level Recall และ Precision ของคลาส \"ไม่ใส่หมวก\" เทียบกับเกณฑ์ใน Requirement",
        "เกณฑ์กำหนดรูปที่มีคนไม่ใส่หมวก **อย่างน้อย 100 รูป** แต่ Test Set จริงมี **25 รูป**",
    ]))
    add(prompt_slides(8, "เทรนโมเดล และตัดสินด้วย Acceptance Gate"))
    add(check(8, "Training และ Acceptance Gate", [
        "เทรน YOLO11s 30 Epoch ภาพขนาด 640 seed 0 ด้วยโค้ดใน `app/ai/train`",
        "รายงานบอกว่าแก้โค้ดของทีมตรงไหน (ถ้าต้องแก้)",
        "`results/model/` มีผลวัดก่อนและหลังเทรน กราฟ และภาพตัวอย่างผลตรวจ",
        "ตัดสิน Acceptance Gate ตามเกณฑ์ของโมเดลใน Requirement รวมจำนวนรูปขั้นต่ำของ Test Set",
        "น้ำหนักโมเดลที่ดีที่สุดยังอยู่บนเครื่อง GPU และเครื่องยังเปิดอยู่",
    ], "Recall 0.80 (20/25) · Precision 0.952 (20/21) · Acceptance Gate **ยังตัดสินไม่ได้** · " + real_short(8).strip("()"),
        "ตัวเลขของคุณอาจต่างจากของผู้สอน ถ้า Test Set มีรูปไม่ครบเกณฑ์ คำตอบที่ถูกคือ **ยังตัดสินไม่ได้**"))
    h8 = howread(8)
    img_n = re.findall(r"\d+", g8[2][2])
    thr = re.findall(r"\d+", g8[2][3])
    add(chart("Recall ถึงเกณฑ์ที่ขอบพอดี แต่รูปใน Test Set ไม่ครบ จึงยังตัดสินไม่ได้", gauge([
        ("Recall \"ไม่ใส่หมวก\"", "ก่อนเทรน %s · %s" % (g8[0][1], g8[0][4]), float(g8[0][2].split()[0]), 1, 0.80, "เกณฑ์ ≥ 0.80", g8[0][2], "warn"),
        ("Precision \"ไม่ใส่หมวก\"", "ก่อนเทรน %s · %s" % (g8[1][1], g8[1][4]), float(g8[1][2].split()[0]), 1, 0.80, "เกณฑ์ ≥ 0.80", g8[1][2], "ok"),
        ("รูปที่มีคนไม่ใส่หมวกใน Test Set", "ไม่ครบเงื่อนไข", int(img_n[0]), 120, int(thr[0]), "เกณฑ์ ≥ %s" % thr[0], "%s รูป" % img_n[0], "bad"),
        ("รูปที่ไม่มีคนไม่ใส่หมวกใน Test Set", "ไม่ครบเงื่อนไข", int(img_n[1]), 120, int(thr[1]), "เกณฑ์ ≥ %s" % thr[1], "%s รูป" % img_n[1], "bad"),
    ]) + '<div class="verdict" style="margin-top:.8em">Acceptance Gate: %s</div>' % g8[4][4].replace("**", "") +
        '<p class="cap">mAP50 รวม 10 คลาส: ก่อนเทรน %s → หลังเทรน %s (%s)</p>' % (g8[3][1], g8[3][2], g8[3][3]),
        [h8[1], h8[2], h8[0]], tone={1: "bad"}, tag="results/model"))
    add(px("Training 30 Epoch: loss ลดลง ส่วน Precision Recall และ mAP50 เพิ่มขึ้น", "results/model/results.png", [
        "ดูแถวบน 3 ช่องแรก: loss ของ Training Set ลดลงตลอด 30 Epoch",
        "ดูช่อง metrics/mAP50(B) แถวล่าง: ค่าเพิ่มขึ้นจนนิ่งช่วงท้าย",
        h8[3],
    ], tone={2: "bad"}, cap="เทรน 8 นาที 55 วินาที บน RTX 3090 · ภาพจริง results/model/results.png"))
    add(fig("ผลตรวจบน Test Set: แถวบนจับถูก (TP) แถวล่างจับพลาด (FN)", "img/c02-pred.jpg",
            "ส่วนหนึ่งของภาพจริง ทุกรูปมีคนไม่ใส่หมวก · ภาพเต็มมีกรณีแจ้งผิด (FP) และกรณีไม่มีคนไม่ใส่หมวก (TN): "
            "[results/model/examples_test_predictions.jpg](results/model/examples_test_predictions.jpg)"))

    step(9, PC)
    r9 = rows(st(9), "ส่วนของระบบ")
    add(divider(9, "คิว 20 งาน + หยุด Worker กลางงาน: " + r9[5][2]))
    add(px("ทดสอบทั้งเส้นทาง และหยุด Worker กลางงานเพื่อดูว่างานหายหรือไม่", "img/n05-deploy-path.jpg", [
        "บนเครื่อง GPU เปิด RabbitMQ, API gateway และ GPU Worker ที่ใช้โมเดลที่เทรนแล้ว",
        "ส่งรูปจาก Test Set 5 รูปผ่านหน้าเว็บ แล้วเทียบผลในฐานข้อมูลกับที่ gateway ตอบ",
        "ส่ง 20 งาน หยุด Worker กลางงาน เปิดใหม่ แล้วนับงานที่เสร็จ",
    ]))
    add(prompt_slides(9, "Deployment และทดสอบทั้งเส้นทาง"))
    add(check(9, "Deployment", [
        "gateway บนเครื่อง GPU: ไม่มี key ตอบ `401` · มี key ตอบ `200`",
        "เว็บเปิดที่ `http://localhost:3410` และ `/api/health` ปกติ",
        "ส่งรูป 5 รูปผ่านหน้าเว็บ ผลในฐานข้อมูลตรงกับที่ gateway ตอบ",
        "ส่ง 20 งานแล้วหยุด Worker กลางงาน งานเสร็จครบ 20 งาน",
        "สิ่งที่แก้โค้ดถูกจดไว้ใน `results/deploy/`",
    ], real_short(9) + " · 5/5 ตรงกัน · 20 งาน หาย 0"))
    h9 = howread(9)
    add(tbl("ผลจริง: ทุกส่วนของระบบเปิดได้ และงานไม่หายเมื่อ Worker ถูกหยุด", table(st(9), "ส่วนของระบบ"),
            post=note(h9[0] + " · " + h9[1], label="อ่านผล")))
    add(px("GPU ใช้ 22 มิลลิวินาทีต่อรูป แต่ผู้ใช้รอหลายวินาที เพราะคอขวดอยู่ที่ dispatcher", N2("n34-bottleneck"), [
        h9[2], "ขั้นที่ 12 จะพบผลของคอขวดนี้อีกครั้งเป็น BUG-02"], tone={1: "warn"}, tag="อ่านผล · README"))

    # ---------- ระยะ D
    PD = "ภาค LAB · ระยะ D"
    CTX.update(kicker="", group="ระยะ D · Verification")
    add(E.divider("ระยะ D", "พิสูจน์ว่าระบบทำตาม Requirement", "<p>%s</p>" % md(para("6 · ระยะ D", "ระยะ C จบที่")["lines"][0]),
                  "img/s02-verify.jpg", small="ภาค LAB"))
    step(10, PD)
    add(divider(10))
    h10 = howread(10)
    add(px("subagent 4 ตัวสำรวจเว็บพร้อมกัน แต่ละตัวมี session และบัญชีทดสอบของตัวเอง", N2("n35-explore"), [
        "เขียน Test Charter 4 ข้อ รูปแบบ **สำรวจ… ด้วย… เพื่อหา…** ตัวละ 1 Charter",
        h10[1],
        "รวมผลไว้ที่ `test/EXPLORATION.md` พร้อมตารางความเสี่ยง P1 / P2 / P3",
    ]))
    add(prompt_slides(10, "Test Charter และ Exploration"))
    add(check(10, "Exploration", [
        "`test/CHARTERS.md` มี Test Charter 4 ข้อ และทุก Business Rule มี Charter รับผิดชอบ",
        "`test/exploration/` มีบันทึกของแต่ละ subagent พร้อมภาพหน้าจอ",
        "ทุกบันทึกเขียนผลที่คาดหวังก่อนผลจริง",
        "`test/EXPLORATION.md` มีจุดที่เว็บไม่ตรง Requirement และตารางความเสี่ยง P1 / P2 / P3",
        "ไม่มีการเปิดโค้ดใน `./app` หรือไฟล์ BUGS-SECRET",
    ], real_short(10)))
    r10 = rows(st(10), "Charter")
    add(chart("ผลจริง: ลอง 53 กฎ ผ่าน 46 ข้อ ต้องระวัง 6 ข้อ และไม่ตรง Requirement 1 ข้อ", stack(
        [(r[0], "", [(int(r[2]), "ok"), (int(r[3]), "warn"), (int(r[4]), "bad")], "%s กฎ" % r[1]) for r in r10],
        legend([("ok", "✅ ตรง Requirement"), ("warn", "⚠️ ต้องระวัง"), ("bad", "❌ ไม่ตรง Requirement")])),
        [h10[2]], tone={0: "bad"}, tag=ttag(10)))

    step(11, PD)
    add(divider(11))
    add(px("ผู้ตรวจ Test Plan ต้องไม่ใช่ผู้เขียน", "img/n06-cross-review.jpg", [
        "Test Case 30–40 ข้อ รหัส TC-<กลุ่ม>-<เลข> ทุกข้อมีผลที่คาดหวังที่ **คำนวณจาก Requirement**",
        "ผู้เขียนแผนคือ Claude ผู้ตรวจคือ Codex (`cyolo1`) ผ่านสกิล agent-team",
        "บันทึกผลตรวจไว้ที่ `PLAN-REVIEW.md` แล้วแก้แผนตามข้อที่รุนแรงสูง",
    ]))
    add(prompt_slides(11, "Test Plan และการตรวจไขว้"))
    add(check(11, "Test Plan", [
        "`test/TEST-PLAN.md` มี 8 หัวข้อ และ Test Case 30–40 ข้อ รหัส TC-<กลุ่ม>-<เลข>",
        "ทุก Test Case มีขั้นตอน ผลที่คาดหวังที่คำนวณให้ดู ที่มา (FR/BR) และระดับ P1–P3",
        "มีกลุ่มของ AI และคิว: ผลตรวจกับกติกา · สถานะงาน · คิวเต็ม · ไฟล์ที่ไม่รับ · สิทธิ์",
        "`test/PLAN-REVIEW.md` มาจากบัญชี cyolo1 (ผู้ตรวจไม่ใช่ผู้เขียน)",
        "ข้อที่รุนแรงสูงถูกแก้ในแผนแล้ว",
    ], real_short(11)))
    r11 = rows(st(11), "กลุ่ม")
    h11 = howread(11)
    add(chart("ผลจริง: Test Case 39 ข้อ ผู้ตรวจพบปัญหาในแผน 38 ข้อ และแก้ครบทุกข้อ", hbars(
        [(r[0], ("Test Case %s ข้อ · P1 %s ข้อ" % (r[1], r[2])) if r[1] != "–" else "", int(r[4]), int(r[3]), "แก้ %s/%s" % (r[4], r[3]), "teal")
         for r in r11[:6]]) + '<p class="cap">ข้อที่ผู้ตรวจพบ: สูง 23 · กลาง 11 · ต่ำ 4</p>',
        [h11[1], h11[0], h11[3]], tone={2: "warn"}, tag=ttag(11)))

    step(12, PD)
    add(divider(12))
    h12 = howread(12)
    add(px("Playwright Test ตาม Test Plan แล้วคัดแยกข้อที่ล้มก่อนตัดสินผล", N2("n37-triage"), [
        "subagent เขียนไฟล์ทดสอบ 1 ไฟล์ต่อกลุ่ม 5.x แล้วรันทั้งชุดบน Chromium 1 รอบ",
        "แก้ได้เฉพาะ **เทสต์ผิด** ห้ามแก้ผลที่คาดหวังให้ตรงกับเว็บ",
        h12[1],
    ]))
    add(prompt_slides(12, "Playwright Test และ Test Report"))
    add(check(12, "Playwright Test", [
        "`test/e2e/` มีไฟล์ทดสอบ 1 ไฟล์ต่อกลุ่ม 5.x",
        "ข้อที่ล้มมีภาพหน้าจอและ trace และถูกคัดแยกเป็น เว็บผิด / แผนผิด / เทสต์ผิด",
        "ไม่มีข้อใดที่แก้ผลที่คาดหวังให้ตรงกับเว็บ",
        "`test/TEST-REPORT.md` มี 6 ส่วน และ `test/index.html` เปิดดูหลักฐานได้",
        "มีผลตัดสินตาม Exit Criteria",
    ], real_short(12)))
    r12 = rows(st(12), "กลุ่ม")
    add(chart("ผลจริง: ผ่าน 27 ล้ม 2 และบล็อก 10 จาก 39 ข้อ ผลตัดสินคือยังส่งมอบไม่ได้", stack(
        [(r[0], r[4] if r[4] != "–" else "", [(int(r[1]), "ok"), (int(r[2]), "bad"), (int(r[3]), "grey")],
          "%d ข้อ" % (int(r[1]) + int(r[2]) + int(r[3]))) for r in r12[:5]],
        legend([("ok", "ผ่าน"), ("bad", "ล้ม"), ("grey", "บล็อก (ยังไม่ได้รัน)")])) +
        '<div class="verdict" style="margin-top:.6em">ผลตัดสินตาม Exit Criteria: ยังส่งมอบไม่ได้</div>',
        [h12[0], h12[3]], tone={0: "bad", 1: "warn"}, tag=ttag(12)))
    bugs = rows(st(12), "รหัส")
    add(px("ข้อบกพร่อง 2 ข้อเป็นเว็บผิดระดับ P1 ทั้งคู่", "img/c03-testreport.jpg",
           pre=cards([("%s · %s" % (r[0], r[2]), r[1], "bad") for r in bugs], 1), points=[h12[2]],
           cap="ส่วนหนึ่งของหน้าหลักฐานจริง · หน้าเต็ม: [image/test-report.png](image/test-report.png) และ [test/index.html](test/index.html)",
           tag="test/TEST-REPORT.md"))

    step(13, PD)
    add(divider(13, lead=sec(st(13))[0]["lines"][0]))
    add(px("เปิดบั๊กที่ซ่อนไว้ 3 ตัว แล้วรันชุดทดสอบเดิมเพื่อดูว่าจับได้กี่ตัว", N2("n38-bug-mode"), [
        "เปิดเว็บใหม่ด้วย `BUG_MODE=1` แล้วรัน Playwright Test ชุดเดิม",
        "เขียนรายงานบั๊กให้เสร็จก่อน แล้วจึงเปิด BUGS-SECRET เพื่อเทียบ",
        "เขียน `DELIVERY.md` สำหรับลูกค้า แล้วปิด BUG_MODE",
    ]))
    add(prompt_slides(13, "Bug Hunt และรายงานส่งมอบ"))
    add(check(13, "Bug Hunt", [
        "`test/BUG-HUNT.md` มีบั๊กทีละตัว พร้อมขั้นตอนทำซ้ำ ผลที่คาดหวัง ผลจริง และหลักฐาน",
        "รายงานบั๊กเขียนเสร็จก่อนเปิด BUGS-SECRET",
        "`DELIVERY.md` มีตาราง User Story → Requirement → Test Case → ผล และสิ่งที่ยังไม่ผ่าน",
        "เว็บกลับเป็นโหมดปกติ (`BUG_MODE` ปิดแล้ว)",
    ], real_short(13)))
    h13 = howread(13)
    add(pair("ไซต์ ข อัตราผ่าน 90.00% พอดี: รอบปกติขึ้นปกติ รอบเปิดบั๊กขึ้นต่ำกว่าเกณฑ์",
             ("รอบปกติ", "ขั้นที่ 10 · ไซต์ ข ขึ้น \"ปกติ\"", "img/c05-explore.jpg"),
             ("รอบเปิดบั๊ก", "`BUG_MODE=1` · ไซต์ ข ขึ้น \"ต่ำกว่าเกณฑ์\"", "img/c06-bug.jpg"),
             cap=h13[0] + " · ภาพเต็ม: [image/explore-report.png](image/explore-report.png) · [image/bug-9000.png](image/bug-9000.png)",
             rows_=True, cls=("good", "after"), tag="ภาพหน้าจอจริง"))
    r13 = rows(st(13), "บั๊กที่ซ่อนไว้")
    must = re.search(r"Must ผ่าน (\d+) เรื่อง · ไม่ผ่าน (\d+) เรื่อง · หลักฐานยังไม่ครบ (\d+) เรื่อง", h13[2])
    mp, mf, mi = (int(x) for x in must.groups())
    add(S("ผลจริง: จับบั๊กได้ 2 จาก 3 ตัว และ Must มีหลักฐานว่าผ่าน 9 จาก 16 เรื่อง",
          stack([("User Story ระดับ Must", "DELIVERY.md", [(mp, "ok"), (mf, "bad"), (mi, "grey")], "%d เรื่อง" % (mp + mf + mi))],
                legend([("ok", "ผ่าน"), ("bad", "ไม่ผ่าน"), ("grey", "หลักฐานยังไม่ครบ")])) +
          cards([(r[0], "Test Case ที่จับได้: %s · ความรุนแรง %s" % (r[1], r[2]), "bad" if "จับไม่ได้" in r[1] else "ok") for r in r13], 3) +
          note(h13[1], label="บั๊กที่หลุด"), tag=ttag(13), cls="mid", maxfs=1.3))
    add(bleed(N2("p22-report"), "ขั้นที่ 13 · รายงานส่งมอบ", "งานจบที่ \"ยังส่งมอบไม่ได้ พร้อมรายการที่ต้องแก้\" ไม่ใช่ \"เสร็จแล้ว\"",
              h13[3].split(": ", 1)[1].replace("\"", "") if ": " in h13[3] else ""))

    step(14, PD)
    r14 = rows(st(14), "รายการ")
    add(divider(14, "ค่าเช่ารวม " + r14[1][1].split(" (")[0]))
    add(prompt_slides(14, "ลบเครื่องและสรุปค่าใช้จ่าย"))
    add(check(14, "ลบเครื่อง", [
        "น้ำหนักโมเดลและผลวัดถูกคัดลอกกลับมาที่ `results/model`",
        "ไม่มีเครื่องป้าย `e2e-sitesafe` เหลืออยู่ (ตรวจซ้ำแล้ว)",
        "เว็บและฐานข้อมูลบนเครื่องนี้หยุดแล้ว",
        "เปิดหน้า Instances ของ Vast.ai ดูด้วยตาอีกครั้งว่าว่าง",
    ], " · ".join("%s %s" % (r[0], r[1]) for r in r14), "ค่าเช่าของคุณขึ้นกับราคาเครื่องและเวลาที่เปิด · **ห้ามข้ามขั้นนี้**"))
    h14 = howread(14)
    hm = re.match(r"(\d+) ชั่วโมง (\d+) นาที", r14[0][1])
    open_min = int(hm.group(1)) * 60 + int(hm.group(2))
    tm = re.search(r"เทรน (\d+) นาที (\d+) วินาที", real(8))
    train_min = int(tm.group(1)) + int(tm.group(2)) / 60.0
    timeline = ('<div class="tl"><div class="bar2"><div class="seg" style="width:%.2f%%"></div></div>'
                '<div class="lbs"><span><b style="color:var(--teal)">■</b> เทรน %s นาที %s วินาที (ขั้นที่ 8)</span><span>เวลาที่เปิดเครื่องทั้งหมด %s</span></div></div>'
                % (100.0 * train_min / open_min, tm.group(1), tm.group(2), r14[0][1]))
    add(chart("ผลจริง: ค่าเช่า GPU ทั้งหัวข้อ $0.76 และเวลาส่วนใหญ่เครื่องเปิดรอ", tiles([
        ("ค่าเช่ารวม", r14[1][1].split(" (")[0].replace("**", ""), r14[1][1].split(" (")[1].rstrip(")"), "ok"),
        ("โทเคนรวมของทีม", r14[2][1], "ขั้นที่ 5 + 6", "warn"), ("เครื่องป้าย `e2e-sitesafe`", "0", r14[3][1], "ok")]) +
        '<div style="height:1.2em"></div>' + timeline, [h14[0], h14[1], h14[2]], tone={1: "warn"}, tag=ttag(14), wide=True))

    # ---------- ปิดท้าย · สกิล
    PE = "ภาค LAB · ปิดท้าย"
    CTX.update(kicker="", group="ปิดท้าย · สกิลเวอร์ชัน 0")
    step(15, PE)
    add(divider(15, lead=para("7 · ปิดท้าย", "14 ขั้น")["lines"][0]))
    h15 = howread(15)
    add(px("สกิลเก็บขั้นตอน คำสั่งจริง และกับดักที่เจอ แล้วหยุดถามคนก่อนใช้โทเคนและเงิน", N2("n40-skill"), [
        h15[0], h15[1], h15[2] + " · " + h15[3]]))
    add(prompt_slides(15, "สร้างสกิลเวอร์ชัน 0"))
    add(check(15, "สกิลเวอร์ชัน 0", [
        "มี `skill_v0/SKILL.md` และติดตั้งไว้ที่ `.claude/skills/agent-team-delivery`",
        "สกิลมีค่าที่ปรับได้พร้อมค่าเริ่มต้น",
        "แต่ละระยะมีเกณฑ์ตรวจผ่าน และมีจุดถามคนก่อนรันทีมจริงและก่อนเช่าเครื่อง",
        "สกิลไม่มีค่า key และไม่มีรายชื่อบั๊กที่ซ่อนไว้",
        "เปิด Claude Code ใหม่ 1 ครั้งแล้วเห็นสกิล",
    ], real_short(15)))
    r15 = rows(st(15), "ระยะ")
    add(S("ผลจริง: สกิล 8 ไฟล์ และแต่ละระยะมีเกณฑ์ตรวจผ่านกับจุดถามคน", tiles([
        ("ไฟล์ในสกิล", re.search(r"สกิล (\d+) ไฟล์", real(15)).group(1), "ไฟล์", ""),
        ("`SKILL.md`", re.search(r"(\d+) บรรทัด", real(15)).group(1), "บรรทัด", ""),
        ("บันทึกกับดัก", re.search(r"กับดัก (\d+) ข้อ", real(15)).group(1), "ข้อ", ""),
        ("สคริปต์ที่ใช้ได้แล้ว", re.search(r"ใช้ได้แล้ว (\d+) ไฟล์", real(15)).group(1), "ไฟล์", "")]) +
        cards([(r[0], "<p>%s</p><p><b>ถามคน:</b> %s</p>" % (md(r[1]), md(r[2])), "warn" if "**" in r[2] else "") for r in r15], 2),
        tag="skill_v0/SKILL.md", maxfs=1.2))

    step(16, PE)
    add(divider(16))
    h16 = howread(16)
    add(pair("แผนจากสกิลสั้นลงเกือบครึ่ง: 112.5 นาที เหลือ 60.6 นาที", ("ขั้นที่ 4", "ทำทีละขั้น · แผน sitesafe · ประมาณ 112.5 นาที", "plan/gantt-plan.png"),
             ("ใช้สกิล", "แผน sitesafe-skill · ประมาณ 60.6 นาที", "results/skill_v0_run/plan/gantt-plan.png"),
             cap=h16[0], rows_=True, tall=True, cls=("", "good"), tag="ภาพจริง plan/ และ results/skill_v0_run/"))
    add(prompt_slides(16, "ลองใช้สกิล"))
    add(check(16, "ลองใช้สกิล", [
        "สกิลทำถึงระยะ Planning แล้วหยุด ไม่รันทีมจริงและไม่เช่าเครื่อง",
        "`results/skill_v0_run/` มีเอกสารระยะ A และแผน `sitesafe-skill`",
        "รายงานเทียบกับรอบทำทีละขั้น: User Story · FR · BR · จำนวนบล็อก · Critical Path · เวลารวมของแผน",
    ], real_short(16)))
    add(tbl("ทำทีละขั้นเทียบกับใช้สกิล: คำสั่งเดียวได้เอกสารและแผน แล้วหยุดรอคนอนุมัติ", table(st(16), "เรื่อง"),
            post=note(h16[2] + " · " + h16[3] + " · " + h16[1], label="อ่านผล")))

    # ===== 4 · สรุป
    CTX.update(kicker="สรุปหัวข้อ", group="สรุป")
    us_ = rows(st(5), "บล็อก")
    add(chart("ภาพรวมผล: ระบบสร้างได้ครบ แต่หลักฐานว่าทำตามที่ลูกค้าขอยังไม่ครบ", stack([
        ("บล็อก รอบแรก", "ขั้นที่ 5", [(6, "ok"), (1, "bad"), (3, "grey")], "10 บล็อก"),
        ("บล็อก หลังรันต่อ", "ขั้นที่ 6", [(10, "ok")], "10 บล็อก"),
        ("Test Case", "ขั้นที่ 12", [(27, "ok"), (2, "bad"), (10, "grey")], "39 ข้อ"),
        ("บั๊กที่ซ่อนไว้", "ขั้นที่ 13", [(2, "ok"), (1, "bad")], "3 ตัว"),
        ("User Story ระดับ Must", "ขั้นที่ 13", [(mp, "ok"), (mf, "bad"), (mi, "grey")], "%d เรื่อง" % (mp + mf + mi)),
    ], legend([("ok", "เสร็จ / ผ่าน / จับได้"), ("bad", "ไม่ผ่าน / ล้ม / จับไม่ได้"), ("grey", "ถูกบล็อก / หลักฐานยังไม่ครบ")])),
        ["Acceptance Gate ของโมเดล: **ยังตัดสินไม่ได้**", "ผลตัดสินการส่งมอบ: **ยังส่งมอบไม่ได้**",
         "ค่าเช่า GPU ทั้งหัวข้อ $0.76 และโทเคนของทีม 2,499,966"], tone={0: "bad", 1: "bad"}, tag="README"))
    add(tbl("16 ขั้นของหัวข้อ และไฟล์ที่ได้จากแต่ละขั้น", table("16 ขั้น", "ระยะ")))
    add(px("บทเรียนจากหัวข้อนี้", N2("p23-lessons"), [
        "ทุก Requirement ย้อนกลับถึงคำพูดได้ จุดที่ลูกค้าขัดกันกลายเป็นคำถามและข้อสมมติ",
        "บล็อกบน Critical Path ที่ไม่ผ่าน หยุดงานท้ายแผนทั้งสาย และสถานะ \"เสร็จ\" ยังไม่ใช่ \"ทำงานได้\"",
        "Test Case ที่ยังไม่ได้รัน คือบั๊กที่ยังไม่มีใครเห็น",
        "ทีม AI สร้างระบบได้ใน 96 นาที แต่การพิสูจน์ใช้เวลามากกว่า และคนเป็นผู้ตัดสินในจุดที่มีความเสี่ยง",
    ]))
    add(S("ข้อจำกัด และสิ่งที่ยังไม่ผ่าน", cards([
        ("Acceptance Gate ยังตัดสินไม่ได้", "Test Set มีรูปที่มีคนไม่ใส่หมวก 25 รูป เกณฑ์ต้องการอย่างน้อย 100 รูป", "bad"),
        ("BUG-01 · รูปค้าง \"รอคิว\"", "รูป 14.9 MB และ 15.0 MB ค้างจนขึ้น ตรวจไม่สำเร็จ · เกินเวลา 15 นาที", "bad"),
        ("BUG-02 · เกิน SLO", "ส่ง 20 รูป p95 ของเวลารอผล = 42.4 วินาที เกินเกณฑ์ 30 วินาที", "bad"),
        ("10 Test Case ถูกบล็อก", "ต้องใช้ตัวตรวจจำลองอีกชุด หรือเป็นรอบ B ที่ต้องขออนุมัติงบแยก", "warn"),
        ("บั๊ก BR-02 จับไม่ได้", "ไม่ใส่เสื้อสะท้อนแสง 2 คนพอดี ได้ \"เตือน\" แทน \"ไม่ผ่าน\"", "bad"),
        ("ข้อสมมติยังไม่ได้รับการยืนยัน", "เช่น พอดี 2 คนไม่ใส่เสื้อ → ไม่ผ่าน · Precision ≥ 0.80 · เพดานไฟล์ 15 MB", "warn"),
    ], 3), cls="mid"))
    CTX.update(kicker="", group="จบหัวข้อ")
    add(E.divider("จบหัวข้อที่ 1", "ยังส่งมอบไม่ได้ พร้อมรายการที่ต้องแก้",
                  '<p>รายละเอียดเต็มของหัวข้อนี้: <a href="README.md" target="_blank">README.md</a> · พรอมต์ทั้งหมด: '
                  '<a href="PROMPTS.md" target="_blank">PROMPTS.md</a> · รายงานส่งมอบ: <a href="DELIVERY.md" target="_blank">DELIVERY.md</a></p>',
                  "image/cover.jpg"))
    return E.SL


if __name__ == "__main__":
    for st_ in (sys.stdout, sys.stderr):
        if hasattr(st_, "reconfigure"):
            st_.reconfigure(encoding="utf-8", errors="replace")
    E.write(build(), out=OUT, title=TITLE)
