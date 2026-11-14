import unittest

from solve import refund


class Normal(unittest.TestCase):
    def test_half(self):
        self.assertEqual(refund(10000, 50, False), 5000)

    def test_restock(self):
        self.assertEqual(refund(10000, 50, True), 4375)

    def test_unused(self):
        self.assertEqual(refund(8000, 0, True), 7000)


class Boundary(unittest.TestCase):
    def test_80_refunds(self):
        self.assertEqual(refund(10000, 80, False), 2000)

    def test_81_none(self):
        self.assertEqual(refund(10000, 81, False), 0)

    def test_100_and_zero_paid(self):
        self.assertEqual(refund(10000, 100, True), 0)
        self.assertEqual(refund(0, 0, True), 0)


class NoDrift(unittest.TestCase):
    def test_floor_once(self):
        # 1001*0.5 = 500.5 -> 500
        self.assertEqual(refund(1001, 50, False), 500)
        # 500.5*0.875 = 437.9375 -> 437 (ปัดครั้งเดียว)
        self.assertEqual(refund(1001, 50, True), 437)

    def test_large(self):
        self.assertEqual(refund(10**15 + 1, 0, False), 10**15 + 1)


class Reject(unittest.TestCase):
    def test_bad(self):
        for args in [(100.0, 10, False), ("100", 10, False), (None, 10, False),
                     (True, 10, False), (-1, 10, False), (100, 10.0, False),
                     (100, -1, False), (100, 101, False), (100, 10, 1),
                     (100, 10, None), (100, True, False), (100, 90.5, True)]:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    refund(*args)

    def test_validate_before_shortcut(self):
        with self.assertRaises(ValueError):
            refund(100, 95, "yes")


if __name__ == "__main__":
    unittest.main()
