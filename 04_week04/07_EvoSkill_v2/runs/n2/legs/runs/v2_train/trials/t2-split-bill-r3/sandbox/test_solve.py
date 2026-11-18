import json
import subprocess
import sys
import unittest

from solve import split_bill


class Normal(unittest.TestCase):
    def test_uneven(self):
        self.assertEqual(split_bill(10000, 3, 0), [3334, 3333, 3333])

    def test_tip(self):
        self.assertEqual(split_bill(10000, 7, 10), [1572, 1572, 1572, 1571, 1571, 1571, 1571])

    def test_even(self):
        self.assertEqual(split_bill(10000, 4, 0), [2500] * 4)

    def test_one_person_tip(self):
        self.assertEqual(split_bill(5000, 1, 100), [10000])


class Boundary(unittest.TestCase):
    def test_zero_total(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_small_total(self):
        self.assertEqual(split_bill(2, 3, 0), [1, 1, 0])

    def test_max_tip(self):
        self.assertEqual(split_bill(101, 2, 100), [101, 101])

    def test_sum_preserved(self):
        self.assertEqual(sum(split_bill(9999, 13, 15)), 11499)  # 9999*1.15=11498.85


class NoDrift(unittest.TestCase):
    def test_half_up_grand(self):
        # 1001*105/100 = 1051.05 -> 1051 ; 3 คน
        self.assertEqual(split_bill(1001, 3, 5), [351, 350, 350])

    def test_half_exact(self):
        # 10*105/100 = 10.5 -> 11 (ปัดครึ่งขึ้น ไม่ใช่ banker)
        self.assertEqual(split_bill(10, 1, 5), [11])

    def test_half_exact_even(self):
        # 30*105/100 = 31.5 -> 32 (banker จะได้ 32 เช่นกัน) ; 50*105/100=52.5 -> 53
        self.assertEqual(split_bill(50, 1, 5), [53])


class Reject(unittest.TestCase):
    def test_bad(self):
        bad = [(-1, 1, 0), (100, 0, 0), (100, -2, 0), (100, 1, -1), (100, 1, 101),
               (100.0, 1, 0), (100, 1.0, 0), (100, 1, 5.0), ("100", 1, 0),
               (100, "1", 0), (100, 1, "5"), (True, 1, 0), (100, True, 0),
               (100, 1, True), (None, 1, 0)]
        for args in bad:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    split_bill(*args)


class Cli(unittest.TestCase):
    def run_cli(self, payload):
        p = subprocess.run([sys.executable, "solve.py"], input=json.dumps(payload),
                           capture_output=True, text=True)
        return p.returncode, json.loads(p.stdout)

    def test_ok(self):
        self.assertEqual(self.run_cli({"total": 10000, "people": 3, "tip_percent": 0}),
                         (0, {"ok": True, "result": [3334, 3333, 3333]}))

    def test_error(self):
        code, out = self.run_cli({"total": 100, "people": 0, "tip_percent": 0})
        self.assertEqual(code, 2)
        self.assertFalse(out["ok"])


if __name__ == "__main__":
    unittest.main()
