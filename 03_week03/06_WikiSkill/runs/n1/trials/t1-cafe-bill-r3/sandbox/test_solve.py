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
        self.assertEqual(cafe_bill([it(10000, 2)], True), 19260)

    def test_threshold(self):
        self.assertEqual(cafe_bill([it(49999)], False), 53499)  # 53498.93
        self.assertEqual(cafe_bill([it(50000)], False), 50825)  # 50825

    def test_member_below_threshold(self):
        self.assertEqual(cafe_bill([it(10000)], True), 9630)

    def test_both(self):
        self.assertEqual(cafe_bill([it(50000)], True), 45743)  # 45742.5 half up

    def test_half_up(self):
        self.assertEqual(cafe_bill([it(50000)], True), 45743)

    def test_errors(self):
        bad = [([it(100, 0)], False), ([it(-1)], False), ([it(100.0)], False),
               ([it(100, 1.0)], False), ([it(True)], False), ([it(100)], 1),
               ("x", False), ([{"price": 1}], False), ([5], False)]
        for a, m in bad:
            with self.assertRaises(ValueError):
                cafe_bill(a, m)

    def run_cli(self, s):
        return subprocess.run([sys.executable, "solve.py"], input=s,
                              capture_output=True, text=True)

    def test_cli(self):
        r = self.run_cli('{"items":[{"price":10000,"qty":2}],"member":false}')
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 21400})
        r = self.run_cli('{"items":[{"price":100,"qty":0}],"member":false}')
        self.assertEqual(r.returncode, 2)
        self.assertFalse(json.loads(r.stdout)["ok"])
        self.assertNotIn("Traceback", r.stderr)


if __name__ == "__main__":
    unittest.main()
