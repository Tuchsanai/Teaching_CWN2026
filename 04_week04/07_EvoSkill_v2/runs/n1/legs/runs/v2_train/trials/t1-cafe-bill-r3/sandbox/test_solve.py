"""python3 -m unittest -q test_solve"""
import unittest

from solve import cafe_bill  # <- เปลี่ยนชื่อฟังก์ชัน


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(cafe_bill([{'price': 4500, 'qty': 2}], False), 9630)  # คำนวณมือแล้ว


class Boundary(unittest.TestCase):
    def test_on_line(self):
        self.assertEqual(cafe_bill([{'price': 50000, 'qty': 1}], False), 50825)

    def test_below_line(self):
        self.assertEqual(cafe_bill([{'price': 49999, 'qty': 1}], False), 53499)


class NoDrift(unittest.TestCase):
    def test_rounding(self):
        self.assertEqual(cafe_bill([{'price': 4505, 'qty': 1}], True), 4338)


class Reject(unittest.TestCase):
    def test_zero_qty(self):
        with self.assertRaises(ValueError):
            cafe_bill([{'price': 4500, 'qty': 0}], False)

    def test_float(self):
        with self.assertRaises(ValueError):
            cafe_bill([{'price': 4500.0, 'qty': 1}], False)

    def test_str(self):
        with self.assertRaises(ValueError):
            cafe_bill([{'price': 4500, 'qty': '2'}], False)

    def test_bool(self):
        with self.assertRaises(ValueError):
            cafe_bill([{'price': True, 'qty': 1}], False)

    def test_none_member(self):
        with self.assertRaises(ValueError):
            cafe_bill([], 1)

    def test_missing_key(self):
        with self.assertRaises(ValueError):
            cafe_bill([{'price': 1}], False)

    def test_negative_price(self):
        with self.assertRaises(ValueError):
            cafe_bill([{'price': -1, 'qty': 1}], False)


class Empty(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(cafe_bill([], False), 0)


if __name__ == "__main__":
    unittest.main()
