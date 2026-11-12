import unittest
from solve import shipping_fee as f


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(f(500, 10, False), 4000)
        self.assertEqual(f(3000, 10, False), 8000)

    def test_boundary_below(self):
        self.assertEqual(f(999, 100, False), 4000)
        self.assertEqual(f(4999, 100, False), 8000)

    def test_boundary_at(self):
        self.assertEqual(f(1000, 0, False), 4000)
        self.assertEqual(f(1001, 0, False), 8000)
        self.assertEqual(f(5000, 0, False), 8000)
        self.assertEqual(f(5001, 0, False), 8000 + 2)  # 1.5 satang -> 2
        self.assertEqual(f(1, 100.01, False), 4800)

    def test_half_up(self):
        self.assertEqual(f(5001, 0, False), 8002)
        self.assertEqual(f(5003, 0, False), 8005)  # 4.5 -> 5

    def test_over_5000(self):
        self.assertEqual(f(30000, 0, False), 8000 + 37500)

    def test_combined(self):
        self.assertEqual(f(500, 101, True), 7200)
        self.assertEqual(f(30000, 200, True), 81900)

    def test_reject_range(self):
        for a in [(0, 1, False), (30001, 1, False), (5, -1, False)]:
            with self.assertRaises(ValueError):
                f(*a)

    def test_reject_float(self):
        with self.assertRaises(ValueError):
            f(500.0, 1, False)
        with self.assertRaises(ValueError):
            f(500, float("nan"), False)

    def test_reject_bool_or_type(self):
        for a in [(True, 1, False), ("5", 1, False), (5, None, False),
                  (5, 1, 1), (5, True, False), (5, 1, None)]:
            with self.assertRaises(ValueError):
                f(*a)


if __name__ == "__main__":
    unittest.main()
