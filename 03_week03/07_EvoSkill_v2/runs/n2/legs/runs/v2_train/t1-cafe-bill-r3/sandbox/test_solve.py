"""รัน: python3 -m unittest -q test_solve (ค่าที่คาดคำนวณมือ)"""
import unittest

from solve import cafe_bill


def one(price, qty=1):
    return [{"price": price, "qty": qty}]


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(cafe_bill(one(10000), False), 10700)  # 10000*1.07

    def test_normal_2(self):
        self.assertEqual(cafe_bill(one(10000), True), 9630)  # 9000*1.07

    def test_normal_3(self):
        self.assertEqual(cafe_bill(one(20000, 3), True), 54891)  # 60000*.95*.9*1.07


class Boundary(unittest.TestCase):
    def test_boundary_1(self):
        self.assertEqual(cafe_bill(one(50000), False), 50825)  # 47500*1.07 ลดที่ 500 พอดี

    def test_boundary_2(self):
        self.assertEqual(cafe_bill(one(49999), False), 53499)  # 53498.93 ไม่ลด

    def test_boundary_3(self):
        self.assertEqual(cafe_bill([], False), 0)


class NoDrift(unittest.TestCase):
    def test_no_drift_1(self):
        self.assertEqual(cafe_bill(one(50), False), 54)  # 53.5 -> half-up

    def test_no_drift_2(self):
        self.assertEqual(cafe_bill(one(50001), False), 50826)  # 50826.0165

    def test_no_drift_3(self):
        self.assertEqual(cafe_bill(one(5), True), 5)  # 4.815


class Reject(unittest.TestCase):
    def test_reject_1(self):
        for bad in (one(-1), one(100, 0), one(100, -2)):
            with self.assertRaises(ValueError):
                cafe_bill(bad, False)

    def test_reject_2(self):
        for bad in (one(100.0), one(100, 1.0)):
            with self.assertRaises(ValueError):
                cafe_bill(bad, False)

    def test_reject_3(self):
        for bad in (one("100"), one(100, "1"), "x", None, [1], [{"price": 1}]):
            with self.assertRaises(ValueError):
                cafe_bill(bad, False)

    def test_reject_4(self):
        for bad in (one(True), one(100, True)):
            with self.assertRaises(ValueError):
                cafe_bill(bad, False)
        for m in (1, "yes", None):
            with self.assertRaises(ValueError):
                cafe_bill(one(100), m)


if __name__ == "__main__":
    unittest.main()
