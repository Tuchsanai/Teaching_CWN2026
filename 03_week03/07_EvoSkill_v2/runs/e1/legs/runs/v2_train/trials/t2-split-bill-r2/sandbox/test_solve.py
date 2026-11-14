import unittest
from solve import split_bill as f
class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(f(10000,3,0),[3334,3333,3333])
        self.assertEqual(f(0,2,10),[0,0])
        self.assertEqual(f(1000,1,10),[1100])
    def test_half(self):
        self.assertEqual(f(5,1,10),[6])  # 5.5 -> 6
        self.assertEqual(f(1,1,50),[2])  # 1.5 -> 2
        self.assertEqual(f(1,1,49),[1])
    def test_sum(self):
        r=f(99999,7,13); self.assertEqual(len(r),7); self.assertEqual(sum(r),112999)
        self.assertEqual(len(f(10,50,0)),50)
    def test_reject(self):
        for a in [(-1,1,0),(1,0,0),(1,1,-1),(1,1,101),(1.0,1,0),(1,1.0,0),(1,1,0.0),('1',1,0),(True,1,0),(1,True,0),(1,1,True),(None,1,0)]:
            with self.assertRaises(ValueError): f(*a)
unittest.main() if __name__=='__main__' else None
