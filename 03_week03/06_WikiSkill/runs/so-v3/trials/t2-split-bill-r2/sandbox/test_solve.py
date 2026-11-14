import json
import subprocess
import sys
import unittest

from solve import split_bill


class TestSplitBill(unittest.TestCase):
    def test_even(self):
        self.assertEqual(split_bill(1000, 2, 0), [500, 500])

    def test_remainder_first_people(self):
        self.assertEqual(split_bill(1000, 3, 0), [334, 333, 333])

    def test_tip(self):
        self.assertEqual(split_bill(1000, 4, 10), [275] * 4)

    def test_round_half_up_once(self):
        # 5 * 110 / 100 = 5.5 -> 6
        self.assertEqual(split_bill(5, 1, 10), [6])
        # 1 * 105/100 = 1.05 -> 1
        self.assertEqual(split_bill(1, 1, 5), [1])

    def test_zero_total(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_sum_matches(self):
        r = split_bill(9999, 7, 13)
        self.assertEqual(sum(r), (2 * 9999 * 113 + 100) // 200)
        self.assertEqual(len(r), 7)

    def test_invalid(self):
        for args in [(-1, 1, 0), (1, 0, 0), (1, 1, 101), (1, 1, -1),
                     (1.0, 1, 0), (True, 1, 0), (1, "2", 0), (None, 1, 0)]:
            with self.assertRaises(ValueError):
                split_bill(*args)

    def test_cli(self):
        p = subprocess.run([sys.executable, "solve.py"], capture_output=True, text=True,
                           input=json.dumps({"total": 1000, "people": 3, "tip_percent": 0}))
        self.assertEqual(p.returncode, 0)
        self.assertEqual(json.loads(p.stdout), {"ok": True, "result": [334, 333, 333]})
        p = subprocess.run([sys.executable, "solve.py"], capture_output=True, text=True, input="{bad")
        self.assertEqual(p.returncode, 2)
        self.assertFalse(json.loads(p.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
