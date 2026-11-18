#!/usr/bin/env python3
"""เครื่องมือสร้างสไลด์ HTML จาก README.md ของบทเรียน (ไฟล์กลาง ไม่มีเนื้อหาเฉพาะบท)

วิธีใช้: คัดลอกไฟล์นี้ไว้ที่ <บท>/tools/slides_engine.py แล้วเขียนโครงเรื่องใน <บท>/tools/build_slides.py
(ตัวอย่างโครงเรื่อง: outline_template.py ของสกิล readme-slides)

ส่วนประกอบ
- อ่าน README.md เป็นบล็อก: load() แล้วค้นด้วย sec() table() codes() para() prompt() eye()
- ชิ้นส่วนของสไลด์: fig() explain() tiles() cards() versus() bars() tbl() code() fileflow() note() divider() cover()
- สมการ LaTeX: load(latex=True) ทำให้ $...$ และ $$...$$ ถูกเรียงพิมพ์ด้วย KaTeX ตอนสร้างไฟล์ (ต้องมี Node.js) ·
  สไลด์สมการ: equation() eqbox() parts() tc() · ฟอนต์ของ KaTeX ฝังในไฟล์ HTML จึงเปิดได้โดยไม่ต้องต่ออินเทอร์เน็ต
- สไลด์พรอมต์ (ข้อความตรงตัวอักษรจาก README + ปุ่มคัดลอก): prompt_slides() · รายการตรวจผล: check_slide()
- write(): ประกอบไฟล์ HTML ไฟล์เดียว (CSS และ JS อยู่ในไฟล์) · ขนาดตัวอักษรของแต่ละสไลด์ปรับตอนเปิดไฟล์ให้พอดีหน้า
"""
import base64, html, json, math, os, re, shutil, struct, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(p):
    return open(os.path.join(ROOT, p), encoding="utf-8").read()


# ------------------------------------------------------------------ อ่าน Markdown เป็นบล็อก
BLOCK_START = re.compile(r"^\s*(#{1,6}\s|```|\||- |>|!\[|<details|<p>|---\s*$|<!--)")


def split_row(s):
    s = s.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", s)]


def parse(lines):
    out, i, n = [], 0, len(lines)
    while i < n:
        ln = lines[i]
        s = ln.strip()
        if not s or s.startswith("<!--"):
            i += 1
            continue
        if s == "---":
            out.append({"t": "hr"})
            i += 1
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", s)
        if m:
            out.append({"t": "h", "level": len(m.group(1)), "text": m.group(2).strip()})
            i += 1
            continue
        if s.startswith("```"):
            j, buf = i + 1, []
            while j < n and not lines[j].strip().startswith("```"):
                buf.append(lines[j])
                j += 1
            out.append({"t": "code", "lang": s[3:].strip(), "text": "\n".join(buf)})
            i = j + 1
            continue
        if s.startswith("<details"):
            m = re.match(r"<details>\s*<summary>(.*?)</summary>", s)
            j, buf = i + 1, []
            while lines[j].strip() != "</details>":
                buf.append(lines[j])
                j += 1
            out.append({"t": "details", "summary": m.group(1), "blocks": parse(buf)})
            i = j + 1
            continue
        if s == "<p>":
            j, imgs = i + 1, []
            while lines[j].strip() != "</p>":
                mm = re.search(r'<img src="([^"]+)"[^>]*alt="([^"]*)"', lines[j])
                if mm:
                    imgs.append({"t": "img", "alt": mm.group(2), "src": mm.group(1)})
                j += 1
            out.append({"t": "imgrow", "imgs": imgs})
            i = j + 1
            continue
        m = re.match(r"^!\[(.*?)\]\((.*?)\)\s*$", s)
        if m:
            out.append({"t": "img", "alt": m.group(1), "src": m.group(2)})
            i += 1
            continue
        if s.startswith(">"):
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(re.sub(r"^\s*> ?", "", lines[i]))
                i += 1
            kind = "NOTE"
            m = re.match(r"\[!(\w+)\]", buf[0].strip())
            if m:
                kind, buf = m.group(1), buf[1:]
            out.append({"t": "alert", "kind": kind, "blocks": parse(buf)})
            continue
        if s.startswith("|"):
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append(split_row(lines[i]))
                i += 1
            out.append({"t": "table", "head": rows[0], "rows": rows[2:]})
            continue
        if s.startswith("- "):
            items = []
            while i < n and lines[i].strip().startswith("- "):
                items.append(lines[i].strip()[2:])
                i += 1
            out.append({"t": "ul", "items": items})
            continue
        buf = [s]
        i += 1
        while i < n and lines[i].strip() and not BLOCK_START.match(lines[i]):
            buf.append(lines[i].strip())
            i += 1
        out.append({"t": "p", "lines": buf})
    return out


# ------------------------------------------------------------------ สมการ LaTeX (เรียงพิมพ์ด้วย KaTeX ตอนสร้างไฟล์)
KATEX_HOME = os.environ.get("README_SLIDES_KATEX") or os.path.join(os.path.expanduser("~"), ".cache", "readme-slides")
MATH = {}            # (ข้อความ LaTeX, เป็นสมการแยกบรรทัดหรือไม่) -> HTML ของ KaTeX
MATH_ON = [False]    # True = inline() เรียงพิมพ์ $...$ และ $$...$$ (เปิดด้วย load(latex=True))
MATH_RE = re.compile(r"\$\$(.+?)\$\$|(?<![\\$])\$(?!\s)([^$\n]+?)(?<!\s)\$(?![\d$])")
PALETTE = {"navy": "#12305e", "teal": "#0f8f8c", "orange": "#e87f1c", "red": "#c92a2a", "green": "#15803d", "purple": "#6d4bb3", "ink": "#1c2533"}
GREEK = {"theta": "θ", "eta": "η", "tau": "τ", "nabla": "∇", "star": "★", "in": "∈", "sum": "∑", "leftarrow": "←", "cdot": "·",
         "times": "×", "lvert": "|", "rvert": "|", "arg": "arg ", "qquad": " ", "tilde": "", "frac": ""}
NODE_JS = """const katex=require(process.argv[1]);
const items=JSON.parse(require('fs').readFileSync(0,'utf8'));
process.stdout.write(JSON.stringify(items.map(([tex,display])=>{
  try{return katex.renderToString(tex,{displayMode:display,throwOnError:true,strict:false,output:'html'});}
  catch(e){return 'ERR:'+e.message;}})));"""


def katex_dir():
    """โฟลเดอร์ dist ของ KaTeX · ครั้งแรกติดตั้งด้วย npm ไว้ที่ ~/.cache/readme-slides (เปลี่ยนที่ได้ด้วย README_SLIDES_KATEX)"""
    d = os.path.join(KATEX_HOME, "node_modules", "katex", "dist")
    if not os.path.exists(os.path.join(d, "katex.min.js")):
        if not shutil.which("npm"):
            raise SystemExit("สมการ LaTeX ในสไลด์ต้องใช้ Node.js (node และ npm) · ติดตั้งแล้วรันใหม่")
        os.makedirs(KATEX_HOME, exist_ok=True)
        subprocess.run("npm install katex@0.16 --no-audit --no-fund --silent", shell=True, cwd=KATEX_HOME, check=True)
    return d


def tex_many(items):
    """เรียงพิมพ์หลายสมการในการเรียก node ครั้งเดียว · items = [(LaTeX, display)]"""
    todo = [k for k in dict.fromkeys((t.strip(), bool(d)) for t, d in items) if k not in MATH]
    if not todo:
        return
    node = shutil.which("node")
    if not node:
        raise SystemExit("สมการ LaTeX ในสไลด์ต้องใช้ Node.js (node และ npm) · ติดตั้งแล้วรันใหม่")
    r = subprocess.run([node, "-e", NODE_JS, os.path.join(katex_dir(), "katex.min.js")], input=json.dumps(todo),
                       capture_output=True, text=True, encoding="utf-8")
    if r.returncode:
        raise SystemExit("KaTeX ทำงานไม่สำเร็จ: " + r.stderr[-800:])
    for k, h in zip(todo, json.loads(r.stdout)):
        if h.startswith("ERR:"):
            raise SystemExit("สมการ LaTeX เรียงพิมพ์ไม่ได้: %s\n  %s" % (k[0], h[4:]))
        MATH[k] = h


def tex(src, display=False):
    """LaTeX -> HTML ของ KaTeX · display=True = สมการแยกบรรทัด (ตัวใหญ่ ขีดจำกัดอยู่ใต้ ∑ และ arg max)"""
    k = (src.strip(), bool(display))
    if k not in MATH:
        tex_many([k])
    return MATH[k]


def tc(color, src):
    """ใส่สีให้ส่วนหนึ่งของสมการ · color = ชื่อใน PALETTE หรือรหัสสี #rrggbb"""
    return r"\textcolor{%s}{%s}" % (PALETTE.get(color, color), src)


def uncolor(src):
    """ถอด \textcolor{..}{..} และช่องว่างออก · ใช้ตรวจว่าสมการที่ใส่สีในสไลด์ตรงกับสมการใน README"""
    out, stack, depth, i = [], [], 0, 0
    while i < len(src):
        m = re.match(r"\\textcolor\{[^}]*\}\{", src[i:])
        if m:
            depth += 1
            stack.append(depth)
            i += m.end()
            continue
        c = src[i]
        if c == "{" and src[i - 1:i] != "\\":
            depth += 1
        elif c == "}" and src[i - 1:i] != "\\":
            if stack and stack[-1] == depth:
                stack.pop()
                depth -= 1
                i += 1
                continue
            depth -= 1
        out.append(c)
        i += 1
    return re.sub(r"\s+", "", "".join(out))


def detex(t):
    """LaTeX -> ข้อความธรรมดา (ใช้ในชื่อสไลด์ของหน้าสารบัญ และการประมาณความยาว)"""
    t = re.sub(r"\\textcolor\{[^}]*\}", "", t)
    t = re.sub(r"\\([A-Za-z]+)", lambda m: GREEK.get(m.group(1), "" if m.group(1) in ("text", "mathcal", "mathrm", "mathbf") else m.group(1)), t)
    return re.sub(r"[{}\\_^]|,(?=\s)|;", "", t)


def katex_css(page):
    """CSS ของ KaTeX พร้อมฟอนต์ woff2 ฝังในไฟล์ (ตัดตระกูลฟอนต์ที่หน้านี้ไม่ได้ใช้ออก)"""
    d = katex_dir()
    css = open(os.path.join(d, "katex.min.css"), encoding="utf-8").read()
    optional = {"Fraktur": "mathfrak|textfrak", "SansSerif": "mathsf|textsf", "Script": "mathscr|textscr", "Typewriter": "mathtt|texttt",
                "Caligraphic": "mathcal", "AMS": "amsrm|mathbb"}

    def face(m):
        f = re.search(r"fonts/(KaTeX_(\w+?)-\w+)\.woff2", m.group(0))
        if f.group(2) in optional and not re.search(optional[f.group(2)], page):
            return ""
        data = base64.b64encode(open(os.path.join(d, "fonts", f.group(1) + ".woff2"), "rb").read()).decode("ascii")
        return re.sub(r"src:[^}]*", 'src:url(data:font/woff2;base64,%s) format("woff2")' % data, m.group(0))

    return re.sub(r"@font-face\{[^}]*\}", face, css)


# ------------------------------------------------------------------ ข้อความในบรรทัด
def esc(s):
    return html.escape(s, quote=False)


def inline(s):
    codes = []

    def keep(m):
        codes.append(m.group(1))
        return "\x00%d\x00" % (len(codes) - 1)

    s = re.sub(r"`([^`]+)`", keep, s)
    maths = []
    if MATH_ON[0] and "$" in s:
        def keepm(m):
            maths.append(tex(m.group(1) or m.group(2), bool(m.group(1))))
            return "\x01%d\x01" % (len(maths) - 1)

        s = MATH_RE.sub(keepm, s)
    s = esc(s)
    s = re.sub(r"&lt;(/?(?:br|sub|sup|code))&gt;", r"<\1>", s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)

    def link(m):
        t, h = m.group(1), m.group(2)
        if h.startswith("#"):
            return '<span class="xref">%s</span>' % t
        return '<a href="%s" target="_blank" rel="noopener">%s</a>' % (h, t)

    s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, s)
    s = re.sub(r'(?<![\w/"=#-])(ACCEPT|REJECT)(?![\w-])',
               lambda m: '<span class="v %s">%s</span>' % (m.group(1).lower(), m.group(1)), s)
    s = re.sub(r"\x00(\d+)\x00", lambda m: "<code>%s</code>" % esc(codes[int(m.group(1))]), s)
    return re.sub(r"\x01(\d+)\x01", lambda m: maths[int(m.group(1))], s)


COMB = re.compile("[ัิ-ฺ็-๎]")


def plain(s):
    if MATH_ON[0] and "$" in s:
        s = MATH_RE.sub(lambda m: detex(m.group(1) or m.group(2)), s)
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
    s = re.sub(r"</?(?:br|sub|sup|code)>", " ", s)
    return re.sub(r"\s+", " ", s.replace("**", "").replace("`", "")).strip()


def vlen(s):
    return len(COMB.sub("", plain(s)))


W = 1456.0   # ความกว้างของเนื้อหาในสไลด์ (px)


# ------------------------------------------------------------------ ภาพ
def img_size(src):
    p = os.path.join(ROOT, src)
    try:
        with open(p, "rb") as f:
            d = f.read(32)
            if d[:8] == b"\x89PNG\r\n\x1a\n":
                return struct.unpack(">II", d[16:24])
            f.seek(2)
            while True:
                b = f.read(4)
                if len(b) < 4:
                    break
                marker, size = struct.unpack(">HH", b)
                if 0xFFC0 <= marker <= 0xFFCF and marker not in (0xFFC4, 0xFFC8, 0xFFCC):
                    h, w = struct.unpack(">xHH", f.read(5))
                    return w, h
                f.seek(size - 2, 1)
    except OSError:
        pass
    return 1600, 900


def img_tag(b):
    w, h = img_size(b["src"])
    return '<img src="%s" alt="%s" width="%d" height="%d">' % (b["src"], html.escape(b["alt"]), w, h)


def fig_nat_h(b):
    w, h = img_size(b["src"])
    return W * h / w


def fig_html(b, has_text):
    nat = fig_nat_h(b)
    if nat < 520:
        return '<div class="fig wide">%s</div>' % img_tag(b)
    figmin = int(min(nat, 690) * (0.7 if has_text else 0.5))
    return '<div class="fig" style="--figmin:%dpx">%s</div>' % (figmin, img_tag(b))


# ------------------------------------------------------------------ โค้ด
KW = (r"\b(?:def|return|if|elif|else|for|in|not|and|or|import|from|try|except|raise|as|is|None|True|False|"
      r"class|with|lambda|while|min|max|int|isinstance|type)\b")
TOK = re.compile(r"(?P<c>#[^\n]*)|(?P<s>\"(?:\\.|[^\"\\\n])*\"|'(?:\\.|[^'\\\n])*')|(?P<k>%s)|(?P<n>\b\d[\d_]*\b)" % KW)


def hl_py(text):
    out, pos = [], 0
    for m in TOK.finditer(text):
        out.append(esc(text[pos:m.start()]))
        out.append('<span class="tk-%s">%s</span>' % (m.lastgroup, esc(m.group())))
        pos = m.end()
    out.append(esc(text[pos:]))
    return "".join(out)


def hl_text(text):
    out = []
    for l in text.split("\n"):
        s, e = l.strip(), esc(l)
        if s.startswith("✗") or "REJECT" in s:
            e = '<span class="err">%s</span>' % e
        elif s.startswith("✓") or "ACCEPT" in s:
            e = '<span class="ok">%s</span>' % e
        elif s.startswith("$ ") or s.startswith(">>> "):
            e = '<span class="cmd">%s</span>' % e
        elif re.match(r"^(แบบที่ \d|score )", s):
            e = '<span class="dim">%s</span>' % e
        out.append(e)
    return "\n".join(out)


def pre_html(text, lang="", cls=""):
    body = hl_py(text) if lang == "python" else hl_text(text)
    return '<pre class="code %s"><button class="copy">คัดลอก</button><span class="t">%s</span></pre>' % (cls, body)


# ------------------------------------------------------------------ บล็อก -> HTML
def table_html(b):
    cols = len(b["head"])
    h = "".join("<th>%s</th>" % inline(c) for c in b["head"])
    rows = []
    for r in b["rows"]:
        tds = []
        for c in r + [""] * (cols - len(r)):
            cls = ' class="yes"' if c.startswith("✓") or c.startswith("✅") else ' class="no"' if c.startswith("✗") or c.startswith("❌") else ""
            tds.append("<td%s>%s</td>" % (cls, inline(c)))
        rows.append("<tr>%s</tr>" % "".join(tds))
    return '<table class="c%d"><thead><tr>%s</tr></thead><tbody>%s</tbody></table>' % (cols, h, "".join(rows))


def render(b):
    t = b["t"]
    if t == "p":
        first = b["lines"][0]
        if first.startswith("👀"):
            rest = [first[1:].strip()] + b["lines"][1:]
            return '<div class="note eye"><span class="lbl">ข้อสังเกต</span><span>%s</span></div>' % "<br>".join(inline(x) for x in rest)
        body = "<br>".join(inline(x) for x in b["lines"])
        if first.startswith("**ผลจริง"):
            return '<div class="note result">%s</div>' % body
        return "<p>%s</p>" % body
    if t == "lead":
        m = re.match(r"^\*\*(.+?)\*\*(.*)$", b["text"])
        if m:
            return '<h3 class="lead">%s<span>%s</span></h3>' % (inline(m.group(1)), inline(m.group(2)))
        return '<h3 class="lead">%s</h3>' % inline(b["text"])
    if t == "ul":
        return "<ul>%s</ul>" % "".join("<li>%s</li>" % inline(x) for x in b["items"])
    if t == "table":
        return table_html(b)
    if t == "code":
        return pre_html(b["text"], b["lang"])
    if t == "alert":
        cls = {"NOTE": "info", "TIP": "ok", "IMPORTANT": "warn"}.get(b["kind"], "info")
        return '<div class="note %s">%s</div>' % (cls, "".join(render(x) for x in b["blocks"]))
    return ""


# ------------------------------------------------------------------ สไลด์
def S(kicker, title, body, tag="", cls="", maxfs=1.4, lead=""):
    return {"kicker": kicker, "title": title, "body": body, "tag": tag, "cls": cls, "maxfs": maxfs, "lead": lead}


PROMPTS = []
PW = 138  # ตัวอักษรต่อบรรทัดของกล่องพรอมต์ (ประมาณ)


def prompt_slides(alert, kicker, title):
    code = next(x for x in alert["blocks"] if x["t"] == "code")
    how = next((x for x in alert["blocks"] if x["t"] == "p"), None)
    how = inline(how["lines"][0].replace("📋", "").strip()) if how else ""
    text = code["text"]
    pid = "prompt%d" % len(PROMPTS)
    PROMPTS.append(text)
    lines = text.split("\n")
    vis = [max(1, math.ceil(vlen(l) / PW)) for l in lines]
    total = sum(vis)
    n = 1 if total <= 24 else math.ceil(total / 26)
    cuts, acc, target = [0], 0, total / n
    for k, v in enumerate(vis):
        acc += v
        if len(cuts) < n and acc >= target * len(cuts) and k + 1 < len(lines):
            j = k + 1                      # ตัดที่บรรทัดว่างที่ใกล้ที่สุด
            near = [x for x in range(len(lines)) if not lines[x].strip() and abs(x - j) <= 6 and x > cuts[-1]]
            if near:
                j = min(near, key=lambda x: abs(x - j)) + 1
            cuts.append(j)
    cuts.append(len(lines))
    out = []
    for k in range(len(cuts) - 1):
        a, b = cuts[k], cuts[k + 1]
        part = "\n".join(lines[a:b]).strip("\n")
        label = "พรอมต์ทั้งหมด %d บรรทัด" % len(lines) if n == 1 else "ส่วนที่ %d/%d · บรรทัด %d–%d จาก %d" % (k + 1, n, a + 1, b, len(lines))
        body = ('<div class="pbar"><span class="how">%s</span><span class="plabel">%s</span>'
                '<button class="copy big" data-full="%s">คัดลอกพรอมต์ทั้งหมด</button></div>'
                '<pre class="code prompt"><span class="t">%s</span></pre>') % (how, label, pid, esc(part))
        out.append(S(kicker, "พรอมต์ · " + title, body, tag="Copy &amp; Paste", cls="pslide", maxfs=1.45))
    return out


# ------------------------------------------------------------------ สไลด์ที่เพิ่มเอง
def photo(src):
    return os.path.exists(os.path.join(ROOT, src))


def divider(big, title, sub_html, img="", small=""):
    style = ' style="background-image:url(%s)"' % img if img and photo(img) else ""
    cls = "divider photo" if style else "divider"
    body = ('<div class="shade"></div><div class="inner"><div class="small">%s</div><div class="big">%s</div><h1>%s</h1>'
            '<div class="sub">%s</div>%s</div>') % (small, big, inline(title), sub_html,
                                                    '<div class="imgnote">ภาพจำลอง</div>' if style else "")
    return {"raw": body, "cls": cls, "style": style, "title": "%s · %s" % (big, plain(title)), "kicker": "", "tag": "", "lead": ""}


# ------------------------------------------------------------------ ค้นบล็อกใน README.md
md = inline
SECS = []


def load(path="README.md", transform=None, latex=False):
    """อ่าน Markdown แล้วแบ่งเป็นหัวข้อ (ระดับ # ถึง ####) · คืน SECS = [{"level", "text", "blocks"}]
    transform = ฟังก์ชันแปลงข้อความก่อนอ่าน · latex=True = บทที่มีสมการ: $...$ และ $$...$$ ถูกเรียงพิมพ์ด้วย KaTeX
    (ทั้งข้อความจาก README และข้อความที่เขียนในโครงเรื่อง · ไม่แตะข้อความในโค้ด)"""
    del SECS[:]
    cur = None
    text = read(path)
    if transform:
        text = transform(text)
    if latex:
        MATH_ON[0] = True
        text = re.sub(r"^[ \t]*\$\$[ \t]*\n(.+?)\n[ \t]*\$\$[ \t]*$", lambda m: "$$" + " ".join(m.group(1).split("\n")) + "$$", text, flags=re.S | re.M)
        bare = re.sub(r"`[^`\n]+`", "", re.sub(r"```.*?```", "", text, flags=re.S))
        tex_many([(m.group(1) or m.group(2), bool(m.group(1))) for m in MATH_RE.finditer(bare)])
    for b in parse(text.split("\n")):
        if b["t"] == "h" and b["level"] <= 4:
            cur = {"level": b["level"], "text": b["text"], "blocks": []}
            SECS.append(cur)
        elif cur is not None:
            cur["blocks"].append(b)
    return SECS


def sec(prefix):
    """บล็อกของหัวข้อแรกที่ชื่อขึ้นต้นด้วย prefix"""
    for s in SECS:
        if s["text"].startswith(prefix):
            return s["blocks"]
    raise KeyError("ไม่พบหัวข้อที่ขึ้นต้นด้วย %r ใน README" % prefix)


def walk(blocks):
    for b in blocks:
        yield b
        if b["t"] in ("details", "alert"):
            yield from walk(b["blocks"])


def table(prefix, head0):
    """ตารางในหัวข้อ prefix (รวมที่อยู่ใน <details>) ที่หัวคอลัมน์แรกขึ้นต้นด้วย head0"""
    for b in walk(sec(prefix)):
        if b["t"] == "table" and plain(b["head"][0]).startswith(head0):
            return b
    raise KeyError("ไม่พบตารางที่คอลัมน์แรกขึ้นต้นด้วย %r ในหัวข้อ %r" % (head0, prefix))


def codes(prefix, lang=None):
    return [b for b in walk(sec(prefix)) if b["t"] == "code" and (lang is None or b["lang"] == lang)]


def para(prefix, start):
    for b in walk(sec(prefix)):
        if b["t"] == "p" and b["lines"][0].startswith(start):
            return b
    raise KeyError("ไม่พบย่อหน้าที่ขึ้นต้นด้วย %r ในหัวข้อ %r" % (start, prefix))


def prompt(prefix):
    """กล่อง > [!IMPORTANT] ที่มีพรอมต์ (code fence) ของหัวข้อ prefix"""
    for b in sec(prefix):
        if b["t"] == "alert" and any(x["t"] == "code" for x in b["blocks"]):
            return b
    raise KeyError("ไม่พบกล่องพรอมต์ในหัวข้อ %r" % prefix)


def eye(prefix, mark="👀"):
    """ข้อสังเกตของหัวข้อ (ย่อหน้าที่ขึ้นต้นด้วย mark) ไม่รวมเครื่องหมาย"""
    p = para(prefix, mark)
    return " ".join([p["lines"][0][len(mark):].strip()] + p["lines"][1:])


# ------------------------------------------------------------------ ชิ้นส่วนของสไลด์
SL, CTX = [], {"kicker": "", "group": ""}


def add(s):
    """ต่อสไลด์ (หรือรายการสไลด์) ท้ายเด็ค · group ใช้จัดกลุ่มในหน้าสารบัญ (ปุ่ม O)"""
    for x in s if isinstance(s, list) else [s]:
        x["group"] = CTX["group"]
        SL.append(x)


def slide(title, body, tag="", cls="", maxfs=1.4):
    """สไลด์ทั่วไป · cls="mid" จัดเนื้อหากลางหน้า · maxfs = ตัวคูณขนาดตัวอักษรสูงสุดที่ยอมให้ขยาย"""
    return S(CTX["kicker"], title, body, tag=tag, cls=cls, maxfs=maxfs)


def note(text, kind="eye", label="ข้อสังเกต"):
    if kind == "eye":
        return '<div class="note eye"><span class="lbl">%s</span><span>%s</span></div>' % (label, md(text))
    return '<div class="note %s">%s</div>' % (kind, md(text))


def fig(title, src, cap="", tag=""):
    """ภาพเต็มสไลด์ + คำบรรยาย 1 บรรทัด"""
    b = {"t": "img", "src": src, "alt": plain(title)}
    body = fig_html(b, bool(cap)) + ('<p class="cap">%s</p>' % md(cap) if cap else "")
    return slide(title, body, tag=tag, maxfs=1.1)


def explain(title, src, steps, post=""):
    """ภาพด้านซ้าย + ขั้นตอนเรียงเลขด้านขวา (3-5 ขั้น ขั้นละ 1-2 บรรทัด)"""
    side = "".join('<div class="stp"><span class="n">%d</span><span>%s</span></div>' % (k + 1, md(x)) for k, x in enumerate(steps))
    if not os.path.exists(os.path.join(ROOT, src)):
        return slide(title, '<div class="ex"><div class="side fitbox">%s%s</div></div>' % (side, post))
    img = img_tag({"t": "img", "src": src, "alt": plain(title)})
    return slide(title, '<div class="ex"><div class="fig">%s</div><div class="side fitbox">%s%s</div></div>' % (img, side, post), maxfs=1.25)


def tiles(items):
    """ตัวเลขใหญ่ · items = [(ป้าย, ตัวเลข, คำอธิบายสั้น, โทน "" | "ok" | "bad" | "warn")]"""
    out = []
    for k, num, s, tone in items:
        out.append('<div class="tile %s"><div class="k">%s</div><div class="num">%s</div><div class="s">%s</div></div>' % (tone, md(k), num, md(s)))
    return '<div class="tiles">%s</div>' % "".join(out)


def cards(items, cols=3):
    """การ์ด · items = [(หัวข้อ หรือ (เลข, หัวข้อ), ข้อความ หรือ HTML, โทน)]"""
    out = []
    for it in items:
        head, text, tone = (list(it) + [""])[:3]
        badge = ""
        if isinstance(head, tuple):
            badge, head = '<span class="n">%s</span>' % head[0], head[1]
        text = text if text.startswith("<") else "<p>%s</p>" % md(text)
        out.append('<div class="cardx %s"><h4>%s%s</h4>%s</div>' % (tone, badge, md(head), text))
    return '<div class="cards" style="--cols:%d">%s</div>' % (cols, "".join(out))


def eqbox(src, sub=""):
    """กล่องสมการตัวใหญ่ · src = LaTeX 1 สมการ หรือรายการของสมการ (เรียงบนลงล่าง) · sub = คำอธิบายใต้สมการ"""
    rows = "".join('<div class="row">%s</div>' % tex(x, True) for x in ([src] if isinstance(src, str) else src))
    return '<div class="eqbox">%s%s</div>' % (rows, '<div class="sub">%s</div>' % md(sub) if sub else "")


def parts(items, cols=0, numbered=True):
    """การ์ดอธิบายส่วนของสมการ สีเดียวกับในสมการ
    items = [(สี, สัญลักษณ์ LaTeX, หัวข้อ, ข้อความ, ป้ายเล็กเหนือการ์ด (เว้นได้), ค่าตัวอย่างแบบ mono (เว้นได้))]"""
    out = []
    for k, it in enumerate(items):
        color, sym, head, text, role, lab = (list(it) + ["", ""])[:6]
        out.append('<div class="part" style="--c:%s">%s<div class="top">%s<span class="sym">%s</span></div><h4>%s</h4><p>%s</p>%s</div>' % (
            PALETTE.get(color, color), '<div class="role">%s</div>' % md(role) if role else "",
            '<span class="n">%d</span>' % (k + 1) if numbered else "", tex(tc(color, sym)), md(head), md(text),
            '<span class="lab">%s</span>' % esc(lab) if lab else ""))
    return '<div class="parts" style="--cols:%d">%s</div>' % (cols or len(items), "".join(out))


def equation(title, src, items, lead="", post="", cols=0, numbered=True, sub=""):
    """สไลด์สมการ: บรรทัดนำ + สมการตัวใหญ่ (ใส่สีด้วย tc()) + การ์ดอธิบายทีละส่วน + หมายเหตุ"""
    body = ('<p class="eqlead">%s</p>' % md(lead) if lead else "") + eqbox(src, sub) + parts(items, cols, numbered) + post
    return slide(title, body, cls="mid", maxfs=1.3)


def versus(call, bad, good):
    """เทียบ 2 ฝั่ง · bad และ good = (ป้าย, วิธีคิด, ค่าตัวใหญ่, คำอธิบาย) · call = โค้ดที่เรียก (เว้นว่างได้)"""
    def box(cls, d):
        return ('<div class="sidebox %s"><div class="hd2">%s</div><div class="calc">%s</div><div class="bigv">%s</div><p>%s</p></div>'
                % (cls, d[0], esc(d[1]), esc(d[2]), md(d[3])))
    top = '<div class="callbox">%s</div>' % esc(call) if call else ""
    return top + '<div class="vs">%s%s</div>' % (box("bad", bad), box("good", good))


def bars(rows):
    """แท่งสัดส่วน · rows = [(ป้าย, คำอธิบายย่อย, ตัวตั้ง, ตัวหาร, ข้อความด้านขวา)]"""
    out = []
    for label, sub, num, den, text in rows:
        r = num / den if den else 0
        tone = "" if r >= 0.99 else "mid" if r >= 0.5 else "low"
        out.append('<div class="bar"><div class="lb">%s%s</div><div class="tr"><div class="fl %s" style="width:%d%%"></div></div>'
                   '<div class="vl">%s</div></div>' % (md(label), "<small>%s</small>" % md(sub) if sub else "", tone, round(r * 100), md(text)))
    return '<div class="bars">%s</div>' % "".join(out)


def tbl(title, t, pre="", post="", tag="ตารางหลัก"):
    """ตาราง 1 ตารางจาก README (ใช้เฉพาะจุดที่ผู้ฟังต้องโฟกัสกับข้อมูลรายแถว)"""
    return slide(title, pre + table_html(t) + post, tag=tag)


def code(title, text, lang="text", pre="", post="", maxfs=1.3):
    return slide(title, pre + pre_html(text, lang) + post, maxfs=maxfs)


def heat_color(v):
    """สีของช่องคะแนน 0.4 (แดง) ถึง 1.0 (เขียว)"""
    hue = max(0, min(130, (v - 0.4) / 0.6 * 130))
    return "hsl(%d,62%%,80%%)" % hue


def fileflow(t, mid, in_label="INPUT · ไฟล์ที่ใช้", out_label="OUTPUT · ไฟล์ที่ได้เพิ่มหลังรัน"):
    """แผนภาพ ไฟล์เข้า -> ขั้นตอน -> ไฟล์ออก จากตาราง 2 คอลัมน์ของ README (คอลัมน์ 1 = เข้า · คอลัมน์ 2 = ออก)"""
    ins = [r[0] for r in t["rows"] if r[0].strip()]
    outs = [r[1] for r in t["rows"] if len(r) > 1 and r[1].strip()]
    col = lambda cls, head, items: '<div class="ffcol %s"><div class="ffh">%s</div>%s</div>' % (
        cls, head, "".join('<div class="file">%s</div>' % md(x) for x in items))
    return ('<div class="ff">%s<div class="ffar">➜</div><div class="ffmid">%s</div><div class="ffar">➜</div>%s</div>'
            % (col("in", in_label, ins), mid, col("out", out_label, outs)))


def check_slide(key, items, ref, note_text, title):
    """รายการตรวจผลที่ติ๊กได้ · key ต้องไม่ซ้ำกันในเด็ค (ใช้จำค่าที่ติ๊กในเบราว์เซอร์)"""
    rows = "".join('<label class="chk"><input type="checkbox" data-k="%s-%d"><span>%s</span></label>' % (key, k, inline(x))
                   for k, x in enumerate(items))
    body = '<div class="checks">%s</div>' % rows
    if ref:
        body += '<div class="note result">%s</div>' % inline(ref)
    if note_text:
        body += '<div class="note eye"><span class="lbl">หมายเหตุ</span><span>%s</span></div>' % inline(note_text)
    return slide("ตรวจผลของคุณ · " + title, body, tag="Checklist", cls="cslide", maxfs=1.4)


def cover(title, sub, img, small="", hint=""):
    """หน้าปก: ภาพเต็มหน้า + ชื่อบท"""
    hint = hint or ('กด <span class="kbd">→</span> หรือ <span class="kbd">Space</span> เพื่อไปต่อ · <span class="kbd">O</span> สารบัญ · '
                    '<span class="kbd">F</span> เต็มจอ · คลิกภาพเพื่อขยาย')
    raw = ('<div class="shade"></div><div class="inner"><div class="small">%s</div><h1>%s</h1><div class="sub">%s</div>'
           '<div class="hint">%s</div><div class="imgnote">ภาพจำลอง</div></div>') % (esc(small), esc(title), esc(sub), hint)
    return {"raw": raw, "cls": "cover", "style": ' style="background-image:url(%s)"' % img, "title": "ปก", "kicker": "", "tag": "", "lead": ""}



def slide_html(s):
    dt = html.escape(s["title"] if "raw" in s else plain(s["title"]) + (" — " + s["lead"] if s.get("lead") else "") + (" (%s)" % s["pg"] if s.get("pg") else ""))
    if "raw" in s:
        return '<section class="slide %s"%s data-title="%s" data-group="%s">%s</section>' % (s["cls"], s["style"], dt, html.escape(s["group"]), s["raw"])
    tag = '<span class="tag">%s</span>' % s["tag"] if s["tag"] else ""
    pg = '<span class="pg">%s</span>' % s["pg"] if s.get("pg") else ""
    return ('<section class="slide %s" data-title="%s" data-group="%s" data-max="%.2f"><header class="hd"><div class="kicker">%s</div>'
            '<h2><span class="tt">%s</span>%s%s</h2></header><div class="body">%s</div></section>') % (
        s["cls"], dt, html.escape(s["group"]), s["maxfs"], inline(s["kicker"]), inline(s["title"]), tag, pg, s["body"])


CSS = r"""
:root{--navy:#12305e;--teal:#0f8f8c;--teal-soft:#e2f5f4;--orange:#e87f1c;--orange-soft:#fff1e3;--red:#c92a2a;--red-soft:#fdecec;
--green:#15803d;--green-soft:#e7f7ec;--ink:#1c2533;--muted:#5b6b80;--line:#d8e0ec;--bg:#f5f7fb;--card:#fff;--code:#0e1a2b;
--font:'IBM Plex Sans Thai','Leelawadee UI','Noto Sans Thai','Segoe UI',sans-serif;--mono:'JetBrains Mono','Cascadia Code',Consolas,monospace}
*{box-sizing:border-box}
html,body{margin:0;height:100%;background:#070d18;overflow:hidden;font-family:var(--font);color:var(--ink)}
#stage{position:fixed;inset:0;display:flex;align-items:center;justify-content:center}
#deck{width:1600px;height:900px;position:relative;transform-origin:center center;flex:none}
.slide{position:absolute;inset:0;background:var(--bg);padding:40px 72px 44px;display:none;flex-direction:column;overflow:hidden}
.slide.active,.slide.measure{display:flex}
.slide.measure{visibility:hidden}
.slide.active{animation:fade .25s ease}
@keyframes fade{from{opacity:0}to{opacity:1}}
.hd{flex:none;margin-bottom:16px;padding-bottom:12px;border-bottom:2px solid var(--line)}
.kicker{font-size:17px;font-weight:600;color:var(--teal);letter-spacing:.01em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.kicker code{font-size:.9em;background:none;padding:0;color:inherit}
h2{font-size:36px;line-height:1.22;margin:3px 0 0;color:var(--navy);font-weight:700;display:flex;align-items:center;gap:14px}
h2 .tt{min-width:0}
h2 code{font-size:.88em}
.tag{flex:none;font-size:15px;font-weight:600;background:var(--orange-soft);color:#9a4d06;border:1px solid #f6d3ad;border-radius:999px;padding:3px 13px;white-space:nowrap}
.pg{flex:none;margin-left:auto;font-size:16px;font-weight:500;color:var(--muted);white-space:nowrap}
.slide .no{display:none;position:absolute;right:26px;bottom:12px;font-size:13px;color:#8796ab}
.slide .dk{position:absolute;left:72px;bottom:12px;font-size:13px;color:#8796ab}
.body{flex:1;min-height:0;display:flex;flex-direction:column;gap:.5em;font-size:calc(23px*var(--fs,1));overflow:hidden}
.body.scroll{overflow:auto}
.body>*{flex:none;margin:0}
p{line-height:1.55}
ul{padding-left:1.3em;margin:0}
li{line-height:1.5;margin:.22em 0}
b,strong{color:var(--navy)}
a{color:#1d5fd0;text-decoration:none;border-bottom:1px solid rgba(29,95,208,.3)}
.xref{color:var(--navy);font-weight:600}
code{font-family:var(--mono);font-size:.84em;background:#e6edf7;color:#0b3b7a;padding:.08em .38em;border-radius:5px;overflow-wrap:break-word}
pre,code{font-variant-ligatures:none}
h3.lead{font-size:1.14em;color:var(--navy);font-weight:700;line-height:1.35;padding-left:.6em;border-left:5px solid var(--teal)}
h3.lead span{font-weight:400;color:var(--muted);font-size:.86em}
h3.lead span b{color:var(--muted)}
table{border-collapse:separate;border-spacing:0;width:100%;font-size:.9em;background:#fff;border:1px solid var(--line);border-radius:10px;overflow:hidden}
th,td{padding:.4em .62em;text-align:left;vertical-align:top;line-height:1.42;border-bottom:1px solid var(--line)}
th{background:var(--navy);color:#fff;font-weight:600}
th code{background:rgba(255,255,255,.16);color:#fff}
tbody tr:last-child td{border-bottom:0}
tbody tr:nth-child(even) td{background:#f6f9fd}
td:first-child{font-weight:500}
td.yes{color:#0f5132}td.no{color:#9b1c1c}
table.c6,table.c7{font-size:.84em}
.v{font-weight:700;font-size:.92em;padding:.05em .5em;border-radius:6px;white-space:nowrap}
.v.accept{background:var(--green-soft);color:var(--green)}
.v.reject{background:var(--red-soft);color:var(--red)}
.note{border-left:6px solid var(--teal);background:var(--teal-soft);padding:.55em .9em;border-radius:8px;line-height:1.5}
.note>*{margin:0}
.note>*+*{margin-top:.4em}
.note.ok{border-color:var(--green);background:var(--green-soft)}
.note.warn{border-color:var(--orange);background:var(--orange-soft)}
.note.bad{border-color:var(--red);background:var(--red-soft)}
.note.result{border-color:var(--navy);background:#e9eff8}
.note.eye{border-color:var(--orange);background:var(--orange-soft);display:flex;gap:.8em;align-items:baseline}
.note.eye>*+*{margin-top:0}
.note .lbl{flex:none;font-size:.72em;font-weight:700;letter-spacing:.04em;color:#fff;background:var(--orange);border-radius:6px;padding:.15em .6em}
pre.code{position:relative;background:var(--code);color:#dbe7ff;font-family:var(--mono);font-size:.74em;line-height:1.5;padding:.85em 1.1em;border-radius:10px;white-space:pre-wrap;overflow-wrap:anywhere;tab-size:4}
pre.code.term{border-left:6px solid var(--teal)}
pre .copy{position:absolute;top:8px;right:8px;font-family:var(--font);font-size:14px;background:#26406a;color:#fff;border:0;border-radius:7px;padding:5px 12px;cursor:pointer;opacity:.85}
pre .copy:hover,.copy.big:hover{background:var(--teal);opacity:1}
pre .err{color:#ff9b9b}pre .ok{color:#86e3ae}pre .dim{color:#8ea3c4}pre .cmd{color:#ffd28a}
.tk-c{color:#7f93b5;font-style:italic}.tk-s{color:#a5e8b5}.tk-k{color:#ffb86b}.tk-n{color:#8fd3ff}
.fig{flex:1 1 0;min-height:var(--figmin,260px);display:flex;align-items:center;justify-content:center}
.fig img{max-width:100%;max-height:100%;width:auto;height:auto;object-fit:contain;border-radius:10px;box-shadow:0 6px 22px rgba(18,48,94,.16);background:#fff;cursor:zoom-in}
.fig.wide{flex:none;min-height:0;display:block}
.fig.wide img{width:100%;max-height:none}
.body>.fig.wide:only-child{margin:auto 0}
.figrow{flex:1 1 0;min-height:0;display:flex;gap:24px;align-items:center}
.figrow .fig{height:100%}
.cols{display:flex;gap:26px;align-items:flex-start}
.cols .col{flex:1;min-width:0;display:flex;flex-direction:column;gap:.5em}
.cols .col>*{margin:0}
.cmp pre.code{font-size:.72em}
.fails{display:flex;flex-direction:column;gap:.45em}
.fails .cardx{padding:.4em .8em}
.slide.mid .body{justify-content:center;gap:.8em}
.cardx h4 code{font-size:.9em}
.fails .cardx p{font-size:.8em;font-family:var(--mono);line-height:1.45}
/* พรอมต์ */
.pbar{display:flex;align-items:center;gap:16px;background:var(--orange-soft);border:1px solid #f6d3ad;border-radius:10px;padding:.45em .8em;font-size:.86em}
.pbar .how{flex:1;min-width:0}
.pbar .plabel{flex:none;color:var(--muted);font-size:.9em}
.copy.big{flex:none;font-family:var(--font);font-size:19px;font-weight:700;background:var(--orange);color:#fff;border:0;border-radius:9px;padding:9px 20px;cursor:pointer;box-shadow:0 3px 10px rgba(232,127,28,.35)}
.copy.done{background:var(--green)!important}
pre.code.prompt{font-size:.76em;line-height:1.52;border:2px solid #f08a24}
.full{display:none}
/* checklist */
.checks{display:flex;flex-direction:column;gap:.45em}
.chk{display:flex;gap:.7em;align-items:flex-start;background:#fff;border:1px solid var(--line);border-radius:10px;padding:.5em .8em;cursor:pointer;line-height:1.45}
.chk input{width:1.15em;height:1.15em;margin-top:.2em;flex:none;accent-color:var(--teal)}
.chk:has(input:checked){background:var(--green-soft);border-color:#a7dcb8}
/* ภาพ + ขั้นตอน */
.fitbox{overflow:hidden}
.ex{flex:1 1 0;min-height:0;display:flex;gap:30px;align-items:stretch}
.ex .fig{flex:1.5 1 0;min-height:0;min-width:0}
.ex .side{flex:1 1 0;min-width:0;display:flex;flex-direction:column;justify-content:center;gap:.5em}
.ex .side>*{flex:none;margin:0}
.stp{display:flex;gap:.7em;align-items:flex-start;background:#fff;border:1px solid var(--line);border-radius:12px;padding:.5em .8em;line-height:1.45;box-shadow:0 2px 6px rgba(18,48,94,.05)}
.stp .n{flex:none;width:1.75em;height:1.75em;border-radius:50%;background:var(--navy);color:#fff;font-weight:700;display:flex;align-items:center;justify-content:center;font-size:.88em;margin-top:.05em}
.cap{color:var(--muted);line-height:1.5;text-align:center}
.cap b{color:var(--navy)}
/* ตัวเลขใหญ่ */
.tiles{display:flex;gap:20px;align-items:stretch}
.tile{flex:1;min-width:0;background:#fff;border:1px solid var(--line);border-top:7px solid var(--teal);border-radius:14px;padding:.6em .85em .7em;box-shadow:0 3px 10px rgba(18,48,94,.06)}
.tile .k{font-size:.74em;font-weight:600;color:var(--muted);letter-spacing:.02em}
.tile .num{font-size:2.05em;font-weight:700;color:var(--navy);line-height:1.2;white-space:nowrap}
.tile .num small{font-size:.5em;font-weight:600;color:var(--muted)}
.tile .s{font-size:.8em;color:var(--muted);line-height:1.4}
.tile.ok{border-top-color:var(--green)}.tile.ok .num{color:var(--green)}
.tile.bad{border-top-color:var(--red)}.tile.bad .num{color:var(--red)}
.tile.warn{border-top-color:var(--orange)}
/* การ์ด */
.cards{display:grid;gap:18px;grid-template-columns:repeat(var(--cols,3),minmax(0,1fr))}
.cardx{background:#fff;border:1px solid var(--line);border-left:7px solid var(--teal);border-radius:14px;padding:.65em .9em;box-shadow:0 3px 10px rgba(18,48,94,.05);display:flex;flex-direction:column;gap:.3em}
.cardx>*{margin:0}
.cardx h4{font-size:1.02em;color:var(--navy);line-height:1.35}
.cardx p,.cardx li{font-size:.88em;line-height:1.48;color:#2b3648}
.cardx .n{display:inline-flex;width:1.6em;height:1.6em;border-radius:50%;background:var(--navy);color:#fff;align-items:center;justify-content:center;font-size:.85em;margin-right:.45em}
.cardx.ok{border-left-color:var(--green)}.cardx.bad{border-left-color:var(--red)}.cardx.warn{border-left-color:var(--orange)}.cardx.navy{border-left-color:var(--navy)}
.cardx .chips{display:flex;flex-direction:column;gap:.3em}
.cardx .chips div{font-size:.86em;line-height:1.45}
/* สมการ (KaTeX) */
.katex{font-size:1.1em;font-family:KaTeX_Main,'IBM Plex Sans Thai','Leelawadee UI','Times New Roman',serif}
.katex-display{margin:0}
.eqbox{background:#fff;border:2px solid var(--line);border-radius:18px;padding:.3em .6em;text-align:center;box-shadow:0 4px 14px rgba(18,48,94,.06);font-size:2.2em;color:var(--ink);display:flex;flex-direction:column;gap:.12em}
.eqbox .row+.row{border-top:1px dashed var(--line);padding-top:.12em}
.eqbox .sub{font-size:.36em;color:var(--muted);line-height:1.4;padding-bottom:.3em}
.eqlead{color:var(--muted);font-size:.95em;line-height:1.45}
.parts{display:grid;gap:16px;grid-template-columns:repeat(var(--cols,4),minmax(0,1fr))}
.part{background:#fff;border:1px solid var(--line);border-top:9px solid var(--c);border-radius:14px;padding:.55em .8em .65em;display:flex;flex-direction:column;gap:.22em;box-shadow:0 3px 10px rgba(18,48,94,.05)}
.part>*{margin:0}
.part .role{font-size:.64em;font-weight:700;letter-spacing:.08em;color:var(--muted)}
.part .top{display:flex;align-items:center;gap:.5em;min-height:2.3em}
.part .n{flex:none;display:inline-flex;width:1.7em;height:1.7em;border-radius:50%;background:var(--c);color:#fff;align-items:center;justify-content:center;font-size:.8em;font-weight:700}
.part .sym{font-size:1.3em;color:var(--c)}
.part h4{font-size:1em;color:var(--navy);line-height:1.3}
.part p{font-size:.86em;line-height:1.45;color:#2b3648}
.part .lab{align-self:flex-start;font-family:var(--mono);font-size:.74em;color:#0b6b69;background:var(--teal-soft);border-radius:6px;padding:.12em .5em;margin-top:.15em}
/* เทียบ 2 ฝั่ง */
.vs{display:flex;gap:26px;align-items:stretch}
.vs .sidebox{flex:1;min-width:0;border-radius:16px;padding:.8em 1em;border:2px solid var(--line);background:#fff;display:flex;flex-direction:column;gap:.4em}
.vs .sidebox>*{margin:0}
.vs .bad{border-color:#f0b4b4;background:#fff8f8}.vs .good{border-color:#a7dcb8;background:#f5fcf7}
.vs .hd2{font-size:.8em;font-weight:700;letter-spacing:.03em}
.vs .bad .hd2{color:var(--red)}.vs .good .hd2{color:var(--green)}
.vs .bigv{font-family:var(--mono);font-size:2.6em;font-weight:700;line-height:1.15}
.vs .bad .bigv{color:var(--red)}.vs .good .bigv{color:var(--green)}
.vs .calc{font-family:var(--mono);font-size:.95em;color:#2b3648}
.callbox{background:var(--code);color:#dbe7ff;font-family:var(--mono);border-radius:12px;padding:.6em 1em;font-size:1.05em;text-align:center}
.formula{background:#fff;border:2px solid var(--navy);border-radius:16px;padding:.7em 1em;text-align:center;font-size:1.25em;font-weight:700;color:var(--navy);line-height:1.5}
.bigq{font-size:1.9em;font-weight:700;color:var(--navy);line-height:1.35;margin:auto 0 .2em!important}
.bigq em{font-style:normal;color:var(--orange)}
.bigsub{font-size:1.05em;color:var(--muted);line-height:1.6;margin-bottom:auto!important}
/* แท่ง */
.bars{display:flex;flex-direction:column;gap:.5em}
.bar{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(0,1fr) 7.5em;gap:18px;align-items:center;background:#fff;border:1px solid var(--line);border-radius:12px;padding:.45em .85em}
.bar .lb{line-height:1.4}
.bar .lb small{display:block;color:var(--muted);font-size:.8em}
.bar .tr{height:1.15em;background:#e7edf5;border-radius:999px;overflow:hidden}
.bar .fl{height:100%;border-radius:999px;background:var(--green);min-width:6px}
.bar .fl.mid{background:var(--orange)}.bar .fl.low{background:var(--red)}
.bar .vl{font-family:var(--mono);font-weight:700;color:var(--navy);text-align:right;font-size:.92em}
/* ตารางสี 18 Trial */
.heat{display:grid;grid-template-columns:auto repeat(6,1fr);gap:8px;align-items:stretch}
.heat .hh{font-family:var(--mono);font-size:.74em;font-weight:600;color:var(--navy);text-align:center;padding:.2em 0}
.heat .hr{font-size:.82em;color:var(--muted);display:flex;align-items:center;padding-right:.4em;white-space:nowrap}
.heat .hc{border-radius:10px;text-align:center;font-family:var(--mono);font-weight:700;font-size:1.15em;padding:.55em 0;color:#12305e}
.heat .grp{grid-column:span 4;text-align:center;font-size:.8em;font-weight:700;color:#fff;background:var(--teal);border-radius:8px;padding:.15em}
.heat .grp.val{grid-column:span 2;background:var(--orange)}
/* Input -> LAB -> Output */
.ff{display:flex;gap:22px;align-items:center}
.ffcol{flex:1;min-width:0;display:flex;flex-direction:column;gap:.42em}
.ffh{font-size:.78em;font-weight:700;letter-spacing:.04em;color:var(--muted)}
.file{background:#fff;border:1px solid var(--line);border-left:7px solid var(--teal);border-radius:10px;padding:.42em .7em;font-size:.9em;line-height:1.42}
.ffcol.out .file{border-left-color:var(--orange)}
.ffmid{flex:none;width:8em;text-align:center;background:var(--navy);color:#fff;border-radius:18px;padding:1.1em .5em;font-weight:700;font-size:1.1em;line-height:1.3;position:relative}
.ffmid small{display:block;font-weight:500;font-size:.62em;color:#b9d2f5;margin-top:.3em}
.ffar{flex:none;font-size:2em;color:var(--orange);font-weight:700}
/* กลุ่มข้อตรวจ */
.ck{display:flex;gap:.55em;align-items:baseline;font-size:.86em;line-height:1.45}
.ck code{flex:none}
/* แผนของบท */
.road{display:flex;gap:26px;align-items:stretch}
.road .partbox{flex:1;border-radius:18px;padding:.8em 1em 1em;background:#fff;border:2px solid var(--line);display:flex;flex-direction:column;gap:.55em}
.road .partbox>*{margin:0}
.road .ph{font-size:1.25em;font-weight:700;color:var(--navy)}
.road .ph small{font-size:.6em;font-weight:600;color:var(--teal);margin-left:.6em}
.road .secbox{border-left:7px solid var(--teal);background:var(--bg);border-radius:10px;padding:.5em .8em}
.road .secbox b{display:block;font-size:1.02em}
.road .secbox span{font-size:.86em;color:#2b3648;line-height:1.45;display:block}
.road .partbox.lab .secbox{border-left-color:var(--orange)}
/* ปก และหน้าคั่น */
.cover,.divider{padding:0;background:linear-gradient(135deg,#0d2447 0%,#163f7a 62%,#0f8f8c 140%);background-size:cover;background-position:center;color:#fff}
.cover .shade,.divider.photo .shade{position:absolute;inset:0;background:linear-gradient(90deg,rgba(6,13,26,.96) 0%,rgba(6,13,26,.86) 46%,rgba(6,13,26,.25) 80%)}
.inner{position:relative;height:100%;padding:90px 96px 70px;display:flex;flex-direction:column;max-width:1120px;font-size:25px}
.divider:not(.photo) .inner{max-width:1400px}
.inner .small{font-size:21px;font-weight:600;color:#8fe0dc;letter-spacing:.03em;min-height:28px}
.inner .big{font-size:120px;font-weight:700;line-height:1.05;color:#fff;margin-top:8px}
.inner h1{font-size:54px;line-height:1.2;margin:10px 0 0;color:#fff}
.cover .inner h1{font-size:68px;margin-top:120px}
.inner .sub{margin-top:26px;color:#d6e4fb;line-height:1.55;display:flex;flex-direction:column;gap:.55em}
.cover .inner .sub{font-size:34px;color:#cfe0ff}
.inner .sub p,.inner .sub ul{margin:0}
.inner b{color:#fff}
.inner code{background:rgba(255,255,255,.14);color:#fff}
.inner a{color:#9fd8ff;border-bottom-color:rgba(159,216,255,.4)}
.inner .xref{color:#fff}
.inner .hint{margin-top:auto;font-size:19px;color:#9fb6dd}
.inner .v.accept{background:rgba(134,227,174,.2);color:#9af0bf}.inner .v.reject{background:rgba(255,155,155,.2);color:#ffb3b3}
.imgnote{position:absolute;right:22px;bottom:14px;font-size:13px;color:#fff;background:rgba(0,0,0,.45);padding:2px 10px;border-radius:7px}
.facts{display:flex;gap:18px;margin-top:10px}
.facts div:last-child{flex:2}
.facts div{flex:1;background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.22);border-radius:14px;padding:16px 20px;font-size:26px;font-weight:600;color:#fff}
.facts .fl{display:block;font-size:16px;font-weight:500;color:#9fd8ff;margin-bottom:4px}
.kbd{display:inline-block;border:1px solid #9fb6dd;border-bottom-width:3px;border-radius:7px;padding:0 9px;font-family:var(--mono);font-size:.8em;margin:0 2px;background:rgba(255,255,255,.06)}
.body .kbd{border-color:#9aa9bf;background:#fff}
/* ส่วนควบคุม */
#bar{position:fixed;left:0;bottom:0;height:4px;background:var(--orange);transition:width .25s;z-index:5}
#hud{position:fixed;right:14px;bottom:12px;display:flex;gap:6px;align-items:center;z-index:6;font-family:var(--font);opacity:.35;transition:opacity .2s}
#hud:hover{opacity:1}
#hud button{background:rgba(18,48,94,.85);color:#fff;border:1px solid rgba(255,255,255,.3);border-radius:9px;height:36px;min-width:38px;font-size:16px;cursor:pointer;padding:0 10px}
#hud button:hover{background:var(--teal)}
#count{color:#fff;background:rgba(18,48,94,.85);border-radius:9px;padding:7px 10px;font-size:15px;min-width:80px;text-align:center}
body.ov #stage{display:none}
#ov{display:none;position:fixed;inset:0;overflow:auto;padding:26px 32px 60px;z-index:10;background:#0b1424;color:#dbe7ff}
body.ov #ov{display:block}
#ov h4{margin:22px 0 10px;font-size:19px;color:#8fe0dc;font-weight:600;border-bottom:1px solid #22324d;padding-bottom:6px}
#ov .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));gap:10px}
#ov .th{background:#16233a;border:2px solid transparent;border-radius:9px;padding:9px 12px;cursor:pointer;font-size:15px;line-height:1.4}
#ov .th:hover,#ov .th.cur{border-color:var(--orange)}
#ov .th span{color:var(--orange);font-weight:700;margin-right:6px}
#lb{display:none;position:fixed;inset:0;z-index:20;background:rgba(4,8,16,.95);overflow:auto;padding:18px;text-align:center;cursor:zoom-out}
#lb.on{display:block}
#lb img{width:min(100%,2000px);height:auto;border-radius:8px;background:#fff}
@media print{html,body{overflow:visible;height:auto;background:#fff}#hud,#bar,#ov,#lb,.copy{display:none!important}.slide .no{display:block}
#stage{position:static;display:block}#deck{transform:none!important;height:auto}
.slide{display:flex!important;position:relative;width:1600px;height:900px;page-break-after:always;break-after:page;animation:none}}
@page{size:1600px 900px;margin:0}
"""

JS = r"""
(function(){
  const deck=document.getElementById('deck');
  const slides=[...deck.querySelectorAll('.slide')];
  const N=slides.length; let cur=0;
  slides.forEach((s,k)=>{ if(!s.classList.contains('cover')){ const n=document.createElement('div'); n.className='no'; n.textContent=(k+1)+' / '+N; s.appendChild(n);} });
  function fit(){ deck.style.transform='scale('+Math.min(innerWidth/1600,innerHeight/900)+')'; }
  /* ปรับขนาดตัวอักษรของแต่ละสไลด์ให้พอดีหน้า: เริ่มที่ค่าสูงสุด แล้วลดจนไม่ล้น */
  function fitSlide(s){
    const body=s.querySelector('.body'); if(!body) return;
    const on=s.classList.contains('active'); if(!on) s.classList.add('measure');
    body.classList.remove('scroll');
    let fs=parseFloat(s.dataset.max||'1.4');
    const boxes=[body,...body.querySelectorAll('.fitbox')];
    const over=()=>boxes.some(b=>b.scrollHeight>b.clientHeight+3||b.scrollWidth>b.clientWidth+1);
    s.style.setProperty('--fs',fs);
    while(over()&&fs>0.62){ fs=Math.round((fs-0.03)*100)/100; s.style.setProperty('--fs',fs); }
    s.dataset.fs=fs; s.dataset.over=over()?'1':'0';
    if(over()) body.classList.add('scroll');
    if(!on) s.classList.remove('measure');
  }
  function fitAll(){ slides.forEach(fitSlide); document.documentElement.dataset.fitted='1'; }
  function go(i,push){
    cur=Math.max(0,Math.min(N-1,i));
    slides.forEach((s,k)=>s.classList.toggle('active',k===cur));
    document.getElementById('count').textContent=(cur+1)+' / '+N;
    document.getElementById('bar').style.width=((cur+1)/N*100)+'%';
    if(push!==false){ try{ history.replaceState(null,'','#'+(cur+1)); }catch(e){} }
    document.querySelectorAll('#ov .th').forEach((t,k)=>t.classList.toggle('cur',k===cur));
  }
  const next=()=>go(cur+1), prev=()=>go(cur-1);
  function fs(){ if(!document.fullscreenElement){ const r=document.documentElement; r.requestFullscreen&&r.requestFullscreen(); } else document.exitFullscreen&&document.exitFullscreen(); }
  const ovEl=document.getElementById('ov'); let grid=null,last=null;
  slides.forEach((s,k)=>{
    if(s.dataset.group!==last){ last=s.dataset.group; const h=document.createElement('h4'); h.textContent=last; ovEl.appendChild(h); grid=document.createElement('div'); grid.className='grid'; ovEl.appendChild(grid); }
    const d=document.createElement('div'); d.className='th';
    const n=document.createElement('span'); n.textContent=k+1; d.appendChild(n); d.appendChild(document.createTextNode(s.dataset.title||''));
    d.onclick=()=>{ go(k); ov(false); }; grid.appendChild(d);
  });
  function ov(on){ const v=on===undefined?!document.body.classList.contains('ov'):on; document.body.classList.toggle('ov',v);
    if(v){ const c=ovEl.querySelector('.th.cur'); c&&c.scrollIntoView({block:'center'}); } }
  const lb=document.getElementById('lb'), lbi=lb.querySelector('img');
  deck.addEventListener('click',e=>{ const im=e.target.closest('.fig img'); if(im){ lbi.src=im.src; lbi.alt=im.alt; lb.classList.add('on'); lb.scrollTop=0; } });
  lb.addEventListener('click',()=>lb.classList.remove('on'));
  document.addEventListener('keydown',e=>{
    if(e.target.tagName==='INPUT'||e.ctrlKey||e.metaKey||e.altKey) return;
    const k=e.key;
    if(lb.classList.contains('on')){ if(k==='Escape'||k==='Enter'||k===' '){ e.preventDefault(); lb.classList.remove('on'); } return; }
    if(['ArrowRight','PageDown',' ','Enter'].includes(k)){ e.preventDefault(); next(); }
    else if(['ArrowLeft','PageUp','Backspace'].includes(k)){ e.preventDefault(); prev(); }
    else if(k==='Home') go(0); else if(k==='End') go(N-1);
    else if(k==='f'||k==='F') fs(); else if(k==='o'||k==='O') ov();
    else if(k==='Escape'&&document.body.classList.contains('ov')) ov(false);
  });
  document.getElementById('bn').onclick=next; document.getElementById('bp').onclick=prev;
  document.getElementById('bf').onclick=fs; document.getElementById('bo').onclick=()=>ov();
  let tx=null;
  document.addEventListener('touchstart',e=>{ tx=e.touches[0].clientX; },{passive:true});
  document.addEventListener('touchend',e=>{ if(tx===null) return; const dx=e.changedTouches[0].clientX-tx; tx=null; if(Math.abs(dx)>60)(dx<0?next:prev)(); });
  function copyText(text,btn,label){
    const done=()=>{ btn.textContent='คัดลอกแล้ว ✓'; btn.classList.add('done'); setTimeout(()=>{ btn.textContent=label; btn.classList.remove('done'); },1600); };
    const fallback=()=>{ const ta=document.createElement('textarea'); ta.value=text; ta.style.position='fixed'; ta.style.opacity='0'; document.body.appendChild(ta); ta.select(); try{ document.execCommand('copy'); }catch(e){} ta.remove(); done(); };
    if(navigator.clipboard&&window.isSecureContext) navigator.clipboard.writeText(text).then(done,fallback); else fallback();
  }
  window.promptText=id=>document.getElementById(id).textContent;
  document.querySelectorAll('.copy').forEach(b=>{
    const label=b.textContent;
    b.addEventListener('click',ev=>{ ev.stopPropagation();
      const text=b.dataset.full?window.promptText(b.dataset.full):b.parentElement.querySelector('.t').textContent;
      copyText(text,b,label); });
  });
  document.querySelectorAll('.chk input').forEach(c=>{
    const key='slides:'+location.pathname+':'+c.dataset.k;
    try{ c.checked=localStorage.getItem(key)==='1'; }catch(e){}
    c.addEventListener('change',()=>{ try{ localStorage.setItem(key,c.checked?'1':'0'); }catch(e){} });
  });
  addEventListener('resize',fit);
  addEventListener('hashchange',()=>{ const n=parseInt(location.hash.slice(1)); if(n) go(n-1,false); });
  fit(); const start=parseInt(location.hash.slice(1)); go(start?start-1:0,false);
  fitAll();
  if(document.fonts&&document.fonts.ready) document.fonts.ready.then(fitAll);
  addEventListener('load',fitAll);
})();
"""


def write(slides, out="Slides.html", title="Slides"):
    """เขียนไฟล์สไลด์ที่ <บท>/<out> · title = ชื่อบนแท็บของเบราว์เซอร์"""
    out_path = os.path.join(ROOT, out)
    body = "\n".join(slide_html(s) for s in slides)
    full = "\n".join('<pre class="full" id="prompt%d">%s</pre>' % (k, esc(t)) for k, t in enumerate(PROMPTS))
    page = """<!doctype html>
<html lang="th">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Thai:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>%s</style>
</head>
<body>
<!-- สร้างจาก README.md ด้วย tools/build_slides.py · ห้ามแก้ไฟล์นี้ด้วยมือ ให้แก้ README.md แล้วสร้างใหม่ -->
<div id="stage"><div id="deck">
%s
</div></div>
%s
<div id="bar"></div>
<div id="hud"><button id="bo" title="สารบัญ (O)">☰</button><button id="bp" title="ก่อนหน้า (←)">‹</button><span id="count"></span><button id="bn" title="ถัดไป (→)">›</button><button id="bf" title="เต็มจอ (F)">⛶</button></div>
<div id="ov"></div>
<div id="lb"><img alt=""></div>
<script>%s</script>
</body>
</html>
""" % (html.escape(title), (katex_css(body) if 'class="katex' in body else "") + CSS, body, full, JS)
    open(out_path, "w", encoding="utf-8", newline="\n").write(page)
    print("wrote %s · %d slides · %d prompts · %.0f KB" % (os.path.relpath(out_path, ROOT), len(slides), len(PROMPTS), len(page.encode("utf-8")) / 1024))
    return slides
