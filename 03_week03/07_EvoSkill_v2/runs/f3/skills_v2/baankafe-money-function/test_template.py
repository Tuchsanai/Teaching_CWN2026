"""แม่แบบ test_solve.py — เปลี่ยน import และค่าคาดหวังเป็นของโจทย์จริง (คำนวณมือก่อน อย่าเอาผลจากโค้ดมาเป็นค่าคาดหวัง)"""
import unittest

from solve import cafe_bill  # เปลี่ยนเป็นชื่อฟังก์ชันจริง


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(cafe_bill([{"price": 10000, "qty": 1}], False), 10700)


class Boundary(unittest.TestCase):
    # ทดสอบค่าที่ขอบพอดีและเกิน/ขาด 1 หน่วย
    def test_boundary_below(self):
        self.assertEqual(cafe_bill([{"price": 49999, "qty": 1}], False), 53499)

    def test_boundary_at(self):
        self.assertEqual(cafe_bill([{"price": 50000, "qty": 1}], False), 50825)


class NoDrift(unittest.TestCase):
    # ค่าที่ลงเศษครึ่งสตางค์ / ผลรวมที่แจกเศษต้องเท่ายอดเดิม
    def test_no_drift_1(self):
        pass  # ใส่เคสที่คำนวณมือจริง


class Reject(unittest.TestCase):
    def test_reject_float(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 100.0, "qty": 1}], False)

    def test_reject_str(self):
        with self.assertRaises(ValueError):
            cafe_bill([{"price": 100, "qty": "1"}], False)

    def test_reject_bool_flag(self):
        with self.assertRaises(ValueError):
            cafe_bill([], 1)


if __name__ == "__main__":
    unittest.main()
