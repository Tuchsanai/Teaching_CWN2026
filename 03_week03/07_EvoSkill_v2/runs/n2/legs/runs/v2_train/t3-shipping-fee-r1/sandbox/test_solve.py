import unittest
from solve import shipping_fee as f


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(f(500, 10, False), 4000)
        self.assertEqual(f(3000, 10, False), 8000)
        self.assertEqual(f(10000, 10, False), 15500)  # 80+5*15=155 บาท
        self.assertEqual(f(1000, 101, True), 7200)   # 40*1.2*1.5=72
        self.assertEqual(f(30000, 200, True), int(((8000 + 25*1500) * 1.8) + 0.5))

    def test_boundary(self):
        self.assertEqual(f(1000, 100, False), 4000)
        self.assertEqual(f(1001, 100, False), 8000)
        self.assertEqual(f(5000, 100, False), 8000)
        self.assertEqual(f(5001, 100, False), 8002)  # 1.5 สตางค์ -> ปัดขึ้น
        self.assertEqual(f(1, 0, False), 4000)

    def test_half(self):
        # 5001g: 8001.5 -> 8002 ; express: 12002.25 -> 12002
        self.assertEqual(f(5001, 0, True), 12002)
        # 5003g: 8004.5 *1.5 = 12006.75 -> 12007
        self.assertEqual(f(5003, 0, True), 12007)

    def test_reject(self):
        for a in [(0, 1, False), (30001, 1, False), (1, -1, False), (1.0, 1, False),
                  (1, 1.0, False), ("1", 1, False), (True, 1, False), (None, 1, False),
                  (1, 1, 1), (1, 1, None), (1, True, False), (1, "1", False)]:
            with self.assertRaises(ValueError):
                f(*a)


if __name__ == "__main__":
    unittest.main()
