import unittest
from solve import late_fee

class Normal(unittest.TestCase):
    def test_1(self): self.assertEqual(late_fee(10000, 4), 300)
    def test_2(self): self.assertEqual(late_fee(10000, 10), 750)
    def test_3(self): self.assertEqual(late_fee(0, 30), 0)

class Boundary(unittest.TestCase):
    def test_3_days(self): self.assertEqual(late_fee(10000, 3), 0)
    def test_0_days(self): self.assertEqual(late_fee(10000, 0), 0)
    def test_cap_at(self): self.assertEqual(late_fee(10000, 20), 1500)
    def test_below_cap(self): self.assertEqual(late_fee(10000, 19), 1425)
    def test_over_cap(self): self.assertEqual(late_fee(10000, 21), 1500)
    def test_max(self): self.assertEqual(late_fee(10000, 365), 1500)

class NoDrift(unittest.TestCase):
    def test_half_up(self): self.assertEqual(late_fee(200, 5), 8)   # 7.5
    def test_small(self): self.assertEqual(late_fee(10, 10), 1)     # 0.75
    def test_tiny(self): self.assertEqual(late_fee(2, 4), 0)        # 0.06

class Reject(unittest.TestCase):
    def test_float(self):
        with self.assertRaises(ValueError): late_fee(100.0, 5)
    def test_str(self):
        with self.assertRaises(ValueError): late_fee(100, "5")
    def test_bool(self):
        with self.assertRaises(ValueError): late_fee(100, True)
    def test_neg(self):
        with self.assertRaises(ValueError): late_fee(-1, 5)
    def test_days_range(self):
        with self.assertRaises(ValueError): late_fee(100, 366)
        with self.assertRaises(ValueError): late_fee(100, -1)
    def test_none(self):
        with self.assertRaises(ValueError): late_fee(None, 5)

if __name__ == "__main__":
    unittest.main()
