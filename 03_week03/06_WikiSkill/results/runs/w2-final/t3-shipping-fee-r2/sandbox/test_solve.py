import unittest
from solve import shipping_fee


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(shipping_fee(500, 10, False), 4000)
        self.assertEqual(shipping_fee(3000, 10, False), 8000)

    def test_boundary_exact(self):
        self.assertEqual(shipping_fee(1000, 0, False), 4000)
        self.assertEqual(shipping_fee(5000, 100, False), 8000)

    def test_boundary_below(self):
        self.assertEqual(shipping_fee(1, 99, False), 4000)

    def test_boundary_above(self):
        self.assertEqual(shipping_fee(1001, 0, False), 8000)
        self.assertEqual(shipping_fee(5001, 0, False), 8002)  # 8000+1.5
        self.assertEqual(shipping_fee(6000, 101, False), 11400)  # 9500*1.2

    def test_half_up(self):
        self.assertEqual(shipping_fee(5001, 0, False), 8002)  # 8001.5 -> 8002
        self.assertEqual(shipping_fee(5003, 0, False), 8005)  # 8004.5 -> 8005

    def test_express_and_distance(self):
        self.assertEqual(shipping_fee(500, 101, True), 7200)  # 4000*1.2*1.5
        self.assertEqual(shipping_fee(500, 0, True), 6000)

    def test_reject_value(self):
        for a in [(0, 1, False), (30001, 1, False), (100, -1, False)]:
            with self.assertRaises(ValueError):
                shipping_fee(*a)

    def test_reject_type(self):
        for a in [(1000.0, 1, False), (True, 1, False), ("5", 1, False),
                  (100, None, False), (100, 1, 1), (100, 1, None)]:
            with self.assertRaises(ValueError):
                shipping_fee(*a)

    def test_zero_or_cap(self):
        self.assertEqual(shipping_fee(30000, 0, False), 8000 + 25000 * 150 // 100)
        self.assertEqual(shipping_fee(1, 0, False), 4000)


if __name__ == "__main__":
    unittest.main()
