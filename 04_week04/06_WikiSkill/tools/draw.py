#!/usr/bin/env python3
"""ตัวช่วยวาดภาพของบทนี้: HTML -> PNG ด้วย Chrome headless (ตัวอักษรไทยและตัวเลขตรงตามที่พิมพ์)"""
import html, os, subprocess, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = [p for p in (os.environ.get("CHROME", ""), r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                      r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                      "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "/usr/bin/chromium",
                      "/usr/bin/google-chrome") if p and os.path.exists(p)]
RAW, WIKI, SKILL, GATE, BAD, INK, MUTE, LINE = "#8D6E63", "#2A9D8F", "#F4A261", "#6BBF59", "#E76F51", "#4A2F1F", "#7A6557", "#E5D9CC"
MONO = "font-family:Consolas,'Courier New',monospace"
CSS = """
*{box-sizing:border-box} body{margin:0;width:1600px;background:#FBF7F0;color:#3B2A20;
font-family:'Leelawadee UI','Noto Sans Thai','Sarabun',sans-serif;padding:40px 56px;overflow:hidden}
h1{font-size:44px;margin:0 0 6px;color:#4A2F1F} .sub{font-size:25px;color:#7A6557;margin-bottom:22px;line-height:1.35}
.badge{display:inline-block;border-radius:14px;padding:5px 15px;font-weight:700;font-size:23px;color:#fff;white-space:nowrap}
.raw{background:#8D6E63}.wiki{background:#2A9D8F}.skill{background:#F4A261}.gate{background:#6BBF59}.bad{background:#E76F51}.ink{background:#4A2F1F}
.card{background:#fff;border:3px solid #E5D9CC;border-radius:22px;padding:16px 20px}
.mono{font-family:Consolas,'Courier New',monospace}
.row{display:flex;gap:18px} .arrow{font-size:44px;color:#6F4E37;align-self:center;font-weight:800}
.note{font-size:24px;color:#7A6557;line-height:1.4} b{color:#4A2F1F}
table.t{border-collapse:separate;border-spacing:0 8px;width:100%} table.t th{font-size:23px;color:#7A6557;text-align:left;padding:0 14px 2px;font-weight:400}
table.t td{background:#fff;padding:12px 14px;font-size:24px;line-height:1.35;vertical-align:middle}
table.t td:first-child{border-radius:16px 0 0 16px} table.t td:last-child{border-radius:0 16px 16px 0}
"""
e = html.escape


def shot(out, body, height=900):
    """out = path ของ PNG เทียบกับโฟลเดอร์ของบท เช่น 01_theory/img/t01-loop.png"""
    path = os.path.join(ROOT, out)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    page = "<!doctype html><html lang='th'><head><meta charset='utf-8'><style>%s</style></head><body style='height:%dpx'>%s</body></html>" % (
        CSS, height, body)
    with tempfile.TemporaryDirectory() as tmp:
        f = os.path.join(tmp, "p.html")
        open(f, "w", encoding="utf-8").write(page)
        subprocess.run([CHROME[0], "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                        "--window-size=1600,%d" % height, "--screenshot=" + path, "file:///" + f.replace("\\", "/")],
                       capture_output=True, timeout=120)
    print("wrote", out)


def card(color, title, sub="", body="", style=""):
    return """<div class='card' style='border-top:14px solid %s;%s'>
      <div style='font-size:30px;font-weight:800;color:#4A2F1F;line-height:1.2'>%s</div>
      %s<div style='font-size:23px;color:#7A6557;line-height:1.38;margin-top:6px'>%s</div></div>""" % (
        color, style, title, ("<div class='mono' style='font-size:22px;color:#2A6F68;margin-top:5px'>%s</div>" % sub) if sub else "", body)


def arrow(t="➜"):
    return "<div class='arrow'>%s</div>" % t
