import unittest
from solve import refund


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(refund(10000, 50, False), 5000)
        self.assertEqual(refund(10000, 50, True), 4375)

    def test_boundary_exact(self):
        self.assertEqual(refund(10000, 80, False), 2000)

    def test_boundary_below(self):
        self.assertEqual(refund(10000, 79, False), 2100)

    def test_boundary_above(self):
        self.assertEqual(refund(10000, 81, False), 0)
        self.assertEqual(refund(10000, 100, True), 0)

    def test_half_up(self):
        # 1*99/100 = 0.99 -> 1 ; 50*99/100=49.5 -> 50
        self.assertEqual(refund(50, 1, False), 50)
        # 4*50/100 = 2.0; 1*50/100 = 0.5 -> 1
        self.assertEqual(refund(1, 50, False), 1)
        # 4*0.875 = 3.5 -> 4
        self.assertEqual(refund(4, 0, True), 4)

    def test_reject_value(self):
        for args in [(-1, 10, False), (100, -1, False), (100, 101, True)]:
            with self.assertRaises(ValueError):
                refund(*args)

    def test_reject_type(self):
        for args in [(1000.0, 10, False), (True, 10, False), ("1", 10, False),
                     (100, None, False), (100, 10, 1), (100, 10.0, True)]:
            with self.assertRaises(ValueError):
                refund(*args)

    def test_zero_or_cap(self):
        self.assertEqual(refund(0, 0, True), 0)
        self.assertEqual(refund(10000, 0, False), 10000)


if __name__ == "__main__":
    unittest.main()
