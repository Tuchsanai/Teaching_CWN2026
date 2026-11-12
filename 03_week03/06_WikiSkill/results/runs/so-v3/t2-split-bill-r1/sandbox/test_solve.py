import json
import subprocess
import sys
import unittest

from solve import split_bill


class TestSplitBill(unittest.TestCase):
    def test_even(self):
        self.assertEqual(split_bill(1000, 2, 0), [500, 500])

    def test_remainder_to_first(self):
        self.assertEqual(split_bill(1000, 3, 10), [367, 367, 366])

    def test_half_up_once(self):
        self.assertEqual(split_bill(5, 1, 10), [6])
        self.assertEqual(split_bill(1, 1, 50), [2])

    def test_zero_total(self):
        self.assertEqual(split_bill(0, 3, 20), [0, 0, 0])

    def test_more_people_than_satang(self):
        self.assertEqual(split_bill(2, 4, 0), [1, 1, 0, 0])

    def test_invalid(self):
        for args in [(1.0, 1, 0), (True, 1, 0), (10, 0, 0), (10, 1, 101),
                     (-1, 1, 0), (10, "2", 0), (10, 1, None), (10, 1, -1)]:
            with self.assertRaises(ValueError):
                split_bill(*args)

    def test_cli(self):
        p = subprocess.run([sys.executable, "solve.py"], input=json.dumps(
            {"total": 1000, "people": 3, "tip_percent": 10}),
            capture_output=True, text=True)
        self.assertEqual(p.returncode, 0)
        self.assertEqual(json.loads(p.stdout), {"ok": True, "result": [367, 367, 366]})

    def test_cli_errors(self):
        for s in ["not json", "{}", '{"total": 1, "people": 1, "tip_percent": true}']:
            p = subprocess.run([sys.executable, "solve.py"], input=s,
                               capture_output=True, text=True)
            self.assertEqual(p.returncode, 2)
            self.assertFalse(json.loads(p.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
