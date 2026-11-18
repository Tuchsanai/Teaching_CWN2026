#!/usr/bin/env python3
"""วัดผล Base vs Fine-tuned บน Validation Set (data/val.jsonl)

ทุกข้อความของลูกค้าในทุกบทสนทนา -> ส่งประวัติแชทเดียวกัน (system + ข้อความก่อนหน้าจาก Dataset)
ให้ทั้ง 2 โมเดลตอบ (temperature 0) แล้วตรวจด้วยเงื่อนไข "expects" ที่กำกับไว้ในแต่ละข้อ
ระหว่างวัดจะอ่าน VRAM ของเครื่อง server ผ่าน SSH (nvidia-smi) ทุก 2 วินาที
ใช้: python3 code/eval_val.py --ssh ../.lab3ssh
"""
import argparse, json, re, subprocess, threading, time
from pathlib import Path
from statistics import median
import urllib.request

ROOT = Path(__file__).resolve().parents[1]

# ---------------- ตัวตรวจ (กติกาเดียวกับตอนสร้าง Dataset: make_dataset.py) ----------------
def display_text(text):
    return re.sub(r"\[BOOKING\][\s\S]*$", "", text).rstrip()

def contains(text, token):
    if token.startswith("re:"):
        return re.search(token[3:], text, re.I) is not None
    if re.fullmatch(r"[\d-]{9,}", token):
        return token.replace("-", "") in re.sub(r"\D", "", text)
    if re.fullmatch(r"\d+%?", token):
        text = re.sub(r"(?<=\d),(?=\d{3}\b)", "", text)
        return re.search(rf"(?<![\d.,]){re.escape(token)}(?!\d)", text) is not None
    return token.lower() in text.lower()

def is_lang(text, lang):
    thai = len(re.findall(r"[฀-๿]", text)); latin = len(re.findall(r"[A-Za-z]", text))
    if thai + latin == 0:
        return False
    share = thai / (thai + latin)
    return share > 0.5 if lang == "th" else share < 0.2

MD_RE = re.compile(r"\*\*|__|^\s{0,3}#{1,6}\s|^\s*\|.*\|\s*$|```|^\s*[-*]{3,}\s*$", re.M)
TAG_LINE_RE = re.compile(r"^\[BOOKING\](\{[^\n]*\})$")
TAG_KEYS = ["customer_name", "phone", "service", "booking_time"]

def check_tag(full):
    """คืน (tag dict หรือ None, เหตุผลถ้ารูปแบบผิด)"""
    lines = [l.strip() for l in full.strip().splitlines() if l.strip()]
    m = TAG_LINE_RE.match(lines[-1]) if lines else None
    if full.count("[BOOKING]") != 1 or not m:
        return None, "แท็กต้องอยู่บรรทัดสุดท้าย บรรทัดเดียว"
    try:
        tag = json.loads(m.group(1))
    except json.JSONDecodeError:
        return None, "JSON ในแท็กอ่านไม่ได้"
    if not isinstance(tag, dict) or sorted(tag) != sorted(TAG_KEYS) or not all(str(tag[k]).strip() for k in TAG_KEYS):
        return None, "ช่องในแท็กไม่ครบ 4 ช่อง"
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}", str(tag["booking_time"])):
        return None, "booking_time ไม่ใช่ YYYY-MM-DD HH:MM"
    return tag, None

def judge(full, ex):
    shown = display_text(full)
    fails = []
    for item in ex.get("has", []):
        opts = item if isinstance(item, list) else [item]
        if not any(contains(shown, t) for t in opts):
            fails.append("ไม่มี " + " หรือ ".join(opts))
    for t in ex.get("not", []):
        if contains(shown, t):
            fails.append("มีคำต้องห้าม " + t.removeprefix("re:"))
    if ex.get("lang") and not is_lang(shown, ex["lang"]):
        fails.append("ตอบผิดภาษา")
    if ex.get("no_markdown") and MD_RE.search(full):
        fails.append("ใช้ markdown")
    bk = ex.get("booking", "none")
    has_tag = "[BOOKING]" in full
    r = {"has_tag": has_tag, "tag_format_ok": None, "tag_values_ok": None}
    if bk == "none":
        if has_tag:
            fails.append("ใส่แท็กจองทั้งที่ข้อมูลไม่ครบ")
    elif not has_tag:
        fails.append("ไม่ใส่แท็กจองทั้งที่ข้อมูลครบ")
        r["tag_format_ok"] = r["tag_values_ok"] = False
    else:
        tag, why = check_tag(full)
        r["tag_format_ok"] = tag is not None
        if tag is None:
            fails.append("แท็กจองผิดรูปแบบ: " + why); r["tag_values_ok"] = False
        else:
            bad = []
            if bk.get("name_must_contain", bk["customer_name"]) not in str(tag["customer_name"]): bad.append("ชื่อ")
            if re.sub(r"\D", "", str(tag["phone"])) != bk["phone"]: bad.append("เบอร์")
            if str(tag["service"]).strip() != bk["service"]: bad.append("บริการ")
            if tag["booking_time"] != bk["booking_time"]: bad.append("เวลา")
            r["tag_values_ok"] = not bad
            if bad: fails.append("ข้อมูลในแท็กผิด: " + ",".join(bad))
    r["ok"] = not fails
    r["fails"] = fails
    r["says_krub"] = "ครับ" in shown            # บุคลิกน้องสบายใจต้องลงท้าย ค่ะ/นะคะ ถ้ามี "ครับ" = เลียนแบบลูกค้า
    r["thai_in_english"] = ex.get("lang") == "en" and bool(re.search(r"[฀-๿]", shown))
    return r

# ---------------- เรียก server ----------------
def chat(env, model, messages, max_tokens):
    body = json.dumps({"model": model, "messages": messages, "temperature": 0, "max_tokens": max_tokens}).encode()
    req = urllib.request.Request(env["OPENAI_BASE_URL"].rstrip("/") + "/chat/completions", data=body,
                                 headers={"Content-Type": "application/json",
                                          "Authorization": "Bearer " + env["OPENAI_API_KEY"]})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=300) as resp:
        d = json.load(resp)
    return d["choices"][0]["message"]["content"] or "", d["usage"]["completion_tokens"], time.time() - t0

class VramSampler(threading.Thread):
    def __init__(self, ssh):
        super().__init__(daemon=True); self.ssh = ssh; self.samples = []; self.total = None; self.halt = False
    def run(self):
        while not self.halt:
            try:
                out = subprocess.run([self.ssh, "nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader,nounits"],
                                     capture_output=True, text=True, timeout=30).stdout.strip().splitlines()[0]
                used, total = (int(x) for x in out.split(","))
                self.samples.append(used); self.total = total
            except Exception:
                pass
            time.sleep(2)

def pct(n, d):
    return round(100 * n / d, 1) if d else None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--env", default=str(ROOT / "chatbot.env"))
    ap.add_argument("--val", default=str(ROOT / "data/val.jsonl"))
    ap.add_argument("--out", default=str(ROOT / "results/val_eval.json"))
    ap.add_argument("--ssh", default=None, help="สคริปต์ SSH ไปเครื่อง server สำหรับอ่าน VRAM")
    ap.add_argument("--max-tokens", type=int, default=1024)
    a = ap.parse_args()

    env = dict(l.split("=", 1) for l in Path(a.env).read_text().splitlines() if "=" in l and not l.startswith("#"))
    models = {"base": env["BASE_MODEL"], "finetuned": env["FT_MODEL"]}
    convs = [json.loads(l) for l in open(a.val, encoding="utf-8")]

    # หนึ่งรายการต่อหนึ่งข้อความลูกค้า: ประวัติ = ทุกข้อความก่อนหน้า (คำตอบเดิมใน Dataset) เหมือนกันทั้ง 2 โมเดล
    items = []
    for c in convs:
        k = 0
        for i, m in enumerate(c["messages"]):
            if m["role"] == "assistant":
                items.append({"id": f'{c["id"]}#{k + 1}', "kind": c["kind"], "history": c["messages"][:i],
                              "expect": c["expects"][k]}); k += 1

    sampler = VramSampler(a.ssh) if a.ssh else None
    if sampler: sampler.start()
    per_model, rows = {}, []
    for key, name in models.items():
        res, toks, secs = [], 0, 0.0
        for n, it in enumerate(items, 1):
            text, ct, dt = chat(env, name, it["history"], a.max_tokens)
            r = judge(text, it["expect"])
            r.update(id=it["id"], kind=it["kind"], answer=text, tokens=ct, seconds=round(dt, 2),
                     tok_per_s=round(ct / dt, 1) if dt else None)
            res.append(r); toks += ct; secs += dt
            print(f"[{key}] {n}/{len(items)} {'OK ' if r['ok'] else 'BAD'} {it['id']}", flush=True)
        bk = [r for r, it in zip(res, items) if it["expect"]["booking"] != "none"]
        nb = [r for r, it in zip(res, items) if it["expect"]["booking"] == "none"]
        th = [r for r, it in zip(res, items) if it["expect"].get("lang") == "th"]
        en = [r for r, it in zip(res, items) if it["expect"].get("lang") == "en"]
        per_model[key] = {
            "model": name, "n_turns": len(res),
            "correct_pct": pct(sum(r["ok"] for r in res), len(res)),
            "booking_tag_format_pct": pct(sum(bool(r["tag_format_ok"]) for r in bk), len(bk)),
            "booking_tag_values_pct": pct(sum(bool(r["tag_values_ok"]) for r in bk), len(bk)),
            "booking_tag_too_early_pct": pct(sum(r["has_tag"] for r in nb), len(nb)),
            "ends_with_krub_pct": pct(sum(r["says_krub"] for r in th), len(th)),
            "thai_in_english_pct": pct(sum(r["thai_in_english"] for r in en), len(en)),
            "denominators": {"all": len(res), "booking_ready": len(bk), "booking_not_ready": len(nb),
                             "thai": len(th), "english": len(en)},
            "tokens_per_s_overall": round(toks / secs, 1),
            "tokens_per_s_median": median(r["tok_per_s"] for r in res if r["tok_per_s"]),
            "completion_tokens": toks, "seconds": round(secs, 1),
        }
        rows.append(res)
    if sampler:
        sampler.halt = True; sampler.join(5)
    vram = {"peak_mib": max(sampler.samples), "total_mib": sampler.total, "n_samples": len(sampler.samples),
            "note": "vLLM จองหน่วยความจำล่วงหน้า (--gpu-memory-utilization 0.85); ทั้ง 2 ชื่อโมเดลอยู่บน server/GPU เดียวกัน"
            } if sampler and sampler.samples else None

    details = [{"id": b["id"], "kind": b["kind"],
                "base": {k: b[k] for k in ("ok", "fails", "answer", "tokens", "tok_per_s")},
                "finetuned": {k: f[k] for k in ("ok", "fails", "answer", "tokens", "tok_per_s")}}
               for b, f in zip(*rows)]
    out = {"settings": {"temperature": 0, "max_tokens": a.max_tokens, "val_file": "data/val.jsonl",
                        "n_conversations": len(convs), "history": "ประวัติแชทเดียวกันจาก Dataset ทุกข้อ",
                        "concurrency": 1},
           "summary": per_model, "server_vram": vram, "details": details}
    Path(a.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"summary": per_model, "server_vram": vram}, ensure_ascii=False, indent=1))

if __name__ == "__main__":
    main()
