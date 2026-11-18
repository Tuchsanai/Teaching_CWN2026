import unittest
from solve import cafe_bill


def it(p, q=1):
    return {"price": p, "qty": q}


class TestSolve(unittest.TestCase):
    def test_normal_no_discount(self):
        self.assertEqual(cafe_bill([it(10000)], False), 10700)

    def test_normal_member_only(self):
        # 10000*0.9=9000 *1.07=9630
        self.assertEqual(cafe_bill([it(10000)], True), 9630)

    def test_normal_multi_items_big(self):
        # 60000+5000=65000 *.95=61750 *1.07=66072.5 -> 66073
        self.assertEqual(cafe_bill([it(30000, 2), it(5000)], False), 66073)

    def test_edge_exactly_500_baht(self):
        # 50000*.95=47500 *1.07=50825 (พอดีเกณฑ์ ได้ลด)
        self.assertEqual(cafe_bill([it(50000)], False), 50825)

    def test_edge_below_500_baht(self):
        # 49999*1.07=53498.93 -> 53499 (ไม่ได้ลด)
        self.assertEqual(cafe_bill([it(49999)], False), 53499)

    def test_edge_above_500_baht(self):
        # 50001*.95=47500.95 *1.07=50826.0165 -> 50826
        self.assertEqual(cafe_bill([it(50001)], False), 50826)

    def test_discounts_stack_member(self):
        # 47500*.9=42750 *1.07=45742.5 -> half up 45743
        self.assertEqual(cafe_bill([it(50000)], True), 45743)

    def test_rounding_half_up(self):
        # 39150*1.07=41890.5 -> 41891
        self.assertEqual(cafe_bill([it(12000, 2), it(5050, 3)], False), 41891)

    def test_result_is_int(self):
        self.assertIs(type(cafe_bill([it(333, 3)], True)), int)

    def test_reject_items(self):
        for bad in ([], None, "x", [1], [{"price": 1}], [{"qty": 1}], {"price": 1, "qty": 1}):
            with self.assertRaises(ValueError):
                cafe_bill(bad, False)

    def test_reject_price(self):
        for bad in (100.0, True, -1, "100", None):
            with self.assertRaises(ValueError):
                cafe_bill([it(bad)], False)

    def test_reject_qty(self):
        for bad in (0, -1, 1.0, True, "1", None):
            with self.assertRaises(ValueError):
                cafe_bill([it(100, bad)], False)

    def test_reject_member(self):
        for bad in (1, 0, "True", None):
            with self.assertRaises(ValueError):
                cafe_bill([it(100)], bad)

    def test_reject_later_item(self):
        with self.assertRaises(ValueError):
            cafe_bill([it(100), it(100, 0)], False)


if __name__ == "__main__":
    unittest.main()
