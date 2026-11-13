"""ตัวอย่างโครง test_solve.py (แทนที่ฟังก์ชันและตัวเลขตามโจทย์ · ค่าคาดหวังต้องคำนวณมือเป็นเลขตายตัว)"""
import unittest

from solve import cashback  # เปลี่ยนเป็นชื่อฟังก์ชันของโจทย์


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(cashback(20000, 'silver', False), 300)

    def test_normal_2(self):
        self.assertEqual(cashback(20000, 'gold', False), 500)

    def test_normal_3(self):
        self.assertEqual(cashback(20000, 'platinum', True), 1600)


class Boundary(unittest.TestCase):
    def test_boundary_1(self):  # ใต้ขั้นต่ำ 1 สตางค์
        self.assertEqual(cashback(9999, 'gold', False), 0)

    def test_boundary_2(self):  # พอดีขั้นต่ำ ต้องไม่ใช่ 0
        self.assertEqual(cashback(10000, 'silver', False), 150)

    def test_boundary_3(self):  # ชนเพดาน
        self.assertEqual(cashback(500000, 'platinum', False), 20000)

    def test_boundary_4(self):  # เกินเพดาน
        self.assertEqual(cashback(5000000, 'platinum', True), 20000)


class NoDrift(unittest.TestCase):
    def test_no_drift_1(self):  # 300.6 -> 301 (floor จะได้ 300)
        self.assertEqual(cashback(10020, 'silver', True), 301)

    def test_no_drift_2(self):  # 501.0 / ทดสอบค่าที่ลงท้าย .5 ด้วยถ้าสร้างได้
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

    def test_reject_5(self):
        with self.assertRaises(ValueError):
            cashback(True, 'gold', False)

    def test_reject_6(self):
        with self.assertRaises(ValueError):
            cashback(20000, 'gold', 1)


if __name__ == "__main__":
    unittest.main()
