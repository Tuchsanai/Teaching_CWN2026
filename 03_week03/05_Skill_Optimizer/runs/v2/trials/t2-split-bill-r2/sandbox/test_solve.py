import json
import subprocess
import sys
import unittest

from solve import split_bill


class TestSplitBill(unittest.TestCase):
    def test_even(self):
        self.assertEqual(split_bill(1000, 4, 0), [250] * 4)

    def test_remainder_first_pay_more(self):
        self.assertEqual(split_bill(1000, 3, 0), [334, 333, 333])

    def test_tip(self):
        self.assertEqual(split_bill(1000, 2, 10), [550, 550])

    def test_tip_round_half_up(self):
        # 5*10% = 0.5 -> 1 ; total 6 over 1 person
        self.assertEqual(split_bill(5, 1, 10), [6])

    def test_zero_total(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_invalid(self):
        for args in [(-1, 1, 0), (10, 0, 0), (10, 1, 101), (10.0, 1, 0),
                     (True, 1, 0), ("1", 1, 0), (10, 1, None), (10, 1, -1)]:
            with self.assertRaises(ValueError):
                split_bill(*args)

    def test_cli(self):
        p = subprocess.run([sys.executable, "solve.py"], input='{"total":100,"people":3,"tip_percent":0}',
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 0)
        self.assertEqual(json.loads(p.stdout), {"ok": True, "result": [34, 33, 33]})

    def test_cli_error(self):
        p = subprocess.run([sys.executable, "solve.py"], input='{"total":1}', capture_output=True, text=True)
        self.assertEqual(p.returncode, 2)
        self.assertFalse(json.loads(p.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
