import json
import subprocess
import sys
import unittest

from solve import split_bill


def cli(payload):
    return subprocess.run([sys.executable, "solve.py"], input=payload,
                          capture_output=True, text=True)


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(split_bill(1000, 4, 0), [250] * 4)
        self.assertEqual(split_bill(1000, 3, 10), [367, 367, 366])

    def test_edges(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])
        self.assertEqual(split_bill(100, 1, 100), [200])
        self.assertEqual(split_bill(1, 3, 0), [1, 0, 0])

    def test_half_up(self):
        # 5 * 110/100 = 5.5 -> 6
        self.assertEqual(split_bill(5, 1, 10), [6])
        # 1 * 105/100 = 1.05 -> 1
        self.assertEqual(split_bill(1, 1, 5), [1])
        # 25*102/100 = 25.5 -> 26
        self.assertEqual(split_bill(25, 1, 2), [26])

    def test_errors(self):
        for args in [(-1, 1, 0), (10, 0, 0), (10, -1, 0), (10, 1, -1),
                     (10, 1, 101), (10.0, 1, 0), (10, 1.0, 0), (10, 1, 5.0),
                     (True, 1, 0), (10, True, 0), (10, 1, False),
                     ("10", 1, 0), (None, 1, 0)]:
            with self.assertRaises(ValueError, msg=str(args)):
                split_bill(*args)

    def test_cli_ok(self):
        r = cli('{"total": 1000, "people": 3, "tip_percent": 10}')
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": [367, 367, 366]})

    def test_cli_error(self):
        for p in ['{"total": 1000.0, "people": 3, "tip_percent": 10}',
                  '{"total": 1000, "people": 0, "tip_percent": 10}',
                  '{"total": 1000}', 'nope', '[1]']:
            r = cli(p)
            self.assertEqual(r.returncode, 2)
            self.assertFalse(json.loads(r.stdout)["ok"])
            self.assertNotIn("Traceback", r.stderr)


if __name__ == "__main__":
    unittest.main()
