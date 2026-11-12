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
        self.assertEqual(split_bill(1000, 4, 0), [250] * 4)

    def test_remainder(self):
        self.assertEqual(split_bill(100, 3, 0), [34, 33, 33])

    def test_zero(self):
        self.assertEqual(split_bill(0, 2, 10), [0, 0])

    def test_half_up_tip(self):
        # 105 * 1.10 = 115.5 -> 116
        self.assertEqual(split_bill(105, 1, 10), [116])

    def test_tip_then_split(self):
        # 999 * 1.15 = 1148.85 -> 1149; /4 = 287 r 1
        self.assertEqual(split_bill(999, 4, 15), [288, 287, 287, 287])

    def test_more_people_than_satang(self):
        self.assertEqual(split_bill(2, 5, 0), [1, 1, 0, 0, 0])

    def test_invalid(self):
        bad = [(-1, 1, 0), (1.0, 1, 0), (True, 1, 0), ("1", 1, 0), (None, 1, 0),
               (10, 0, 0), (10, 1.0, 0), (10, True, 0), (10, "1", 0), (10, None, 0),
               (10, 1, -1), (10, 1, 101), (10, 1, 5.0), (10, 1, True), (10, 1, "5"), (10, 1, None)]
        for a in bad:
            with self.assertRaises(ValueError, msg=a):
                split_bill(*a)

    def test_cli_ok(self):
        r = run('{"total": 100, "people": 3, "tip_percent": 0}')
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": [34, 33, 33]})

    def test_cli_err(self):
        for p in ['{"total": 1.5, "people": 1, "tip_percent": 0}', 'xx', '{"total": 1}']:
            r = run(p)
            self.assertEqual(r.returncode, 2)
            self.assertFalse(json.loads(r.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
