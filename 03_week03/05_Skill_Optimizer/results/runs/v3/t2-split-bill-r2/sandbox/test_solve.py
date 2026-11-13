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
        self.assertEqual(split_bill(1000, 4, 10), [275, 275, 275, 275])

    def test_zero_total(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_half_up_tip(self):
        # 10 * 105 / 100 = 10.5 -> 11
        self.assertEqual(split_bill(10, 1, 5), [11])

    def test_invalid(self):
        for args in [(1.0, 1, 0), (True, 1, 0), (-1, 1, 0), (10, 0, 0),
                     (10, 1, 101), (10, 1, -1), ("1", 1, 0), (10, 1, None)]:
            with self.assertRaises(ValueError):
                split_bill(*args)

    def test_cli_ok(self):
        p = subprocess.run([sys.executable, "solve.py"], capture_output=True,
                           text=True, input='{"total":1000,"people":3,"tip_percent":0}')
        self.assertEqual(p.returncode, 0)
        self.assertEqual(json.loads(p.stdout), {"ok": True, "result": [334, 333, 333]})

    def test_cli_bad(self):
        for inp in ["not json", "{}", '{"total":1,"people":0,"tip_percent":0}']:
            p = subprocess.run([sys.executable, "solve.py"], capture_output=True,
                               text=True, input=inp)
            self.assertEqual(p.returncode, 2)
            self.assertFalse(json.loads(p.stdout)["ok"])
            self.assertEqual(p.stderr, "")


if __name__ == "__main__":
    unittest.main()
