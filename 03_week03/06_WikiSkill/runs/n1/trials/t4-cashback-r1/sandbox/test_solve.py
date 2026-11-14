import json
import subprocess
import sys
import unittest

from solve import cashback


def run(payload):
    p = subprocess.run([sys.executable, "solve.py"], input=payload,
                       capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cashback(20000, "silver", False), 300)
        self.assertEqual(cashback(20000, "gold", False), 500)
        self.assertEqual(cashback(20000, "platinum", False), 800)

    def test_birthday(self):
        self.assertEqual(cashback(20000, "gold", True), 1000)

    def test_min_boundary(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "platinum", False), 400)
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_cap(self):
        self.assertEqual(cashback(500000, "gold", False), 12500)
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(1000000, "platinum", True), 20000)
        self.assertEqual(cashback(500000, "platinum", True), 20000)

    def test_half_up(self):
        # 10100*1.5% = 151.5 -> 152
        self.assertEqual(cashback(10100, "silver", False), 152)
        # 10020*2.5% = 250.5 -> 251
        self.assertEqual(cashback(10020, "gold", False), 251)

    def test_errors(self):
        bad = [(-1, "gold", False), (10000.0, "gold", False),
               (True, "gold", False), ("1", "gold", False),
               (10000, "bronze", False), (10000, 1, False),
               (10000, "gold", 1), (10000, "gold", None)]
        for a in bad:
            with self.assertRaises(ValueError, msg=str(a)):
                cashback(*a)

    def test_cli_ok(self):
        code, out, _ = run('{"amount": 20000, "tier": "gold", "birthday": true}')
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out), {"ok": True, "result": 1000})

    def test_cli_error(self):
        for payload in ['{"amount": 20000.0, "tier": "gold", "birthday": false}',
                        '{"amount": 1}', 'nope', '[]']:
            code, out, err = run(payload)
            self.assertEqual(code, 2)
            self.assertFalse(json.loads(out)["ok"])
            self.assertNotIn("Traceback", err)


if __name__ == "__main__":
    unittest.main()
