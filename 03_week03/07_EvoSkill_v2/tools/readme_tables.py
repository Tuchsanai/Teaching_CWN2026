#!/usr/bin/env python3
"""ตารางผลของ README สร้างจาก runs/ (ไม่มีตัวเลขที่พิมพ์เอง)

  python tools/readme_tables.py            พิมพ์ทุกตาราง
  ใช้โดยผู้เขียนบทเรียนตอนอัปเดต README หลังรันใหม่
"""
import glob, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALL = ["e1", "e2", "v1", "n1", "n2", "p1", "p2", "f1", "f2", "f3", "h1", "h2"]
SETTING = {"e": "เห็นเฉลยของ Training", "v": "เห็นเฉลยของ Training", "n": "เฉลย + หมายเหตุ 1 ประโยค", "p": "เห็นแต่คะแนน",
           "f": "เซสชันใหม่ทุก epoch", "h": "haiku ทั้ง Solver และ Evolver"}


def st(r):
    return json.load(open(os.path.join(ROOT, "runs", r, "state.json"), encoding="utf-8"))


def pct(x):
    return "%.1f%%" % (x * 100)


def checks(r, leg):
    out, n, notes = {}, 0, {}
    for g in sorted(glob.glob(os.path.join(ROOT, "runs", r, "legs", "runs", leg, "trials", "*", "grade.json"))):
        ch = json.load(open(g, encoding="utf-8")).get("checks")
        if not isinstance(ch, list):
            continue
        n += 1
        for c in ch:
            a, b = out.get(c["id"], (0, 0))
            out[c["id"]] = (a + (1 if c["pass"] else 0), b + 1)
            if not c["pass"]:
                notes.setdefault(c["id"], c.get("note", ""))
    return out, notes


def fail(c, cid):
    return "ไม่มีข้อตรวจนี้" if cid not in c else ("ผ่าน %d/%d" % c[cid] if c[cid][0] == c[cid][1] else "ไม่ผ่าน %d/%d" % (c[cid][1] - c[cid][0], c[cid][1]))


def val(s):
    L, E = s["legs"], s["epochs"]
    return " → ".join("%.1f" % (L[x]["score"] * 100) for x in ["base_val"] + ["v%d_val" % k for k in range(1, E + 1)])


def all_runs():
    print("| การตั้งค่า | การรัน | Validation ราย epoch (%) | Test: ไม่มีสกิล → ชุดสุดท้าย | ผ่านครบ | `policy` ของ Training (epoch 2) | `tests` ใน Test | `x2-refund` ใน Test | Evolver 3 ตา |")
    print("|---|---|---|---|---|---|---|---|---|")
    for r in ALL:
        s = st(r)
        L, E = s["legs"], s["epochs"]
        ct, nt = checks(r, "v%d_test" % E)
        c2, _ = checks(r, "v%d_train" % (E - 1))
        x2 = L["v%d_test" % E]["by_task"]["x2-refund"]
        note = re.sub(r" ·.*", "", nt.get("tests", ""))
        print("| %s | `%s` | %s | %s → **%s** | %d/%d | %s | %s | %s | $%.2f |" % (
            SETTING[r[0]], r, val(s), pct(L["base_test"]["score"]), pct(L["v%d_test" % E]["score"]), L["v%d_test" % E]["passes"], L["v%d_test" % E]["n"],
            fail(c2, "policy"), fail(ct, "tests") + ((" · `%s`" % note) if note else ""),
            "ผิด %d/3" % sum(1 for v in x2 if v < 0.999), sum(t["cost_usd"] for t in s["turns"])))
    tot = sum(sum(l["n"] for l in st(r)["legs"].values()) for r in ALL)
    print("\nรวม rollout %d · ตาของ Evolver %d · Adaptor %d" % (tot, sum(len(st(r)["turns"]) for r in ALL), len(ALL)))
    print("ต้นทุน: Solver $%.2f · Evolver $%.2f · Adaptor $%.2f" % (
        sum(sum(l["cost_usd"] for l in st(r)["legs"].values()) for r in ALL), sum(sum(t["cost_usd"] for t in st(r)["turns"]) for r in ALL),
        sum(st(r)["adapt"]["cost_usd"] for r in ALL)))
    for r in ALL:
        s = st(r)
        print(r, "บัญชี", ",".join(s["cfg"]["accounts"]), "· Evolver นาที %.1f" % (sum(t["wall_s"] for t in s["turns"]) / 60),
              "· สกิล", len(s["turns"][-1]["skills"]), "ตัว %.1f KB" % (s["turns"][-1]["skill_md_bytes"] / 1024), "· ไฟล์แนบ", len(s["turns"][-1]["skill_other_files"]),
              "· ws", len(s["turns"][-1]["workspace_files"]), "· rerun", [t["rerun_old_scripts"] for t in s["turns"]],
              "· นาทีต่อตา", ["%.1f" % (t["wall_s"] / 60) for t in s["turns"]], "· $ต่อตา", ["%.2f" % t["cost_usd"] for t in s["turns"]],
              "· Solver $%.2f" % sum(l["cost_usd"] for l in s["legs"].values()))


def noise1(runs):
    print("| การรัน · leg | โจทย์ | คะแนน 3 ครั้ง |\n|---|---|---|")
    for r in runs:
        s = st(r)
        for leg, l in s["legs"].items():
            for t, v in l["by_task"].items():
                if max(v) - min(v) > 1e-9:
                    print("| `%s` · %s | `%s` | %s |" % (r, leg, t.split("-", 1)[1], " · ".join("%g" % round(x, 2) for x in v)))


def noise2(runs):
    print("| การรัน | เทียบบน Validation | ค่าเฉลี่ย 3 ครั้ง | รับ | เสมอ (ไม่รับ) | ต่ำกว่า (ไม่รับ) |\n|---|---|---|---|---|---|")
    for r in runs:
        for line in open(os.path.join(ROOT, "runs", r, "noise.txt"), encoding="utf-8"):
            c = [x.strip() for x in line.strip().strip("|").split("|")]
            if len(c) == 6 and c[0] == "Validation":
                print("| `%s` | %s | %s | %s | %s | %s |" % (r, c[1], c[2], ("**%s**" % c[3]) if c[3] not in ("0/9", "9/9") else c[3], c[4], c[5]))


if __name__ == "__main__":
    for s_ in (sys.stdout, sys.stderr):
        s_.reconfigure(encoding="utf-8", errors="replace")
    all_runs()
    print()
    noise1(["e1", "n1", "p1", "f1", "h1"])
    print()
    noise2(["e1", "n1", "p1", "f1", "h1"])
    print("\n(การรันซ้ำ)")
    noise2(["e2", "v1", "n2", "p2", "f2", "f3", "h2"])
