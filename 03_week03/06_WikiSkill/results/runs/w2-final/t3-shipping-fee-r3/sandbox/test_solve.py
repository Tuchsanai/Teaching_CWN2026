import unittest
from solve import shipping_fee as F


class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(F(500, 10, False), 4000)
        self.assertEqual(F(3000, 10, False), 8000)

    def test_boundary_exact(self):
        self.assertEqual(F(1000, 0, False), 4000)
        self.assertEqual(F(5000, 100, False), 8000)

    def test_boundary_below(self):
        self.assertEqual(F(999, 99, False), 4000)
        self.assertEqual(F(4999, 0, False), 8000)

    def test_boundary_above(self):
        self.assertEqual(F(1001, 0, False), 8000)
        self.assertEqual(F(6000, 0, False), 9500)
        self.assertEqual(F(500, 101, False), 4800)

    def test_half_up(self):
        # 5001g: 8000+1.5=8001.5 satang -> 8002
        self.assertEqual(F(5001, 0, False), 8002)
        # 5001g express: 12002.25 -> 12002 ; 5003 express: 8004.5*1.5=12006.75->12007
        self.assertEqual(F(5001, 0, True), 12002)
        self.assertEqual(F(5003, 0, True), 12007)

    def test_reject_value(self):
        for a in [(0, 1, False), (30001, 1, False), (100, -1, False)]:
            with self.assertRaises(ValueError):
                F(*a)

    def test_reject_type(self):
        for a in [(1000.0, 1, False), (True, 1, False), ("1", 1, False),
                  (100, None, False), (100, 1, 1), (100, 1.5, False)]:
            with self.assertRaises(ValueError):
                F(*a)

    def test_zero_or_cap(self):
        self.assertEqual(F(1, 0, False), 4000)
        # max: 80+25*15=455 baht *1.2*1.5 = 819
        self.assertEqual(F(30000, 101, True), 81900)
        self.assertEqual(F(500, 101, True), 7200)


if __name__ == "__main__":
    unittest.main()
