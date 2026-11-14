import unittest
from solve import shipping_fee as f


class Normal(unittest.TestCase):
    def test_a(self): self.assertEqual(f(500, 10, False), 4000)
    def test_b(self): self.assertEqual(f(3000, 10, False), 8000)
    def test_c(self): self.assertEqual(f(10000, 10, False), 15500)
    def test_d(self): self.assertEqual(f(10000, 150, True), 27900)


class Boundary(unittest.TestCase):
    def test_w(self):
        self.assertEqual(f(1000, 1, False), 4000)
        self.assertEqual(f(1001, 1, False), 8000)
        self.assertEqual(f(5000, 1, False), 8000)
        self.assertEqual(f(5001, 1, False), 8002)  # 80.015 -> 8001.5 -> 8002
    def test_d(self):
        self.assertEqual(f(500, 100, False), 4000)
        self.assertEqual(f(500, 101, False), 4800)
        self.assertEqual(f(500, 0, True), 0)
    def test_express_cap(self):
        self.assertEqual(f(20000, 1, True), 45750)
        self.assertEqual(f(30000, 1, False), 45500)


class NoDrift(unittest.TestCase):
    def test_a(self): self.assertEqual(f(5001, 101, True), 14403)  # 80.015*1.8=144.027
    def test_b(self): self.assertEqual(f(5333, 1, False), 8500)  # 84.995 -> 8499.5 -> 8500


class Reject(unittest.TestCase):
    def test_bad(self):
        for a in [(0, 1, False), (30001, 1, False), (1000.0, 1, False), ("1000", 1, False),
                  (True, 1, False), (None, 1, False), (500, -1, False), (500, 10.5, False),
                  (500, 1, 1), (500, 1, None), (20001, 1, True), (20001, 0, True)]:
            with self.assertRaises(ValueError):
                f(*a)


if __name__ == "__main__":
    unittest.main()
