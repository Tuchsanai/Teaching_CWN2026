"""python3 -m unittest -q test_solve"""
import unittest

from solve import shipping_fee as f


class Normal(unittest.TestCase):
    def test_tiers(self):
        self.assertEqual(f(500, 10, False), 4000)
        self.assertEqual(f(3000, 10, False), 8000)
        self.assertEqual(f(6000, 50, False), 9500)

    def test_combo(self):
        self.assertEqual(f(6000, 150, True), 17100)
        self.assertEqual(f(500, 10, True), 6000)


class Boundary(unittest.TestCase):
    def test_weight_lines(self):
        self.assertEqual(f(1000, 1, False), 4000)
        self.assertEqual(f(1001, 1, False), 8000)
        self.assertEqual(f(5000, 1, False), 8000)
        self.assertEqual(f(5001, 1, False), 8002)  # 8001.5 -> half-up

    def test_distance_lines(self):
        self.assertEqual(f(500, 100, False), 4000)
        self.assertEqual(f(500, 101, False), 4800)

    def test_pickup(self):
        self.assertEqual(f(500, 0, False), 0)
        self.assertEqual(f(500, 0, True), 0)

    def test_express_limit(self):
        self.assertEqual(f(20000, 1, True), 45750)  # (8000+22500)*1.5=45750
        with self.assertRaises(ValueError):
            f(20001, 1, True)
        self.assertEqual(f(30000, 1, False), 8000 + 37500)


class NoDrift(unittest.TestCase):
    def test_rounding(self):
        self.assertEqual(f(5001, 101, False), 9602)  # 9601.8
        self.assertEqual(f(5003, 1, True), 12007)  # 8004.5*1.5=12006.75

    def test_single_round(self):
        # 8001.5*1.2*1.5 = 14402.7 -> 14403
        self.assertEqual(f(5001, 101, True), 14403)


class Reject(unittest.TestCase):
    def test_bad(self):
        bad = [(0, 1, False), (30001, 1, False), (-1, 1, False), (1.0, 1, False),
               ('1', 1, False), (True, 1, False), (None, 1, False),
               (500, -1, False), (500, 1.0, False), (500, '1', False),
               (500, True, False), (500, None, False),
               (500, 1, 1), (500, 1, 0), (500, 1, 'yes'), (500, 1, None),
               (500, 0, 1)]
        for a in bad:
            with self.assertRaises(ValueError, msg=str(a)):
                f(*a)


if __name__ == "__main__":
    unittest.main()
