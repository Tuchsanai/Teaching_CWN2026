import unittest
from solve import split_bill as s
class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(s(10000,3,0),[3334,3333,3333])
        self.assertEqual(s(10000,4,10),[2750]*4)
        self.assertEqual(s(0,2,50),[0,0])
    def test_boundary(self):
        self.assertEqual(s(1,3,0),[1,0,0])
        self.assertEqual(s(100,1,100),[200])
        self.assertEqual(len(s(5,1000,0)),1000)
    def test_nodrift(self):
        self.assertEqual(s(10,1,5),[11])   # 10.5 -> 11
        self.assertEqual(s(1,1,50),[2])    # 1.5 -> 2
        self.assertEqual(s(9,1,5),[9])     # 9.45 -> 9
        self.assertEqual(sum(s(99991,7,7)),(99991*107*2+100)//200)
    def test_reject(self):
        for a in [(-1,1,0),(1,0,0),(1,1,-1),(1,1,101),(1.0,1,0),(1,1.0,0),(1,1,0.0),('1',1,0),(True,1,0),(1,True,0),(1,1,True),(None,1,0)]:
            with self.assertRaises(ValueError): s(*a)
unittest.main() if __name__=="__main__" else None
