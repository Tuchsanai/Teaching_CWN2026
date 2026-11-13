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
        self.assertEqual(cashback(20000, 'gold', True), 1000)


class Boundary(unittest.TestCase):
    def test_boundary_1(self):
        self.assertEqual(cashback(9999, 'platinum', True), 0)

    def test_boundary_2(self):
        self.assertEqual(cashback(10000, 'silver', False), 150)

    def test_boundary_3(self):
        self.assertEqual(cashback(10001, 'platinum', False), 400)

    def test_boundary_4(self):
        self.assertEqual(cashback(0, 'gold', False), 0)

    def test_boundary_5(self):  # ยังไม่ชนเพดาน
        self.assertEqual(cashback(499975, 'platinum', False), 19999)

    def test_boundary_6(self):  # พอดีเพดาน
        self.assertEqual(cashback(500000, 'platinum', False), 20000)

    def test_boundary_7(self):  # เกินเพดาน
        self.assertEqual(cashback(5000000, 'platinum', True), 20000)

    def test_boundary_8(self):  # เพดานหลังคูณ 2
        self.assertEqual(cashback(400000, 'platinum', True), 20000)
        self.assertEqual(cashback(200000, 'platinum', True), 16000)


class NoDrift(unittest.TestCase):
    def test_no_drift_1(self):  # 151.5 -> 152 (floor/banker's ได้ 151/152)
        self.assertEqual(cashback(10100, 'silver', False), 152)

    def test_no_drift_2(self):  # 250.5 -> 251
        self.assertEqual(cashback(10020, 'gold', False), 251)

    def test_no_drift_3(self):  # รวมก่อนปัด: 2*151.5=303 (ปัดก่อนคูณจะได้ 304)
        self.assertEqual(cashback(10100, 'silver', True), 303)

    def test_no_drift_4(self):  # 400.48 -> 400, 400.52 -> 401
        self.assertEqual(cashback(10012, 'platinum', False), 400)
        self.assertEqual(cashback(10013, 'platinum', False), 401)

    def test_no_drift_5(self):  # 252.5 -> 253 (banker's จะได้ 252)
        self.assertEqual(cashback(10100, 'gold', False), 253)


class Reject(unittest.TestCase):
    def bad(self, *a):
        with self.assertRaises(ValueError):
            cashback(*a)

    def test_reject_1(self):
        self.bad(-1, 'gold', False)

    def test_reject_2(self):
        self.bad(20000, 'bronze', False)

    def test_reject_3(self):
        self.bad(20000.0, 'gold', False)

    def test_reject_4(self):
        self.bad('20000', 'gold', False)

    def test_reject_5(self):
        self.bad(True, 'gold', False)

    def test_reject_6(self):
        self.bad(20000, 'gold', 1)

    def test_reject_7(self):
        self.bad(None, 'gold', False)

    def test_reject_8(self):
        self.bad(20000, None, False)

    def test_reject_9(self):
        self.bad(20000, 'Gold', False)

    def test_reject_10(self):
        self.bad(20000, 'gold', None)

    def test_reject_11(self):
        self.bad(20000, 'gold', 'true')

    def test_reject_12(self):
        self.bad(20000, 1, False)


if __name__ == "__main__":
    unittest.main()
