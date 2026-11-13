import unittest
from solve import late_fee


class Normal(unittest.TestCase):
    def test_a(self):
        self.assertEqual(late_fee(100000, 10), 7500)

    def test_b(self):
        self.assertEqual(late_fee(20000, 5), 750)

    def test_zero_amount(self):
        self.assertEqual(late_fee(0, 100), 0)


class Boundary(unittest.TestCase):
    def test_3_days(self):
        self.assertEqual(late_fee(100000, 3), 0)

    def test_4_days(self):
        self.assertEqual(late_fee(100000, 4), 3000)

    def test_cap(self):
        # 20 days = 15% exactly; 21+ capped
        self.assertEqual(late_fee(100000, 20), 15000)
        self.assertEqual(late_fee(100000, 365), 15000)

    def test_ends(self):
        self.assertEqual(late_fee(100000, 0), 0)


class NoDrift(unittest.TestCase):
    def test_half(self):
        # 100*0.0075*4 = 3.0 ; 50*0.0075*5=1.875 -> 2
        self.assertEqual(late_fee(50, 5), 2)
        # 2*0.0075*100 -> capped 0.3 -> 0
        self.assertEqual(late_fee(2, 100), 0)
        # 10*0.0075*10=0.75 ->1 ; 200*.0075*5=7.5 -> 8
        self.assertEqual(late_fee(200, 5), 8)
        self.assertEqual(late_fee(10, 10), 1)


class Reject(unittest.TestCase):
    def test_bad(self):
        for a, d in [(-1, 5), (100.0, 5), ("1", 5), (True, 5), (100, -1),
                     (100, 366), (100, 5.0), (100, "3"), (100, True), (None, 1)]:
            with self.assertRaises(ValueError):
                late_fee(a, d)


if __name__ == "__main__":
    unittest.main()
