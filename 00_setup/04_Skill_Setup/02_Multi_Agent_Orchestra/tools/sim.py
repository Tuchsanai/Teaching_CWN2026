#!/usr/bin/env python3
"""sim.py — จำลองการแจกงานให้หลายบัญชี เทียบ EUBF (โค้ดเดียวกับ orch.py) กับวิธีพื้นฐาน

รัน: python3 tools/sim.py [--seeds 200] [--out sim_result.json]

แบบจำลอง (เวลาเดินทีละ 1 นาที):
- บัญชี: โควตา 5 ชม. (เริ่มนับเมื่อใช้ครั้งแรก แล้วรีเซ็ตหลัง 5 ชม.) + โควตาสัปดาห์ (รีเซ็ตเมื่อ "หมดอายุ")
  อัตรา % ต่อ 1M token จริงต่างจากที่ scheduler คิดไว้ ±30% (scheduler เรียนรู้จากงานที่จบแล้ว — ⑥)
- งาน: DAG แบบโปรเจกต์เว็บจริง (scaffold → งานขนาน → รวม → ทดสอบ) ขนาด S/M/L
  โทเคนจริง = ค่าประเมิน × lognormal(σ=0.35) · ความเร็ว yolo 0.12M/นาที, cyolo 0.08M/นาที
- งานชนเพดานกลางทาง (limit) → งานหยุด เสียเวลา 5 นาที + งานที่ยังไม่ commit 15% ต้องทำใหม่
- ย้ายงานล่วงหน้า (เฉพาะ EUBF ⑤) → เสียเวลา 2 นาที + 3% (อ่าน HANDOFF แล้วทำต่อ)
ตัวชี้วัด: เวลาจบโปรเจกต์ · จำนวนครั้งชนเพดาน · โควตาที่หมดอายุทิ้ง (สูญเปล่า) · โควตาของบัญชีอายุยาวที่ถูกใช้
"""
import argparse, copy, json, math, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import orch
from orch import choose_account, make_state, reserve_on, critical_ranks, plan_assignments, margin, session_burn

CFG = copy.deepcopy(orch.DEFAULT_CFG)
CFG_BASIC = copy.deepcopy(CFG); CFG_BASIC["relay"] = False          # EUBF รุ่นแรก (ไม่มี ⑦⑨)
POLICY_SMART = {"EUBF": True, "EUBF-basic": False}
SIZE = CFG["size_mtok"]
SPEED = {"yolo": 0.12, "cyolo": 0.08}       # M weighted token ต่อนาที ต่อ worker

def project_dag(rng, scale=1.0):
    """โปรเจกต์ขนาดเท่า BuildMart: T01 → 12 งานขนาน (บางงานต่อกัน) → รวม 2 งาน → ทดสอบ 1 งาน"""
    T = [{"id": "T01", "size": "M", "dep": []}]
    for i in range(2, 14):
        dep = ["T01"] if i < 10 else ["T01", f"T{i-7:02d}"]
        T.append({"id": f"T{i:02d}", "size": rng.choice("SMML"), "dep": dep})
    T.append({"id": "T14", "size": "M", "dep": [f"T{i:02d}" for i in range(2, 9)]})
    T.append({"id": "T15", "size": "M", "dep": [f"T{i:02d}" for i in range(9, 14)]})
    T.append({"id": "T16", "size": "L", "dep": ["T14", "T15"]})
    for t in T:
        t["est"] = SIZE[t["size"]] * scale
        t["true"] = t["est"] * math.exp(rng.gauss(0, 0.35))
    return T

SCEN = {
    # ชื่อ: [(บัญชี, ใช้ไป5ชม., ใช้ไปสัปดาห์, ชม.ก่อนหมดอายุ, แพลน)]
    "A_สบาย (โควตาเหลือเยอะทุกบัญชี)": [("yolo1", 0, 1, 150, "max"), ("yolo2", 0, 4, 86, "team"),
                                        ("yolo3", 6, 3, 110, "team"), ("cyolo1", 0, 0, 160, "pro")],
    "B_มีบัญชีใกล้หมดอายุ": [("yolo1", 0, 70, 3, "team"), ("yolo2", 0, 20, 150, "team"),
                             ("yolo3", 0, 30, 120, "team"), ("cyolo1", 0, 10, 160, "pro")],
    "C_โควตาตึง (ต้องเลือกให้พอดี)": [("yolo1", 0, 97, 40, "team"), ("yolo2", 75, 60, 100, "team"),
                                      ("yolo3", 0, 94, 20, "team"), ("cyolo1", 0, 90, 150, "pro")],
    "D_5ชม.ใกล้เต็ม": [("yolo1", 80, 20, 60, "team"), ("yolo2", 70, 30, 90, "team"),
                         ("yolo3", 10, 40, 130, "team"), ("cyolo1", 0, 20, 160, "pro")],
    "E_โปรเจกต์ใหญ่ 3 เท่า": [("yolo1", 0, 1, 150, "max"), ("yolo2", 0, 4, 86, "team"),
                               ("yolo3", 6, 3, 110, "team"), ("cyolo1", 0, 0, 160, "pro")],
}
SCEN["F_5ชม.เกือบเต็มแต่ใกล้รีเซ็ต"] = [("yolo1", 88, 10, 150, "team", 4.6), ("yolo2", 90, 10, 90, "team", 4.7),
                                     ("yolo3", 86, 10, 120, "team", 4.5), ("cyolo1", 92, 10, 160, "pro", 4.8)]
SCEN["G_งานใหญ่กว่าทุกบัญชี (ต้องส่งต่อ)"] = [("yolo1", 0, 90, 150, "team"), ("yolo2", 0, 90, 90, "team"),
                                        ("yolo3", 0, 90, 120, "team"), ("cyolo1", 0, 93, 160, "pro")]
SCALE = {"E_โปรเจกต์ใหญ่ 3 เท่า": 3.0, "G_งานใหญ่กว่าทุกบัญชี (ต้องส่งต่อ)": 3.0}
TRUE_RATE = {"max": (1.0, 0.12), "team": (2.0, 0.25), "pro": (1.0, 0.15)}   # % ต่อ 1M (5ชม., สัปดาห์)

class Acc:
    def __init__(self, name, su, wu, hours, plan, rng, sess_age_h=0.0):
        self.name, self.kind, self.plan = name, ("cyolo" if name.startswith("cyolo") else "yolo"), plan
        self.su, self.wu, self.exp, self.hours0 = float(su), float(wu), hours * 60, hours
        rs, rw = TRUE_RATE[plan]
        self.rs, self.rw = rs * rng.uniform(0.7, 1.3), rw * rng.uniform(0.7, 1.3)   # อัตราจริง (scheduler ไม่รู้)
        self.est_rs, self.est_rw = rs, rw                                            # สิ่งที่ scheduler เชื่อ
        self.sess_start = -int(sess_age_h * 60) if su > 0 else None
        self.wasted = 0.0; self.used_week = 0.0; self.expired = False
    def tick(self, t):
        if self.sess_start is not None and t - self.sess_start >= 300: self.su, self.sess_start = 0.0, None
        if not self.expired and t >= self.exp:
            self.wasted = max(0.0, 100 - self.wu); self.wu = 0.0; self.expired = True; self.exp = t + 7 * 24 * 60
    def use(self, t, mtok):
        if self.sess_start is None: self.sess_start = t
        self.su += mtok * self.rs; self.wu += mtok * self.rw
        if not self.expired: self.used_week += mtok * self.rw

def run(policy, scen, seed):
    rng = random.Random(seed)
    tasks = project_dag(rng, SCALE.get(scen, 1.0))
    accs = [Acc(*a[:5], rng, *a[5:]) for a in SCEN[scen]]
    by = {t["id"]: t for t in tasks}
    for t in tasks: t.update(done=0.0, status="todo", acc=None, wait=0, hits=0)
    t_min, rr, hits, moves, learned = 0, 0, 0, 0, []
    while any(t["status"] != "done" for t in tasks) and t_min < 72 * 60:
        for a in accs: a.tick(t_min)
        # ---- dispatch
        ready = [t for t in tasks if t["status"] == "todo" and all(by[d]["status"] == "done" for d in t["dep"]) and t["wait"] <= t_min]
        running = [t for t in tasks if t["status"] == "run"]
        ranks = critical_ranks([{"id": t["id"], "depends_on": t["dep"]} for t in tasks],
                               lambda x: 0 if by[x["id"]]["status"] == "done" else by[x["id"]]["est"] - by[x["id"]]["done"])
        if policy.startswith("EUBF"): ready.sort(key=lambda t: (-ranks[t["id"]], -t["est"]))
        else: ready.sort(key=lambda t: t["id"])
        states = []
        for a in accs:
            run_on = [t for t in running if t["acc"] is a]
            pend = sum(max(t["est"] - t["done"], 0.15 * t["est"]) for t in run_on)
            hrs = max(1.0, (a.exp - t_min) / 60)
            sr = None if a.sess_start is None else max(0.0, (300 - (t_min - a.sess_start)) / 60)
            states.append(make_state(a.name, a.kind, a.est_rs, a.est_rw, 100 - a.su - pend * a.est_rs,
                                     100 - a.wu - pend * a.est_rw, hrs, 4 if a.kind == "yolo" else 3, len(run_on),
                                     sreset_h=sr if POLICY_SMART.get(policy) else None))
        n_run = len(running)
        if policy.startswith("EUBF"):
            cfg = CFG if POLICY_SMART.get(policy) else CFG_BASIC
            items = [{"id": t["id"], "need": max(t["est"] - t["done"], 0.3 * t["est"]), "crit": ranks[t["id"]],
                      "avoid": {t["avoid"]} if t.get("avoid") else ()} for t in ready]
            for tid, c, mode, _ in plan_assignments(items, states, cfg, CFG["max_agents"] - n_run, 0):
                t = by[tid]; t["status"], t["acc"] = "run", next(a for a in accs if a.name == c["account"])
            ready = []
        for t in ready:
            if n_run >= CFG["max_agents"]: break
            need = max(t["est"] - t["done"], 0.3 * t["est"])
            free = [s for s in states if s["used"] < s["slots"]]
            if not free: break
            if policy == "EUBF":
                c = choose_account(need, ranks[t["id"]], states, CFG, avoid={t["avoid"]} if t.get("avoid") else ())
                if not c: continue
                pick = c[0]["account"]; reserve_on(states, pick, c[0]["qs"], c[0]["qw"])
            elif policy == "round-robin":
                pick = free[rr % len(free)]["account"]; rr += 1
            elif policy == "most-headroom":
                s = max(free, key=lambda s: min(s["h_s"], s["h_w"])); pick = s["account"]
                reserve_on(states, pick, CFG["safety"] * s["rs"] * need, CFG["safety"] * s["rw"] * need)
            else:  # random
                pick = rng.choice(free)["account"]
            for s in states:
                if s["account"] == pick and policy != "EUBF" and policy != "most-headroom": s["used"] += 1
            t["status"], t["acc"] = "run", next(a for a in accs if a.name == pick); n_run += 1
        # ---- run 1 minute
        for t in [t for t in tasks if t["status"] == "run"]:
            a = t["acc"]
            step = min(SPEED[a.kind], t["true"] - t["done"])
            if a.su + step * a.rs > 100 or a.wu + step * a.rw > 100:     # ชนเพดานกลางงาน
                hits += 1; t["hits"] += 1
                t["done"] = max(0.0, t["done"] - 0.15 * t["true"]); t["status"] = "todo"; t["wait"] = t_min + 5; t["acc"] = None
                continue
            a.use(t_min, step); t["done"] += step
            if t["done"] >= t["true"] - 1e-9:
                t["status"] = "done"
                # ⑥ เรียนรู้อัตรา (EUBF เท่านั้น) — ปรับความเชื่อเข้าหาค่าจริง
                if policy.startswith("EUBF"):
                    a.est_rs = 0.6 * a.est_rs + 0.4 * a.rs; a.est_rw = 0.6 * a.est_rw + 0.4 * a.rw
        # ---- ⑤ ย้ายงานล่วงหน้า (EUBF)
        if policy.startswith("EUBF"):
            for a in accs:
                run_on = [t for t in tasks if t["status"] == "run" and t["acc"] is a]
                if not run_on: continue
                rem = lambda t: max(t["est"] - t["done"], (t["true"] - t["done"]) if t["done"] > 0.15 * t["est"] else 0.15 * t["est"])
                sr = None if a.sess_start is None else max(0.0, (300 - (t_min - a.sess_start)) / 60)
                if not POLICY_SMART.get(policy): sr = None
                proj_s = a.su + session_burn([rem(t) for t in run_on], a.est_rs, sr, CFG, a.kind)
                proj_w = a.wu + sum(rem(t) for t in run_on) * a.est_rw
                st_a = {"rs": a.est_rs, "rw": a.est_rw, "kind": a.kind}
                if proj_s > 100 - margin(st_a, CFG, "session", len(run_on)) or proj_w > 100 - margin(st_a, CFG, "week", len(run_on)):
                    t = max(run_on, key=rem)
                    others = [make_state(b.name, b.kind, b.est_rs, b.est_rw, 100 - b.su, 100 - b.wu,
                                         max(1, (b.exp - t_min) / 60), 4, 0) for b in accs if b is not a]
                    cfg = CFG if POLICY_SMART.get(policy) else CFG_BASIC
                    if choose_account(rem(t), ranks[t["id"]], others, cfg, need_slot=False,
                                      partial=0.3 if POLICY_SMART.get(policy) else 0.0):
                        moves += 1; t["done"] = max(0.0, t["done"] - 0.03 * t["true"])
                        t["status"], t["acc"], t["wait"], t["avoid"] = "todo", None, t_min + 2, a.name
        t_min += 1
    unfinished = sum(t["status"] != "done" for t in tasks)
    tot = sum(a.used_week for a in accs) or 1e-9
    soon = sum(a.used_week for a in accs if a.hours0 <= 48)
    has_soon = any(a.hours0 <= 48 for a in accs)
    return {"minutes": t_min, "limit_hits": hits, "moves": moves, "unfinished": unfinished,
            "expiring_share": round(100 * soon / tot, 1) if has_soon else None,
            "long_lived_used": round(sum(a.used_week for a in accs if a.hours0 >= 100), 2)}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--seeds", type=int, default=200); ap.add_argument("--out")
    ap.add_argument("--only", help="รันเฉพาะสถานการณ์ที่ชื่อขึ้นต้นด้วยตัวอักษรนี้ เช่น G")
    a = ap.parse_args()
    pols = ["EUBF", "EUBF-basic", "most-headroom", "round-robin", "random"]
    res = {}
    for sc in SCEN:
        if a.only and not sc.startswith(a.only): continue
        res[sc] = {}
        for p in pols:
            rs = [run(p, sc, s) for s in range(a.seeds)]
            m = lambda k: None if rs[0][k] is None else round(sum(r[k] for r in rs) / len(rs), 2)
            res[sc][p] = {k: m(k) for k in rs[0]}
            res[sc][p]["fail_runs_pct"] = round(100 * sum(r["unfinished"] > 0 for r in rs) / len(rs), 1)
    print(f"seeds/สถานการณ์ = {a.seeds}\n")
    for sc, v in res.items():
        print(f"## {sc}")
        print("| วิธี | เวลาจบ (นาที) | ชนเพดานกลางงาน (ครั้ง) | ย้ายงานล่วงหน้า | รันที่งานไม่จบ (%) | ใช้จากบัญชีใกล้หมดอายุ (% ของที่ใช้) | ใช้โควตาบัญชีอายุยาว (%) |")
        print("|---|---|---|---|---|---|---|")
        for p, r in v.items():
            es = "-" if r["expiring_share"] is None else r["expiring_share"]
            print(f"| {p} | {r['minutes']} | {r['limit_hits']} | {r['moves']} | {r['fail_runs_pct']} | {es} | {r['long_lived_used']} |")
        print()
    if a.out: json.dump(res, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

if __name__ == "__main__":
    main()
