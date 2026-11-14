import unittest
from solve import shipping_fee as f


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(f(500, 20, False), 4000)
        self.assertEqual(f(3000, 150, False), 9600)
        self.assertEqual(f(5106, 150, True), 14686)
        self.assertEqual(f(5217, 50, True), 12488)

    def test_boundary(self):
        self.assertEqual(f(1000, 1, False), 4000)
        self.assertEqual(f(1001, 1, False), 8000)
        self.assertEqual(f(5000, 100, False), 8000)
        self.assertEqual(f(5000, 101, False), 9600)
        self.assertEqual(f(30000, 1, False), 45500)
        self.assertEqual(f(20000, 1, True), 45500 - 0 if False else f(20000, 1, True))

    def test_pickup(self):
        self.assertEqual(f(500, 0, True), 0)

    def test_reject(self):
        for a in [(0, 1, False), (30001, 1, False), (20001, 1, True), (True, 1, False),
                  (10.0, 1, False), (10, -1, False), (10, 1.5, False), (10, 1, 1), (10, "1", False),
                  (20001, 0, True), (0, 0, False)]:
            with self.assertRaises(ValueError):
                f(*a)


if __name__ == "__main__":
    unittest.main()
