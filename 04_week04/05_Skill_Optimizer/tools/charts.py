#!/usr/bin/env python3
"""วาดกราฟผลจริงจาก runs/ เป็น PNG (HTML -> Chrome headless เพื่อให้ตัวอักษรไทยถูกต้อง)

  python tools/charts.py noskill,v0,v1,v2,v3        (รันบนเครื่อง จากโฟลเดอร์ของบท)

ตัวเลขทุกตัวอ่านจาก runs/results.json และ runs/<รุ่นใหม่>/gate.txt ไม่มีค่าที่พิมพ์เอง
"""
import glob, html, json, os, re, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "runs")
OUT = os.path.join(ROOT, "img")
CHROME = [p for p in (os.environ.get("CHROME", ""), r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                      r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                      "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "/usr/bin/chromium",
                      "/usr/bin/google-chrome") if p and os.path.exists(p)]
NAME = {"noskill": "ไม่มีสกิล"}
CHECKS = [("contract", "มีฟังก์ชัน และคืนค่าเป็น int สตางค์"), ("basic", "กรณีปกติคำนวณถูก"),
          ("half_up", "ลงท้าย .5 สตางค์ ต้องปัดขึ้น"), ("no_drift", "ไม่ปัดระหว่างทาง ผลไม่เพี้ยน"),
          ("boundary", "ค่าขอบของเงื่อนไขถูก"), ("reject_value", "ค่าเกินช่วง ต้อง ValueError"),
          ("reject_type", "ชนิดผิด (float str bool) ต้อง ValueError"), ("cli_ok", "CLI ตอบ {\"ok\": true, \"result\": …}"),
          ("cli_error", "CLI input ผิด ตอบ ok false และ exit 2"), ("tests", "test_solve.py ≥ 6 เทสต์ รันผ่าน"),
          ("policy", "ทำตามนโยบายธุรกิจของงานนั้น (งาน 3 และ 4)")]
CSS = """
*{box-sizing:border-box} body{margin:0;width:1600px;height:900px;background:#FBF7F0;color:#3B2A20;
font-family:'Leelawadee UI','Noto Sans Thai','Sarabun',sans-serif;padding:44px 60px;overflow:hidden}
h1{font-size:46px;margin:0 0 6px;color:#4A2F1F} .sub{font-size:25px;color:#7A6557;margin-bottom:26px}
.teal{background:#2A9D8F}.orange{background:#F4A261}.green{background:#6BBF59}.red{background:#E76F51}.brown{background:#6F4E37}
.badge{display:inline-block;border-radius:14px;padding:6px 16px;font-weight:700;font-size:24px;color:#fff}
.note{font-size:24px;color:#7A6557}
"""


def gates():
    g = {}
    for f in glob.glob(os.path.join(RES, "*", "gate.txt")):       # runs/<รุ่นใหม่>/gate.txt
        txt = open(f, encoding="utf-8").read()
        m = re.search(r"(\S+) แทน (\S+)\s*$", txt)                # บรรทัดสุดท้าย: ผล: ... <ใหม่> แทน <ฐาน>
        d = {"base": m.group(2), "cand": m.group(1), "accept": "ACCEPT" in txt, "text": txt}
        for key, pat in (("train", r"^train: ([\d.]+)% → ([\d.]+)% \(([+-][\d.]+)\) · เกณฑ์ ([\d.]+)"),
                         ("val", r"^val: ([\d.]+)% → ([\d.]+)% \(([+-][\d.]+)\) · เกณฑ์ ([\d.]+)"),
                         ("all", r"^รวม: ([\d.]+)% → ([\d.]+)% \(([+-][\d.]+)\) · เกณฑ์ ([\d.]+)")):
            mm = re.search(pat, txt, re.M)
            if mm:
                d[key] = [float(x) for x in mm.groups()]
        mm = re.search(r"z ([\d.]+) × ความแกว่งของส่วนต่าง ([\d.]+) จุด", txt)
        if mm:
            d["z"], d["se"] = float(mm.group(1)), float(mm.group(2))
        mm = re.search(r"\[โทเคนขาเข้า ([\d.e+]+) → ([\d.e+]+) \(([+-]\d+)%\)\]", txt)
        if mm:
            d["cost"] = [float(mm.group(1)), float(mm.group(2)), int(mm.group(3))]
        g[(d["base"], d["cand"])] = d
    return g


def shot(name, body, height=900):
    os.makedirs(OUT, exist_ok=True)
    page = "<!doctype html><html lang='th'><head><meta charset='utf-8'><style>%s</style></head><body style='height:%dpx'>%s</body></html>" % (
        CSS, height, body)
    with tempfile.TemporaryDirectory() as tmp:
        f = os.path.join(tmp, "p.html")
        open(f, "w", encoding="utf-8").write(page)
        out = os.path.join(OUT, name + ".png")
        subprocess.run([CHROME[0], "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                        "--window-size=1600,%d" % height, "--screenshot=" + out, "file:///" + f.replace("\\", "/")],
                       capture_output=True, timeout=120)
    print("wrote", out)


def chain(labels, G):
    """ลำดับการตัดสิน: รุ่นฐานปัจจุบันของแต่ละรุ่น และผลของ Gate"""
    out = []
    for lb in labels[1:]:
        g = next((v for (b, c), v in G.items() if c == lb), None)
        out.append((lb, g))
    return out


def chart_scores(R, labels, G):
    n = R[labels[0]]["all"]["n"]
    cols = ""
    for lb in labels:
        tr, va, al = (R[lb][k]["score"] * 100 for k in ("train", "val", "all"))
        g = next((v for (b, c), v in G.items() if c == lb), None)
        badge = "<span class='badge brown'>เส้นฐาน</span>" if g is None else (
            "<span class='badge %s'>%s</span>" % ("green" if g["accept"] else "red", "ACCEPT" if g["accept"] else "REJECT"))
        cols += """<div style='flex:1;display:flex;flex-direction:column;align-items:center'>
          <div style='font-size:44px;font-weight:800;color:#4A2F1F'>%.1f%%</div>
          <div style='height:430px;display:flex;align-items:flex-end;gap:14px;border-bottom:4px solid #4A2F1F;padding:0 10px'>
            <div class='teal' style='width:84px;height:%.0fpx;border-radius:12px 12px 0 0;position:relative'><span style='position:absolute;top:-34px;left:0;width:84px;text-align:center;font-size:24px;font-weight:700'>%.1f</span></div>
            <div class='orange' style='width:84px;height:%.0fpx;border-radius:12px 12px 0 0;position:relative'><span style='position:absolute;top:-34px;left:0;width:84px;text-align:center;font-size:24px;font-weight:700'>%.1f</span></div>
          </div>
          <div style='font-size:36px;font-weight:800;margin:14px 0 10px'>%s</div>%s
          <div class='note' style='margin-top:8px'>%s</div></div>""" % (
            al, tr * 4.0, tr, va * 4.0, va, html.escape(NAME.get(lb, lb)), badge,
            "" if g is None else "เทียบกับ %s" % html.escape(NAME.get(g["base"], g["base"])))
    body = """<h1>คะแนนเฉลี่ยของสกิล money-coder แต่ละรุ่น</h1>
    <div class='sub'>ผลจริง รุ่นละ %d Trial (6 โจทย์ × 3 รอบ) · ตัวเลขใหญ่ = คะแนนรวม ·
      <span class='badge teal'>Training Set</span> <span class='badge orange'>Validation Set</span></div>
    <div style='display:flex;gap:10px;margin-top:20px'>%s</div>""" % (n, cols)
    shot("r01-scores", body)


def chart_checks(R, labels):
    head = "".join("<th style='font-size:30px;padding:8px 6px;width:150px'>%s</th>" % html.escape(NAME.get(lb, lb)) for lb in labels)
    rows = ""
    for cid, desc in CHECKS:
        tds = ""
        for lb in labels:
            v = R[lb]["train"]["checks"].get(cid, "-")
            a, b = (int(x) for x in v.split("/")) if "/" in v else (0, 1)
            r = a / b
            col = "#6BBF59" if r >= 0.999 else ("#F4A261" if r >= 0.5 else "#E76F51")
            tds += "<td style='text-align:center'><span style='display:inline-block;width:132px;padding:6px 0;border-radius:12px;background:%s;color:#fff;font-weight:800;font-size:25px'>%s</span></td>" % (col, v)
        rows += "<tr><td style='font-size:24px;padding:5px 10px'><b style='font-family:Consolas,monospace;font-size:27px'>%s</b><span style='color:#7A6557'> · %s</span></td>%s</tr>" % (
            cid, html.escape(desc), tds)
    body = """<h1>ข้อตรวจ 11 แบบ: รุ่นไหนผ่านกี่ Trial</h1>
    <div class='sub'>เฉพาะ Training Set (12 Trial ต่อรุ่น · ข้อที่มีเฉพาะบางงานนับเฉพาะงานนั้น) · <span class='badge green'>ผ่านทุก Trial</span>
      <span class='badge orange'>ผ่านบางส่วน</span> <span class='badge red'>ผ่านน้อยกว่าครึ่ง</span></div>
    <table style='border-collapse:separate;border-spacing:0 5px;width:100%%'><tr><th></th>%s</tr>%s</table>""" % (head, rows)
    shot("r02-checks", body)


def chart_threshold(G, base, cand, R):
    g = G[(base, cand)]
    b, c, d, t = g["all"]
    se = g.get("se", 0)
    steps = [("1", "คะแนนรวมของสองรุ่น", "%s %.1f%% → %s %.1f%%" % (NAME.get(base, base), b, NAME.get(cand, cand), c)),
             ("2", "ผลต่าง", "%+.1f จุด" % d),
             ("3", "Standard Error ของผลต่าง (จากการรันซ้ำ)", "%.1f จุด" % se),
             ("4", "threshold = ค่าที่มากกว่าระหว่าง 2.0 กับ 1.5 × %.1f" % se, "%.1f จุด" % t),
             ("5", "ผลต่าง %s threshold" % ("มากกว่า" if d > t else "ไม่เกิน"), "ACCEPT" if g["accept"] else "REJECT")]
    if d <= t and base in R and cand in R:      # คะแนนไม่ขึ้นเกิน threshold → ตัดสินด้วยต้นทุน
        cb, cc = R[base]["all"]["context_tokens"], R[cand]["all"]["context_tokens"]
        pct = (cc / cb - 1) * 100
        steps = [steps[0], ("2", "ผลต่าง (threshold %.1f จุด)" % t, "%+.1f จุด = คะแนนเท่าเดิม" % d),
                 ("3", "โทเคนขาเข้าต่อ Trial", "{:,} → {:,}".format(cb, cc)),
                 ("4", "ต้นทุนเปลี่ยน (ต้องลดอย่างน้อย 10%)", "%+.0f%%" % pct),
                 ("5", "คะแนนเท่าเดิม และต้นทุน%s" % ("ลดถึงเกณฑ์" if pct <= -10 else "ลดไม่ถึงเกณฑ์"), "ACCEPT" if g["accept"] else "REJECT")]
    bad = [k for k in ("train", "val") if k in g and g[k][2] < -g[k][3]]
    if bad:                                       # ชุดใดชุดหนึ่งลดลงเกิน threshold → ไม่รับทันที
        k = bad[0]
        nm = "Training" if k == "train" else "Validation"
        steps = [("1", "คะแนน %s ของสองรุ่น" % nm, "%.1f%% → %.1f%%" % (g[k][0], g[k][1])),
                 ("2", "ผลต่าง", "%+.1f จุด" % g[k][2]),
                 ("3", "threshold ของชุด %s" % nm, "%.1f จุด" % g[k][3]),
                 ("4", "คะแนน %s ลดลงเกิน threshold" % nm, "ไม่ผ่านเงื่อนไข"),
                 ("5", "ผลการตัดสิน", "REJECT")]
    rows = ""
    for i, (no, what, val) in enumerate(steps):
        last = i == len(steps) - 1
        rows += """<div style='display:flex;align-items:center;gap:26px;background:#fff;border:3px solid #E5D9CC;border-radius:22px;padding:18px 28px;margin-bottom:16px'>
          <div class='badge brown' style='font-size:34px;width:64px;text-align:center'>%s</div>
          <div style='flex:1;font-size:32px'>%s</div>
          <div style='font-size:40px;font-weight:800;%s'>%s</div></div>""" % (
            no, html.escape(what), ("color:#fff;padding:4px 26px;border-radius:16px;background:%s" % ("#6BBF59" if g["accept"] else "#E76F51")) if last else "color:#4A2F1F", html.escape(val))
    body = """<h1>Gate ตัดสิน %s → %s อย่างไร</h1><div class='sub'>ตัวเลขจริงจากคำสั่ง gate · Training และ Validation ต้องไม่ลดลงเกิน threshold ของชุดนั้นด้วย</div>%s""" % (
        html.escape(NAME.get(base, base)), html.escape(NAME.get(cand, cand)), rows)
    shot("r03-threshold-%s-%s" % (base, cand), body)


def chart_path(R, labels, G):
    W, H, x0, y0 = 1480, 600, 110, 90
    lo = min(R[lb]["all"]["score"] for lb in labels) * 100 - 8
    lo = max(0, int(lo // 10 * 10))
    def X(i): return x0 + 90 + i * (W - x0 - 190) / (len(labels) - 1)
    def Y(s): return y0 + (100 - s) / (100 - lo) * (H - y0 - 100)
    svg, cur = "", 0                     # cur = index ของรุ่นฐานปัจจุบัน
    for s in range(lo, 101, 10):
        svg += "<line x1='%d' y1='%.0f' x2='%d' y2='%.0f' stroke='#E5D9CC' stroke-width='2'/><text x='%d' y='%.0f' font-size='24' fill='#7A6557' text-anchor='end'>%d%%</text>" % (
            x0 - 20, Y(s), W - 40, Y(s), x0 - 30, Y(s) + 8, s)
    pts = [(X(i), Y(R[lb]["all"]["score"] * 100)) for i, lb in enumerate(labels)]
    for i, lb in enumerate(labels[1:], 1):
        g = next((v for (b, c), v in G.items() if c == lb), None)
        ok = bool(g and g["accept"])
        bi = labels.index(g["base"]) if g and g["base"] in labels else cur
        svg += "<line x1='%.0f' y1='%.0f' x2='%.0f' y2='%.0f' stroke='%s' stroke-width='7' %s/>" % (
            pts[bi][0], pts[bi][1], pts[i][0], pts[i][1], "#6BBF59" if ok else "#E76F51", "" if ok else "stroke-dasharray='14 12'")
        if ok:
            cur = i
    for i, lb in enumerate(labels):
        g = next((v for (b, c), v in G.items() if c == lb), None)
        col = "#6F4E37" if g is None else ("#6BBF59" if g["accept"] else "#E76F51")
        x, y = pts[i]
        svg += "<circle cx='%.0f' cy='%.0f' r='20' fill='%s' stroke='#fff' stroke-width='5'/>" % (x, y, col)
        svg += "<text x='%.0f' y='%.0f' font-size='34' font-weight='800' fill='#4A2F1F' text-anchor='middle'>%.1f%%</text>" % (x, y - 34, R[lb]["all"]["score"] * 100)
        svg += "<text x='%.0f' y='%d' font-size='32' font-weight='800' fill='#4A2F1F' text-anchor='middle'>%s</text>" % (x, H - 46, html.escape(NAME.get(lb, lb)))
        svg += "<text x='%.0f' y='%d' font-size='23' fill='#7A6557' text-anchor='middle'>{:,} โทเคน</text>".format(R[lb]["all"]["context_tokens"]) % (x, H - 12)
        if g is not None:
            svg += "<text x='%.0f' y='%.0f' font-size='25' font-weight='800' fill='%s' text-anchor='middle'>%s</text>" % (
                x, y + 56, col, "ACCEPT" if g["accept"] else "REJECT")
    final = labels[cur]
    body = """<h1>เส้นทางการปรับสกิลจริง</h1>
    <div class='sub'>คะแนนรวมของแต่ละรุ่น และโทเคนขาเข้าต่อ Trial · เส้นทึบสีเขียว = Gate รับ (กลายเป็นรุ่นฐานใหม่) · เส้นประสีแดง = Gate ไม่รับ (ทิ้ง ใช้รุ่นฐานเดิม)</div>
    <svg width='%d' height='%d' style='font-family:inherit'>%s</svg>
    <div style='font-size:32px;margin-top:6px'>รุ่นที่ใช้งานต่อ: <span class='badge green' style='font-size:32px'>%s</span></div>""" % (W, H, svg, html.escape(NAME.get(final, final)))
    shot("r04-path", body)


def main():
    labels = sys.argv[1].split(",")
    R = json.load(open(os.path.join(RES, "results.json"), encoding="utf-8"))
    G = gates()
    chart_scores(R, labels, G)
    chart_checks(R, labels)
    chart_path(R, labels, G)
    for (b, c) in G:
        g = G[(b, c)]
        if "all" not in g and "train" in g and "val" in g:   # gate หยุดก่อนถึงคะแนนรวม: เติมจาก results.json
            sb, sc = R[b]["all"]["score"] * 100, R[c]["all"]["score"] * 100
            g["all"] = [round(sb, 1), round(sc, 1), round(sc - sb, 1), 2.0]
        if "all" in g:
            chart_threshold(G, b, c, R)


if __name__ == "__main__":
    main()
