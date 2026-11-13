import unittest
from solve import late_fee


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(late_fee(100000, 4), 3000)
        self.assertEqual(late_fee(100000, 10), 7500)

    def test_boundary(self):
        self.assertEqual(late_fee(100000, 3), 0)
        self.assertEqual(late_fee(100000, 0), 0)
        self.assertEqual(late_fee(100000, 20), 15000)
        self.assertEqual(late_fee(100000, 365), 15000)
        self.assertEqual(late_fee(0, 10), 0)

    def test_rounding(self):
        # 10 * 4 * 0.0075 = 0.3 -> 0 ; 70*4*.0075=2.1 -> 2 ; 100*5*.0075=3.75 -> 4
        self.assertEqual(late_fee(70, 4), 2)
        self.assertEqual(late_fee(100, 5), 4)
        # exactly .5: 200*... amount=2, days=... 2*0.15=0.3; use 50*... 10*.0075*... 
        # amount=200,days=5 -> 7.5 -> 8
        self.assertEqual(late_fee(200, 5), 8)
        # cap half: amount=10, 15% =1.5 -> 2
        self.assertEqual(late_fee(10, 100), 2)

    def test_reject(self):
        for a, d in [(-1, 5), (1, -1), (1, 366), (1.0, 5), (1, 5.0), ("1", 5),
                     (1, "5"), (True, 5), (1, True), (None, 5), (1, None), ([], 5)]:
            with self.assertRaises(ValueError):
                late_fee(a, d)


if __name__ == "__main__":
    unittest.main()
