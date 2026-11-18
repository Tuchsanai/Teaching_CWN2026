import json, subprocess, sys, unittest
from solve import refund


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(refund(10000, 50, False), 5000)
        self.assertEqual(refund(10000, 0, False), 10000)
        self.assertEqual(refund(0, 10, True), 0)

    def test_restock(self):
        self.assertEqual(refund(10000, 50, True), 4375)

    def test_threshold(self):
        self.assertEqual(refund(10000, 80, False), 2000)
        self.assertEqual(refund(10000, 81, False), 0)
        self.assertEqual(refund(10000, 100, True), 0)

    def test_rounding(self):
        # 101*0.5 = 50.5 -> 51
        self.assertEqual(refund(101, 50, False), 51)
        # 100*0.99*0.875 = 86.625 -> 87
        self.assertEqual(refund(100, 1, True), 87)
        # 1*0.5 = 0.5 -> 1
        self.assertEqual(refund(1, 50, False), 1)

    def test_invalid(self):
        for args in [(-1, 0, False), (100, -1, False), (100, 101, False),
                     (100.0, 10, False), (100, 10.0, False), (True, 10, False),
                     (100, True, False), (100, 10, 1), (100, 10, "yes"),
                     ("100", 10, False)]:
            with self.assertRaises(ValueError):
                refund(*args)

    def run_cli(self, s):
        return subprocess.run([sys.executable, "solve.py"], input=s,
                              capture_output=True, text=True)

    def test_cli(self):
        r = self.run_cli('{"paid":10000,"used_percent":50,"restock":true}')
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": 4375})
        r = self.run_cli('{"paid":-5,"used_percent":50,"restock":true}')
        self.assertEqual(r.returncode, 2)
        self.assertFalse(json.loads(r.stdout)["ok"])
        self.assertNotIn("Traceback", r.stderr)


if __name__ == "__main__":
    unittest.main()
