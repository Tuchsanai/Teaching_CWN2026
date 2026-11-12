import json
import subprocess
import sys
import unittest

from solve import split_bill


class T(unittest.TestCase):
    def test_even(self):
        self.assertEqual(split_bill(1000, 4, 0), [250] * 4)

    def test_remainder_first(self):
        self.assertEqual(split_bill(100, 3, 0), [34, 33, 33])

    def test_tip(self):
        self.assertEqual(split_bill(1000, 3, 10), [367, 367, 366])

    def test_tip_rounding_half_up(self):
        self.assertEqual(split_bill(5, 1, 10), [6])    # 0.5 -> 1
        self.assertEqual(split_bill(4, 1, 10), [4])    # 0.4 -> 0

    def test_zero_total(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_sum_preserved(self):
        r = split_bill(99999, 7, 15)
        self.assertEqual(sum(r), 99999 + (99999 * 15 * 2 + 100) // 200)

    def test_invalid(self):
        for args in [(-1, 1, 0), (1, 0, 0), (1, 1, -1), (1, 1, 101),
                     (1.5, 1, 0), (1, 1.0, 0), (1, 1, 5.5), (True, 1, 0),
                     ("1", 1, 0)]:
            with self.assertRaises(ValueError):
                split_bill(*args)

    def test_cli(self):
        p = subprocess.run([sys.executable, "solve.py"],
                           input='{"total":100,"people":3,"tip_percent":0}',
                           capture_output=True, text=True)
        self.assertEqual(json.loads(p.stdout), {"shares": [34, 33, 33]})
        p = subprocess.run([sys.executable, "solve.py", '{"total":1,"people":0,"tip_percent":0}'],
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 1)
        self.assertIn("error", json.loads(p.stdout))


if __name__ == "__main__":
    unittest.main()
