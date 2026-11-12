import unittest
from solve import shipping_fee as f


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(f(500, 10, False), 4000)
        self.assertEqual(f(3000, 10, False), 8000)
        self.assertEqual(f(10000, 10, False), 15500)

    def test_edges(self):
        self.assertEqual(f(1000, 0, False), 4000)
        self.assertEqual(f(1001, 0, False), 8000)
        self.assertEqual(f(5000, 0, False), 8000)
        self.assertEqual(f(5001, 0, False), 8002)
        self.assertEqual(f(1, 100, False), 4000)
        self.assertEqual(f(1, 101, False), 4800)

    def test_multipliers(self):
        self.assertEqual(f(500, 10, True), 6000)
        self.assertEqual(f(500, 200, True), 7200)

    def test_half_up(self):
        # 80.025*1.5 = 120.0375 -> 12004 ; 5003g: 80.045 -> 8005 (half up)
        self.assertEqual(f(5003, 0, False), 8005)
        self.assertEqual(f(5001, 0, True), 12002)

    def test_invalid(self):
        for args in [(0, 1, False), (30001, 1, False), (-5, 1, False),
                     (10.0, 1, False), (True, 1, False), ("5", 1, False),
                     (10, -1, False), (10, 1, 1), (10, 1, None),
                     (10, True, False), (None, 1, False)]:
            with self.assertRaises(ValueError):
                f(*args)


if __name__ == "__main__":
    unittest.main()
