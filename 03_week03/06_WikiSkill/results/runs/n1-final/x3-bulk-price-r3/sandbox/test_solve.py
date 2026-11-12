import unittest
from solve import bulk_price


class TestBulkPrice(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(bulk_price(100, 1, False), 107)
        self.assertEqual(bulk_price(100, 5, False), 535)

    def test_boundary_below(self):
        self.assertEqual(bulk_price(1000, 9, False), 9630)
        self.assertEqual(bulk_price(1000, 49, False), 50595)

    def test_boundary_at(self):
        self.assertEqual(bulk_price(1000, 10, False), 10326)  # 10325.5 -> up
        self.assertEqual(bulk_price(1000, 50, False), 49488)  # 49487.5 -> up
        self.assertEqual(bulk_price(1000, 51, False), 50477)

    def test_half_up(self):
        self.assertEqual(bulk_price(50, 1, False), 54)    # 53.5
        self.assertEqual(bulk_price(150, 1, False), 161)  # 160.5
        self.assertEqual(bulk_price(40, 50, False), 1980)  # 1979.5

    def test_combined(self):
        self.assertEqual(bulk_price(1000, 50, True), 48250)
        self.assertEqual(bulk_price(0, 5, True), 0)

    def test_reject_range(self):
        for args in [(-1, 1, False), (100, 0, False), (100, 1001, False)]:
            with self.assertRaises(ValueError):
                bulk_price(*args)

    def test_reject_float(self):
        with self.assertRaises(ValueError):
            bulk_price(100.0, 1, False)
        with self.assertRaises(ValueError):
            bulk_price(100, 1.0, False)

    def test_reject_bool_or_type(self):
        with self.assertRaises(ValueError):
            bulk_price(True, 1, False)
        with self.assertRaises(ValueError):
            bulk_price(100, "1", False)
        with self.assertRaises(ValueError):
            bulk_price(100, 1, 1)
        with self.assertRaises(ValueError):
            bulk_price(None, 1, False)


if __name__ == "__main__":
    unittest.main()
