import json
import subprocess
import sys
import unittest

from solve import cashback


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cashback(20000, "silver", False), 300)
        self.assertEqual(cashback(20000, "gold", False), 500)
        self.assertEqual(cashback(20000, "platinum", False), 800)
        self.assertEqual(cashback(20000, "gold", True), 1000)

    def test_min_boundary(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_cap(self):
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(1000000, "platinum", True), 20000)
        self.assertEqual(cashback(500000, "gold", False), 12500)

    def test_half_up(self):
        self.assertEqual(cashback(10010, "silver", False), 150)   # 150.15
        self.assertEqual(cashback(10033, "silver", False), 150)   # 150.495
        self.assertEqual(cashback(10034, "silver", False), 151)   # 150.51
        self.assertEqual(cashback(10030, "silver", False), 150)   # 150.45
        self.assertEqual(cashback(10050, "silver", False), 151)   # 150.75
        self.assertEqual(cashback(10010, "gold", False), 250)     # 250.25
        self.assertEqual(cashback(10020, "gold", False), 251)     # 250.5 -> up

    def test_errors(self):
        for args in [(-1, "gold", False), (100.0, "gold", False), (True, "gold", False),
                     ("1", "gold", False), (20000, "bronze", False), (20000, 1, False),
                     (20000, "gold", 1), (20000, "gold", None)]:
            with self.assertRaises(ValueError):
                cashback(*args)

    def run_cli(self, s):
        p = subprocess.run([sys.executable, "solve.py"], input=s, capture_output=True, text=True)
        return p.returncode, p.stdout, p.stderr

    def test_cli(self):
        rc, out, _ = self.run_cli('{"amount": 20000, "tier": "gold", "birthday": true}')
        self.assertEqual((rc, json.loads(out)), (0, {"ok": True, "result": 1000}))
        for s in ['{"amount": 20000.0, "tier": "gold", "birthday": true}', 'bad', '{"amount": 1}', '[]']:
            rc, out, err = self.run_cli(s)
            self.assertEqual(rc, 2)
            self.assertFalse(json.loads(out)["ok"])
            self.assertNotIn("Traceback", err)


if __name__ == "__main__":
    unittest.main()
