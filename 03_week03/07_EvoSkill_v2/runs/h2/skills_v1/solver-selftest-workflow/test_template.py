"""โครง test แยกหมวด: คัดลอกไปแก้ชื่อฟังก์ชันและกรณีทดสอบให้ตรงกับโจทย์

รัน: python3 -m unittest -v test_template
expected ทุกค่าต้องคำนวณด้วยสคริปต์ Fraction ก่อนใส่ (ดู SKILL.md)
"""
import unittest

from solve import my_function  # <- แก้ชื่อฟังก์ชันให้ตรงกับโจทย์


class Normal(unittest.TestCase):
    def test_basic(self):
        # ใส่กรณีปกติ 2–3 แบบ ให้ครอบคลุมทุกระดับ/ทุก flag
        # expected ต้องมาจากสคริปต์ Fraction เท่านั้น ห้ามคัดลอกค่าตัวอย่างจากไฟล์นี้
        # self.assertEqual(my_function(<args>), <expected จาก Fraction>)
        pass

    def test_flag_combinations(self):
        # ผสมทุกค่า flag กับทุกกลุ่มที่เป็นไปได้
        pass


class Boundary(unittest.TestCase):
    def test_at_threshold(self):
        # ค่าพอดีเกณฑ์ตามคำในโจทย์ (ตั้งแต่ = >=, เกิน = >)
        pass

    def test_just_below_and_above(self):
        # เกณฑ์ -1 และ +1
        pass

    def test_zero_and_max(self):
        # ค่า 0 และค่าสูงสุดของช่วง
        pass


class NoDrift(unittest.TestCase):
    def test_single_rounding(self):
        # กรณีที่ผลระหว่างทางเป็นทศนิยมใกล้ .5 ยืนยันว่าปัดครั้งเดียวและลำดับถูก
        pass


class Reject(unittest.TestCase):
    def test_bool_is_not_int(self):
        with self.assertRaises(ValueError):
            my_function(True, "gold", False)  # <- ปรับ argument ให้ตรงกับ parameter

    def test_float_is_not_int(self):
        with self.assertRaises(ValueError):
            my_function(4500.0, "gold", False)

    def test_string_is_not_int(self):
        with self.assertRaises(ValueError):
            my_function("4500", "gold", False)

    def test_out_of_range(self):
        with self.assertRaises(ValueError):
            my_function(-1, "gold", False)

    def test_unknown_choice(self):
        with self.assertRaises(ValueError):
            my_function(4500, "bronze", False)


if __name__ == "__main__":
    unittest.main()
