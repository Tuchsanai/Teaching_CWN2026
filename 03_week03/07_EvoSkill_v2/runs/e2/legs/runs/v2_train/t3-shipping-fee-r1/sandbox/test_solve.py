import unittest
from solve import shipping_fee as f


class Normal(unittest.TestCase):
    def test_a(self):
        self.assertEqual(f(500, 10, False), 4000)
        self.assertEqual(f(3000, 10, False), 8000)
        self.assertEqual(f(10000, 10, False), 15500)
        self.assertEqual(f(10000, 101, True), 27900)


class Boundary(unittest.TestCase):
    def test_a(self):
        self.assertEqual(f(1000, 1, False), 4000)
        self.assertEqual(f(1001, 1, False), 8000)
        self.assertEqual(f(5000, 100, False), 8000)
        self.assertEqual(f(20000, 1, True), 45750)
        self.assertEqual(f(30000, 1, False), 45500)
        self.assertEqual(f(500, 0, True), 0)


class NoDrift(unittest.TestCase):
    def test_a(self):
        # 5001g: 8000+1.5=8001.5 satang; *1.2=9601.8 -> 9602; *1.5=14402.7 -> 14403
        self.assertEqual(f(5001, 101, False), 9602)
        self.assertEqual(f(5001, 101, True), 14403)
        self.assertEqual(f(5001, 1, False), 8002)  # 8001.5 half up


class Reject(unittest.TestCase):
    def test_a(self):
        for args in [(0, 1, False), (30001, 1, False), (1000.0, 1, False),
                     ("1000", 1, False), (True, 1, False), (None, 1, False),
                     (500, -1, False), (500, 10.5, False), (500, 1.0, False),
                     (500, 1, 1), (500, 1, None), (20001, 1, True),
                     (0, 0, False)]:
            with self.assertRaises(ValueError, msg=str(args)):
                f(*args)


if __name__ == "__main__":
    unittest.main()
