import unittest
from solve import split_bill

class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(split_bill(1000, 3, 10), [367, 367, 366])
        self.assertEqual(split_bill(1000, 4, 0), [250]*4)
        self.assertEqual(split_bill(0, 2, 50), [0, 0])
    def test_boundary(self):
        self.assertEqual(split_bill(100, 1, 100), [200])
        self.assertEqual(sum(split_bill(1, 5, 0)), 1)
    def test_rounding(self):
        # 10*105/100=10.5 -> 11 (half-up)
        self.assertEqual(split_bill(10, 1, 5), [11])
    def test_reject(self):
        for a in [(-1,1,0),(1,0,0),(1,1,-1),(1,1,101),(1.0,1,0),("3",1,0),(True,1,0),(1,1,True),(None,1,0),(1,1.0,0)]:
            with self.assertRaises(ValueError): split_bill(*a)

unittest.main() if __name__ == "__main__" else None
