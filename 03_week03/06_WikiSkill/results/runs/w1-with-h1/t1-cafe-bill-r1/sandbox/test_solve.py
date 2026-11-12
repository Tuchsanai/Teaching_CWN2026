import json
import subprocess
import sys
import unittest
from solve import cafe_bill


def I(p, q=1):
    return {"price": p, "qty": q}


class T(unittest.TestCase):
    def test_normal(self):
        # 10000*1.07 = 10700
        self.assertEqual(cafe_bill([I(5000, 2)], False), 10700)

    def test_threshold(self):
        # 49999*1.07=53498.93 -> 53499
        self.assertEqual(cafe_bill([I(49999)], False), 53499)
        # 50000*.95*1.07 = 50825
        self.assertEqual(cafe_bill([I(50000)], False), 50825)
        self.assertEqual(cafe_bill([I(50001)], False), 50826)  # 50826.0 approx 50825.95..

    def test_member(self):
        # 10000*.9*1.07 = 9630
        self.assertEqual(cafe_bill([I(10000)], True), 9630)
        # 50000*.95*.9*1.07 = 45742.5 -> 45743
        self.assertEqual(cafe_bill([I(50000)], True), 45743)

    def test_half_up_single_round(self):
        # 50 *1.07 = 53.5 -> 54
        self.assertEqual(cafe_bill([I(50)], False), 54)
        # 10*.9*1.07=9.63 -> 10
        self.assertEqual(cafe_bill([I(10)], True), 10)

    def test_invalid(self):
        bad = [
            ([I(1.0)], False), ([I(True)], False), ([I("1")], False),
            ([I(None)], False), ([I(-1)], False),
            ([I(1, 0)], False), ([I(1, 1.0)], False), ([I(1, True)], False),
            ([I(1, None)], False), ([I(1, "1")], False),
            ([{"price": 1}], False), (["x"], False), (None, False),
            ("abc", False), ([I(1)], 1), ([I(1)], None), ([I(1)], "True"),
        ]
        for items, m in bad:
            with self.assertRaises(ValueError):
                cafe_bill(items, m)

    def run_cli(self, s):
        return subprocess.run([sys.executable, "solve.py"], input=s,
                              capture_output=True, text=True)

    def test_cli(self):
        r = self.run_cli(json.dumps({"items": [I(5000, 2)], "member": False}))
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 10700})
        for s in ['{"items": [], "member": 1}', 'nope', '[]', '{"items": []}']:
            r = self.run_cli(s)
            self.assertEqual(r.returncode, 2)
            self.assertFalse(json.loads(r.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
