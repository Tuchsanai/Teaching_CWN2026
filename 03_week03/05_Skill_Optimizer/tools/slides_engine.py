#!/usr/bin/env python3
"""เครื่องมือเรนเดอร์ของสไลด์ (ใช้โดย tools/build_slides.py)

- อ่าน Markdown ของ README.md เป็นบล็อก (parse) และแปลงบล็อกเป็น HTML (render)
- สไลด์พรอมต์ (ข้อความตรงตัวอักษรจาก README.md) · รายการตรวจผลของ LAB · ผลดิบของ gate · โค้ดจริงจาก runs/
- CSS และ JS ของสไลด์ · ขนาดตัวอักษรของแต่ละสไลด์ปรับตอนเปิดไฟล์ให้พอดีหน้า (fitAll)
"""
import html, json, math, os, re, struct, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "Skill_Optimizer_Slides.html")
DECK = "Skill Optimizer · money-coder"


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


# ------------------------------------------------------------------ ข้อความในบรรทัด
def esc(s):
    return html.escape(s, quote=False)


def inline(s):
    codes = []

    def keep(m):
        codes.append(m.group(1))
        return "\x00%d\x00" % (len(codes) - 1)

    s = re.sub(r"`([^`]+)`", keep, s)
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
    return re.sub(r"\x00(\d+)\x00", lambda m: "<code>%s</code>" % esc(codes[int(m.group(1))]), s)


COMB = re.compile("[ัิ-ฺ็-๎]")


def plain(s):
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
    s = re.sub(r"</?(?:br|sub|sup|code)>", " ", s)
    return re.sub(r"\s+", " ", s.replace("**", "").replace("`", "")).strip()


def vlen(s):
    return len(COMB.sub("", plain(s)))


# ------------------------------------------------------------------ ประมาณความสูง (px ที่ขนาดตัวอักษรปกติ)
FS, W = 23.0, 1456.0
BUD = 600.0          # ความสูงของเนื้อหาที่พอดี 1 สไลด์
SOFT = 0.55 * BUD    # ถ้าเกินนี้ หัวข้อย่อยถัดไปขึ้นสไลด์ใหม่
CAP = 1.22 * BUD     # เกินนี้ต้องแบ่ง (ที่เหลือให้ JS ย่อตัวอักษร)


def text_h(s, width, fs=FS):
    return max(1, math.ceil(vlen(s) * fs * 0.5 / width)) * fs * 1.5


def table_rows_h(b, width=W):
    fs = FS * 0.9
    cols = len(b["head"])
    rows = [b["head"]] + [r + [""] * (cols - len(r)) for r in b["rows"]]

    def cell_w(c):
        return max(vlen(x) for x in re.split(r"<br>", c)) * fs * 0.5 + 30

    nat = [max(cell_w(r[k]) for r in rows) for k in range(cols)]
    colw = list(nat)
    if sum(nat) > width:
        left, todo = width, sorted(range(cols), key=lambda k: nat[k])
        while todo:
            k = todo[0]
            if nat[k] <= left / len(todo):
                colw[k] = nat[k]
                left -= nat[k]
                todo.pop(0)
            else:
                tot = sum(nat[x] for x in todo)
                for x in todo:
                    colw[x] = left * nat[x] / tot
                break
    hs = []
    for r in rows:
        lines = 1
        for k in range(cols):
            n = sum(max(1, math.ceil(vlen(x) * fs * 0.5 / max(40, colw[k] - 30))) for x in re.split(r"<br>", r[k]))
            lines = max(lines, n)
        hs.append(lines * fs * 1.42 + 20)
    return hs


def code_h(text, width=W):
    per = (width - 50) / (FS * 0.74 * 0.56)
    n = sum(max(1, math.ceil(vlen(l) / per)) for l in text.split("\n"))
    return n * FS * 0.74 * 1.5 + 40


def est(b, width=W):
    t = b["t"]
    if t == "p":
        return sum(text_h(l, width) for l in b["lines"]) + 14
    if t == "lead":
        return 52
    if t == "ul":
        return sum(text_h(x, width - 40) + 8 for x in b["items"]) + 12
    if t == "table":
        return sum(table_rows_h(b, width)) + 14
    if t == "code":
        return code_h(b["text"], width) + 12
    if t == "alert":
        return sum(est(x, width - 60) for x in b["blocks"]) + 40
    return 0


def split_table(b):
    hs = table_rows_h(b)
    total = sum(hs)
    if total <= CAP or len(b["rows"]) < 2:
        return [b]
    n = math.ceil(total / BUD)
    target = (total - hs[0]) / n
    parts, cur, acc = [], [], 0.0
    for r, h in zip(b["rows"], hs[1:]):
        if cur and acc + h / 2 > target and len(parts) < n - 1:
            parts.append(cur)
            cur, acc = [], 0.0
        cur.append(r)
        acc += h
    parts.append(cur)
    return [{"t": "table", "head": b["head"], "rows": p} for p in parts]


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


def fig_budget(b):
    """ข้อความที่อยู่ร่วมสไลด์กับภาพได้ (px): ภาพสัดส่วนปกติให้ภาพใหญ่ที่สุด ภาพแนวกว้างมากเหลือที่ให้ข้อความ"""
    return max(130.0, BUD + 40 - fig_nat_h(b) - 30)


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
def is_lead(b):
    if b["t"] != "p" or len(b["lines"]) != 1:
        return False
    m = re.match(r"^\*\*(.+?)\*\*(.*)$", b["lines"][0])
    if not m or m.group(1).endswith(":") and m.group(2).strip():
        return False
    rest = m.group(2).strip()
    return rest == "" or rest.startswith("·") or rest.startswith("(")


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


def gate_slide(cand, kicker, title):
    txt = read("runs/%s/gate.txt" % cand).strip()
    body = ('<p>ข้อความที่คำสั่ง <code>gate</code> พิมพ์จริง เก็บไว้ที่ <a href="runs/%s/gate.txt" target="_blank">'
            '<code>runs/%s/gate.txt</code></a></p>%s'
            '<table class="c2"><thead><tr><th>ส่วนของข้อความ</th><th>อ่านว่า</th></tr></thead><tbody>'
            '<tr><td><code>train:</code> <code>val:</code> <code>รวม:</code></td><td>คะแนนของรุ่นฐาน → รุ่นใหม่ (ผลต่างเป็นจุด) แยกตามชุด</td></tr>'
            '<tr><td><code>เกณฑ์</code></td><td>ค่าที่มากกว่าระหว่าง <code>eps</code> 2.0 จุด กับ <code>z</code> 1.5 × ความแกว่งของส่วนต่างสองรุ่น ของชุดนั้น</td></tr>'
            '<tr><td><code>ผล:</code></td><td>คำตัดสินของโปรแกรม · <span class="v accept">ACCEPT</span> = exit 0 · <span class="v reject">REJECT</span> = exit 1</td></tr>'
            '</tbody></table>') % (cand, cand, pre_html(txt, "text", "term"))
    return S(kicker, "ผลดิบของ gate · " + title, body, tag="runs/%s/gate.txt" % cand, maxfs=1.1)


def mk(cur, kicker, title, tag):
    has_text = bool(cur["pre"] or cur["post"])
    parts = [render(b) for b in cur["pre"]]
    if cur["fig"]:
        parts.append(fig_html(cur["fig"], has_text))
    parts += [render(b) for b in cur["post"]]
    lead = next((plain(b["text"]) for b in cur["pre"] + cur["post"] if b["t"] == "lead"), "")
    return S(kicker, title, "".join(parts), tag=tag, maxfs=1.0 if cur["fig"] else 1.4, lead=lead)


def flow(blocks, kicker, title, tag="", check=None):
    out, pending = [], []          # pending = สไลด์รายละเอียดที่รอต่อท้ายสไลด์หลักที่กำลังสะสม
    cur = {"pre": [], "fig": None, "post": [], "est": 0.0}

    def flush():
        nonlocal cur
        if cur["pre"] or cur["fig"] or cur["post"]:
            out.append(mk(cur, kicker, title, tag))
        out.extend(pending)
        pending.clear()
        cur = {"pre": [], "fig": None, "post": [], "est": 0.0}

    for b in blocks:
        t = b["t"]
        if t == "hr":
            continue
        if t == "img":
            if cur["fig"] is not None or cur["est"] > fig_budget(b):
                flush()
            cur["fig"] = b
            m = re.search(r"r03-threshold-(\w+)-(\w+)\.png", b["src"])
            if m:
                flush()
                out.append(gate_slide(m.group(2), kicker, title))
            continue
        if t == "imgrow":
            flush()
            body = '<div class="figrow">%s</div>' % "".join('<div class="fig">%s</div>' % img_tag(x) for x in b["imgs"])
            out.append(S(kicker, title, body, tag=tag, maxfs=1.0))
            continue
        if t == "details":
            # ข้อความสั้นที่ตามหลัง <details> อยู่ต่อในสไลด์หลัก แล้วสไลด์รายละเอียดจึงตามมา
            (pending if (cur["pre"] or cur["fig"] or cur["post"]) else out).extend(
                flow(b["blocks"], "%s › %s" % (kicker, title), b["summary"], tag="รายละเอียด"))
            continue
        if t == "alert" and any(x["t"] == "code" for x in b["blocks"]):
            flush()
            out += prompt_slides(b, kicker, title)
            if check:
                out.append(check_slide(check, kicker, title))
            continue
        if t == "h":
            b, t = {"t": "lead", "text": b["text"]}, "lead"
        elif is_lead(b):
            b, t = {"t": "lead", "text": b["lines"][0]}, "lead"
        parts = split_table(b) if t == "table" else [b]
        for k, pb in enumerate(parts):
            h = est(pb)
            if cur["fig"]:
                if t == "lead" or cur["est"] + h > fig_budget(cur["fig"]):
                    flush()
            elif cur["est"] > 0 and (k > 0 or cur["est"] + h > CAP or (t == "lead" and cur["est"] > SOFT)):
                flush()
            (cur["post"] if cur["fig"] else cur["pre"]).append(pb)
            cur["est"] += h
    flush()
    return out


# ------------------------------------------------------------------ สไลด์ที่เพิ่มเอง
# รายการตรวจผลของแต่ละ LAB · เรียบเรียงจากตาราง Input/Output พรอมต์ และ "ผลจริง" ของ LAB นั้นใน README.md
CHECKS = {
    "ขั้น 0.1": {
        "items": [
            "มีโฟลเดอร์ `Teaching/my-skill-optimizer/` และมีไฟล์ครบ: `SKILL.md` · `scripts/skillopt.py` · `references/source.md` · `references/suite.md` · `references/issues.md`",
            "`scripts/skillopt.py` มีครบ 7 คำสั่ง: `lint` `run` `grade` `report` `failures` `null` `gate`",
            "`references/source.md` มีตาราง ส่วนของสกิล | มาจากข้อไหนของเปเปอร์ | เหมือนหรือต่าง",
            "รายงานมีผลทดสอบ `gate` 5 คู่ (`noskill` → `v0` → `v1` → `v2` → `v3` → `v4`) และตัดสินตรงกับ `runs/<รุ่นใหม่>/gate.txt` ทุกคู่",
        ],
        "ref": "ผลของผู้สอน: ใช้ 14 นาที · ไม่เรียกโมเดล · `gate` ตรงทุกตัวอักษร (ACCEPT 4 คู่ · REJECT 1 คู่) · `null` `lint` `report` ตรงกับไฟล์ที่เก็บไว้",
        "note": "เครื่องมือที่สร้างเองไม่ต้องเหมือนใครทุกบรรทัด สิ่งที่ต้องตรงคือ **รูปแบบ** และ **ผลตัดสิน**",
    },
    "ขั้น 0.2": {
        "items": [
            "รายงานเป็นตาราง รายการ | ผล",
            "`my-skill-optimizer` ถูกติดตั้งเป็น global skill ชื่อ `skill-optimizer` ของบัญชี yolo",
            "ใน container มี `/workspace/sklab/suite/` และ `/workspace/sklab/runs/v0/skills/` (โครงโฟลเดอร์เดิม)",
            "`suite/check_grader.py` ผ่าน: เฉลยอ้างอิงผ่าน 10/10 ห้าโจทย์ และ 11/11 โจทย์ค่าส่ง",
            "มีบัญชี `yolo` ที่ล็อกอินแล้วอย่างน้อย 1 บัญชี",
        ],
        "ref": "ผลของผู้สอน: ติดตั้งสกิล ✅ · คัดลอกโจทย์ ✅ · ตัวตรวจผ่าน ✅ · บัญชีที่ใช้ได้ `yolo1` `yolo2` `yolo3` · ใช้ 1 นาที",
        "note": "ตรวจตัวตรวจก่อนเสมอ ถ้าเครื่องวัดผิด ตัวเลขหลังจากนี้ใช้ไม่ได้ทั้งหมด",
    },
    "LAB 1": {
        "items": [
            "`runs/noskill/trials/` และ `runs/v0/trials/` มีรุ่นละ 18 โฟลเดอร์ (6 โจทย์ × 3 รอบ) รวม 36 Trial",
            "`runs/report.md` มีตารางเทียบ `noskill` กับ `v0` · `runs/results.json` ถูกเขียน",
            "`runs/v0/null.txt` มีความแกว่งของ `v0` แยกชุด train · val · all",
            "`runs/v0/gate.txt` มีบรรทัด `ผล:` ของการตัดสิน `noskill` → `v0`",
            "ผลของ Validation Set ที่เก็บลงเครื่อง มีแค่คะแนนและต้นทุน (ไม่มีผลรายข้อ)",
        ],
        "ref": "ผลของผู้สอน: ไม่มีสกิล 45.3% → `v0` 67.9% (+22.6 จุด · เกณฑ์ 2.6) · ACCEPT · ผ่านครบทุกข้อ 0/18 ทั้งสองรุ่น · ใช้ 4 นาที",
    },
    "LAB 2": {
        "items": [
            "`runs/ISSUES.md` มีตาราง ปัญหา | พบกี่ Trial | สาเหตุ | ทางแก้ · เก็บเฉพาะสาเหตุที่พบมากกว่า 1 Trial",
            "`runs/v1/skills/money-coder/SKILL.md` ต่างจาก `v0` ไม่เกิน 3 จุด",
            "`runs/v1/trials/` มี 18 โฟลเดอร์ · วัดด้วยค่าเดียวกับ `v0`",
            "`runs/v1/gate.txt` มีผลตัดสิน `v0` → `v1` · `runs/report.md` มีทุกรุ่น",
            "ดูว่า Claude จัดการข้อ `policy` อย่างไร: เดากฎเอง หรือจดเป็นปัญหาเปิด",
        ],
        "ref": "ผลของผู้สอน: รวม 67.9% → 93.5% (+25.6 จุด · เกณฑ์ 2.3) · ACCEPT · แก้ 3 จุด (`cli_ok`/`cli_error` · `tests` · `reject_type`) · `policy` ยัง 0/6 และถูกจดเป็นปัญหาเปิด · ใช้ 5 นาที",
    },
    "LAB 3": {
        "items": [
            "`runs/v2/skills/money-coder/SKILL.md` มีนโยบายค่าส่งและนโยบายเงินคืน เขียนเป็นนโยบายของร้าน ไม่มี Input หรือคำตอบของข้อตรวจ",
            "แก้ไม่เกิน 3 จุดจากรุ่นฐาน",
            "`runs/v2/trials/` มี 18 โฟลเดอร์ · `runs/v2/gate.txt` มีผลตัดสิน `v1` → `v2`",
            "`runs/ISSUES.md` ปิดปัญหา `policy` · `runs/report.md` มี `v2`",
        ],
        "ref": "ผลของผู้สอน: Training 95.2% → 100.0% · รวม 93.5% → 96.7% (+3.2 จุด · เกณฑ์ 2.0) · ACCEPT · `policy` 0/6 → 6/6 · Validation ยัง 90% · ใช้ 5 นาที",
    },
    "LAB 4": {
        "items": [
            "`runs/v3/skills/money-coder/SKILL.md` แก้ไม่เกิน 3 จุด ให้เป็นกติกาที่ตรวจสอบได้ ไม่มี Input หรือคำตอบของข้อตรวจ",
            "ไม่มีการเปิดผลรายข้อ Trace หรือโค้ดของ Validation Set",
            "`runs/v3/trials/` มี 18 โฟลเดอร์ · `runs/v3/gate.txt` มีผลตัดสิน `v2` → `v3`",
            "ถ้า REJECT: ใช้ `v2` ต่อ และไม่วัดซ้ำเพื่อให้ผ่าน",
            "`runs/ISSUES.md` และ `runs/report.md` ถูกอัปเดต",
        ],
        "ref": "ผลของผู้สอน: Validation 90.0% → 100.0% · รวม 96.7% → 100.0% (+3.3 จุด · เกณฑ์ 2.0) · ACCEPT · แก้ 2 จุด · โทเคนขาเข้า +10.2% · ใช้ 7 นาที",
    },
    "LAB 5": {
        "items": [
            "`runs/v4/skills/money-coder/SKILL.md`: กติกาละ 1 บรรทัด ไม่เกิน 60 ตัวอักษร (นับเป็น 1 จุด ไม่แก้อย่างอื่น)",
            "`runs/v4/trials/` มี 18 โฟลเดอร์ · `runs/v4/gate.txt` มีผลตัดสิน `v3` → `v4`",
            "ถ้า REJECT: ใช้ `v3` ต่อ ไม่แก้ `v4` เพิ่ม และไม่วัดซ้ำ",
            "รายงานมีโทเคนขาเข้าเทียบกับรุ่นฐาน และข้อตรวจของ Training Set ที่เปลี่ยนไป",
            "`runs/ISSUES.md` จดว่าการย่อแบบนี้ได้ผลหรือไม่ เพราะอะไร",
        ],
        "ref": "ผลของผู้สอน: รวม 100.0% → 80.3% (−19.7 จุด) · REJECT · สกิลสั้นลง 81% แต่โทเคนขาเข้าลดแค่ 5.2% · `cli_ok` และ `cli_error` 12/12 → 0/12 · ใช้ 6 นาที",
    },
}
VARY = "ตัวเลขของคุณอาจต่างจากของผู้สอน เพราะ Agent เขียนไม่เหมือนกันทุกครั้ง (ข้อ 2.7) · สิ่งที่ต้องมีเหมือนกันคือไฟล์ผลและคำตัดสินของ `gate`"


def check_slide(key, kicker, title):
    c = CHECKS[key]
    items = "".join('<label class="chk"><input type="checkbox" data-k="%s-%d"><span>%s</span></label>' % (key, k, inline(x))
                    for k, x in enumerate(c["items"]))
    body = '<div class="checks">%s</div><div class="note result">%s</div>' % (items, inline(c["ref"]))
    body += '<div class="note eye"><span class="lbl">หมายเหตุ</span><span>%s</span></div>' % inline(c.get("note") or VARY)
    return S(kicker, "ตรวจผลของคุณ · " + title, body, tag="Checklist", cls="cslide", maxfs=1.4)


def photo(src):
    return os.path.exists(os.path.join(ROOT, src))


def divider(big, title, sub_html, img="", small=""):
    style = ' style="background-image:url(%s)"' % img if img and photo(img) else ""
    cls = "divider photo" if style else "divider"
    body = ('<div class="shade"></div><div class="inner"><div class="small">%s</div><div class="big">%s</div><h1>%s</h1>'
            '<div class="sub">%s</div>%s</div>') % (small, big, inline(title), sub_html,
                                                    '<div class="imgnote">ภาพจำลอง</div>' if style else "")
    return {"raw": body, "cls": cls, "style": style, "title": "%s · %s" % (big, plain(title)), "kicker": "", "tag": "", "lead": ""}


def compare_slides(kicker):
    """โค้ดจริงของ Agent จาก runs/ (โจทย์เงินคืน รอบที่ 1): ไม่มีสกิล เทียบกับ v3 · ผลตรวจอ่านจาก grade.json"""
    def one(label):
        base = "runs/%s/trials/t4-cashback-r1" % label
        g = json.loads(read(base + "/grade.json"))
        return base, read(base + "/sandbox/solve.py").rstrip().split("\n"), g["checks"]

    def head(name, base):
        return '<h3 class="lead">%s<span> · <a href="%s/sandbox/solve.py" target="_blank">เปิดไฟล์ solve.py</a></span></h3>' % (name, base)

    def two(left, right, fl=1.15, fr=1):
        return '<div class="cols"><div class="col" style="flex:%s">%s</div><div class="col" style="flex:%s">%s</div></div>' % (fl, left, fr, right)

    b0, c0, k0 = one("noskill")
    b3, c3, k3 = one("v3")
    cut = next(k for k, l in enumerate(c3) if l.startswith("def _main"))
    bad = [c for c in k0 if not c["pass"]]
    fails = "".join('<div class="cardx bad"><h4><code>%s</code></h4><p>%s</p></div>' % (c["id"], esc(c["note"])) for c in bad)
    s1 = S(kicker, "โค้ดจริงของ Agent ตอนไม่มีสกิล: ผ่าน %d จาก %d ข้อ" % (len(k0) - len(bad), len(k0)), two(
        head("ไม่มีสกิล · โจทย์เงินคืน รอบที่ 1", b0) + pre_html("\n".join(c0), "python"),
        '<h3 class="lead">ข้อความจากตัวตรวจ (grade.json)</h3><div class="fails">%s</div>' % fails, 1, 1.05), tag="runs/noskill", cls="cmp", maxfs=1.2)
    ok3 = sum(1 for c in k3 if c["pass"])
    s2 = S(kicker, "โค้ดจริงของ Agent ด้วยสกิล `v3`: ผ่าน %d จาก %d ข้อ" % (ok3, len(k3)), two(
        head("สกิลรุ่น v3 · ส่วนฟังก์ชัน", b3) + pre_html("\n".join(c3[:cut]).rstrip(), "python"),
        head("สกิลรุ่น v3 · ส่วน CLI", b3) + pre_html("\n".join(c3[cut:]), "python"), 1, 1), tag="runs/v3", cls="cmp", maxfs=1.2)
    rows = [
        ("`type(amount) is not int` · `type(birthday) is not bool` → `raise ValueError`", "ความรู้แฝงข้อ 3 ตรวจสอบข้อมูลนำเข้า", "`reject_value` `reject_type`"),
        ("`birthday and tier in (\"gold\", \"platinum\")`", "นโยบาย C1 สิทธิ์เดือนเกิดเฉพาะ gold และ platinum", "`policy`"),
        ("`num // _DEN` บนตัวเศษจำนวนเต็ม ไม่มี `float`", "ความรู้แฝงข้อ 1 และนโยบาย C2 เงินคืนปัดลง", "`contract` `no_drift` `policy`"),
        ("`_main()` อ่าน JSON จาก stdin · ตอบ `{\"ok\": …}` · `return 0` หรือ `return 2`", "ความรู้แฝงข้อ 4 สัญญาการเรียกผ่าน CLI", "`cli_ok` `cli_error`"),
        ("ไฟล์ `test_solve.py` ที่ส่งคู่กัน", "ความรู้แฝงข้อ 5 ชุดทดสอบหน่วย", "`tests`"),
    ]
    tab = table_html({"t": "table", "head": ["ส่วนของโค้ด `v3`", "มาจากกติกาข้อไหนของสกิล", "ข้อตรวจที่ผ่าน"], "rows": [list(r) for r in rows]})
    s3 = S(kicker, "โค้ดแต่ละส่วนของ `v3` มาจากกติกาข้อไหนของสกิล", tab, tag="ตารางหลัก")
    return [s1, s2, s3]


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
.fails .cardx p{font-size:.8em;font-family:var(--mono);line-height:1.45}
.center{justify-content:center}
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
    const key='skillopt-slides:'+c.dataset.k;
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


def write(slides):
    body = "\n".join(slide_html(s) for s in slides)
    full = "\n".join('<pre class="full" id="prompt%d">%s</pre>' % (k, esc(t)) for k, t in enumerate(PROMPTS))
    page = """<!doctype html>
<html lang="th">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Skill Optimizer · Slides</title>
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
""" % (CSS, body, full, JS)
    open(OUT, "w", encoding="utf-8", newline="\n").write(page)
    print("wrote %s · %d slides · %d prompts · %.0f KB" % (os.path.relpath(OUT, ROOT), len(slides), len(PROMPTS), len(page.encode("utf-8")) / 1024))
    return slides
