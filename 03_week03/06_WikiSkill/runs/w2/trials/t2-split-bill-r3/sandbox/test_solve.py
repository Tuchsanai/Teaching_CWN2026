import json, subprocess, sys, unittest
from solve import split_bill


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(split_bill(1000, 3, 10), [367, 367, 366])
        self.assertEqual(split_bill(1000, 4, 0), [250] * 4)

    def test_edges(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])
        self.assertEqual(split_bill(100, 1, 100), [200])
        self.assertEqual(split_bill(1, 3, 0), [1, 0, 0])

    def test_rounding(self):
        self.assertEqual(split_bill(1005, 2, 10), [553, 553])  # 1105.5 -> 1106
        self.assertEqual(split_bill(1004, 1, 10), [1104])  # 1104.4 -> 1104

    def test_invalid(self):
        for args in [(-1, 1, 0), (10, 0, 0), (10, 1, -1), (10, 1, 101),
                     (10.0, 1, 0), (10, 1.0, 0), (10, 1, 5.0),
                     (True, 1, 0), (10, True, 0), (10, 1, False), ("10", 1, 0)]:
            with self.assertRaises(ValueError):
                split_bill(*args)

    def run_cli(self, s):
        return subprocess.run([sys.executable, "solve.py"], input=s,
                              capture_output=True, text=True)

    def test_cli(self):
        r = self.run_cli('{"total":1000,"people":3,"tip_percent":10}')
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout), {"ok": True, "result": [367, 367, 366]})
        r = self.run_cli('{"total":-1,"people":3,"tip_percent":10}')
        self.assertEqual(r.returncode, 2)
        self.assertFalse(json.loads(r.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
