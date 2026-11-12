import json
import subprocess
import sys
import unittest

from solve import split_bill


def run(payload):
    return subprocess.run([sys.executable, "solve.py"], input=payload,
                          capture_output=True, text=True)


class T(unittest.TestCase):
    def test_even(self):
        self.assertEqual(split_bill(1000, 2, 0), [500, 500])

    def test_remainder(self):
        self.assertEqual(split_bill(1000, 3, 0), [334, 333, 333])

    def test_tip(self):
        self.assertEqual(split_bill(1000, 4, 10), [275] * 4)

    def test_half_up(self):
        # 15*110/100 = 16.5 -> 17
        self.assertEqual(split_bill(15, 1, 10), [17])
        # 1*50/100 = 1.5 -> 2 ; 1*149/100=1.49 -> 1
        self.assertEqual(split_bill(1, 1, 50), [2])
        self.assertEqual(split_bill(1, 1, 49), [1])

    def test_zero(self):
        self.assertEqual(split_bill(0, 3, 20), [0, 0, 0])

    def test_more_people_than_satang(self):
        self.assertEqual(split_bill(2, 4, 0), [1, 1, 0, 0])

    def test_invalid(self):
        bad = [(1.0, 1, 0), (True, 1, 0), ("1", 1, 0), (None, 1, 0), (-1, 1, 0),
               (1, 0, 0), (1, 1.0, 0), (1, True, 0), (1, None, 0), (1, "1", 0),
               (1, 1, -1), (1, 1, 101), (1, 1, 1.0), (1, 1, True), (1, 1, None),
               (1, 1, "1")]
        for a in bad:
            with self.assertRaises(ValueError):
                split_bill(*a)

    def test_cli(self):
        r = run(json.dumps({"total": 1000, "people": 3, "tip_percent": 0}))
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": [334, 333, 333]})
        r = run(json.dumps({"total": 1, "people": 0, "tip_percent": 0}))
        self.assertEqual(r.returncode, 2)
        self.assertFalse(json.loads(r.stdout)["ok"])
        self.assertEqual(run("not json").returncode, 2)


if __name__ == "__main__":
    unittest.main()
