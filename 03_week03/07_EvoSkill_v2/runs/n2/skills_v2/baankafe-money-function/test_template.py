"""แม่แบบ test_solve.py — เปลี่ยนชื่อฟังก์ชันและค่าที่คาด (คำนวณมือ/Fraction แยกจากโค้ดหลัก)
รัน: python3 -m unittest -q test_solve"""
import unittest

from solve import my_function  # <- เปลี่ยนชื่อ


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(my_function(1, False), 0)  # <- ค่าที่คาดจริง

    def test_normal_2(self):
        self.assertEqual(my_function(2, True), 0)

    def test_normal_3(self):
        self.assertEqual(my_function(3, False), 0)


class Boundary(unittest.TestCase):
    # ติดขอบทั้งสองข้างของทุกเงื่อนไข (>= X กับ X-1, ช่วงต่ำสุด/สูงสุด)
    def test_boundary_1(self):
        self.assertEqual(my_function(1, False), 0)

    def test_boundary_2(self):
        self.assertEqual(my_function(1, False), 0)

    def test_boundary_3(self):
        self.assertEqual(my_function(1, False), 0)


class NoDrift(unittest.TestCase):
    # เคสที่มีเศษสตางค์/ครึ่งสตางค์ ให้รู้ว่าปัดทิศไหน
    def test_no_drift_1(self):
        self.assertEqual(my_function(1, True), 0)

    def test_no_drift_2(self):
        self.assertEqual(my_function(1, True), 0)


class Reject(unittest.TestCase):
    def test_reject_1(self):
        with self.assertRaises(ValueError):
            my_function(-1, False)

    def test_reject_2(self):
        with self.assertRaises(ValueError):
            my_function(1.0, False)  # float

    def test_reject_3(self):
        with self.assertRaises(ValueError):
            my_function("1", False)  # str

    def test_reject_4(self):
        with self.assertRaises(ValueError):
            my_function(True, False)  # bool


if __name__ == "__main__":
    unittest.main()
