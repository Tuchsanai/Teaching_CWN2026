import json
import subprocess
import sys
import unittest

from solve import split_bill


class TestSplitBill(unittest.TestCase):
    def test_even(self):
        self.assertEqual(split_bill(1000, 2, 0), [500, 500])

    def test_remainder_first_people(self):
        self.assertEqual(split_bill(100, 3, 0), [34, 33, 33])

    def test_tip(self):
        self.assertEqual(split_bill(1000, 4, 10), [275] * 4)

    def test_rounding_half_up(self):
        self.assertEqual(split_bill(5, 1, 10), [6])  # 5.5 -> 6

    def test_zero_total(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_sum_preserved(self):
        self.assertEqual(sum(split_bill(9999, 7, 13)), (9999 * 113 * 2 + 100) // 200)

    def test_invalid(self):
        for args in [(1.5, 1, 0), (True, 1, 0), (-1, 1, 0), (10, 0, 0),
                     (10, 1, 101), (10, 1, -1), ("10", 1, 0), (None, 1, 0)]:
            with self.assertRaises(ValueError):
                split_bill(*args)

    def test_cli(self):
        r = subprocess.run([sys.executable, "solve.py"], capture_output=True, text=True,
                           input=json.dumps({"total": 100, "people": 3, "tip_percent": 0}))
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": [34, 33, 33]})

    def test_cli_error(self):
        r = subprocess.run([sys.executable, "solve.py"], capture_output=True, text=True, input="nope")
        self.assertEqual(r.returncode, 2)
        self.assertFalse(json.loads(r.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
