import unittest
from solve import shipping_fee as f


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(f(500, 10, False), 4000)
        self.assertEqual(f(3000, 10, False), 8000)
        self.assertEqual(f(10000, 10, False), 8000 + 7500)
        self.assertEqual(f(500, 150, True), 4000 * 12 * 3 // 20)  # 7200

    def test_boundary(self):
        self.assertEqual(f(1000, 1, False), 4000)
        self.assertEqual(f(1001, 1, False), 8000)
        self.assertEqual(f(5000, 1, False), 8000)
        self.assertEqual(f(5001, 1, False), 8002)  # 1.5 สตางค์ -> 8001.5 ปัดขึ้น
        self.assertEqual(f(500, 100, False), 4000)
        self.assertEqual(f(500, 101, False), 4800)
        self.assertEqual(f(500, 0, False), 0)
        self.assertEqual(f(20000, 1, True), (8000 + 22500) * 3 // 2)
        self.assertEqual(f(30000, 1, False), 8000 + 37500)

    def test_nodrift(self):
        # 5003 g: 8004.5 *1.2*1.5 = 14408.1 -> 14408
        self.assertEqual(f(5003, 101, True), 14408)

    def test_reject(self):
        bad = [(0, 1, False), (30001, 1, False), (-1, 1, False), (500.0, 1, False),
               ("5", 1, False), (True, 1, False), (None, 1, False),
               (500, -1, False), (500, 10.5, False), (500, 10.0, False),
               (500, "1", False), (500, True, False), (500, None, False),
               (500, 1, 1), (500, 1, 0), (500, 1, "yes"), (500, 1, None),
               (20001, 1, True), (20001, 0, True), (0, 0, False)]
        for a in bad:
            with self.assertRaises(ValueError, msg=a):
                f(*a)


if __name__ == "__main__":
    unittest.main()
