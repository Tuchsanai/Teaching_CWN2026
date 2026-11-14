import unittest
from solve import shipping_fee as f


class TestSolve(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(f(500, 10, False), 4000)
        self.assertEqual(f(3000, 50, False), 8000)
        self.assertEqual(f(10000, 50, False), 15500)  # 80+75 บาท
        self.assertEqual(f(500, 10, True), 6000)
        self.assertEqual(f(3000, 150, True), 14400)  # 80*1.2*1.5

    def test_weight_edges(self):
        self.assertEqual(f(1, 0, False), 4000)
        self.assertEqual(f(1000, 0, False), 4000)
        self.assertEqual(f(1001, 0, False), 8000)
        self.assertEqual(f(5000, 0, False), 8000)
        self.assertEqual(f(5001, 0, False), 8002)  # 1.5 สตางค์ปัดขึ้น
        self.assertEqual(f(30000, 0, False), 8000 + 37500)

    def test_distance_edges(self):
        # สมมติ: เกิน 100 กม. คือ > 100 ; พอดี 100 ไม่เพิ่ม
        self.assertEqual(f(500, 100, False), 4000)
        self.assertEqual(f(500, 100.5, False), 4800)
        self.assertEqual(f(500, 101, False), 4800)
        self.assertEqual(f(500, 99, False), 4000)

    def test_rounding(self):
        # 8001.5 -> 8002 ; express 8001.5*1.5=12002.25 -> 12002
        self.assertEqual(f(5001, 0, False), 8002)
        self.assertEqual(f(5001, 0, True), 12002)
        self.assertEqual(f(5003, 0, False), 8005)  # 8004.5 ปัดขึ้น
        self.assertIs(type(f(5001, 0, True)), int)

    def test_reject(self):
        bad = [
            (0, 1, False), (-1, 1, False), (30001, 1, False),
            (4500.0, 1, False), (True, 1, False), ("5", 1, False), (None, 1, False),
            (500, -1, False), (500, float("nan"), False), (500, float("inf"), False),
            (500, "10", False), (500, True, False), (500, None, False),
            (500, 1, 1), (500, 1, 0), (500, 1, "yes"), (500, 1, None),
        ]
        for a in bad:
            with self.subTest(a=a):
                with self.assertRaises(ValueError):
                    f(*a)


if __name__ == "__main__":
    unittest.main()
