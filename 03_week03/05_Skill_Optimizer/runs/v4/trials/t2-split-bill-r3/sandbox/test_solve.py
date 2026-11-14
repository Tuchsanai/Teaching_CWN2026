import json
import subprocess
import sys
import unittest

from solve import split_bill


class TestSplitBill(unittest.TestCase):
    def test_even(self):
        self.assertEqual(split_bill(1000, 4, 0), [250] * 4)

    def test_remainder_goes_to_first(self):
        self.assertEqual(split_bill(100, 3, 0), [34, 33, 33])

    def test_tip(self):
        self.assertEqual(split_bill(1000, 2, 10), [550, 550])

    def test_half_up_rounding(self):
        # 5 * 110% = 5.5 -> 6
        self.assertEqual(split_bill(5, 1, 10), [6])
        # 1 * 105% = 1.05 -> 1
        self.assertEqual(split_bill(1, 1, 5), [1])

    def test_zero_total(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_more_people_than_satang(self):
        self.assertEqual(split_bill(2, 4, 0), [1, 1, 0, 0])

    def test_sum_preserved(self):
        r = split_bill(12345, 7, 13)
        self.assertEqual(sum(r), (12345 * 113 + 50) // 100)

    def test_invalid(self):
        for args in [(1.5, 1, 0), (-1, 1, 0), (10, 0, 0), (10, 1, 101),
                     (10, 1, -1), (True, 1, 0), ("10", 1, 0), (10, 1, 5.0)]:
            with self.assertRaises(ValueError):
                split_bill(*args)

    def test_cli(self):
        p = subprocess.run([sys.executable, "solve.py"], capture_output=True, text=True,
                           input=json.dumps({"total": 100, "people": 3, "tip_percent": 0}))
        self.assertEqual(json.loads(p.stdout), [34, 33, 33])


if __name__ == "__main__":
    unittest.main()
