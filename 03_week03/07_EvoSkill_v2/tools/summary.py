#!/usr/bin/env python3
"""สรุปผลของทุกการรันใน runs/ เป็นตาราง Markdown (ใช้ตอนเขียน README · ไม่เรียกโมเดล)

  python tools/summary.py [ชื่อการรัน ...]      (รันบนเครื่อง จากโฟลเดอร์ของบท)

อ่าน runs/<ชื่อ>/state.json และ legs/runs/<leg>/trials/*/grade.json (ผลรายข้อ: มีเฉพาะ Training และ Test)
"""
import glob, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def pct(x):
    return "-" if x is None else "%.1f" % (x * 100)


def fails(run, leg):
    out, notes, n = {}, {}, 0
    for g in sorted(glob.glob(os.path.join(ROOT, "runs", run, "legs", "runs", leg, "trials", "*", "grade.json"))):
        ch = json.load(open(g, encoding="utf-8")).get("checks")
        if not isinstance(ch, list):
            continue
        n += 1
        task = os.path.basename(os.path.dirname(g))
        for c in ch:
            if not c["pass"]:
                out.setdefault(c["id"], []).append(task)
                notes.setdefault(c["id"], c.get("note", ""))
    return n, out, notes


def main():
    runs = sys.argv[1:] or sorted(d for d in os.listdir(os.path.join(ROOT, "runs")) if os.path.isfile(os.path.join(ROOT, "runs", d, "state.json")))
    print("| การรัน | Validation ราย epoch | Training ราย epoch | Test ไม่มีสกิล | Test ชุดสุดท้าย (ผ่าน) | Evolver $ | Solver $ | Adaptor $ | สกิลชุดสุดท้าย | KB |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for r in runs:
        st = json.load(open(os.path.join(ROOT, "runs", r, "state.json"), encoding="utf-8"))
        L, T, E = st["legs"], st["turns"], st["epochs"]
        val = [L.get("base_val")] + [L.get("v%d_val" % k) for k in range(1, E + 1)]
        trn = [L.get("base_train")] + [L.get("v%d_train" % k) for k in range(1, E)]
        ft, bt = L.get("v%d_test" % E), L.get("base_test")
        last = T[-1] if T else {}
        print("| `%s` | %s | %s | %s | %s | %.2f | %.2f | %.2f | %s (+%d ไฟล์) | %.1f |" % (
            r, " → ".join(pct(s["score"]) if s else "-" for s in val), " → ".join(pct(s["score"]) if s else "-" for s in trn),
            pct(bt["score"]) if bt else "-", ("%s%% (%d/%d)" % (pct(ft["score"]), ft["passes"], ft["n"])) if ft else "-",
            sum(t["cost_usd"] for t in T), sum(s["cost_usd"] for s in L.values()), (st.get("adapt") or {}).get("cost_usd", 0),
            ", ".join(last.get("skills", [])), len(last.get("skill_other_files", [])), last.get("skill_md_bytes", 0) / 1024))
    for r in runs:
        st = json.load(open(os.path.join(ROOT, "runs", r, "state.json"), encoding="utf-8"))
        print("\n### %s" % r)
        ad = st.get("adapt") or {}
        if ad:
            print("Adaptor: %.0f วินาที · เครื่องมือ %d · $%.2f · reference %d ไฟล์ (เฉลย %d)" % (
                ad.get("wall_s", 0), ad.get("tool_calls", 0), ad.get("cost_usd", 0), ad["reference"]["files"], ad["reference"]["answers"]))
        for t in st["turns"]:
            print("ตา %d: %.0f วินาที · เครื่องมือ %d (Bash %d) · subagent %d · ย่อ %d · $%.2f · %s · %.1f KB · อื่น %s · ws %s · +%d ~%d -%d" % (
                t["k"], t["wall_s"], t["tool_calls"], t["bash"], t["subagents"], t["compactions"], t["cost_usd"], ",".join(t["skills"]),
                t["skill_md_bytes"] / 1024, t["skill_other_files"], t["workspace_files"], len(t["files_added"]), len(t["files_changed"]), len(t["files_removed"])))
        for leg in sorted(st["legs"]):
            s = st["legs"][leg]
            n, f, notes = fails(r, leg)
            ftxt = " · ".join("%s %d/%d" % (k, len(v), n) for k, v in sorted(f.items(), key=lambda kv: -len(kv[1]))) if n else "(ไม่มีผลรายข้อ)"
            print("- %-10s %s%% ผ่าน %d/%d · by_task %s · ไม่ผ่าน: %s" % (leg, pct(s["score"]), s["passes"], s["n"],
                                                                 {k.split("-")[0]: v for k, v in s["by_task"].items()}, ftxt or "ไม่มี"))
            if leg.endswith("_test") or leg.endswith("%d_train" % (st["epochs"] - 1)) or leg == "v1_train":
                for k, v in f.items():
                    print("    ✗ %s [%s]: %s" % (k, ",".join(sorted(set(x.split("-r")[0].split("-")[0] for x in v))), notes[k][:150]))


if __name__ == "__main__":
    for s in (sys.stdout, sys.stderr):
        s.reconfigure(encoding="utf-8", errors="replace")
    main()
