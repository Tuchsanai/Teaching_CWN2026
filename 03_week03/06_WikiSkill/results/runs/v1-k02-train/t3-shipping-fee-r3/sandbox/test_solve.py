import unittest
from solve import shipping_fee


class T(unittest.TestCase):
    def test_tiers(self):
        self.assertEqual(shipping_fee(1000, 0, False), 4000)
        self.assertEqual(shipping_fee(1001, 0, False), 8000)
        self.assertEqual(shipping_fee(5000, 0, False), 8000)
        self.assertEqual(shipping_fee(6000, 0, False), 9500)
        self.assertEqual(shipping_fee(5001, 0, False), 8002)  # 1.5 satang -> 2
        self.assertEqual(shipping_fee(30000, 0, False), 45500)

    def test_modifiers(self):
        self.assertEqual(shipping_fee(500, 100, False), 4000)
        self.assertEqual(shipping_fee(500, 101, False), 4800)
        self.assertEqual(shipping_fee(500, 0, True), 6000)
        self.assertEqual(shipping_fee(500, 101, True), 7200)

    def test_invalid(self):
        for a in [(0, 0, False), (30001, 0, False), (-1, 0, False), (100, -1, False),
                  (100.0, 0, False), (100, 1.0, False), (True, 0, False),
                  (100, 0, 1), (100, 0, None), ("5", 0, False)]:
            with self.assertRaises(ValueError):
                shipping_fee(*a)


if __name__ == "__main__":
    unittest.main()
