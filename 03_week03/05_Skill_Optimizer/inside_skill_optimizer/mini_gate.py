#!/usr/bin/env python3
"""mini_gate.py - ประตูรับ (gate) ฉบับย่อ สำหรับอ่านให้เข้าใจหลักการ

  python inside_skill_optimizer/mini_gate.py v0 v1        (รันบนเครื่อง จากโฟลเดอร์ของบท)

อ่านผลการวัดจริงใน results/runs/ แล้วตัดสินด้วยสูตรเดียวกับ skillopt.py
ไม่เรียก AI ไม่ใช้โทเคน · ใช้ Python มาตรฐานเท่านั้น
"""
import glob, json, os, statistics, sys

RUNS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results", "runs")
EPS, Z = 2.0, 1.5          # เกณฑ์ขั้นต่ำ 2 จุด · ต้องดีขึ้น 1.5 เท่าของความแกว่ง


def load(label):
    """1 แถว = 1 Trial: โจทย์ ชุด คะแนน (0-100) และโทเคนขาเข้า"""
    rows = []
    for d in sorted(glob.glob(os.path.join(RUNS, label, "*"))):
        m = json.load(open(os.path.join(d, "metrics.json"), encoding="utf-8"))
        g = json.load(open(os.path.join(d, "grade.json"), encoding="utf-8"))
        rows.append({"task": m["task"], "split": m["split"], "score": g["score"] * 100,
                     "tokens": m["input_tokens"] + m["cache_read"] + m["cache_write"]})
    return rows


def mean(rows, key="score"):
    return round(statistics.mean(r[key] for r in rows), 1)      # ปัดเหมือนตาราง report


def se_of_mean(rows):
    """ความแกว่งของค่าเฉลี่ย: ดูว่าโจทย์เดียวกัน รันซ้ำแล้วคะแนนต่างกันแค่ไหน"""
    by_task = {}
    for r in rows:
        by_task.setdefault(r["task"], []).append(r["score"])
    var = statistics.mean(statistics.variance(v) for v in by_task.values())   # ทุกโจทย์รันจำนวนรอบเท่ากัน
    return (var / len(rows)) ** 0.5


def threshold(base, cand):
    se_diff = (se_of_mean(base) ** 2 + se_of_mean(cand) ** 2) ** 0.5           # ความแกว่งของ "ผลต่าง" สองรุ่น
    return max(EPS, Z * se_diff), se_diff


def main():
    for st in (sys.stdout, sys.stderr):
        if hasattr(st, "reconfigure"):
            st.reconfigure(encoding="utf-8", errors="replace")
    base_name, cand_name = sys.argv[1], sys.argv[2]
    base, cand = load(base_name), load(cand_name)
    ok = True
    for split in ("train", "val"):                                # ข้อ 1-2: แต่ละชุดต้องไม่แย่ลงเกินเกณฑ์
        b = [r for r in base if r["split"] == split]
        c = [r for r in cand if r["split"] == split]
        t, _ = threshold(b, c)
        diff = mean(c) - mean(b)
        print("%-5s %.1f%% -> %.1f%% (%+.1f) เกณฑ์ %.1f จุด%s" % (
            split, mean(b), mean(c), diff, t, "  X ลดลงเกินเกณฑ์" if diff < -t else ""))
        ok = ok and diff >= -t
    if ok:                                                        # ข้อ 3: คะแนนรวมดีขึ้นเกินเกณฑ์ หรือถูกลง 10%
        t, se = threshold(base, cand)
        gain = mean(cand) - mean(base)
        cost = (mean(cand, "tokens") / mean(base, "tokens") - 1) * 100
        print("รวม   %.1f%% -> %.1f%% (%+.1f) เกณฑ์ %.1f จุด = ค่าที่มากกว่าระหว่าง %.1f กับ %.1f x %.1f" % (
            mean(base), mean(cand), gain, t, EPS, Z, se))
        print("โทเคนขาเข้าต่อ Trial %.0f -> %.0f (%+.0f%%)" % (mean(base, "tokens"), mean(cand, "tokens"), cost))
        ok = gain > t or cost <= -10
    print("ผล: %s %s แทน %s" % ("ACCEPT รับ" if ok else "REJECT ไม่รับ", cand_name, base_name))


if __name__ == "__main__":
    main()
