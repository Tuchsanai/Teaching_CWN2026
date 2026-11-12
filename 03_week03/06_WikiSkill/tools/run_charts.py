#!/usr/bin/env python3
"""รายการกราฟผลจริงของบทนี้ (ถูกเรียกโดย  python tools/charts.py)"""
import os
from charts import R, path, compare, effort, state, pct
from draw import ROOT, RAW, WIKI, SKILL, GATE, BAD, INK


def has(ws):
    if not os.path.isfile(os.path.join(ROOT, "runs", ws, "state.json")):
        return False
    st = state(ws)                                   # วาดเฉพาะ workspace ที่รันจบรอบแล้ว
    return st["phase"] == "gate" and st["history"] and all("outcome" in h for h in st["history"])


def opt_calls(st):
    return sum(1 for h in st["history"] if h.get("maintainer")) + sum((h.get("proposer") or {}).get("calls") or 0 for h in st["history"])


def trials(st):
    return st["baseline"]["trials"] + sum(h["train"]["trials"] + (h.get("val") or {}).get("trials", 0) for h in st["history"])


SUB = "ผลจริง · โมเดลที่ทำโจทย์ %s / effort medium · โจทย์ละ %d รอบ (Training %d Trial · Validation %d Trial ต่อการวัด 1 ครั้ง)"
for ws, title in (("w1", "เส้นทางของ WikiSkill: รันหลัก (w1)"), ("w2", "เส้นทางของ WikiSkill: วัดซ้ำ 6 รอบต่อโจทย์ (w2)"),
                  ("n1", "เส้นทางเมื่อตัด Wiki ออก (n1)"), ("h1", "เส้นทางของ WikiSkill กับโมเดลเล็ก (h1)")):
    if has(ws):
        c = state(ws)["cfg"]
        path(ws, "img/r01-path-%s.png" % ws, title, SUB % (c["model"], c["reps"], 4 * c["reps"], 2 * c["reps"]))

rows = [("noskill-test", "ไม่มีสกิล", "วัดเฉพาะ Test Set", "#BCAAA4"),
        ("so-v3", "Skill Optimizer v3", "บท 05 · คนเขียน แล้วปรับ 3 รอบ", INK),
        ("w1-final", "WikiSkill (w1)", "เริ่มจากว่าง · หยุดที่รอบ 1", WIKI)]
if "w2-final" in R:
    rows.append(("w2-final", "WikiSkill (w2)", "เริ่มจากว่าง · วัดซ้ำ 6 รอบ", WIKI))
if "n1-final" in R:
    rows.append(("n1-final", "ไม่มี Wiki (n1)", "เริ่มจากว่าง · ตัด Wiki ออก", SKILL))
compare([r for r in rows if r[0] in R], "img/r02-compare.png", "คะแนนของสกิลแต่ละชุดบนโจทย์ 9 ข้อ",
        "ผลจริง · โมเดลที่ทำโจทย์ sonnet / effort medium · โจทย์ละ 3 รอบ = 27 Trial ต่อชุดสกิล")

if "h1-final" in R:
    rows = [("h1-noskill-test", "haiku · ไม่มีสกิล", "วัดเฉพาะ Test Set", "#BCAAA4"),
            ("h1-final", "haiku · สกิลตัวเอง", "ปรับจาก Trace ของ haiku", WIKI),
            ("h1-with-w1", "haiku · สกิล sonnet", "สกิลจาก w1", SKILL),
            ("h1-with-v3", "haiku · สกิล v3", "สกิลของบท 05", INK),
            ("w1-with-h1", "sonnet · สกิล haiku", "สกิลจาก h1", RAW)]
    compare([r for r in rows if r[0] in R], "img/r03-transfer.png", "ย้ายสกิลข้ามโมเดล (Cross-Model Skill Transfer)",
            "ผลจริง · โจทย์ละ 3 รอบ = 27 Trial ต่อชุด · ชื่อใต้แท่ง = โมเดลที่ทำโจทย์ · สกิลที่ใช้")

E = [("Skill Optimizer", INK, [("สกิลรุ่นแรก", "คนเขียน"), ("รอบ (รับ · ไม่รับ)", "5 (4 · 1)"), ("Trial ระหว่างปรับ", "108"),
                                     ("ผู้ปรับเรียกโมเดล", "ไม่ได้วัด"), ("คนสั่งงาน", "5 พรอมต์"),
                                     ("คะแนน 27 Trial", pct(R["so-v3"]["all"]["score"])), ("โทเคนต่อ Trial", format(R["so-v3"]["all"]["context_tokens"], ","))])]
for ws, lb, name, col in (("w1", "w1-final", "WikiSkill (w1)", WIKI), ("w2", "w2-final", "WikiSkill (w2)", WIKI),
                          ("n1", "n1-final", "ไม่มี Wiki (n1)", SKILL)):
    if has(ws) and lb in R:
        st = state(ws)
        acc = sum(1 for h in st["history"] if h.get("accepted"))
        E.append((name, col, [("สกิลรุ่นแรก", "ว่าง"), ("รอบ (รับ · ไม่รับ)", "%d (%d · %d)" % (len(st["history"]), acc, len(st["history"]) - acc)),
                              ("Trial ระหว่างปรับ", str(trials(st))), ("ผู้ปรับเรียกโมเดล", "%d ครั้ง" % opt_calls(st)),
                              ("คนสั่งงาน", "1 คำสั่ง"), ("คะแนน 27 Trial", pct(R[lb]["all"]["score"])),
                              ("โทเคนต่อ Trial", format(R[lb]["all"]["context_tokens"], ","))]))
effort(E, "img/r04-effort.png")
