import unittest

from solve import shipping_fee as fn


class Normal(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(fn(500, 10, False), 4000)
        self.assertEqual(fn(3000, 10, True), 12000)
        self.assertEqual(fn(10000, 200, False), 18600)

    def test_far_express(self):
        self.assertEqual(fn(10000, 200, True), 27900)


class Boundary(unittest.TestCase):
    def test_weight(self):
        self.assertEqual(fn(1, 0, False), 4000)
        self.assertEqual(fn(1000, 0, False), 4000)
        self.assertEqual(fn(1001, 0, False), 8000)
        self.assertEqual(fn(5000, 0, False), 8000)
        self.assertEqual(fn(5001, 0, False), 8002)
        self.assertEqual(fn(30000, 0, False), 45500)

    def test_distance(self):
        self.assertEqual(fn(500, 100, False), 4000)
        self.assertEqual(fn(500, 101, False), 4800)


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        # 80.15*1.5 = 120.225 baht -> 12022.5 satang -> 12023
        self.assertEqual(fn(5010, 0, True), 12023)
        self.assertEqual(fn(5001, 101, True), 14403)  # 80.015*1.8=144.027 -> 14402.7


class Reject(unittest.TestCase):
    def test_bad(self):
        for args in [(0, 1, False), (30001, 1, False), (100, -1, False),
                     (100.0, 1, False), ("100", 1, False), (True, 1, False),
                     (100, 1.0, False), (100, "1", False), (100, 1, 1),
                     (100, 1, "yes"), (100, True, False)]:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    fn(*args)


if __name__ == "__main__":
    unittest.main()
