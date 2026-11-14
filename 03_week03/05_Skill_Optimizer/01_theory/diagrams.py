#!/usr/bin/env python3
"""วาดตารางของบททฤษฎี SkillOpt เป็น PNG (HTML -> Chrome headless ตัวอักษรไทยและสัญลักษณ์ตรงทุกตัว)

  python 01_theory/diagrams.py            (รันบนเครื่อง จากโฟลเดอร์ของบท)
  python 01_theory/diagrams.py mapping    (วาดเฉพาะภาพที่ระบุ)
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "tools"))
import charts
from charts import shot

charts.OUT = os.path.join(HERE, "img")
MONO = "font-family:Consolas,monospace"
INK, MUTE, LINE = "#4A2F1F", "#7A6557", "#E5D9CC"
TEAL, ORANGE, GREEN, RED, BROWN, PURPLE = "#2A9D8F", "#F4A261", "#6BBF59", "#E76F51", "#6F4E37", "#8E6BBF"


def mapping():
    L = [(BROWN, "สิ่งที่ถูกปรับ", "น้ำหนักของโมเดล θ", "ข้อความในสกิล s"),
         (BROWN, "สิ่งที่ไม่เปลี่ยน", "โครงสร้างของโมเดล", "โมเดลเป้าหมาย M และ Harness h (ถูกล็อก)"),
         (TEAL, "Forward Pass", "ป้อนข้อมูล ได้คำตอบของโมเดล", "Rollout: M ทำงานด้วยสกิล s ได้ Trajectory τ และคะแนน r"),
         (TEAL, "Loss", "ค่าความผิดพลาดของคำตอบ", "ความผิดพลาดของงาน (คะแนน r ต่ำ = ผิดมาก)"),
         (PURPLE, "Backward Pass", "คำนวณ Gradient ของ Loss", "Minibatch Reflection: Optimizer อ่าน Trajectory แล้วเสนอวิธีแก้สกิล"),
         (PURPLE, "ผู้ปรับ (Optimizer)", "SGD · Adam", "Optimizer Model O (โมเดลภาษาอีกตัว)"),
         (ORANGE, "การปรับ 1 ก้าว", "θ ← θ − η · Gradient", "แก้ข้อความ: add · delete · replace"),
         (ORANGE, "Learning Rate", "η = ขนาดของก้าว", "Edit Budget L<sub>t</sub> = จำนวนข้อที่แก้ได้ต่อก้าว"),
         (ORANGE, "LR Schedule", "ลด η ลงเมื่อเทรนไปนาน", "ลด L<sub>t</sub> จาก 4 เหลือ 2 (Cosine)"),
         (GREEN, "Minibatch", "ข้อมูลกลุ่มเล็กต่อ 1 ก้าว", "Rollout Batch B และ Reflection Minibatch B<sub>m</sub>"),
         (GREEN, "Validation", "วัดบนข้อมูลที่ไม่ได้ใช้เทรน", "Validation Gate บน D<sub>sel</sub>: รับเมื่อคะแนนสูงกว่าเดิมเท่านั้น"),
         (GREEN, "Checkpoint ที่ดีที่สุด", "เก็บน้ำหนักที่ Validation ดีที่สุด", "s<sub>best</sub> → ส่งออกเป็น best_skill.md"),
         (RED, "Momentum", "จำทิศทางของก้าวก่อน ๆ", "Slow / Meta Update ข้าม Epoch"),
         (RED, "Test Set", "ใช้รายงานผลครั้งสุดท้าย", "D<sub>test</sub>: ไม่ถูกแตะจนจบการเทรน")]
    rows = ""
    for col, name, dl, so in L:
        rows += """<div style='display:flex;align-items:center;gap:18px;background:#fff;border-radius:12px;padding:7px 16px;margin-bottom:6px;border-left:12px solid %s'>
          <div style='width:300px;font-size:25px;font-weight:800;color:%s'>%s</div>
          <div style='width:440px;font-size:23px'>%s</div>
          <div style='flex:1;font-size:23px'>%s</div></div>""" % (col, INK, name, dl, so)
    head = """<div style='display:flex;gap:18px;padding:0 16px 6px 28px;font-size:22px;color:%s;font-weight:700'>
      <div style='width:300px'>แนวคิด</div><div style='width:440px'>การเทรนโมเดล (Gradient Descent)</div><div style='flex:1'>SkillOpt (ปรับข้อความของสกิล)</div></div>""" % MUTE
    body = """<h1>เทียบการเทรนโมเดล กับ SkillOpt</h1>
    <div class='sub' style='margin-bottom:14px'>สีของแถบ: น้ำตาล = สิ่งที่ปรับ · เขียวอมฟ้า = Forward · ม่วง = Backward · ส้ม = ขนาดก้าว · เขียว = การตรวจ · แดง = ความจำระยะยาวและการรายงานผล</div>%s%s""" % (head, rows)
    shot("t01-mapping", body, 1010)


def algorithm():
    L = [("1–2", "รับเข้า", "โมเดลเป้าหมาย M · Optimizer O · Harness h · D<sub>train</sub> D<sub>sel</sub> D<sub>test</sub> · สกิลเริ่มต้น s<sub>0</sub> · จำนวน Epoch E · L<sub>t</sub>", "", ""),
         ("3–5", "เริ่มต้น", "s<sub>cur</sub> = s<sub>best</sub> = s<sub>0</sub> · วัด s<sub>0</sub> บน D<sub>sel</sub>", "ค่าเริ่มต้นของน้ำหนัก", BROWN),
         ("6–7", "ทำซ้ำ e = 1 … E", "สลับลำดับ D<sub>train</sub> · ล้าง Buffer ℬ", "Epoch", BROWN),
         ("9", "　Rollout", "M ทำงานในกลุ่มงานด้วย s<sub>cur</sub> ได้ Trajectory และคะแนน", "Forward Pass", TEAL),
         ("10", "　แยกกลุ่ม", "แยกงานที่ผิดกับงานที่ถูก แล้วแบ่งเป็น Minibatch ขนาด B<sub>m</sub>", "Minibatch", PURPLE),
         ("11–12", "　Reflection", "O อ่าน Minibatch ของงานที่ผิดและของงานที่ถูก แล้วเสนอ Edit", "Backward Pass", PURPLE),
         ("13", "　Merge", "รวมข้อเสนอ ตัดข้อที่ซ้ำหรือขัดกัน · ให้การแก้ข้อผิดมาก่อน", "รวม Gradient", PURPLE),
         ("14–15", "　Rank แล้ว Clip", "เรียงตามประโยชน์ เก็บไม่เกิน L<sub>t</sub> ข้อ → ได้สกิลรุ่นใหม่ s<sub>new</sub>", "Learning Rate", ORANGE),
         ("16–21", "　Validate", "วัด s<sub>new</sub> บน D<sub>sel</sub> (ถ้าเคยวัดสกิลนี้แล้ว ใช้คะแนนที่จำไว้)", "Validation", GREEN),
         ("22–26", "　ถ้าคะแนนสูงกว่าเดิม", "รับ: s<sub>cur</sub> = s<sub>new</sub> · ถ้าสูงกว่าที่ดีที่สุดด้วย s<sub>best</sub> = s<sub>new</sub>", "เก็บ Checkpoint", GREEN),
         ("27–29", "　ถ้าไม่", "ไม่รับ: จด Edit ที่ถูกปฏิเสธลง Buffer ℬ", "ไม่มีในการเทรนปกติ", RED),
         ("31–37", "　จบ Epoch (e ≥ 2)", "Slow Update: เทียบสกิลของ Epoch ก่อนกับปัจจุบัน · อัปเดต Meta Skill", "Momentum", RED),
         ("39–40", "ส่งออก", "วัด s<sub>best</sub> บน D<sub>test</sub> ครั้งเดียว · ส่งออก s<sub>best</sub>", "Test", INK)]
    rows = ""
    for no, name, txt, dl, col in L:
        rows += """<div style='display:flex;align-items:center;gap:16px;background:#fff;border-radius:12px;padding:7px 16px;margin-bottom:6px;border-left:12px solid %s'>
          <div style='%s;width:86px;font-size:21px;color:%s'>%s</div>
          <div style='width:300px;font-size:24px;font-weight:800;color:%s;white-space:pre'>%s</div>
          <div style='flex:1;font-size:22px'>%s</div>
          <div style='width:230px;font-size:21px;color:#2A6F68;text-align:right;font-weight:700'>%s</div></div>""" % (
            col or LINE, MONO, MUTE, no, INK, name, txt, dl)
    body = """<h1>Algorithm 1 ของ SkillOpt</h1>
    <div class='sub' style='margin-bottom:14px'>เลขทางซ้าย = บรรทัดใน Algorithm 1 ของเปเปอร์ · ทางขวา = สิ่งที่เทียบได้ในการเทรนโมเดล ·
      s<sub>cur</sub> = สกิลปัจจุบัน · s<sub>best</sub> = สกิลที่ดีที่สุด · s<sub>new</sub> = สกิลรุ่นใหม่ที่ยังไม่ถูกรับ</div>%s""" % rows
    shot("t02-algorithm", body, 960)


def compare():
    L = [("สิ่งที่ถูกปรับ", "ข้อความในสกิล 1 ไฟล์", "<span style='%s'>SKILL.md</span> ของ money-coder" % MONO, "เหมือนกัน"),
         ("โมเดลที่ทำงาน (ถูกล็อก)", "Target Model M", "Agent (โมเดล sonnet)", "เหมือนกัน"),
         ("ผู้เสนอวิธีแก้", "Optimizer Model O ทำเองอัตโนมัติ", "Claude Code ตามพรอมต์ของเรา", "บทนี้มีคนกำกับ"),
         ("Forward Pass", "Rollout Batch 40 งานต่อก้าว", "18 Trial ต่อรุ่น (6 งาน × 3 รอบ)", "บทนี้วัดทุกงานทุกก้าว"),
         ("Backward Pass", "Reflection ทั้งงานที่ผิดและงานที่ถูก", "ดูเฉพาะข้อที่ผิดของ Training Set", "บทนี้ง่ายกว่า"),
         ("Learning Rate", "L<sub>t</sub> = 4 ลดเหลือ 2", "แก้ไม่เกิน 3 จุดต่อรุ่น", "แนวคิดเดียวกัน"),
         ("Validation Gate", "คะแนนบน D<sub>sel</sub> ต้องสูงกว่าเดิม", "ต้องดีขึ้นเกินเกณฑ์ความแกว่ง หรือต้นทุนลด ≥ 10%", "บทนี้คิดความแกว่งและต้นทุน"),
         ("ความจำของผู้ปรับ", "Rejected Buffer · Meta Skill", "<span style='%s'>ISSUES.md</span>" % MONO, "แนวคิดเดียวกัน"),
         ("Slow Update", "มี (ท้าย Epoch ตั้งแต่ Epoch ที่ 2)", "ไม่มี", "บทนี้ไม่มี"),
         ("Test Split", "มี ใช้รายงานผลครั้งเดียว", "ไม่มี (แบบฝึกหัดข้อ 2)", "บทนี้ไม่มี")]
    tone = {"เหมือนกัน": GREEN, "แนวคิดเดียวกัน": GREEN, "บทนี้ไม่มี": RED}
    rows = ""
    for name, so, us, note in L:
        rows += """<div style='display:flex;align-items:center;gap:18px;background:#fff;border-radius:12px;padding:9px 16px;margin-bottom:7px;border-left:12px solid %s'>
          <div style='width:290px;font-size:25px;font-weight:800;color:%s'>%s</div>
          <div style='width:420px;font-size:23px'>%s</div>
          <div style='flex:1;font-size:23px'>%s</div>
          <div style='width:290px;font-size:21px;color:%s;text-align:right'>%s</div></div>""" % (
            tone.get(note, ORANGE), INK, name, so, us, MUTE, note)
    head = """<div style='display:flex;gap:18px;padding:0 16px 6px 28px;font-size:22px;color:%s;font-weight:700'>
      <div style='width:290px'>หัวข้อ</div><div style='width:420px'>SkillOpt (เปเปอร์)</div><div style='flex:1'>บทนี้ (skill-optimizer + money-coder)</div><div style='width:290px;text-align:right'>สรุป</div></div>""" % MUTE
    body = """<h1>SkillOpt ในเปเปอร์ เทียบกับ LAB ของบทนี้</h1>
    <div class='sub' style='margin-bottom:14px'>แถบเขียว = เหมือนกันหรือแนวคิดเดียวกัน · แถบส้ม = ต่างกันในรายละเอียด · แถบแดง = บทนี้ไม่มี</div>%s%s""" % (head, rows)
    shot("t03-vs-lab", body, 860)


def box(color, sym, name, ex, w="flex:1"):
    return """<div style='%s;background:#fff;border:3px solid %s;border-top:14px solid %s;border-radius:18px;padding:12px 16px;text-align:center'>
      <div style='font-size:46px;font-weight:800;color:%s;font-style:italic;font-family:Cambria,Georgia,serif'>%s</div>
      <div style='font-size:24px;font-weight:800;color:%s'>%s</div>
      <div style='font-size:21px;color:%s;margin-top:4px'>%s</div></div>""" % (w, LINE, color, color, sym, INK, name, MUTE, ex)


def big_arrow(txt="➜"):
    return "<div style='font-size:46px;color:%s;align-self:center;font-weight:800'>%s</div>" % (BROWN, txt)


def gd_step():
    """สูตรปรับน้ำหนัก 1 ก้าว พร้อมตัวเลขตัวอย่าง (ตัวเลขสมมติ)"""
    def term(color, top, mid, bot):
        return """<div style='text-align:center'><div style='font-size:21px;color:%s;font-weight:700;height:30px'>%s</div>
          <div style='font-size:64px;font-weight:800;color:%s;font-family:Cambria,Georgia,serif;line-height:1.1'>%s</div>
          <div style='font-size:22px;color:%s'>%s</div></div>""" % (color, top, color, mid, MUTE, bot)
    op = lambda t: "<div style='font-size:58px;color:%s;font-family:Cambria,Georgia,serif;align-self:center;padding:0 6px'>%s</div>" % (INK, t)
    sym = (term(GREEN, "น้ำหนักใหม่", "θ", "ค่าหลังปรับ") + op("←") + term(BROWN, "น้ำหนักเดิม", "θ", "ค่าก่อนปรับ") + op("−") +
           term(ORANGE, "Learning Rate", "η", "ขนาดของก้าว") + op("×") + term(PURPLE, "Gradient", "∇Loss", "ทิศที่ Loss เพิ่ม"))
    num = (term(GREEN, "", "4.8", "") + op("←") + term(BROWN, "", "5.0", "") + op("−") + term(ORANGE, "", "0.1", "") + op("×") + term(PURPLE, "", "2.0", ""))
    rows = "".join("""<div style='display:flex;align-items:center;gap:16px;background:#fff;border-radius:12px;padding:9px 18px;margin-bottom:7px;border-left:12px solid %s'>
        <div style='width:330px;font-size:25px;font-weight:800;color:%s'>%s</div><div style='flex:1;font-size:23px'>%s</div></div>""" % (c, INK, a, b) for c, a, b in [
        (PURPLE, "Gradient = +2.0", "เพิ่มน้ำหนัก 1 หน่วย Loss จะเพิ่ม 2 หน่วย → ต้อง <b>ลด</b> น้ำหนัก (เดินทางตรงข้าม)"),
        (ORANGE, "Learning Rate = 0.1", "เดินแค่ 0.1 ของ Gradient → ขยับ 0.1 × 2.0 = 0.2"),
        (GREEN, "น้ำหนักใหม่ = 4.8", "5.0 − 0.2 = 4.8 · แล้วทำซ้ำจาก Forward Pass อีกรอบ")])
    body = """<h1>สูตรปรับน้ำหนัก 1 ก้าว</h1>
    <div class='sub' style='margin-bottom:10px'>บรรทัดบน = สูตร · บรรทัดล่าง = ตัวเลขตัวอย่าง (สมมติว่าโมเดลมีน้ำหนักตัวเดียว)</div>
    <div style='display:flex;justify-content:center;gap:10px;background:#fff;border:3px solid %s;border-radius:22px;padding:14px 20px 10px'>%s</div>
    <div style='display:flex;justify-content:center;gap:34px;margin:6px 0 14px'>%s</div>%s""" % (LINE, sym, num, rows)
    shot("t04-gd-step", body, 650)


def eq_overview():
    """ภาพรวมของ 3 สมการ: ข้อมูล 3 ชุด ทำหน้าที่อะไร"""
    def stage(color, eq, title, lines):
        return """<div style='flex:1;background:#fff;border:3px solid %s;border-top:14px solid %s;border-radius:20px;padding:14px 18px'>
          <div style='%s;font-size:21px;color:%s'>%s</div>
          <div style='font-size:28px;font-weight:800;color:%s;margin:2px 0 8px'>%s</div>
          <div style='font-size:23px;line-height:1.45'>%s</div></div>""" % (LINE, color, MONO, MUTE, eq, INK, title, lines)
    cards = big_arrow().join([
        stage(TEAL, "สมการ 1", "ทำงาน 1 ครั้ง", "โมเดล + งาน + สกิล<br>→ <b>Trajectory</b> และ <b>คะแนน</b><br><span style='color:%s'>หน่วยที่เล็กที่สุดของทุกอย่าง</span>" % MUTE),
        stage(GREEN, "ระหว่างเทรน", "สร้างสกิลหลายรุ่น", "ใช้งานจาก <b>D<sub>tr</sub></b><br>→ สกิล s<sub>0</sub>, s<sub>1</sub>, s<sub>2</sub>, …<br><span style='color:%s'>ชุดนี้เรียกว่า 𝒞(D<sub>tr</sub>)</span>" % MUTE),
        stage(ORANGE, "สมการ 2", "เลือกรุ่นที่ดีที่สุด", "วัดทุกรุ่นบน <b>D<sub>sel</sub></b><br>→ เลือกรุ่นที่คะแนนเฉลี่ยสูงสุด<br><span style='color:%s'>ได้ s<sup>★</sup><sub>sel</sub></span>" % MUTE),
        stage(RED, "สมการ 3", "รายงานผล", "วัดรุ่นที่เลือกบน <b>D<sub>test</sub></b><br>→ ตัวเลขที่เขียนลงเปเปอร์<br><span style='color:%s'>ทำครั้งเดียวตอนจบ</span>" % MUTE)])
    data = "".join("""<div style='flex:1;border-radius:16px;padding:10px 16px;background:%s;color:#fff'>
        <div style='font-size:27px;font-weight:800'>%s</div><div style='font-size:22px'>%s</div></div>""" % (c, a, b) for c, a, b in [
        (GREEN, "D<sub>tr</sub> · Train", "ให้โมเดลลองทำ เพื่อหาว่าควรแก้สกิลอย่างไร"),
        (ORANGE, "D<sub>sel</sub> · Selection", "ตัดสินว่ารุ่นไหนดีกว่า (ไม่ใช้หาวิธีแก้)"),
        (RED, "D<sub>test</sub> · Test", "ล็อกไว้ ใช้รายงานผลครั้งเดียว")])
    body = """<h1>ภาพรวมของสมการทั้ง 3</h1>
    <div class='sub' style='margin-bottom:14px'>สมการ 1 นิยามการทำงาน 1 ครั้ง · สมการ 2 บอกวิธีเลือกสกิล · สมการ 3 บอกวิธีรายงานผล · แต่ละขั้นใช้ข้อมูลคนละชุด</div>
    <div style='display:flex;gap:8px;align-items:stretch'>%s</div>
    <div style='font-size:24px;font-weight:800;color:%s;margin:20px 0 8px'>ข้อมูล 3 ชุด ไม่ซ้ำกัน</div>
    <div style='display:flex;gap:14px'>%s</div>""" % (cards, INK, data)
    shot("t05-eq-overview", body, 590)


def eq1():
    ins = "".join([box(BROWN, "M", "โมเดลเป้าหมาย", "ถูกล็อก ไม่ถูกแก้<br><span style='%s;color:#2A6F68'>sonnet</span>" % MONO),
                   box(GREEN, "x", "งาน 1 ชิ้น", "โจทย์ 1 ข้อ<br><span style='%s;color:#2A6F68'>cashback</span>" % MONO),
                   box(ORANGE, "s", "สกิล", "ข้อความที่ถูกปรับ<br><span style='%s;color:#2A6F68'>v0/SKILL.md</span>" % MONO)])
    mid = box(TEAL, "h", "Harness", "ระบบที่ให้โมเดลทำงาน<br><span style='%s;color:#2A6F68'>claude -p</span>" % MONO, "width:300px")
    outs = "".join([box(PURPLE, "τ", "Trajectory", "บันทึกทุกขั้นที่โมเดลทำ<br><span style='%s;color:#2A6F68'>Trace ของ Trial</span>" % MONO),
                    box(RED, "r", "คะแนน", "ตัวเลข 0 ถึง 1<br><span style='%s;color:#2A6F68'>7 จาก 10 ข้อ = 0.7</span>" % MONO)])
    body = """<h1>สมการ 1: การทำงาน 1 ครั้ง</h1>
    <div class='sub' style='margin-bottom:12px'>อ่านจากซ้ายไปขวา: ของ 3 อย่างเข้า Harness แล้วได้ของ 2 อย่างออกมา · ตัวอักษรสีเขียวเข้ม = สิ่งนั้นใน LAB ของบทนี้</div>
    <div style='text-align:center;font-size:54px;font-family:Cambria,Georgia,serif;color:%s;background:#fff;border:3px solid %s;border-radius:20px;padding:8px;margin-bottom:18px'>
      ( <span style='color:%s'><i>τ</i></span> , <span style='color:%s'><i>r</i></span> ) &nbsp;=&nbsp; <span style='color:%s'><i>h</i></span> ( <span style='color:%s'><i>M</i></span> , <span style='color:%s'><i>x</i></span> , <span style='color:%s'><i>s</i></span> )</div>
    <div style='display:flex;gap:12px;align-items:stretch'>
      <div style='flex:3;display:flex;gap:10px'>%s</div>%s%s%s<div style='flex:2;display:flex;gap:10px'>%s</div></div>
    <div class='note' style='margin-top:18px'>ถ้าเปลี่ยนแค่ <b>s</b> แล้วคะแนน <b>r</b> เปลี่ยน แปลว่าผลนั้นมาจากสกิล เพราะ M, x และ h เหมือนเดิมทุกอย่าง</div>""" % (
        INK, LINE, PURPLE, RED, TEAL, BROWN, GREEN, ORANGE, ins, big_arrow(), mid, big_arrow(), outs)
    shot("t06-eq1", body, 600)


# สมการ 2 และ 3 และตารางที่เชื่อมทั้ง 3 สมการ วาดใน diagrams_eq.py (ใช้ MathML)


def edits():
    """ตัวอย่าง Edit 3 แบบ ด้วยข้อความของสกิล money-coder"""
    def row(color, op, th, before, after, src):
        cell = lambda t, bg: "<div style='flex:1;background:%s;border-radius:12px;padding:10px 14px;font-size:21px;line-height:1.4'>%s</div>" % (bg, t)
        return """<div style='display:flex;gap:12px;align-items:stretch;background:#fff;border-radius:16px;padding:10px 14px;margin-bottom:10px;border-left:14px solid %s'>
          <div style='width:190px'><div style='%s;font-size:30px;font-weight:800;color:%s'>%s</div><div style='font-size:24px;font-weight:800;color:%s'>%s</div>
            <div style='font-size:19px;color:%s;margin-top:4px'>%s</div></div>%s%s</div>""" % (
            color, MONO, color, op, INK, th, MUTE, src, cell(before, "#FBF1EC"), cell(after, "#EAF6E6"))
    rows = (row(GREEN, "add", "เพิ่มกฎ", "<span style='color:%s'>(ไม่มีกฎเรื่องวิธีทำงาน)</span>" % MUTE,
                "<b>+</b> เขียนไฟล์โค้ด ไฟล์เทสต์ และรันเทสต์ ในการเรียกเครื่องมือ Bash ครั้งเดียว แล้วตอบทันที", "จริง · v2 → v3") +
            row(ORANGE, "replace", "แทนกฎเดิม", "ต้องเรียกใช้จาก command line ได้ รับ JSON และตอบเป็น JSON",
                "สำเร็จตอบ {\"ok\": true, \"result\": …} exit 0 · ข้อมูลผิดตอบ {\"ok\": false, \"error\": \"…\"} exit 2", "จริง · v0 → v1") +
            row(RED, "delete", "ลบกฎ", "<s>ใส่คำอธิบายยาว ๆ ไว้ท้ายคำตอบทุกครั้ง</s>",
                "<span style='color:%s'>(กฎถูกลบ เพราะทำให้งานช้าและไม่ช่วยให้ถูกขึ้น)</span>" % MUTE, "ตัวอย่างสมมติ"))
    head = """<div style='display:flex;gap:12px;padding:0 14px 6px 28px;font-size:21px;color:%s;font-weight:700'>
      <div style='width:190px'>ชนิดของ Edit</div><div style='flex:1'>สกิลก่อนแก้</div><div style='flex:1'>สกิลหลังแก้</div></div>""" % MUTE
    body = """<h1>Edit 3 แบบ: add · replace · delete</h1>
    <div class='sub' style='margin-bottom:12px'>1 Edit = แก้กฎ 1 ข้อในสกิล · ตัวอย่าง add และ replace มาจากสกิล money-coder ของ LAB · delete เป็นตัวอย่างสมมติ (LAB ไม่มีรุ่นที่ลบกฎ)</div>%s%s""" % (head, rows)
    shot("t08-edits", body, 610)


def gate_timeline():
    """ตัวอย่างการตัดสินของ Gate 6 ก้าว (ตัวเลขสมมติ)"""
    S = [("เริ่ม", 70, None), ("ก้าว 1", 75, True), ("ก้าว 2", 75, False), ("ก้าว 3", 72, False), ("ก้าว 4", 80, True), ("ก้าว 5", 78, False), ("ก้าว 6", 84, True)]
    cur, bars = 70, ""
    for name, sc, ok in S:
        col = BROWN if ok is None else (GREEN if ok else RED)
        why = "สกิลเริ่มต้น" if ok is None else ("%d &gt; %d" % (sc, cur) if ok else ("%d = %d เท่ากัน" % (sc, cur) if sc == cur else "%d &lt; %d" % (sc, cur)))
        verdict = "" if ok is None else ("ACCEPT" if ok else "REJECT")
        h = int((sc - 60) * 9)
        bars += """<div style='flex:1;display:flex;flex-direction:column;align-items:center;justify-content:flex-end'>
          <div style='font-size:26px;font-weight:800;color:%s'>%d</div>
          <div style='width:110px;height:%dpx;background:%s;border-radius:12px 12px 0 0;opacity:%s'></div>
          <div style='font-size:23px;font-weight:800;color:%s;margin-top:6px'>%s</div>
          <div style='font-size:20px;color:%s;height:28px'>%s</div>
          <div style='font-size:22px;font-weight:800;color:%s;height:30px'>%s</div>
          <div style='font-size:20px;color:%s'>ปัจจุบัน = %d</div></div>""" % (
            col, sc, h, col, "1" if ok is not False else "0.55", INK, name, MUTE, why, col, verdict, MUTE, sc if ok is not False else cur)
        if ok:
            cur = sc
    body = """<h1>Validation Gate ตัดสินอย่างไร (ตัวอย่างสมมติ 6 ก้าว)</h1>
    <div class='sub' style='margin-bottom:6px'>แท่ง = คะแนนบน D<sub>sel</sub> ของสกิลรุ่นใหม่ในก้าวนั้น · เทียบกับคะแนนของ <b>สกิลปัจจุบัน</b> · ต้องสูงกว่าจึงรับ เท่ากันก็ไม่รับ</div>
    <div style='display:flex;gap:6px;align-items:flex-end;height:430px;background:#fff;border:3px solid %s;border-radius:20px;padding:14px 18px'>%s</div>
    <div class='note' style='margin-top:12px'>สกิลปัจจุบันขยับเฉพาะก้าวที่ถูกรับ: 70 → 75 → 80 → 84 · ก้าว 2 3 5 ถูกปฏิเสธ และ Edit ของก้าวนั้นถูกจดลง Buffer</div>""" % (LINE, bars)
    shot("t09-gate-timeline", body, 680)


def reflection_example():
    """Backward Pass เดินตามด้วยผลจริงของ LAB (v0 -> v1) จัดให้อยู่ในรูปของ SkillOpt"""
    def col(color, no, title, sub, inner, w="flex:1"):
        return """<div style='%s;background:#fff;border:3px solid %s;border-top:14px solid %s;border-radius:18px;padding:10px 12px'>
          <div style='font-size:24px;font-weight:800;color:%s'><span style='color:%s'>%s</span> %s</div>
          <div style='font-size:19px;color:%s;margin-bottom:8px;height:50px'>%s</div>%s</div>""" % (w, LINE, color, INK, color, no, title, MUTE, sub, inner)
    chip = lambda t, bg, fg="#3B2A20", extra="": "<div style='background:%s;color:%s;border-radius:10px;padding:6px 10px;font-size:20px;margin-bottom:6px;line-height:1.3;%s'>%s</div>" % (bg, fg, extra, t)
    c1 = (chip("<b>12 Trajectory</b><br>4 งาน × 3 รอบ ด้วยสกิล v0", "#F3EDE4") +
          chip("งานที่ผิด (คะแนน &lt; 1.0)<br><b>12 ใบ</b>", "#FBE3DC") + chip("งานที่ถูก (คะแนน = 1.0)<br><b>0 ใบ</b>", "#E3F3DE"))
    c2 = (chip("กลุ่มที่ 1 · 8 ใบ", "#EFE6FA") + chip("กลุ่มที่ 2 · 4 ใบ", "#EFE6FA") +
          chip("อ่านทีละกลุ่ม หาข้อผิดที่<br><b>เกิดซ้ำในกลุ่ม</b>", "#F3EDE4"))
    P = [("A", "CLI ตอบ JSON คนละรูปแบบ", "12/12", ORANGE), ("B", "เทสต์ไม่ครบ 6 หรือรันไม่ได้", "5/12", ORANGE),
         ("C", "ข้อมูลผิดชนิด ไม่ได้ ValueError", "4/12", ORANGE), ("D", "ผลไม่ตรงนโยบายของร้าน", "6/12", MUTE)]
    c3 = "".join(chip("<b style='color:%s'>%s</b> %s<br><span style='%s;color:%s'>พบ %s Trial</span>" % (c, k, t, MONO, MUTE, n), "#FFF6EA") for k, t, n, c in P)
    c4 = (chip("<b>1</b> &nbsp;A &nbsp;<span style='color:%s'>12/12</span>" % MUTE, "#E3F3DE") + chip("<b>2</b> &nbsp;B &nbsp;<span style='color:%s'>5/12</span>" % MUTE, "#E3F3DE") +
          chip("<b>3</b> &nbsp;C &nbsp;<span style='color:%s'>4/12</span>" % MUTE, "#E3F3DE") +
          "<div style='border-top:3px dashed %s;margin:8px 0 8px;font-size:18px;color:%s;text-align:center'>ไม่มีข้อเสนอที่ใช้กับงานอื่นได้</div>" % (RED, RED) +
          chip("D &nbsp;6/12 &nbsp;ต้องถามทีม", "#FBE3DC", MUTE))
    c5 = (chip("<b>replace</b> กฎข้อ 4<br>กำหนดรูปแบบ JSON และ exit code", "#E3F3DE") + chip("<b>replace</b> กฎข้อ 5<br>unittest อย่างน้อย 6 เทสต์", "#E3F3DE") +
          chip("<b>replace</b> กฎข้อ 3<br>ValueError เท่านั้น", "#E3F3DE"))
    a = "<div style='font-size:34px;color:%s;align-self:center;font-weight:800'>➜</div>" % BROWN
    body = """<h1>Backward Pass เดินตามด้วยผลจริงของ LAB (v0 → v1)</h1>
    <div class='sub' style='margin-bottom:12px'>จำนวน Trial ที่พบข้อผิดเป็นผลจริงของ LAB · LAB ไม่ได้แบ่ง Minibatch จริง ภาพนี้จัดผลให้อยู่ในรูปของ SkillOpt โดยใช้ B<sub>m</sub> = 8 และ L = 3</div>
    <div style='display:flex;gap:6px;align-items:stretch'>%s%s%s%s%s%s%s%s%s</div>
    <div class='note' style='margin-top:14px'>ผลหลังผ่าน Gate: Training 68.6%% → 95.2%% · Validation 66.7%% → 90.0%% · ข้อ D ถูกแก้ใน v2 เมื่อคนในทีมให้นโยบายธุรกิจ</div>""" % (
        col(TEAL, "1", "หลักฐาน", "Rollout Batch จาก Forward Pass", c1, "width:250px"), a,
        col(PURPLE, "2", "แบ่งกลุ่ม", "Minibatch ละไม่เกิน 8 ใบ", c2, "width:250px"), a,
        col(ORANGE, "3", "ข้อเสนอ", "รวมจากทุกกลุ่ม ตัดข้อที่ซ้ำแล้ว", c3), a,
        col(GREEN, "4", "Rank แล้ว Clip", "เรียงตามจำนวนที่พบ เก็บ L = 3", c4, "width:230px"), a,
        col(BROWN, "5", "สกิลรุ่นใหม่ v1", "ใช้ Edit ที่เหลือ 3 ข้อ", c5))
    shot("t10-reflection-example", body, 720)


def three_way():
    L = [("ใช้อะไรเป็นหลักฐาน", "Loss ของข้อมูลใน Minibatch", "Trajectory ของงานใน Minibatch แยกงานที่ผิดกับงานที่ถูก",
          "ข้อที่ผิดของ Training 12 Trial และ Trace", PURPLE),
         ("หาทิศของตัวอย่างแต่ละตัว", "Gradient ของตัวอย่างแต่ละตัว", "Reflection: Optimizer Model อ่านทีละกลุ่ม แล้วเสนอ Edit",
          "Claude Code อ่านข้อที่ผิด แล้วหาสาเหตุ", PURPLE),
         ("รวมทิศในกลุ่ม", "เฉลี่ย Gradient ทั้ง Minibatch สัญญาณรบกวนหักล้างกัน", "Merge: เก็บข้อที่เกิดซ้ำ ตัดข้อที่ซ้ำ ขัดกัน หรือเฉพาะตัวอย่าง",
          "เก็บสาเหตุที่พบมากกว่า 1 Trial", PURPLE),
         ("จำกัดขนาดของก้าว", "คูณด้วย Learning Rate η", "Rank แล้ว Clip เหลือไม่เกิน L<sub>t</sub> ข้อ", "แก้ไม่เกิน 3 จุดต่อรุ่น", ORANGE),
         ("ผลของก้าว", "น้ำหนักชุดใหม่ θ", "สกิลรุ่นใหม่ s<sub>new</sub>", "โฟลเดอร์รุ่นใหม่ เช่น v1", GREEN),
         ("ใครเป็นคนทำ", "สูตรคณิตศาสตร์ (Backpropagation)", "Optimizer Model O", "Claude Code ตามพรอมต์ของเรา", BROWN)]
    rows = ""
    for name, gd, so, lab, col in L:
        rows += """<div style='display:flex;align-items:center;gap:16px;background:#fff;border-radius:12px;padding:10px 16px;margin-bottom:7px;border-left:12px solid %s'>
          <div style='width:270px;font-size:24px;font-weight:800;color:%s'>%s</div>
          <div style='width:360px;font-size:22px'>%s</div><div style='flex:1;font-size:22px'>%s</div><div style='width:360px;font-size:22px'>%s</div></div>""" % (
            col, INK, name, gd, so, lab)
    head = """<div style='display:flex;gap:16px;padding:0 16px 6px 28px;font-size:22px;color:%s;font-weight:700'>
      <div style='width:270px'>ขั้นของ Backward Pass</div><div style='width:360px'>Gradient Descent</div><div style='flex:1'>SkillOpt (เปเปอร์)</div><div style='width:360px'>LAB ของเรา (money-coder)</div></div>""" % MUTE
    body = """<h1>Backward Pass เทียบ 3 ทาง</h1>
    <div class='sub' style='margin-bottom:14px'>ทั้งสามทำสิ่งเดียวกัน: จากหลักฐานของกลุ่มเล็ก หาทิศที่ควรปรับ รวมให้เหลือทิศที่เชื่อได้ แล้วปรับเพียงเล็กน้อย</div>%s%s""" % (head, rows)
    shot("t11-backward-three-way", body, 660)


def skill_anatomy():
    """ไฟล์สกิล 1 ไฟล์มี 2 ส่วน: ใครแก้ส่วนไหนได้ เมื่อไร"""
    bar = lambda w, c="#D9CFC3": "<div style='height:14px;width:%d%%;background:%s;border-radius:7px;margin:9px 0'></div>" % (w, c)
    doc = """<div style='width:520px;background:#fff;border:4px solid %s;border-radius:20px;padding:16px 20px'>
      <div style='%s;font-size:24px;color:#2A6F68;font-weight:700;margin-bottom:8px'>best_skill.md</div>
      <div style='border:3px solid %s;border-radius:14px;padding:10px 14px;margin-bottom:12px'>
        <div style='font-size:23px;font-weight:800;color:%s'>ส่วนกฎทั่วไป</div>%s%s%s%s%s</div>
      <div style='border:3px dashed %s;border-radius:14px;padding:10px 14px;background:#FDF1EE'>
        <div style='%s;font-size:18px;color:%s'>SLOW_UPDATE_START</div>
        <div style='font-size:23px;font-weight:800;color:%s'>🔒 ส่วนที่ถูกป้องกัน</div>%s%s
        <div style='%s;font-size:18px;color:%s'>SLOW_UPDATE_END</div></div></div>""" % (
        LINE, MONO, ORANGE, ORANGE, bar(92), bar(80, "#F4A261"), bar(88), bar(70, "#F4A261"), bar(84),
        RED, MONO, MUTE, RED, bar(86, "#E9A99A"), bar(64, "#E9A99A"), MONO, MUTE)
    def who(color, title, rows):
        r = "".join("<div style='display:flex;gap:10px;font-size:22px;margin-top:5px'><div style='width:170px;color:%s'>%s</div><div style='flex:1'>%s</div></div>" % (MUTE, a, b) for a, b in rows)
        return "<div style='background:#fff;border-radius:16px;padding:12px 18px;margin-bottom:12px;border-left:14px solid %s'><div style='font-size:26px;font-weight:800;color:%s'>%s</div>%s</div>" % (color, INK, title, r)
    right = (who(ORANGE, "ส่วนกฎทั่วไป ← ก้าวปกติ (Fast Update)", [("แก้เมื่อไร", "ทุกก้าว"), ("แก้ได้เท่าไร", "ไม่เกิน L<sub>t</sub> ข้อต่อก้าว"), ("เรียนจากอะไร", "Rollout Batch ของก้าวนั้น"), ("ผ่าน Gate", "ต้องผ่าน")]) +
             who(RED, "ส่วนที่ถูกป้องกัน ← Slow Update", [("แก้เมื่อไร", "ท้าย Epoch (ตั้งแต่ Epoch ที่ 2)"), ("ก้าวปกติแก้ได้ไหม", "<b>ไม่ได้</b>"), ("เรียนจากอะไร", "การเทียบสกิลของ Epoch ก่อนกับปัจจุบัน"), ("ผ่าน Gate", "ต้องผ่าน")]) +
             who(PURPLE, "Meta Skill ← ไม่อยู่ในไฟล์นี้", [("อยู่ที่ไหน", "หน้าพรอมต์ของ Optimizer Model"), ("ส่งออกไหม", "<b>ไม่ส่งออก</b>")]))
    body = """<h1>ไฟล์สกิล 1 ไฟล์ มี 2 ส่วน</h1>
    <div class='sub' style='margin-bottom:14px'>แถบสีส้ม = บรรทัดที่ก้าวปกติเพิ่งแก้ · กรอบเส้นประ = ส่วนที่ก้าวปกติแตะไม่ได้ มีเครื่องหมายกำกับหัวท้าย</div>
    <div style='display:flex;gap:26px;align-items:flex-start'>%s<div style='flex:1'>%s</div></div>""" % (doc, right)
    shot("t12-skill-anatomy", body, 745)


def timeline():
    """โครง 2 วงซ้อนของ Algorithm 1 ตลอด 4 Epoch (จำนวนก้าวต่อ Epoch ในภาพเป็นตัวอย่าง)"""
    def step(t): return "<div style='background:#EAF6E6;border:2px solid %s;border-radius:10px;padding:6px 0;text-align:center;font-size:20px;margin-bottom:5px'>%s</div>" % (GREEN, t)
    def end(t, c, bg): return "<div style='background:%s;border:2px solid %s;border-radius:10px;padding:6px 0;text-align:center;font-size:20px;font-weight:700;margin-bottom:5px;color:%s'>%s</div>" % (bg, c, INK, t)
    none = "<div style='border:2px dashed %s;border-radius:10px;padding:6px 0;text-align:center;font-size:19px;color:%s;margin-bottom:5px'>ยังไม่มี</div>" % (LINE, MUTE)
    cols = ""
    for e in range(1, 5):
        tail = (none + none) if e == 1 else (end("Slow Update", RED, "#FDF1EE") + end("Meta Skill", PURPLE, "#F1EAFA"))
        cols += """<div style='flex:1;background:#fff;border:3px solid %s;border-top:14px solid %s;border-radius:18px;padding:10px 12px'>
          <div style='font-size:26px;font-weight:800;color:%s;margin-bottom:2px'>Epoch %d</div>
          <div style='font-size:19px;color:%s;margin-bottom:8px'>สลับลำดับงาน · ล้าง Buffer</div>
          %s%s%s<div style='text-align:center;font-size:20px;color:%s;margin:-2px 0 4px'>⋮</div>
          <div style='font-size:19px;color:%s;margin:6px 0 4px'>ท้าย Epoch</div>%s</div>""" % (
            LINE, BROWN, INK, e, MUTE, step("ก้าว: Forward → Backward → Gate"), step("ก้าว: Forward → Backward → Gate"), step("ก้าว: Forward → Backward → Gate"), MUTE, MUTE, tail)
    lr = """<div style='display:flex;align-items:center;gap:14px;margin:12px 0 10px'>
      <div style='width:300px;font-size:23px;font-weight:800;color:%s'>Learning Rate L<sub>t</sub></div>
      <div style='font-size:24px;font-weight:800;color:%s'>4</div>
      <div style='flex:1;height:22px;border-radius:11px;background:linear-gradient(90deg,#F4A261,#FBE3CC)'></div>
      <div style='font-size:24px;font-weight:800;color:%s'>2</div>
      <div style='width:330px;font-size:21px;color:%s'>ลดลงแบบ Cosine ตลอดการเทรน</div></div>""" % (INK, ORANGE, ORANGE, MUTE)
    foot = """<div style='display:flex;gap:12px'>
      <div style='flex:1;background:#fff;border-radius:14px;padding:10px 16px;border-left:12px solid %s;font-size:22px'><b>ก่อนเริ่ม</b> · วัดสกิลเริ่มต้น s<sub>0</sub> บน D<sub>sel</sub></div>
      <div style='flex:1;background:#fff;border-radius:14px;padding:10px 16px;border-left:12px solid %s;font-size:22px'><b>หลังจบ</b> · วัด s<sub>best</sub> บน D<sub>test</sub> ครั้งเดียว แล้วส่งออก</div></div>""" % (BROWN, RED)
    body = """<h1>โครงของ Algorithm 1: วงซ้อน 2 ชั้น</h1>
    <div class='sub' style='margin-bottom:10px'>วงนอก = Epoch (ค่าตั้งต้น 4 รอบ) · วงใน = ก้าว (ข้อ 6.1–6.3) · จำนวนก้าวต่อ Epoch ขึ้นกับจำนวนงานฝึก ในภาพแสดง 3 ก้าวเป็นตัวอย่าง</div>
    <div style='display:flex;gap:10px'>%s</div>%s%s""" % (cols, lr, foot)
    shot("t13-timeline", body, 705)


if __name__ == "__main__":
    for w in sys.argv[1:] or ["mapping", "algorithm", "compare", "gd_step", "eq_overview", "eq1", "edits", "gate_timeline",
                              "reflection_example", "three_way", "skill_anatomy", "timeline"]:
        globals()[w]()
