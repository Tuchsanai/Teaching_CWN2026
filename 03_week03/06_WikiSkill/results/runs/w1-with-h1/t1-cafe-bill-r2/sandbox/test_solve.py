import json
import subprocess
import sys
import unittest

from solve import cafe_bill


def run(payload):
    return subprocess.run([sys.executable, "solve.py"], input=payload,
                          capture_output=True, text=True)


class T(unittest.TestCase):
    def test_normal(self):
        # 10000*1.07 = 10700
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 1}], False), 10700)
        # member: 10000*.9*1.07 = 9630
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 1}], True), 9630)

    def test_threshold(self):
        # 49999*1.07 = 53498.93 -> 53499
        self.assertEqual(cafe_bill([{"price": 49999, "qty": 1}], False), 53499)
        # 50000*.95*1.07 = 50825
        self.assertEqual(cafe_bill([{"price": 25000, "qty": 2}], False), 50825)
        # 50001*.95*1.07 = 50826.01605 -> 50826
        self.assertEqual(cafe_bill([{"price": 50001, "qty": 1}], False), 50826)

    def test_half_up(self):
        # 50 *1.07 = 53.5 -> 54
        self.assertEqual(cafe_bill([{"price": 50, "qty": 1}], False), 54)
        # 10*1.07 = 10.7 -> 11 ; 5*1.07=5.35 -> 5
        self.assertEqual(cafe_bill([{"price": 5, "qty": 1}], False), 5)

    def test_multi_step_single_round(self):
        # 60000*.95*.9*1.07 = 54891
        self.assertEqual(cafe_bill([{"price": 20000, "qty": 3}], True), 54891)

    def test_invalid(self):
        ok = [{"price": 100, "qty": 1}]
        bad_items = [None, "x", {}, [None], [{"price": 1}], [{"price": 1.0, "qty": 1}],
                     [{"price": True, "qty": 1}], [{"price": "1", "qty": 1}],
                     [{"price": None, "qty": 1}], [{"price": -1, "qty": 1}],
                     [{"price": 1, "qty": 0}], [{"price": 1, "qty": 1.0}],
                     [{"price": 1, "qty": True}]]
        for b in bad_items:
            with self.assertRaises(ValueError):
                cafe_bill(b, False)
        for m in [1, 0, None, "True", 1.0]:
            with self.assertRaises(ValueError):
                cafe_bill(ok, m)

    def test_cli(self):
        r = run(json.dumps({"items": [{"price": 10000, "qty": 1}], "member": False}))
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 10700})
        r = run(json.dumps({"items": [{"price": 1.5, "qty": 1}], "member": False}))
        self.assertEqual(r.returncode, 2)
        self.assertFalse(json.loads(r.stdout)["ok"])
        self.assertEqual(run("not json").returncode, 2)


if __name__ == "__main__":
    unittest.main()
