import unittest

from solve import shipping_fee as f


class Normal(unittest.TestCase):
    def test_small(self):
        self.assertEqual(f(500, 10, False), 4000)

    def test_heavy(self):
        self.assertEqual(f(6000, 1, False), 9500)

    def test_far_express(self):
        self.assertEqual(f(6000, 101, True), 17100)


class Boundary(unittest.TestCase):
    def test_1000_1001(self):
        self.assertEqual(f(1000, 5, False), 4000)
        self.assertEqual(f(1001, 5, False), 8000)

    def test_5000_5001(self):
        self.assertEqual(f(5000, 5, False), 8000)
        self.assertEqual(f(5001, 5, False), 8002)  # 8001.5 half-up

    def test_distance_100_101(self):
        self.assertEqual(f(500, 100, False), 4000)
        self.assertEqual(f(500, 101, False), 4800)

    def test_express_cap(self):
        self.assertEqual(f(20000, 1, True), 45750)  # (8000+22500)*1.5



class NoDrift(unittest.TestCase):
    def test_half_satang(self):
        self.assertEqual(f(5003, 1, False), 8005)  # 8004.5 -> 8005
        self.assertEqual(f(5001, 101, False), 9602)  # 8001.5*1.2=9601.8

    def test_express_fraction(self):
        self.assertEqual(f(5001, 1, True), 12002)  # 12002.25


class Reject(unittest.TestCase):
    def test_types(self):
        for args in [(100.0, 1, False), ("5", 1, False), (100, 1.5, False),
                     (True, 1, False), (100, 1, 1), (None, 1, False)]:
            with self.assertRaises(ValueError):
                f(*args)

    def test_range(self):
        for args in [(0, 1, False), (30001, 1, False), (100, -1, False)]:
            with self.assertRaises(ValueError):
                f(*args)

    def test_express_over_cap(self):
        with self.assertRaises(ValueError):
            f(20001, 1, True)

    def test_zero_distance_still_validates(self):
        self.assertEqual(f(100, 0, False), 0)
        with self.assertRaises(ValueError):
            f(0, 0, False)


if __name__ == "__main__":
    unittest.main()
