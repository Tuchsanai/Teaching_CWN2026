import unittest
from solve import shipping_fee as f


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(f(500, 10, False), 4000)
        self.assertEqual(f(3000, 10, False), 8000)

    def test_boundary_exact(self):
        self.assertEqual(f(1000, 0, False), 4000)
        self.assertEqual(f(5000, 100, False), 8000)

    def test_boundary_below(self):
        self.assertEqual(f(999, 99, False), 4000)
        self.assertEqual(f(1, 0, False), 4000)

    def test_boundary_above(self):
        self.assertEqual(f(1001, 0, False), 8000)
        self.assertEqual(f(5000, 101, False), 9600)
        self.assertEqual(f(6000, 0, False), 9500)

    def test_half_up(self):
        # 5001 g: 8000+1.5 = 8001.5 -> 8002
        self.assertEqual(f(5001, 0, False), 8002)
        # 5001 g express: 8001.5*1.5 = 12002.25 -> 12002
        self.assertEqual(f(5001, 0, True), 12002)
        # 5003 g: 8004.5 -> 8005
        self.assertEqual(f(5003, 0, False), 8005)

    def test_reject_value(self):
        for args in [(0, 1, False), (30001, 1, False), (100, -1, False), (-5, 0, True)]:
            with self.assertRaises(ValueError):
                f(*args)

    def test_reject_type(self):
        for args in [(1000.0, 1, False), (True, 1, False), ("5", 1, False),
                     (None, 1, False), (100, 1.5, False), (100, 1, 1), (100, 1, None)]:
            with self.assertRaises(ValueError):
                f(*args)

    def test_zero_or_cap(self):
        self.assertEqual(f(1, 0, True), 6000)
        self.assertEqual(f(30000, 0, False), 8000 + 37500)
        self.assertEqual(f(30000, 200, True), 45500 * 6 * 3 // 10)


if __name__ == "__main__":
    unittest.main()
