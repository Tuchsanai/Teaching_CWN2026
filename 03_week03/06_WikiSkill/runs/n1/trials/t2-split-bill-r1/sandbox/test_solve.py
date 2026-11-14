import json
import subprocess
import sys
import unittest

from solve import split_bill


def cli(payload):
    p = subprocess.run([sys.executable, "solve.py"], input=payload,
                       capture_output=True, text=True)
    return p.returncode, json.loads(p.stdout), p.stderr


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(split_bill(10000, 4, 10), [2750] * 4)

    def test_remainder(self):
        self.assertEqual(split_bill(100, 3, 0), [34, 33, 33])

    def test_zero_total(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_one_person(self):
        self.assertEqual(split_bill(999, 1, 100), [1998])

    def test_half_up(self):
        # 1 * 150 / 100 = 1.5 -> 2
        self.assertEqual(split_bill(1, 1, 50), [2])
        # 3 * 110 / 100 = 3.3 -> 3
        self.assertEqual(split_bill(3, 1, 10), [3])
        # 5 * 110 / 100 = 5.5 -> 6
        self.assertEqual(split_bill(5, 1, 10), [6])

    def test_sum(self):
        self.assertEqual(sum(split_bill(12345, 7, 13)), (2 * 12345 * 113 + 100) // 200)

    def test_errors(self):
        bad = [(-1, 1, 0), (1, 0, 0), (1, -1, 0), (1, 1, -1), (1, 1, 101),
               (1.0, 1, 0), (1, 1.0, 0), (1, 1, 5.0), (True, 1, 0),
               (1, True, 0), (1, 1, True), ("1", 1, 0), (None, 1, 0)]
        for a in bad:
            with self.assertRaises(ValueError, msg=str(a)):
                split_bill(*a)

    def test_cli_ok(self):
        code, out, _ = cli('{"total": 100, "people": 3, "tip_percent": 0}')
        self.assertEqual(code, 0)
        self.assertEqual(out, {"ok": True, "result": [34, 33, 33]})

    def test_cli_errors(self):
        for payload in ['{"total": 100.0, "people": 3, "tip_percent": 0}',
                        '{"total": 100, "people": 0, "tip_percent": 0}',
                        '{"total": 100}', '[1]']:
            code, out, err = cli(payload)
            self.assertEqual(code, 2)
            self.assertFalse(out["ok"])
            self.assertNotIn("Traceback", err)

    def test_cli_bad_json(self):
        p = subprocess.run([sys.executable, "solve.py"], input="{bad",
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 2)
        self.assertNotIn("Traceback", p.stderr)


if __name__ == "__main__":
    unittest.main()
