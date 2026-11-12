import unittest
from solve import shipping_fee as f


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(f(3000, 10, False), 8000)

    def test_boundary_below(self):
        self.assertEqual(f(999, 100, False), 4000)
        self.assertEqual(f(4999, 100, False), 8000)

    def test_boundary_at(self):
        self.assertEqual(f(1000, 100, False), 4000)
        self.assertEqual(f(1001, 100, False), 8000)
        self.assertEqual(f(5000, 100, False), 8000)
        self.assertEqual(f(5001, 100.5, False), 9600 + 2)  # 8001.5*1.2=9601.8

    def test_half_up(self):
        # 8001 satang... 5001g -> 8001.5 -> half-up 8002
        self.assertEqual(f(5001, 0, False), 8002)
        # 5003g: 8004.5 -> 8005
        self.assertEqual(f(5003, 0, False), 8005)

    def test_combined(self):
        self.assertEqual(f(10000, 150, True), int((8000 + 7500) * 1.2 * 1.5))
        self.assertEqual(f(500, 101, True), 7200)

    def test_reject_range(self):
        for a in [(0, 1, False), (30001, 1, False), (100, -1, False)]:
            with self.assertRaises(ValueError):
                f(*a)

    def test_reject_float(self):
        with self.assertRaises(ValueError):
            f(1000.0, 1, False)
        with self.assertRaises(ValueError):
            f(1000, float("nan"), False)

    def test_reject_bool_or_type(self):
        for a in [(True, 1, False), ("100", 1, False), (100, None, False),
                  (100, 1, 1), (100, True, False)]:
            with self.assertRaises(ValueError):
                f(*a)


if __name__ == "__main__":
    unittest.main()
