import unittest
from solve import bulk_price as fn


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(fn(10000, 1, False), 10700)
        self.assertEqual(fn(10000, 10, False), 103255)
        self.assertEqual(fn(10000, 50, True), 482503)

    def test_boundary(self):
        self.assertEqual(fn(1000, 9, False), 9630)
        self.assertEqual(fn(1000, 10, False), 10326)  # 10325.5 half-up
        self.assertEqual(fn(0, 5, True), 0)

    def test_reject(self):
        for a in ((1.0, 1, False), (1, 0, False), (1, 1001, False), (1, 1, 1),
                  (-1, 1, False), (True, 1, False), (1, "2", False)):
            with self.assertRaises(ValueError):
                fn(*a)


if __name__ == "__main__":
    unittest.main()
