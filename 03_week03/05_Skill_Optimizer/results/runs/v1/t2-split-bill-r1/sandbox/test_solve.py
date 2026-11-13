import json
import subprocess
import sys
import unittest

from solve import split_bill


def run_cli(text):
    p = subprocess.run([sys.executable, "solve.py"], input=text,
                       capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


class TestSplitBill(unittest.TestCase):
    def test_even(self):
        self.assertEqual(split_bill(1000, 4, 0), [250] * 4)

    def test_remainder_first_people(self):
        self.assertEqual(split_bill(1000, 3, 0), [334, 333, 333])

    def test_tip(self):
        self.assertEqual(split_bill(1000, 2, 10), [550, 550])

    def test_tip_rounding_half_up(self):
        # tip = 5*10/100 = 0.5 -> 1
        self.assertEqual(split_bill(5, 1, 10), [6])

    def test_zero_total(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_invalid(self):
        for args in [(1.0, 1, 0), (True, 1, 0), (10, 0, 0), (-1, 1, 0),
                     (10, 1, 101), ("1", 1, 0), (10, None, 0), (10, 1, 5.0)]:
            with self.assertRaises(ValueError):
                split_bill(*args)

    def test_cli_ok(self):
        code, out, _ = run_cli('{"total": 1000, "people": 3, "tip_percent": 0}')
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out), {"ok": True, "result": [334, 333, 333]})

    def test_cli_errors(self):
        for text in ["not json", '{"total": 1}', '[1]',
                     '{"total": 1.5, "people": 1, "tip_percent": 0}']:
            code, out, err = run_cli(text)
            self.assertEqual(code, 2)
            self.assertFalse(json.loads(out)["ok"])
            self.assertNotIn("Traceback", err)


if __name__ == "__main__":
    unittest.main()
