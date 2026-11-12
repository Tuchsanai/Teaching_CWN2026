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
        self.assertEqual(split_bill(1000, 4, 10), [275, 275, 275, 275])

    def test_half_up_rounding(self):
        # 1005 * 1.05 = 1055.25 -> 1055
        self.assertEqual(sum(split_bill(1005, 1, 5)), 1055)
        # 10 * 1.05 = 10.5 -> 11
        self.assertEqual(split_bill(10, 1, 5), [11])

    def test_zero_total(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_more_people_than_satang(self):
        self.assertEqual(split_bill(2, 4, 0), [1, 1, 0, 0])

    def test_invalid(self):
        for args in [(-1, 1, 0), (1, 0, 0), (1, 1, 101), (1.0, 1, 0),
                     (True, 1, 0), ("1", 1, 0), (1, None, 0), (1, 1, -1)]:
            with self.assertRaises(ValueError):
                split_bill(*args)

    def _cli(self, text):
        p = subprocess.run([sys.executable, "solve.py"], input=text,
                           capture_output=True, text=True)
        return p.returncode, json.loads(p.stdout)

    def test_cli_ok(self):
        self.assertEqual(self._cli('{"total":100,"people":3,"tip_percent":0}'),
                         (0, {"ok": True, "result": [34, 33, 33]}))

    def test_cli_errors(self):
        for t in ["not json", '{"total":1}', '{"total":1.5,"people":1,"tip_percent":0}', "[]"]:
            code, out = self._cli(t)
            self.assertEqual(code, 2)
            self.assertFalse(out["ok"])


if __name__ == "__main__":
    unittest.main()
