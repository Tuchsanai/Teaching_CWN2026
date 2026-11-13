import unittest
from solve import shipping_fee as f


class Normal(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(f(500, 10, False), 4000)
        self.assertEqual(f(3000, 10, False), 8000)
        self.assertEqual(f(10000, 10, False), 8000 + 7500)
        self.assertEqual(f(3000, 200, True), 14400)  # 8000*1.2*1.5


class Boundary(unittest.TestCase):
    def test_edges(self):
        self.assertEqual(f(1000, 0, False), 4000)
        self.assertEqual(f(1001, 0, False), 8000)
        self.assertEqual(f(5000, 100, False), 8000)
        self.assertEqual(f(5001, 100.01, False), 9602)  # (8000+1.5)*1.2=9601.8
        self.assertEqual(f(30000, 0, False), 8000 + 37500)


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        self.assertEqual(f(5001, 0, False), 8002)   # 8001.5 -> 8002
        self.assertEqual(f(5003, 0, True), 12007)   # 8004.5*1.5=12006.75 -> 12007
        

class Reject(unittest.TestCase):
    def test_bad(self):
        for a in [(0, 1, False), (30001, 1, False), (-1, 1, False), (1.0, 1, False),
                  ("5", 1, False), (True, 1, False), (5, -1, False), (5, "1", False),
                  (5, None, False), (5, True, False), (5, 1, 1), (5, 1, None)]:
            with self.assertRaises(ValueError):
                f(*a)


if __name__ == "__main__":
    unittest.main()
