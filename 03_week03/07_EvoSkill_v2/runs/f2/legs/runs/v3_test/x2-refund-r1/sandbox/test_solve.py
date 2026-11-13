import unittest
from solve import refund


class Normal(unittest.TestCase):
    def test_no_restock(self):
        self.assertEqual(refund(10000, 50, False), 5000)

    def test_restock(self):
        self.assertEqual(refund(10000, 50, True), 4375)

    def test_unused(self):
        self.assertEqual(refund(8000, 0, True), 7000)


class Boundary(unittest.TestCase):
    def test_80(self):
        self.assertEqual(refund(10000, 80, False), 2000)

    def test_81(self):
        self.assertEqual(refund(10000, 81, False), 0)

    def test_100_and_zero_paid(self):
        self.assertEqual(refund(10000, 100, True), 0)
        self.assertEqual(refund(0, 0, False), 0)


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        # 1*50/100 = 0.5 -> 1
        self.assertEqual(refund(1, 50, False), 1)
        # 10*(70/100)*(7/8) = 6.125 -> 6
        self.assertEqual(refund(10, 30, True), 6)
        # 4*(1/2)*(7/8)=1.75 -> 2 ; 1*7/8 -> 1
        self.assertEqual(refund(4, 50, True), 2)
        # 100*0.5*... 12*(50/100)*(7/8)=5.25 -> 5 ; 6*(1/2)*(7/8)=2.625->3
        self.assertEqual(refund(6, 50, True), 3)
        # exactly .5 after restock: 4*(1/1)... 4*7/8=3.5 -> 4
        self.assertEqual(refund(4, 0, True), 4)


class Reject(unittest.TestCase):
    def test_bad(self):
        for args in [(-1, 0, False), (10, -1, False), (10, 101, False),
                     (10.0, 0, False), ("3", 0, False), (True, 0, False),
                     (10, 5.0, False), (10, True, False),
                     (10, 5, 1), (10, 5, None), (10, "5", True)]:
            with self.assertRaises(ValueError, msg=str(args)):
                refund(*args)


if __name__ == "__main__":
    unittest.main()
