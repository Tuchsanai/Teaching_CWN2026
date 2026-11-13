import unittest
from solve import refund


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(refund(10000, 50, False), 5000)
        self.assertEqual(refund(10000, 50, True), 4375)
        self.assertEqual(refund(10000, 0, False), 10000)

    def test_boundary(self):
        self.assertEqual(refund(10000, 80, False), 2000)
        self.assertEqual(refund(10000, 81, False), 0)
        self.assertEqual(refund(0, 0, True), 0)
        self.assertEqual(refund(10000, 100, True), 0)

    def test_half_up(self):
        # 1*(50/100)=0.5 -> 1 ; 1*0.5*7/8=0.4375 -> 0 ; 4*0.9*... 
        self.assertEqual(refund(1, 50, False), 1)
        self.assertEqual(refund(1, 50, True), 0)
        # 20*80/100*7/8 = 14 ; 30*70/100*7/8=18.375 -> 18 ; 12*... 
        self.assertEqual(refund(30, 70, True), 8)
        # 4*(87.5/100)? paid=1,used=0,restock -> 0.875 -> 1
        self.assertEqual(refund(1, 0, True), 1)
        # exactly .5: paid=4, used 0, restock => 3.5 -> 4
        self.assertEqual(refund(4, 0, True), 4)

    def test_reject(self):
        for a in [(-1, 0, False), (1.0, 0, False), ("1", 0, False), (True, 0, False),
                  (None, 0, False), (1, -1, False), (1, 101, False), (1, 5.0, False),
                  (1, True, False), (1, 0, 1), (1, 0, None), (1, [], False)]:
            with self.assertRaises(ValueError):
                refund(*a)


if __name__ == "__main__":
    unittest.main()
