"""เทสต์ของเฉลยอ้างอิง: python3 -m unittest -q test_solve"""
import unittest

from solve import late_fee


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(late_fee(100000, 4), 3000)

    def test_normal_2(self):
        self.assertEqual(late_fee(100000, 10), 7500)

    def test_normal_3(self):
        self.assertEqual(late_fee(100000, 3), 0)

    def test_normal_4(self):
        self.assertEqual(late_fee(100000, 21), 15000)

    def test_normal_5(self):
        self.assertEqual(late_fee(250000, 7), 13125)

    def test_normal_6(self):
        self.assertEqual(late_fee(1234, 7), 65)


class Reject(unittest.TestCase):
    def test_reject_1(self):
        with self.assertRaises(ValueError):
            late_fee(-1, 5)

    def test_reject_2(self):
        with self.assertRaises(ValueError):
            late_fee(100000, 366)

    def test_reject_3(self):
        with self.assertRaises(ValueError):
            late_fee(100000.0, 5)

    def test_reject_4(self):
        with self.assertRaises(ValueError):
            late_fee(100000, '5')


if __name__ == "__main__":
    unittest.main()
