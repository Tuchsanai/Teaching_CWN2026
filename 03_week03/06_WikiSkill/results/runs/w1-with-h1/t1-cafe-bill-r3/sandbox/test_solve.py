import json
import subprocess
import sys
import unittest

from solve import cafe_bill


def it(p, q=1):
    return {"price": p, "qty": q}


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cafe_bill([it(10000, 2)], False), 21400)  # 20000*1.07

    def test_threshold(self):
        self.assertEqual(cafe_bill([it(49999)], False), 53499)  # 49999*1.07=53498.93
        self.assertEqual(cafe_bill([it(50000)], False), 50825)  # 50000*.95*1.07=50825
        self.assertEqual(cafe_bill([it(50001)], False), 50826)  # 50826.0 -> 50825.95+...

    def test_member(self):
        self.assertEqual(cafe_bill([it(10000)], True), 9630)  # 10000*.9*1.07
        self.assertEqual(cafe_bill([it(50000)], True), 45743)  # 45742.5 -> up

    def test_half_up(self):
        self.assertEqual(cafe_bill([it(50)], True), 48)  # 48.15
        self.assertEqual(cafe_bill([it(50000)], True), 45743)

    def test_invalid(self):
        bad = [
            ([it(1.0)], False), ([it(True)], False), ([it("1")], False),
            ([it(None)], False), ([it(100, 0)], False), ([it(100, 1.0)], False),
            ([it(-1)], False), ([{"price": 1}], False), ("x", False),
            ([it(100)], 1), ([it(100)], None), ([5], False),
        ]
        for a, m in bad:
            with self.assertRaises(ValueError):
                cafe_bill(a, m)

    def run_cli(self, s):
        return subprocess.run([sys.executable, "solve.py"], input=s,
                              capture_output=True, text=True)

    def test_cli(self):
        r = self.run_cli(json.dumps({"items": [it(10000, 2)], "member": False}))
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 21400})
        r = self.run_cli(json.dumps({"items": [it(1.5)], "member": False}))
        self.assertEqual(r.returncode, 2)
        self.assertFalse(json.loads(r.stdout)["ok"])
        self.assertEqual(self.run_cli("not json").returncode, 2)


if __name__ == "__main__":
    unittest.main()
