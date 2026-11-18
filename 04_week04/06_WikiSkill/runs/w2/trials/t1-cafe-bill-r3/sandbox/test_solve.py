import json
import subprocess
import sys
import unittest

from solve import cafe_bill


def run(payload):
    return subprocess.run([sys.executable, "solve.py"], input=payload,
                          capture_output=True, text=True)


class T(unittest.TestCase):
    def test_basic(self):
        # 10000*2=20000 -> *1.07 = 21400
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 2}], False), 21400)

    def test_threshold(self):
        # 49999 ไม่ลด: 49999*1.07=53498.93 -> 53499
        self.assertEqual(cafe_bill([{"price": 49999, "qty": 1}], False), 53499)
        # 50000 ลด 5%: 47500*1.07=50825
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], False), 50825)

    def test_member(self):
        # 10000*0.9*1.07=9630
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 1}], True), 9630)
        # 50000*.95*.9*1.07=45742.5 -> 45743
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], True), 45743)

    def test_rounding(self):
        # 1*1.07=1.07 -> 1 ; 50*1.07=53.5 -> 54
        self.assertEqual(cafe_bill([{"price": 1, "qty": 1}], False), 1)
        self.assertEqual(cafe_bill([{"price": 50, "qty": 1}], False), 54)

    def test_invalid(self):
        bad = [
            ([{"price": 100, "qty": 0}], False),
            ([{"price": -1, "qty": 1}], False),
            ([{"price": 100.0, "qty": 1}], False),
            ([{"price": 100, "qty": 1.0}], False),
            ([{"price": True, "qty": 1}], False),
            ([{"price": 100, "qty": True}], False),
            ([{"price": 100}], False),
            ([5], False),
            ("x", False),
            ([{"price": 100, "qty": 1}], 1),
            ([{"price": 100, "qty": 1}], "yes"),
        ]
        for items, m in bad:
            with self.assertRaises(ValueError):
                cafe_bill(items, m)

    def test_cli(self):
        r = run(json.dumps({"items": [{"price": 10000, "qty": 2}], "member": False}))
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 21400})
        r = run(json.dumps({"items": [{"price": 100, "qty": -1}], "member": False}))
        self.assertEqual(r.returncode, 2)
        self.assertFalse(json.loads(r.stdout)["ok"])
        self.assertNotIn("Traceback", r.stderr)


if __name__ == "__main__":
    unittest.main()
