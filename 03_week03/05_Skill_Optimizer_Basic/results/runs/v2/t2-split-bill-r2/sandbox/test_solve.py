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
        self.assertEqual(split_bill(1000, 4, 10), [275, 275, 275, 275])

    def test_half_up_tip(self):
        # 10 * 105 over 100 = 10.5 -> 11
        self.assertEqual(split_bill(10, 1, 5), [11])

    def test_zero_total(self):
        self.assertEqual(split_bill(0, 3, 20), [0, 0, 0])

    def test_sum_preserved(self):
        r = split_bill(9999, 7, 13)
        self.assertEqual(sum(r), (2 * 9999 * 113 + 100) // 200)
        self.assertEqual(len(r), 7)

    def test_invalid(self):
        for args in [(-1, 1, 0), (10, 0, 0), (10, 1, 101), (10.0, 1, 0),
                     (True, 1, 0), ("1", 1, 0), (10, None, 0)]:
            with self.assertRaises(ValueError):
                split_bill(*args)

    def _cli(self, text):
        p = subprocess.run([sys.executable, "solve.py"], input=text,
                           capture_output=True, text=True)
        return p.returncode, p.stdout

    def test_cli_ok(self):
        code, out = self._cli('{"total": 100, "people": 3, "tip_percent": 0}')
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out), {"ok": True, "result": [34, 33, 33]})

    def test_cli_errors(self):
        for text in ["not json", '{"total": 1}', '{"total": 1.5, "people": 1, "tip_percent": 0}']:
            code, out = self._cli(text)
            self.assertEqual(code, 2)
            self.assertFalse(json.loads(out)["ok"])


if __name__ == "__main__":
    unittest.main()
