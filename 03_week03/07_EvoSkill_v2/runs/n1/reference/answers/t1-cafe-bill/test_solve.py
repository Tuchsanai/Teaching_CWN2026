"""เทสต์ของเฉลยอ้างอิง: python3 -m unittest -q test_solve"""
import unittest

from solve import cafe_bill


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(cafe_bill([{'price': 4500, 'qty': 2}], False), 9630)

    def test_normal_2(self):
        self.assertEqual(cafe_bill([{'price': 4500, 'qty': 2}], True), 8667)

    def test_normal_3(self):
        self.assertEqual(cafe_bill([{'price': 12000, 'qty': 1}, {'price': 6500, 'qty': 2}], False), 26750)


class Boundary(unittest.TestCase):
    def test_boundary_1(self):
        self.assertEqual(cafe_bill([{'price': 50000, 'qty': 1}], False), 50825)

    def test_boundary_2(self):
        self.assertEqual(cafe_bill([{'price': 49999, 'qty': 1}], False), 53499)

    def test_boundary_3(self):
        self.assertEqual(cafe_bill([{'price': 0, 'qty': 1}, {'price': 4500, 'qty': 1}], False), 4815)


class NoDrift(unittest.TestCase):
    def test_no_drift_1(self):
        self.assertEqual(cafe_bill([{'price': 4505, 'qty': 1}], True), 4338)

    def test_no_drift_2(self):
        self.assertEqual(cafe_bill([{'price': 25075, 'qty': 2}], True), 45880)


class Reject(unittest.TestCase):
    def test_reject_1(self):
        with self.assertRaises(ValueError):
            cafe_bill([{'price': 4500, 'qty': 0}], False)

    def test_reject_2(self):
        with self.assertRaises(ValueError):
            cafe_bill([{'price': 4500, 'qty': -1}], False)

    def test_reject_3(self):
        with self.assertRaises(ValueError):
            cafe_bill([{'price': 4500.0, 'qty': 1}], False)

    def test_reject_4(self):
        with self.assertRaises(ValueError):
            cafe_bill([{'price': 4500, 'qty': '2'}], False)


if __name__ == "__main__":
    unittest.main()
