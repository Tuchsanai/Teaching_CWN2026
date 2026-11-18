#!/usr/bin/env python3
"""ภาพโฟลเดอร์ my-skill-optimizer ที่ได้จาก LAB 0 ขั้น 0.1 (img/d10-lab0-folder.png)

อ่านไฟล์จริงจากโฟลเดอร์ที่สร้าง: นับบรรทัดของแต่ละไฟล์ และแสดงต้นไฟล์ SKILL.md
แล้วเรนเดอร์เป็นหน้าต่างแบบ File Explorer ด้วย Chrome (Playwright)

  python tools/folder_shot.py [โฟลเดอร์ my-skill-optimizer]     (ค่าเริ่มต้น: ../../my-skill-optimizer)
"""
import html, os, sys
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "..", "my-skill-optimizer"))
OUT = os.path.join(HERE, "img", "d10-lab0-folder.png")

# ไฟล์ที่พรอมต์ขั้น 0.1 สั่งให้สร้าง · หน้าที่เรียบเรียงจากตารางผลจริงใน README.md
TREE = [
    (0, "dir", "my-skill-optimizer", ""),
    (1, "md", "SKILL.md", "ขั้นตอนที่ AI ทำตาม"),
    (1, "dir", "scripts", ""),
    (2, "py", "scripts/skillopt.py", "โปรแกรม 7 คำสั่ง"),
    (1, "dir", "references", ""),
    (2, "md", "references/source.md", "มาจากข้อไหนของเปเปอร์"),
    (2, "md", "references/suite.md", "รูปแบบชุดโจทย์และ gate"),
    (2, "md", "references/issues.md", "รูปแบบของ ISSUES.md"),
]
ICON = {"dir": "📁", "md": "📝", "py": "🐍"}


def lines(rel):
    with open(os.path.join(SRC, rel), encoding="utf-8") as f:
        return f.read().splitlines()


rows = []
for depth, kind, rel, role in TREE:
    name = os.path.basename(rel)
    n = "" if kind == "dir" else "%d บรรทัด" % len(lines(rel))
    sel = " sel" if rel == "SKILL.md" else ""
    rows.append('<div class="row%s" style="padding-left:%dpx"><span class="ic">%s</span><span class="nm">%s</span>'
                '<span class="role">%s</span><span class="n">%s</span></div>'
                % (sel, 14 + depth * 26, ICON[kind], html.escape(name), html.escape(role), n))

head = lines("SKILL.md")[:30]
code = "\n".join('<span class="ln">%2d</span>%s' % (i + 1, html.escape(l[:120] + ("…" if len(l) > 120 else ""))) for i, l in enumerate(head))

page = """<!doctype html><html><head><meta charset="utf-8"><style>
body{margin:0;background:#e9eef3;font-family:'Segoe UI','Leelawadee UI',sans-serif}
.win{margin:24px;width:1552px;border-radius:10px;overflow:hidden;box-shadow:0 10px 30px rgba(0,0,0,.18);background:#fff}
.bar{height:40px;background:#f3f3f3;display:flex;align-items:center;padding:0 16px;font-size:15px;color:#333;border-bottom:1px solid #ddd}
.bar .dots{margin-left:auto;letter-spacing:18px;color:#666}
.addr{height:42px;display:flex;align-items:center;gap:10px;padding:0 16px;border-bottom:1px solid #e3e3e3;font-size:15px;color:#444}
.addr .box{flex:1;background:#f7f7f7;border:1px solid #ddd;border-radius:6px;padding:6px 12px}
.body{display:flex;height:760px}
.tree{width:640px;border-right:1px solid #e3e3e3;padding-top:10px}
.hdr{display:flex;font-size:13px;color:#777;padding:4px 14px 8px;border-bottom:1px solid #eee;margin-bottom:6px}
.hdr span:last-child{margin-left:auto}
.row{display:flex;align-items:center;height:62px;font-size:20px;color:#222;padding-right:16px}
.row.sel{background:#dbeafe}
.ic{width:34px;font-size:22px}
.nm{font-weight:600;font-family:Consolas,monospace;font-size:19px}
.role{margin-left:14px;color:#2563eb;font-size:16px}
.n{margin-left:auto;color:#666;font-size:16px;white-space:nowrap}
.prev{flex:1;display:flex;flex-direction:column;min-width:0}
.tab{height:40px;display:flex;align-items:center;padding:0 16px;font-size:15px;color:#333;background:#fafafa;border-bottom:1px solid #e3e3e3}
pre{margin:0;padding:12px 16px;font-family:Consolas,'Leelawadee UI',monospace;font-size:15px;line-height:23.6px;color:#1f2937;white-space:pre;overflow:hidden}
.ln{display:inline-block;width:34px;color:#9ca3af}
</style></head><body><div class="win">
<div class="bar">📁 my-skill-optimizer<span class="dots">— ▢ ✕</span></div>
<div class="addr">← → ↑<span class="box">Teaching › my-skill-optimizer</span></div>
<div class="body"><div class="tree"><div class="hdr"><span>ชื่อ · หน้าที่</span><span>ขนาด</span></div>%s</div>
<div class="prev"><div class="tab">👁 ตัวอย่างไฟล์ · SKILL.md (30 บรรทัดแรก)</div><pre>%s</pre></div></div>
</div></body></html>""" % ("".join(rows), code)

with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome")
    pg = b.new_page(viewport={"width": 1600, "height": 900}, device_scale_factor=1)
    pg.set_content(page)
    pg.locator(".win").screenshot(path=OUT)
    b.close()
print(OUT)
