import unittest
from solve import split_bill

class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(split_bill(10000, 3, 10), [3667, 3667, 3666])
        self.assertEqual(split_bill(0, 2, 0), [0, 0])
        r = split_bill(100, 1, 0); self.assertEqual(r, [100]); self.assertIs(type(r[0]), int)
    def test_halfup(self):
        self.assertEqual(split_bill(5, 1, 10), [6])   # 5.5 -> 6
        self.assertEqual(split_bill(1, 1, 49), [1])   # 1.49 -> 1
        self.assertEqual(sum(split_bill(9999, 7, 15)), 11499)  # 11498.85->11499
    def test_reject(self):
        for a in [(-1,1,0),(1,0,0),(1,1,-1),(1,1,101),(1.0,1,0),(1,"2",0),(True,1,0),(1,1,None),(1,1,5.0)]:
            with self.assertRaises(ValueError): split_bill(*a)
unittest.main() if __name__=="__main__" else None
