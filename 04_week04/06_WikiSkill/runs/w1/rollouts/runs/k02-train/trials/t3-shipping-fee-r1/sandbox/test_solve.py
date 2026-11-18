import unittest
from solve import shipping_fee as f


class TestSolve(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(f(500, 10, False), 4000)
        self.assertEqual(f(3000, 10, False), 8000)
        self.assertEqual(f(10000, 10, False), 15500)  # 80 + 5*15 = 155 บาท
        self.assertEqual(f(500, 150, True), 7200)     # 40*1.2*1.5 = 72 บาท

    def test_weight_boundaries(self):
        self.assertEqual(f(1, 0, False), 4000)
        self.assertEqual(f(1000, 0, False), 4000)
        self.assertEqual(f(1001, 0, False), 8000)
        self.assertEqual(f(5000, 0, False), 8000)
        self.assertEqual(f(5001, 0, False), 8000 + 2)  # 1.5 สตางค์ -> ปัดขึ้น 2
        self.assertEqual(f(30000, 0, False), 8000 + 37500)

    def test_distance_boundaries(self):
        self.assertEqual(f(500, 100, False), 4000)  # ข้อสมมติ: เกิน 100 จริงจึงคิดเพิ่ม
        self.assertEqual(f(500, 100.5, False), 4800)
        self.assertEqual(f(500, 101, False), 4800)

    def test_rounding(self):
        self.assertEqual(f(5001, 0, False), 8002)  # 8001.5 -> 8002
        self.assertEqual(f(5003, 0, False), 8005)  # 8004.5 -> 8005
        self.assertEqual(f(5001, 101, True), 14403)  # 8001.5*1.8=14402.7

    def test_type_int(self):
        self.assertIs(type(f(5001, 0, True)), int)

    def test_reject(self):
        bad = [
            (0, 1, False), (-5, 1, False), (30001, 1, False), (500.0, 1, False),
            (True, 1, False), ("500", 1, False), (None, 1, False),
            (500, -1, False), (500, "10", False), (500, True, False),
            (500, float("nan"), False), (500, float("inf"), False), (500, None, False),
            (500, 1, 1), (500, 1, None), (500, 1, "yes"),
        ]
        for args in bad:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    f(*args)


if __name__ == "__main__":
    unittest.main()
