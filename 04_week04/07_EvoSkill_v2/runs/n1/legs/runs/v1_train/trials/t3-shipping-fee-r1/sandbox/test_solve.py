"""python3 -m unittest -q test_solve"""
import unittest

from solve import shipping_fee as f


class Normal(unittest.TestCase):
    def test_tiers(self):
        self.assertEqual(f(500, 10, False), 4000)
        self.assertEqual(f(3000, 10, False), 8000)
        self.assertEqual(f(7000, 10, False), 11000)

    def test_combo(self):
        self.assertEqual(f(7000, 150, True), 19800)  # 11000*1.2*1.5

    def test_pickup(self):
        self.assertEqual(f(500, 0, True), 0)


class Boundary(unittest.TestCase):
    def test_lines(self):
        self.assertEqual(f(1000, 1, False), 4000)
        self.assertEqual(f(1001, 1, False), 8000)
        self.assertEqual(f(5000, 1, False), 8000)
        self.assertEqual(f(5001, 1, False), 8002)  # 8001.5 half-up
        self.assertEqual(f(1, 100, False), 4000)
        self.assertEqual(f(1, 101, False), 4800)
        self.assertEqual(f(30000, 1, False), 45500)
        self.assertEqual(f(20000, 1, True), 45750)  # 30500*1.5
        with self.assertRaises(ValueError):
            f(20001, 1, True)


class NoDrift(unittest.TestCase):
    def test_rounding(self):
        self.assertEqual(f(5003, 1, False), 8005)   # 8004.5
        self.assertEqual(f(5001, 101, False), 9602)  # 9601.8
        self.assertEqual(f(5001, 1, True), 12002)  # 12002.25


class Reject(unittest.TestCase):
    def test_bad(self):
        for args in [(0, 1, False), (30001, 1, False), (-1, 1, False), (1.0, 1, False),
                     ("1", 1, False), (None, 1, False), (True, 1, False),
                     (100, -1, False), (100, 1.0, False), (100, "1", False), (100, True, False),
                     (100, None, False), (100, 0, 1), (100, 1, "yes"), (100, 0, None)]:
            with self.assertRaises(ValueError, msg=str(args)):
                f(*args)


if __name__ == "__main__":
    unittest.main()
