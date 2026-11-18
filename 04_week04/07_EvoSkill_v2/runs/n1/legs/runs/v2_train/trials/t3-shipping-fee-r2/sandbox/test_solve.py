"""python3 -m unittest -q test_solve"""
import unittest

from solve import shipping_fee as f


class Normal(unittest.TestCase):
    def test_tiers(self):
        self.assertEqual(f(500, 10, False), 4000)
        self.assertEqual(f(3000, 10, False), 8000)
        self.assertEqual(f(6000, 10, False), 9500)

    def test_far_express(self):
        self.assertEqual(f(6000, 150, True), 17100)
        self.assertEqual(f(500, 10, True), 6000)
        self.assertEqual(f(500, 101, False), 4800)


class Boundary(unittest.TestCase):
    def test_weight_lines(self):
        self.assertEqual(f(1000, 5, False), 4000)
        self.assertEqual(f(1001, 5, False), 8000)
        self.assertEqual(f(5000, 5, False), 8000)
        self.assertEqual(f(30000, 5, False), 8000 + 37500)
        self.assertEqual(f(1, 5, False), 4000)

    def test_distance_lines(self):
        self.assertEqual(f(500, 100, False), 4000)
        self.assertEqual(f(500, 101, False), 4800)

    def test_pickup(self):
        self.assertEqual(f(500, 0, False), 0)
        self.assertEqual(f(500, 0, True), 0)

    def test_express_limit(self):
        self.assertEqual(f(20000, 5, True), int((8000 + 22500) * 1.5))
        with self.assertRaises(ValueError):
            f(20001, 5, True)
        with self.assertRaises(ValueError):
            f(20001, 0, True)


class NoDrift(unittest.TestCase):
    def test_rounding(self):
        self.assertEqual(f(5001, 5, False), 8002)   # 8001.5 -> half-up
        self.assertEqual(f(5001, 101, False), 9602)  # 9601.8
        self.assertEqual(f(5003, 5, False), 8005)   # 8004.5 -> 8005
        self.assertEqual(f(5001, 5, True), 12002)   # 12002.25


class Reject(unittest.TestCase):
    def test_bad(self):
        bad = [(0, 5, False), (30001, 5, False), (-1, 5, False), (500.0, 5, False),
               ('5', 5, False), (True, 5, False), (None, 5, False),
               (500, -1, False), (500, 5.0, False), (500, '5', False),
               (500, True, False), (500, None, False),
               (500, 5, 1), (500, 5, 0), (500, 5, 'yes'), (500, 5, None),
               (500, 0, 1)]
        for args in bad:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    f(*args)


if __name__ == "__main__":
    unittest.main()
