#!/usr/bin/env python3
"""วาดแผนภาพทฤษฎีของ WikiSkill เป็น PNG ลง 01_theory/img/

  python tools/diagrams.py            (รันบนเครื่อง จากโฟลเดอร์ของบท · ใช้ Chrome headless)

ตัวเลขของภาพที่มาจากการรันจริงอ่านจาก runs/w1/ (state.json และไฟล์ใน wiki/ raw/) ไม่มีค่าที่พิมพ์เอง
ตัวเลขของเปเปอร์ (Table 1 และ Table 3) คัดจาก arXiv:2608.27454
"""
import glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from draw import ROOT, RAW, WIKI, SKILL, GATE, BAD, INK, MUTE, LINE, MONO, shot, card, arrow, e

D = "01_theory/img/"
ST = json.load(open(os.path.join(ROOT, "runs", "w1", "state.json"), encoding="utf-8"))
H = ST["history"]


def pct(x):
    return "%.1f%%" % (x * 100)


def size(*parts):
    return sum(os.path.getsize(f) for f in glob.glob(os.path.join(ROOT, *parts)))


def chars(*parts):
    return sum(len(open(f, encoding="utf-8").read()) for f in glob.glob(os.path.join(ROOT, *parts)))


# ------------------------------------------------------------------ t01 วงรอบร่วม
def loop():
    cards = arrow().join([
        card(RAW, "1 Rollout", "", "Agent ทำโจทย์ Training<br>ด้วยสกิลปัจจุบัน<br>ได้ <b>Trace</b> ของทุกงาน", "flex:1"),
        card(WIKI, "2 Analyze", "", "อ่าน Trace<br>หาสาเหตุที่พลาด<br>และวิธีที่ได้ผล", "flex:1"),
        card(SKILL, "3 Propose", "", "เสนอแก้สกิล<br>(สร้างใหม่ หรือ แก้ของเดิม)", "flex:1"),
        card(GATE, "4 Gate", "", "วัดด้วย Validation Set<br>ดีขึ้น = รับ<br>ไม่ดีขึ้น = ย้อนกลับ", "flex:1")])
    body = """<h1>วงรอบการปรับสกิล (Skill Evolution Loop)</h1>
    <div class='sub'>วิธีปรับสกิลอัตโนมัติทุกวิธีใช้วงรอบ 4 ขั้นนี้ร่วมกัน รวมถึง Skill Optimizer ของบท 05</div>
    <div class='row' style='gap:10px'>%s</div>
    <div style='text-align:center;font-size:30px;color:#6F4E37;font-weight:800;margin:14px 0 6px'>↺ ทำซ้ำรอบถัดไป</div>
    <div class='card' style='border:4px dashed %s;background:#FFF6EC;margin-top:10px'>
      <div style='font-size:32px;font-weight:800;color:%s'>คำถามของ WikiSkill</div>
      <div style='font-size:28px;margin-top:6px;line-height:1.4'>สิ่งที่เรียนรู้ได้ในขั้น 2 ของรอบนี้ <b>ถูกเก็บไว้ที่ไหน</b> เพื่อให้รอบถัดไปใช้ต่อได้</div></div>""" % (cards, SKILL, INK)
    shot(D + "t01-loop.png", body, 580)


# ------------------------------------------------------------------ t02 ปัญหา
def problem():
    cards = "".join([
        card(BAD, "1 ลืม (Forgetting)", "", "ข้อเสนอที่เคยถูกปฏิเสธ<br>ถูกเสนอซ้ำในรอบหลัง<br>เพราะไม่มีบันทึกว่าเคยลองแล้ว", "flex:1"),
        card(BAD, "2 หลักฐานไม่สะสม", "", "ปัญหาที่พบรอบละ 1 ครั้ง<br>ไม่ถูกนับรวมข้ามรอบ<br>จึงไม่เคยถึงเกณฑ์ที่จะแก้", "flex:1"),
        card(BAD, "3 บริบทไม่พอ (Context Limit)", "", "Trace ดิบของทุกรอบยาวเกินกว่า<br>ที่โมเดลจะอ่านใหม่ทั้งหมด<br>ทุกครั้งที่จะเสนอแก้", "flex:1")])
    rows = [("EvoSkill", "ประวัติข้อเสนอและผลการวัด เป็นรายการเรียงต่อกัน (Flat History)"),
            ("Trace2Skill", "รวมบทเรียนจาก Trace เข้าเป็น patch ของสกิลโดยตรง"),
            ("SkillOpt", "Feedback ของการแก้ที่ถูกปฏิเสธ และคำแนะนำสรุปรายรอบ (Meta Guidance)"),
            ("Skill Optimizer (บท 05)", "ISSUES.md ที่ผู้ปรับสกิลเขียนเอง")]
    tr = "".join("<tr><td style='width:420px'><b>%s</b></td><td>%s</td></tr>" % r for r in rows)
    body = """<h1>ปัญหา: ความรู้ที่ได้ระหว่างการปรับสกิลกระจัดกระจาย</h1>
    <div class='sub'>สิ่งที่เรียนรู้จากแต่ละรอบถูกเก็บปนอยู่ในประวัติการปรับ ไม่ได้เป็นความรู้ที่จัดระเบียบและโตขึ้นเรื่อย ๆ จึงเกิดอาการ 3 อย่าง</div>
    <div class='row'>%s</div>
    <div style='font-size:27px;font-weight:800;color:%s;margin:22px 0 2px'>วิธีก่อนหน้าเก็บสิ่งที่เรียนรู้ไว้ที่ไหน</div>
    <table class='t'>%s</table>
    <div class='note' style='margin-top:8px'>วิธีอัตโนมัติก่อนหน้าไม่มีวิธีใดเก็บสิ่งที่เรียนรู้เป็น <b>ชั้นความรู้ที่แยกออกมา</b> และพัฒนาต่อได้เอง → WikiSkill เพิ่มชั้นนี้</div>""" % (cards, INK, tr)
    shot(D + "t02-problem.png", body, 750)


# ------------------------------------------------------------------ t03 สามชั้น
def layers():
    rows = [
        (RAW, "Raw Layer", "raw/", "Trace ของ Training ทุกงาน:<br>ทุกคำสั่ง โค้ดที่เขียน ผลของ Grader",
         "Inference Agent<br>(ผ่านโปรแกรม)", "Wiki Maintainer<br>Skill Proposer", "เขียนครั้งเดียว ไม่แก้<br><b>(Immutable)</b>", "ไม่"),
        (WIKI, "Wiki Layer", "wiki/", "patterns/ (1 หน้าต่อ 1 pattern)<br>index.md · log.md · skill-impact.md",
         "Wiki Maintainer<br>+ โปรแกรม (skill-impact)", "Wiki Maintainer<br>Skill Proposer", "เพิ่มและแก้ทีละจุด<br><b>(Incremental)</b>", "<b>ไม่ย้อนกลับ</b><br>(Persistent)"),
        (SKILL, "Skills Layer", "skills/", "SKILL.md (ขั้นตอนที่ Agent ทำตาม)<br>PURPOSE.md (สกิลนี้มาจาก pattern ใด)",
         "Skill Proposer<br>(ต้องผ่าน Gate)", "Inference Agent", "สร้างหรือแก้ 1 สกิลต่อรอบ<br><b>(Atomic Proposal)</b>", "<b>ย้อนกลับ</b>เมื่อ<br>Validation ไม่ดีขึ้น"),
    ]
    th = "".join("<th>%s</th>" % t for t in ("ชั้น", "เก็บอะไร", "ใครเขียน", "ใครอ่าน", "เปลี่ยนอย่างไร", "ย้อนกลับหรือไม่"))
    tr = ""
    for col, name, d, what, w, r, how, rb in rows:
        tr += """<tr><td style='border-left:16px solid %s;width:250px'><div style='font-size:30px;font-weight:800;color:%s'>%s</div>
          <div class='mono' style='font-size:24px;color:#2A6F68'>%s</div></td><td style='width:420px'>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>""" % (
            col, INK, name, d, what, w, r, how, rb)
    body = """<h1>สถาปัตยกรรมความรู้ 3 ชั้น (Three-Layer Knowledge Architecture)</h1>
    <div class='sub'>แยก <b>ประสบการณ์ดิบ</b> · <b>ความรู้สะสม</b> · <b>ขั้นตอนที่ใช้ทำงาน</b> ออกจากกัน เพราะสามอย่างนี้มีผู้ใช้ อายุ และวิธีเปลี่ยนแปลงต่างกัน</div>
    <table class='t' style='border-spacing:0 12px'><tr>%s</tr>%s</table>
    <div class='row' style='justify-content:center;gap:26px;margin-top:10px;font-size:27px;font-weight:800;color:%s'>
      <span class='badge raw' style='font-size:26px'>ประสบการณ์ดิบ</span> ➜ สรุปเป็น ➜ <span class='badge wiki' style='font-size:26px'>ความรู้</span> ➜ เลือกเขียนเป็น ➜ <span class='badge skill' style='font-size:26px'>ขั้นตอน</span></div>""" % (th, tr, INK)
    shot(D + "t03-layers.png", body, 760)


# ------------------------------------------------------------------ t04 บทบาท
def roles():
    def cell(kind, txt):
        col = {"w": "#E3F3DE;border:2px solid #6BBF59;color:#2F6B22", "r": "#E1F1EF;border:2px solid #2A9D8F;color:#1F6F66",
               "x": "#FBE3DC;border:2px solid #E76F51;color:#A63D25", "-": "#F3EEE7;border:2px solid #E5D9CC;color:#7A6557"}[kind]
        return "<td><div style='border-radius:14px;padding:9px 12px;font-size:23px;line-height:1.3;background:%s'>%s</div></td>" % (col, txt)
    rows = [
        ("Inference Agent", "ทำโจทย์ด้วยสกิลปัจจุบัน", [("w", "<b>สร้าง</b> Trace ของงานที่ทำ"), ("x", "<b>ห้ามอ่าน</b>"), ("r", "<b>อ่าน</b>แล้วทำตาม"), ("-", "ถูกวัด")]),
        ("Wiki Maintainer", "สรุป Trace เป็นความรู้", [("r", "<b>อ่าน</b> Trace ที่สุ่มมา<br>ไม่ผ่าน ≤ 5 · ผ่าน ≤ 3"), ("w", "<b>เขียน</b> patterns/<br>index.md · log.md"), ("r", "อ่าน (ดูว่าสกิลช่วยหรือไม่)"), ("-", "ไม่เห็น")]),
        ("Skill Proposer", "เสนอแก้สกิล 1 ตัว", [("r", "<b>เลือกอ่าน</b>เองตามต้องการ<br>(ReAct · อย่างน้อย 4 Trace)"), ("r", "<b>อ่าน</b> index ก่อน<br>แล้วเลือกเปิด pattern"), ("w", "<b>เสนอ</b> create หรือ patch<br>(โปรแกรมเป็นผู้เขียนไฟล์)"), ("-", "เห็นแค่คะแนนรวม")]),
        ("Gating and Rollback", "โปรแกรม ไม่ใช่โมเดล", [("-", "–"), ("w", "<b>เขียน</b> skill-impact.md<br>(diff · คะแนน · รับ/ไม่รับ)"), ("w", "<b>รับ</b> หรือ <b>ย้อนกลับ</b>"), ("w", "<b>วัด</b> Validation<br>เทียบกับ R_best")]),
    ]
    th = "<th></th>" + "".join("<th style='font-size:27px;font-weight:800;color:#fff;background:%s;border-radius:14px;padding:8px 14px'>%s</th>" % c for c in (
        (RAW, "Raw Layer"), (WIKI, "Wiki Layer"), (SKILL, "Skills Layer"), (GATE, "Validation Set")))
    tr = ""
    for name, sub, cells in rows:
        tr += "<tr><td style='width:300px'><div style='font-size:28px;font-weight:800;color:%s'>%s</div><div style='font-size:22px;color:%s'>%s</div></td>%s</tr>" % (
            INK, name, MUTE, sub, "".join(cell(k, t) for k, t in cells))
    body = """<h1>ส่วนประกอบ 4 ตัว และสิทธิ์ต่อแต่ละชั้น</h1>
    <div class='sub'>แต่ละส่วนเห็นและแก้ได้เฉพาะสิ่งที่จำเป็นต่อหน้าที่ของตัวเอง ·
      <span style='color:#2F6B22;font-weight:700'>เขียว = เขียน</span> · <span style='color:#1F6F66;font-weight:700'>ฟ้าเขียว = อ่าน</span> · <span style='color:#A63D25;font-weight:700'>แดง = ห้าม</span></div>
    <table class='t' style='border-spacing:8px 10px'><tr>%s</tr>%s</table>""" % (th, tr)
    body = body.replace("table.t td{background:#fff", "")
    shot(D + "t04-roles.png", body, 710)


# ------------------------------------------------------------------ t05 หนึ่งรอบ (ตัวเลขจริงของ iteration 1)
def iteration():
    h = H[0]
    m, p = h["maintainer"], h["proposer"]
    steps = [
        (RAW, "1 Rollout", "wikiskill.py rollout", "Inference Agent ทำโจทย์ Training <b>%d งาน</b><br>คะแนน <b>%s</b> · ผ่านครบ %d/%d" % (
            h["train_n"], pct(h["train_score"]), h["train_perfect"], h["train_n"]), "raw/iter-01/traces/ (%d ไฟล์)" % h["train_n"]),
        (WIKI, "2 Wiki Maintainer", "wikiskill.py maintain", "อ่าน Trace ที่สุ่มมา <b>%d ไฟล์</b><br>เรียกโมเดล <b>1 ครั้ง</b> (%.0f วินาที)" % (
            len(h["sampled"]["fail"]) + len(h["sampled"]["pass"]), m["wall_s"]), "wiki/patterns/ +%d หน้า · index.md · log.md" % len(h["patterns_created"])),
        (SKILL, "3 Skill Proposer", "wikiskill.py propose", "ReAct <b>%d รอบ</b> (%.0f วินาที)<br>อ่าน pattern <b>%d หน้า</b> + Trace <b>%d ไฟล์</b>" % (
            p["calls"], p["wall_s"], p["patterns_read"], p["traces_read"]), "ข้อเสนอ: %s 1 สกิล" % h["proposal"]["action"]),
        (GATE, "4 Gating and Rollback", "wikiskill.py gate", "Validation ของสกิลที่เสนอ <b>%s</b><br>R_best ก่อนหน้า <b>%s</b>" % (
            pct(h["val_score"]), pct(h["r_best_before"])), "%s → wiki/skill-impact.md" % h["outcome"]),
    ]
    cards = arrow().join(
        """<div class='card' style='flex:1;border-top:14px solid %s'><div style='font-size:29px;font-weight:800;color:%s'>%s</div>
        <div class='mono' style='font-size:21px;color:#2A6F68;margin:4px 0 8px'>%s</div>
        <div style='font-size:24px;line-height:1.4'>%s</div>
        <div style='margin-top:10px;border-top:2px dashed %s;padding-top:8px;font-size:22px;color:%s'>ผลที่ได้<br><span class='mono' style='color:%s;font-size:21px'>%s</span></div></div>""" % (
            c, INK, t, cmd, txt, LINE, MUTE, INK, out) for c, t, cmd, txt, out in steps)
    body = """<h1>1 รอบของ WikiSkill (ตัวเลขจริงของรอบที่ 1)</h1>
    <div class='sub'>สกิลตอนเริ่ม = ว่าง · Wiki ตอนเริ่ม = ว่าง · Validation ของชุดสกิลว่าง (R_best เริ่มต้น) = %s</div>
    <div class='row' style='gap:8px'>%s</div>
    <div class='note' style='margin-top:18px'>สกิลที่ได้: <span class='mono' style='color:%s'>skills/%s/SKILL.md</span> · ทั้ง 4 ขั้นรวมกัน = Algorithm 1 บรรทัด 8–19</div>""" % (
        pct(ST["baseline"]["val_score"]), cards, INK, h["proposal"]["name"])
    shot(D + "t05-iteration.png", body, 620)


# ------------------------------------------------------------------ t06 อัลกอริทึม
def algorithm():
    L = [("", "รับเข้า", "โจทย์ Training · โจทย์ Validation · จำนวนรอบสูงสุด K", "", ""),
         ("2", "เริ่มต้น", "ชุดสกิล S₀ = ว่าง · Wiki W₀ = ว่าง", "init", INK),
         ("3", "วัดเส้นฐาน", "R_best = คะแนน Validation ของชุดสกิลว่าง", "baseline", GATE),
         ("4", "ทำซ้ำ k = 1 … K", "", "loop", INK),
         ("5–7", "　หยุดก่อนกำหนด", "ถ้า R_best = 100% ให้จบ", "", GATE),
         ("8", "　Inference", "Agent ทำโจทย์ Training ด้วยสกิล S<sub>k−1</sub> → Trace ของรอบ k", "rollout", RAW),
         ("9", "　Sampling", "สุ่ม Trace: ไม่ผ่าน ≤ 5 + ผ่าน ≤ 3", "maintain", WIKI),
         ("10", "　Wiki Maintenance", "W′<sub>k</sub> = Maintainer(W<sub>k−1</sub>, Trace ที่สุ่ม)", "maintain", WIKI),
         ("11", "　Skill Proposal", "P<sub>k</sub> = Proposer(W′<sub>k</sub>, S<sub>k−1</sub>, Trace ของรอบ k)", "propose", SKILL),
         ("12", "　Apply", "S′<sub>k</sub> = S<sub>k−1</sub> + P<sub>k</sub> (สกิลที่เสนอ ยังไม่รับ)", "propose", SKILL),
         ("13", "　Validate", "วัด S′<sub>k</sub> ด้วยโจทย์ Validation", "gate", GATE),
         ("14–15", "　ถ้าคะแนน &gt; R_best", "รับ: S<sub>k</sub> = S′<sub>k</sub> และ R_best = คะแนนใหม่", "gate", GATE),
         ("16–17", "　ถ้าไม่", "ย้อนกลับ: S<sub>k</sub> = S<sub>k−1</sub> <b>(Wiki ไม่ย้อนกลับ)</b>", "gate", BAD),
         ("19", "　Update Wiki Log", "W<sub>k</sub> = W′<sub>k</sub> + บันทึกข้อเสนอ diff คะแนน และผลการตัดสิน", "gate", WIKI),
         ("21", "ส่งออก", "ชุดสกิล S<sub>K</sub> และ Wiki W<sub>K</sub>", "status", INK)]
    rows = ""
    for no, name, txt, cmd, col in L:
        rows += """<div style='display:flex;align-items:center;gap:16px;background:#fff;border-radius:12px;padding:7px 16px;margin-bottom:6px;border-left:12px solid %s'>
          <div class='mono' style='width:86px;font-size:22px;color:%s'>%s</div>
          <div style='width:330px;font-size:25px;font-weight:800;color:%s;white-space:pre'>%s</div>
          <div style='flex:1;font-size:24px'>%s</div>
          <div class='mono' style='width:150px;font-size:22px;color:#2A6F68;text-align:right'>%s</div></div>""" % (
            col or LINE, MUTE, no, INK, name, txt, cmd)
    body = """<h1>Algorithm 1: วงรอบของ WikiSkill</h1>
    <div class='sub'>เลขทางซ้าย = บรรทัดใน Algorithm 1 ของเปเปอร์ · ทางขวา = คำสั่งของ <span class='mono'>wikiskill.py</span> ที่ทำบรรทัดนั้น ·
      S = ชุดสกิล · W = Wiki · R_best = คะแนน Validation ที่ดีที่สุด</div>%s""" % rows
    shot(D + "t06-algorithm.png", body, 1060)


# ------------------------------------------------------------------ t07 ทำไม Inference Agent ห้ามอ่าน Wiki
def no_wiki_for_agent():
    def col(color, title, steps, end, score):
        s = "".join("<div style='background:#fff;border:3px solid %s;border-radius:16px;padding:10px 16px;font-size:24px;line-height:1.35;margin-bottom:6px'>%s</div>%s" % (
            LINE, t, "<div style='text-align:center;font-size:26px;color:#6F4E37;font-weight:800;line-height:1;margin-bottom:6px'>▼</div>" if i < len(steps) - 1 else "")
            for i, t in enumerate(steps))
        return """<div style='flex:1'><div class='badge' style='background:%s;font-size:28px;margin-bottom:12px'>%s</div>%s
          <div style='border-radius:16px;padding:12px 16px;font-size:25px;font-weight:800;color:#fff;background:%s;margin-top:8px'>%s</div>
          <div style='font-size:24px;color:%s;margin-top:8px'>ผลในเปเปอร์ (เฉลี่ย 4 Benchmark): <b style='font-size:30px'>%s</b></div></div>""" % (
            color, title, s, color, end, MUTE, score)
    a = col(BAD, "แบบ ก · Agent อ่านได้ทั้ง Skill และ Wiki",
            ["สกิลยังขาดกฎข้อหนึ่ง", "Agent เปิด Wiki เจอวิธีแก้ จึงทำถูก", "Trace ของรอบนี้ <b>ดูดี</b> ไม่มีข้อที่พลาด",
             "Proposer ไม่เห็นว่าสกิลขาดอะไร จึงไม่แก้"], "สกิลไม่ครบ · ใช้ได้เมื่อมี Wiki อยู่ด้วยเท่านั้น", "60.9%")
    b = col(GATE, "แบบ ข · Agent อ่านได้เฉพาะ Skill (WikiSkill)",
            ["สกิลยังขาดกฎข้อหนึ่ง", "Agent มีแต่สกิล จึง <b>พลาด</b> ตรงจุดที่สกิลขาด", "Trace ของรอบนี้ <b>ชี้ช่องว่าง</b> ของสกิลชัดเจน",
             "Proposer เห็นช่องว่าง จึงเติมกฎลงในสกิล"], "สกิลครบในตัวเอง · ใช้งานได้โดยไม่ต้องมี Wiki", "63.7%")
    body = """<h1>ทำไม Inference Agent ห้ามอ่าน Wiki ระหว่างการปรับสกิล</h1>
    <div class='sub'>Wiki มีไว้ให้ <b>ผู้ปรับสกิล</b> ใช้ ไม่ใช่ผู้ทำงาน · ถ้า Agent ได้คำตอบจาก Wiki โดยตรง Trace จะไม่บอกว่าสกิลขาดอะไร (เปเปอร์ ข้อ 5.1 · Table 3)</div>
    <div class='row' style='gap:40px'>%s%s</div>""" % (a, b)
    shot(D + "t07-agent-no-wiki.png", body, 720)


# ------------------------------------------------------------------ t08 Progressive disclosure (ขนาดจริง)
def disclosure():
    k = H[-1]["k"]
    it = "iter-%02d" % k
    idx = chars("runs", "w1", "wiki", "index.md")
    npat = len(glob.glob(os.path.join(ROOT, "runs", "w1", "wiki", "patterns", "*.md")))
    pat = chars("runs", "w1", "wiki", "patterns", "*.md")
    ntr = len(glob.glob(os.path.join(ROOT, "runs", "w1", "raw", it, "traces", "*.md")))
    tr = chars("runs", "w1", "raw", it, "traces", "*.md")
    p = H[-1]["proposer"]
    levels = [
        (WIKI, "ชั้น 1 · ได้รับตั้งแต่ต้น", "wiki/index.md · wiki/skill-impact.md · summary.md",
         "index = 1 บรรทัดต่อ 1 pattern: <b>ปัญหา + สาเหตุ + วิธีแก้</b>", "index %s ตัวอักษร (%d pattern)" % (format(idx, ","), npat), 800),
        (WIKI, "ชั้น 2 · เปิดเมื่อเกี่ยวข้อง", "wiki/patterns/&lt;ชื่อ&gt;.md",
         "หน้า pattern: อาการ · สาเหตุ · หลักฐานจาก Trace · วิธีแก้", "ทั้งหมด %s ตัวอักษร · รอบที่ %d เปิดอ่าน <b>%d หน้า</b>" % (format(pat, ","), k, p["patterns_read"]), 1090),
        (RAW, "ชั้น 3 · เปิดเมื่อต้องยืนยันสาเหตุ", "traces/&lt;trace_id&gt;.md",
         "Trace ดิบ: ทุกคำสั่งและผลของ Grader (ไม่เกิน 15,000 ตัวอักษรต่อไฟล์)", "ทั้งหมด %s ตัวอักษร (%d ไฟล์) · รอบที่ %d เปิดอ่าน <b>%d ไฟล์</b>" % (format(tr, ","), ntr, k, p["traces_read"]), 1380),
    ]
    rows = ""
    for col, title, files, what, real, w in levels:
        rows += """<div style='width:%dpx;margin:0 auto 14px;background:#fff;border:3px solid %s;border-top:14px solid %s;border-radius:20px;padding:12px 20px'>
          <div style='display:flex;justify-content:space-between;align-items:baseline;gap:14px'><div style='font-size:28px;font-weight:800;color:%s'>%s</div>
          <div class='mono' style='font-size:21px;color:#2A6F68'>%s</div></div>
          <div style='font-size:23px;margin-top:4px'>%s</div><div style='font-size:22px;color:%s;margin-top:4px'>ผลจริง: %s</div></div>""" % (
            w, LINE, col, INK, title, files, what, MUTE, real)
    body = """<h1>Skill Proposer อ่านความรู้ทีละชั้น (Progressive Disclosure)</h1>
    <div class='sub'>Proposer ไม่ได้รับ Trace ทั้งหมดในครั้งเดียว · เริ่มจากสารบัญสั้น ๆ แล้วใช้เครื่องมือ Read เลือกเปิดเฉพาะหน้าที่ต้องใช้ (ReAct) จึงไม่เกินบริบทของโมเดล</div>
    %s<div class='note'>คุณภาพของ <b>index.md</b> สำคัญที่สุด: ถ้าคำอธิบาย 1 บรรทัดไม่ชัด Proposer จะไม่รู้ว่าควรเปิดหน้าใด</div>""" % rows
    shot(D + "t08-disclosure.png", body, 760)


# ------------------------------------------------------------------ t09 เทียบวิธี
def methods():
    rows = [("Trace2Skill", "วิเคราะห์ทุก Trace แยกกัน แล้วรวม patch แบบลำดับชั้น", "อยู่ใน patch ที่รวมแล้ว", "N + (1 + 1/(c−1))·N/B + 1", "32.1 – 55.6"),
            ("EvoSkill", "ป้อนเฉพาะ Trace ที่ไม่ผ่าน + ประวัติข้อเสนอ แล้วค้นหาในกลุ่มสกิลที่ดีที่สุด", "ประวัติข้อเสนอแบบรายการ", "2·N/B", "33.7 – 56.1"),
            ("SkillOpt", "Rollout → Reflect → Aggregate → Select → Update → Evaluate", "Feedback ของการแก้ที่ถูกปฏิเสธ", "K_opt·N/B (K_opt ≈ 6–8)", "35.2 – 55.9"),
            ("WikiSkill", "Maintainer สรุปลง Wiki แล้ว Proposer อ่าน Wiki + Trace ตามต้องการ", "<b>Wiki Layer ที่แยกออกมา และไม่ถูกย้อนกลับ</b>", "<b>1 + T_ReAct</b> (ไม่ขึ้นกับ N)", "<b>38.5 – 68.1</b>")]
    th = "".join("<th>%s</th>" % t for t in ("วิธี", "ทำงานอย่างไร", "สิ่งที่เรียนรู้ถูกเก็บที่ไหน", "การเรียกโมเดลของผู้ปรับ ต่อรอบ", "คะแนนเฉลี่ยในเปเปอร์ (5 โมเดล)"))
    tr = "".join("<tr><td style='width:190px;font-weight:800;font-size:27px;color:%s%s'>%s</td><td style='width:470px'>%s</td><td style='width:320px'>%s</td><td class='mono' style='font-size:22px;width:320px'>%s</td><td style='font-size:26px'>%s</td></tr>" % (
        INK, ";border-left:14px solid " + (WIKI if r[0] == "WikiSkill" else LINE), r[0], r[1], r[2], r[3], r[4]) for r in rows)
    body = """<h1>WikiSkill เทียบกับวิธีปรับสกิลก่อนหน้า</h1>
    <div class='sub'>ทุกวิธีใช้วงรอบ Rollout → Analyze → Propose → Gate เหมือนกัน · ต่างกันที่วิธีเก็บสิ่งที่เรียนรู้ ·
      N = จำนวนโจทย์ Training · B = ขนาด batch · T_ReAct = จำนวนรอบ ReAct ของ Proposer (ราว 10–20)</div>
    <table class='t'><tr>%s</tr>%s</table>
    <div class='note' style='margin-top:6px'>คะแนนเฉลี่ย = ช่วงของค่าเฉลี่ย 5 Benchmark จากโมเดลเล็กสุด (Qwen-3.5-4B) ถึงใหญ่สุด (Gemini-3.5-Flash) · ที่มา: Table 1 และ Table 7 ของเปเปอร์</div>""" % (th, tr)
    shot(D + "t09-methods.png", body, 750)


# ------------------------------------------------------------------ t11 ผลในเปเปอร์ (Table 1 คอลัมน์ Avg.)
PAPER = [("Qwen-3.5-4B", [26.2, 32.1, 33.7, 35.2, 38.5]), ("Qwen-3.5-9B", [29.9, 36.7, 42.3, 40.2, 47.4]),
         ("Qwen-3.6-27B", [39.4, 47.3, 53.3, 50.7, 63.3]), ("Gemma-4-31B", [41.3, 45.8, 43.4, 49.1, 54.9]),
         ("Gemini-3.5-Flash", [49.5, 55.6, 56.1, 55.9, 68.1])]
METHODS = [("No skill", "#BCAAA4"), ("Trace2Skill", "#8D6E63"), ("EvoSkill", "#F4A261"), ("SkillOpt", "#6F4E37"), ("WikiSkill", "#2A9D8F")]


def paper_results():
    groups = ""
    for model, vals in PAPER:
        bars = "".join("""<div style='width:44px;height:%.0fpx;background:%s;border-radius:8px 8px 0 0;position:relative'>
          <span style='position:absolute;top:-28px;left:-8px;width:60px;text-align:center;font-size:20px;font-weight:%s;color:%s'>%.1f</span></div>""" % (
            v * 6.2, METHODS[i][1], "800" if i == 4 else "400", INK, v) for i, v in enumerate(vals))
        groups += """<div style='flex:1;display:flex;flex-direction:column;align-items:center'>
          <div style='height:470px;display:flex;align-items:flex-end;gap:6px;border-bottom:4px solid %s;padding:0 6px'>%s</div>
          <div style='font-size:25px;font-weight:800;margin-top:10px;color:%s'>%s</div>
          <div style='font-size:22px;color:%s'>WikiSkill ดีกว่าไม่มีสกิล +%.1f</div></div>""" % (INK, bars, INK, model, MUTE, vals[4] - vals[0])
    legend = " ".join("<span class='badge' style='background:%s'>%s</span>" % (c, n) for n, c in METHODS)
    body = """<h1>ผลในเปเปอร์: คะแนนเฉลี่ย 5 Benchmark ของแต่ละโมเดล</h1>
    <div class='sub'>คะแนนบน Test Set เฉลี่ยจากการปรับสกิล 3 ครั้งอิสระ (Table 1 คอลัมน์ Avg.) · %s</div>
    <div class='row' style='gap:8px;margin-top:34px'>%s</div>
    <div class='note' style='margin-top:14px'>WikiSkill ได้คะแนนเฉลี่ยสูงสุดทุกโมเดล · ส่วนต่างจากไม่มีสกิลโตตามขนาดโมเดลในตระกูล Qwen (+12.3 → +17.5 → +23.9)</div>""" % (legend, groups)
    shot(D + "t11-paper-results.png", body, 800)


def ablation():
    rows = [("–", "–", "ไม่มีสกิล (เส้นฐาน)", 40.4, "#BCAAA4"), ("มี", "ไม่มี", "ไม่มี Wiki Maintainer", 45.3, BAD),
            ("ไม่มี", "ไม่มี", "ไม่มี Wiki Maintainer", 48.7, "#F4A261"), ("มี", "มี", "", 60.9, "#8D6E63"),
            ("ไม่มี", "มี", "WikiSkill", 63.7, WIKI)]
    h = ""
    for a, b, note, v, col in rows:
        h += """<div style='display:flex;align-items:center;gap:18px;margin-bottom:12px'>
          <div style='width:250px;font-size:25px;text-align:center;background:#fff;border-radius:12px;padding:8px'>%s</div>
          <div style='width:250px;font-size:25px;text-align:center;background:#fff;border-radius:12px;padding:8px'>%s</div>
          <div style='flex:1;display:flex;align-items:center;gap:14px'><div style='height:52px;width:%.0fpx;background:%s;border-radius:0 12px 12px 0'></div>
          <div style='font-size:32px;font-weight:800;color:%s'>%.1f%%</div><div style='font-size:22px;color:%s'>%s</div></div></div>""" % (
            a, b, v * 11.5, col, INK, v, MUTE, note)
    body = """<h1>การทดลองตัดส่วนประกอบ (Ablation) ในเปเปอร์</h1>
    <div class='sub'>โมเดล Gemini-3.5-Flash · คะแนนเฉลี่ย 4 Benchmark (Table 3) · เปลี่ยนเฉพาะว่าใครอ่าน Wiki ได้ระหว่างการปรับสกิล</div>
    <div style='display:flex;gap:18px;font-size:23px;color:%s;margin-bottom:8px'><div style='width:250px;text-align:center'>Agent อ่าน Wiki</div>
      <div style='width:250px;text-align:center'>Proposer อ่าน Wiki</div><div>คะแนนเฉลี่ย</div></div>%s
    <div class='note' style='margin-top:10px'>1) ให้ Proposer อ่าน Wiki: 48.7%% → 63.7%% (<b>+15.0</b>) = ความรู้สะสมคือส่วนที่ทำให้ดีขึ้นมากที่สุด<br>
      2) ให้ Inference Agent อ่าน Wiki ด้วย: 63.7%% → 60.9%% (<b>−2.8</b>) = Wiki ควรอยู่ฝั่งผู้ปรับสกิลเท่านั้น</div>""" % (MUTE, h)
    shot(D + "t12-ablation.png", body, 660)


# ------------------------------------------------------------------ t13 แผนที่โค้ด
def code_map():
    rows = [(INK, "init", "cmd_init()", "สร้าง raw/ wiki/ skills/ ว่าง และ state.json", "บรรทัด 2"),
            (GATE, "baseline", "cmd_baseline() → rollouts()", "วัด Validation ด้วยชุดสกิลว่าง → R_best", "บรรทัด 3"),
            (RAW, "rollout", "cmd_rollout() → rollouts() → render_trace()", "Agent ทำโจทย์ Training · เขียน Trace ลง raw/iter-k/", "บรรทัด 8"),
            (WIKI, "maintain", "cmd_maintain() → sample_traces() → llm() → apply_edits()", "prompts/maintainer.md · แก้ wiki/patterns index log", "บรรทัด 9–10"),
            (SKILL, "propose", "cmd_propose() → llm(tools=Read) → build_candidate()", "prompts/proposer.md · ได้ proposal.json + candidate/skills", "บรรทัด 11–12"),
            (GATE, "gate", "cmd_gate() → rollouts()", "วัด Validation · รับ/ย้อนกลับ · เขียน wiki/skill-impact.md", "บรรทัด 13–19"),
            (INK, "loop", "cmd_loop()", "เรียก rollout → maintain → propose → gate ซ้ำจนจบ", "บรรทัด 4–20")]
    tr = "".join("""<tr><td style='border-left:14px solid %s;width:170px' class='mono'><b style='font-size:27px'>%s</b></td>
        <td class='mono' style='font-size:22px;color:#2A6F68;width:610px'>%s</td><td>%s</td><td style='width:170px;color:%s'>%s</td></tr>""" % (
        c, cmd, fn, what, MUTE, line) for c, cmd, fn, what, line in rows)
    body = """<h1>จากอัลกอริทึมสู่โค้ด: wikiskill.py</h1>
    <div class='sub'>1 คำสั่ง = 1 ขั้นของ Algorithm 1 · สถานะของวงรอบเก็บใน <span class='mono'>state.json</span> จึงรันทีละขั้นหรือรันต่อจากที่ค้างได้</div>
    <table class='t'><tr><th>คำสั่ง</th><th>ฟังก์ชันใน wikiskill.py</th><th>ทำอะไร</th><th>Algorithm 1</th></tr>%s</table>""" % tr
    shot(D + "t13-code-map.png", body, 850)


# ------------------------------------------------------------------ d00 เรื่องทั้งหมดในภาพเดียว (README หลัก)
def story():
    cards = arrow().join([
        card(RAW, "1 Agent ทำโจทย์", "raw/", "AI เขียนโค้ดคิดเงินของร้าน<br>ทุกขั้นที่ทำถูกบันทึกเป็น <b>Trace</b>", "flex:1"),
        card(WIKI, "2 สรุปลงสมุดความรู้", "wiki/", "Wiki Maintainer อ่าน Trace<br>จดว่าพลาด <b>เพราะอะไร</b> และแก้อย่างไร", "flex:1"),
        card(SKILL, "3 เขียนสกิลจากสมุด", "skills/", "Skill Proposer อ่าน Wiki<br>แล้วเสนอสร้างหรือแก้สกิล <b>1 ตัว</b>", "flex:1"),
        card(GATE, "4 วัดแล้วตัดสิน", "Validation", "ดีขึ้น = ใช้สกิลใหม่<br>ไม่ดีขึ้น = <b>ทิ้งสกิล แต่เก็บความรู้</b>", "flex:1")])
    body = """<h1>WikiSkill: ปรับสกิลโดยมีสมุดความรู้คั่นกลาง</h1>
    <div class='sub'>โจทย์เดียวกับบท 05: ให้ AI เขียนโค้ดคิดเงินของร้าน BaanKafe ให้ถูกกฎของร้าน · ต่างกันที่บทนี้ <b>ไม่มีคนเขียนสกิลให้</b> ระบบเริ่มจากสกิลว่างและสมุดว่าง</div>
    <div class='row' style='gap:10px'>%s</div>
    <div style='text-align:center;font-size:30px;color:#6F4E37;font-weight:800;margin:14px 0 0'>↺ ทำซ้ำจนคะแนน Validation เต็ม หรือครบจำนวนรอบ</div>""" % cards
    shot("img/d00-story.png", body, 480)


if __name__ == "__main__":
    which = sys.argv[1:] or ["story", "loop", "problem", "layers", "roles", "iteration", "algorithm", "no_wiki_for_agent", "disclosure",
                             "methods", "paper_results", "ablation", "code_map"]
    for w in which:
        globals()[w]()
