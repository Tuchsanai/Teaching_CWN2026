import unittest
from solve import split_bill
class T(unittest.TestCase):
    def test_n(self):
        self.assertEqual(split_bill(1000,3,0),[334,333,333])
        self.assertEqual(split_bill(1000,2,10),[550,550])
        self.assertEqual(split_bill(0,3,0),[0,0,0])
    def test_round(self):
        self.assertEqual(split_bill(1050,1,5),[1103])  # 1102.5 -> 1103
        self.assertEqual(sum(split_bill(9999,7,13)),round(9999*1.13+1e-9))
    def test_reject(self):
        for a in [(-1,1,0),(1,0,0),(1,1,101),(1,1,-1),(1.0,1,0),("3",1,0),(True,1,0),(1,1,True),(1,None,0)]:
            with self.assertRaises(ValueError): split_bill(*a)
