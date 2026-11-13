import subprocess, sys, unittest
from solve import split_bill


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(split_bill(10000, 4, 0), [2500] * 4)
        self.assertEqual(split_bill(10000, 3, 10), [3667, 3667, 3666])
        self.assertEqual(split_bill(0, 2, 50), [0, 0])
        self.assertEqual(split_bill(100, 1, 100), [200])

    def test_half_up(self):
        # 10*1.05=10.5 -> 11 (floor would give 10)
        self.assertEqual(split_bill(10, 1, 5), [11])

    def test_sum(self):
        r = split_bill(12345, 7, 13)
        self.assertEqual(sum(r), 13950)  # 12345*1.13=13949.85 -> 13950
        self.assertTrue(all(type(x) is int for x in r))

    def test_reject(self):
        for a in [(-1, 1, 0), (1, 0, 0), (1, 1, -1), (1, 1, 101), (1.0, 1, 0),
                  ("3", 1, 0), (True, 1, 0), (1, True, 0), (1, 1, None),
                  (float("nan"), 1, 0), (1, 1, 5.0)]:
            with self.assertRaises(ValueError):
                split_bill(*a)

    def test_big(self):
        self.assertEqual(sum(split_bill(10**12, 3, 7)), 1070000000000)

    def test_cli(self):
        p = subprocess.run([sys.executable, "solve.py"], input='{"total":10000,"people":3,"tip_percent":10}',
                           capture_output=True, text=True)
        self.assertEqual(p.stdout.strip(), '{"ok": true, "result": [3667, 3667, 3666]}')
        p = subprocess.run([sys.executable, "solve.py"], input='{"total":-1,"people":3,"tip_percent":10}',
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 2)


