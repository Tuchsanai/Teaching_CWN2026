import unittest
from solve import split_bill

class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(split_bill(10000, 4, 0), [2500]*4)
        self.assertEqual(split_bill(10000, 3, 0), [3334, 3333, 3333])
        self.assertEqual(split_bill(10000, 2, 10), [5500, 5500])
    def test_boundary(self):
        self.assertEqual(split_bill(0, 3, 0), [0, 0, 0])
        self.assertEqual(split_bill(1, 1, 100), [2])
        self.assertEqual(split_bill(5, 7, 0), [1]*5 + [0]*2)
        self.assertEqual(len(split_bill(100, 1000, 0)), 1000)
    def test_rounding(self):
        # 10*105/100 = 10.5 -> 11 (half-up)
        self.assertEqual(sum(split_bill(10, 1, 5)), 11)
        # 1*150/100=1.5 -> 2
        self.assertEqual(split_bill(1, 1, 50), [2])
        # 1*149/100=1.49 -> 1
        self.assertEqual(split_bill(1, 1, 49), [1])
    def test_reject(self):
        for args in [(-1,1,0),(100,0,0),(100,-1,0),(100,1,-1),(100,1,101),
                     (100.0,1,0),(100,1.0,0),(100,1,10.0),("100",1,0),
                     (100,"1",0),(True,1,0),(100,True,0),(100,1,True),
                     (None,1,0),(100,None,0),(100,1,None)]:
            with self.assertRaises(ValueError, msg=str(args)):
                split_bill(*args)
if __name__ == "__main__":
    unittest.main()
