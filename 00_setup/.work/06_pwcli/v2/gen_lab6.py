#!/usr/bin/env python3
"""Generate the LAB 6 step-by-step walkthrough (markdown) from the real reference run in ref/run/steps."""
import json, re
from pathlib import Path

STEPS = Path(__file__).parent / "ref/run/steps"
CMP = {1: "s01", 2: "s02", 4: "s04", 6: "s06", 7: "s07", 9: "s09", 11: "s11"}
SPECS = {  # same specs as the compare.py calls -> numbered yaml under each compare image
 1: ['combobox "Change ticket type', 'button "1 passenger', 'seating class', 'combobox "Where from', 'combobox "Where to', 'textbox "Departure"'],
 2: ['listbox "Select your ticket', 'option "Round trip"', 'option "One way"', 'option "Multi-city"'],
 4: ['combobox "Where else', 'option "Bangkok"', 'option "Suvarnabhumi', 'option "Don Mueang'],
 6: [r'combobox "Where to\?" \[expanded', 'option "Anywhere"', 'option "Europe"', 'option "Japan"'],
 7: [r'combobox "Where to\?" \[expanded', 'option "Tokyo, Japan"', 'option "Haneda', 'option "Narita'],
 9: ['textbox "Departure"', 'button "Wednesday, October 14, 2026', 'button "Thursday, October 15, 2026', 'button "Friday, October 16, 2026', 'button "Done'],
 11: ['combobox "Change ticket type', 'combobox "Where from', 'combobox "Where to', 'textbox "Departure"', 'button "Search"'],
}
CIRC = "①②③④⑤⑥⑦⑧"


def numbered(snap, specs, target_line):
    rows = []
    for i, sp in enumerate(specs):
        n, l = next((n, l) for n, l in enumerate(snap, 1) if re.search(sp, l))
        rows.append((l.strip(), f"# {CIRC[i]} บรรทัด {n}" + (" ← เป้าของ step นี้" if n == target_line else "")))
    w = max(len(a) for a, _ in rows)
    return "\n".join(f"{a.ljust(w)}   {b}" for a, b in rows)

# per step: title, observe note, decide note, act note, verify note (Thai, short)
NOTES = {
 1: ("เปิดรายการประเภทตั๋ว",
     "หน้าแรกของ Google Flights ค่าเริ่มต้นเป็น Round trip โค้ดเช็กก่อนว่าเป้าหมาย \"One way\" สำเร็จหรือยัง (ยัง) จึงต้องถาม LLM",
     "ยังไม่มี option \"One way\" ในหน้า LLM จึงเลือกทางที่กติกาใน goal บอกไว้: click combobox ประเภทตั๋วเพื่อเปิดรายการ",
     "ผ่านทั้ง 4 ข้อ โค้ดวาดวงแดงรอบ combobox ตาม box `480,400,138,36` แล้วจึงสั่งกด",
     "dropdown เปิดแล้ว แต่ประเภทตั๋วยังไม่ใช่ One way → **ยังไม่ผ่าน** โค้ดวนกลับไป Observe ใหม่ และ ref `e107` หายไปจาก snapshot ใหม่แล้ว"),
 2: ("เลือก One way",
     "หน้าเปลี่ยน: มี listbox 3 option โผล่มา snapshot มี 267 บรรทัด",
     "\"สิ่งที่ทำไปแล้ว\" บอก LLM ว่าเปิดรายการไปแล้ว และ snapshot ที่ส่งไปเหลือแค่ 3 บรรทัด (กรองด้วยคำใบ้ของ step) LLM จึงเลือกได้ง่าย",
     "ref `e541` มีอยู่ใน snapshot ล่าสุดจริง (ถ้า LLM ตอบ `e107` จากรอบก่อน ข้อ \"ref exists\" จะไม่ผ่าน)",
     "ชื่อ combobox เปลี่ยนเป็น `Change ticket type. One way` → **ผ่าน** ไปเป้าหมายถัดไป · ก่อนถาม LLM เรื่องชั้นโดยสาร โค้ด verify ก่อนและพบว่า `Economy` + `1 passenger` เป็นค่าเริ่มต้นอยู่แล้ว จึงข้ามโดยไม่เรียก LLM"),
 3: ("เปิดช่องต้นทาง",
     "ฟอร์มถูก render ใหม่หลังเลือก One way ทุก element ได้ ref ใหม่ (`Where from?` เป็น `e637` ไม่ใช่ `e136` แบบใน LAB 2)",
     "ต้นทางแสดง `Bangkok` แต่ยังไม่ได้ระบุสนามบิน LLM จึงเลือกเปิดช่องเพื่อดูตัวเลือก",
     "ผ่านทั้ง 4 ข้อ",
     "หน้าเปลี่ยน: ช่องที่พิมพ์ได้กลายเป็น element ใหม่ชื่อ `Where else?` [expanded] ยังไม่มี BKK ในชื่อ → **ยังไม่ผ่าน**"),
 4: ("เลือก Suvarnabhumi (BKK)",
     "dropdown ต้นทางเปิดอยู่ มี option สนามบินให้เลือกทันทีโดยไม่ต้องพิมพ์",
     "goal บอกว่า \"ถ้าเห็น option 'Suvarnabhumi Airport (BKK)' ให้ click\" LLM เห็นจริงใน 6 บรรทัดที่ส่งไป จึงไม่ต้อง fill",
     "ผ่านทั้ง 4 ข้อ",
     "ชื่อช่องต้นทางเปลี่ยนเป็น `Where from? Bangkok BKK` → **ผ่าน**"),
 5: ("เปิดช่องปลายทาง",
     "ต้นทางเสร็จแล้ว ช่อง `Where to?` ยังว่าง",
     "ยังไม่มี option Tokyo และช่องยังไม่ [expanded] ตาม goal ต้อง click ช่องก่อน",
     "ผ่านทั้ง 4 ข้อ",
     "ช่อง `Where to?` เป็น [expanded] แล้ว แต่ยังไม่มีค่า Tokyo → **ยังไม่ผ่าน**"),
 6: ("พิมพ์ Tokyo",
     "dropdown ปลายทางเปิดอยู่ แต่มีแค่ปลายทางแนะนำ (Anywhere, Europe, Japan, …) ไม่มี Tokyo",
     "ไม่มี option `Tokyo, Japan` LLM จึง fill ตาม goal",
     "มีข้อตรวจเพิ่ม 1 ข้อสำหรับ fill: ค่าที่กรอกต้องอยู่ในรายการที่โค้ดอนุญาต (`Tokyo`) ถ้า LLM จะพิมพ์อย่างอื่นจะไม่ผ่าน",
     "ช่องมีค่า Tokyo แล้วแต่ dropdown ยัง [expanded] = ยังไม่ได้เลือกจริง → **ยังไม่ผ่าน** · น่าสนใจ: ref `e965` **ยังอยู่** เพราะการพิมพ์ไม่ได้สร้างช่องใหม่ แต่โค้ดก็ยัง observe ใหม่ตามกติกา"),
 7: ("เลือก Tokyo, Japan",
     "รายการเปลี่ยนเป็นผลค้นหาของคำว่า Tokyo",
     "\"สิ่งที่ทำไปแล้ว\" มี 2 บรรทัด (click + fill) LLM เลือก option ที่ตรงชื่อเป้าหมายพอดี ไม่เลือก Haneda/Narita",
     "ผ่านทั้ง 4 ข้อ",
     "dropdown ปิดแล้ว และช่อง `Where to?` มีค่า Tokyo → **ผ่าน** (ต้องผ่านทั้งสองเงื่อนไข ดู A5)"),
 8: ("เปิดปฏิทิน",
     "ฟอร์มมี One way / BKK / Tokyo ครบ เหลือวันเดินทาง โค้ดคำนวณวันที่เป้าหมาย = 15 ต.ค. 2026 ไว้แล้วตั้งแต่เริ่ม",
     "ยังไม่มีปุ่มวันที่ 15 LLM จึงเปิดช่อง Departure",
     "ผ่านทั้ง 4 ข้อ",
     "ปฏิทินเปิดแล้ว (snapshot รอบถัดไปยาว 1,566 บรรทัด) แต่ยังไม่ได้เลือกวัน → **ยังไม่ผ่าน**"),
 9: ("เลือกวันที่ 15 ต.ค. 2026",
     "ปฏิทิน 2 เดือนมีปุ่มวันหลายร้อยปุ่ม snapshot **1,566 บรรทัด**",
     "โค้ดกรองด้วยคำใบ้ `Departure|October 15, 2026` เหลือส่งให้ LLM แค่ **2 บรรทัด** (A6 token budget) โอกาสกดผิดวันแทบเป็นศูนย์",
     "ผ่านทั้ง 4 ข้อ · ชื่อปุ่มมีราคา `7160 Thai baht` แต่ไม่ติด denylist เพราะเราห้ามแค่ \"จอง/จ่าย\" ไม่ได้ห้ามคำว่าราคา",
     "ช่อง Departure มีค่า `Thu, Oct 15` → **ผ่าน**"),
 10: ("กด Done ของปฏิทิน",
     "ปฏิทินยังเปิดอยู่ ปุ่มค้นหาถูกบังอยู่ข้างหลัง",
     "goal บอกให้กด Done ก่อนถ้าเห็น LLM เห็นปุ่ม `Done. Search for one-way flights…`",
     "ชื่อปุ่มมีคำว่า Search แต่ไม่ติด denylist (การค้นหาอนุญาต) ผ่านทั้ง 4 ข้อ",
     "ปฏิทินปิด แต่ URL ยังไม่ใช่ `/travel/flights/search` → **ยังไม่ผ่าน** (ปุ่ม Done แค่ปิดปฏิทิน ไม่ได้ค้นหา)"),
 11: ("กด Search",
     "ปุ่ม `Search` โผล่แล้ว (ใน LAB 2 ยังไม่มีปุ่มนี้)",
     "\"สิ่งที่ทำไปแล้ว\" บอกว่ากด Done ไปแล้ว LLM จึงเลือก Search",
     "ผ่านทั้ง 4 ข้อ",
     "URL เป็นหน้า `/travel/flights/search` และมีผลเที่ยวบิน ≥ 3 รายการ → **ผ่าน** ครบทุกเป้าหมาย"),
}


def excerpt_prompt(txt):
    """goal + history + trimmed snapshot (max 10 element lines) from prompt.txt"""
    goal = re.search(r"เป้าหมายของ step นี้:\n(.*?)\n\n", txt, re.S).group(1)
    hist = re.search(r"สิ่งที่ทำไปแล้วใน step นี้:\n(.*?)\n\n", txt, re.S).group(1)
    snap = re.search(r"\[ref=\.\.\.\]\):\n(.*?)\n\nกติกา", txt, re.S).group(1).splitlines()
    keep = snap if len(snap) <= 10 else [l for l in snap if not re.search(r'"(Main menu|Skip to|Accessibility|Change appearance|Google apps)', l)][:7] + [f"...   (รวม {len(snap)} บรรทัด)"]
    return f"เป้าหมายของ step นี้:\n{goal}\n\nสิ่งที่ทำไปแล้วใน step นี้:\n{hist}\n\nหน้าเว็บตอนนี้ (snapshot ตัดแล้ว):\n" + "\n".join(keep)


def main():
    out = []
    for d in sorted(STEPS.glob("[01]*_*")):
        n = int(d.name[:2])
        if n not in NOTES:
            continue
        title, n_obs, n_dec, n_act, n_ver = NOTES[n]
        j = json.loads((d / "decision.json").read_text())
        snap = (d / "snapshot.yml").read_text().splitlines()
        t = j["target"]; dec = j["llm_decision"]
        tline = snap[t["line"] - 1].strip()
        act = (d / "act.txt").read_text()
        cmd = act.splitlines()[0]
        pw = next((l for l in act.splitlines() if l.startswith("await ")), "")
        url = next((l for l in act.splitlines() if l.startswith("- Page URL")), "")
        ver = j["verify"]
        old = ver["old_ref_still_in_new_snapshot"]
        vlines = [l for l in act.splitlines() if l.startswith(("#   ", "# เป้าหมาย"))]
        out.append(f"#### Step {n:02d} · {title}\n")
        out.append(f"📁 [`log/steps/{d.name}/`](log/steps/{d.name}/) · LLM ใช้เวลา {j['llm_seconds']} วินาที\n")
        # 1 observe
        out.append(f"**① Observe** — `playwright-cli snapshot --boxes` ได้ [`snapshot.yml`](log/steps/{d.name}/snapshot.yml) {j['observe']['snapshot_lines']:,} บรรทัด · บรรทัด {t['line']} คือ element ที่จะถูกเลือกในรอบนี้\n")
        if n in CMP:
            out.append(f"![Step {n}: ซ้าย ภาพจริงของหน้าในช่วง Observe มีกรอบสีตาม box, ขวา บรรทัด YAML เดียวกัน](img/lab6-{CMP[n]}-compare.png)\n")
            out.append("```yaml\n" + numbered(snap, SPECS[n], t["line"]) + "\n```\n")
        else:
            out.append(f"```yaml\n{tline}\n```\n")
        out.append(f"{n_obs}\n")
        # 2 decide
        out.append(f"**② Decide** — ส่ง {j['observe']['lines_sent_to_llm']} บรรทัดให้ LLM ([`prompt.txt`](log/steps/{d.name}/prompt.txt) ตัดตอน):\n")
        out.append("```text\n" + excerpt_prompt((d / "prompt.txt").read_text()) + "\n```\n")
        out.append("LLM ตอบ (`decision.json` → `llm_decision`):\n")
        out.append("```json\n" + json.dumps(dec, ensure_ascii=False) + "\n```\n")
        out.append(f"{n_dec}\n")
        # 3 validate -> act
        checks = " · ".join(("✓ " if c["pass"] else "✗ ") + c["check"] for c in j["validate"]["checks"])
        out.append(f"**③ Validate → Act** — {checks} → `{j['validate']['verdict']}`\n")
        out.append(f"<img src=\"log/steps/{d.name}/page.png\" width=\"860\" alt=\"Step {n} ภาพจริงก่อนกด วงแดงรอบ {t['role']} {t['name'][:40]} พร้อม callout\">\n")
        out.append("```text\n" + "\n".join(x for x in [cmd, pw, url[:110] + ("…" if len(url) > 110 else "")] if x) + "\nexit code: 0\n```\n")
        out.append(f"{n_act}\n")
        # 4 verify
        proof = [l.replace("#   ", "  ", 1).replace("# ", "", 1) for l in vlines]
        out.append(f"**④ Verify** — snapshot ใหม่ [`verify.yml`](log/steps/{d.name}/verify.yml):\n")
        out.append("```text\n" + "\n".join(proof + [f"ref {dec['ref']} ใน snapshot ใหม่: {'ยังอยู่' if old else 'ไม่มีแล้ว'}"]) + "\n```\n")
        out.append(f"{n_ver}\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
