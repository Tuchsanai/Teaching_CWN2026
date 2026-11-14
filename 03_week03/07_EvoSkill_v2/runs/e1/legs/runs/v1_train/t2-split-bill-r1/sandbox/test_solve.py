import unittest
from solve import split_bill

class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(split_bill(10000, 3, 10), [3667, 3667, 3666])
        self.assertEqual(split_bill(0, 2, 0), [0, 0])
        self.assertEqual(split_bill(100, 1, 0), [100])
    def test_halfup(self):
        self.assertEqual(split_bill(5, 1, 10), [6])   # 5.5 -> 6
        self.assertEqual(split_bill(4, 1, 10), [4])   # 4.4 -> 4
        r = split_bill(12345, 7, 15)
        self.assertEqual(sum(r), 14197); self.assertTrue(all(type(x) is int for x in r))
    def test_reject(self):
        for a in [(-1,1,0),(1,0,0),(1,1,-1),(1,1,101),(1.0,1,0),(1,"2",0),(True,1,0),(1,1,None),(1,True,0)]:
            with self.assertRaises(ValueError): split_bill(*a)

if __name__ == "__main__":
    unittest.main()
