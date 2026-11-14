import json, subprocess, sys, unittest
from solve import cashback


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(cashback(20000, "silver", False), 300)
        self.assertEqual(cashback(20000, "gold", False), 500)
        self.assertEqual(cashback(20000, "platinum", False), 800)

    def test_threshold(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(0, "gold", False), 0)
        self.assertEqual(cashback(10000, "silver", False), 150)

    def test_birthday(self):
        self.assertEqual(cashback(20000, "gold", True), 1000)

    def test_rounding(self):
        # 10001*0.015=150.015 -> 150 ; 10033*0.015=150.495 -> 150 ; 10034*.015=150.51 -> 151
        self.assertEqual(cashback(10001, "silver", False), 150)
        self.assertEqual(cashback(10034, "silver", False), 151)
        # 10010*0.025=250.25 ; 10030*.025=250.75 -> 251 ; 10020*.025=250.5 -> 251
        self.assertEqual(cashback(10020, "gold", False), 251)

    def test_cap(self):
        self.assertEqual(cashback(500000, "gold", False), 12500)
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(500000, "gold", True), 20000)
        self.assertEqual(cashback(10**9, "silver", True), 20000)

    def test_invalid(self):
        for args in [(-1, "gold", False), (20000.0, "gold", False),
                     (True, "gold", False), ("1", "gold", False),
                     (20000, "bronze", False), (20000, 1, False),
                     (20000, "gold", 1), (20000, "gold", None),
                     (-5, "gold", False)]:
            with self.assertRaises(ValueError):
                cashback(*args)

    def run_cli(self, s):
        return subprocess.run([sys.executable, "solve.py"], input=s,
                              capture_output=True, text=True)

    def test_cli(self):
        r = self.run_cli('{"amount":20000,"tier":"gold","birthday":true}')
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 1000})
        r = self.run_cli('{"amount":-1,"tier":"gold","birthday":true}')
        self.assertEqual(r.returncode, 2)
        self.assertFalse(json.loads(r.stdout)["ok"])
        self.assertNotIn("Traceback", r.stderr)


if __name__ == "__main__":
    unittest.main()
