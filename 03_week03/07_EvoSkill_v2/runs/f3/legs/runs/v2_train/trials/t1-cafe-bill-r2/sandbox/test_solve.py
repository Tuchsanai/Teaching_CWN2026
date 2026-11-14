import unittest
from solve import cafe_bill


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cafe_bill([{"price": 4500, "qty": 2}], False), 9630)
        self.assertEqual(cafe_bill([{"price": 4500, "qty": 2}], True), 8667)

    def test_boundary(self):
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], False), 50825)
        self.assertEqual(cafe_bill([{"price": 49999, "qty": 1}], False), 53499)

    def test_empty(self):
        self.assertEqual(cafe_bill([], False), 0)

    def test_reject(self):
        for bad in ([{"price": 1.0, "qty": 1}], [{"price": 1, "qty": 0}],
                    [{"price": -1, "qty": 1}], [{"price": True, "qty": 1}],
                    [{"price": 1}], [5], "x"):
            with self.assertRaises(ValueError):
                cafe_bill(bad, False)
        with self.assertRaises(ValueError):
            cafe_bill([], 1)


if __name__ == "__main__":
    unittest.main()
