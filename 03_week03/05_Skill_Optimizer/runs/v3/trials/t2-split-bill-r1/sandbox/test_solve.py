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
    def test_even_split(self):
        self.assertEqual(split_bill(1000, 4, 0), [250, 250, 250, 250])

    def test_remainder_to_first(self):
        self.assertEqual(split_bill(100, 3, 0), [34, 33, 33])

    def test_tip_exact(self):
        self.assertEqual(split_bill(1000, 2, 10), [550, 550])

    def test_tip_half_up(self):
        # 10 * 105 = 1050 -> 10.5 -> 11
        self.assertEqual(split_bill(10, 1, 5), [11])

    def test_zero_total(self):
        self.assertEqual(split_bill(0, 3, 20), [0, 0, 0])

    def test_sum_preserved(self):
        r = split_bill(9999, 7, 15)
        self.assertEqual(sum(r), (9999 * 115 * 2 + 100) // 200)
        self.assertLessEqual(max(r) - min(r), 1)

    def test_invalid_values(self):
        for args in [(-1, 1, 0), (10, 0, 0), (10, 1, 101), (10, 1, -1),
                     (10.0, 1, 0), (True, 1, 0), (10, "2", 0), (10, 1, None)]:
            with self.assertRaises(ValueError):
                split_bill(*args)

    def test_cli_ok(self):
        code, out, _ = run_cli('{"total": 100, "people": 3, "tip_percent": 0}')
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out), {"ok": True, "result": [34, 33, 33]})

    def test_cli_errors(self):
        for text in ["not json", '{"total": 1}', '[1]',
                     '{"total": 1, "people": 0, "tip_percent": 0}']:
            code, out, err = run_cli(text)
            self.assertEqual(code, 2)
            self.assertFalse(json.loads(out)["ok"])
            self.assertNotIn("Traceback", err)


if __name__ == "__main__":
    unittest.main()
