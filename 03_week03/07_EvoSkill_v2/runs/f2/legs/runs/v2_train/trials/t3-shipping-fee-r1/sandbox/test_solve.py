import unittest
from solve import shipping_fee as f


class Normal(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(f(500, 10, False), 4000)
        self.assertEqual(f(3000, 10, False), 8000)
        self.assertEqual(f(10000, 10, False), 15500)
        self.assertEqual(f(500, 150, True), 7200)


class Boundary(unittest.TestCase):
    def test_edges(self):
        self.assertEqual(f(1000, 100, False), 4000)
        self.assertEqual(f(1001, 101, False), 9600)
        self.assertEqual(f(5000, 1, False), 8000)
        self.assertEqual(f(5001, 1, False), 8002)
        self.assertEqual(f(30000, 1, False), 8000 + 37500)
        self.assertEqual(f(20000, 1, True), int((8000 + 22500) * 1.5))
        self.assertEqual(f(500, 0, True), 0)


class NoDrift(unittest.TestCase):
    def test_half(self):
        self.assertEqual(f(5001, 1, False), 8002)  # 8001.5 -> 8002
        self.assertEqual(f(5003, 1, True), 12007)  # 12006.75 -> 12007

    def test_exact(self):
        self.assertEqual(f(5001, 101, False), 9602)  # 9601.8


class Reject(unittest.TestCase):
    def test_bad(self):
        for a in [(0, 1, False), (30001, 1, False), (1.0, 1, False), (True, 1, False),
                  (10, -1, False), (10, 1.5, False), (10, 1, 1), (10, 1, None),
                  ("5", 1, False), (20001, 1, True)]:
            with self.assertRaises(ValueError):
                f(*a)


if __name__ == "__main__":
    unittest.main()
