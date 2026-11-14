import json
import subprocess
import sys
import unittest

from solve import cafe_bill


def it(p, q=1):
    return {"price": p, "qty": q}


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cafe_bill([it(10000, 2)], False), 21400)

    def test_threshold(self):
        # 49999 -> *1.07 = 53499.0 -> 53499 (ไม่ลด)
        self.assertEqual(cafe_bill([it(49999)], False), 53499)
        # 50000 -> 47500 * 1.07 = 50825
        self.assertEqual(cafe_bill([it(50000)], False), 50825)
        self.assertEqual(cafe_bill([it(50001)], False), 50826)  # 50825.95 -> 50826

    def test_member(self):
        # 10000*0.9*1.07 = 9630
        self.assertEqual(cafe_bill([it(10000)], True), 9630)
        # 100000*.95*.9*1.07 = 91485
        self.assertEqual(cafe_bill([it(50000, 2)], True), 91485)

    def test_rounding(self):
        # 50*1.07 = 53.5 -> 54
        self.assertEqual(cafe_bill([it(50)], False), 54)
        # 10*1.07 = 10.7 -> 11
        self.assertEqual(cafe_bill([it(10)], False), 11)
        # 10*1.07 = 10.7; 5*1.07=5.35 -> 5
        self.assertEqual(cafe_bill([it(5)], False), 5)

    def test_invalid(self):
        bad = [
            ([it(100, 0)], False),
            ([it(-1)], False),
            ([it(100.0)], False),
            ([it(100, 1.0)], False),
            ([it(True)], False),
            ([it(100, True)], False),
            ([{"price": 1}], False),
            ([5], False),
            ("x", False),
            ([it(100)], 1),
            ([it(100)], "yes"),
            ([it(-5)], None),
        ]
        for a, m in bad:
            with self.assertRaises(ValueError):
                cafe_bill(a, m)

    def run_cli(self, payload):
        return subprocess.run([sys.executable, "solve.py"], input=payload,
                              capture_output=True, text=True)

    def test_cli_ok(self):
        r = self.run_cli(json.dumps({"items": [it(10000, 2)], "member": False}))
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 21400})

    def test_cli_bad(self):
        r = self.run_cli(json.dumps({"items": [it(-1)], "member": False}))
        self.assertEqual(r.returncode, 2)
        self.assertFalse(json.loads(r.stdout)["ok"])
        self.assertNotIn("Traceback", r.stderr)


if __name__ == "__main__":
    unittest.main()
