import unittest
from solve import late_fee


class TestLateFee(unittest.TestCase):
    def test_grace(self):
        self.assertEqual(late_fee(100000, 3), 0)
        self.assertEqual(late_fee(100000, 0), 0)

    def test_day4_counts_all_days(self):
        self.assertEqual(late_fee(100000, 4), 3000)

    def test_cap(self):
        self.assertEqual(late_fee(100000, 20), 15000)
        self.assertEqual(late_fee(100000, 365), 15000)

    def test_half_up(self):
        # 200*4*75/10000 = 6 ; 10*4*75/10000=0.3 -> 0 ; 70*4*75/10000=2.1
        self.assertEqual(late_fee(10, 4), 0)
        self.assertEqual(late_fee(200, 4), 6)
        # 50*7*75/10000 = 2.625 -> 3 ; 2*... half case: 100*... 
        self.assertEqual(late_fee(50, 7), 3)
        # exactly .5: amount=20, days=10 -> 20*750/10000=1.5 -> 2
        self.assertEqual(late_fee(20, 10), 2)

    def test_zero_amount(self):
        self.assertEqual(late_fee(0, 100), 0)

    def test_invalid(self):
        for a, d in [(-1, 5), (10, -1), (10, 366), (1.5, 5), (10, 5.0),
                     (True, 5), (10, True), ("10", 5), (None, 5)]:
            with self.assertRaises(ValueError):
                late_fee(a, d)


if __name__ == "__main__":
    unittest.main()
