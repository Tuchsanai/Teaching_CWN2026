import unittest
from solve import shipping_fee as f


class T(unittest.TestCase):
    def test_tiers(self):
        self.assertEqual(f(1000, 0, False), 4000)
        self.assertEqual(f(1001, 0, False), 8000)
        self.assertEqual(f(5000, 0, False), 8000)
        self.assertEqual(f(6000, 0, False), 9500)
        self.assertEqual(f(30000, 0, False), 8000 + 37500)

    def test_modifiers(self):
        self.assertEqual(f(500, 100, False), 4000)
        self.assertEqual(f(500, 101, False), 4800)
        self.assertEqual(f(500, 101, True), 7200)
        self.assertEqual(f(500, 0, True), 6000)

    def test_half_up(self):
        # 5001 g: 8001.5 satang -> 8002
        self.assertEqual(f(5001, 0, False), 8002)
        # 5001 g express: 12002.25 -> 12002
        self.assertEqual(f(5001, 0, True), 12002)
        # 5003 g: 8004.5 -> 8005
        self.assertEqual(f(5003, 0, False), 8005)

    def test_invalid(self):
        for a in [(0, 0, False), (30001, 0, False), (-1, 0, False), (100, -1, False),
                  (100.0, 0, False), (True, 0, False), (100, 0.0, False),
                  (100, 0, 1), (100, 0, None), ("5", 0, False)]:
            with self.assertRaises(ValueError):
                f(*a)


if __name__ == "__main__":
    unittest.main()
