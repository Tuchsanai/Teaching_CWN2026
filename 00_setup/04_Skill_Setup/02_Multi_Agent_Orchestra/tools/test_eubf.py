#!/usr/bin/env python3
"""unit test ของอัลกอริทึม EUBF (ใช้ฟังก์ชันจริงจาก orch.py) — รัน: python3 tools/test_eubf.py"""
import copy, os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import orch
from orch import choose_account, make_state, reserve_on, critical_ranks, FACTORS, plan_assignments, capacity

CFG = copy.deepcopy(orch.DEFAULT_CFG)

def acc(name, h_w, hours, h_s=100, rs=2.0, rw=0.25, slots=4, used=0, is_orch=False, bonus=0.0, sreset_h=None):
    kind = "cyolo" if name.startswith("cyolo") else "yolo"
    return make_state(name, kind, rs, rw, h_s, h_w, hours, slots, used, is_orch, bonus, 100, sreset_h)

def pick(cost, states, crit=0.5, cfg=CFG, **kw):
    c = choose_account(cost, crit, states, cfg, **kw)
    return c[0]["account"] if c else None

class TestEUBF(unittest.TestCase):
    def test_1_feasibility_job_must_fit(self):
        """งานต้องปิดได้: งาน 10M tok ต้องใช้ 13%×... ของสัปดาห์ → บัญชีที่เหลือไม่พอถูกตัดทิ้ง"""
        st = [acc("yolo1", h_w=2, hours=10), acc("yolo2", h_w=60, hours=150)]
        c = choose_account(10.0, 0.5, st, CFG)          # qw = 1.3*0.25*10 = 3.25% > 2%
        self.assertEqual([x["account"] for x in c], ["yolo2"])

    def test_2_expiring_first(self):
        """โควตาเท่ากัน แต่ yolo1 หมดอายุใน 5 ชม. → ใช้ yolo1 ก่อน (use-it-or-lose-it)"""
        st = [acc("yolo1", h_w=40, hours=5), acc("yolo2", h_w=40, hours=150)]
        self.assertEqual(pick(1.0, st), "yolo1")

    def test_3_best_fit_big_job_to_big_bin(self):
        """งานใหญ่ (40M) ใส่ได้แค่ถังใหญ่ · งานเล็กเติมถังเล็กที่ใกล้หมดอายุ → ไม่เปลืองถังใหญ่"""
        st = [acc("yolo1", h_w=10, hours=20, rs=1.0), acc("yolo2", h_w=95, hours=150, rs=1.0)]
        self.assertEqual(pick(30.0, st), "yolo2")         # สัปดาห์ 9.75% > 10−2 (เผื่อ 2%) · 5ชม. 39% ผ่าน
        self.assertEqual(pick(2.0, st), "yolo1")          # เล็ก → ถังเล็ก (ใกล้หมดอายุกว่า + พอดีกว่า)
        self.assertEqual(choose_account(40.0, 0.5, [acc("yolo2", h_w=95, hours=150)], CFG), [])  # 5ชม. 104% → ไม่มีใครรับ

    def test_4_session_window_guard(self):
        """สัปดาห์เหลือเยอะ แต่หน้าต่าง 5 ชม. ใกล้เต็ม → ห้ามรับงานที่ล้น 5 ชม."""
        st = [acc("yolo1", h_w=90, hours=5, h_s=10), acc("yolo2", h_w=50, hours=150, h_s=100)]
        self.assertEqual(pick(3.0, st), "yolo2")          # qs = 1.3*2*3 = 7.8% > 10−3.6

    def test_5_orchestrator_reserve(self):
        """บัญชีของ orchestrator ต้องเหลือสำรอง (orch_min_headroom+5) หลังรับงาน"""
        st = [acc("yolo1", h_w=22.5, hours=5, is_orch=True), acc("yolo2", h_w=60, hours=150)]
        self.assertEqual(pick(2.0, st), "yolo2")          # yolo1: 22.5 − เผื่อ 2 − สำรอง 20 = 0.5 < 0.65 → ไม่รับ
        st[0]["is_orch"] = False
        self.assertEqual(pick(2.0, st), "yolo1")          # ถ้าไม่ใช่ orchestrator → รับได้ (ใกล้หมดอายุกว่า)

    def test_6_reserve_prevents_overbooking(self):
        """จองโควตาทีละงาน: 3 งาน × 6M ลงบัญชีที่มีที่พอแค่ 2 งาน → งานที่ 3 ไปบัญชีอื่น"""
        st = [acc("yolo1", h_w=6.2, hours=5), acc("yolo2", h_w=90, hours=150)]
        got = []
        for _ in range(3):
            c = choose_account(6.0, 0.5, st, CFG)[0]       # qw = 1.95% ต่องาน
            got.append(c["account"]); reserve_on(st, c["account"], c["qs"], c["qw"])
        self.assertEqual(got, ["yolo1", "yolo1", "yolo2"])

    def test_7_slots_and_load(self):
        """slot เต็มแล้วไม่รับ · โหลดสูงได้คะแนนลดลง"""
        st = [acc("yolo1", h_w=50, hours=50, slots=2, used=2), acc("yolo2", h_w=50, hours=50)]
        self.assertEqual(pick(1.0, st), "yolo2")
        st = [acc("yolo1", h_w=50, hours=50, used=3), acc("yolo2", h_w=50, hours=50, used=0)]
        self.assertEqual(pick(1.0, st), "yolo2")

    def test_8_critical_path_rank(self):
        """งานที่มีงานอื่นรอยาวกว่าได้ rank สูงกว่า"""
        tasks = [{"id": "A", "depends_on": []}, {"id": "B", "depends_on": ["A"]}, {"id": "C", "depends_on": ["B"]},
                 {"id": "X", "depends_on": []}]
        r = critical_ranks(tasks, lambda t: 1.0)
        self.assertEqual(r["A"], 1.0); self.assertGreater(r["A"], r["X"]); self.assertGreater(r["B"], r["C"])

    def test_9_speed_for_critical_tasks(self):
        """งานวิกฤต (crit=1) ไป yolo ที่เร็วกว่า เมื่อปัจจัยอื่นเท่ากัน"""
        st = [acc("cyolo1", h_w=50, hours=50), acc("yolo1", h_w=50, hours=50)]
        self.assertEqual(pick(1.0, st, crit=1.0), "yolo1")

    def test_10_toggle_and_add_factors(self):
        """เพิ่ม/ลดตัวแปรได้: น้ำหนัก 0 = ปิด · เพิ่มตัวแปรใหม่ใน FACTORS แล้วใส่น้ำหนัก"""
        cfg = copy.deepcopy(CFG); cfg["weights"] = {"urgency": 0.0, "fit": 0.0, "session": 1.0, "speed": 0, "load": 0, "bonus": 0}
        st = [acc("yolo1", h_w=40, hours=5, h_s=50), acc("yolo2", h_w=40, hours=150, h_s=100)]
        c = choose_account(1.0, 0.5, st, cfg)
        self.assertEqual(c[0]["account"], "yolo2")       # ปิด urgency → ดูแค่ session
        self.assertNotIn("urgency", c[0]["parts"])
        FACTORS["cheap"] = lambda s, x: 1.0 if s["kind"] == "cyolo" else 0.0   # ตัวแปรใหม่: ชอบ cyolo
        try:
            cfg["weights"] = {"cheap": 1.0}
            st = [acc("yolo1", h_w=50, hours=5), acc("cyolo1", h_w=50, hours=150)]
            self.assertEqual(pick(1.0, st, cfg=cfg), "cyolo1")
        finally:
            del FACTORS["cheap"]

    def test_11_bonus_from_accounts_json(self):
        """ตัวแปร bonus (จาก accounts.json) เปิดใช้ด้วยน้ำหนัก > 0"""
        cfg = copy.deepcopy(CFG); cfg["weights"]["bonus"] = 0.5
        st = [acc("yolo1", h_w=50, hours=100), acc("yolo2", h_w=50, hours=100, bonus=1.0)]
        self.assertEqual(pick(1.0, st, cfg=cfg), "yolo2")

    def test_13_plan_limit_below_switch_limit(self):
        """เส้นวางแผน (มี σ) อยู่ใต้เส้นย้ายงานเสมอ: รับงานเต็ม capacity แล้ว ค่าคาดการณ์ (ไม่มี σ) ยังไม่ถึงเส้นย้าย → ไม่ย้ายไปมา"""
        from orch import margin
        for h_w in (7, 30, 90):
            s = acc("yolo1", h_w=h_w, hours=50)
            cap = capacity(s, CFG)
            proj_w = (100 - h_w) + cap * s["rw"]                  # ใช้จริงตามค่าประเมิน (ไม่คูณ σ)
            self.assertLessEqual(proj_w, 100 - margin(s, CFG, "week"))

    def test_14_session_reset_aware(self):
        """⑦ 5 ชม. เหลือ 20% แต่จะรีเซ็ตใน 0.2 ชม. → งาน 10M (5 ชม. ใช้ 26%) รับได้ เพราะส่วนใหญ่ทำหลังรีเซ็ต"""
        st = [acc("yolo1", h_w=90, hours=100, h_s=20, sreset_h=0.2)]
        self.assertEqual(pick(10.0, st), "yolo1")
        st = [acc("yolo1", h_w=90, hours=100, h_s=20, sreset_h=4.5)]   # รีเซ็ตอีกนาน → รับไม่ได้
        self.assertEqual(pick(10.0, st), None)

    def test_15_planned_relay(self):
        """⑨ ไม่มีใครปิดงานคนเดียวได้ แต่รวมกันพอ → เริ่มที่บัญชีที่ดีสุด (โหมด relay) แทนการรอ"""
        st = [acc("yolo1", h_w=15, hours=10), acc("yolo2", h_w=15, hours=100)]   # คนละ ~37M · งาน 70M
        plan = plan_assignments([{"id": "BIG", "need": 70.0, "crit": 1.0}], st, CFG, 12, 5)
        self.assertEqual(len(plan), 1); self.assertEqual(plan[0][2], "relay")
        self.assertEqual(plan[0][1]["account"], "yolo1")                 # ใกล้หมดอายุกว่า เริ่มก่อน
        st = [acc("yolo1", h_w=8, hours=10), acc("yolo2", h_w=8, hours=100)]     # รวมกันยังไม่พอ + มีงานอื่นรันอยู่ → รอ
        self.assertEqual(plan_assignments([{"id": "BIG", "need": 70.0, "crit": 1.0}], st, CFG, 11, 5), [])
        st = [acc("yolo1", h_w=8, hours=10), acc("yolo2", h_w=8, hours=100)]     # ไม่มีใครรันเลย → ห้ามค้าง เริ่มแบบ best-effort
        plan = plan_assignments([{"id": "BIG", "need": 70.0, "crit": 1.0}], st, CFG, 12, 5)
        self.assertEqual(len(plan), 1); self.assertEqual(plan[0][2], "relay")

    def test_16_mrv_most_constrained_first(self):
        """⑧ งาน "only cyolo" มีทางเลือกเดียว ได้เลือกก่อน แม้ rank ต่ำกว่า → งานยืดหยุ่นไม่แย่ง slot สุดท้าย"""
        st = [acc("cyolo1", h_w=60, hours=5, slots=1), acc("yolo1", h_w=60, hours=150, slots=1)]
        ready = [{"id": "FLEX", "need": 1.0, "crit": 1.0}, {"id": "CX", "need": 1.0, "crit": 0.2, "only": "cyolo"}]
        plan = {tid: c["account"] for tid, c, mode, _ in plan_assignments(ready, st, CFG, 12, 5)}
        self.assertEqual(plan, {"CX": "cyolo1", "FLEX": "yolo1"})

    def test_12_nobody_fits(self):
        """ไม่มีบัญชีไหนปิดงานได้ → คืนรายการว่าง (orchestrator ต้องแบ่งงาน)"""
        st = [acc("yolo1", h_w=3, hours=10), acc("yolo2", h_w=4, hours=150)]
        self.assertEqual(choose_account(50.0, 0.5, st, CFG), [])

if __name__ == "__main__":
    unittest.main(verbosity=2)
