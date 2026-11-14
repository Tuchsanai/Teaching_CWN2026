import unittest
from fractions import Fraction
from solve import late_fee


def ref(a, d):
    if d <= 3:
        return 0
    v = Fraction(a) * min(Fraction(75, 10000) * d, Fraction(15, 100))
    return int((v * 2 + 1) // 2)


class Normal(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(late_fee(100000, 10), 7500)
        self.assertEqual(late_fee(5001, 7), ref(5001, 7))
        self.assertEqual(late_fee(0, 30), 0)

    def test_cap(self):
        self.assertEqual(late_fee(100000, 100), 15000)
        self.assertEqual(late_fee(25075, 365), ref(25075, 365))


class Boundary(unittest.TestCase):
    def test_grace(self):
        for d in (0, 1, 2, 3):
            self.assertEqual(late_fee(100000, d), 0)
        self.assertEqual(late_fee(100000, 4), 3000)  # นับรวม 3 วันแรก
        self.assertEqual(late_fee(100000, 5), 3750)

    def test_cap_edge(self):
        self.assertEqual(late_fee(100000, 19), 14250)
        self.assertEqual(late_fee(100000, 20), 15000)
        self.assertEqual(late_fee(100000, 21), 15000)
        self.assertEqual(late_fee(100000, 365), 15000)


class NoDrift(unittest.TestCase):
    def test_half(self):
        # 200*0.03=6 ; 10*0.03=0.3->0 ; 50*0.03=1.5->2 ; 150*0.0375=5.625->6
        self.assertEqual(late_fee(50, 4), 2)
        self.assertEqual(late_fee(10, 4), 0)
        self.assertEqual(late_fee(150, 5), 6)
        self.assertEqual(late_fee(10, 20), 2)   # 1.5 -> 2
        self.assertEqual(late_fee(30, 20), 5)   # 4.5 -> 5
        self.assertEqual(late_fee(10, 10), 1)   # 0.75 -> 1
        self.assertEqual(late_fee(1, 4), 0)

    def test_many(self):
        for a in (1, 33, 5333, 25075, 99999):
            for d in range(0, 366, 7):
                self.assertEqual(late_fee(a, d), ref(a, d))


class Reject(unittest.TestCase):
    def test_amount(self):
        for v in (-1, 1000.0, "1000", True, None, [1]):
            with self.assertRaises(ValueError):
                late_fee(v, 5)

    def test_days(self):
        for v in (-1, 366, 5.0, "5", True, False, None):
            with self.assertRaises(ValueError):
                late_fee(1000, v)

    def test_order(self):
        with self.assertRaises(ValueError):
            late_fee(1000, 366)
        with self.assertRaises(ValueError):
            late_fee(-1, 0)


if __name__ == "__main__":
    unittest.main()
