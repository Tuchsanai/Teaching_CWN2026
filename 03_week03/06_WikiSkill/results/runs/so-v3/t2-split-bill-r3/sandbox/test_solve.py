import json
import subprocess
import sys
import unittest

from solve import split_bill


class TestSplitBill(unittest.TestCase):
    def test_even(self):
        self.assertEqual(split_bill(1000, 4, 0), [250] * 4)

    def test_remainder_first_pay_more(self):
        self.assertEqual(split_bill(1000, 3, 10), [367, 367, 366])

    def test_tip_half_up(self):
        # 10 * 105 = 1050 -> 10.5 exactly -> 11
        self.assertEqual(split_bill(10, 1, 5), [11])

    def test_zero_total(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_sum_preserved(self):
        self.assertEqual(sum(split_bill(1000, 7, 100)), 2000)

    def test_invalid_inputs(self):
        for args in [(-1, 1, 0), (10, 0, 0), (10, 1, 101), (10, 1, -1),
                     (5.0, 1, 0), (True, 1, 0), ("5", 1, 0), (10, None, 0)]:
            with self.assertRaises(ValueError):
                split_bill(*args)

    def _cli(self, text):
        p = subprocess.run([sys.executable, "solve.py"], input=text,
                           capture_output=True, text=True)
        return p.returncode, json.loads(p.stdout)

    def test_cli_ok(self):
        code, out = self._cli('{"total": 1000, "people": 3, "tip_percent": 10}')
        self.assertEqual((code, out), (0, {"ok": True, "result": [367, 367, 366]}))

    def test_cli_errors(self):
        for text in ["not json", "{}", '{"total": 1.5, "people": 1, "tip_percent": 0}']:
            code, out = self._cli(text)
            self.assertEqual(code, 2)
            self.assertFalse(out["ok"])


if __name__ == "__main__":
    unittest.main()
