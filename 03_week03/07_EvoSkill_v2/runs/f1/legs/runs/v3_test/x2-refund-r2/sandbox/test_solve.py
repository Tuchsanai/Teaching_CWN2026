import unittest
from solve import refund as fn


class Normal(unittest.TestCase):
    def test_half_course(self):
        self.assertEqual(fn(10000, 50, False), 5000)

    def test_half_course_restock(self):
        self.assertEqual(fn(10000, 50, True), 4375)

    def test_unused(self):
        self.assertEqual(fn(1001, 0, False), 1001)

    def test_over_80_zero(self):
        self.assertEqual(fn(10000, 95, True), 0)

    def test_zero_paid(self):
        self.assertEqual(fn(0, 10, True), 0)


class Boundary(unittest.TestCase):
    def test_80(self):
        self.assertEqual(fn(10000, 80, False), 2000)

    def test_81(self):
        self.assertEqual(fn(10000, 81, False), 0)

    def test_79(self):
        self.assertEqual(fn(10000, 79, False), 2100)

    def test_100_and_0(self):
        self.assertEqual(fn(500, 100, False), 0)
        self.assertEqual(fn(500, 0, False), 500)


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        self.assertEqual(fn(1, 50, False), 1)   # 0.5
        self.assertEqual(fn(4, 0, True), 4)     # 3.5

    def test_round_down(self):
        self.assertEqual(fn(1, 50, True), 0)    # 0.4375
        self.assertEqual(fn(1001, 0, True), 876)  # 875.875 up

    def test_exact(self):
        self.assertEqual(fn(16, 50, True), 7)
        self.assertEqual(fn(3, 0, True), 3)     # 2.625


class Reject(unittest.TestCase):
    def _bad(self, *a):
        with self.assertRaises(ValueError):
            fn(*a)

    def test_paid(self):
        for v in (-1, 1.0, "100", True, None):
            with self.subTest(v=v):
                self._bad(v, 10, False)

    def test_used(self):
        for v in (-1, 101, 10.0, "10", True, None):
            with self.subTest(v=v):
                self._bad(100, v, False)

    def test_restock(self):
        for v in (1, 0, "yes", None, 1.0):
            with self.subTest(v=v):
                self._bad(100, 10, v)


if __name__ == "__main__":
    unittest.main()
