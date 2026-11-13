"""เทสต์ของเฉลยอ้างอิง: python3 -m unittest -q test_solve"""
import unittest

from solve import refund


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(refund(100000, 0, False), 100000)

    def test_normal_2(self):
        self.assertEqual(refund(100000, 25, False), 75000)

    def test_normal_3(self):
        self.assertEqual(refund(100000, 50, True), 43750)

    def test_normal_4(self):
        self.assertEqual(refund(100000, 81, False), 0)

    def test_normal_5(self):
        self.assertEqual(refund(240000, 10, True), 189000)

    def test_normal_6(self):
        self.assertEqual(refund(5551, 13, True), 4226)


class Reject(unittest.TestCase):
    def test_reject_1(self):
        with self.assertRaises(ValueError):
            refund(-1, 10, False)

    def test_reject_2(self):
        with self.assertRaises(ValueError):
            refund(100000, 101, False)

    def test_reject_3(self):
        with self.assertRaises(ValueError):
            refund(100000.0, 10, False)

    def test_reject_4(self):
        with self.assertRaises(ValueError):
            refund(100000, 10, 'yes')


if __name__ == "__main__":
    unittest.main()
