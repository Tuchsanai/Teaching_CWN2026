import unittest
from solve import split_bill as s
class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(s(10000,3,0),[3334,3333,3333])
        self.assertEqual(s(10000,4,10),[2750]*4)
        self.assertEqual(s(0,3,50),[0,0,0])
    def test_half(self):
        self.assertEqual(s(1,1,50),[2])   # 1.5 -> 2
        self.assertEqual(s(1,2,50),[1,1])
        self.assertEqual(s(5,1,10),[6])   # 5.5 -> 6
        self.assertEqual(s(1,1,49),[1])   # 1.49 -> 1
    def test_sum(self):
        r=s(99999,7,13); self.assertEqual(len(r),7); self.assertEqual(sum(r),(99999*113*2+100)//200)
        self.assertEqual(len(s(100,1000,0)),1000)
    def test_reject(self):
        for a in [(-1,1,0),(1,0,0),(1,1,-1),(1,1,101),(1.0,1,0),(1,1.0,0),(1,1,0.0),('1',1,0),(True,1,0),(1,True,0),(1,1,True),(None,1,0)]:
            with self.assertRaises(ValueError): s(*a)
unittest.main() if __name__=='__main__' else None
