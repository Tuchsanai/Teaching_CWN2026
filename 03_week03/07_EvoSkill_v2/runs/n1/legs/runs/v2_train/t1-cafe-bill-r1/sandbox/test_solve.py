import unittest

from solve import cafe_bill


def one(price, qty=1):
    return [{"price": price, "qty": qty}]


class Normal(unittest.TestCase):
    def test_normal_1(self):  # 20000 -> ไม่ลด -> x1.07
        self.assertEqual(cafe_bill(one(10000, 2), False), 21400)

    def test_normal_2(self):  # 60000 -> 57000 -> 60990
        self.assertEqual(cafe_bill(one(30000, 2), False), 60990)

    def test_normal_3(self):  # 60000 -> 57000 -> 51300 -> 54891
        self.assertEqual(cafe_bill(one(30000, 2), True), 54891)

    def test_normal_4(self):  # สมาชิก ยอดต่ำกว่า 500: 20000*.9*1.07 = 19260
        self.assertEqual(cafe_bill(one(10000, 2), True), 19260)

    def test_normal_5(self):  # หลายรายการ 30000+2*10000 = 50000
        items = [{"price": 30000, "qty": 1}, {"price": 10000, "qty": 2}]
        self.assertEqual(cafe_bill(items, False), 50825)


class Boundary(unittest.TestCase):
    def test_boundary_1(self):  # 49999*1.07 = 53498.93
        self.assertEqual(cafe_bill(one(49999), False), 53499)

    def test_boundary_2(self):  # 50000 -> 47500 -> 50825
        self.assertEqual(cafe_bill(one(50000), False), 50825)

    def test_boundary_3(self):  # 50001 -> 47500.95 -> 50826.0165
        self.assertEqual(cafe_bill(one(50001), False), 50826)

    def test_boundary_4(self):  # ราคา 0
        self.assertEqual(cafe_bill(one(0), False), 0)

    def test_boundary_5(self):  # list ว่าง
        self.assertEqual(cafe_bill([], True), 0)

    def test_boundary_6(self):  # qty=1 ขั้นต่ำ
        self.assertEqual(cafe_bill(one(100, 1), False), 107)


class NoDrift(unittest.TestCase):
    def test_no_drift_1(self):  # 150*1.07 = 160.5 -> 161 (round() ได้ 160)
        self.assertEqual(cafe_bill(one(150), False), 161)

    def test_no_drift_2(self):  # 50000*.95*.9*1.07 = 45742.5 -> 45743
        self.assertEqual(cafe_bill(one(50000), True), 45743)

    def test_no_drift_3(self):  # ปัดกลางทาง 47510 จะได้ 50836 แต่ปัดครั้งเดียวได้ 50835
        self.assertEqual(cafe_bill(one(50010), False), 50835)

    def test_no_drift_4(self):  # 50 * 1.07 = 53.5 -> 54
        self.assertEqual(cafe_bill(one(50), False), 54)


class Reject(unittest.TestCase):
    def bad(self, items, member=False):
        with self.assertRaises(ValueError):
            cafe_bill(items, member)

    def test_reject_1(self):
        self.bad(one(100, 0))

    def test_reject_2(self):
        self.bad(one(100, -1))

    def test_reject_3(self):
        self.bad(one(-1, 1))

    def test_reject_4(self):
        self.bad(one(100.0, 1))

    def test_reject_5(self):
        self.bad(one(100, 1.0))

    def test_reject_6(self):
        self.bad(one("100", 1))

    def test_reject_7(self):
        self.bad(one(100, "1"))

    def test_reject_8(self):
        self.bad(one(True, 1))

    def test_reject_9(self):
        self.bad(one(100, True))

    def test_reject_10(self):
        self.bad(one(None, 1))

    def test_reject_11(self):
        self.bad([{"price": 100}])

    def test_reject_12(self):
        self.bad([{"qty": 1}])

    def test_reject_13(self):
        self.bad([5])

    def test_reject_14(self):
        self.bad(None)

    def test_reject_15(self):
        self.bad(tuple(one(100)))

    def test_reject_16(self):
        self.bad(one(100), 1)

    def test_reject_17(self):
        self.bad(one(100), None)

    def test_reject_18(self):
        self.bad(one(100), "True")


if __name__ == "__main__":
    unittest.main()
