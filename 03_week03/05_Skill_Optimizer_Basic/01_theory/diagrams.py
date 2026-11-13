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


if __name__ == "__main__":
    for w in sys.argv[1:] or ["mapping", "algorithm", "compare"]:
        globals()[w]()
