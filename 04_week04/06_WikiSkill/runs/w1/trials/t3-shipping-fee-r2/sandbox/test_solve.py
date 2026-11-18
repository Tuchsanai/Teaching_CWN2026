import unittest
from solve import shipping_fee as f


class TestSolve(unittest.TestCase):
    def test_light(self):
        self.assertEqual(f(500, 10, False), 4000)

    def test_mid(self):
        self.assertEqual(f(3000, 10, False), 8000)

    def test_heavy(self):
        self.assertEqual(f(10000, 10, False), 15500)

    def test_far(self):
        self.assertEqual(f(500, 150, False), 4800)

    def test_express(self):
        self.assertEqual(f(500, 10, True), 6000)

    def test_far_express(self):
        self.assertEqual(f(500, 150, True), 7200)

    def test_edge_1000(self):
        self.assertEqual(f(1000, 0, False), 4000)
        self.assertEqual(f(1001, 0, False), 8000)

    def test_edge_5000(self):
        self.assertEqual(f(5000, 0, False), 8000)
        self.assertEqual(f(5001, 0, False), 8002)  # เกิน 1 ก. = 1.5 สตางค์ ปัดขึ้น

    def test_edge_distance(self):
        self.assertEqual(f(500, 100, False), 4000)  # พอดี 100 ไม่คิดเพิ่ม
        self.assertEqual(f(500, 100.5, False), 4800)

    def test_edge_weight_limits(self):
        self.assertEqual(f(1, 0, False), 4000)
        self.assertEqual(f(30000, 0, False), 8000 + 37500)

    def test_rounding_half_up(self):
        self.assertEqual(f(5003, 0, False), 8005)  # 4.5 -> 5

    def test_int_type(self):
        self.assertIs(type(f(5001, 150, True)), int)

    def test_reject_weight_g(self):
        for bad in (0, -1, 30001, 500.0, True, "500", None):
            with self.assertRaises(ValueError):
                f(bad, 10, False)

    def test_reject_distance_km(self):
        for bad in (-1, -0.1, True, "10", None, float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                f(500, bad, False)

    def test_reject_express(self):
        for bad in (1, 0, "True", None):
            with self.assertRaises(ValueError):
                f(500, 10, bad)


if __name__ == "__main__":
    unittest.main()
