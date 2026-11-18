"""ให้โมเดลครูตอบบทสนทนาลูกค้า แล้วคัดเฉพาะบทที่ตอบถูกเป็น Dataset (Training 90% / Validation 10%)

อ่าน   lab3_qlora/data/questions.jsonl  (บทสนทนาฝั่งลูกค้า + เงื่อนไขของคำตอบแต่ละข้อความ)
       lab3_qlora/teacher.env            (TEACHER_BASE_URL, TEACHER_MODEL, TEACHER_API_KEY)
       lab3_qlora/code/web/db/init.sql   (ข้อมูลร้านและบริการ = ชุดเดียวกับที่เว็บอ่านจาก PostgreSQL)
เขียน  lab3_qlora/data/train.jsonl, val.jsonl, teacher_raw.jsonl (คำตอบดิบทุกครั้ง ใช้ทำต่อได้ถ้าหยุดกลางทาง)
       lab3_qlora/results/dataset_report.json

system prompt / temperature 0.3 / max_tokens 1024 / ตัด <think> / ประวัติแชทที่เก็บแท็กจองไว้
ทำแบบเดียวกับ code/web (lib/prompt.ts, lib/llm.ts, app/api/chat/route.ts)
"""
from __future__ import annotations

import argparse
import json
import os
import random
import re
import sys
import time
import urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from threading import Lock

LAB = Path(__file__).resolve().parent.parent
DATA = LAB / "data"
RESULTS = LAB / "results"
SEED = 7
VAL_SHARE = 0.10


# ---------------------------------------------------------------- ข้อมูลร้าน (จาก init.sql ของเว็บ)
def load_shop(sql_path: Path):
    sql = sql_path.read_text(encoding="utf-8")
    svc_block = re.search(r"INSERT INTO services[^;]*?VALUES(.*?)ON CONFLICT", sql, re.S).group(1)
    services = [
        {"name_th": m[0], "duration_min": int(m[1]), "price_thb": int(m[2]), "description_th": m[3]}
        for m in re.findall(r"\('([^']*)',\s*(\d+),\s*(\d+),\s*'([^']*)'\)", svc_block)
    ]
    info_block = re.search(r"INSERT INTO shop_info[^;]*?VALUES(.*?)ON CONFLICT", sql, re.S).group(1)
    info = dict(re.findall(r"\('([^']*)',\s*'([^']*)'\)", info_block))
    return services, info


def build_system_prompt(services, info, now: str) -> str:
    """ตรงกับ buildSystemPrompt() ใน code/web/lib/prompt.ts ทุกตัวอักษร ต่างแค่ "วันเวลาปัจจุบัน" ใช้ของแต่ละบท"""
    g = lambda k: info.get(k, "-")
    service_lines = "\n".join(
        f"- {s['name_th']} | {s['duration_min']} นาที | {s['price_thb']} บาท | {s['description_th']}" for s in services
    )
    return f"""คุณคือ "น้องสบายใจ" พนักงานต้อนรับของร้าน {info.get('shop_name', 'สบายใจ นวดแผนไทย')}
ตอบภาษาไทยสุภาพ ลงท้าย ค่ะ/นะคะ ตอบสั้นกระชับ

กฎสำคัญ:
1. ตอบเฉพาะเรื่องร้านนี้ ถ้าถามเรื่องอื่น (เช่น สูตรอาหาร ข่าว การบ้าน) ให้ปฏิเสธสุภาพแล้วชวนกลับมาเรื่องบริการนวดของร้าน
2. ใช้เฉพาะข้อมูลด้านล่าง ห้ามแต่งราคา บริการ หรือโปรโมชันเอง ถ้าลูกค้าถามบริการที่ไม่มีในรายการ ให้ตอบว่าร้านไม่มีบริการนั้น และห้ามบอกราคาของบริการที่ไม่มี
3. ไม่วินิจฉัยโรค ถ้าอาการรุนแรงหรือไม่แน่ใจ ให้แนะนำปรึกษาแพทย์
4. ลูกค้าพิมพ์ภาษาอังกฤษ ให้ตอบเป็นภาษาอังกฤษ ลูกค้าพิมพ์ภาษาไทย ให้ตอบภาษาไทย (ดูจากข้อความล่าสุดของลูกค้า)
5. จำสิ่งที่ลูกค้าบอกไว้ในแชทนี้ (ชื่อ อาการ สิ่งที่ไม่ต้องการ งบประมาณ) แล้วใช้ตอบคำถามถัดไป
6. ถ้าลูกค้าถามเวลาที่อยู่นอกเวลาเปิดร้าน หรือหลังรอบสุดท้าย ให้บอกตรง ๆ ว่าไม่ได้เพราะร้านปิดแล้ว
7. ถ้าต้องคิดส่วนลด ให้คิดจากราคาในรายการและบอกราคาหลังลดเป็นตัวเลข เช่น 450 บาท ลด 15% เหลือ 382.50 บาท
8. ตอบเป็นข้อความธรรมดา ห้ามใช้ markdown (ห้ามใช้ ** ตัวหนา, #, ตาราง) ถ้าจะแจกแจงให้ขึ้นบรรทัดใหม่ขึ้นต้นด้วย "- " หรือ "1."

วันเวลาปัจจุบัน: {now} (เวลาประเทศไทย)

ข้อมูลร้าน:
เวลาเปิด-ปิด: {g('hours')}
ที่อยู่: {g('address')}
โทรศัพท์: {g('phone')}
โปรโมชัน: {g('promotions')}
นโยบายร้าน: {g('policies')}
การยกเลิกหรือเลื่อนนัด: {g('cancellation')}
การชำระเงิน: {g('payment')}
ที่จอดรถ: {g('parking')}

รายการบริการ (ชื่อ | เวลา | ราคา | รายละเอียด):
{service_lines}

การจองคิว:
- เมื่อลูกค้าต้องการจอง ให้ถามข้อมูลที่ยังขาดจนครบ 4 อย่าง: ชื่อ, เบอร์โทร, บริการ (ต้องเป็นชื่อในรายการด้านบน), วันและเวลา (อยู่ในเวลาเปิดร้าน)
- ถ้าลูกค้าเปลี่ยนใจระหว่างจอง ให้ใช้ข้อมูลล่าสุดที่ลูกค้าบอก
- เมื่อได้ข้อมูลครบแล้ว ไม่ต้องถามยืนยันซ้ำ ให้สรุปการจองสั้น ๆ แล้วขึ้นบรรทัดสุดท้ายเป็นแท็กนี้ "ตามรูปแบบเป๊ะ" (บรรทัดเดียว JSON ล้วน):
[BOOKING]{{"customer_name":"ชื่อลูกค้า","phone":"เบอร์โทร","service":"ชื่อบริการตามรายการ","booking_time":"YYYY-MM-DD HH:MM"}}
- ห้ามใส่แท็ก [BOOKING] ถ้าข้อมูลยังไม่ครบ"""


# ---------------------------------------------------------------- เรียกโมเดลครู (แบบ lib/llm.ts)
def load_env(path: Path) -> dict:
    env = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


class Teacher:
    def __init__(self, env: dict):
        base = env["TEACHER_BASE_URL"].rstrip("/")
        self.url = f"{base}/chat/completions" if base.endswith("/v1") else f"{base}/v1/chat/completions"
        self.model = env["TEACHER_MODEL"]
        self._key = env["TEACHER_API_KEY"]  # ไม่พิมพ์ออกจอ
        self.lock = Lock()
        self.prompt_tokens = self.completion_tokens = self.calls = 0

    def chat(self, messages) -> str:
        body = json.dumps({"model": self.model, "messages": messages, "stream": False,
                           "temperature": 0.3, "max_tokens": 1024}).encode()
        req = urllib.request.Request(self.url, data=body, method="POST", headers={
            "Content-Type": "application/json", "Authorization": f"Bearer {self._key}"})
        last = None
        for attempt in range(4):  # ปัญหาเครือข่าย ลองใหม่ (ไม่นับเป็นการตอบใหม่)
            try:
                with urllib.request.urlopen(req, timeout=180) as r:
                    j = json.loads(r.read())
                u = j.get("usage") or {}
                with self.lock:
                    self.calls += 1
                    self.prompt_tokens += u.get("prompt_tokens", 0)
                    self.completion_tokens += u.get("completion_tokens", 0)
                return j["choices"][0]["message"]["content"] or ""
            except Exception as e:  # noqa: BLE001
                last = e
                time.sleep(2 * (attempt + 1))
        raise RuntimeError(f"teacher error: {type(last).__name__}")


def strip_think(raw: str) -> str:
    s = raw
    close = s.rfind("</think>")
    if close != -1 and "<think>" not in s[:close]:
        s = s[close + len("</think>"):]
    s = re.sub(r"<think>[\s\S]*?</think>", "", s)
    if "<think>" in s:
        s = s[: s.index("<think>")]
    return s.strip()


def display_text(text: str) -> str:
    """ข้อความที่ลูกค้าเห็นบนเว็บ (ตัดแท็กจองออก) = ข้อความที่ชุดทดสอบตรวจ"""
    return re.sub(r"\[BOOKING\][\s\S]*$", "", text).rstrip()


# ---------------------------------------------------------------- ตรวจคำตอบ (กติกาเดียวกับ e2e/tests/check.ts)
def contains(text: str, token: str) -> bool:
    if token.startswith("re:"):
        return re.search(token[3:], text, re.I) is not None
    if re.fullmatch(r"[\d-]{9,}", token):
        return token.replace("-", "") in re.sub(r"\D", "", text)
    if re.fullmatch(r"\d+%?", token):
        text = re.sub(r"(?<=\d),(?=\d{3}\b)", "", text)  # 1,147.50 = 1147.50 (ตัวเลขเดียวกัน แค่มีจุลภาคคั่นหลักพัน)
        return re.search(rf"(?<![\d.,]){re.escape(token)}(?!\d)", text) is not None
    return token.lower() in text.lower()


def is_lang(text: str, lang: str) -> bool:
    thai = len(re.findall(r"[฀-๿]", text))
    latin = len(re.findall(r"[A-Za-z]", text))
    if thai + latin == 0:
        return False
    share = thai / (thai + latin)
    return share > 0.5 if lang == "th" else share < 0.2


MD_RE = re.compile(r"\*\*|__|^\s{0,3}#{1,6}\s|^\s*\|.*\|\s*$|```|^\s*[-*]{3,}\s*$", re.M)
TAG_LINE_RE = re.compile(r'^\[BOOKING\](\{[^\n]*\})$')
TAG_KEYS = ["customer_name", "phone", "service", "booking_time"]

# ชนิดเหตุผล (ใช้นับในรายงาน)
R_WORD = "ไม่มีตัวเลข/คำที่ต้องมี"
R_FORBID = "มีคำที่ห้ามมี"
R_LANG = "ตอบผิดภาษา"
R_MD = "ใช้ markdown"
R_TAG_FMT = "แท็กจองผิดรูปแบบ"
R_TAG_EARLY = "ใส่แท็กจองทั้งที่ข้อมูลไม่ครบ"
R_TAG_MISS = "ไม่ใส่แท็กจองทั้งที่ข้อมูลครบ"
R_TAG_VAL = "ข้อมูลในแท็กจองผิด"
R_ERR = "เรียกโมเดลครูไม่สำเร็จ"
# บทที่ผิดหลายอย่าง นับเป็นเหตุผลหลักตามลำดับนี้
MAIN_ORDER = [R_ERR, R_LANG, R_TAG_EARLY, R_TAG_MISS, R_TAG_FMT, R_TAG_VAL, R_MD, R_WORD, R_FORBID]


def check_answer(full: str, ex: dict) -> list[tuple[str, str]]:
    """คืนรายการ (ชนิดเหตุผล, รายละเอียด) ว่างคือผ่าน"""
    fails = []
    shown = display_text(full)
    for item in ex.get("has", []):
        opts = item if isinstance(item, list) else [item]
        if not any(contains(shown, t) for t in opts):
            fails.append((R_WORD, "ไม่มี " + " หรือ ".join(opts)))
    for t in ex.get("not", []):
        if contains(shown, t):
            fails.append((R_FORBID, f"มี {t.removeprefix('re:')}"))
    if ex.get("lang") and not is_lang(shown, ex["lang"]):
        fails.append((R_LANG, f"ต้องตอบภาษา{'ไทย' if ex['lang'] == 'th' else 'อังกฤษ'}"))
    if ex.get("no_markdown") and MD_RE.search(full):
        fails.append((R_MD, MD_RE.search(full).group(0).strip()[:20]))

    bk = ex.get("booking", "none")
    has_tag = "[BOOKING]" in full
    if bk == "none":
        if has_tag:
            fails.append((R_TAG_EARLY, "ข้อมูลยังไม่ครบแต่มีแท็ก"))
        return fails
    if not has_tag:
        fails.append((R_TAG_MISS, "ข้อมูลครบแล้วแต่ไม่มีแท็ก"))
        return fails
    lines = [l.strip() for l in full.strip().splitlines() if l.strip()]
    m = TAG_LINE_RE.match(lines[-1]) if lines else None
    if full.count("[BOOKING]") != 1 or not m:
        fails.append((R_TAG_FMT, "แท็กต้องอยู่บรรทัดสุดท้าย บรรทัดเดียว"))
        return fails
    try:
        tag = json.loads(m.group(1))
    except json.JSONDecodeError:
        fails.append((R_TAG_FMT, "JSON ในแท็กอ่านไม่ได้"))
        return fails
    if not isinstance(tag, dict) or sorted(tag) != sorted(TAG_KEYS) or not all(str(tag[k]).strip() for k in TAG_KEYS):
        fails.append((R_TAG_FMT, "ช่องในแท็กไม่ครบ 4 ช่อง"))
        return fails
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}", str(tag["booking_time"])):
        fails.append((R_TAG_FMT, f"booking_time ไม่ใช่ YYYY-MM-DD HH:MM ({tag['booking_time']})"))
        return fails
    if bk.get("name_must_contain", bk["customer_name"]) not in str(tag["customer_name"]):
        fails.append((R_TAG_VAL, f"ชื่อ {tag['customer_name']} ≠ {bk['customer_name']}"))
    if re.sub(r"\D", "", str(tag["phone"])) != bk["phone"]:
        fails.append((R_TAG_VAL, f"เบอร์ {tag['phone']} ≠ {bk['phone']}"))
    if str(tag["service"]).strip() != bk["service"]:
        fails.append((R_TAG_VAL, f"บริการ {tag['service']} ≠ {bk['service']}"))
    if tag["booking_time"] != bk["booking_time"]:
        fails.append((R_TAG_VAL, f"เวลา {tag['booking_time']} ≠ {bk['booking_time']}"))
    return fails


# ---------------------------------------------------------------- ตอบทั้งบท
def run_dialog(teacher: Teacher, system: str, conv: dict) -> dict:
    """ส่งทีละข้อความ ประวัติแชทเก็บคำตอบเต็ม (มีแท็กจอง) เหมือน route.ts หยุดที่ข้อความแรกที่ผิด"""
    msgs = [{"role": "system", "content": system}]
    answers, fails = [], []
    for i, turn in enumerate(conv["turns"]):
        msgs.append({"role": "user", "content": turn["user"]})
        try:
            full = strip_think(teacher.chat(msgs))
        except RuntimeError as e:
            return {"messages": msgs, "answers": answers, "fails": [(R_ERR, str(e))], "fail_turn": i + 1}
        msgs.append({"role": "assistant", "content": full})
        answers.append(full)
        fails = check_answer(full, turn["expect"])
        if fails:
            return {"messages": msgs, "answers": answers, "fails": fails, "fail_turn": i + 1}
    return {"messages": msgs, "answers": answers, "fails": [], "fail_turn": None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=8, help="จำนวนบทที่ส่งพร้อมกัน")
    ap.add_argument("--limit", type=int, default=0, help="ลองแค่ N บทแรก (0 = ทั้งหมด)")
    args = ap.parse_args()

    services, info = load_shop(LAB / "code/web/db/init.sql")
    teacher = Teacher(load_env(LAB / "teacher.env"))
    convs = [json.loads(l) for l in (DATA / "questions.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    if args.limit:
        convs = convs[: args.limit]

    # ทำต่อจากที่ค้าง: บทที่ตอบจบแล้วใน teacher_raw.jsonl ไม่ต้องถามครูซ้ำ
    raw_path = DATA / "teacher_raw.jsonl"
    done, prev = {}, {}
    report_path = RESULTS / "dataset_report.json"
    if raw_path.exists() and report_path.exists():  # รวมเวลาและ token ของรอบก่อนหน้าด้วย
        prev = json.loads(report_path.read_text(encoding="utf-8"))
    if raw_path.exists():
        for l in raw_path.read_text(encoding="utf-8").splitlines():
            r = json.loads(l)
            done[r["id"]] = r
    raw_f = raw_path.open("a", encoding="utf-8")
    wlock = Lock()

    def work(conv):
        if conv["id"] in done:
            return done[conv["id"]]
        system = build_system_prompt(services, info, conv["now"])
        attempts = []
        for _ in range(2):  # ตอบครั้งแรก + ตอบบทนั้นใหม่ได้ 1 ครั้ง
            r = run_dialog(teacher, system, conv)
            attempts.append({"answers": r["answers"], "fails": r["fails"], "fail_turn": r["fail_turn"]})
            if not r["fails"]:
                break
        rec = {"id": conv["id"], "kind": conv["kind"], "passed": not attempts[-1]["fails"],
               "attempts": attempts, "messages": r["messages"] if not r["fails"] else None}
        with wlock:
            raw_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            raw_f.flush()
        return rec

    t0 = time.time()
    results = {}
    with ThreadPoolExecutor(args.workers) as ex:
        futs = {ex.submit(work, c): c["id"] for c in convs}
        for n, f in enumerate(as_completed(futs), 1):
            rec = f.result()
            results[rec["id"]] = rec
            if n % 25 == 0 or n == len(convs):
                ok = sum(r["passed"] for r in results.values())
                print(f"[{n}/{len(convs)}] ผ่าน {ok} · {time.time() - t0:.0f} วินาที", flush=True)
    raw_f.close()
    elapsed = time.time() - t0

    # ---------------- เขียน Dataset
    rows = []
    for conv in convs:
        rec = results[conv["id"]]
        if not rec["passed"]:
            continue
        rows.append({"id": conv["id"], "kind": conv["kind"], "kind_th": conv["kind_th"], "now": conv["now"],
                     "messages": rec["messages"],
                     "expects": [t["expect"] for t in conv["turns"]],
                     "retried": len(rec["attempts"]) == 2})
    rows.sort(key=lambda r: r["id"])
    rng = random.Random(SEED)
    rng.shuffle(rows)
    n_val = round(len(rows) * VAL_SHARE)
    val, train = rows[:n_val], rows[n_val:]
    for name, part in (("train", train), ("val", val)):
        with (DATA / f"{name}.jsonl").open("w", encoding="utf-8") as f:
            for r in part:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # ---------------- รายงาน
    kind_th = {c["kind"]: c["kind_th"] for c in convs}
    per_kind = defaultdict(lambda: Counter())
    for c in convs:
        per_kind[c["kind"]]["total"] += 1
    for r in results.values():
        k = per_kind[r["kind"]]
        k["passed"] += r["passed"]
        k["first_try"] += r["passed"] and len(r["attempts"]) == 1
    for name, part in (("train", train), ("val", val)):
        for r in part:
            per_kind[r["kind"]][name] += 1

    first_fail = Counter()   # เหตุผลที่ครั้งแรกไม่ผ่าน (ทั้งบทที่ผ่านตอนตอบใหม่และที่ถูกทิ้ง)
    drop_reason = Counter()  # เหตุผลของบทที่ถูกทิ้ง (ครั้งที่ 2) 1 บทนับได้หลายเหตุผล
    drop_main = Counter()    # เหตุผลแรกของแต่ละบทที่ถูกทิ้ง (รวมแล้ว = จำนวนบทที่ถูกทิ้ง)
    dropped = []
    for r in sorted(results.values(), key=lambda r: r["id"]):
        if r["attempts"][0]["fails"]:
            first_fail.update({f[0] for f in r["attempts"][0]["fails"]})
        if not r["passed"]:
            last = r["attempts"][-1]
            drop_reason.update({f[0] for f in last["fails"]})
            kinds = [f[0] for f in last["fails"]]
            drop_main[next(k for k in MAIN_ORDER if k in kinds)] += 1
            dropped.append({"id": r["id"], "kind": r["kind"], "turn": last["fail_turn"],
                            "reasons": [f"{a}: {b}" for a, b in last["fails"]]})

    report = {
        "teacher_model": teacher.model,
        "settings": {"temperature": 0.3, "max_tokens": 1024, "retry_per_dialog": 1, "split_seed": SEED,
                     "val_share": VAL_SHARE, "workers": args.workers,
                     "system_prompt": "buildSystemPrompt() ของ code/web/lib/prompt.ts + วันเวลาปัจจุบันของแต่ละบท"},
        "dialogs_total": len(convs),
        "user_messages_total": sum(len(c["turns"]) for c in convs),
        "passed": len(rows),
        "passed_first_try": sum(r["passed"] and len(r["attempts"]) == 1 for r in results.values()),
        "passed_after_retry": sum(r["passed"] and len(r["attempts"]) == 2 for r in results.values()),
        "dropped": len(convs) - len(rows),
        "train": len(train), "val": len(val),
        "train_assistant_turns": sum(len(r["expects"]) for r in train),
        "val_assistant_turns": sum(len(r["expects"]) for r in val),
        "per_kind": {k: {"kind_th": kind_th[k], **dict(v)} for k, v in per_kind.items()},
        "first_attempt_fail_reasons": dict(first_fail.most_common()),
        "drop_main_reason": dict(drop_main.most_common()),
        "drop_reasons": dict(drop_reason.most_common()),
        "dropped_dialogs": dropped,
        "teacher_calls": teacher.calls + prev.get("teacher_calls", 0),
        "prompt_tokens": teacher.prompt_tokens + prev.get("prompt_tokens", 0),
        "completion_tokens": teacher.completion_tokens + prev.get("completion_tokens", 0),
        "elapsed_sec": round(elapsed + prev.get("elapsed_sec", 0), 1),
    }
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "dataset_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("dialogs_total", "passed", "passed_after_retry", "dropped", "train", "val",
                                             "drop_reasons", "elapsed_sec")}, ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
