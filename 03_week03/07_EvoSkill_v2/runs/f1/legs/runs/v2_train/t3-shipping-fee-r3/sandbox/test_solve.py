import unittest

from solve import shipping_fee as fn


class Normal(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(fn(500, 10, False), 4000)
        self.assertEqual(fn(3000, 10, False), 8000)
        self.assertEqual(fn(10000, 10, False), 15500)
        self.assertEqual(fn(10000, 200, True), 27900)


class Boundary(unittest.TestCase):
    def test_weight(self):
        self.assertEqual(fn(1000, 0, False), 4000)
        self.assertEqual(fn(1001, 0, False), 8000)
        self.assertEqual(fn(5000, 0, False), 8000)
        self.assertEqual(fn(1, 0, False), 4000)
        self.assertEqual(fn(30000, 0, False), 45500)

    def test_distance(self):
        self.assertEqual(fn(500, 100, False), 4000)
        self.assertEqual(fn(500, 101, False), 4800)


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        # 8000 + 1.5 = 8001.5 -> 8002
        self.assertEqual(fn(5001, 0, False), 8002)
        # 8001.5*1.2 = 9601.8 -> 9602
        self.assertEqual(fn(5001, 101, False), 9602)
        # 8001.5*1.5 = 12002.25 -> 12002
        self.assertEqual(fn(5001, 0, True), 12002)
        # 8003*1.5 = 12004.5 -> 12005
        self.assertEqual(fn(5002, 0, True), 12005)


class Reject(unittest.TestCase):
    def test_bad(self):
        for args in [(0, 1, False), (30001, 1, False), (-1, 1, False),
                     (1.0, 1, False), ("5", 1, False), (5, -1, False),
                     (5, 1.0, False), (5, 1, 1), (True, 1, False),
                     (5, 1, "yes")]:
            with self.assertRaises(ValueError):
                fn(*args)


if __name__ == "__main__":
    unittest.main()
