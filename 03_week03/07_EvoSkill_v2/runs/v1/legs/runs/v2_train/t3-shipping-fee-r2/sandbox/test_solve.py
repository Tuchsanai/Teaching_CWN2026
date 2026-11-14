import unittest
from solve import shipping_fee as f


class Normal(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(f(500, 10, False), 4000)
        self.assertEqual(f(3000, 10, False), 8000)
        self.assertEqual(f(10000, 10, False), 8000 + 7500)
        self.assertEqual(f(1000, 150, True), 7200)


class Boundary(unittest.TestCase):
    def test_weight(self):
        self.assertEqual(f(1000, 1, False), 4000)
        self.assertEqual(f(1001, 1, False), 8000)
        self.assertEqual(f(5000, 1, False), 8000)
        self.assertEqual(f(5001, 1, False), 8002)  # 1.5 satang -> 2
        self.assertEqual(f(30000, 1, False), 8000 + 37500)

    def test_distance(self):
        self.assertEqual(f(500, 100, False), 4000)
        self.assertEqual(f(500, 101, False), 4800)
        self.assertEqual(f(500, 0, False), 0)

    def test_express_cap(self):
        self.assertEqual(f(20000, 1, True), (8000 + 22500) * 3 // 2)
        with self.assertRaises(ValueError):
            f(20001, 1, True)


class NoDrift(unittest.TestCase):
    def test_half(self):
        # 8000+1.5=8001.5 -> 8002 ; *1.2=9601.8 -> 9602
        self.assertEqual(f(5001, 101, False), 9602)
        # 8001.5*1.5 = 12002.25 -> 12002
        self.assertEqual(f(5001, 1, True), 12002)


class Reject(unittest.TestCase):
    def test_bad(self):
        for a in [(0, 1, False), (30001, 1, False), (-1, 1, False),
                  (1000.0, 1, False), ("1000", 1, False), (True, 1, False),
                  (None, 1, False), (500, -1, False), (500, 1.0, False),
                  (500, float("nan"), False), (500, "1", False),
                  (500, True, False), (500, 1, 1), (500, 1, "yes"),
                  (500, 1, None)]:
            with self.assertRaises(ValueError, msg=str(a)):
                f(*a)


if __name__ == "__main__":
    unittest.main()
