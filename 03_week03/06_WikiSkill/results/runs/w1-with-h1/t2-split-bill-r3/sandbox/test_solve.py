import json
import subprocess
import sys
import unittest

from solve import split_bill


def run(payload):
    return subprocess.run([sys.executable, "solve.py"], input=payload,
                          capture_output=True, text=True)


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(split_bill(1000, 2, 0), [500, 500])
        self.assertEqual(split_bill(1000, 3, 0), [334, 333, 333])
        self.assertEqual(split_bill(0, 3, 10), [0, 0, 0])
        self.assertEqual(split_bill(100, 1, 100), [200])

    def test_tip_half_up(self):
        # 105 * 110% = 115.5 -> 116 -> 58, 58
        self.assertEqual(split_bill(105, 2, 10), [58, 58])
        # 1 * 150%? tip max 100; 1*105% = 1.05 -> 1
        self.assertEqual(split_bill(1, 1, 5), [1])
        # 10 * 105% = 10.5 -> 11 -> 4,4,3
        self.assertEqual(split_bill(10, 3, 5), [4, 4, 3])

    def test_sum_and_more_people_than_money(self):
        r = split_bill(2, 5, 0)
        self.assertEqual(r, [1, 1, 0, 0, 0])

    def test_invalid(self):
        bad = [(1.0, 1, 0), (True, 1, 0), ("1", 1, 0), (None, 1, 0), (-1, 1, 0),
               (1, 1.0, 0), (1, True, 0), (1, "1", 0), (1, None, 0), (1, 0, 0),
               (1, 1, 0.0), (1, 1, True), (1, 1, "0"), (1, 1, None),
               (1, 1, -1), (1, 1, 101)]
        for a in bad:
            with self.assertRaises(ValueError, msg=str(a)):
                split_bill(*a)

    def test_cli(self):
        r = run(json.dumps({"total": 1000, "people": 3, "tip_percent": 0}))
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": [334, 333, 333]})
        for p in ['{"total": 1, "people": 0, "tip_percent": 0}', 'xx', '{"total":1}', '[]']:
            r = run(p)
            self.assertEqual(r.returncode, 2)
            self.assertFalse(json.loads(r.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
