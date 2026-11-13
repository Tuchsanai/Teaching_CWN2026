import unittest

from solve import cafe_bill


def one(price, qty=1):
    return [{"price": price, "qty": qty}]


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(cafe_bill(one(10000, 2), False), 21400)

    def test_normal_2(self):
        self.assertEqual(cafe_bill(one(10000, 2), True), 19260)

    def test_normal_3(self):
        self.assertEqual(cafe_bill([{"price": 333, "qty": 3}, {"price": 1, "qty": 1}], False), 1070)

    def test_normal_4(self):  # 100000 -> 95000 -> 101650
        self.assertEqual(cafe_bill(one(50000, 2), False), 101650)


class Boundary(unittest.TestCase):
    def test_boundary_1(self):  # 49999 ไม่ลด: 53498.93
        self.assertEqual(cafe_bill(one(49999), False), 53499)

    def test_boundary_2(self):  # 50000 ลด 5%: 50825
        self.assertEqual(cafe_bill(one(50000), False), 50825)

    def test_boundary_3(self):  # 50001: 50826.0165
        self.assertEqual(cafe_bill(one(50001), False), 50826)

    def test_boundary_4(self):  # ยอดรวมข้ามหลายรายการถึง 50000
        self.assertEqual(cafe_bill([{"price": 25000, "qty": 1}, {"price": 12500, "qty": 2}], False), 50825)

    def test_boundary_5(self):
        self.assertEqual(cafe_bill([], False), 0)

    def test_boundary_6(self):  # 49999 member: 48149.037
        self.assertEqual(cafe_bill(one(49999), True), 48149)


class NoDrift(unittest.TestCase):
    def test_no_drift_1(self):  # 160.5 -> 161 (round() ได้ 160)
        self.assertEqual(cafe_bill(one(150), False), 161)

    def test_no_drift_2(self):  # 45742.5 -> 45743
        self.assertEqual(cafe_bill(one(50000), True), 45743)

    def test_no_drift_3(self):  # 9.63 -> 10
        self.assertEqual(cafe_bill(one(10), True), 10)

    def test_no_drift_4(self):  # 53.5 -> 54 / 10.7 -> 11
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
        self.bad(one(-1))

    def test_reject_4(self):
        self.bad(one(100.0))

    def test_reject_5(self):
        self.bad(one(100, 1.0))

    def test_reject_6(self):
        self.bad(one("100"))

    def test_reject_7(self):
        self.bad(one(True))

    def test_reject_8(self):
        self.bad(one(100, True))

    def test_reject_9(self):
        self.bad(one(None))

    def test_reject_10(self):
        self.bad([{"price": 100}])

    def test_reject_11(self):
        self.bad([{"qty": 1}])

    def test_reject_12(self):
        self.bad(["x"])

    def test_reject_13(self):
        self.bad(None)

    def test_reject_14(self):
        self.bad(tuple(one(100)))

    def test_reject_15(self):
        self.bad(one(100), 1)

    def test_reject_16(self):
        self.bad(one(100), None)

    def test_reject_17(self):
        self.bad(one(100), "True")


if __name__ == "__main__":
    unittest.main()
