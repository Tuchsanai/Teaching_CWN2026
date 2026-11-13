import unittest
from solve import cashback as fn


class Normal(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(fn(20000, "silver", False), 300)
        self.assertEqual(fn(20000, "gold", False), 500)
        self.assertEqual(fn(20000, "platinum", True), 1600)


class Boundary(unittest.TestCase):
    def test_min(self):
        self.assertEqual(fn(9999, "platinum", True), 0)
        self.assertEqual(fn(10000, "platinum", False), 400)
        self.assertEqual(fn(10001, "gold", False), 250)
        self.assertEqual(fn(0, "gold", False), 0)

    def test_cap(self):
        self.assertEqual(fn(500000, "platinum", False), 20000)
        self.assertEqual(fn(500000, "platinum", True), 20000)
        self.assertEqual(fn(1000000, "silver", False), 15000)


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        self.assertEqual(fn(10020, "silver", True), 301)
        self.assertEqual(fn(10010, "silver", False), 150)  # 150.15
        self.assertEqual(fn(10100, "silver", False), 152)  # 151.5 -> 152


class Reject(unittest.TestCase):
    def test_bad(self):
        for a in [(-1, "gold", False), (20000.0, "gold", False), ("20000", "gold", False),
                  (True, "gold", False), (20000, "bronze", False), (20000, ["x"], False),
                  (20000, "gold", 1), (20000, "gold", None)]:
            with self.assertRaises(ValueError):
                fn(*a)


if __name__ == "__main__":
    unittest.main()
