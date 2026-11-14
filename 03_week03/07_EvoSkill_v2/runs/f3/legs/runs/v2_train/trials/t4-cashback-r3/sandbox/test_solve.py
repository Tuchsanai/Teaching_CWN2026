import unittest
from solve import cashback


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cashback(20000, "silver", False), 300)
        self.assertEqual(cashback(20000, "platinum", True), 1600)
        self.assertEqual(cashback(20000, "silver", True), 300)

    def test_boundary(self):
        self.assertEqual(cashback(9999, "gold", False), 0)
        self.assertEqual(cashback(10000, "gold", False), 250)
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(0, "gold", True), 0)

    def test_nodrift(self):
        self.assertEqual(cashback(10015, "platinum", True), 801)
        self.assertEqual(cashback(10020, "gold", True), 501)

    def test_reject(self):
        for a in [(-1, "gold", False), (1.0, "gold", False), ("1", "gold", False),
                  (True, "gold", False), (10000, "bronze", False), (10000, ["x"], False),
                  (10000, "gold", 1), (0, "x", False)]:
            with self.assertRaises(ValueError):
                cashback(*a)


if __name__ == "__main__":
    unittest.main()
