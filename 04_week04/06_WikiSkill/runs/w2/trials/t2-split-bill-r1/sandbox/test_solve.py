import json, subprocess, sys, unittest
from solve import split_bill


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(split_bill(1000, 4, 0), [250] * 4)
        self.assertEqual(split_bill(1000, 3, 0), [334, 333, 333])
        self.assertEqual(split_bill(1000, 2, 10), [550, 550])

    def test_zero(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_rounding(self):
        # 105*1.05 = 110.25 -> 110 ; /3 = 36 r2
        self.assertEqual(split_bill(105, 3, 5), [37, 37, 36])
        # 10*1.05 = 10.5 -> 11
        self.assertEqual(split_bill(10, 1, 5), [11])
        # 100 * 1.00 = 100, 7 คน -> 14 r2
        self.assertEqual(split_bill(100, 7, 0), [15, 15] + [14] * 5)

    def test_more_people_than_satang(self):
        self.assertEqual(split_bill(2, 5, 0), [1, 1, 0, 0, 0])

    def test_invalid(self):
        for args in [(-1, 1, 0), (10, 0, 0), (10, 1, -1), (10, 1, 101),
                     (10.0, 1, 0), (10, 1.0, 0), (10, 1, 5.0),
                     (True, 1, 0), (10, True, 0), (10, 1, False),
                     ("10", 1, 0), (None, 1, 0)]:
            with self.assertRaises(ValueError, msg=str(args)):
                split_bill(*args)

    def run_cli(self, s):
        return subprocess.run([sys.executable, "solve.py"], input=s,
                              capture_output=True, text=True)

    def test_cli_ok(self):
        r = self.run_cli('{"total":1000,"people":3,"tip_percent":0}')
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": [334, 333, 333]})

    def test_cli_bad(self):
        for s in ['{"total":-1,"people":1,"tip_percent":0}', 'xx', '[]', '{"total":1}']:
            r = self.run_cli(s)
            self.assertEqual(r.returncode, 2)
            self.assertFalse(json.loads(r.stdout)["ok"])
            self.assertNotIn("Traceback", r.stderr)


if __name__ == "__main__":
    unittest.main()
