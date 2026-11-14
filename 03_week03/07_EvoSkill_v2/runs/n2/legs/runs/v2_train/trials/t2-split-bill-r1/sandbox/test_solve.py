import json
import subprocess
import sys
import unittest

from solve import split_bill


class Normal(unittest.TestCase):
    def test_1(self):
        self.assertEqual(split_bill(10000, 3, 0), [3334, 3333, 3333])

    def test_2(self):
        self.assertEqual(split_bill(10000, 7, 10), [1572, 1572, 1572, 1571, 1571, 1571, 1571])

    def test_3(self):
        self.assertEqual(split_bill(10000, 4, 0), [2500] * 4)

    def test_4(self):
        self.assertEqual(split_bill(9999, 1, 100), [19998])


class Boundary(unittest.TestCase):
    def test_zero_total(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])

    def test_tiny(self):
        self.assertEqual(split_bill(2, 3, 0), [1, 1, 0])

    def test_one_person(self):
        self.assertEqual(split_bill(12345, 1, 0), [12345])

    def test_tip_100(self):
        self.assertEqual(split_bill(101, 2, 100), [101, 101])


class NoDrift(unittest.TestCase):
    def test_half_up(self):  # 101*105/100 = 106.05 -> 106
        self.assertEqual(split_bill(101, 1, 5), [106])

    def test_half_exact(self):  # 10*105/100 = 10.5 -> 11 (ไม่ใช่ banker's 10)
        self.assertEqual(split_bill(10, 1, 5), [11])

    def test_large(self):
        self.assertEqual(sum(split_bill(10**15 + 1, 7, 13)), (10**15 + 1) * 113 // 100 + (1 if ((10**15 + 1) * 113 % 100) >= 50 else 0))


class Reject(unittest.TestCase):
    def test_bad(self):
        bad = [(-1, 1, 0), (1, 0, 0), (1, -1, 0), (1, 1, -1), (1, 1, 101),
               (1.0, 1, 0), (1, 1.0, 0), (1, 1, 5.0), ("1", 1, 0), (1, "1", 0),
               (1, 1, "5"), (True, 1, 0), (1, True, 0), (1, 1, True), (None, 1, 0)]
        for args in bad:
            with self.subTest(args=args), self.assertRaises(ValueError):
                split_bill(*args)


class Cli(unittest.TestCase):
    def run_cli(self, payload):
        p = subprocess.run([sys.executable, "solve.py"], input=json.dumps(payload),
                           capture_output=True, text=True)
        return p.returncode, json.loads(p.stdout)

    def test_ok(self):
        self.assertEqual(self.run_cli({"total": 10000, "people": 3, "tip_percent": 0}),
                         (0, {"ok": True, "result": [3334, 3333, 3333]}))

    def test_error(self):
        code, out = self.run_cli({"total": 1, "people": 0, "tip_percent": 0})
        self.assertEqual(code, 2)
        self.assertFalse(out["ok"])


if __name__ == "__main__":
    unittest.main()
