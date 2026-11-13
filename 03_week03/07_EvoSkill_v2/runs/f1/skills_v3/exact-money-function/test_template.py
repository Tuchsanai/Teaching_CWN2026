"""เทมเพลต test_solve.py — เปลี่ยน my_function และค่าคาดหวังให้ตรงโจทย์ (คำนวณมือด้วย Fraction ยืนยันก่อนใส่)
รัน: python3 -m unittest -q test_solve"""
import unittest

from solve import my_function as fn  # <- เปลี่ยนชื่อ


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(fn(20000, False), 18000)


class Boundary(unittest.TestCase):
    def test_boundary_below(self):  # X-1, X, X+1 ของทุกเส้นขอบ
        self.assertEqual(fn(9999, False), 9999)


class NoDrift(unittest.TestCase):
    def test_half_up(self):  # เศษ .5 พอดีต้องขึ้น / เศษไม่ลงตัวไม่มี float drift
        self.assertEqual(fn(10001, True), 9001)


class Reject(unittest.TestCase):
    def test_negative(self):
        with self.assertRaises(ValueError):
            fn(-1, False)

    def test_float(self):
        with self.assertRaises(ValueError):
            fn(20000.0, False)

    def test_str(self):
        with self.assertRaises(ValueError):
            fn("20000", False)

    def test_bad_flag(self):
        with self.assertRaises(ValueError):
            fn(20000, 1)


if __name__ == "__main__":
    unittest.main()
