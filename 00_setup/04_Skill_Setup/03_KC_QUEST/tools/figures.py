#!/usr/bin/env python3
"""figures.py — วาด "การ์ดสมการ" ของบทเรียน KC-QUEST (สมการจริง + ไอเดีย + แทนค่าตัวอย่าง) → image/eq-*.png

ใช้ HTML + KaTeX แล้วถ่ายภาพด้วย Chromium (Playwright ของ Python) · รัน: python tools/figures.py [ชื่อการ์ด ...]
ตัวเลขตัวอย่างทั้งหมดมาจาก `python tools/kcquest.py explain --round 4` (สถานการณ์ examples/quota_lesson.json)
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(os.path.dirname(HERE), "image")
KATEX = "https://cdn.jsdelivr.net/npm/katex@0.16.11/dist"

# สีประจำพจน์ (ใช้ซ้ำทั้งบทเรียน)
C = {"o": "#e67e22", "g": "#2e9e5b", "b": "#2b7bd6", "p": "#8e44ad", "r": "#c0392b", "k": "#111", "t": "#16a3a3", "y": "#b7950b"}

CSS = """
*{box-sizing:border-box} body{margin:0;background:#fff;font-family:'Leelawadee UI','Sarabun',Tahoma,sans-serif;color:#222}
#card{width:1600px;padding:0 0 34px;background:#fff}
.hd{background:#2b7bd6;color:#fff;padding:22px 44px;font-size:38px;font-weight:700}
.hd small{font-size:24px;font-weight:400;opacity:.9;margin-left:14px}
.idea{margin:24px 44px 0;padding:16px 24px;background:#fff7e6;border-left:8px solid #e67e22;border-radius:10px;font-size:26px}
.eq{margin:26px 44px 6px;padding:22px;border:2px solid #e3e8ef;border-radius:16px;text-align:center;font-size:40px;background:#fbfcfe}
.eq.sm{font-size:32px}
.row{display:flex;gap:22px;margin:18px 44px 0}
.col{flex:1}
.lg{display:grid;grid-template-columns:auto 1fr;gap:10px 18px;margin:20px 44px 0;font-size:25px;align-items:center}
.tag{font-weight:700;padding:4px 14px;border-radius:10px;color:#fff;text-align:center;white-space:nowrap}
.ex{margin:22px 44px 0;padding:16px 24px;background:#eef6ff;border-radius:12px;font-size:25px;line-height:1.6}
.ex b{color:#c0392b}
.note{margin:16px 44px 0;font-size:22px;color:#666}
table{border-collapse:collapse;font-size:24px;margin:18px 44px 0;width:calc(100% - 88px)}
td,th{border:1px solid #dde3ea;padding:8px 12px;text-align:center} th{background:#f2f5f9}
.katex{font-size:1.0em}
"""

def tag(color, text): return f'<span class="tag" style="background:{C[color]}">{text}</span>'
def tc(color, tex): return f"\\textcolor{{{C[color]}}}{{{tex}}}"

CARDS = {}

# ---------------------------------------------------------------- 0) แบบจำลองคณิตศาสตร์
CARDS["eq-model"] = ("แบบจำลองคณิตศาสตร์ของปัญหาแจกงาน", "เขียนเป็น optimization เต็มรูป", f"""
<div class="idea">💡 ไอเดีย: เลือก <b>ใครทำงานไหน</b> และ <b>เริ่มเมื่อไร</b> ให้โปรเจกต์จบเร็วที่สุด โดยไม่ผิดกฎ 4 ข้อ</div>
<div class="eq sm">$$\\begin{{aligned}}
&\\min_{{\\,{tc('b','x')},\\;{tc('b','s')}}}\\;\\; {tc('g','C_{\\max}')} = \\max_j\\,(s_j + p_j)\\\\[4pt]
\\text{{s.t.}}\\;\\; &{tc('k','\\textstyle\\sum_a x_{ja} = 1')} && \\forall j \\quad &&(1)\\ \\text{{งานละ 1 บัญชี}}\\\\
&{tc('o','s_k \\ge s_j + p_j')} && \\forall (j\\!\\to\\!k)\\in E &&(2)\\ \\text{{รองานก่อนหน้า}}\\\\
&{tc('r','\\textstyle\\sum_j x_{ja}\\,\\sigma r^{5}_a c_j \\le H^{5}_a - m - Q_a')} && \\forall a &&(3)\\ \\text{{โควตา 5 ชม.}}\\\\
&{tc('r','\\textstyle\\sum_j x_{ja}\\,\\sigma r^{w}_a c_j \\le H^{w}_a - m - Q_a')} && \\forall a &&(4)\\ \\text{{โควตาสัปดาห์}}\\\\
&{tc('p','\\#\\{{j: x_{ja}=1,\\ s_j\\le t< s_j+p_j\\}} \\le K_a')} && \\forall a,t &&(5)\\ \\text{{รับพร้อมกันได้ K งาน}}\\\\
&{tc('b','x_{ja}\\in\\{{0,1\\}},\\ s_j\\ge 0')},\\quad p_j = c_j / v_a &&&&
\\end{{aligned}}$$</div>
<div class="lg">
{tag('b','ตัวแปร')}<div>$x_{{ja}}=1$ ถ้างาน $j$ ให้บัญชี $a$ ทำ · $s_j$ = เวลาเริ่มงาน $j$ · $p_j$ = เวลาทำ = ขนาด $c_j$ ÷ ความเร็ว $v_a$</div>
{tag('g','เป้าหมาย')}<div>$C_{{\\max}}$ (makespan) = เวลาที่งานสุดท้ายเสร็จ · เป้าหมายรอง: ใช้โควตาที่ <b>ใกล้หมดอายุ</b> ก่อน (ไม่ทิ้งของฟรี)</div>
{tag('r','ข้อจำกัด')}<div>(1) ทุกงานมีคนทำ · (2) ลูกศรใน DAG · (3)(4) โควตา 2 ถังต้องพอ (เผื่อ σ, m, Q) · (5) ช่องรับงาน (slot)</div>
</div>
<div class="ex">📏 ขนาดปัญหา catfood: 14 งาน × 4 บัญชี → แค่ "ใครทำ" ก็มี $4^{{14}}$ ≈ <b>268 ล้าน</b> แบบ ยังไม่นับลำดับเวลา · ปัญหานี้ครอบปัญหา <b>P|prec|C<sub>max</sub></b> และ <b>bin packing</b> ซึ่งเป็น <b>NP-hard</b> → ใช้ heuristic ที่ตัดสินใจทีละงานแทน</div>
""")

# ---------------------------------------------------------------- 1) rank + ลำดับ
CARDS["eq-rank"] = ("① จัดลำดับ: งานไหนได้เลือกก่อน", "critical path + MRV", f"""
<div class="idea">💡 ไอเดีย: งานที่อยู่บน <b>เส้นทางยาวที่สุด</b> ถ้าช้า ทั้งโปรเจกต์ช้าตาม → ให้ได้เลือกบัญชีก่อน · งานที่ <b>มีทางเลือกน้อย</b> ให้เลือกก่อน ไม่งั้นโดนแย่งที่</div>
<div class="eq">$$\\mathrm{{rank}}(j) = {tc('g','c_j')} + \\max_{{k\\in {tc('b','\\mathrm{succ}(j)')}}} {tc('b','\\mathrm{rank}(k)')} \\qquad {tc('o','\\kappa_j')} = \\frac{{\\mathrm{{rank}}(j)}}{{\\max_i \\mathrm{{rank}}(i)}}$$</div>
<div class="eq sm">$$\\text{{เรียงงานตาม}}\\quad \\big(\\ {tc('p','\\min(|A_j|,3)')}\\ \\uparrow,\\;\\; {tc('o','\\kappa_j')}\\ \\downarrow,\\;\\; {tc('g','c_j')}\\ \\downarrow\\ \\big)$$</div>
<div class="lg">
{tag('g','c<sub>j</sub>')}<div>ขนาดของงานเอง (S 0.6 · M 1.5 · L 3 ล้านโทเคน)</div>
{tag('b','succ(j)')}<div>งานที่รอ $j$ (ลูกศรที่ออกจาก $j$) · ใช้แค่ตัวที่ <b>มากที่สุด</b> เพราะงานพวกนั้นทำพร้อมกันได้</div>
{tag('o','κ<sub>j</sub>')}<div>rank แบบ 0..1 (หารด้วย rank สูงสุด) ใช้เป็น "ความวิกฤต" ในคะแนน V</div>
{tag('p','|A<sub>j</sub>|')}<div>จำนวนบัญชีที่ <b>รับงานนี้ได้</b> (ผ่านขั้น ② กรอง) · น้อย = ได้ก่อน (MRV: Minimum Remaining Values)</div>
</div>
<div class="ex">🔢 รอบที่ 4: rank(T08) = 3 + max(T12 7.5, T09 4.5, T10 4.5) = <b>10.5</b> → κ = 10.5 ÷ 15 = <b>0.7</b> · ทุกงานมีทางเลือก ≥ 3 → ชั้น MRV เท่ากัน (นับสูงสุดแค่ 3) จึงตัดสินด้วย κ: T08 0.7 → T11 0.6 → T06 0.5 → T07 0.24 · MRV มีผลเมื่อบางงานมีทางเลือกแค่ 1–2 บัญชี (เช่น งานรูปที่ต้องเป็น cyolo)</div>
""")

# ---------------------------------------------------------------- 2) capacity / feasibility
CARDS["eq-capacity"] = ("② กรอง: บัญชีนี้ทำงานนี้จนจบได้ไหม", "hard constraint → ตัดทิ้ง ไม่ใช่หักคะแนน", f"""
<div class="idea">💡 ไอเดีย: เหมือนเช็กน้ำมันก่อนออกรถ — <b>ระยะที่วิ่งได้ = น้ำมันที่ใช้ได้ ÷ อัตรากิน</b> · บัญชี AI มี <b>2 ถัง</b> (5 ชม. และสัปดาห์) ต้องพอทั้งคู่ → ใช้ค่า min</div>
<div class="eq">$$C_a=\\min\\!\\left(\\frac{{{tc('b','H^{5}_a')}-{tc('o','m^{5}_a')}-{tc('r','Q_a')}}}{{{tc('p','\\sigma')}\\,{tc('g','r^{5}_a')}}},\\ \\frac{{{tc('b','H^{w}_a')}-{tc('o','m^{w}_a')}-{tc('r','Q_a')}}}{{{tc('p','\\sigma')}\\,{tc('g','r^{w}_a')}}}\\right) \\qquad \\text{{ผ่านเมื่อ}}\\ \\ c_j \\le C_a$$</div>
<div class="lg">
{tag('b','H')}<div>โควตาที่ <b>เหลือ</b> (%) ของแต่ละถัง หลังหักงานที่กำลังรันและที่จองไว้แล้ว</div>
{tag('g','r')}<div>อัตรากิน: ใช้ 1 ล้านโทเคนแล้วโควตาหายกี่ % (5 ชม. ≈ 2 · สัปดาห์ ≈ 0.25 · เรียนรู้จริงในขั้น ⑥)</div>
{tag('p','σ = 1.3')}<div>เผื่อค่าประเมินผิด 30% (robust: คิดเหมือนงานใหญ่กว่าที่เดา)</div>
{tag('o','m')}<div>ระยะเบรก = โควตาที่ใช้ได้ใน 15 นาที $= \\max(2,\\ r\\cdot v\\cdot 0.25\\cdot n)$ · เวลาที่ ⑤ ตอบสนองทัน</div>
{tag('r','Q = 20')}<div>กันไว้ให้ <b>ตัวคุมวง</b> (orchestrator) เท่านั้น บัญชีอื่น Q = 0</div>
</div>
<div class="ex">🔢 งาน T08 (c = 3): yolo3 → ถัง 5 ชม. (100 − 3.6) ÷ (1.3×2) = 37.08 · ถังสัปดาห์ (7 − 2) ÷ (1.3×0.25) = <b>15.38</b> → C = 15.38 ✅<br>
yolo1 → (6 − 3.6) ÷ (1.3×2) = <b>0.92</b> &lt; 3 ❌ ตัดทิ้ง (ถ้าให้ทำ จะชนเพดานกลางงาน)</div>
""")

# ---------------------------------------------------------------- 3) factors
CARDS["eq-factors"] = ("③ ให้คะแนน: 5 ตัวแปร (แต่ละตัวอยู่ในช่วง 0..1)", "แต่ละตัวมาจากเป้าหมายคนละข้อ", f"""
<table>
<tr><th>ตัวแปร</th><th>สูตร</th><th>ไอเดีย (มาจากเป้าหมายไหน)</th><th>yolo2 · T08</th></tr>
<tr><td>{tag('o','U ใกล้หมดอายุ')}</td><td>$\\dfrac{{T_0}}{{T_0 + T_a}},\\ T_0 = 24$</td><td style="text-align:left">โควตาที่จะรีเซ็ตใน $T_a$ ชม. ถ้าไม่ใช้ก็หายฟรี → ใช้ก่อน<br>(เป้าหมายรอง: ไม่ทิ้งโควตา)</td><td>24 ÷ 44 = <b>0.545</b></td></tr>
<tr><td>{tag('g','F พอดีถัง')}</td><td>$\\min\\!\\Big(1,\\dfrac{{\\sigma r^{{w}}_a c_j}}{{H^{{w}}_a}}\\Big)$</td><td style="text-align:left">best-fit ของ bin packing: งานกินถังไปมาก = พอดีถัง<br>เก็บถังใหญ่ไว้ให้งานใหญ่</td><td>0.98 ÷ 43.04 = <b>0.023</b></td></tr>
<tr><td>{tag('b','R ว่าง 5 ชม.')}</td><td>$\\dfrac{{\\max(0,\\ H^{{5}}_a - \\sigma r^{{5}}_a c_j)}}{{100}}$</td><td style="text-align:left">หลังรับงานแล้วถัง 5 ชม. ยังเหลือเท่าไร<br>เหลือมาก = ไม่ชนเพดานรายชั่วโมง</td><td>(74.4 − 7.8) ÷ 100 = <b>0.666</b></td></tr>
<tr><td>{tag('p','V เร็ว×วิกฤต')}</td><td>$v_{{\\text{{kind}}}}\\cdot\\kappa_j$</td><td style="text-align:left">งานบนสายวิกฤตไปบัญชีที่เร็ว (yolo 1.0 · cyolo 0.7)<br>(เป้าหมายหลัก: ลด C<sub>max</sub>)</td><td>1.0 × 0.7 = <b>0.7</b></td></tr>
<tr><td>{tag('r','L งานล้น')}</td><td>$\\dfrac{{\\text{{used}}_a}}{{\\text{{slots}}_a}}$ (น้ำหนักติดลบ)</td><td style="text-align:left">บัญชีที่ทำอยู่หลายงานแล้วโดนหักคะแนน<br>→ กระจายงาน ไม่กองที่เดียว</td><td>0 ÷ 4 = <b>0</b></td></tr>
</table>
<div class="note">ทุกตัวถูกทำให้อยู่ช่วง 0..1 ก่อนรวม (normalize) ไม่งั้นตัวที่หน่วยใหญ่จะกลบตัวอื่น · ตัวเลขมาจากรอบที่ 4 ของบทเรียน</div>
""")

# ---------------------------------------------------------------- 4) score + argmax + reserve
CARDS["eq-score"] = ("③④ รวมคะแนน → เลือก → จองทันที", "weighted sum (scalarization) + greedy", f"""
<div class="idea">💡 ไอเดีย: เป้าหมายหลายข้อขัดกัน → <b>ถ่วงน้ำหนักแล้วรวมเป็นเลขเดียว</b> (เหมือนให้คะแนนคอนโด: ราคา 40% ทำเล 30% …) แล้วเลือกตัวที่สูงสุด จากนั้น <b>จองโควตาทันที</b></div>
<div class="eq sm">$$S_{{a}}=100\\big({tc('o','0.40\\,U')}+{tc('g','0.20\\,F')}+{tc('b','0.15\\,R')}+{tc('p','0.15\\,V')}{tc('r','\\,-\\,0.10\\,L')}\\big)\\qquad a^{{*}}=\\arg\\max_{{a\\in A_j}} S_a$$</div>
<div class="eq sm">$$\\text{{จอง:}}\\quad H^{{5}}_{{a^*}} \\leftarrow H^{{5}}_{{a^*}} - \\sigma r^{{5}}_{{a^*}} c_j,\\qquad H^{{w}}_{{a^*}} \\leftarrow H^{{w}}_{{a^*}} - \\sigma r^{{w}}_{{a^*}} c_j,\\qquad \\text{{used}}_{{a^*}} \\leftarrow \\text{{used}}_{{a^*}} + 1$$</div>
<div class="ex">🔢 T08: yolo2 = 100 × (0.4×0.545 + 0.2×0.023 + 0.15×0.666 + 0.15×0.7 − 0.1×0) = <b>42.8</b> · yolo3 = 34.9 · cyolo1 = 26.3 → ได้ <b>yolo2</b><br>
จอง: 5 ชม. 74.4 → <b>66.6</b> · สัปดาห์ 43.04 → <b>42.06</b> · used 0 → <b>1</b> · งานถัดไป (T11) จึงเห็น R ลด L เพิ่ม คะแนน yolo2 ลดเอง</div>
<div class="ex">🔢 T07 (งานสุดท้ายของรอบ): yolo2 ทำอยู่ 3/4 แล้ว L = 0.75 → ถูกหัก 7.5 คะแนน · yolo3 ได้ <b>26.7</b> ชนะ yolo2 26.0 → งานเริ่มกระจาย</div>
""")

# ---------------------------------------------------------------- 5) lower bound + Graham
CARDS["eq-bound"] = ("ดีแค่ไหน: ขอบล่างของเวลา + ทฤษฎี list scheduling", "เทียบกับคำตอบที่ดีที่สุดได้โดยไม่ต้องหา", f"""
<div class="idea">💡 ไอเดีย: ไม่ว่าแจกเก่งแค่ไหน ก็เร็วกว่า <b>สายวิกฤต</b> ไม่ได้ และเร็วกว่า <b>งานทั้งหมด ÷ จำนวน agent</b> ไม่ได้ → ถ้าทำได้เท่าขอบล่าง = ดีที่สุดแล้ว</div>
<div class="eq">$$C_{{\\max}} \\;\\ge\\; LB = \\max\\Big(\\ {tc('o','\\frac{{\\text{{rank}}_{{\\max}}}}{{v}}')},\\ \\ {tc('b','\\frac{{\\sum_j c_j}}{{N\\, v}}')}\\ \\Big)$$</div>
<div class="eq sm">$$\\text{{Graham (1966):}}\\quad C^{{\\text{{list}}}}_{{\\max}} \\;\\le\\; \\Big(2-\\frac{{1}}{{N}}\\Big)\\, C^{{\\text{{OPT}}}}_{{\\max}}$$</div>
<div class="ex">🔢 catfood (6 agent · yolo เร็ว 7.2 M/ชม.): สายวิกฤต 15 ÷ 7.2 = <b>125 นาที</b> · งานรวม 26.1 ÷ (6 × 7.2) = 36 นาที → LB = <b>125 นาที</b><br>
KC-QUEST ได้ <b>125 นาที = เท่าขอบล่าง</b> → ในตัวอย่างนี้ดีที่สุดแล้ว (optimal) แม้ใช้ heuristic</div>
<div class="note">Graham (ปัญหาพื้นฐานที่ไม่มีโควตา): การแจกแบบ "มีคนว่างเมื่อไรแจกทันที" (list scheduling) แย่สุดไม่เกิน 2 เท่าของคำตอบที่ดีที่สุดเสมอ · การเรียงด้วย rank (critical path) ช่วยให้เข้าใกล้ขอบล่างในทางปฏิบัติ</div>
""")

# ---------------------------------------------------------------- 6) urgency curve (กราฟ)
def urgency_svg():
    W, H, X0, Y0, PW, PH = 1500, 520, 110, 40, 1300, 400
    def px(T): return X0 + T / 168 * PW
    def py(u): return Y0 + PH - u * PH
    pts = " ".join(f"{px(T):.1f},{py(24 / (24 + T)):.1f}" for T in range(0, 169))
    s = [f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Leelawadee UI, Tahoma" font-size="22">',
         f'<line x1="{X0}" y1="{Y0 + PH}" x2="{X0 + PW}" y2="{Y0 + PH}" stroke="#888"/><line x1="{X0}" y1="{Y0}" x2="{X0}" y2="{Y0 + PH}" stroke="#888"/>']
    for T in (0, 24, 48, 72, 96, 120, 144, 168):
        s.append(f'<text x="{px(T)}" y="{Y0 + PH + 30}" text-anchor="middle" fill="#555">{T}</text>')
    for u in (0, 0.25, 0.5, 0.75, 1):
        s.append(f'<text x="{X0 - 14}" y="{py(u) + 7}" text-anchor="end" fill="#555">{u:g}</text><line x1="{X0}" y1="{py(u)}" x2="{X0 + PW}" y2="{py(u)}" stroke="#eee"/>')
    s.append(f'<polyline points="{pts}" fill="none" stroke="{C["o"]}" stroke-width="5"/>')
    lx, ly = X0 + PW - 430, Y0 + 30          # กล่องค่าทางขวาบน (ที่ว่าง)
    s.append(f'<rect x="{lx - 20}" y="{ly - 34}" width="450" height="190" rx="12" fill="#fafbfd" stroke="#e3e8ef"/>')
    for n, (name, T, col, dy) in enumerate((("yolo2", 20, C["o"], -22), ("yolo3", 100, C["b"], -22), ("yolo1", 130, C["g"], 40), ("cyolo1", 150, C["p"], -22))):
        u = 24 / (24 + T)
        s.append(f'<circle cx="{px(T)}" cy="{py(u)}" r="11" fill="{col}"/><text x="{px(T)}" y="{py(u) + dy}" text-anchor="middle" font-weight="700" fill="{col}">{name}</text>')
        s.append(f'<circle cx="{lx}" cy="{ly + n * 42 - 7}" r="9" fill="{col}"/><text x="{lx + 20}" y="{ly + n * 42}" fill="{col}" font-weight="700">{name}: T = {T} ชม. → U = 24 ÷ {24 + T} = {u:.3f}</text>')
    s.append(f'<text x="{px(24) + 16}" y="{py(0.5) - 12}" fill="#888" font-size="19">T = T₀ = 24 → U = 0.5</text><circle cx="{px(24)}" cy="{py(0.5)}" r="6" fill="#999"/>')
    s.append(f'<text x="{X0 + PW}" y="{Y0 + PH + 62}" text-anchor="end" fill="#333">T = อีกกี่ชั่วโมงโควตาสัปดาห์จะรีเซ็ต (หมดอายุ)</text>')
    s.append("</svg>")
    return "\n".join(s)

CARDS["eq-urgency"] = ("U: ทำไมต้องเป็น T₀ ÷ (T₀ + T)", "ใช้ก่อนหมดอายุ = ไม่ทิ้งของฟรี", f"""
<div class="idea">💡 ไอเดีย: โควตาสัปดาห์ที่เหลือ <b>จะหายไปเฉย ๆ ตอนรีเซ็ต</b> · บัญชีที่ใกล้รีเซ็ตจึงควรถูกใช้ก่อน · ต้องการฟังก์ชันที่ <b>T น้อย → ใกล้ 1</b>, <b>T มาก → ใกล้ 0</b>, ลดลงแบบนุ่ม ๆ และไม่ติดลบ</div>
<div class="eq sm">$$U_a = \\frac{{T_0}}{{T_0+T_a}}\\qquad T_a=0\\Rightarrow U=1,\\quad T_a=T_0=24\\Rightarrow U=0.5,\\quad T_a\\to\\infty\\Rightarrow U\\to 0$$</div>
<div style="margin:6px 44px 0">{urgency_svg()}</div>
<div class="note">ในบทเรียน yolo2 จะรีเซ็ตใน 20 ชม. จึงมี U สูงสุด (0.545) → ได้งานส่วนใหญ่ · ปรับความชันได้ด้วย T₀ (config: urgency_t0_h)</div>
""")

# ---------------------------------------------------------------- 7) project + migrate + learn + failover
CARDS["eq-runtime"] = ("⑤⑥✦ ระหว่างทำงาน: คาดการณ์ · ย้าย · เรียนรู้ · ส่งไม้", "feedback control: แผนผิดก็แก้ได้ระหว่างทาง", rf"""
<div class="idea">💡 ไอเดีย: ขั้น ①–④ ตัดสินใจจาก <b>ค่าประเมิน</b> ซึ่งอาจผิด · ขั้น ⑤⑥✦ คือ <b>วงจรป้อนกลับ</b> ที่ดูของจริงแล้วแก้ (เหมือนขับรถแล้วคอยดูเกจน้ำมัน)</div>
<div class="eq sm">$$\text{{⑤ คาดการณ์}}\quad P_a = {tc('b','u_a')} + \sum_{{j\,\in\,\text{{run}}(a)}} {tc('o',r'\mathrm{rem}_j')}\cdot r_a \;>\; {tc('r','100 - m')}\;\Rightarrow\; \text{{ย้ายงาน}}$$</div>
<div class="lg">{tag('b','u')}<div>ใช้ไปแล้ว (%) ของถังนั้น</div>{tag('o','rem')}<div>โทเคนที่งานยังต้องใช้ ≈ max(ประเมิน − ใช้ไป, 0.15 × ประเมิน) แล้วปรับด้วยความคืบหน้า (checklist)</div>{tag('r','100 − m')}<div>เส้นย้ายงาน อยู่ <b>เหนือ</b> เส้นแจกงาน (ที่หาร σ) เสมอ → งานที่เพิ่งแจกจะไม่ถูกย้ายไปมา · ย้าย = commit งานค้าง + HANDOFF แล้วบัญชีอื่นทำต่อ</div></div>
<div class="eq sm">$$\text{{⑥ เรียนรู้ (EMA)}}\quad r \leftarrow {tc('g','0.5')}\,r + 0.5\,\frac{{\Delta\%}}{{\Delta\text{{โทเคน}}}} \qquad k_{{\text{{size}}}} \leftarrow {tc('g','0.6')}\,k + 0.4\,\frac{{\text{{ใช้จริง}}}}{{\text{{ประเมิน}}}}$$</div>
<div class="note">EMA = ค่าเฉลี่ยเคลื่อนที่แบบถ่วงน้ำหนัก: เชื่อค่าที่เพิ่งวัดส่วนหนึ่ง เก็บค่าเดิมส่วนหนึ่ง → ปรับตัวเร็วแต่ไม่แกว่ง · ใช้ r ใหม่ในขั้น ② ทันที และขนาดงานกลายเป็น c = ĉ × k</div>
<div class="eq sm">$$\text{{✦ ส่งไม้}}\quad H_{{\text{{orch}}}} < 15\%\;\Rightarrow\; \text{{orch}} \leftarrow \arg\max_a \big(H_a + 5\cdot\mathbb{{1}}[a\ \text{{เป็น yolo}}]\big)$$</div>
<div class="note">ตัวคุมวงใกล้หมด → ส่งไม้ให้บัญชีที่เหลือมากสุด (Claude ได้ +5 เพราะตอบเร็วกว่า) · สถานะทั้งหมดเก็บในไฟล์ จึงเปลี่ยนคนคุมกลางทางได้</div>
""")


# ---------------------------------------------------------------- 8) กราฟการคำนวณ (computation graph) ของคู่ yolo2 × T08
STEPC = {"in": "#7f8c8d", "1": C["o"], "2": C["b"], "3": C["g"], "4": C["p"]}
COLX = [30, 450, 900, 1350, 1800, 2240]

def graph_body():
    # (id, คอลัมน์, y, ขั้น, หัวข้อ, สูตร TeX หรือ None, ค่า)
    N = [
        ("c", 0, 130, "in", "ขนาดงาน $c_j$", None, "3 (L)"),
        ("succ", 0, 225, "in", "งานที่รอ succ(T08)", None, "T12 7.5 · T09 4.5 · T10 4.5"),
        ("rmax", 0, 320, "in", "rank สูงสุดทั้งกราฟ", None, "15"),
        ("H5", 0, 440, "in", "เหลือ 5 ชม. $H^5$", None, "74.4%"),
        ("Hw", 0, 535, "in", "เหลือสัปดาห์ $H^w$", None, "43.04%"),
        ("r5", 0, 630, "in", "อัตรา $r^5$ · $r^w$", None, "2 · 0.25 %/M"),
        ("T", 0, 725, "in", "อีกกี่ชม.หมดอายุ $T$", None, "20 ชม."),
        ("used", 0, 820, "in", "ทำอยู่ / slot", None, "0 / 4"),
        ("v", 0, 915, "in", "ชนิด · ความเร็ว", None, "yolo · v 1.0 · 7.2 M/ชม."),
        ("sig", 0, 1035, "in", "ค่าคงที่", None, "σ 1.3 · T₀ 24 · Q 0"),
        ("w", 0, 1130, "in", "น้ำหนัก $w$", None, "0.40 · 0.20 · 0.15 · 0.15 · −0.10"),
        ("rank", 1, 140, "1", "rank(T08)", r"c_j+\max_{k}\mathrm{rank}(k)", "3 + 7.5 = 10.5"),
        ("kap", 1, 300, "1", "ความวิกฤต κ", r"\mathrm{rank}/\mathrm{rank}_{\max}", "10.5 ÷ 15 = 0.7"),
        ("m", 1, 460, "2", "ระยะเบรก m", r"\max(2,\ r\,v\,0.25\,(n{+}1))", "m⁵ 3.6 · mʷ 2"),
        ("q", 1, 620, "2", "โควตาที่งานจะใช้ q", r"q=\sigma\, r\, c_j", "q⁵ 7.8 · qʷ 0.975"),
        ("C5", 2, 380, "2", "ถัง 5 ชม. รับได้", r"\frac{H^5-m^5-Q}{\sigma r^5}", "70.8 ÷ 2.6 = 27.23"),
        ("Cw", 2, 540, "2", "ถังสัปดาห์รับได้", r"\frac{H^w-m^w-Q}{\sigma r^w}", "41.04 ÷ 0.325 = 126.3"),
        ("C", 2, 700, "2", "รับได้จริง $C_a$", r"\min(C^5, C^w)", "27.23"),
        ("ok", 2, 860, "2", "ผ่านกรอง?", r"c_j \le C_a", "3 ≤ 27.23 ✅"),
        ("U", 3, 130, "3", "U ใกล้หมดอายุ", r"\frac{T_0}{T_0+T}", "24 ÷ 44 = 0.545"),
        ("F", 3, 285, "3", "F พอดีถัง", r"q^w / H^w", "0.975 ÷ 43.04 = 0.023"),
        ("R", 3, 440, "3", "R ว่าง 5 ชม.", r"(H^5-q^5)/100", "66.6 ÷ 100 = 0.666"),
        ("V", 3, 595, "3", "V เร็ว × วิกฤต", r"v\cdot\kappa", "1.0 × 0.7 = 0.7"),
        ("L", 3, 750, "3", "L งานล้น", r"\mathrm{used}/\mathrm{slots}", "0 ÷ 4 = 0"),
        ("S", 4, 400, "3", "คะแนน $S$", r"100\sum_k w_k f_k", "21.8+0.5+10.0+10.5−0 = 42.8"),
        ("oth", 4, 130, "in", "คะแนนบัญชีอื่น (คิดแบบเดียวกัน)", None, "yolo3 34.9 · cyolo1 26.3 · yolo1 ✗ ตัดแล้ว"),
        ("arg", 4, 660, "4", "เลือก $a^*$", r"\arg\max_{a\,\in\,A_j} S_a", "yolo2 (42.8)"),
        ("res", 5, 660, "4", "จองทันที", r"H\leftarrow H-q,\ \mathrm{used}{+}{+}", "H⁵ 66.6 · Hʷ 42.06 · used 1"),
    ]
    E = [("c","rank"),("succ","rank"),("rank","kap"),("rmax","kap"),
         ("r5","m"),("v","m"),("used","m"),("sig","q"),("r5","q"),("c","q"),
         ("H5","C5"),("m","C5"),("sig","C5"),("Hw","Cw"),("m","Cw"),("C5","C"),("Cw","C"),("C","ok"),("c","ok"),
         ("T","U"),("sig","U"),("q","F"),("Hw","F"),("H5","R"),("q","R"),("kap","V"),("v","V"),("used","L"),
         ("U","S"),("F","S"),("R","S"),("V","S"),("L","S"),("w","S"),
         ("S","arg"),("ok","arg"),("oth","arg"),("arg","res"),("q","res")]
    W_IN, W_CALC, H_IN, H_CALC = 370, 390, 80, 132
    pos = {}
    for n in N:
        i, col, y, st = n[0], n[1], n[2], n[3]
        w = W_IN if (st == "in" and col == 0) else W_CALC
        h = H_IN if n[5] is None else H_CALC
        if i == "oth": w, h = 390, 100
        pos[i] = (COLX[col], y, w, h)
    step_of = {n[0]: n[3] for n in N}
    svg = []
    for a, b in E:
        xa, ya, wa, ha = pos[a]; xb, yb, wb, hb = pos[b]
        x1, y1, x2, y2 = xa + wa, ya + ha / 2, xb - 4, yb + hb / 2
        mx = (x1 + x2) / 2
        col = STEPC[step_of[b]]
        svg.append(f'<path d="M{x1},{y1} C{mx},{y1} {mx},{y2} {x2},{y2}" fill="none" stroke="{col}" stroke-opacity=".55" stroke-width="2.4" marker-end="url(#ah)"/>')
    xr, yr, wr, hr = pos["res"]
    svg.append(f'<path d="M{xr + wr/2},{yr + hr} L{xr + wr/2},1235 L14,1235 L14,{pos["H5"][1] + 40} L{COLX[0] - 4},{pos["H5"][1] + 40}" fill="none" stroke="{C["p"]}" stroke-width="3" stroke-dasharray="10 7" marker-end="url(#ah2)"/>')
    svg.append(f'<text x="{COLX[1]}" y="1222" font-size="24" fill="{C["p"]}" font-weight="700">↺ ค่าที่จองแล้วกลายเป็นอินพุตของงานถัดไป (T11): H⁵ 74.4 → 66.6 · used 0 → 1 → R ลด L เพิ่ม คะแนน yolo2 ลดเอง</text>')
    boxes = []
    for i, col, y, st, title, tex, val in N:
        x, yy, w, h = pos[i]
        f = f'<div class="nf">$\\displaystyle {tex}$</div>' if tex else ""
        boxes.append(f'<div class="nd" style="left:{x}px;top:{yy}px;width:{w}px;height:{h}px;border-color:{STEPC[st]}">'
                     f'<div class="nt" style="color:{STEPC[st]}">{title}</div>{f}<div class="nv">{val}</div></div>')
    heads = [("อินพุต (ข้อมูล)", 0, "in"), ("① ค่ากลาง · ② เตรียม", 1, "2"), ("② กรอง", 2, "2"), ("③ ตัวแปรคะแนน", 3, "3"), ("③ รวม · ④ เลือก", 4, "4"), ("④ จอง", 5, "4")]
    hh = "".join(f'<div class="ch" style="left:{COLX[c]}px;color:{STEPC[s_]}">{t}</div>' for t, c, s_ in heads)
    return f"""
<div class="idea">💡 อ่านแบบนักวิทยาศาสตร์: ทุกกล่องคือ <b>ตัวแปร 1 ตัว</b> · ลูกศรบอกว่า <b>คำนวณจากอะไร</b> · ในกล่อง = สูตร + ค่าจริงของคู่ <b>yolo2 × งาน T08</b> (รอบที่ 4) · ไล่จากซ้ายไปขวาจะได้คะแนน 42.8 และการจอง</div>
<div style="position:relative;height:1260px;margin:10px 0 0">
<svg width="2660" height="1260" style="position:absolute;left:0;top:0">
<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0L10,5L0,10z" fill="#888"/></marker>
<marker id="ah2" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0L10,5L0,10z" fill="{C['p']}"/></marker></defs>
{''.join(svg)}</svg>{hh}{''.join(boxes)}</div>
"""

GRAPH_CSS = """
.nd{position:absolute;background:#fff;border:3px solid;border-radius:14px;padding:6px 12px;box-shadow:0 2px 6px rgba(0,0,0,.06)}
.nt{font-size:21px;font-weight:700;line-height:1.3}
.nf{font-size:20px;margin:4px 0 2px;white-space:nowrap}
.nf .katex-display{margin:.35em 0}
.nv{font-size:21px;font-weight:700;color:#111}
.ch{position:absolute;top:70px;font-size:24px;font-weight:700}
"""
CARDS["eq-graph"] = ("กราฟการคำนวณของ KC-QUEST", "ตัวแปรไหนมาจากไหน · คำนวณอย่างไร · ค่าจริงทุกโหนด", graph_body(), 2660)

# ---------------------------------------------------------------- 9) ไล่การคำนวณทั้งรอบ (trace)
def trace_body():
    rows = [
        ("T08", "L 3", "74.4", "0/4", "0.666", "0", "42.8", "34.9", "26.3", "✗ (C 0.92)", "yolo2", "yolo2 H⁵ 74.4 → 66.6 · used 1"),
        ("T11", "M 1.5", "66.6", "1/4", "0.627", "0.25", "37.9", "32.6", "25.8", "✗ (C 0.92)", "yolo2", "yolo2 H⁵ 66.6 → 62.7 · used 2"),
        ("T06", "L 3", "62.7", "2/4", "0.549", "0.5", "33.0", "31.9", "24.2", "✗ (C 0.92)", "yolo2", "yolo2 H⁵ 62.7 → 54.9 · used 3"),
        ("T07", "S 0.6", "54.9", "3/4", "0.533", "0.75", "26.0", "26.7", "22.3", "10.5", "yolo3", "yolo3 Hʷ 7 → 6.8 · used 1"),
    ]
    tr = []
    for r in rows:
        win = r[10]
        def cell(v, acc):
            st = "background:#fdebd0;font-weight:700;color:#c0392b" if acc == win else ""
            return f'<td style="{st}">{v}{" ★" if acc == win else ""}</td>'
        tr.append(f"<tr><td><b>{r[0]}</b><br><small>{r[1]}</small></td><td>{r[2]}</td><td>{r[3]}</td><td>{r[4]}</td><td>{r[5]}</td>"
                  f"{cell(r[6], 'yolo2')}{cell(r[7], 'yolo3')}{cell(r[8], 'cyolo1')}<td style='color:#999'>{r[9]}</td><td style='text-align:left'>{r[11]}</td></tr>")
    return f"""
<div class="idea">💡 ไล่ตามลำดับที่ ① เรียงไว้ · ทุกแถว: ② กรอง → ③ คะแนนทุกบัญชี → ④ ผู้ชนะ (★) จองทันที → <b>ค่าที่จองแล้วไหลลงไปเป็นอินพุตของแถวถัดไป</b> (ช่องสีฟ้า)</div>
<table><tr><th rowspan="2">งาน</th><th colspan="4" style="background:#eaf2fb">สถานะ yolo2 ตอนเริ่มแถว</th><th colspan="3">③ คะแนน S</th><th rowspan="2">yolo1</th><th rowspan="2">④ จองแล้ว</th></tr>
<tr><th style="background:#eaf2fb">H⁵</th><th style="background:#eaf2fb">used</th><th style="background:#eaf2fb">R</th><th style="background:#eaf2fb">L</th><th>yolo2</th><th>yolo3</th><th>cyolo1</th></tr>
{''.join(tr)}</table>
<div class="ex">🔢 สูตรของ yolo2 ทั้ง 4 แถว: S = 100 × (0.4×<b>0.545</b> + 0.2×F + 0.15×<b>R</b> + 0.15×(1.0×κ) − 0.1×<b>L</b>) · U คงที่ (ยังไม่รีเซ็ต) · R ลดเพราะจอง H⁵ · L เพิ่มเพราะ used เพิ่ม · κ ลดตามงาน (0.7 → 0.6 → 0.5 → 0.24)<br>
แถวสุดท้าย L = 0.75 ถูกหัก <b>7.5</b> คะแนน → yolo3 (26.7) แซง yolo2 (26.0) = <b>การจองทำให้งานกระจายเอง</b> โดยไม่ต้องมีกฎ "ห้ามให้บัญชีเดียวเกิน X งาน"</div>
"""
CARDS["eq-trace"] = ("ไล่การคำนวณทั้งรอบที่ 4 ทีละงาน", "สถานะเปลี่ยน → คะแนนเปลี่ยน → ผู้ชนะเปลี่ยน", trace_body())

def page(title, sub, body, width=1600):
    return f"""<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="{KATEX}/katex.min.css">
<script defer src="{KATEX}/katex.min.js"></script>
<script defer src="{KATEX}/contrib/auto-render.min.js" onload="renderMathInElement(document.body,{{delimiters:[{{left:'$$',right:'$$',display:true}},{{left:'$',right:'$',display:false}}]}});document.body.dataset.ok=1"></script>
<style>{CSS}{GRAPH_CSS}#card{{width:{width}px}}</style></head><body><div id="card"><div class="hd">{title}<small>{sub}</small></div>{body}</div></body></html>"""

def main():
    from playwright.sync_api import sync_playwright
    want = sys.argv[1:] or list(CARDS)
    tmp = os.path.join(os.path.dirname(HERE), "out", "figures"); os.makedirs(tmp, exist_ok=True)
    with sync_playwright() as pw:
        b = None
        for ch in (None, "chrome", "msedge"):
            try: b = pw.chromium.launch(channel=ch) if ch else pw.chromium.launch(); break
            except Exception: continue
        pg = b.new_page(device_scale_factor=2, viewport={"width": 1600, "height": 900})
        for name in want:
            t, sub, body, *wd = CARDS[name]
            width = wd[0] if wd else 1600
            pg.set_viewport_size({"width": width, "height": 900})
            html = os.path.join(tmp, name + ".html")
            open(html, "w", encoding="utf-8").write(page(t, sub, body, width))
            pg.goto("file:///" + html.replace(os.sep, "/"))
            pg.wait_for_function("document.body.dataset.ok == '1'", timeout=30000)
            pg.wait_for_timeout(300)
            out = os.path.join(IMG, name + ".png")
            pg.locator("#card").screenshot(path=out)
            print(out)
        b.close()

if __name__ == "__main__":
    main()
