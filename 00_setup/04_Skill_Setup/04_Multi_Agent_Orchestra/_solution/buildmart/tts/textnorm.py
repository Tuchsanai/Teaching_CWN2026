"""Text cleaning + Thai readability normalization for TTS (no heavy deps)."""
import re

THAI_RE = re.compile(r"[฀-๿]")
MAX_CHARS = 600

_EMOJI_RE = re.compile(
    "["
    "\U0001F000-\U0001FAFF"  # pictographs, emoticons, transport, symbols ext
    "\U00002600-\U000027BF"  # misc symbols + dingbats
    "\U0001F1E6-\U0001F1FF"  # flags
    "\U00002B00-\U00002BFF"
    "\U0000FE00-\U0000FE0F"  # variation selectors
    "\U0000200D"             # ZWJ
    "\U000020E3"
    "]+"
)
_TAG_RE = re.compile(r"\[(?:CALC|ADD_TO_CART|QUOTE|[A-Z_]{3,})\]\s*(\{[^{}]*\})?")
_CITE_RE = re.compile(r"\[\d+(?:\s*,\s*\d+)*\]")
_THINK_RE = re.compile(r"<think>.*?(</think>|$)", re.S)
_MD_LINK_RE = re.compile(r"!?\[([^\]]*)\]\([^)]*\)")
_URL_RE = re.compile(r"(https?://|www\.)\S+")
_PATH_RE = re.compile(r"/api/\S+")


def detect_lang(text: str) -> str:
    return "th" if THAI_RE.search(text or "") else "en"


def clean_text(text: str) -> str:
    t = text or ""
    t = _THINK_RE.sub(" ", t)
    t = _TAG_RE.sub(" ", t)
    t = _MD_LINK_RE.sub(r"\1", t)
    t = _URL_RE.sub(" ", t)
    t = _PATH_RE.sub(" ", t)
    t = _CITE_RE.sub(" ", t)
    t = _EMOJI_RE.sub(" ", t)
    t = re.sub(r"`{1,3}", "", t)
    t = re.sub(r"(\*\*|__|~~|\*)", "", t)
    t = re.sub(r"^\s{0,3}#{1,6}\s*", "", t, flags=re.M)        # headings
    t = re.sub(r"^\s*[-+•>]\s+", "", t, flags=re.M)            # bullets / quotes
    t = re.sub(r"^\s*\|?[-:| ]{3,}\|?\s*$", "", t, flags=re.M)  # table rules
    t = t.replace("|", " ")
    t = re.sub(r"\s*\n+\s*", " ", t)  # newlines -> space
    t = re.sub(r"[ \t]{2,}", " ", t).strip()
    if len(t) > MAX_CHARS:
        t = t[:MAX_CHARS]
    return t


# ---------------- Thai readability ----------------
_ONES = ["ศูนย์", "หนึ่ง", "สอง", "สาม", "สี่", "ห้า", "หก", "เจ็ด", "แปด", "เก้า"]
_UNITS = ["", "สิบ", "ร้อย", "พัน", "หมื่น", "แสน"]


def _int_to_thai(n: int) -> str:
    if n == 0:
        return "ศูนย์"
    if n < 0:
        return "ลบ" + _int_to_thai(-n)
    if n >= 1_000_000:
        hi, lo = divmod(n, 1_000_000)
        return _int_to_thai(hi) + "ล้าน" + (_int_to_thai(lo) if lo else "")
    digits = str(n)
    out = []
    L = len(digits)
    for i, ch in enumerate(digits):
        d = int(ch)
        pos = L - i - 1
        if d == 0:
            continue
        if pos == 0 and d == 1 and L > 1:
            out.append("เอ็ด")
        elif pos == 1 and d == 2:
            out.append("ยี่สิบ")
        elif pos == 1 and d == 1:
            out.append("สิบ")
        else:
            out.append(_ONES[d] + _UNITS[pos])
    return "".join(out)


def num_to_thai(s: str) -> str:
    s = s.replace(",", "")
    if "." in s:
        a, b = s.split(".", 1)
        return _int_to_thai(int(a or 0)) + "จุด" + "".join(_ONES[int(c)] for c in b if c.isdigit())
    return _int_to_thai(int(s))


def _baht(m):
    num = m.group(1).replace(",", "")
    if "." in num:
        a, b = num.split(".", 1)
        b = (b + "00")[:2]
        s = _int_to_thai(int(a or 0)) + "บาท"
        if int(b):
            s += _int_to_thai(int(b)) + "สตางค์"
        return " " + s + " "
    return " " + _int_to_thai(int(num)) + "บาท "


def _time(m):
    h, mi = int(m.group(1)), int(m.group(2))
    if h > 24 or mi > 59:
        return m.group(0)
    s = _int_to_thai(h) + "นาฬิกา"
    if mi:
        s += _int_to_thai(mi) + "นาที"
    return " " + s + " "


ABBR = [
    ("ตร.ซม.", "ตารางเซนติเมตร"),
    ("ตร.มม.", "ตารางมิลลิเมตร"),
    ("ตร.ม.", "ตารางเมตร"),
    ("ลบ.ม.", "ลูกบาศก์เมตร"),
    ("ลบ.ซม.", "ลูกบาศก์เซนติเมตร"),
    ("กก.", "กิโลกรัม"),
    ("มม.", "มิลลิเมตร"),
    ("ซม.", "เซนติเมตร"),
    ("กม.", "กิโลเมตร"),
    ("ชม.", "ชั่วโมง"),
    ("มอก.", "มอก "),
    ("บจก.", "บริษัทจำกัด"),
    ("จ.", "จังหวัด"),
]
# number followed by unit-like latin abbreviations
LATIN_UNITS = [
    (r"(?<=\d)\s*kg\b", " กิโลกรัม"),
    (r"(?<=\d)\s*mm\b", " มิลลิเมตร"),
    (r"(?<=\d)\s*cm\b", " เซนติเมตร"),
    (r"(?<=\d)\s*m2\b", " ตารางเมตร"),
    (r"(?<=\d)\s*m3\b", " ลูกบาศก์เมตร"),
    (r"(?<=\d)\s*A\b", " แอมป์"),
    (r"(?<=\d)\s*%", " เปอร์เซ็นต์"),
    (r"(?<=\d)\s*m\b", " เมตร"),
]


def thai_readable(text: str) -> str:
    t = text
    # times 07:00 / 07.00 น.
    t = re.sub(r"\b(\d{1,2})[:.](\d{2})\s*(?:น\.)", _time, t)
    t = re.sub(r"\b(\d{1,2}):(\d{2})\b", _time, t)
    # prices: 1,234.50 บาท / ฿1,234
    t = re.sub(r"฿\s*(\d[\d,]*(?:\.\d+)?)", _baht, t)
    t = re.sub(r"(\d[\d,]*(?:\.\d+)?)\s*บาท", _baht, t)
    # abbreviations (longest first already)
    for a, full in ABBR:
        t = t.replace(a, full)
    for pat, rep in LATIN_UNITS:
        t = re.sub(pat, rep, t)
    t = re.sub(r"(\d)\s*[–-]\s*(\d)", r"\1 ถึง \2", t)  # ranges 16–20
    t = re.sub(r"(\d)\s*[x×]\s*(\d)", r"\1 คูณ \2", t)
    t = re.sub(r"(?<![\d.])(\d[\d,]*(?:\.\d+)?)", lambda m: " " + num_to_thai(m.group(1)) + " ", t)
    t = re.sub(r"\s*/\s*", " ต่อ ", t)
    t = t.replace("ๆ", " ๆ ")
    t = re.sub(r"\s{2,}", " ", t).strip()
    return t


if __name__ == "__main__":
    for s in [
        "ร้านเปิดวันจันทร์ถึงเสาร์ 07:00 ถึง 18:00 น. ครับ",
        "**ปูน CEM-001** ราคา 145 บาท/ถุง 😀 [1] ใช้ 3.5 ลบ.ม. หนัก 1,250.5 กก. พื้นที่ 20 ตร.ม. [CALC]{\"type\":\"concrete\",\"volume\":3}",
        "- เบรกเกอร์ 16–20 A รวม 15,607.29 บาท ดู https://x.y/z",
    ]:
        c = clean_text(s)
        print(c, "=>", thai_readable(c))
