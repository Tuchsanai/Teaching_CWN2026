import unittest
from solve import late_fee


class TestSolve(unittest.TestCase):
    def test_normal_small_delay(self):
        # 10000 * 0.75% * 4 = 300
        self.assertEqual(late_fee(10000, 4), 300)

    def test_normal_ten_days(self):
        self.assertEqual(late_fee(20000, 10), 1500)

    def test_normal_zero_amount(self):
        self.assertEqual(late_fee(0, 100), 0)

    def test_edge_three_days_free(self):
        self.assertEqual(late_fee(10000, 3), 0)

    def test_edge_zero_days(self):
        self.assertEqual(late_fee(10000, 0), 0)

    def test_edge_cap_at_20_days(self):
        # 20 วัน = 15% พอดี
        self.assertEqual(late_fee(10000, 20), 1500)
        self.assertEqual(late_fee(10000, 19), 1425)

    def test_edge_cap_beyond(self):
        self.assertEqual(late_fee(10000, 21), 1500)
        self.assertEqual(late_fee(10000, 365), 1500)

    def test_rounding_half_up(self):
        # 66*75*4/10000 = 1.98 -> 2 ; 10*75*... ; 2*75*4/... = 0.06 -> 0
        self.assertEqual(late_fee(66, 4), 2)
        self.assertEqual(late_fee(2, 4), 0)
        # 200*0.0075*4 = 6.0 ; 134*0.0075*5=5.025 -> 5 ; 140*.0075*5=5.25->5; 100*.0075*... 
        self.assertEqual(late_fee(134, 5), 5)
        # พอดี .5: 200*75*... 200*75*d/10000=1.5d -> d=5 -> 7.5 -> 8
        self.assertEqual(late_fee(200, 5), 8)

    def test_result_is_int(self):
        self.assertIs(type(late_fee(12345, 7)), int)
        self.assertIs(type(late_fee(12345, 2)), int)

    def test_reject_amount(self):
        for bad in (-1, 100.0, True, "100", None):
            with self.assertRaises(ValueError):
                late_fee(bad, 5)

    def test_reject_days_late(self):
        for bad in (-1, 366, 5.0, True, "5", None):
            with self.assertRaises(ValueError):
                late_fee(1000, bad)


if __name__ == "__main__":
    unittest.main()
