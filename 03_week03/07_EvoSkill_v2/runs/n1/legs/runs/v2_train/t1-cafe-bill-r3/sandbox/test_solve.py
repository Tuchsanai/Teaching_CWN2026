import unittest

from solve import cafe_bill


def one(price, qty=1):
    return [{"price": price, "qty": qty}]


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(cafe_bill(one(10000, 2), False), 21400)

    def test_normal_2(self):
        self.assertEqual(cafe_bill(one(100000), False), 101650)

    def test_normal_3(self):
        self.assertEqual(cafe_bill(one(100000), True), 91485)

    def test_normal_4(self):
        self.assertEqual(cafe_bill([{"price": 6000, "qty": 1}, {"price": 7000, "qty": 2}], False), 21400)


class Boundary(unittest.TestCase):
    def test_boundary_1(self):
        self.assertEqual(cafe_bill(one(49999), False), 53499)

    def test_boundary_2(self):
        self.assertEqual(cafe_bill(one(50000), False), 50825)

    def test_boundary_3(self):
        self.assertEqual(cafe_bill(one(50001), False), 50826)

    def test_boundary_4(self):
        self.assertEqual(cafe_bill(one(49999), True), 48149)

    def test_boundary_5(self):
        self.assertEqual(cafe_bill(one(50000), True), 45743)

    def test_boundary_6(self):
        self.assertEqual(cafe_bill([], False), 0)

    def test_boundary_7(self):
        self.assertEqual(cafe_bill(one(0), True), 0)


class NoDrift(unittest.TestCase):
    def test_no_drift_1(self):  # 160.5 -> 161
        self.assertEqual(cafe_bill(one(150), False), 161)

    def test_no_drift_2(self):  # 53.5 -> 54
        self.assertEqual(cafe_bill(one(50), False), 54)

    def test_no_drift_3(self):  # 45743.41 รวมก่อนปัดครั้งเดียว (ปัดทีละขั้นได้ 45744)
        self.assertEqual(cafe_bill(one(50001), True), 45743)

    def test_no_drift_4(self):  # 10.7 -> 11
        self.assertEqual(cafe_bill(one(10), False), 11)


class Reject(unittest.TestCase):
    def bad(self, items, member=False):
        with self.assertRaises(ValueError):
            cafe_bill(items, member)

    def test_reject_1(self): self.bad(one(100, 0))
    def test_reject_2(self): self.bad(one(100, -1))
    def test_reject_3(self): self.bad(one(-1))
    def test_reject_4(self): self.bad(one(100.0))
    def test_reject_5(self): self.bad(one(100, 1.0))
    def test_reject_6(self): self.bad(one("100"))
    def test_reject_7(self): self.bad(one(100, "1"))
    def test_reject_8(self): self.bad(one(True))
    def test_reject_9(self): self.bad(one(100, True))
    def test_reject_10(self): self.bad(one(None))
    def test_reject_11(self): self.bad([{"price": 100}])
    def test_reject_12(self): self.bad([{"qty": 1}])
    def test_reject_13(self): self.bad([5])
    def test_reject_14(self): self.bad(None)
    def test_reject_15(self): self.bad("abc")
    def test_reject_16(self): self.bad(one(100), 1)
    def test_reject_17(self): self.bad(one(100), None)
    def test_reject_18(self): self.bad(one(100), "True")


if __name__ == "__main__":
    unittest.main()
