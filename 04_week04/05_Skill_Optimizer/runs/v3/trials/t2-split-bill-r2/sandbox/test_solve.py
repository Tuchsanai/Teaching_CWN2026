import json
import subprocess
import sys
import unittest

from solve import split_bill


class TestSplitBill(unittest.TestCase):
    def test_even(self):
        self.assertEqual(split_bill(10000, 4, 0), [2500] * 4)

    def test_remainder_first_people(self):
        self.assertEqual(split_bill(100, 3, 0), [34, 33, 33])

    def test_tip(self):
        self.assertEqual(split_bill(1000, 2, 10), [550, 550])

    def test_round_half_up(self):
        # 1 * 150 / 100 = 1.5 -> 2
        self.assertEqual(split_bill(1, 1, 50), [2])
        # 1 * 104/100 = 1.04 -> 1
        self.assertEqual(split_bill(1, 1, 4), [1])

    def test_zero_total(self):
        self.assertEqual(split_bill(0, 3, 20), [0, 0, 0])

    def test_sum_matches(self):
        r = split_bill(9999, 7, 13)
        self.assertEqual(sum(r), (2 * 9999 * 113 + 100) // 200)
        self.assertEqual(len(r), 7)

    def test_invalid(self):
        for args in [(-1, 1, 0), (1, 0, 0), (1, 1, -1), (1, 1, 101),
                     (1.5, 1, 0), (True, 1, 0), (1, 1, "5"), (1, None, 0)]:
            with self.assertRaises(ValueError):
                split_bill(*args)

    def test_cli(self):
        p = subprocess.run([sys.executable, "solve.py"], capture_output=True,
                           text=True, input='{"total":100,"people":3,"tip_percent":0}')
        self.assertEqual(p.returncode, 0)
        self.assertEqual(json.loads(p.stdout), {"ok": True, "result": [34, 33, 33]})
        p = subprocess.run([sys.executable, "solve.py"], capture_output=True,
                           text=True, input='bad')
        self.assertEqual(p.returncode, 2)
        self.assertFalse(json.loads(p.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
