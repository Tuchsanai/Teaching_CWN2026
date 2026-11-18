import json, subprocess, sys, unittest
from solve import late_fee


def run(payload):
    return subprocess.run([sys.executable, "solve.py"], input=payload,
                          capture_output=True, text=True)


class T(unittest.TestCase):
    def test_grace(self):
        self.assertEqual(late_fee(100000, 0), 0)
        self.assertEqual(late_fee(100000, 3), 0)

    def test_basic(self):
        self.assertEqual(late_fee(100000, 4), 3000)   # 3%
        self.assertEqual(late_fee(100000, 10), 7500)  # 7.5%

    def test_cap(self):
        self.assertEqual(late_fee(100000, 20), 15000)
        self.assertEqual(late_fee(100000, 21), 15000)
        self.assertEqual(late_fee(100000, 365), 15000)
        self.assertEqual(late_fee(0, 10), 0)

    def test_rounding(self):
        self.assertEqual(late_fee(100, 4), 3)    # 3.0
        self.assertEqual(late_fee(50, 4), 2)     # 1.5 -> 2
        self.assertEqual(late_fee(49, 4), 1)     # 1.47 -> 1

    def test_invalid(self):
        for a, d in [(-1, 5), (100, -1), (100, 366), (100.0, 5), (100, 5.0),
                     (True, 5), (100, True), ("1", 5), (None, 5)]:
            with self.assertRaises(ValueError):
                late_fee(a, d)

    def test_cli(self):
        r = run(json.dumps({"amount": 100000, "days_late": 4}))
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 3000})
        r = run(json.dumps({"amount": -5, "days_late": 4}))
        self.assertEqual(r.returncode, 2)
        self.assertFalse(json.loads(r.stdout)["ok"])
        self.assertNotIn("Traceback", r.stderr)


if __name__ == "__main__":
    unittest.main()
