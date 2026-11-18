import json
import subprocess
import sys
import unittest

from solve import split_bill


class T(unittest.TestCase):
    def test_even(self):
        self.assertEqual(split_bill(1000, 2, 0), [500, 500])

    def test_remainder(self):
        self.assertEqual(split_bill(100, 3, 0), [34, 33, 33])

    def test_tip(self):
        self.assertEqual(split_bill(1000, 4, 10), [275] * 4)

    def test_tip_rounding(self):
        # tip = 5*10/100 = 0.5 -> 1
        self.assertEqual(split_bill(5, 1, 10), [6])

    def test_zero(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_sum(self):
        r = split_bill(9999, 7, 13)
        self.assertEqual(sum(r), 9999 + (9999 * 13 + 50) // 100)
        self.assertLessEqual(max(r) - min(r), 1)

    def test_invalid(self):
        for args in [(-1, 1, 0), (1, 0, 0), (1, 1, -1), (1, 1, 101),
                     (1.5, 1, 0), (1, 1, True), ("1", 1, 0)]:
            with self.assertRaises(ValueError):
                split_bill(*args)

    def test_cli(self):
        p = subprocess.run([sys.executable, "solve.py"], capture_output=True, text=True,
                           input=json.dumps({"total": 100, "people": 3, "tip_percent": 0}))
        self.assertEqual(json.loads(p.stdout), [34, 33, 33])
        p = subprocess.run([sys.executable, "solve.py", '{"total":1,"people":0,"tip_percent":0}'],
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 1)
        self.assertIn("error", json.loads(p.stdout))


if __name__ == "__main__":
    unittest.main()
