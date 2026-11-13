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
        self.assertEqual(cashback(0, 'gold', True), 0)


class Boundary(unittest.TestCase):
    def test_boundary_1(self):
        self.assertEqual(cashback(9999, 'platinum', True), 0)

    def test_boundary_2(self):
        self.assertEqual(cashback(10000, 'silver', False), 150)

    def test_boundary_3(self):
        self.assertEqual(cashback(10001, 'platinum', False), 400)

    def test_boundary_4(self):  # ยังไม่ชนเพดาน
        self.assertEqual(cashback(499987, 'platinum', False), 19999)

    def test_boundary_5(self):  # พอดีเพดาน
        self.assertEqual(cashback(500000, 'platinum', False), 20000)

    def test_boundary_6(self):  # เกินเพดาน
        self.assertEqual(cashback(500001, 'platinum', False), 20000)
        self.assertEqual(cashback(5000000, 'platinum', True), 20000)

    def test_boundary_7(self):  # เพดานกรณีเดือนเกิด
        self.assertEqual(cashback(249990, 'platinum', True), 19999)
        self.assertEqual(cashback(250000, 'platinum', True), 20000)
        self.assertEqual(cashback(250010, 'platinum', True), 20000)


class NoDrift(unittest.TestCase):
    def test_no_drift_1(self):  # 151.5 -> 152
        self.assertEqual(cashback(10100, 'silver', False), 152)

    def test_no_drift_2(self):  # 250.5 -> 251
        self.assertEqual(cashback(10020, 'gold', False), 251)

    def test_no_drift_3(self):  # 400.52 -> 401
        self.assertEqual(cashback(10013, 'platinum', False), 401)

    def test_no_drift_4(self):  # 2x รวมก่อนปัด: 10010*0.015*2=300.3 -> 300 (ปัดก่อนคูณ: 150*2=300 / 301.. )
        self.assertEqual(cashback(10030, 'silver', True), 301)  # 300.9 ; ปัดก่อนคูณ 150*2=300


class Reject(unittest.TestCase):
    def test_reject_amount(self):
        for bad in (-1, 20000.0, '20000', True, None):
            with self.assertRaises(ValueError):
                cashback(bad, 'gold', False)

    def test_reject_tier(self):
        for bad in ('bronze', 'Gold', None, 1, ''):
            with self.assertRaises(ValueError):
                cashback(20000, bad, False)

    def test_reject_birthday(self):
        for bad in (1, 0, 'true', None):
            with self.assertRaises(ValueError):
                cashback(20000, 'gold', bad)


if __name__ == "__main__":
    unittest.main()
