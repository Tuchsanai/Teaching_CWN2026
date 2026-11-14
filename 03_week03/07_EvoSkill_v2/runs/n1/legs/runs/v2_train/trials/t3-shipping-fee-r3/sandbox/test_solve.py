"""python3 -m unittest -q test_solve"""
import unittest

from solve import shipping_fee as f


class Normal(unittest.TestCase):
    def test_tiers(self):
        self.assertEqual(f(500, 10, False), 4000)
        self.assertEqual(f(3000, 10, False), 8000)
        self.assertEqual(f(10000, 10, False), 15500)

    def test_far_express(self):
        self.assertEqual(f(1000, 101, True), 7200)
        self.assertEqual(f(3000, 101, False), 9600)
        self.assertEqual(f(3000, 10, True), 12000)


class Boundary(unittest.TestCase):
    def test_lines(self):
        self.assertEqual(f(1000, 1, False), 4000)
        self.assertEqual(f(1001, 1, False), 8000)
        self.assertEqual(f(5000, 1, False), 8000)
        self.assertEqual(f(30000, 1, False), 45500)
        self.assertEqual(f(1, 1, False), 4000)

    def test_distance_line(self):
        self.assertEqual(f(1000, 100, False), 4000)
        self.assertEqual(f(1000, 101, False), 4800)

    def test_pickup_zero(self):
        self.assertEqual(f(30000, 0, False), 0)
        self.assertEqual(f(20000, 0, True), 0)

    def test_express_limit(self):
        self.assertEqual(f(20000, 1, True), 45750)
        with self.assertRaises(ValueError):
            f(20001, 1, True)
        with self.assertRaises(ValueError):
            f(20001, 0, True)


class NoDrift(unittest.TestCase):
    def test_rounding(self):
        self.assertEqual(f(5001, 1, False), 8002)    # 8001.5
        self.assertEqual(f(5001, 101, False), 9602)  # 9601.8
        self.assertEqual(f(5001, 1, True), 12002)    # 12002.25
        self.assertEqual(f(5003, 1, False), 8005)    # 8004.5


class Reject(unittest.TestCase):
    def test_bad(self):
        bad = [(0, 1, False), (30001, 1, False), (-1, 1, False), (1.0, 1, False),
               ('1', 1, False), (True, 1, False), (None, 1, False),
               (100, -1, False), (100, 1.0, False), (100, '1', False),
               (100, True, False), (100, None, False),
               (100, 1, 1), (100, 1, 0), (100, 1, 'yes'), (100, 1, None),
               (100, 0, 1)]
        for a in bad:
            with self.subTest(a=a), self.assertRaises(ValueError):
                f(*a)


if __name__ == "__main__":
    unittest.main()
