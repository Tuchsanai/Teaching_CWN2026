#!/usr/bin/env python3
"""วาดแผนภาพทฤษฎีของ EvoSkill v2 เป็น PNG ลง 01_theory/img/

  python tools/diagrams.py [ชื่อภาพ ...]      (รันบนเครื่อง จากโฟลเดอร์ของบท · ใช้ Chrome headless)

ตัวเลขของเปเปอร์คัดจาก arXiv:2610.25931 (Table 2, 3, 4, 5 และ Figure 2, 4, 5)
ตัวเลขของภาพที่มาจากการรันจริงอ่านจาก runs/e1/state.json ไม่มีค่าที่พิมพ์เอง
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from draw import ROOT, USER, ADAPT, SOLVER, EVOLVER, FILE, BAD, INK, MUTE, LINE, MONO, shot, card, arrow, e

D = "01_theory/img/"


def state(ws="e1"):
    p = os.path.join(ROOT, "runs", ws, "state.json")
    return json.load(open(p, encoding="utf-8")) if os.path.isfile(p) else None


def pct(x):
    return "%.1f%%" % (x * 100)


def pill(color, text, size=22):
    return "<span style='display:inline-block;background:%s;color:#fff;border-radius:12px;padding:3px 13px;font-weight:700;font-size:%dpx;white-space:nowrap'>%s</span>" % (color, size, text)


def box(color, title, body, style="", tsize=28, bsize=22):
    return """<div style='background:#fff;border:3px solid %s;border-left:14px solid %s;border-radius:18px;padding:12px 16px;%s'>
      <div style='font-size:%dpx;font-weight:800;color:%s;line-height:1.2'>%s</div>
      <div style='font-size:%dpx;color:%s;line-height:1.36;margin-top:4px'>%s</div></div>""" % (LINE, color, style, tsize, INK, title, bsize, MUTE, body)


def strip(color, text, size=25, mt=16):
    return "<div style='border:4px dashed %s;background:#FFF6EC;border-radius:18px;padding:12px 18px;font-size:%dpx;line-height:1.4;margin-top:%dpx'>%s</div>" % (color, size, mt, text)


def table(heads, rows, widths=None, size=23):
    th = "".join("<th style='%s'>%s</th>" % ("width:%dpx" % widths[i] if widths and widths[i] else "", h) for i, h in enumerate(heads))
    tr = ""
    for r in rows:
        col = r[0] if isinstance(r[0], tuple) else None
        cells = r[1:] if col else r
        tr += "<tr>" + "".join("<td style='font-size:%dpx;%s'>%s</td>" % (
            size, ("border-left:14px solid %s;" % col[0]) if (col and i == 0) else "", c) for i, c in enumerate(cells)) + "</tr>"
    return "<table class='t'><tr>%s</tr>%s</table>" % (th, tr)


# ------------------------------------------------------------------ t01 จาก v1 สู่ v2
def v1v2():
    left = """<div class='card' style='flex:1.02;border-top:14px solid %s'>
      <div style='font-size:32px;font-weight:800;color:%s'>EvoSkill v1</div>
      <div class='note' style='margin:4px 0 12px'>ตัวปรับสกิล = Agent 2 ตัว ทำงานต่อกัน</div>
      <div class='row' style='gap:8px;align-items:stretch'>%s%s%s</div>
      <div class='note' style='margin-top:14px'>• benchmark ใหม่ต้อง <b>แปลงด้วยมือ</b> ให้เข้ารูปแบบที่ระบบรองรับ<br>• รองรับตัวตรวจของผู้ใช้ได้จำกัด</div></div>""" % (
        FILE, INK, box(FILE, "Proposer", "อ่านจุดพลาดของ Solver<br>แล้ว <b>เสนอ</b> การแก้", "flex:1"), arrow(),
        box(FILE, "Generator", "นำข้อเสนอไป <b>เขียน</b><br>เป็นไฟล์สกิล", "flex:1"))
    right = """<div class='card' style='flex:1.5;border-top:14px solid %s'>
      <div style='font-size:32px;font-weight:800;color:%s'>EvoSkill v2</div>
      <div class='note' style='margin:4px 0 12px'>Agent 3 ตัว วางซ้อนบน Agent Harness ที่ใช้อยู่แล้ว (เช่น Claude Code)</div>
      <div class='row' style='gap:8px;align-items:stretch'>%s%s%s</div>
      <div class='note' style='margin-top:14px'>• ผู้ใช้ <b>อธิบาย benchmark เป็นข้อความ</b> และให้ตัวตรวจของตัวเอง<br>• Evolver เป็นเซสชันเดียวที่อยู่ <b>ตลอดการรัน</b></div></div>""" % (
        EVOLVER, INK, box(ADAPT, "Benchmark Adaptor", "<b>ใหม่</b> · เตรียมสนาม<br>ก่อนเริ่ม (ครั้งเดียว)", "flex:1.15", 25, 21),
        box(SOLVER, "Solver", "ทำโจทย์ด้วย<br>ชุดสกิลปัจจุบัน", "flex:0.85", 25, 21),
        box(EVOLVER, "Evolver", "<b>รวม</b> Proposer + Generator<br>อ่านผล แล้วเขียนสกิลเอง", "flex:1.35", 25, 21))
    body = """<h1>จาก EvoSkill v1 สู่ EvoSkill v2</h1>
    <div class='sub'>เปลี่ยน 2 อย่าง: รวม Agent 2 ตัวของตัวปรับสกิลเป็น Evolver ตัวเดียว และเพิ่ม Benchmark Adaptor</div>
    <div class='row' style='align-items:stretch'>%s<div class='arrow'>➜</div>%s</div>%s""" % (
        left, right, strip(EVOLVER, "คำถามของเปเปอร์ไม่ใช่ \"สกิลช่วยได้หรือไม่\" (งานก่อนหน้าตอบแล้วว่าช่วยได้) แต่คือ <b>ควรปรับสกิลอย่างไรจึงดีที่สุด</b>: ใครเป็นผู้เขียนสกิล · จำอะไรข้ามรอบ · เห็นการทำโจทย์กี่ครั้ง · ตัดสินอย่างไรว่าจะเก็บสกิลชุดใด"))
    shot(D + "t01-v1-v2.png", body, 700)


# ------------------------------------------------------------------ t02 สถาปัตยกรรม (Figure 1 ของเปเปอร์ วาดใหม่)
def architecture():
    def band(label, color, inner):
        return """<div style='border:3px solid %s;border-radius:22px;background:#FFFDF9;padding:12px 16px 14px;margin-bottom:14px'>
          <div style='font-size:22px;font-weight:800;color:%s;letter-spacing:1px;margin-bottom:8px'>%s</div>%s</div>""" % (LINE, color, label, inner)
    b1 = "<div class='row' style='gap:8px;align-items:stretch'>%s%s%s%s%s</div>" % (
        box(USER, "ผู้ใช้", "คำสั่งเป็นข้อความ · ข้อมูล<br>การแบ่งชุด · ตัวตรวจ<br><span class='mono' style='font-size:19px'>grade(task, snapshot)</span>", "flex:1", 26, 21), arrow(),
        box(ADAPT, "Benchmark Adaptor", "Claude Code 1 เซสชัน<br>รันครั้งเดียว บนเครื่องที่ใช้แล้วทิ้ง", "flex:1.05", 26, 21), arrow(),
        "<div style='flex:2.1;display:flex;gap:10px'>%s%s</div>" % (
            box(FILE, "Plug-in ที่ล็อกแล้ว", "โจทย์ทุกข้อพร้อมชุดของมัน<br>และตัวตรวจ · ล็อกด้วย hash", "flex:1", 25, 21),
            box(FILE, "Reference Folder", "เฉพาะของชุด Training<br><b>ไม่มี</b> Validation · Test · ตัวตรวจ", "flex:1", 25, 21)))
    b2 = """<div class='row' style='gap:8px;align-items:stretch'>%s%s%s%s%s</div>
      <div class='row' style='gap:8px;margin-top:10px;align-items:stretch'>
        <div style='flex:1;text-align:center;font-size:24px;font-weight:800;color:%s;align-self:center'>⟲ ชุดสกิลถัดไป กลับไปที่ Solver</div>
        %s</div>""" % (
        box(SOLVER, "Solver", "Claude Code · system prompt เดิม<br>ทำโจทย์ Training และ Validation<br>ข้อละ <b>N = 3 ครั้ง</b>", "flex:1.1", 26, 21), arrow(),
        box(USER, "ตัวตรวจของผู้ใช้", "โฟลเดอร์ทำงานตอนจบ<br>→ คะแนน 0 ถึง 1", "flex:0.85", 26, 21),
        "<div class='arrow' style='font-size:21px;line-height:1.25;text-align:center;font-weight:700;color:%s'>คะแนน Training<br>transcript<br>โฟลเดอร์ทำงาน<br><span style='font-size:40px'>➜</span></div>" % MUTE,
        box(EVOLVER, "Evolver", "Claude Code <b>1 เซสชันตลอดการรัน</b><br>ข้อความสั้น 1 ข้อความต่อ epoch<br>อ่านผล → เขียนชุดสกิลถัดไป", "flex:1.2", 26, 21),
        EVOLVER,
        box(FILE, "คะแนน Validation", "บันทึกทุก epoch · <b>ไม่เคยให้ Evolver เห็น</b>", "flex:1", 25, 21))
    b3 = "<div class='row' style='gap:8px'>%s</div>" % box(
        FILE, "Held-out Test", "ชุดสกิลของ <b>epoch สุดท้าย</b> · โจทย์ Test ทุกข้อ ข้อละ 3 ครั้ง · วัด <b>ครั้งเดียว</b> หลังจบทุก epoch", "flex:1", 26, 22)
    body = """<h1>สถาปัตยกรรมของ EvoSkill v2</h1>
    <div class='sub'>%s Agent (Claude Code) &nbsp; %s ผู้ใช้เป็นผู้ให้ &nbsp; %s ไฟล์หรือบันทึก</div>%s%s%s""" % (
        pill(ADAPT, "&nbsp;") + " " + pill(SOLVER, "&nbsp;") + " " + pill(EVOLVER, "&nbsp;"), pill(USER, "&nbsp;"), pill(FILE, "&nbsp;"),
        band("ก่อนการรัน (ครั้งเดียว)", ADAPT, b1), band("แต่ละ EPOCH", EVOLVER, b2), band("หลังการรัน", INK, b3))
    shot(D + "t02-architecture.png", body, 940)


# ------------------------------------------------------------------ t03 Benchmark Adaptor
def adaptor():
    st = state()
    ad = (st or {}).get("adapt")
    real = ""
    if ad:
        real = strip(ADAPT, "<b>ผลจริงของบทนี้ (การรัน e1):</b> Benchmark Adaptor ใช้ %.0f วินาที · เรียกเครื่องมือ %d ครั้ง · ได้โจทย์ train %d · validation %d · test %d ข้อ · reference/ %d ไฟล์ (เฉลยอ้างอิงของ Training %d ไฟล์) · ตรวจการรั่วอัตโนมัติ: %s" % (
            ad["wall_s"], ad["tool_calls"], ad["tasks"]["train"], ad["tasks"]["validation"], ad["tasks"]["test"],
            ad["reference"]["files"], ad["reference"]["answers"], "ไม่พบ" if ad["audit_ok"] else "พบ"), 24)
    left = "".join([
        box(USER, "1 คำสั่งของผู้ใช้ (ข้อความ 1 หน้า)", "benchmark ข้อมูล และการแบ่งชุด · Solver ได้อะไรและต้องส่งอะไร<br>ตัวตรวจ · สภาพแวดล้อม · ขนาดของการรัน (เช่น 3 epochs · 3 samples per task)", "margin-bottom:10px", 26, 21),
        box(USER, "2 ข้อมูล (data root)", "ไฟล์โจทย์ทุกข้อ และเฉลยของโจทย์", "margin-bottom:10px", 26, 21),
        box(USER, "3 ตัวตรวจ", "<span class='mono'>grade(task, snapshot)</span> → คะแนน 0 ถึง 1<br>snapshot = โฟลเดอร์ทำงานของ Solver ตอนจบ", "", 26, 21)])
    right = "".join([
        box(FILE, "Plug-in · <span class='mono' style='font-size:22px'>benchmark_plugin.py</span>", "ฟังก์ชันเดียว <span class='mono'>list_tasks(root)</span> คืนโจทย์ทุกข้อ<br>พร้อมชุด (train / validation / test) และค่าที่ตัวตรวจอ่าน", "margin-bottom:10px", 26, 21),
        box(FILE, "Reference Folder · <span class='mono' style='font-size:22px'>reference/</span>", "ทุกอย่างที่ผู้ใช้ส่งมา <b>ยกเว้น</b> ของชุด Validation · Test และตัวตรวจ<br>= สิ่งเดียวที่ Evolver รู้เกี่ยวกับ benchmark นอกจาก rollout", "margin-bottom:10px", 26, 21),
        box(INK, "โปรแกรมล็อก (Freeze)", "เก็บ sha256 ของ plug-in · ตัวตรวจ · รายการโจทย์<br>หลังจากนี้ไม่มี Agent ตัวใดแก้ได้", "", 26, 21)])
    body = """<h1>Benchmark Adaptor: แปลงคำสั่งของคนเป็นสนามทดลอง</h1>
    <div class='sub'>ทำงานครั้งเดียวก่อนมีสกิลตัวแรก · หลังจากนั้นการแบ่งชุดและตัวตรวจถูกล็อก</div>
    <div class='row' style='align-items:center'><div style='flex:1'>%s</div>
      <div style='text-align:center'>%s<div class='arrow'>➜</div></div><div style='flex:1.1'>%s</div></div>%s""" % (
        left, "<div style='background:%s;color:#fff;border-radius:20px;padding:18px 16px;font-size:27px;font-weight:800;line-height:1.25'>Benchmark<br>Adaptor</div>" % ADAPT, right, real)
    shot(D + "t03-adaptor.png", body, 800 if real else 690)


# ------------------------------------------------------------------ t04 เครื่องของ Evolver (Table 1)
def evolver_view():
    R, W = pill(EVOLVER, "อ่าน"), pill(SOLVER, "เขียน")
    rows = [
        ((EVOLVER,), "<span class='mono'>/evo/traces/epoch_K/</span>", "บันทึกเซสชันของ Solver ของ rollout ชุด Training ทุกครั้ง (ไม่ถูกแก้)", R),
        ((EVOLVER,), "<span class='mono'>/evo/scores/epoch_K.json</span>", "คะแนนของ rollout ชุด Training แต่ละครั้ง (0 ถึง 1) หรือ <i>grader_failed</i>", R),
        ((EVOLVER,), "<span class='mono'>/evo/solver_workspaces/epoch_K/</span>", "โฟลเดอร์ทำงานของ Solver ตอนจบ rollout แต่ละครั้ง", R),
        ((EVOLVER,), "<span class='mono'>/evo/skills/epoch_K/</span>", "ชุดสกิลที่ Solver ของ epoch K ใช้ (epoch 0 = ไม่มีสกิล)", R),
        ((EVOLVER,), "<span class='mono'>/evo/reference/</span>", "Reference Folder ของ Benchmark Adaptor (เฉพาะของชุด Training)", R),
        ((SOLVER,), "<span class='mono'>/evo/staging/</span>", "ชุดสกิลถัดไป · เริ่มจากชุดที่ Evolver ทิ้งไว้ครั้งก่อน", W),
        ((SOLVER,), "<span class='mono'>/evo/evolver_workspace/</span>", "โฟลเดอร์ส่วนตัวของ Evolver · อยู่ข้าม epoch (บันทึกและสคริปต์ของมันเอง)", W),
    ]
    body = """<h1>เครื่องของ Evolver: เห็นอะไร แก้อะไรได้</h1>
    <div class='sub'>Table 1 ของเปเปอร์ · K = หมายเลข epoch · ของทุก epoch ก่อนหน้ายังอยู่ครบ</div>%s%s""" % (
        table(["path บนเครื่องของ Evolver", "เก็บอะไร", "สิทธิ์"], rows, [520, None, 120]),
        "<div style='border:4px solid %s;background:#FDECE6;border-radius:18px;padding:12px 18px;font-size:25px;line-height:1.4;margin-top:10px'><b style='color:%s'>สิ่งที่ไม่เคยถูกส่งมาที่เครื่องนี้:</b> rollout และคะแนนของชุด Validation และ Test · โค้ดของตัวตรวจ · การกันนี้ทำโดยโปรแกรมควบคุมการรัน Evolver จึงเลี่ยงไม่ได้แม้จะพยายาม</div>" % (BAD, BAD))
    shot(D + "t04-evolver-view.png", body, 800)


# ------------------------------------------------------------------ t05 ใครเห็นอะไร
def who_sees():
    G, B, N = "#E4F2DE", "#FDE3DC", "#F3EEE7"

    def c(bg, t):
        return "<div style='background:%s;border-radius:12px;padding:9px 12px;font-size:21px;line-height:1.3'>%s</div>" % (bg, t)
    rows = [
        ((ADAPT,), "<b style='font-size:26px'>Benchmark Adaptor</b><br><span style='color:%s;font-size:20px'>ก่อนการรัน · ครั้งเดียว</span>" % MUTE,
         c(G, "<b>อ่าน</b> ทั้งหมด"), c(G, "<b>อ่าน</b> ทั้งหมด<br>เพื่อแบ่งชุดให้ถูก"), c(G, "<b>อ่าน</b> (รู้ว่าตัวตรวจ<br>ต้องการค่าอะไร)"), c(N, "ยังไม่มีสกิล")),
        ((SOLVER,), "<b style='font-size:26px'>Solver</b><br><span style='color:%s;font-size:20px'>ทุก rollout</span>" % MUTE,
         c(N, "เห็นเฉพาะข้อความ<br>ของโจทย์ที่กำลังทำ"), c(N, "เห็นเฉพาะข้อความ<br>ของโจทย์ที่กำลังทำ"), c(B, "<b>ไม่เห็น</b><br>(ไม่เห็นเฉลยด้วย)"), c(G, "<b>อ่าน</b> แล้วทำตาม")),
        ((EVOLVER,), "<b style='font-size:26px'>Evolver</b><br><span style='color:%s;font-size:20px'>ทุก epoch</span>" % MUTE,
         c(G, "<b>อ่าน</b> rollout · คะแนน<br>และ Reference Folder"), c(B, "<b>ไม่เห็นอะไรเลย</b><br>แม้แต่คะแนน"), c(B, "<b>ไม่เห็น</b><br>ได้แต่คะแนน 0 ถึง 1"), c(G, "<b>เขียน</b> ชุดถัดไป<br>อ่านชุดเก่าได้ทุกชุด")),
        ((USER,), "<b style='font-size:26px'>โปรแกรมควบคุมการรัน</b><br><span style='color:%s;font-size:20px'>ไม่ใช่โมเดล</span>" % MUTE,
         c(N, "ส่ง rollout ไปเครื่อง<br>ของ Evolver"), c(N, "บันทึกคะแนน<br>ไม่ส่งให้ใคร"), c(N, "รันตัวตรวจ<br>ของผู้ใช้"), c(N, "รับทุกชุด<br>ไม่มีการปฏิเสธ")),
    ]
    body = """<h1>ใครเห็นอะไร (Information Isolation)</h1>
    <div class='sub'>%s เห็นหรือเขียนได้ &nbsp; %s ไม่เห็น &nbsp; · &nbsp; เฉลยของโจทย์เห็นได้เฉพาะฝั่งผู้ปรับสกิล ไม่เคยให้ Solver เห็น</div>%s""" % (
        pill("#6BBF59", "เขียว"), pill(BAD, "แดง"),
        table(["", "ชุด Training", "ชุด Validation · Test", "ตัวตรวจ", "ชุดสกิล"], rows, [330, None, None, None, None]))
    shot(D + "t05-who-sees.png", body, 690)


# ------------------------------------------------------------------ t06 อัลกอริทึม
def algorithm():
    L = [("", "<b>รับเข้า</b>  คำสั่งของผู้ใช้ I · ข้อมูล D · ตัวตรวจ G · จำนวน epoch E · จำนวนครั้งต่อโจทย์ N", "", ""),
         ("1", "(plug-in, reference) ← <b>BenchmarkAdaptor</b>(I, D, G)", "ครั้งเดียว ก่อนมีสกิลตัวแรก", "adapt"),
         ("2", "ล็อก plug-in และ G ด้วย hash", "หลังจากนี้การแบ่งชุดและตัวตรวจเปลี่ยนไม่ได้", "adapt"),
         ("3", "S<sub>0</sub> ← ว่าง", "epoch 0 ไม่มีสกิล", "base"),
         ("4", "<b>Solver</b> ทำโจทย์ train · validation · test ด้วย S<sub>0</sub> ข้อละ N ครั้ง", "เส้นฐาน (Baseline)", "base"),
         ("5", "<b>ทำซ้ำ</b> K = 1 … E", "", ""),
         ("6", "&nbsp;&nbsp;&nbsp;&nbsp;<b>Evolver</b> (เซสชันเดิม) อ่าน rollout และคะแนนของ train + reference", "เห็นของทุก epoch ก่อนหน้า ไม่เห็น validation", "turn"),
         ("7", "&nbsp;&nbsp;&nbsp;&nbsp;S<sub>K</sub> ← สิ่งที่ Evolver ทิ้งไว้ใน staging", "<b>รับทุกชุด</b> ไม่มีการปฏิเสธ", "turn"),
         ("8", "&nbsp;&nbsp;&nbsp;&nbsp;<b>Solver</b> ทำโจทย์ validation ด้วย S<sub>K</sub> ข้อละ N ครั้ง", "บันทึกคะแนน ไม่ให้ Evolver เห็น", "rollout"),
         ("9", "&nbsp;&nbsp;&nbsp;&nbsp;<b>ถ้า</b> K &lt; E: <b>Solver</b> ทำโจทย์ train ด้วย S<sub>K</sub> ข้อละ N ครั้ง", "หลักฐานของตาถัดไป", "rollout"),
         ("10", "<b>Solver</b> ทำโจทย์ test ด้วย S<sub>E</sub> ข้อละ N ครั้ง", "วัดครั้งเดียว ด้วยชุดของ epoch สุดท้าย", "test"),
         ("", "<b>ส่งออก</b>  S<sub>E</sub> และชุดสกิลของทุก epoch", "", "")]
    col = {"adapt": ADAPT, "base": SOLVER, "turn": EVOLVER, "rollout": SOLVER, "test": INK}
    tr = ""
    for n, code, note, cmd in L:
        tr += "<tr><td style='width:60px;text-align:right;color:%s;font-weight:800'>%s</td><td style='%s;font-size:23px'>%s</td><td style='color:%s;font-size:21px'>%s</td><td style='width:150px'>%s</td></tr>" % (
            MUTE, n, MONO, code, MUTE, note, pill(col[cmd], cmd, 21) if cmd else "")
    body = """<h1>อัลกอริทึมของ EvoSkill v2</h1>
    <div class='sub'>เรียบเรียงจาก Section 3 ของเปเปอร์ · คอลัมน์ขวา = คำสั่งของ <span class='mono'>evoskill.py</span> ที่ทำบรรทัดนั้น</div>
    <table class='t' style='border-spacing:0 5px'><tr><th></th><th>ขั้นตอน</th><th>หมายเหตุ</th><th>คำสั่ง</th></tr>%s</table>%s""" % (
        tr, strip(EVOLVER, "สิ่งที่ <b>ไม่มี</b> ในอัลกอริทึมนี้: บรรทัด \"ถ้าคะแนนดีขึ้นจึงรับ\" · คะแนน Validation ไม่ถูกใช้ตัดสินอะไรระหว่างการรันเลย", 24, 8))
    shot(D + "t06-algorithm.png", body, 900)


# ------------------------------------------------------------------ t07 การตัดสินใจออกแบบ 4 ข้อ
def choices():
    rows = [
        ((EVOLVER,), "<b style='font-size:25px'>1 Evolver เป็น Agent ที่มี bash</b>", "ลำดับของการเรียกโมเดลครั้งเดียว<br>ตอบจากข้อความใน prompt<br><span style='color:%s'>(SkillOpt · GEPA · ACE)</span>" % MUTE,
         "Claude Code ที่รันโค้ดได้<br>และแตกงานให้ subagent ได้", "<b>ทดสอบคำอธิบาย</b> ของจุดพลาดได้<br>ก่อนเขียนลงสกิล"),
        ((EVOLVER,), "<b style='font-size:25px'>2 Evolver มีสถานะ (Stateful)</b>", "เริ่มเซสชันใหม่ทุกรอบ<br><span style='color:%s'>(SkillBoost · 8 จาก 13 ระบบที่สำรวจ)</span>" % MUTE,
         "<b>เซสชันเดียวตลอดการรัน</b><br>+ โฟลเดอร์ส่วนตัวข้าม epoch", "ทุกตาเก็บ ย้อนกลับ หรือผสม<br>สิ่งที่เคยลองได้ทั้งหมด"),
        ((SOLVER,), "<b style='font-size:25px'>3 หลายครั้งต่อโจทย์</b>", "โจทย์ละ 1 ครั้ง<br><span style='color:%s'>(35 จาก 43 ระบบที่สำรวจ)</span>" % MUTE,
         "โจทย์ละ <b>N = 3 ครั้ง</b>", "แยก <b>พลาดซ้ำ</b> ออกจาก<br>พลาดโดยบังเอิญได้"),
        ((INK,), "<b style='font-size:25px'>4 รับชุดสกิลของทุก epoch</b>", "เก็บเฉพาะเมื่อคะแนนผ่านเกณฑ์<br><span style='color:%s'>(SkillOpt: Validation สูงขึ้น)</span>" % MUTE,
         "<b>ไม่มีขั้นปฏิเสธ</b><br>ทดสอบชุดของ epoch สุดท้าย", "คะแนนแกว่ง ประตูรับอาจทิ้งของดี<br>การแก้ที่พลาดกลายเป็น <b>หลักฐาน</b>"),
    ]
    body = """<h1>การตัดสินใจออกแบบ 4 ข้อของ Evolver</h1>
    <div class='sub'>Section 6 ของเปเปอร์ · ทั้ง 4 ข้อใช้เหมือนกันทั้งสอง benchmark และเป็นสิ่งที่ต่างจากวิธีที่นำมาเทียบ</div>%s""" % table(
        ["การตัดสินใจ", "วิธีที่พบบ่อย", "EvoSkill v2 เลือก", "ได้อะไร"], rows, [400, None, None, None], 22)
    shot(D + "t07-design-choices.png", body, 720)


# ------------------------------------------------------------------ t08 ความแกว่งของ rollout (Table 2)
def mixed():
    data = [("SpreadsheetBench v2 · Training (57 โจทย์)", [("ไม่มีสกิล", 10, 4, 43), ("ตาที่ 1", 27, 11, 19), ("ตาที่ 2", 36, 12, 9)]),
            ("SpreadsheetBench v2 · Validation (57 โจทย์)", [("ไม่มีสกิล", 5, 5, 47), ("ตาที่ 1", 14, 5, 38), ("ตาที่ 2", 10, 9, 38), ("ตาที่ 3", 11, 8, 38)]),
            ("τ³-bench banking · Training (19 โจทย์)", [("ไม่มีสกิล", 3, 7, 9), ("ตาที่ 1", 10, 3, 6), ("ตาที่ 2", 7, 10, 2)]),
            ("τ³-bench banking · Validation (20 โจทย์)", [("ไม่มีสกิล", 3, 5, 12), ("ตาที่ 1", 7, 8, 5), ("ตาที่ 2", 6, 8, 6), ("ตาที่ 3", 7, 9, 4)])]
    G, Y, R = "#6BBF59", "#F4A261", "#E76F51"
    blocks = ""
    for title, rows in data:
        inner = ""
        for name, a, m, z in rows:
            tot = a + m + z
            seg = "".join("<div style='width:%.2f%%;background:%s;color:#fff;font-weight:800;font-size:21px;text-align:center;line-height:38px'>%s</div>" % (
                v * 100.0 / tot, c, v) for v, c in ((a, G), (m, Y), (z, R)))
            inner += "<div style='display:flex;align-items:center;gap:10px;margin:5px 0'><div style='width:120px;font-size:22px'>%s</div><div style='flex:1;display:flex;border-radius:10px;overflow:hidden'>%s</div><div style='width:150px;font-size:21px;color:%s'>บางครั้ง %d%%</div></div>" % (
                name, seg, MUTE, round(m * 100.0 / tot))
        blocks += "<div class='card' style='flex:1 1 46%%;padding:12px 18px'><div style='font-size:24px;font-weight:800;color:%s;margin-bottom:4px'>%s</div>%s</div>" % (INK, title, inner)
    body = """<h1>Solver ทำโจทย์เดิมซ้ำ ผลไม่เหมือนกันทุกครั้ง</h1>
    <div class='sub'>Table 2 ของเปเปอร์ · จำนวนโจทย์แยกตามจำนวนครั้งที่ผ่านจาก 3 ครั้ง &nbsp; %s &nbsp; %s &nbsp; %s</div>
    <div style='display:flex;flex-wrap:wrap;gap:14px'>%s</div>%s""" % (
        pill(G, "ผ่าน 3/3"), pill(Y, "ผ่านบางครั้ง (1–2/3)"), pill(R, "ผ่าน 0/3"), blocks,
        strip(SOLVER, "โจทย์ที่ <b>ผ่านบางครั้ง</b> มี 7%–21% บน SpreadsheetBench v2 และ 16%–53% บน τ³-bench · ถ้าวัดโจทย์ละ 1 ครั้ง โจทย์กลุ่มนี้จะปรากฏเป็น \"ผ่าน\" หรือ \"พลาด\" <b>ตามโชค</b>", 24))
    shot(D + "t08-mixed-tasks.png", body, 800)


# ------------------------------------------------------------------ t09 ข้อเสนอที่ถูกปฏิเสธ (Table 3)
def rejected():
    rows = [
        ((SOLVER,), "SkillOpt ก้าวที่ 2", "SpreadsheetBench v2", "Validation", "17 เทียบ 19", "<b>2</b>"),
        ((SOLVER,), "SkillOpt ก้าวที่ 3", "SpreadsheetBench v2", "Validation", "17 เทียบ 19", "<b>2</b>"),
        ((SOLVER,), "SkillOpt สกิลสุดท้าย", "SpreadsheetBench v2", "Validation", "18 เทียบ 19", "<b>1</b>"),
        ((SOLVER,), "SkillOpt ก้าวที่ 3", "τ³-bench banking", "Validation", "8 เทียบ 9", "<b>1</b>"),
        ((SOLVER,), "SkillOpt สกิลสุดท้าย", "τ³-bench banking", "Validation", "8 เทียบ 9", "<b>1</b>"),
        ((FILE,), "SkillBoost รอบที่ 3", "SpreadsheetBench v2", "Training", "20 และ 21 เทียบ 21", "พลาดใหม่ 4 และ 2"),
        ((FILE,), "SkillBoost รอบที่ 3", "τ³-bench banking", "Training", "10 และ 7 เทียบ 8", "พลาดใหม่ 1 และ 3"),
    ]
    body = """<h1>ประตูรับตัดสินด้วยผลต่างที่เล็กกว่าความแกว่ง</h1>
    <div class='sub'>Table 3 ของเปเปอร์ (คัดมา) · ข้อเสนอที่ SkillOpt และ SkillBoost <b>ปฏิเสธ</b> ในการรันที่เห็น Ground Truth ละเอียด · วัดโจทย์ละ 1 ครั้ง</div>%s
    <div class='row' style='margin-top:14px;align-items:stretch'>%s<div class='arrow'>&lt;</div>%s</div>%s""" % (
        table(["ข้อเสนอที่ถูกปฏิเสธ", "benchmark", "ชุดที่ใช้ตัดสิน", "โจทย์ที่ผ่าน (ใหม่ เทียบ เดิม)", "ต่างกันกี่โจทย์"], rows, [330, 330, 220, None, 260], 22),
        box(BAD, "ผลต่างที่ใช้ตัดสิน", "<b style='font-size:34px;color:%s'>ไม่เกิน 2 โจทย์</b> ทุกครั้งที่ปฏิเสธ" % BAD, "flex:1", 26, 24),
        box(SOLVER, "โจทย์ที่ผลแกว่งระหว่างครั้ง", "<b style='font-size:34px;color:%s'>3 ถึง 12 โจทย์</b> ต่อชุด (Table 2)" % INK, "flex:1", 26, 24),
        strip(BAD, "ถ้าสุ่ม rollout ใหม่อีกครั้ง ข้อเสนอที่ถูกปฏิเสธเหล่านี้ <b>ตัวใดก็อาจถูกรับได้</b> · การตัดสินจึงสะท้อนโชคของการวัด มากกว่าคุณภาพของสกิล", 24))
    shot(D + "t09-rejected.png", body, 860)


# ------------------------------------------------------------------ t10 ผลในเปเปอร์: Held-out
def bars(groups, total, colors, h=300):
    """groups = [(ชื่อกลุ่ม, [(ชื่อ, จำนวนที่ผ่าน), ...])] -> HTML แท่งแนวตั้ง"""
    out = ""
    for gname, items in groups:
        cols = ""
        for (name, v), col in zip(items, colors[:len(items)] if len(items) == len(colors) else colors):
            p = v * 100.0 / total
            cols += """<div style='flex:1;text-align:center'><div style='height:%dpx;display:flex;flex-direction:column;justify-content:flex-end'>
              <div style='font-size:25px;font-weight:800;color:%s'>%d</div><div style='font-size:19px;color:%s;margin-bottom:3px'>%.1f%%</div>
              <div style='height:%.0fpx;background:%s;border-radius:10px 10px 0 0;margin:0 8px'></div></div>
              <div style='font-size:19px;line-height:1.2;margin-top:6px;height:50px'>%s</div></div>""" % (h, INK, v, MUTE, p, p / 60.0 * (h - 62), col, name)
        out += "<div class='card' style='flex:1;padding:12px 10px'><div style='font-size:24px;font-weight:800;color:%s;text-align:center;margin-bottom:4px'>%s</div><div style='display:flex'>%s</div></div>" % (INK, gname, cols)
    return "<div class='row' style='gap:14px'>%s</div>" % out


def paper_heldout():
    C4 = ["#BCAAA4", FILE, SOLVER, EVOLVER]
    ssb = bars([("เห็น Ground Truth ละเอียด", [("ไม่มีสกิล", 81), ("SkillBoost", 101), ("SkillOpt", 102), ("EvoSkill v2", 126)]),
                ("เห็นแค่ผ่านหรือไม่ผ่าน", [("ไม่มีสกิล", 81), ("SkillBoost", 85), ("SkillOpt", 107), ("EvoSkill v2", 105)])], 312, C4, 290)
    C5 = ["#BCAAA4", FILE, SOLVER, "#7FC8BE", EVOLVER]
    tau = bars([("เห็น Ground Truth ละเอียด", [("ไม่มีสกิล", 26), ("SkillBoost", 36), ("SkillOpt", 43), ("EvoSkill v2<br>Haiku evolver", 46), ("EvoSkill v2", 48)]),
                ("เห็นแค่ผ่านหรือไม่ผ่าน", [("ไม่มีสกิล", 26), ("SkillBoost", 23), ("SkillOpt", 37), ("EvoSkill v2<br>Haiku evolver", 33), ("EvoSkill v2", 41)])], 93, C5, 290)
    body = """<h1>ผลในเปเปอร์: Held-out Test</h1>
    <div class='sub'>จำนวน episode ที่ผ่าน (ตัวเลขบนแท่ง) และ pass rate · Solver ตัวเดียวกันทุกวิธี · ทุกวิธีใช้ Claude Sonnet 5.5 เป็นผู้ปรับสกิล (ยกเว้นแท่ง Haiku evolver)</div>
    <div style='font-size:27px;font-weight:800;color:%s;margin:2px 0 8px'>SpreadsheetBench v2 · Solver = Sonnet 5.5 · 104 โจทย์ × 3 ครั้ง = 312 episode</div>%s
    <div style='font-size:27px;font-weight:800;color:%s;margin:16px 0 8px'>τ³-bench banking · Solver = Haiku 5.5 · 31 โจทย์ × 3 ครั้ง = 93 episode</div>%s""" % (INK, ssb, INK, tau)
    shot(D + "t10-paper-heldout.png", body, 1010)


# ------------------------------------------------------------------ t11 ผลในเปเปอร์: ต้นทุนของผู้ปรับสกิล
def paper_cost():
    def tb(title, total, rows):
        tr = ""
        for name, col, h1, c1, p1, h2, c2, p2 in rows:
            tr += "<tr><td style='border-left:14px solid %s;font-weight:800'>%s</td><td>%s</td><td>%s</td><td><b>%s</b></td><td>%s</td><td>%s</td><td><b>%s</b></td></tr>" % (col, name, h1, c1, p1, h2, c2, p2)
        return """<div style='font-size:26px;font-weight:800;color:%s;margin:12px 0 0'>%s (Held-out จาก %d episode)</div>
        <table class='t' style='table-layout:fixed'><tr><th style='width:400px'></th><th colspan='3' style='font-weight:800;color:#4A2F1F'>เห็น Ground Truth ละเอียด</th><th colspan='3' style='font-weight:800;color:#4A2F1F'>เห็นแค่ผ่านหรือไม่ผ่าน</th></tr>
        <tr><th></th><th>Held-out</th><th>ต้นทุน</th><th>ต่อ 1 จุดที่เพิ่ม</th><th>Held-out</th><th>ต้นทุน</th><th>ต่อ 1 จุดที่เพิ่ม</th></tr>%s</table>""" % (INK, title, total, tr)
    ssb = tb("SpreadsheetBench v2", 312, [
        ("ไม่มีสกิล", "#BCAAA4", "81", "–", "–", "81", "–", "–"),
        ("SkillBoost", FILE, "101", "$13.95", "$2.18", "85", "$13.66", "$10.65"),
        ("SkillOpt", SOLVER, "102", "$8.56", "$1.27", "107", "$6.65", "$0.80"),
        ("EvoSkill v2", EVOLVER, "126", "$12.84", "$0.89", "105", "$0.53", "$0.07")])
    tau = tb("τ³-bench banking", 93, [
        ("ไม่มีสกิล", "#BCAAA4", "26", "–", "–", "26", "–", "–"),
        ("SkillBoost", FILE, "36", "$6.98", "$0.65", "23", "$8.64", "ไม่เพิ่ม"),
        ("SkillOpt", SOLVER, "43", "$5.55", "$0.30", "37", "$6.22", "$0.53"),
        ("EvoSkill v2 · Haiku evolver", "#7FC8BE", "46", "$1.87", "$0.09", "33", "$0.73", "$0.10"),
        ("EvoSkill v2", EVOLVER, "48", "$0.99", "$0.04", "41", "$1.55", "$0.10")])
    body = """<h1>ผลในเปเปอร์: ต้นทุนของผู้ปรับสกิล</h1>
    <div class='sub'>Table 4 และ 5 ของเปเปอร์ · ต้นทุน = ราคาตามรายการของผู้ปรับสกิลอย่างเดียว (ไม่รวม rollout ของ Solver) · Held-out = จำนวน episode ที่ผ่าน</div>%s%s%s""" % (
        ssb, tau, strip(EVOLVER, "\"ต่อ 1 จุดที่เพิ่ม\" = ต้นทุน ÷ จำนวนจุดของ pass rate บน Held-out ที่เพิ่มจากไม่มีสกิล · EvoSkill v2 ต่ำสุดทั้ง 4 การเทียบ", 24, 10))
    shot(D + "t11-paper-cost.png", body, 960)


# ------------------------------------------------------------------ t12 ผลในเปเปอร์: รายอีพ็อก
def paper_epochs():
    def chart(title, series, lo=10, hi=90, note=""):
        W, H, x0, y0 = 720, 380, 70, 20

        def X(i):
            return x0 + 40 + i * (W - x0 - 90) / 3.0

        def Y(v):
            return y0 + (hi - v) / float(hi - lo) * (H - y0 - 50)
        svg = ""
        for v in range(lo, hi + 1, 20):
            svg += "<line x1='%d' y1='%.0f' x2='%d' y2='%.0f' stroke='%s' stroke-width='2'/><text x='%d' y='%.0f' font-size='19' fill='%s' text-anchor='end'>%d%%</text>" % (
                x0, Y(v), W - 10, Y(v), LINE, x0 - 8, Y(v) + 6, MUTE, v)
        for i, lab in enumerate(["ไม่มีสกิล", "epoch 1", "epoch 2", "epoch 3"]):
            svg += "<text x='%.0f' y='%d' font-size='20' fill='%s' text-anchor='middle'>%s</text>" % (X(i), H - 12, MUTE, lab)
        for name, col, dash, vals, dy in series:
            pts = " ".join("%.0f,%.0f" % (X(i), Y(v)) for i, v in enumerate(vals))
            svg += "<polyline points='%s' fill='none' stroke='%s' stroke-width='6' %s/>" % (pts, col, "stroke-dasharray='14 9'" if dash else "")
            for i, v in enumerate(vals):
                svg += "<circle cx='%.0f' cy='%.0f' r='9' fill='%s' stroke='#fff' stroke-width='3'/><text x='%.0f' y='%.0f' font-size='21' font-weight='800' fill='%s' text-anchor='middle'>%.1f</text>" % (
                    X(i), Y(v), col, X(i), Y(v) + dy, col, v)
        return "<div class='card' style='flex:1;padding:12px 14px'><div style='font-size:24px;font-weight:800;color:%s'>%s</div><svg width='%d' height='%d'>%s</svg><div class='note' style='font-size:21px'>%s</div></div>" % (INK, title, W, H, svg, note)
    a = chart("SpreadsheetBench v2 · เห็น Ground Truth ละเอียด", [("train", SOLVER, True, [21.6, 57.3, 73.1], -18), ("val", EVOLVER, False, [12.9, 28.1, 25.7, 25.7], 32)],
              note="Training ขึ้น <b>51.5 จุด</b> · Validation ขึ้น <b>12.8 จุด</b>")
    b = chart("τ³-bench banking · ไม่เห็นเฉลยของ Training", [("train", SOLVER, True, [33.3, 47.4, 82.5], -18), ("val", EVOLVER, False, [26.7, 38.3, 50.0, 46.7], 32)],
              note="Training ขึ้น <b>49.2 จุด</b> · Validation ขึ้น <b>20.0 จุด</b>")
    body = """<h1>ผลในเปเปอร์: คะแนนราย epoch</h1>
    <div class='sub'>pass rate ของ EvoSkill v2 (ร้อยละของ episode) &nbsp; %s &nbsp; %s</div>
    <div class='row'>%s%s</div>%s""" % (
        pill(SOLVER, "เส้นประ = Training (Evolver เห็น)"), pill(EVOLVER, "เส้นทึบ = Validation (Evolver ไม่เห็น)"), a, b,
        strip(BAD, "Training ขึ้นมากกว่า Validation หลายเท่า = Evolver เขียนกฎบางข้อที่ <b>เข้ากับโจทย์ชุด Training โดยเฉพาะ</b> และใช้กับโจทย์อื่นไม่ได้ (Overfitting ของผู้ปรับสกิล) · เปเปอร์รายงานเรื่องนี้เอง", 24))
    shot(D + "t12-paper-epochs.png", body, 770)


# ------------------------------------------------------------------ t13 เทียบวิธีปรับสกิล
def methods():
    rows = [
        ((FILE,), "<b style='font-size:24px'>SkillOpt</b>", "ลำดับของการเรียกโมเดลครั้งเดียว<br>(40 ครั้งในการรัน 1 ครั้ง)", "ข้อความที่ส่งต่อ:<br>สกิล และโน้ต", "1", "Validation ต้องสูงขึ้น", "ผลตรวจรายจุดของ<br>Training ที่พลาด"),
        ((FILE,), "<b style='font-size:24px'>SkillBoost</b>", "Agent · <b>เซสชันใหม่</b> ทุกรอบ", "สกิล", "1", "Training ผ่านมากขึ้น และ<br>พลาดใหม่น้อยกว่า 5%", "จุดผิดจุดแรกของ<br>Training ที่พลาด"),
        ((USER,), "<b style='font-size:24px'>Skill Optimizer</b><br><span style='font-size:19px;color:%s'>บท 05</span>" % MUTE, "Claude Code ตามพรอมต์ของคน<br>ทีละรอบ", "<span class='mono'>ISSUES.md</span>", "3", "ดีขึ้นเกินความแกว่ง<br>และ Validation ไม่ลด", "ข้อตรวจที่ไม่ผ่านของ<br>Training"),
        ((SOLVER,), "<b style='font-size:24px'>WikiSkill</b><br><span style='font-size:19px;color:%s'>บท 06</span>" % MUTE, "Maintainer (เรียก 1 ครั้ง) +<br>Proposer (ReAct · อ่านอย่างเดียว)", "Wiki ที่ไม่ย้อนกลับ", "3", "Validation ต้องสูงกว่า<br>R_best", "ข้อความของตัวตรวจ<br>ใน Trace ของ Training"),
        ((EVOLVER,), "<b style='font-size:24px'>EvoSkill v2</b><br><span style='font-size:19px;color:%s'>บทนี้</span>" % MUTE, "Agent ที่มี bash<br><b>เซสชันเดียวตลอดการรัน</b>", "บริบทของเซสชัน + โฟลเดอร์<br>ส่วนตัว + ทุกชุดสกิลและ rollout", "3", "<b>รับทุก epoch</b>", "คะแนน 0 ถึง 1<br>(+ เฉลยของ Training ถ้าผู้ใช้ให้)"),
    ]
    body = """<h1>EvoSkill v2 เทียบกับวิธีปรับสกิลอื่น</h1>
    <div class='sub'>2 แถวบน = วิธีที่เปเปอร์นำมาเทียบ · 2 แถวกลาง = วิธีของบท 05 และ 06 ตามที่ใช้ใน LAB ของเรา</div>%s""" % table(
        ["วิธี", "ผู้ปรับสกิลคืออะไร", "จำอะไรข้ามรอบ", "ครั้งต่อ<br>โจทย์", "กติการับสกิล", "เห็นอะไรจากตัวตรวจ"], rows, [215, 330, 280, 95, 255, None], 21)
    shot(D + "t13-methods.png", body, 760)


ALL = {"v1v2": v1v2, "architecture": architecture, "adaptor": adaptor, "evolver_view": evolver_view, "who_sees": who_sees,
       "algorithm": algorithm, "choices": choices, "mixed": mixed, "rejected": rejected, "paper_heldout": paper_heldout,
       "paper_cost": paper_cost, "paper_epochs": paper_epochs, "methods": methods}

# ------------------------------------------------------------------ t14 เส้นเวลาของ 1 การรัน (ผลจริง)
def timeline(ws="e1", out=None):
    st = state(ws)
    if not st or st["phase"] != "test":
        print("ข้าม timeline: ยังไม่มี runs/%s ที่รันจบ" % ws)
        return
    L, T, E = st["legs"], st["turns"], st["epochs"]

    def sc(lb):
        return pct(L[lb]["score"]) if lb in L else "–"

    def step(color, head, title, lines, flex="1"):
        return """<div style='flex:%s;background:#fff;border:3px solid %s;border-top:12px solid %s;border-radius:16px;padding:9px 10px;text-align:center'>
          <div style='font-size:18px;font-weight:800;color:%s;letter-spacing:.5px'>%s</div>
          <div style='font-size:24px;font-weight:800;color:%s;line-height:1.15;margin:2px 0 4px'>%s</div>
          <div style='font-size:20px;color:%s;line-height:1.35'>%s</div></div>""" % (flex, LINE, color, color, head, INK, title, MUTE, lines)
    ar = "<div style='align-self:center;font-size:30px;font-weight:800;color:#6F4E37'>➜</div>"
    ad = st["adapt"]
    row1 = [step(ADAPT, "adapt", "Benchmark Adaptor", "%.0f วินาที<br>โจทย์ %d · %d · %d<br>reference %d ไฟล์" % (
        ad["wall_s"], ad["tasks"]["train"], ad["tasks"]["validation"], ad["tasks"]["test"], ad["reference"]["files"]), "1.05"),
        step(SOLVER, "base · epoch 0", "Solver ไม่มีสกิล", "Training <b>%s</b><br>Validation <b>%s</b><br>Test <b>%s</b>" % (sc("base_train"), sc("base_val"), sc("base_test")))]
    row2 = []
    for t in T:
        k = t["k"]
        ev = step(EVOLVER, "turn · ตาที่ %d" % k, "Evolver", "%.0f วินาที · Bash %d ครั้ง<br>skills_v%d · %.1f KB" % (t["wall_s"], t["bash"], k, t["skill_md_bytes"] / 1024.0))
        so = step(SOLVER, "rollout · epoch %d" % k, "Solver + skills_v%d" % k, "Validation <b>%s</b><br>%s" % (
            sc("v%d_val" % k), ("Training <b>%s</b>" % sc("v%d_train" % k)) if k < E else "<span style='color:%s'>(epoch สุดท้าย ไม่วัด Training)</span>" % MUTE))
        (row1 if k == 1 else row2).extend([ev, so])
    row2.append(step(INK, "test", "Held-out Test", "skills_v%d<br><b style='font-size:26px;color:%s'>%s</b>" % (E, INK, sc("v%d_test" % E)), "0.8"))
    tot = sum(s["n"] for s in L.values())
    body = """<h1>เส้นเวลาของการรัน %s (ผลจริง)</h1>
    <div class='sub'>%d epochs · โจทย์ละ %d ครั้ง · %s Benchmark Adaptor &nbsp;%s Solver &nbsp;%s Evolver &nbsp; · &nbsp; ตัวเลข = คะแนนเฉลี่ยของ leg นั้น</div>
    <div class='row' style='gap:8px;align-items:stretch'>%s</div>
    <div style='text-align:center;font-size:26px;font-weight:800;color:#6F4E37;margin:6px 0'>↓</div>
    <div class='row' style='gap:8px;align-items:stretch'>%s</div>%s""" % (
        ws, E, st["n"], pill(ADAPT, "&nbsp;"), pill(SOLVER, "&nbsp;"), pill(EVOLVER, "&nbsp;"), ar.join(row1), ar.join(row2),
        strip(EVOLVER, "รวม rollout ของ Solver <b>%d ครั้ง</b> ($%.2f) · Evolver <b>%d ตา</b> ($%.2f) · Evolver เห็นเฉพาะผลของ Training · คะแนน Validation และ Test ในภาพนี้ <b>Evolver ไม่เคยเห็น</b>" % (
            tot, sum(s["cost_usd"] for s in L.values()), len(T), sum(t["cost_usd"] for t in T)), 23))
    shot(out or (D + "t14-run-timeline.png"), body)


# ------------------------------------------------------------------ t15 Evolver ทำอะไรในแต่ละตา (e1 · สรุปจาก turns/turn_K/actions.md)
E1_TURNS = [
    ("อ่านคะแนนของ epoch 0 และรายการไฟล์<br>อ่านโจทย์และเฉลยอ้างอิงใน <span class='mono'>reference/</span><br>เทียบโค้ดของ Solver กับเฉลยทีละโจทย์",
     "Solver ไม่ตรวจ input และปัดเศษลง<br>ซ้ำกันทุก rollout",
     "เขียนสกิลใหม่ 1 ตัว: ตรวจ input · ปัดครึ่งขึ้นครั้งเดียว · รันเทสต์ก่อนส่ง"),
    ("<b>รันเทสต์ของเฉลยกับโค้ดของ Solver ทั้ง 12 ไฟล์</b><br>ผ่านครบ แต่คะแนนยังเป็น 0.7<br>กลับไปอ่านเฉลยอีกครั้ง",
     "เฉลยทุกข้อมี <span class='mono'>main()</span> ที่อ่าน JSON จาก stdin<br>\"ตัวตรวจอาจเรียกผ่าน CLI\" (ระบุว่ายังเป็นการเดา)",
     "เพิ่มหัวข้อ CLI พร้อมแม่แบบ <span class='mono'>main()</span> และวิธีทดสอบ"),
    ("<b>เขียนสคริปต์ fuzz</b> ป้อน input หลายพันชุด<br>ให้โค้ดของ Solver และเฉลย แล้วเทียบผล<br>ทดสอบ CLI ด้วย stdin ผิดรูปแบบ",
     "โค้ดทำงานเหมือนเฉลยแล้ว<br>\"บอกสาเหตุของ 0.1 ที่เหลือไม่ได้\"",
     "เพิ่มหัวข้อตรวจท้ายงาน (เป็นการกันพลาด ไม่ใช่การแก้ที่มีหลักฐาน)"),
]


def evolver_turns():
    st = state("e1")
    if not st or len(st["turns"]) < 3:
        print("ข้าม evolver_turns: ยังไม่มี runs/e1")
        return
    L = st["legs"]
    cols = ""
    for t, (did, found, wrote) in zip(st["turns"], E1_TURNS):
        k = t["k"]
        before = L["base_train" if k == 1 else "v%d_train" % (k - 1)]["score"]
        after = L["v%d_val" % k]["score"]

        def sec(color, head, txt):
            return "<div style='margin-top:10px'><div style='font-size:19px;font-weight:800;color:%s'>%s</div><div style='font-size:21px;line-height:1.36;color:%s'>%s</div></div>" % (color, head, INK, txt)
        cols += """<div class='card' style='flex:1;border-top:14px solid %s;padding:12px 16px'>
          <div style='font-size:30px;font-weight:800;color:%s'>ตาที่ %d</div>
          <div style='font-size:21px;color:%s'>%.0f วินาที · Bash %d ครั้ง (รัน Python %d) · $%.2f</div>
          <div style='font-size:21px;color:%s;margin-top:2px'>คะแนน Training ที่เห็น: <b>%s</b></div>%s%s%s
          <div style='margin-top:12px;background:#E4F2DE;border-radius:12px;padding:8px 12px;font-size:22px'>Validation หลังใช้ skills_v%d: <b>%s</b></div></div>""" % (
            EVOLVER, INK, k, MUTE, t["wall_s"], t["bash"], t["bash_python"], t["cost_usd"], MUTE, pct(before),
            sec(EVOLVER, "ทำอะไร", did), sec(BAD, "ข้อสรุป", found), sec(SOLVER, "เขียนอะไรลงสกิล", wrote), k, pct(after))
    body = """<h1>Evolver ทำอะไรในแต่ละตา (การรัน e1)</h1>
    <div class='sub'>สรุปจาก <span class='mono'>runs/e1/turns/turn_K/actions.md</span> · ทั้ง 3 ตาอยู่ในเซสชันเดียวกัน · Evolver เห็นคะแนนเป็นตัวเลขอย่างเดียว ไม่เห็นว่าข้อตรวจใดไม่ผ่าน</div>
    <div class='row' style='align-items:stretch'>%s</div>""" % cols
    shot(D + "t15-evolver-turns.png", body)


# ------------------------------------------------------------------ t16 อัลกอริทึม -> โค้ดของบทนี้ -> source code ต้นฉบับ
def code_map():
    m = "<span class='mono'>%s</span>"
    rows = [
        ((ADAPT,), "1–2 &nbsp; Benchmark Adaptor และการล็อก", (m % "adapt") + " · " + (m % "cmd_adapt() audit() verify()") + "<br>prompt: " + (m % "prompts/adaptor.md"),
         (m % "prompts/BA_GUIDANCE.template.md") + "<br>" + (m % "plugin_runner.py") + " · " + (m % "plugin_api.py")),
        ((SOLVER,), "3–4 &nbsp; epoch 0 ไม่มีสกิล", (m % "base") + " · " + (m % "cmd_base()") + " → " + (m % "rollouts()"),
         (m % "scripts/cc_solver/") + "<br>" + (m % "scripts/daytona/cc_leg_driver.py")),
        ((EVOLVER,), "6–7 &nbsp; ตาของ Evolver · รับทุกชุด", (m % "turn") + " · " + (m % "cmd_turn() sync_evo() agent()") + "<br>prompt: " + (m % "evolver_system.md") + " · " + (m % "evolver_message.md"),
         (m % "scripts/daytona/evolver_session.py") + "<br>" + (m % "prompts/EVOLVER_SYSTEM.md") + " · " + (m % "EPOCH_MESSAGE.md")),
        ((SOLVER,), "8–9 &nbsp; Solver ใช้ skills_vK", (m % "rollout") + " · " + (m % "cmd_rollout()") + " → " + (m % "rollouts()"), m % "src/orchestrator/loop.py"),
        ((INK,), "10 &nbsp; Held-out Test", (m % "test") + " · " + (m % "cmd_test()"), m % "src/orchestrator/loop.py"),
        ((FILE,), "ทั้งอัลกอริทึม", (m % "run") + " · " + (m % "cmd_run() next_step()"), (m % "src/run.py") + " (คำสั่ง " + (m % "evoskill run") + ")"),
        ((USER,), "สิ่งที่ผู้ใช้ส่ง", (m % "bench/instruction.md") + " · " + (m % "split.json") + "<br>" + (m % "benchmark_grader.py") + " · " + (m % "data/"),
         (m % "examples/ssbv2/") + " · " + (m % "examples/tau3_banking/") + "<br>(" + (m % "instruction.md") + " · " + (m % "split.json") + " · " + (m % "grader.py") + ")"),
    ]
    body = """<h1>อัลกอริทึม → โค้ดของบทนี้ → source code ต้นฉบับ</h1>
    <div class='sub'>คอลัมน์กลาง = <span class='mono'>evoskill/evoskill.py</span> ของบทนี้ · คอลัมน์ขวา = <span class='mono'>github.com/sentient-agi/EvoSkill</span> (branch v2)</div>%s""" % table(
        ["บรรทัดของอัลกอริทึม (ขั้น 10)", "คำสั่งและฟังก์ชันของบทนี้", "ไฟล์ใน source code ต้นฉบับ"], rows, [430, None, None], 21)
    shot(D + "t16-code-map.png", body)


ALL.update({"timeline": timeline, "evolver_turns": evolver_turns, "code_map": code_map})


if __name__ == "__main__":
    for name in (sys.argv[1:] or list(ALL)):
        ALL[name]()
