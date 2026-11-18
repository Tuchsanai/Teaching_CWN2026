import json, subprocess, sys, unittest
from solve import split_bill


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(split_bill(1000, 4, 0), [250] * 4)

    def test_remainder(self):
        self.assertEqual(split_bill(100, 3, 0), [34, 33, 33])
        self.assertEqual(split_bill(10, 4, 0), [3, 3, 2, 2])

    def test_tip(self):
        self.assertEqual(split_bill(1000, 2, 10), [550, 550])
        self.assertEqual(split_bill(1000, 3, 100), [667, 667, 666])

    def test_rounding(self):
        # 5*1.10=5.5 -> 6
        self.assertEqual(split_bill(5, 1, 10), [6])
        # 1*1.04=1.04 -> 1
        self.assertEqual(split_bill(1, 1, 4), [1])

    def test_zero(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_invalid(self):
        for a in [(-1, 1, 0), (10, 0, 0), (10, 1, -1), (10, 1, 101),
                  (10.0, 1, 0), (10, 1.0, 0), (10, 1, 5.0),
                  (True, 1, 0), (10, True, 0), (10, 1, False), ("10", 1, 0)]:
            with self.assertRaises(ValueError):
                split_bill(*a)

    def run_cli(self, s):
        return subprocess.run([sys.executable, "solve.py"], input=s,
                              capture_output=True, text=True)

    def test_cli_ok(self):
        r = self.run_cli('{"total":100,"people":3,"tip_percent":0}')
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": [34, 33, 33]})

    def test_cli_bad(self):
        r = self.run_cli('{"total":-5,"people":3,"tip_percent":0}')
        self.assertEqual(r.returncode, 2)
        self.assertFalse(json.loads(r.stdout)["ok"])
        self.assertNotIn("Traceback", r.stderr)


if __name__ == "__main__":
    unittest.main()
