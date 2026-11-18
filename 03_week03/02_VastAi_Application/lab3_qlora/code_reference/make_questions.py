"""สร้างบทสนทนาฝั่งลูกค้าของร้าน "สบายใจ นวดแผนไทย" สำหรับทำ Dataset (ยังไม่มีคำตอบ)

ผลลัพธ์: lab3_qlora/data/questions.jsonl  หนึ่งบรรทัด = หนึ่งบทสนทนา
  {"id", "kind", "kind_th", "now": "YYYY-MM-DD HH:MM", "turns": [{"user": ..., "expect": {...}}]}

expect ของแต่ละข้อความลูกค้า = เงื่อนไขที่คำตอบของบอทต้องผ่าน (กติกาเดียวกับ e2e/tests/check.ts)
  has     ต้องมีทุกรายการ (รายการที่เป็น list = มีอย่างใดอย่างหนึ่ง)
  not     ห้ามมี            คำขึ้นต้น re: = regular expression · ตัวเลขล้วนต้องไม่เป็นส่วนของเลขอื่น
  lang    th | en           ภาษาของคำตอบ
  booking "none" = ห้ามมีแท็ก [BOOKING] · object = ต้องมีแท็กที่ค่าตรง
          (customer_name ต้องมี name_must_contain, phone เทียบเฉพาะตัวเลข, service และ booking_time ต้องตรงเป๊ะ)
  no_markdown  ห้ามใช้ ** หรือ # หรือตาราง (กฎข้อ 8 ของ system prompt)
  must    เงื่อนไขเป็นคำพูดภาษาไทย

ข้อมูลร้านอ่านจากโค้ดเว็บที่คัดลอกมา (web/db/init.sql) · ข้อความต้องห้ามอ่านจาก e2e/cases.json
และปุ่มลัดใน web/components/Chat.tsx
"""
from __future__ import annotations

import json
import math
import random
import re
from collections import Counter
from datetime import date, datetime, timedelta
from difflib import SequenceMatcher
from pathlib import Path

SEED = 2026
HERE = Path(__file__).resolve().parent
LAB = HERE.parent
OUT = LAB / "data" / "questions.jsonl"
SIM_THRESHOLD = 0.75  # ความคล้ายกับข้อความของชุดทดสอบตั้งแต่ค่านี้ขึ้นไป = "คล้าย" -> สุ่มใหม่

# ---------------------------------------------------------------- 1. ข้อมูลร้านจากโค้ดเว็บ
SQL = (HERE / "web" / "db" / "init.sql").read_text(encoding="utf-8")
SERVICES_DB = {
    m[0]: {"min": int(m[1]), "price": int(m[2]), "desc": m[3]}
    for m in re.findall(r"\('([^']+)',\s*(\d+),\s*(\d+),\s*'([^']*)'\)", SQL)
}
INFO = dict(re.findall(r"\('(\w+)',\s+'([^']*)'\)", SQL))
assert len(SERVICES_DB) == 8 and "hours" in INFO, "อ่านข้อมูลร้านจาก init.sql ไม่ครบ"
assert "10:00 - 22:00" in INFO["hours"] and "21:00" in INFO["hours"]
OPEN_H, CLOSE_H, LAST_H = 10, 22, 21

# ชื่อเรียกที่ลูกค้าใช้ (ไทย / อังกฤษ) -> ชื่อบริการในระบบ
ALIASES = {
    "นวดไทยแผนโบราณ": (["นวดไทย 1 ชั่วโมง", "นวดแผนไทย 60 นาที", "นวดไทยแผนโบราณ", "นวดไทยชั่วโมงเดียว", "นวดแผนโบราณ 1 ชม."],
                        ["a one-hour Thai massage", "traditional Thai massage (60 min)", "the 60-minute Thai massage"]),
    "นวดไทยแผนโบราณ 2 ชั่วโมง": (["นวดไทย 2 ชั่วโมง", "นวดแผนไทยแบบ 2 ชม.", "นวดไทยเต็ม 120 นาที", "นวดไทยแผนโบราณสองชั่วโมง"],
                                  ["a two-hour Thai massage", "the 120-minute Thai massage"]),
    "นวดน้ำมันอโรมา": (["นวดอโรมา", "นวดน้ำมันหอมระเหย", "อโรมาออยล์", "นวดน้ำมัน"],
                        ["an aromatherapy oil massage", "the aroma massage"]),
    "นวดเท้าสะท้อนจุด": (["นวดเท้า", "นวดกดจุดฝ่าเท้า", "นวดฝ่าเท้า", "นวดเท้าสะท้อนจุด"],
                          ["a foot reflexology massage", "foot massage"]),
    "นวดคอบ่าไหล่": (["นวดคอบ่าไหล่", "นวดคอกับบ่า", "นวดบ่าไหล่", "นวดคอ บ่า ไหล่"],
                      ["a neck and shoulder massage", "the neck & shoulder massage"]),
    "นวดแก้ปวดหลัง": (["นวดแก้ปวดหลัง", "นวดหลัง", "นวดแก้หลังตึง", "นวดเน้นหลัง"],
                       ["a back pain massage", "the back massage"]),
    "ประคบสมุนไพร": (["ประคบสมุนไพร", "นวดลูกประคบ", "ลูกประคบสมุนไพร", "นวดประคบ"],
                      ["a herbal compress massage", "the herbal compress"]),
    "นวดหน้าและศีรษะ": (["นวดหน้าและศีรษะ", "นวดหน้ากับหัว", "นวดศีรษะ", "นวดหน้า"],
                         ["a face and head massage", "the head massage"]),
}
assert set(ALIASES) == set(SERVICES_DB)
SVC = list(SERVICES_DB)
PRICE = {k: v["price"] for k, v in SERVICES_DB.items()}
MINS = {k: v["min"] for k, v in SERVICES_DB.items()}

# ---------------------------------------------------------------- 2. ข้อความต้องห้าม (ชุดทดสอบ 26 เคส + ปุ่มลัด)
CASES = json.loads((HERE / "e2e" / "cases.json").read_text(encoding="utf-8"))["cases"]
FORBIDDEN = [s["type"] for c in CASES for s in c["steps"] if "type" in s]
FORBIDDEN += [t for c in CASES for t in c.get("confirm", [])]
CHAT = (HERE / "web" / "components" / "Chat.tsx").read_text(encoding="utf-8")
FORBIDDEN += re.findall(r'key: "\w+", label: "[^"]*", text: "([^"]+)"', CHAT)
FORBIDDEN = sorted(set(FORBIDDEN))


def norm(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[\s\-.,!?:;\"'()/]+", "", s)
    s = re.sub(r"(นะคะ|นะครับ|ค่ะ|คะ|ครับผม|ครับ|คับ|จ้า|จ๊ะ)", "", s)
    return s


FORB_N = [norm(t) for t in FORBIDDEN]


def similarity(text: str) -> tuple[float, str]:
    """ความคล้ายสูงสุดกับข้อความต้องห้าม (นับว่ามีข้อความต้องห้ามอยู่ข้างในเป็น 1.0)"""
    n = norm(text)
    best, who = 0.0, ""
    for f, raw in zip(FORB_N, FORBIDDEN):
        r = 1.0 if (len(f) >= 8 and f in n) or (len(n) >= 8 and n in f) else SequenceMatcher(None, n, f).ratio()
        if r > best:
            best, who = r, raw
    return best, who


# ---------------------------------------------------------------- 3. ตัวช่วยสร้างข้อความ
TH_MONTH = ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน", "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]
TH_MON = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."]
EN_MONTH = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
TH_WEEKDAY = ["วันจันทร์", "วันอังคาร", "วันพุธ", "วันพฤหัสบดี", "วันศุกร์", "วันเสาร์", "วันอาทิตย์"]
PREFIX = ["", "", "", "สวัสดีค่ะ ", "สวัสดีครับ ", "รบกวนสอบถามค่ะ ", "ขอถามหน่อยครับ ", "แอดมินคะ ", "น้องสบายใจ ", "สอบถามหน่อยนะคะ ", "หวัดดีครับ "]
Q_END = ["คะ", "ครับ", "คะ?", "ครับ?", "", "จ๊ะ", " ครับผม", "นะคะ"]
S_END = ["ค่ะ", "ครับ", "นะคะ", "นะครับ", "", "จ้า"]
FIRST = ["สมชาย", "วิภา", "อรุณี", "กิตติ", "ณัฐวุฒิ", "พิมพ์ชนก", "ธนพล", "ศิริพร", "จิราพร", "อนุชา", "ปวีณา", "วรเชษฐ์", "สุดารัตน์",
         "ภาณุ", "กมลชนก", "ชัยวัฒน์", "รัชนี", "ธีรภัทร", "นันทนา", "เอกชัย", "พัชรา", "ศุภชัย", "ดวงใจ", "ประเสริฐ", "เบญจวรรณ",
         "ณัฐธิดา", "วีระ", "อัญชลี", "ธวัชชัย", "มาลัย", "สุนทร", "ลลิตา", "ปกรณ์", "ชุติมา", "บุญมี", "ทิพวรรณ", "ภูมิ", "แพรวา"]
LAST = ["ศรีสุข", "บุญมา", "แก้วกาญจนา", "ทองดี", "สายสุวรรณ", "มีสุข", "พงษ์ไพบูลย์", "วงศ์ใหญ่", "จันทร์เพ็ญ", "ปัญญาดี",
        "รุ่งเรือง", "เพชรงาม", "สุขสวัสดิ์", "อินทรวงศ์", "คำแก้ว", "ธนากร", "ชัยมงคล", "ศรีวิไล", "บัวขาว", "ดวงดี"]
EN_FIRST = ["John", "Emma", "Liam", "Sophie", "Daniel", "Mia", "Lucas", "Hannah", "Ken", "Yuki", "Oliver", "Chloe"]
EN_LAST = ["Miller", "Brown", "Tanaka", "Schmidt", "Wilson", "Garcia", "Lee", "Martin", "Dubois", "Novak"]
NOT_OFFERED = [("ทำเล็บ", "เล็บ"), ("ตัดผม", "ผม"), ("ทำสีผม", "สีผม"), ("สครับผิว", "สครับ"), ("ซาวน่า", "ซาวน่า"),
               ("แว็กซ์ขน", "แว็กซ์"), ("ต่อขนตา", "ขนตา"), ("นวดหินร้อน", "หินร้อน"), ("นวดสวีดิช", "สวีดิช"),
               ("ฝังเข็ม", "ฝังเข็ม"), ("อบไอน้ำ", "ไอน้ำ"), ("ทรีตเมนต์หน้าใส", "ทรีตเมนต์"), ("โยคะ", "โยคะ"),
               ("นวดแผนจีนกัวซา", "กัวซา"), ("พอกโคลน", "โคลน"), ("สปาเท้า", "สปาเท้า")]
NO = ["ไม่มี", "ขออภัย"]
REFUSE_TIME = ["ไม่ได้", "ปิด", "ไม่ทัน", "ไม่สามารถ", "ไม่รับ", "ไม่ว่าง"]


def money(v: float) -> list[str]:
    """ตัวเลขเงินที่ยอมรับ (382.50 -> 382 หรือ 383 · 1050 -> 1050 หรือ 1,050)"""
    if abs(v - round(v)) < 1e-9:
        v = int(round(v))
        return sorted({str(v), f"{v:,}"})
    return [str(math.floor(v)), str(math.ceil(v))]


def H(v) -> list[str]:  # one-of
    return money(v) if isinstance(v, (int, float)) else v


def en_clock(h: int) -> list[str]:
    hh = h - 12 if h > 12 else h
    suf = "pm" if h >= 12 else "am"
    return [str(h), f"{hh} {suf}", f"{hh}{suf}", f"{hh}:00 {suf}", f"{hh}:00{suf}", f"{hh} p.m" if suf == "pm" else f"{hh} a.m"]


def E(has=None, not_=None, lang="th", booking="none", must=""):
    has = [h if isinstance(h, list) and len(h) > 1 else (h[0] if isinstance(h, list) else h) for h in (has or [])]
    parts = []
    for h in has:
        parts.append(" หรือ ".join(h) if isinstance(h, list) else h)
    auto = ("ต้องมี " + " และ ".join(parts)) if parts else ""
    if not_:
        auto += (" · " if auto else "") + "ห้ามมี " + ", ".join(t.removeprefix("re:") for t in not_)
    if isinstance(booking, dict):
        b = booking
        auto += (" · " if auto else "") + f"ต้องมีแท็กจอง ชื่อ {b['customer_name']} เบอร์ {b['phone']} บริการ {b['service']} เวลา {b['booking_time']}"
    else:
        auto += (" · " if auto else "") + "ต้องยังไม่มีแท็กจอง"
    auto += f" · ตอบภาษา{'ไทย' if lang == 'th' else 'อังกฤษ'}"
    return {"has": has, "not": not_ or [], "lang": lang, "booking": booking, "no_markdown": True,
            "must": (must + " · " if must else "") + auto}


def T(user, **kw):
    # เว้นวรรคระหว่างตัวเลขกับอักษรไทย ("ขอ6 ธ.ค." -> "ขอ 6 ธ.ค.") ให้อ่านเหมือนคนพิมพ์
    user = re.sub(r"(?<=[ก-๙])(?=\d)|(?<=\d)(?=[ก-๙])", " ", user)
    return {"user": user, "expect": E(**kw)}


class Ctx:
    """บริบทของหนึ่งบท: random + วันเวลาปัจจุบันที่สุ่มให้บทนี้"""

    def __init__(self, rng: random.Random):
        self.r = rng
        d0 = datetime(2026, 11, 20)
        day = d0 + timedelta(days=rng.randint(0, 130))
        hour = rng.randint(9, 21) if rng.random() < 0.75 else rng.choice([0, 1, 6, 7, 8, 22, 23])
        self.now = day.replace(hour=hour, minute=rng.randint(0, 59))

    # ข้อความสั้น ๆ
    def q(self, core):
        return (self.r.choice(PREFIX) + core + self.r.choice(Q_END)).strip()

    def s(self, core):
        return (core + self.r.choice(S_END)).strip()

    def pick(self, xs):
        return self.r.choice(xs)

    def alias(self, svc):
        return self.pick(ALIASES[svc][0])

    def ealias(self, svc):
        return self.pick(ALIASES[svc][1])

    # ลูกค้า + วันเวลาจอง
    def person(self, en=False):
        if en:
            f, l = self.pick(EN_FIRST), self.pick(EN_LAST)
        else:
            f, l = self.pick(FIRST), self.pick(LAST)
        full = f"{f} {l}" if self.r.random() < 0.7 else f
        d = self.pick(["08", "09", "06"]) + "".join(str(self.r.randint(0, 9)) for _ in range(8))
        style = self.r.randint(0, 2)
        shown = d if style == 0 else (f"{d[:3]}-{d[3:6]}-{d[6:]}" if style == 1 else f"{d[:3]} {d[3:6]} {d[6:]}")
        return {"full": full, "first": f, "digits": d, "shown": shown}

    def slot(self, svc=None, bad=False):
        d = self.now.date() + timedelta(days=self.r.randint(1, 20))
        if bad:
            h, m = self.pick([(7, 0), (8, 0), (8, 30), (9, 0), (9, 30), (21, 30), (22, 0), (22, 30), (23, 0), (0, 0), (1, 0)])
        else:
            last = 20 if svc and MINS[svc] >= 120 else LAST_H
            h = self.r.randint(OPEN_H, last)
            m = 0 if h == last else self.pick([0, 0, 30])
        return datetime(d.year, d.month, d.day, h, m)

    def date_th(self, dt: datetime):
        delta = (dt.date() - self.now.date()).days
        opts = [f"วันที่ {dt.day} {TH_MONTH[dt.month - 1]}", f"{dt.day} {TH_MON[dt.month - 1]}", f"{dt.day}/{dt.month}",
                f"{dt.day} {TH_MONTH[dt.month - 1]} {dt.year + 543}", f"{dt:%Y-%m-%d}"]
        if delta == 1:
            opts += ["พรุ่งนี้", "พรุ่งนี้", "วันพรุ่งนี้"]
        if delta == 2:
            opts += ["มะรืนนี้", "มะรืน"]
        return self.pick(opts)

    def time_th(self, dt: datetime):
        h, m = dt.hour, dt.minute
        opts = [f"{h:02d}:{m:02d} น.", f"{h}.{m:02d} น.", f"{h:02d}:{m:02d}"]
        half = " ครึ่ง" if m == 30 else ""
        if m in (0, 30):
            if 6 <= h <= 11:
                opts.append(f"{h} โมงเช้า{half}" if not half else f"{h} โมงครึ่ง")
            elif h == 12:
                opts.append("เที่ยง" + half.strip())
            elif h == 13:
                opts.append("บ่ายโมง" + half.strip())
            elif h in (14, 15):
                opts.append(f"บ่าย {h - 12} โมง{half.strip()}")
            elif 16 <= h <= 18:
                opts.append(f"{h - 12} โมงเย็น{half.strip()}")
            elif 19 <= h <= 23:
                opts.append(f"{h - 18} ทุ่ม{half.strip()}")
            elif h == 0 and m == 0:
                opts.append("เที่ยงคืน")
            elif 1 <= h <= 5:
                opts.append(f"ตี {h}{half.strip()}")
        return self.pick(opts)

    def when_th(self, dt):
        t = self.time_th(dt)
        joiner = self.pick([" เวลา ", " ", " ตอน "])
        return f"{self.date_th(dt)}{joiner}{t}"

    def when_en(self, dt):
        h = dt.hour % 12 or 12
        ap = "am" if dt.hour < 12 else "pm"
        t = f"{h}:{dt.minute:02d} {ap}" if dt.minute else f"{h} {ap}"
        d = self.pick([f"{EN_MONTH[dt.month - 1]} {dt.day}", f"{dt.day} {EN_MONTH[dt.month - 1]}", f"{dt:%Y-%m-%d}"])
        if (dt.date() - self.now.date()).days == 1 and self.r.random() < 0.5:
            d = "tomorrow"
        return f"{d} at {t}"

    @staticmethod
    def tag(p, svc, dt):
        return {"customer_name": p["full"], "name_must_contain": p["first"], "phone": p["digits"],
                "service": svc, "booking_time": f"{dt:%Y-%m-%d %H:%M}"}


# ---------------------------------------------------------------- 4. ตัวสร้างบทสนทนาแต่ละชนิด
def g_info(c: Ctx):
    k = c.pick(["hours", "last", "addr", "addr2", "phone", "line", "park", "pay_pp", "pay_cash", "pay_cc", "cancel",
                "resched", "early", "fever", "preg", "open_now", "list", "promo"])
    if k == "hours":
        core = c.pick(["ร้านเปิดให้บริการกี่โมง", "ปิดร้านกี่โมง", "เวลาทำการของร้านเป็นยังไง", "เปิดทุกวันไหม ปิดกี่โมง", "วันอาทิตย์เปิดไหม เปิดถึงกี่โมง"])
        return [T(c.q(core), has=[["10"], ["22", "4 ทุ่ม"]])]
    if k == "last":
        core = c.pick(["รอบสุดท้ายที่รับลูกค้าคือกี่โมง", "ถ้าจะไปนวดหลังเลิกงาน ต้องไปไม่เกินกี่โมง", "คิวสุดท้ายของวันกี่โมง", "เข้าร้านช้าสุดได้ถึงกี่โมง"])
        return [T(c.q(core), has=[["21", "3 ทุ่ม"]])]
    if k == "addr":
        core = c.pick(["ร้านตั้งอยู่ตรงไหน", "ขอที่อยู่ร้านหน่อย", "ร้านอยู่ถนนอะไร", "จะไปร้านต้องไปทางไหน อยู่ซอยไหน"])
        return [T(c.q(core), has=["นิมมาน"])]
    if k == "addr2":
        core = c.pick(["ร้านอยู่กรุงเทพหรือเปล่า", "ร้านมีสาขาที่ภูเก็ตไหม", "อยู่อำเภอไหน", "รหัสไปรษณีย์ของร้านคืออะไร"])
        return [T(c.q(core), has=[["เชียงใหม่", "50200"]])]
    if k == "phone":
        core = c.pick(["ติดต่อร้านทางโทรศัพท์เบอร์อะไร", "มีเบอร์ให้โทรไปสอบถามไหม", "เบอร์ร้านคือเบอร์อะไร", "โทรหาร้านได้ที่เบอร์ไหน"])
        return [T(c.q(core), has=["053-123-456"])]
    if k == "line":
        core = c.pick(["ร้านมีไลน์ไหม", "แอดไลน์ร้านได้ที่ไอดีอะไร", "ขอไลน์ร้านหน่อย", "ทักไลน์ร้านได้ไหม ไอดีอะไร"])
        return [T(c.q(core), has=["sabaijai"])]
    if k == "park":
        core = c.pick(["ขับรถไปจะมีที่จอดไหม", "ที่จอดรถหน้าร้านจอดได้กี่คัน", "เอารถไปจอดตรงไหนได้บ้าง", "ร้านมีลานจอดรถหรือเปล่า"])
        return [T(c.q(core), has=["4"])]
    if k == "pay_pp":
        core = c.pick(["สแกนจ่ายพร้อมเพย์ได้ไหม", "โอนจ่ายผ่านพร้อมเพย์ได้หรือเปล่า", "จ่ายด้วย QR พร้อมเพย์ได้ไหม"])
        return [T(c.q(core), has=["พร้อมเพย์"])]
    if k == "pay_cash":
        core = c.pick(["ร้านรับชำระเงินแบบไหนบ้าง", "จ่ายได้กี่ช่องทาง", "จ่ายเงินสดได้ใช่ไหม"])
        return [T(c.q(core), has=["เงินสด"])]
    if k == "pay_cc":
        core = c.pick(["รูดบัตรได้หรือเปล่า", "ใช้บัตร visa จ่ายได้ไหม", "ไม่มีเงินสด รูดการ์ดได้ไหม"])
        return [T(c.q(core), has=[["บัตรเครดิต", "บัตร"]])]
    if k == "cancel":
        core = c.pick(["จองแล้วยกเลิกได้ไหม ต้องบอกก่อนนานแค่ไหน", "ถ้าไปไม่ได้ ต้องแจ้งร้านก่อนกี่ชั่วโมง", "นโยบายยกเลิกการจองเป็นยังไง"])
        return [T(c.q(core), has=["3"])]
    if k == "resched":
        core = c.pick(["อยากเลื่อนนัดต้องแจ้งก่อนกี่ชั่วโมง", "เลื่อนวันนวดได้ไหม ต้องบอกล่วงหน้าเท่าไหร่", "ขอเปลี่ยนเวลานัดต้องแจ้งก่อนนานไหม"])
        return [T(c.q(core), has=["3"])]
    if k == "early":
        core = c.pick(["ต้องไปถึงร้านก่อนเวลานัดกี่นาที", "ควรมาก่อนนัดนานแค่ไหน", "มีกฎว่าต้องมาก่อนเวลาไหม"])
        return [T(c.q(core), has=["10"])]
    if k == "fever":
        core = c.pick(["ตอนนี้มีไข้อ่อน ๆ ไปนวดได้ไหม", "ตัวรุม ๆ เป็นไข้ นวดแล้วจะหายไหม", "ไข้ 38 องศา นวดได้หรือเปล่า"])
        return [T(c.q(core), has=[["ไม่แนะนำ", "แพทย์", "หาย", "งด"]])]
    if k == "preg":
        core = c.pick(["ท้องได้ 6 สัปดาห์ มานวดได้ไหม", "เพิ่งรู้ว่าตั้งท้องเดือนแรก นวดอันตรายไหม", "คนท้องอ่อน ๆ นวดเท้าได้หรือเปล่า"])
        return [T(c.q(core), has=[["ไม่แนะนำ", "แพทย์"]])]
    if k == "open_now":
        core = c.pick(["ตอนนี้ร้านเปิดอยู่ไหม", "ตอนนี้ยังเปิดอยู่หรือเปล่า", "ถ้าไปเดี๋ยวนี้เลยร้านเปิดไหม"])
        h = c.now.hour
        if OPEN_H <= h < LAST_H:
            return [T(c.q(core), has=[["เปิดอยู่", "ยังเปิด", "เปิดให้บริการ", "22", "21"]], must=f"ตอนนี้ {c.now:%H:%M} ร้านเปิดอยู่")]
        if LAST_H <= h < CLOSE_H:
            return [T(c.q(core), has=[["21", "รอบสุดท้าย"]], must=f"ตอนนี้ {c.now:%H:%M} เลยรอบสุดท้ายแล้ว")]
        return [T(c.q(core), has=[["ปิดแล้ว", "ปิดอยู่", "ยังไม่เปิด", "ปิดทำการ", "ปิดค่ะ"], "10"], must=f"ตอนนี้ {c.now:%H:%M} ร้านปิด")]
    if k == "list":
        core = c.pick(["ร้านมีนวดแบบไหนให้เลือกบ้าง", "มีบริการอะไรบ้าง", "เมนูนวดของร้านมีอะไรบ้าง", "นอกจากนวดไทยมีอย่างอื่นไหม"])
        return [T(c.q(core), has=["นวดน้ำมันอโรมา", "นวดเท้าสะท้อนจุด", "ประคบสมุนไพร"])]
    core = c.pick(["ช่วงนี้ร้านจัดโปรอะไรอยู่บ้าง", "มีโปรลดราคาไหม", "มีดีลพิเศษอะไรบ้าง", "ส่วนลดของร้านมีแบบไหนบ้าง"])
    return [T(c.q(core), has=["10%", "15%"])]


def g_price(c: Ctx):
    k = c.pick(["one", "one", "one", "dur", "max", "diff", "sum", "group", "budget", "rec", "rec", "doctor", "detail"])
    if k == "one":
        s = c.pick(SVC)
        core = c.pick(["{a} กี่บาท", "{a} ราคาเท่าไร", "ขอทราบราคา{a}", "{a} คิดค่าบริการเท่าไหร่", "อยากรู้ราคา{a}", "{a} ตกเท่าไหร่"]).format(a=c.alias(s))
        return [T(c.q(core), has=[money(PRICE[s])], not_=["re:ลด"])]
    if k == "dur":
        s = c.pick(SVC)
        core = c.pick(["{a} ใช้เวลากี่นาที", "{a} นวดนานเท่าไหร่", "{a} กี่นาทีเสร็จ"]).format(a=c.alias(s))
        return [T(c.q(core), has=[[str(MINS[s])] + (["ชั่วโมง"] if MINS[s] == 60 else []) + (["2 ชั่วโมง"] if MINS[s] == 120 else [])])]
    if k == "max":
        core = c.pick(["บริการที่แพงที่สุดคืออะไร", "นวดอะไรราคาสูงสุด", "อันไหนราคาแพงสุด"])
        return [T(c.q(core), has=["600"])]
    if k == "diff":
        a, b = c.r.sample([s for s in SVC], 2)
        if PRICE[a] == PRICE[b]:
            core = c.pick(["{a} กับ{b} ราคาต่างกันไหม", "{a} แพงกว่า{b}หรือเปล่า"]).format(a=c.alias(a), b=c.alias(b))
            return [T(c.q(core), has=[money(PRICE[a]), ["เท่ากัน", "เท่า", "ราคาเดียวกัน"]])]
        hi, lo = (a, b) if PRICE[a] > PRICE[b] else (b, a)
        core = c.pick(["{a} กับ{b} ต่างกันกี่บาท", "{a} แพงกว่า{b}เท่าไหร่", "{a} เทียบกับ{b} ราคาห่างกันเท่าไร"]).format(a=c.alias(hi), b=c.alias(lo))
        return [T(c.q(core), has=[money(PRICE[hi] - PRICE[lo])])]
    if k == "sum":
        a, b = c.r.sample(SVC, 2)
        core = c.pick(["ถ้าทำ{a}ต่อด้วย{b} รวมเท่าไหร่", "{a} บวก{b} จ่ายทั้งหมดกี่บาท", "อยากได้ทั้ง{a}และ{b} ต้องเตรียมเงินเท่าไร"]).format(a=c.alias(a), b=c.alias(b))
        return [T(c.q(core), has=[money(PRICE[a] + PRICE[b])])]
    if k == "group":
        s, n = c.pick(SVC), c.r.randint(2, 5)
        core = c.pick(["มากัน {n} คน ทุกคนเอา{a} รวมกี่บาท", "พาเพื่อนไป {n} คน {a}คนละครั้ง ทั้งหมดเท่าไหร่", "ครอบครัว {n} คนจะ{a} ค่าใช้จ่ายรวมเท่าไร"]).format(n=n, a=c.alias(s))
        return [T(c.q(core), has=[money(PRICE[s] * n)])]
    if k == "budget":
        b = c.pick([260, 280, 320, 400, 460, 520])
        ok = [s for s in SVC if PRICE[s] <= b]
        bad = [s for s in SVC if PRICE[s] > b]
        core = c.pick(["มีงบ {b} บาท นวดอะไรได้บ้าง", "งบไม่เกิน {b} เลือกอะไรได้", "ถ้ามีเงิน {b} บาท แนะนำอะไรดี"]).format(b=b)
        return [T(c.q(core), has=[ok], not_=[f"re:{bad[0]}[^\\n]{{0,25}}?{PRICE[bad[0]]}"] if bad else [],
                  must=f"แนะนำได้เฉพาะบริการที่ราคาไม่เกิน {b} บาท")]
    if k == "rec":
        core, svc = c.pick([
            ("ยืนขายของทั้งวัน เมื่อยเท้ามาก ควรนวดแบบไหน", "นวดเท้าสะท้อนจุด"),
            ("เดินเที่ยวมาทั้งวัน ปวดฝ่าเท้า มีอะไรช่วยได้", "นวดเท้าสะท้อนจุด"),
            ("เครียดงาน ปวดหัวตึบ ๆ ทุกวัน แนะนำหน่อย", "นวดหน้าและศีรษะ"),
            ("นอนไม่ค่อยหลับ อยากผ่อนคลายด้วยกลิ่นหอม ๆ", "นวดน้ำมันอโรมา"),
            ("นั่งหน้าคอมทั้งวัน คอแข็งไปหมด", "นวดคอบ่าไหล่"),
            ("ชอบกลิ่นสมุนไพร อยากได้นวดแบบอุ่น ๆ", "ประคบสมุนไพร"),
            ("มีเวลาแค่ครึ่งชั่วโมง อยากนวดคลายบ่า", "นวดคอบ่าไหล่"),
            ("อยากนวดยาว ๆ ทั้งตัวแบบไทยเต็มที่", "นวดไทยแผนโบราณ 2 ชั่วโมง"),
        ])
        return [T(c.q(core), has=[svc] if svc != "นวดไทยแผนโบราณ 2 ชั่วโมง" else [["2 ชั่วโมง", "120"]])]
    if k == "doctor":
        core = c.pick(["ปวดหลังร้าวลงขา ขาชาด้วย นวดได้ไหม", "เพิ่งผ่าตัดหลังมาเดือนก่อน นวดหลังได้ไหม", "ข้อเท้าแพลงบวมแดง นวดเท้าช่วยได้ไหม", "เจ็บหน้าอกเวลานวด เป็นอะไรหรือเปล่า"])
        return [T(c.q(core), has=["แพทย์"], must="ไม่วินิจฉัยโรค ให้แนะนำพบแพทย์")]
    s, kw = c.pick([("นวดน้ำมันอโรมา", ["ลาเวนเดอร์", "ตะไคร้", "มะลิ"]), ("ประคบสมุนไพร", ["ไพล", "ขมิ้น", "ตะไคร้"])])
    core = c.pick(["{a} ใช้อะไรบ้าง", "{a} มีกลิ่นอะไรบ้าง", "{a} เป็นยังไง ใช้สมุนไพรอะไร"]).format(a=c.alias(s))
    return [T(c.q(core), has=[kw])]


def g_discount(c: Ctx):
    k = c.pick(["student", "student", "weekday", "weekday", "package", "students", "promo10"])
    if k == "student":
        s = c.pick(SVC)
        core = c.pick(["เป็นนักศึกษา {a} จ่ายเท่าไหร่", "มีบัตรนักศึกษา ถ้า{a}จะเหลือกี่บาท", "นักศึกษาทำ{a} ลดแล้วเหลือเท่าไร", "{a} ราคานักศึกษาเท่าไหร่"]).format(a=c.alias(s))
        return [T(c.q(core), has=[money(PRICE[s] * 0.85)], must=f"{PRICE[s]} ลด 15%")]
    if k == "students":
        s, n = c.pick(SVC), c.r.randint(2, 4)
        core = c.pick(["นักศึกษา {n} คน {a}คนละครั้ง รวมเท่าไหร่", "พวกเราเป็นนักศึกษา {n} คน จะ{a} จ่ายรวมกี่บาท"]).format(n=n, a=c.alias(s))
        return [T(c.q(core), has=[money(PRICE[s] * 0.85 * n)], must=f"({PRICE[s]} ลด 15%) × {n}")]
    if k == "package":
        core = c.pick(["แพ็กเกจ 5 ครั้งได้อะไรแถม", "ซื้อคอร์สนวดหลายครั้งมีของแถมไหม", "ถ้าซื้อเป็นแพ็กเกจจะคุ้มกว่าไหม"])
        return [T(c.q(core), has=["5", "นวดเท้า"])]
    if k == "promo10":
        core = c.pick(["ส่วนลด 10% ใช้ได้วันไหนบ้าง", "โปรลด 10 เปอร์เซ็นต์มีเงื่อนไขอะไร", "ลด 10% ต้องมาก่อนกี่โมง"])
        return [T(c.q(core), has=["14", ["จันทร์", "พฤหัส"]])]
    s = c.pick(SVC)
    wd = c.r.randint(0, 6)
    h = c.pick([10, 11, 12, 13, 15, 16, 18])
    t = c.time_th(datetime(2026, 1, 1, h, 0))
    core = c.pick(["ถ้ามา{d} {t} {a} ได้ลดไหม จ่ายเท่าไหร่", "{d} {t} อยาก{a} ได้ส่วนลดหรือเปล่า เหลือกี่บาท", "จะไป{a}{d} {t} ต้องจ่ายเท่าไร"]).format(d=TH_WEEKDAY[wd], t=t, a=c.alias(s))
    if wd <= 3 and h < 14:
        return [T(c.q(core), has=[money(PRICE[s] * 0.9)], must=f"{TH_WEEKDAY[wd]} ก่อน 14:00 ได้ลด 10% จาก {PRICE[s]}")]
    return [T(c.q(core), has=[money(PRICE[s])], not_=money(PRICE[s] * 0.9), must=f"{TH_WEEKDAY[wd]} {h}:00 ไม่เข้าเงื่อนไขลด 10% ต้องจ่ายเต็ม {PRICE[s]}")]


def g_not_offered(c: Ctx):
    svc, kw = c.pick(NOT_OFFERED)
    core = c.pick(["ร้านรับ{s}ด้วยไหม", "มี{s}หรือเปล่า", "อยาก{s} ทำที่ร้านได้ไหม", "{s} ราคาเท่าไหร่", "ขอจอง{s}พรุ่งนี้ได้ไหม", "ร้านมีบริการ{s}รึเปล่า"]).format(s=svc)
    return [T(c.q(core), has=[NO], not_=[f"re:{kw}[^\\n]{{0,15}}?\\d{{2,4}}\\s*บาท"], must=f"ร้านไม่มีบริการ{svc} ห้ามแต่งราคา")]


OFFTOPIC = [
    ("สอนทำผัดไทยหน่อย", "re:ซอสมะขาม|เส้นจันท์|วิธีทำ|ส่วนผสม"),
    ("แกงเขียวหวานใส่อะไรบ้าง", "re:พริกแกง|กะทิ|วิธีทำ|ส่วนผสม"),
    ("ช่วยแก้สมการ x^2-5x+6=0 ให้หน่อย", "re:x\\s*=\\s*[23]"),
    ("ช่วยเขียนโค้ด python เรียงตัวเลขให้หน่อย", "re:def |sorted\\(|import "),
    ("ผลบอลเมื่อคืนใครชนะ", "re:\\d+\\s*-\\s*\\d+"),
    ("หุ้นตัวไหนน่าซื้อตอนนี้", "re:แนะนำหุ้น|ซื้อหุ้น"),
    ("หวยงวดนี้ออกเลขอะไร", "re:เลขเด็ด|รางวัลที่ 1"),
    ("ช่วยแปลกลอนภาษาอังกฤษเป็นไทยหน่อย", "re:แปลว่า"),
    ("พรุ่งนี้เชียงใหม่ฝนตกไหม", "re:พยากรณ์|ฝนตก\\s*\\d+%"),
    ("แนะนำร้านข้าวซอยอร่อย ๆ แถวนิมมานหน่อย", "re:ข้าวซอย[^\\n]{0,20}(ร้าน|เจ้า)"),
    ("ช่วยเขียนเรียงความเรื่องสิ่งแวดล้อม 1 หน้า", "re:สิ่งแวดล้อมเป็น|มลพิษ"),
    ("ไปดอยสุเทพยังไงดี", "re:รถแดง|ขึ้นดอย|ทางขึ้น"),
    ("วิธีลดน้ำหนักเร็ว ๆ ทำยังไง", "re:แคลอรี|ออกกำลังกาย|ควบคุมอาหาร"),
    ("แต่งกลอนวันแม่ให้หน่อย", "re:แม่[^\\n]{0,10}(รัก|พระคุณ)"),
    ("ราคาทองวันนี้เท่าไหร่", "re:บาทละ|ทองคำแท่ง"),
    ("ช่วยคิดชื่อร้านกาแฟเปิดใหม่ให้หน่อย", "re:คาเฟ่|coffee"),
]


def g_offtopic(c: Ctx):
    core, bad = c.pick(OFFTOPIC)
    return [T(c.q(core), has=[["ขออภัย", "ค่ะ"], ["นวด", "ร้าน"]], not_=[bad], must="ปฏิเสธสุภาพแล้วชวนกลับมาเรื่องนวด")]


def g_english(c: Ctx):
    k = c.pick(["price", "price", "hours", "last", "addr", "phone", "park", "pay", "student", "promo", "nails", "offtopic", "cancel", "dur"])
    if k == "price":
        s = c.pick(SVC)
        q = c.pick(["What's the price of {a}?", "How much do you charge for {a}?", "Could you tell me the cost of {a}?", "Price for {a}, please?"]).format(a=c.ealias(s))
        return [T(q, has=[money(PRICE[s])], lang="en")]
    if k == "dur":
        s = c.pick(SVC)
        q = c.pick(["How long is {a}?", "How many minutes does {a} take?"]).format(a=c.ealias(s))
        return [T(q, has=[[str(MINS[s]), "hour"]], lang="en")]
    if k == "hours":
        q = c.pick(["What are your opening hours?", "When do you close today?", "Are you open on Sundays? Until what time?", "What time does the shop open in the morning?"])
        return [T(q, has=[en_clock(10)[:1] + ["10 am", "10am", "10:00"], en_clock(22)], lang="en")]
    if k == "last":
        q = c.pick(["What's the latest time I can walk in?", "When is your last booking slot?", "Until what time do you accept customers?"])
        return [T(q, has=[en_clock(21)], lang="en")]
    if k == "addr":
        q = c.pick(["Where is the shop?", "What's your address?", "Which road are you on?", "Are you in Chiang Mai?"])
        return [T(q, has=[["nimman", "chiang mai"]], lang="en")]
    if k == "phone":
        q = c.pick(["What's your phone number?", "How can I call the shop?", "Do you have a contact number or LINE?"])
        return [T(q, has=[["053-123-456", "sabaijai"]], lang="en")]
    if k == "park":
        q = c.pick(["Is there parking at the shop?", "Can I park my car there?", "How many parking spaces do you have?"])
        return [T(q, has=["4"], lang="en")]
    if k == "pay":
        q = c.pick(["Can I pay by credit card?", "Do you accept PromptPay?", "What payment methods do you take?"])
        return [T(q, has=[["credit", "promptpay", "cash"]], lang="en")]
    if k == "student":
        s = c.pick(SVC)
        q = c.pick(["I'm a student. How much would {a} be?", "Is there a student price for {a}?"]).format(a=c.ealias(s))
        return [T(q, has=[money(PRICE[s] * 0.85)], lang="en")]
    if k == "promo":
        q = c.pick(["Do you have any promotions right now?", "Any discounts available?", "Are there special deals this month?"])
        return [T(q, has=[["10%", "15%"]], lang="en")]
    if k == "cancel":
        q = c.pick(["How early must I cancel a booking?", "Can I reschedule? How much notice do you need?"])
        return [T(q, has=["3"], lang="en")]
    if k == "nails":
        svc, kw = c.pick([("manicure", "manicure"), ("haircut", "haircut"), ("hot stone massage", "hot stone"), ("sauna", "sauna"), ("eyelash extension", "eyelash"), ("waxing", "wax")])
        q = c.pick(["Do you offer {s}?", "How much is a {s} at your shop?", "Can I book a {s}?"]).format(s=svc)
        return [T(q, has=[["not", "sorry", "unfortunately", "only"]], not_=[f"re:{kw}[^\\n]{{0,20}}?\\d{{2,4}}\\s*(baht|thb)"], lang="en", must=f"ร้านไม่มี {svc}")]
    q, bad = c.pick([("Can you give me a recipe for green curry?", "re:coconut milk|curry paste"),
                     ("Who won the football match last night?", "re:\\d+\\s*-\\s*\\d+"),
                     ("Write me a python script to sort a list.", "re:def |sorted\\("),
                     ("What's the weather in Bangkok tomorrow?", "re:forecast|°c")])
    return [T(q, has=[["sorry", "only", "unfortunately"], "massage"], not_=[bad], lang="en", must="ปฏิเสธสุภาพเป็นภาษาอังกฤษ")]


def g_followup(c: Ctx):
    k = c.pick(["student", "name", "late", "lang_en", "lang_th", "package", "group_park", "compare", "budget_mem", "promo_calc"])
    if k == "student":
        s = c.pick(SVC)
        return [T(c.q(c.pick(["{a} เท่าไหร่", "สนใจ{a} ราคาเท่าไร"]).format(a=c.alias(s))), has=[money(PRICE[s])]),
                T(c.q(c.pick(["ถ้ามีบัตรนักศึกษาล่ะ ลดเหลือเท่าไหร่", "เราเรียนมหาลัยอยู่ ลดได้อีกไหม", "นักศึกษาได้ราคาพิเศษหรือเปล่า"])), has=[money(PRICE[s] * 0.85)])]
    if k == "name":
        f = c.pick(FIRST)
        sym, svc = c.pick([("ยืนทั้งวันจนเท้าระบม", "นวดเท้าสะท้อนจุด"), ("ปวดหัวจากความเครียด", "นวดหน้าและศีรษะ"), ("บ่าตึงจากการนั่งเรียนออนไลน์", "นวดคอบ่าไหล่"), ("อยากหลับสบายผ่อนคลาย", "นวดน้ำมันอโรมา")])
        return [T(c.s(f"สวัสดี เราชื่อ{f} ช่วงนี้{sym}"), has=[[svc, "นวด"]]),
                T(c.q(c.pick(["ควรเลือกนวดแบบไหน", "มีบริการไหนเหมาะกับเราบ้าง", "อันไหนตรงกับอาการนี้"])), has=[svc]),
                T(c.q(c.pick(["อันนั้นราคาเท่าไหร่ แล้วเราบอกชื่อไว้ว่าอะไรนะ", "ราคาเท่าไร แล้วยังจำชื่อเราได้อยู่ไหม"])), has=[money(PRICE[svc]), f])]
    if k == "late":
        bad = c.pick([(21, 30, "3 ทุ่มครึ่ง"), (22, 0, "4 ทุ่ม"), (23, 30, "5 ทุ่มครึ่ง")])
        good = c.pick([(19, 0, "1 ทุ่ม"), (20, 0, "2 ทุ่ม"), (20, 30, "2 ทุ่มครึ่ง"), (18, 0, "6 โมงเย็น")])
        return [T(c.q(c.pick(["คืนนี้ {t} ไปนวดได้ไหม", "เลิกงานดึก ไปถึง {t} ยังรับอยู่หรือเปล่า"]).format(t=bad[2])), has=[REFUSE_TIME + ["21"]]),
                T(c.q(c.pick(["ถ้าเป็น {t} ล่ะ", "ขยับมาเป็น {t} พอไหวไหม"]).format(t=good[2])), has=[["ได้", "ทัน", "ว่าง", "รับ"]], not_=["ไม่ทัน", "ไม่ได้"])]
    if k == "lang_en":
        s = c.pick(SVC)
        return [T(c.q(c.pick(["{a} ราคาเท่าไหร่", "{a} กี่บาท"]).format(a=c.alias(s))), has=[money(PRICE[s])]),
                T(c.pick(["Sorry, my Thai friend asked for me. Is there parking?", "Thanks! And where exactly is the shop?", "Great. Can I pay by card?"]),
                  has=[["4", "nimman", "chiang mai", "credit", "card"]], lang="en")]
    if k == "lang_th":
        s = c.pick(SVC)
        return [T(c.pick(["Hi, how long is {a}?", "Hello! What does {a} cost?"]).format(a=c.ealias(s)), has=[[str(PRICE[s]), str(MINS[s]), "hour"]], lang="en"),
                T(c.q(c.pick(["ขอเบอร์ติดต่อร้านด้วย", "แล้วรอบสุดท้ายกี่โมง", "ร้านปิดกี่โมง"])), has=[["053-123-456", "21", "22"]])]
    if k == "package":
        return [T(c.q(c.pick(["ซื้อแพ็กเกจ 5 ครั้งได้แถมอะไร", "ถ้าซื้อคอร์ส 5 ครั้งมีของแถมไหม"])), has=["นวดเท้า"]),
                T(c.q(c.pick(["บริการที่แถมนั้นปกติขายเท่าไหร่", "ของแถมนั้นถ้าซื้อเองกี่บาท"])), has=["300"]),
                T(c.q(c.pick(["แล้วมันใช้เวลานวดกี่นาที", "อันที่แถมนวดนานไหม"])), has=["45"])]
    if k == "group_park":
        n, s = c.r.randint(2, 4), c.pick(SVC)
        return [T(c.s(c.pick(["จะพาแม่กับพี่สาวไปด้วย รวม {n} คน", "ไปกันเป็นกลุ่ม {n} คน"]).format(n=n)), has=[["ยินดี", "ได้", "ค่ะ"]]),
                T(c.q(c.pick(["ถ้าทุกคนเลือก{a} รวมเท่าไหร่", "เอา{a}ทุกคน ทั้งหมดกี่บาท"]).format(a=c.alias(s))), has=[money(PRICE[s] * n)]),
                T(c.q(c.pick(["เอารถไป 2 คัน จอดพอไหม", "มีที่จอดให้รถสองคันหรือเปล่า"])), has=["4"])]
    if k == "compare":
        a, b = c.pick([("นวดเท้าสะท้อนจุด", "นวดหน้าและศีรษะ"), ("นวดคอบ่าไหล่", "นวดเท้าสะท้อนจุด"), ("ประคบสมุนไพร", "นวดแก้ปวดหลัง"), ("นวดน้ำมันอโรมา", "ประคบสมุนไพร")])
        longer = a if MINS[a] > MINS[b] else b
        cheaper = a if PRICE[a] < PRICE[b] else b
        t1 = T(c.q(c.pick(["{a} กับ{b} ต่างกันยังไง", "ลังเลระหว่าง{a}กับ{b}"]).format(a=c.alias(a), b=c.alias(b))), has=[money(PRICE[a]), money(PRICE[b])])
        if MINS[a] != MINS[b]:
            t2 = T(c.q(c.pick(["อันไหนนวดนานกว่ากัน", "ตัวไหนใช้เวลามากกว่า"])), has=[longer, str(MINS[longer])])
        else:
            t2 = T(c.q(c.pick(["อันไหนถูกกว่ากัน", "ตัวไหนประหยัดกว่า"])), has=[cheaper, money(PRICE[cheaper])])
        return [t1, t2]
    if k == "budget_mem":
        return [T(c.s(c.pick(["ผิวแพ้ง่าย ใช้น้ำมันไม่ได้", "ไม่ชอบกลิ่นน้ำมันหอม"])), has=[["นวด", "ค่ะ"]]),
                T(c.q(c.pick(["มีเงิน 300 บาท เลือกอะไรได้บ้าง", "งบ 300 พอนวดอะไร"])), has=[["นวดคอบ่าไหล่", "นวดเท้า", "นวดหน้า"]], not_=["อโรมา"])]
    s = c.pick(SVC)
    return [T(c.q(c.pick(["{a} ราคาเท่าไหร่", "{a} คิดเท่าไร"]).format(a=c.alias(s))), has=[money(PRICE[s])]),
            T(c.q(c.pick(["ถ้ามาวันอังคาร 11 โมงได้ลดไหม", "มาวันจันทร์ 10 โมงเช้าจะเหลือกี่บาท"])), has=[money(PRICE[s] * 0.9)], must=f"ลด 10% จาก {PRICE[s]}")]


# ---- จองคิว
def items_th(c: Ctx, p, svc, dt):
    return {
        "name": c.s(c.pick(["ชื่อ{n}", "ผมชื่อ{n}", "ดิฉันชื่อ{n}", "จองในชื่อ{n}", "ใช้ชื่อ{n}"]).format(n=p["full"])),
        "phone": c.s(c.pick(["เบอร์โทร {d}", "ติดต่อได้ที่ {d}", "เบอร์ {d}", "โทร {d}"]).format(d=p["shown"])),
        "service": c.s(c.pick(["เอา{a}", "ขอเป็น{a}", "อยากได้{a}", "สนใจ{a}"]).format(a=c.alias(svc))),
        "time": c.s(c.pick(["ขอ{w}", "สะดวก{w}", "ขอคิว{w}", "{w}ว่างไหม", "ไปได้{w}"]).format(w=c.when_th(dt))),
    }


OPENERS = ["ขอจองคิวหน่อย", "จะจองนวด", "อยากนัดนวดล่วงหน้า", "รบกวนจองคิวให้หน่อย", "ขอนัดคิวนวด", "จองคิวผ่านแชทได้เลยไหม",
           "อยากลงคิวไว้ก่อน", "ขอทำนัดหน่อย", "ช่วยลงคิวให้ที", "อยากได้คิวนวดสักรอบ"]


def g_booking_step(c: Ctx):
    svc, p = c.pick(SVC), c.person()
    dt = c.slot(svc)
    it = items_th(c, p, svc, dt)
    order = ["name", "phone", "service", "time"]
    c.r.shuffle(order)
    if c.r.random() < 0.5:  # เปิดด้วยการบอกบริการที่อยากจองไปเลย
        order.remove("service")
        opener = c.pick(["อยากจอง{a}", "ขอนัด{a}หน่อย", "จะจองคิว{a}", "ขอคิว{a}"]).format(a=c.alias(svc))
    else:
        opener = c.pick(OPENERS)
    turns = [T((c.pick(PREFIX) + c.s(opener)).strip(), must="ถามข้อมูลที่ยังขาด")]
    for i, k in enumerate(order):
        last = i == len(order) - 1
        turns.append(T(it[k], booking=Ctx.tag(p, svc, dt) if last else "none"))
    return turns


def g_booking_full(c: Ctx):
    svc = c.pick(SVC)
    en = c.r.random() < 0.25
    p = c.person(en=en)
    dt = c.slot(svc)
    if en:
        q = c.pick(["Hi, I'd like to book {a} on {w}. My name is {n}, phone {d}.",
                    "Please book {a} for {n} ({d}) on {w}.",
                    "Booking request: {n}, tel {d}, {a}, {w}. Thanks!"]).format(a=c.ealias(svc), w=c.when_en(dt), n=p["full"], d=p["shown"])
        return [T(q, booking=Ctx.tag(p, svc, dt), lang="en")]
    q = c.pick(["ขอจอง{a} {w} ชื่อ{n} เบอร์ {d}", "จองคิวให้หน่อย {n} โทร {d} {a} {w}",
                "{n} ค่ะ ขอนัด{a} {w} ติดต่อ {d}", "ชื่อ{n} เบอร์ {d} อยากได้{a} {w}",
                "รบกวนจอง{a}ให้{n} {w} เบอร์ติดต่อ {d}"]).format(a=c.alias(svc), w=c.when_th(dt), n=p["full"], d=p["shown"])
    return [T(c.s(q), booking=Ctx.tag(p, svc, dt))]


def g_booking_change(c: Ctx):
    svc, p = c.pick(SVC), c.person()
    dt = c.slot(svc)
    k = c.pick(["service", "service", "time", "time", "phone", "name"])
    new_svc, new_dt, new_p = svc, dt, dict(p)
    if k == "service":
        new_svc = c.pick([s for s in SVC if s != svc])
        if MINS[new_svc] >= 120 and dt.hour > 20:
            new_svc = "นวดคอบ่าไหล่"
        change = c.s(c.pick(["เปลี่ยนใจแล้ว ขอเป็น{a}แทน", "เดี๋ยวก่อน เปลี่ยนเป็น{a}ดีกว่า", "ขอแก้บริการเป็น{a}"]).format(a=c.alias(new_svc)))
    elif k == "time":
        new_dt = c.slot(svc)
        while new_dt == dt:
            new_dt = c.slot(svc)
        change = c.s(c.pick(["ขอเลื่อนเป็น{w}แทน", "ติดธุระ ขอเปลี่ยนเป็น{w}", "แก้เวลาเป็น{w}ได้ไหม"]).format(w=c.when_th(new_dt)))
    elif k == "phone":
        q = c.person()
        new_p.update(digits=q["digits"], shown=q["shown"])
        change = c.s(c.pick(["ขอแก้เบอร์เป็น {d}", "เบอร์เมื่อกี้ผิด ที่ถูกคือ {d}", "ใช้เบอร์ {d} แทนดีกว่า"]).format(d=q["shown"]))
    else:
        f, l = c.pick(FIRST), c.pick(LAST)
        while f == p["first"]:
            f = c.pick(FIRST)
        new_p.update(full=f"{f} {l}", first=f)
        change = c.s(c.pick(["ขอเปลี่ยนชื่อผู้จองเป็น{n}", "จองในชื่อ{n}แทนนะ เพราะพาเพื่อนไป", "แก้ชื่อเป็น{n}"]).format(n=f"{f} {l}"))
    it = items_th(c, p, svc, dt)
    order = ["name", "phone", "service", "time"]
    c.r.shuffle(order)
    if order[-1] == k:  # ข้อมูลที่จะเปลี่ยนต้องไม่ใช่ชิ้นสุดท้าย
        order[-1], order[0] = order[0], order[-1]
    pos = order.index(k)
    seq = order[: pos + 1] + ["CHANGE"] + order[pos + 1:]
    turns = [T((c.pick(PREFIX) + c.s(c.pick(OPENERS))).strip(), must="ถามข้อมูลที่ยังขาด")] if c.r.random() < 0.5 else []
    for i, x in enumerate(seq):
        last = i == len(seq) - 1
        user = change if x == "CHANGE" else it[x]
        turns.append(T(user, booking=Ctx.tag(new_p, new_svc, new_dt) if last else "none",
                       must=("ใช้ข้อมูลล่าสุดที่ลูกค้าเปลี่ยน" if last else "")))
    return turns


def g_booking_closed(c: Ctx):
    svc, p = c.pick(SVC), c.person()
    bad = c.slot(svc, bad=True)
    good = c.slot(svc)
    good = good.replace(year=bad.year, month=bad.month, day=bad.day)
    first = c.s(c.pick(["ขอจอง{a} {w} ชื่อ{n} เบอร์ {d}", "{n} โทร {d} อยากนัด{a} {w}"]).format(
        a=c.alias(svc), w=c.when_th(bad), n=p["full"], d=p["shown"]))
    t_good = c.time_th(good)
    second = c.s(c.pick(["งั้นขอเป็น {t} วันเดิม", "ถ้าอย่างนั้นเปลี่ยนเป็น {t} แทน", "โอเค เอา {t} วันเดียวกันแทน"]).format(t=t_good))
    return [T(first, has=[REFUSE_TIME], must=f"{bad:%H:%M} อยู่นอกเวลารับลูกค้า (10:00–21:00)"),
            T(second, booking=Ctx.tag(p, svc, good), must="ใช้วันเดิมกับเวลาใหม่")]


def g_booking_incomplete(c: Ctx):
    svc, p = c.pick(SVC), c.person()
    dt = c.slot(svc)
    k = c.pick(["name", "phone", "service", "time", "vague", "notoffered"])
    it = items_th(c, p, svc, dt)
    if k == "vague":
        vague = c.pick(["พรุ่งนี้ช่วงบ่าย", "เสาร์นี้ตอนเย็น", "สัปดาห์หน้าวันไหนก็ได้", "เร็ว ๆ นี้"])
        q = c.s(f"ขอจอง{c.alias(svc)} {vague} ชื่อ{p['full']} เบอร์ {p['shown']}")
        return [T(q, has=[["กี่โมง", "เวลา", "วันที่", "วันไหน"]], must="เวลายังไม่ชัด ต้องถามวันเวลาที่แน่นอน")]
    if k == "notoffered":
        ns, kw = c.pick(NOT_OFFERED)
        q = c.s(f"จอง{ns} {c.when_th(dt)} ชื่อ{p['full']} เบอร์ {p['shown']}")
        return [T(q, has=[NO], not_=[f"re:{kw}[^\\n]{{0,15}}?\\d{{2,4}}\\s*บาท"], must=f"ร้านไม่มี{ns} จองไม่ได้")]
    ask = {"name": ["ชื่อ"], "phone": ["เบอร์", "โทร"], "service": ["บริการ", "นวดแบบไหน", "นวดอะไร"], "time": ["วัน", "เวลา", "กี่โมง"]}[k]
    given = [x for x in ["name", "phone", "service", "time"] if x != k]
    if c.r.random() < 0.5:
        return [T(" ".join(it[x] for x in given), has=[ask], must=f"ข้อมูลยังไม่ครบ ต้องถาม{ask[0]}")]
    turns = [T(it[x], must="ข้อมูลยังไม่ครบ") for x in given]
    turns[-1] = T(it[given[-1]], has=[ask], must=f"ข้อมูลยังไม่ครบ ต้องถาม{ask[0]}")
    return turns


KINDS = [  # ชนิด, ชื่อไทย, จำนวนบท, ตัวสร้าง
    ("info", "ข้อมูลร้าน (เวลา ที่อยู่ ติดต่อ นโยบาย)", 70, g_info),
    ("price", "ราคาและบริการ", 70, g_price),
    ("discount", "ส่วนลดและโปรโมชัน", 55, g_discount),
    ("not_offered", "บริการที่ร้านไม่มี", 40, g_not_offered),
    ("offtopic", "เรื่องนอกร้าน", 40, g_offtopic),
    ("english", "ภาษาอังกฤษ", 50, g_english),
    ("followup", "ถามต่อเนื่องหลายข้อความ", 70, g_followup),
    ("booking_step", "จองคิว · ให้ข้อมูลทีละอย่าง", 40, g_booking_step),
    ("booking_full", "จองคิว · ครบในข้อความเดียว", 40, g_booking_full),
    ("booking_change", "จองคิว · เปลี่ยนใจกลางทาง", 35, g_booking_change),
    ("booking_closed", "จองคิว · ขอเวลานอกเวลาเปิดร้าน", 30, g_booking_closed),
    ("booking_incomplete", "จองคิว · ให้ข้อมูลไม่ครบ", 30, g_booking_incomplete),
]


# ---------------------------------------------------------------- 5. สร้าง ตรวจซ้ำ/คล้าย แล้วเขียนไฟล์
def main():
    rng = random.Random(SEED)
    seen: set[str] = set()
    used_now: set[str] = set()
    dialogs, rejected = [], Counter()
    max_sim, max_pair = 0.0, ("", "")
    for kind, kind_th, n, gen in KINDS:
        made, tries = 0, 0
        while made < n:
            tries += 1
            assert tries < n * 200, f"สร้าง {kind} ไม่ซ้ำได้ไม่ครบ"
            c = Ctx(rng)
            if f"{c.now:%Y-%m-%d %H:%M}" in used_now:
                rejected["วันเวลาปัจจุบันซ้ำ"] += 1
                continue
            turns = gen(c)
            texts = [t["user"] for t in turns]
            keys = [norm(t) for t in texts]
            if len(set(keys)) < len(keys) or any(k in seen for k in keys):
                rejected["ซ้ำกับข้อความที่มีแล้ว"] += 1
                continue
            sims = [similarity(t) for t in texts]
            if any(s >= SIM_THRESHOLD for s, _ in sims):
                rejected["คล้ายชุดทดสอบ"] += 1
                continue
            for t, (s, w) in zip(texts, sims):
                if s > max_sim:
                    max_sim, max_pair = s, (t, w)
            seen.update(keys)
            used_now.add(f"{c.now:%Y-%m-%d %H:%M}")
            dialogs.append({"kind": kind, "kind_th": kind_th, "now": f"{c.now:%Y-%m-%d %H:%M}", "turns": turns})
            made += 1
    rng.shuffle(dialogs)
    for i, d in enumerate(dialogs, 1):
        d["id"] = f"q{i:04d}"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as f:
        for d in dialogs:
            f.write(json.dumps({"id": d["id"], **{k: v for k, v in d.items() if k != "id"}}, ensure_ascii=False) + "\n")

    n_msgs = sum(len(d["turns"]) for d in dialogs)
    print(f"เขียน {len(dialogs)} บท ({n_msgs} ข้อความลูกค้า) -> {OUT.relative_to(LAB.parent)}")
    for kind, kind_th, _, _ in KINDS:
        ds = [d for d in dialogs if d["kind"] == kind]
        print(f"  {kind:<19} {kind_th:<40} {len(ds):>4} บท  {sum(len(d['turns']) for d in ds):>4} ข้อความ")
    print(f"ข้อความต้องห้าม (ชุดทดสอบ + ปุ่มลัด): {len(FORBIDDEN)} ข้อความ")
    print(f"สุ่มทิ้งระหว่างสร้าง: {dict(rejected)}")
    print(f"ความคล้ายสูงสุดที่เหลือ: {max_sim:.2f}  '{max_pair[0]}'  ~  '{max_pair[1]}'")
    print(f"ข้อความซ้ำในชุดใหม่: {n_msgs - len(seen)}  · วันเวลาปัจจุบันไม่ซ้ำกัน: {len({d['now'] for d in dialogs})} ค่า")


if __name__ == "__main__":
    main()
