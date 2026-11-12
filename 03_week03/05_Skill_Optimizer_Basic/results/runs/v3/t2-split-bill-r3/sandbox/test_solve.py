import json
import subprocess
import sys
import unittest

from solve import split_bill


class TestSplitBill(unittest.TestCase):
    def test_even(self):
        self.assertEqual(split_bill(1000, 4, 0), [250, 250, 250, 250])

    def test_remainder_first_people(self):
        self.assertEqual(split_bill(100, 3, 0), [34, 33, 33])

    def test_tip(self):
        self.assertEqual(split_bill(1000, 2, 10), [550, 550])

    def test_tip_half_up(self):
        # 10 * 105 = 1050 -> 10.5 -> 11
        self.assertEqual(split_bill(10, 1, 5), [11])

    def test_zero_total(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_sum_preserved(self):
        self.assertEqual(sum(split_bill(9999, 7, 15)), 11499)

    def test_invalid(self):
        for args in [(-1, 1, 0), (1, 0, 0), (1, 1, 101), (1, 1, -1),
                     (1.0, 1, 0), (True, 1, 0), ("1", 1, 0), (1, None, 0)]:
            with self.assertRaises(ValueError):
                split_bill(*args)

    def _cli(self, text):
        p = subprocess.run([sys.executable, "solve.py"], input=text,
                           capture_output=True, text=True)
        return p.returncode, p.stdout, p.stderr

    def test_cli_ok(self):
        code, out, _ = self._cli('{"total": 100, "people": 3, "tip_percent": 0}')
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out), {"ok": True, "result": [34, 33, 33]})

    def test_cli_errors(self):
        for text in ["not json", "{}", '{"total": 1.5, "people": 1, "tip_percent": 0}', "[1]"]:
            code, out, err = self._cli(text)
            self.assertEqual(code, 2)
            self.assertFalse(json.loads(out)["ok"])
            self.assertNotIn("Traceback", err)


if __name__ == "__main__":
    unittest.main()
