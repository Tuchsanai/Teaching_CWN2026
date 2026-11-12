import unittest
from solve import bulk_price


class TestBulkPrice(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(bulk_price(10000, 1, False), 10700)

    def test_boundary_below(self):
        self.assertEqual(bulk_price(10000, 9, False), 96300)
        self.assertEqual(bulk_price(10000, 49, False), 505950)

    def test_boundary_at(self):
        self.assertEqual(bulk_price(10000, 10, False), 103255)
        self.assertEqual(bulk_price(10000, 50, False), 494875)

    def test_half_up(self):
        self.assertEqual(bulk_price(50, 1, False), 54)
        self.assertEqual(bulk_price(10000, 50, True), 482503)

    def test_combined(self):
        self.assertEqual(bulk_price(0, 5, True), 0)
        self.assertEqual(bulk_price(10000, 10, True), 100674)

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
        for args in [(True, 1, False), (100, True, False), (100, 1, 1),
                     ("100", 1, False), (100, None, False), (100, 1, None)]:
            with self.assertRaises(ValueError):
                bulk_price(*args)


if __name__ == "__main__":
    unittest.main()
