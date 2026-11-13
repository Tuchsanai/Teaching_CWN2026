import unittest
from solve import late_fee


class Normal(unittest.TestCase):
    def test_cases(self):
        self.assertEqual(late_fee(100000, 10), 7500)   # 7.5%
        self.assertEqual(late_fee(100000, 4), 3000)    # 3%
        self.assertEqual(late_fee(0, 100), 0)


class Boundary(unittest.TestCase):
    def test_grace(self):
        self.assertEqual(late_fee(100000, 3), 0)
        self.assertEqual(late_fee(100000, 0), 0)
        self.assertEqual(late_fee(100000, 4), 3000)

    def test_cap(self):
        self.assertEqual(late_fee(100000, 19), 14250)
        self.assertEqual(late_fee(100000, 20), 15000)
        self.assertEqual(late_fee(100000, 21), 15000)
        self.assertEqual(late_fee(100000, 365), 15000)


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        # 10*4*0.0075 = 0.3 -> 0 ; 70*4*.0075=2.1 ->2 ; 50*5*.0075=1.875 ->2
        self.assertEqual(late_fee(70, 4), 2)
        self.assertEqual(late_fee(50, 5), 2)
        # 200*5*.0075 = 7.5 -> 8
        self.assertEqual(late_fee(200, 5), 8)
        # 10 * 0.03 = 0.3 -> 0 ; 50*0.03=1.5 -> 2
        self.assertEqual(late_fee(50, 4), 2)
        self.assertEqual(late_fee(10, 4), 0)


class Reject(unittest.TestCase):
    def test_bad(self):
        for a, d in [(-1, 5), (100, -1), (100, 366), (100.0, 5), (100, 5.0),
                     ("100", 5), (100, "5"), (True, 5), (100, True), (None, 5), (100, None)]:
            with self.assertRaises(ValueError):
                late_fee(a, d)


if __name__ == "__main__":
    unittest.main()
