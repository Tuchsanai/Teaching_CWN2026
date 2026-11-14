"""python3 -m unittest -q test_solve"""
import unittest

from solve import example  # <- เปลี่ยนชื่อฟังก์ชัน


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(example([{'price': 4500, 'qty': 2}], False), 9630)  # คำนวณมือแล้ว


class Boundary(unittest.TestCase):
    def test_on_line(self):
        self.assertEqual(example([{'price': 50000, 'qty': 1}], False), 50825)

    def test_below_line(self):
        self.assertEqual(example([{'price': 49999, 'qty': 1}], False), 53499)


class NoDrift(unittest.TestCase):
    def test_rounding(self):
        self.assertEqual(example([{'price': 4505, 'qty': 1}], True), 4338)


class Reject(unittest.TestCase):
    def test_zero_qty(self):
        with self.assertRaises(ValueError):
            example([{'price': 4500, 'qty': 0}], False)

    def test_float(self):
        with self.assertRaises(ValueError):
            example([{'price': 4500.0, 'qty': 1}], False)

    def test_str(self):
        with self.assertRaises(ValueError):
            example([{'price': 4500, 'qty': '2'}], False)

    def test_bool(self):
        with self.assertRaises(ValueError):
            example([{'price': True, 'qty': 1}], False)


if __name__ == "__main__":
    unittest.main()
