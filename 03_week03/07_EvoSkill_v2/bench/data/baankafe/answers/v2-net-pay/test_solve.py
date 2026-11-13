"""เทสต์ของเฉลยอ้างอิง: python3 -m unittest -q test_solve"""
import unittest

from solve import net_pay


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(net_pay(40, 10000, False), 388000)

    def test_normal_2(self):
        self.assertEqual(net_pay(40, 10000, True), 368000)

    def test_normal_3(self):
        self.assertEqual(net_pay(45, 10000, False), 460750)


class Boundary(unittest.TestCase):
    def test_boundary_1(self):
        self.assertEqual(net_pay(0, 10000, False), 0)

    def test_boundary_2(self):
        self.assertEqual(net_pay(40, 12345, False), 478986)

    def test_boundary_3(self):
        self.assertEqual(net_pay(41, 10000, False), 402550)


class NoDrift(unittest.TestCase):
    def test_no_drift_1(self):
        self.assertEqual(net_pay(38, 5005, True), 174975)

    def test_no_drift_2(self):
        self.assertEqual(net_pay(41, 5005, True), 191091)


class Reject(unittest.TestCase):
    def test_reject_1(self):
        with self.assertRaises(ValueError):
            net_pay(-1, 10000, False)

    def test_reject_2(self):
        with self.assertRaises(ValueError):
            net_pay(81, 10000, False)

    def test_reject_3(self):
        with self.assertRaises(ValueError):
            net_pay(40.0, 10000, False)

    def test_reject_4(self):
        with self.assertRaises(ValueError):
            net_pay('40', 10000, False)


if __name__ == "__main__":
    unittest.main()
