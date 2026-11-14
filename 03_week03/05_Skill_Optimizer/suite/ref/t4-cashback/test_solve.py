"""เทสต์ของเฉลยอ้างอิง: python3 -m unittest -q test_solve"""
import unittest

from solve import cashback


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(cashback(20000, 'silver', False), 300)

    def test_normal_2(self):
        self.assertEqual(cashback(20000, 'gold', False), 500)

    def test_normal_3(self):
        self.assertEqual(cashback(20000, 'platinum', True), 1600)


class Boundary(unittest.TestCase):
    def test_boundary_1(self):
        self.assertEqual(cashback(9999, 'gold', False), 0)

    def test_boundary_2(self):
        self.assertEqual(cashback(10000, 'silver', False), 150)

    def test_boundary_3(self):
        self.assertEqual(cashback(500000, 'platinum', False), 20000)


class NoDrift(unittest.TestCase):
    def test_no_drift_1(self):
        self.assertEqual(cashback(10015, 'platinum', True), 801)

    def test_no_drift_2(self):
        self.assertEqual(cashback(10020, 'gold', True), 501)


class Reject(unittest.TestCase):
    def test_reject_1(self):
        with self.assertRaises(ValueError):
            cashback(-1, 'gold', False)

    def test_reject_2(self):
        with self.assertRaises(ValueError):
            cashback(20000, 'bronze', False)

    def test_reject_3(self):
        with self.assertRaises(ValueError):
            cashback(20000.0, 'gold', False)

    def test_reject_4(self):
        with self.assertRaises(ValueError):
            cashback('20000', 'gold', False)


if __name__ == "__main__":
    unittest.main()
