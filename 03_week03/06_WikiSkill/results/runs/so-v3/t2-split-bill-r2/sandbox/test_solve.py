import json
import subprocess
import sys
import unittest

from solve import split_bill


class TestSplitBill(unittest.TestCase):
    def test_even_split(self):
        self.assertEqual(split_bill(1000, 4, 0), [250, 250, 250, 250])

    def test_remainder_to_first(self):
        self.assertEqual(split_bill(100, 3, 0), [34, 33, 33])

    def test_tip_added(self):
        self.assertEqual(split_bill(1000, 2, 10), [550, 550])

    def test_tip_half_up(self):
        # 10 * 105 = 1050 -> 10.5 exactly -> rounds up to 11
        self.assertEqual(split_bill(10, 1, 5), [11])

    def test_zero_total(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_more_people_than_satang(self):
        self.assertEqual(split_bill(2, 4, 0), [1, 1, 0, 0])

    def test_invalid_inputs(self):
        for args in [(-1, 1, 0), (1, 0, 0), (1, 1, 101), (1, 1, -1),
                     (1.0, 1, 0), (True, 1, 0), (1, "2", 0), (None, 1, 0)]:
            with self.assertRaises(ValueError):
                split_bill(*args)

    def test_cli(self):
        ok = subprocess.run([sys.executable, "solve.py"], input='{"total": 100, "people": 3, "tip_percent": 0}',
                            capture_output=True, text=True)
        self.assertEqual(ok.returncode, 0)
        self.assertEqual(json.loads(ok.stdout), {"ok": True, "result": [34, 33, 33]})
        for bad in ["not json", '{"total": 1}', '{"total": 1, "people": 0, "tip_percent": 0}']:
            r = subprocess.run([sys.executable, "solve.py"], input=bad, capture_output=True, text=True)
            self.assertEqual(r.returncode, 2)
            self.assertFalse(json.loads(r.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
