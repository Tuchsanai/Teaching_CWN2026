"""รัน: python3 -m unittest -q test_solve"""
import json
import subprocess
import sys
import unittest

from solve import split_bill


class Normal(unittest.TestCase):
    def test_1(self):
        self.assertEqual(split_bill(10000, 3, 0), [3334, 3333, 3333])

    def test_2(self):
        self.assertEqual(split_bill(10000, 7, 10), [1572, 1572, 1572, 1571, 1571, 1571, 1571])

    def test_3(self):
        self.assertEqual(split_bill(10000, 4, 0), [2500] * 4)

    def test_4(self):
        self.assertEqual(split_bill(5000, 1, 100), [10000])


class Boundary(unittest.TestCase):
    def test_zero_total(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_tiny(self):
        self.assertEqual(split_bill(2, 3, 0), [1, 1, 0])

    def test_one_person(self):
        self.assertEqual(split_bill(12345, 1, 0), [12345])

    def test_max_tip(self):
        self.assertEqual(split_bill(101, 2, 100), [101, 101])


class NoDrift(unittest.TestCase):
    def test_half_up_total(self):
        # 1*150/100 = 1.5 -> 2 (half-up)
        self.assertEqual(split_bill(1, 1, 50), [2])

    def test_sum_preserved(self):
        r = split_bill(99999, 7, 15)  # 114998.85 -> 114999
        self.assertEqual(sum(r), 114999)
        self.assertEqual(r, [16429, 16429, 16429, 16428, 16428, 16428, 16428])

    def test_not_split_rounding(self):
        # 1 สตางค์ ทิป 10% -> 1.1 -> 1
        self.assertEqual(split_bill(5, 1, 10), [6])


class Reject(unittest.TestCase):
    def test_bad(self):
        bad = [(-1, 1, 0), (1, 0, 0), (1, -1, 0), (1, 1, -1), (1, 1, 101),
               (1.0, 1, 0), (1, 1.0, 0), (1, 1, 1.0), ("1", 1, 0), (1, "1", 0),
               (True, 1, 0), (1, True, 0), (1, 1, True), (None, 1, 0)]
        for a in bad:
            with self.subTest(a=a), self.assertRaises(ValueError):
                split_bill(*a)


class Cli(unittest.TestCase):
    def run_cli(self, payload):
        p = subprocess.run([sys.executable, "solve.py"], input=json.dumps(payload),
                           capture_output=True, text=True)
        return p.returncode, json.loads(p.stdout)

    def test_ok(self):
        self.assertEqual(self.run_cli({"total": 10000, "people": 3, "tip_percent": 0}),
                         (0, {"ok": True, "result": [3334, 3333, 3333]}))

    def test_err(self):
        code, out = self.run_cli({"total": 10000, "people": 0, "tip_percent": 0})
        self.assertEqual(code, 2)
        self.assertFalse(out["ok"])


if __name__ == "__main__":
    unittest.main()
