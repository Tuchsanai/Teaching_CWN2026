import json, subprocess, sys, unittest
from solve import split_bill


class T(unittest.TestCase):
    def test_even(self):
        self.assertEqual(split_bill(1000, 4, 0), [250] * 4)

    def test_remainder(self):
        self.assertEqual(split_bill(1000, 3, 0), [334, 333, 333])

    def test_tip(self):
        self.assertEqual(split_bill(1000, 2, 10), [550, 550])

    def test_tip_rounding(self):
        # tip = 1005*7/100 = 70.35 -> 70 ; 1075 / 2
        self.assertEqual(split_bill(1005, 2, 7), [538, 537])
        self.assertEqual(split_bill(50, 1, 1), [51])  # 0.5 -> 1

    def test_zero(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_sum(self):
        r = split_bill(9999, 7, 13)
        self.assertEqual(sum(r), 9999 + (9999 * 13 + 50) // 100)

    def test_invalid(self):
        for a in [(-1, 1, 0), (1, 0, 0), (1, 1, 101), (1, 1, -1),
                  (1.5, 1, 0), (1, 1.0, 0), (1, 1, 5.0), (True, 1, 0), ("1", 1, 0)]:
            with self.assertRaises(ValueError):
                split_bill(*a)

    def test_cli(self):
        p = subprocess.run([sys.executable, "solve.py", '{"total":1000,"people":3,"tip_percent":0}'],
                           capture_output=True, text=True)
        self.assertEqual(json.loads(p.stdout), {"shares": [334, 333, 333]})
        p = subprocess.run([sys.executable, "solve.py"], input='{"total":1,"people":0,"tip_percent":0}',
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 1)
        self.assertIn("error", json.loads(p.stdout))


if __name__ == "__main__":
    unittest.main()
