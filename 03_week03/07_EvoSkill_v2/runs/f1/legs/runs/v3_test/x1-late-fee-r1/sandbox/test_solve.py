import unittest

from solve import late_fee as fn


class Normal(unittest.TestCase):
    def test_normal_4_days(self):
        self.assertEqual(fn(10000, 4), 300)

    def test_normal_7_days(self):
        self.assertEqual(fn(10000, 7), 525)

    def test_normal_10_days(self):
        self.assertEqual(fn(20000, 10), 1500)

    def test_zero_amount(self):
        self.assertEqual(fn(0, 100), 0)


class Boundary(unittest.TestCase):
    def test_grace_edge(self):
        self.assertEqual(fn(10000, 0), 0)
        self.assertEqual(fn(10000, 3), 0)
        self.assertEqual(fn(10000, 4), 300)

    def test_cap_edge(self):
        self.assertEqual(fn(10000, 19), 1425)
        self.assertEqual(fn(10000, 20), 1500)
        self.assertEqual(fn(10000, 21), 1500)

    def test_days_range(self):
        self.assertEqual(fn(10000, 365), 1500)
        self.assertEqual(fn(0, 0), 0)


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        self.assertEqual(fn(50, 4), 2)  # 1.5

    def test_below_half(self):
        self.assertEqual(fn(70, 4), 2)  # 2.1
        self.assertEqual(fn(10, 4), 0)  # 0.3

    def test_above_half(self):
        self.assertEqual(fn(90, 4), 3)  # 2.7
        self.assertEqual(fn(10050, 5), 377)  # 376.875

    def test_cap_half_up(self):
        self.assertEqual(fn(10, 100), 2)  # 1.5
        self.assertEqual(fn(15, 20), 2)  # 2.25


class Reject(unittest.TestCase):
    def test_bad_values(self):
        bad = [-1, 1.0, "1", True, None, [1]]
        for v in bad:
            with self.subTest(p="amount", v=v):
                with self.assertRaises(ValueError):
                    fn(v, 5)
        for v in bad + [366, 4.0]:
            with self.subTest(p="days", v=v):
                with self.assertRaises(ValueError):
                    fn(1000, v)

    def test_amount_float(self):
        with self.assertRaises(ValueError):
            fn(1000.5, 5)

    def test_days_bool(self):
        with self.assertRaises(ValueError):
            fn(1000, False)


if __name__ == "__main__":
    unittest.main()
