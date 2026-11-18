import unittest
from solve import bulk_price as fn


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(fn(10000, 1, False), 10700)
        self.assertEqual(fn(10000, 10, False), 103255)

    def test_boundary(self):
        self.assertEqual(fn(1000, 9, False), 9630)
        self.assertEqual(fn(1000, 10, False), 10326)
        self.assertEqual(fn(1000, 49, False), 50595)
        self.assertEqual(fn(1000, 50, False), 49488)
        self.assertEqual(fn(0, 5, True), 0)

    def test_reject(self):
        for a in [(1.0, 1, False), (-1, 1, False), (1, 0, False), (1, 1001, False),
                  (1, 1.0, False), (1, 1, 1), (True, 1, False), (None, 1, False), ("1", 1, False)]:
            with self.assertRaises(ValueError):
                fn(*a)


if __name__ == "__main__":
    unittest.main()
