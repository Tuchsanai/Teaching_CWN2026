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
for ws, title in (("w1", "เส้นทางของ WikiSkill: workspace w1 (LAB 1)"), ("w2", "เส้นทางของ WikiSkill: รันซ้ำ workspace w2 (LAB 3)"),
                  ("n1", "เส้นทางเมื่อตัด Wiki ออก: workspace n1 (LAB 4)")):
    if has(ws):
        c = state(ws)["cfg"]
        path(ws, "img/r01-path-%s.png" % ws, title, SUB % (c["model"], c["reps"], 4 * c["reps"], 2 * c["reps"]))

rows = [("noskill", "ไม่มีสกิล", "Agent ได้รับแค่โจทย์", "#BCAAA4"),
        ("so-v3", "Skill Optimizer v3", "บท 05 · คนเขียน แล้วปรับ 3 รุ่น", INK),
        ("w1", "WikiSkill (w1)", "ไม่มีคนเขียน · 2 รอบ", WIKI)]
compare([r for r in rows if r[0] in R], "img/r02-compare.png", "คะแนนของสกิลแต่ละชุดบนโจทย์ 9 ข้อ (LAB 2)",
        "ผลจริง · โมเดลที่ทำโจทย์ sonnet / effort medium · โจทย์ละ 3 รอบ = 27 Trial ต่อชุดสกิล")

rows = [("noskill", "ไม่มีสกิล", "ได้รับแค่โจทย์", "#BCAAA4"),
        ("w1", "w1", "LAB 1 · WikiSkill", WIKI), ("w2", "w2", "LAB 3 · รันซ้ำ", WIKI),
        ("n1", "n1", "LAB 4 · ไม่มี Wiki", SKILL),
        ("w1p", "w1p", "LAB 5.1 · นโยบายกว้าง", BAD), ("w1q", "w1q", "LAB 5.2 · มีขอบเขต", GATE),
        ("so-v3", "v3 ของบท 05", "Skill Optimizer", INK)]
if "w2" in R:
    compare([r for r in rows if r[0] in R], "img/r03-all.png", "คะแนนของสกิลทุกชุดบนโจทย์ 9 ข้อ",
            "ผลจริง · โมเดลที่ทำโจทย์ sonnet / effort medium · โจทย์ละ 3 รอบ = 27 Trial ต่อชุดสกิล")

E = [("Skill Optimizer (บท 05)", INK, [("สกิลรุ่นแรก", "คนเขียน"), ("รอบ (รับ · ไม่รับ)", "5 (4 · 1)"), ("Trial ระหว่างปรับ", "108"),
                                         ("ผู้ปรับเรียกโมเดล", "คนสั่งทีละรุ่น"), ("คนสั่งงาน", "5 พรอมต์"),
                                         ("คะแนน 27 Trial", pct(R["so-v3"]["all"]["score"])), ("โทเคนต่อ Trial", format(R["so-v3"]["all"]["context_tokens"], ","))])]
for ws, name, col in (("w1", "WikiSkill (w1)", WIKI), ("w2", "WikiSkill (w2)", WIKI), ("n1", "ไม่มี Wiki (n1)", SKILL)):
    if has(ws) and ws in R:
        st = state(ws)
        acc = sum(1 for h in st["history"] if h.get("accepted"))
        E.append((name, col, [("สกิลรุ่นแรก", "ว่าง"), ("รอบ (รับ · ไม่รับ)", "%d (%d · %d)" % (len(st["history"]), acc, len(st["history"]) - acc)),
                              ("Trial ระหว่างปรับ", str(trials(st))), ("ผู้ปรับเรียกโมเดล", "%d ครั้ง" % opt_calls(st)),
                              ("คนสั่งงาน", "1 พรอมต์"), ("คะแนน 27 Trial", pct(R[ws]["all"]["score"])),
                              ("โทเคนต่อ Trial", format(R[ws]["all"]["context_tokens"], ","))]))
effort(E, "img/r04-effort.png")
