"""เทสต์ของ solve.py: python3 -m unittest -q test_solve
แม่แบบ: คัดลอกเป็น ./test_solve.py แล้วแทน example_fn/ค่า ให้ตรงโจทย์ (หนึ่งเมธอด = หนึ่งกรณี)"""
import unittest

from solve import example_fn


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(example_fn(20000, False), 20000)

    def test_normal_2(self):
        self.assertEqual(example_fn(20000, True), 18000)

    def test_normal_3(self):
        self.assertEqual(example_fn(12345, False), 12345)


class Boundary(unittest.TestCase):
    def test_boundary_1(self):   # พอดีเกณฑ์ (≥)
        self.assertEqual(example_fn(0, False), 0)

    def test_boundary_2(self):   # ต่ำกว่าเกณฑ์ 1 หน่วย
        self.assertEqual(example_fn(1, False), 1)

    def test_boundary_3(self):   # ค่าสูงสุด/ขอบบนที่โจทย์อนุญาต
        self.assertEqual(example_fn(10**9, False), 10**9)


class NoDrift(unittest.TestCase):  # เศษสตางค์ / ทิศทางการปัด ตรวจมือแล้วด้วย Fraction
    def test_no_drift_1(self):
        self.assertEqual(example_fn(4505, True), 4055)  # 4054.5 → half-up

    def test_no_drift_2(self):
        self.assertEqual(example_fn(1, True), 1)        # 0.9 → 1


class Reject(unittest.TestCase):
    def test_reject_1(self):     # ต่ำกว่าช่วง (ติดลบ/0 ตามโจทย์)
        with self.assertRaises(ValueError):
            example_fn(-1, False)

    def test_reject_2(self):     # float
        with self.assertRaises(ValueError):
            example_fn(100.0, False)

    def test_reject_3(self):     # str
        with self.assertRaises(ValueError):
            example_fn("100", False)

    def test_reject_4(self):     # bool ในช่องจำนวนเต็ม / int ในช่อง flag
        with self.assertRaises(ValueError):
            example_fn(100, 1)


if __name__ == "__main__":
    unittest.main()
