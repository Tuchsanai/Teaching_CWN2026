"""เทสต์ของเฉลยอ้างอิง: python3 -m unittest -q test_solve"""
import unittest

from solve import bulk_price


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(bulk_price(25000, 1, False), 26750)

    def test_normal_2(self):
        self.assertEqual(bulk_price(25000, 10, False), 258138)

    def test_normal_3(self):
        self.assertEqual(bulk_price(25000, 9, False), 240750)

    def test_normal_4(self):
        self.assertEqual(bulk_price(25000, 50, False), 1237188)

    def test_normal_5(self):
        self.assertEqual(bulk_price(25000, 20, True), 503368)

    def test_normal_6(self):
        self.assertEqual(bulk_price(4989, 50, True), 240721)


class Reject(unittest.TestCase):
    def test_reject_1(self):
        with self.assertRaises(ValueError):
            bulk_price(25000, 0, False)

    def test_reject_2(self):
        with self.assertRaises(ValueError):
            bulk_price(-1, 5, False)

    def test_reject_3(self):
        with self.assertRaises(ValueError):
            bulk_price(25000.0, 5, False)

    def test_reject_4(self):
        with self.assertRaises(ValueError):
            bulk_price(25000, '5', False)


if __name__ == "__main__":
    unittest.main()
