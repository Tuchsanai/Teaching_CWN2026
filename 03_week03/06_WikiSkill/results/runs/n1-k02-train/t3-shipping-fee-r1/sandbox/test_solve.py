import unittest
from solve import shipping_fee as f


class T(unittest.TestCase):
    def test_base(self):
        self.assertEqual(f(1, 0, False), 4000)
        self.assertEqual(f(1000, 0, False), 4000)
        self.assertEqual(f(1001, 0, False), 8000)
        self.assertEqual(f(5000, 0, False), 8000)
        self.assertEqual(f(5001, 0, False), 8002)  # 1.5 satang -> half-up
        self.assertEqual(f(10000, 0, False), 15500)
        self.assertEqual(f(30000, 0, False), 45500)

    def test_distance_express(self):
        self.assertEqual(f(500, 100, False), 4000)
        self.assertEqual(f(500, 101, False), 4800)
        self.assertEqual(f(500, 0, True), 6000)
        self.assertEqual(f(500, 150, True), 7200)

    def test_half_up(self):
        self.assertEqual(f(5001, 0, False), 8002)
        self.assertEqual(f(5003, 0, False), 8005)  # 8004.5

    def test_invalid(self):
        for a in [(0, 0, False), (30001, 0, False), (1.0, 0, False), (True, 0, False),
                  (100, -1, False), (100, None, False), (100, "5", False),
                  (100, 0, 1), (100, 0, None), (100, float("nan"), False)]:
            with self.assertRaises(ValueError):
                f(*a)


if __name__ == "__main__":
    unittest.main()
