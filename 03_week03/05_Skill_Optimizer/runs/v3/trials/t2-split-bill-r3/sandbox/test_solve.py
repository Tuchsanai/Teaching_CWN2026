import json
import subprocess
import sys
import unittest

from solve import split_bill


class TestSplitBill(unittest.TestCase):
    def test_even(self):
        self.assertEqual(split_bill(1000, 2, 0), [500, 500])

    def test_remainder_to_first(self):
        self.assertEqual(split_bill(100, 3, 0), [34, 33, 33])

    def test_tip(self):
        self.assertEqual(split_bill(1000, 1, 10), [1100])

    def test_round_half_up(self):
        # 1 * 150 / 100 = 1.5 -> 2
        self.assertEqual(split_bill(1, 1, 50), [2])
        # 1 * 110/100 = 1.1 -> 1
        self.assertEqual(split_bill(1, 1, 10), [1])

    def test_zero_total(self):
        self.assertEqual(split_bill(0, 3, 20), [0, 0, 0])

    def test_sum_preserved(self):
        r = split_bill(9999, 7, 15)
        self.assertEqual(sum(r), (2 * 9999 * 115 + 100) // 200)
        self.assertEqual(len(r), 7)

    def test_invalid(self):
        for args in [(-1, 1, 0), (1, 0, 0), (1, 1, 101), (1, 1, -1),
                     (1.5, 1, 0), (True, 1, 0), (1, 1, "5"), (None, 1, 0)]:
            with self.assertRaises(ValueError):
                split_bill(*args)

    def test_cli(self):
        p = subprocess.run([sys.executable, "solve.py"], input='{"total":100,"people":3,"tip_percent":0}',
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 0)
        self.assertEqual(json.loads(p.stdout), {"ok": True, "result": [34, 33, 33]})
        p = subprocess.run([sys.executable, "solve.py"], input='bad', capture_output=True, text=True)
        self.assertEqual(p.returncode, 2)
        self.assertFalse(json.loads(p.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
