import unittest
from solve import shipping_fee as f


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(f(500, 10, False), 4000)
        self.assertEqual(f(3000, 10, False), 8000)
        self.assertEqual(f(10000, 10, False), 8000 + 7500)
        self.assertEqual(f(3000, 150, True), 14400)

    def test_boundary(self):
        self.assertEqual(f(1000, 1, False), 4000)
        self.assertEqual(f(1001, 1, False), 8000)
        self.assertEqual(f(5000, 1, False), 8000)
        self.assertEqual(f(5001, 1, False), 8002)  # 1.5 -> 2 half-up
        self.assertEqual(f(100, 100, False), 4000)
        self.assertEqual(f(100, 101, False), 4800)
        self.assertEqual(f(20000, 1, True), int((8000 + 22500) * 1.5))
        self.assertEqual(f(30000, 1, False), 8000 + 37500)

    def test_pickup(self):
        self.assertEqual(f(500, 0, True), 0)

    def test_rounding(self):
        # 8000+1.5=8001.5 *1.5 = 12002.25 -> 12002
        self.assertEqual(f(5001, 1, True), 12002)
        # 8003*... w=5003 -> 8004.5 -> half-up 8005
        self.assertEqual(f(5003, 1, False), 8005)

    def test_reject(self):
        for args in [(0, 1, False), (30001, 1, False), (20001, 1, True),
                     (1.0, 1, False), ("3", 1, False), (True, 1, False),
                     (None, 1, False), (100, -1, False), (100, "5", False),
                     (100, None, False), (100, True, False), (100, 1, 1),
                     (100, 1, None), (100, float("nan"), False),
                     (500, 0, "x"), (0, 0, False)]:
            with self.assertRaises(ValueError, msg=str(args)):
                f(*args)


if __name__ == "__main__":
    unittest.main()
