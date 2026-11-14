import unittest
from solve import shipping_fee


class TestSolve(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(shipping_fee(500, 10, False), 4000)
        self.assertEqual(shipping_fee(3000, 50, False), 8000)
        self.assertEqual(shipping_fee(10000, 50, False), 8000 + 7500)
        self.assertEqual(shipping_fee(500, 200, True), 7200)

    def test_edges(self):
        self.assertEqual(shipping_fee(1, 0, False), 4000)
        self.assertEqual(shipping_fee(1000, 0, False), 4000)
        self.assertEqual(shipping_fee(1001, 0, False), 8000)
        self.assertEqual(shipping_fee(5000, 0, False), 8000)
        self.assertEqual(shipping_fee(5001, 0, False), 8002)  # 1.5 สตางค์ -> ปัด 2
        self.assertEqual(shipping_fee(30000, 0, False), 8000 + 37500)
        # ระยะ 100 พอดี ไม่เพิ่ม; เกิน 100 เพิ่ม 20%
        self.assertEqual(shipping_fee(500, 100, False), 4000)
        self.assertEqual(shipping_fee(500, 100.1, False), 4800)

    def test_rounding(self):
        # 8001.5*1.2 = 9601.8 -> 9602
        self.assertEqual(shipping_fee(5001, 101, False), 9602)
        # 8001.5*1.5 = 12002.25 -> 12002
        self.assertEqual(shipping_fee(5001, 0, True), 12002)
        self.assertIs(type(shipping_fee(5001, 101, True)), int)

    def test_reject(self):
        for args in [(0, 1, False), (30001, 1, False), (-5, 1, False),
                     (4500.0, 1, False), (True, 1, False), ("5", 1, False),
                     (500, -1, False), (500, "1", False), (500, True, False),
                     (500, float("nan"), False), (500, float("inf"), False),
                     (500, 1, 1), (500, 1, None), (500, 1, "True")]:
            with self.assertRaises(ValueError):
                shipping_fee(*args)


if __name__ == "__main__":
    unittest.main()
