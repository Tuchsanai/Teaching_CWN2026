import unittest

from solve import cashback


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(cashback(20000, 'silver', False), 300)

    def test_normal_2(self):
        self.assertEqual(cashback(20000, 'gold', False), 500)

    def test_normal_3(self):
        self.assertEqual(cashback(20000, 'platinum', True), 1600)

    def test_normal_4(self):
        self.assertEqual(cashback(30000, 'gold', True), 1500)


class Boundary(unittest.TestCase):
    def test_boundary_1(self):
        self.assertEqual(cashback(9999, 'platinum', True), 0)

    def test_boundary_2(self):
        self.assertEqual(cashback(10000, 'silver', False), 150)

    def test_boundary_3(self):
        self.assertEqual(cashback(10001, 'silver', False), 150)

    def test_boundary_4(self):
        self.assertEqual(cashback(0, 'gold', False), 0)

    def test_boundary_5(self):  # ยังไม่ชนเพดาน
        self.assertEqual(cashback(499975, 'platinum', False), 19999)

    def test_boundary_6(self):  # พอดีเพดาน
        self.assertEqual(cashback(500000, 'platinum', False), 20000)

    def test_boundary_7(self):  # เกินเพดาน
        self.assertEqual(cashback(500025, 'platinum', False), 20000)

    def test_boundary_8(self):  # เพดานหลังคูณ 2
        self.assertEqual(cashback(5000000, 'platinum', True), 20000)

    def test_boundary_9(self):  # คูณ 2 พอดีเพดาน
        self.assertEqual(cashback(400000, 'gold', True), 20000)


class NoDrift(unittest.TestCase):
    def test_no_drift_1(self):  # 154.5 -> 155
        self.assertEqual(cashback(10300, 'silver', False), 155)

    def test_no_drift_2(self):  # 250.5 -> 251
        self.assertEqual(cashback(10020, 'gold', False), 251)

    def test_no_drift_3(self):  # 304.5 -> 305 (รวมคูณ 2 ก่อนปัดครั้งเดียว)
        self.assertEqual(cashback(10150, 'silver', True), 305)

    def test_no_drift_4(self):  # 150.15 -> 150
        self.assertEqual(cashback(10010, 'silver', False), 150)


class Reject(unittest.TestCase):
    def check(self, *args):
        with self.assertRaises(ValueError):
            cashback(*args)

    def test_reject_1(self):
        self.check(-1, 'gold', False)

    def test_reject_2(self):
        self.check(20000, 'bronze', False)

    def test_reject_3(self):
        self.check(20000.0, 'gold', False)

    def test_reject_4(self):
        self.check('20000', 'gold', False)

    def test_reject_5(self):
        self.check(True, 'gold', False)

    def test_reject_6(self):
        self.check(20000, 'gold', 1)

    def test_reject_7(self):
        self.check(None, 'gold', False)

    def test_reject_8(self):
        self.check(20000, None, False)

    def test_reject_9(self):
        self.check(20000, 'gold', None)

    def test_reject_10(self):
        self.check(20000, 'Gold', False)

    def test_reject_11(self):
        self.check(20000, 'gold', 'True')


if __name__ == "__main__":
    unittest.main()
