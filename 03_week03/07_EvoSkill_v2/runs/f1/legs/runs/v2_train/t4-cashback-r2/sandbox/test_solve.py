import unittest
from solve import cashback as fn


class Normal(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(fn(20000, "silver", False), 300)
        self.assertEqual(fn(20000, "gold", False), 500)
        self.assertEqual(fn(20000, "platinum", False), 800)
        self.assertEqual(fn(20000, "gold", True), 1000)
        self.assertEqual(fn(0, "gold", True), 0)


class Boundary(unittest.TestCase):
    def test_min(self):
        self.assertEqual(fn(9999, "platinum", True), 0)
        self.assertEqual(fn(10000, "platinum", False), 400)
        self.assertEqual(fn(10001, "platinum", False), 400)

    def test_cap(self):
        self.assertEqual(fn(500000, "platinum", False), 20000)
        self.assertEqual(fn(500001, "platinum", False), 20000)
        self.assertEqual(fn(499999, "platinum", False), 19999.96 and 20000)
        self.assertEqual(fn(1000000, "platinum", True), 20000)


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        self.assertEqual(fn(10020, "silver", True), 301)
        self.assertEqual(fn(10010, "silver", False), 150)  # 150.15
        self.assertEqual(fn(10030, "silver", False), 150)  # 150.45
        self.assertEqual(fn(10100, "gold", False), 253)    # 252.5 -> 253


class Reject(unittest.TestCase):
    def test_bad(self):
        for args in [(-1, "gold", False), (1000.0, "gold", False), ("1000", "gold", False),
                     (True, "gold", False), (10000, "bronze", False), (10000, ["gold"], False),
                     (10000, "gold", 1), (10000, "gold", "yes")]:
            with self.assertRaises(ValueError):
                fn(*args)


if __name__ == "__main__":
    unittest.main()
