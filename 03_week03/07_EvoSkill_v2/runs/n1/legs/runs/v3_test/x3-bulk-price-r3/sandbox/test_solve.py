import unittest

from solve import bulk_price


class Normal(unittest.TestCase):
    def test_normal_1(self):
        self.assertEqual(bulk_price(10000, 1, False), 10700)

    def test_normal_2(self):
        self.assertEqual(bulk_price(10000, 10, False), 103255)

    def test_normal_3(self):
        self.assertEqual(bulk_price(10000, 50, False), 494875)

    def test_normal_4(self):
        self.assertEqual(bulk_price(10000, 50, True), 482503)


class Boundary(unittest.TestCase):
    def test_boundary_1(self):  # 9 ถุง ยังไม่ลด
        self.assertEqual(bulk_price(10000, 9, False), 96300)

    def test_boundary_2(self):  # 10 ถุง ลด 3.5%
        self.assertEqual(bulk_price(10000, 10, False), 103255)

    def test_boundary_3(self):  # 11 ถุง: 110000*.965*1.07
        self.assertEqual(bulk_price(10000, 11, False), 113581)  # 113580.5

    def test_boundary_4(self):  # 49 ถุง ยังลด 3.5% (505949.5)
        self.assertEqual(bulk_price(10000, 49, False), 505950)

    def test_boundary_5(self):  # 50 ถุง ลด 7.5% ไม่ซ้อน
        self.assertEqual(bulk_price(10000, 50, False), 494875)

    def test_boundary_6(self):  # 51 ถุง: 510000*.925*1.07
        self.assertEqual(bulk_price(10000, 51, False), 504773)  # 504772.5

    def test_boundary_7(self):
        self.assertEqual(bulk_price(0, 1, False), 0)

    def test_boundary_8(self):
        self.assertEqual(bulk_price(10000, 1000, False), 9897500)


class NoDrift(unittest.TestCase):
    def test_no_drift_1(self):  # 53.5 -> 54
        self.assertEqual(bulk_price(50, 1, False), 54)

    def test_no_drift_2(self):  # 100673.625 -> 100674 (floor ได้ 100673)
        self.assertEqual(bulk_price(10000, 10, True), 100674)

    def test_no_drift_3(self):  # 10.3255 -> 10
        self.assertEqual(bulk_price(1, 10, False), 10)

    def test_no_drift_4(self):  # 7.49 -> 7
        self.assertEqual(bulk_price(7, 1, False), 7)


class Reject(unittest.TestCase):
    def test_reject_1(self):
        for args in [(-1, 1, False), (100, 0, False), (100, -1, False),
                     (100, 1001, False)]:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    bulk_price(*args)

    def test_reject_2(self):
        for args in [(100.0, 1, False), (100, 1.0, False), ('100', 1, False),
                     (100, '1', False), (None, 1, False), (100, None, False)]:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    bulk_price(*args)

    def test_reject_3(self):
        for args in [(True, 1, False), (100, True, False)]:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    bulk_price(*args)

    def test_reject_4(self):
        for c in [1, 0, 'true', None, 1.0]:
            with self.subTest(c=c):
                with self.assertRaises(ValueError):
                    bulk_price(100, 1, c)


if __name__ == "__main__":
    unittest.main()
