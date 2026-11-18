import json
import subprocess
import sys
import unittest

from solve import split_bill


class TestSplitBill(unittest.TestCase):
    def test_even(self):
        self.assertEqual(split_bill(1000, 4, 0), [250] * 4)

    def test_remainder_to_first(self):
        self.assertEqual(split_bill(1000, 3, 0), [334, 333, 333])

    def test_tip(self):
        self.assertEqual(split_bill(1000, 2, 10), [550, 550])

    def test_tip_rounding_half_up(self):
        # 5*10% = 0.5 -> 1 ; total 6 over 1 person
        self.assertEqual(split_bill(5, 1, 10), [6])

    def test_zero_total(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_sum_preserved(self):
        r = split_bill(9999, 7, 15)
        self.assertEqual(sum(r), 9999 + (9999 * 15 * 2 + 100) // 200)
        self.assertEqual(len(r), 7)

    def test_invalid(self):
        for args in [(-1, 1, 0), (1, 0, 0), (1, 1, 101), (1, 1, -1),
                     (1.0, 1, 0), (True, 1, 0), (1, "2", 0), (None, 1, 0)]:
            with self.assertRaises(ValueError):
                split_bill(*args)

    def test_cli(self):
        p = subprocess.run([sys.executable, "solve.py"], capture_output=True,
                           text=True, input='{"total":1000,"people":3,"tip_percent":0}')
        self.assertEqual(p.returncode, 0)
        self.assertEqual(json.loads(p.stdout), {"ok": True, "result": [334, 333, 333]})

    def test_cli_error(self):
        p = subprocess.run([sys.executable, "solve.py"], capture_output=True,
                           text=True, input='{"total":1}')
        self.assertEqual(p.returncode, 2)
        self.assertFalse(json.loads(p.stdout)["ok"])
        self.assertNotIn("Traceback", p.stderr)


if __name__ == "__main__":
    unittest.main()
