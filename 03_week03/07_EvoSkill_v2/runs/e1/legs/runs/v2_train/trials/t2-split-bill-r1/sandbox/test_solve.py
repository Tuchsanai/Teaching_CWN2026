import unittest
from solve import split_bill as f
class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(f(10000,3,0),[3334,3333,3333])
        self.assertEqual(f(0,2,10),[0,0])
        self.assertEqual(f(10000,4,10),[2750]*4)
    def test_boundary(self):
        self.assertEqual(f(1,1,0),[1]); self.assertEqual(f(100,1,100),[200])
    def test_round(self):
        self.assertEqual(f(1,1,50),[2])  # 1.5 -> 2
        self.assertEqual(f(1,3,0),[1,0,0])
        self.assertEqual(sum(f(12345,7,13)),(12345*113*2+100)//200)
        self.assertEqual(len(f(5,1000,0)),1000)
    def test_reject(self):
        for a in [(-1,1,0),(1,0,0),(1,1,-1),(1,1,101),(1.0,1,0),(1,1.0,0),(1,1,0.0),("1",1,0),(True,1,0),(1,True,0),(1,1,True),(None,1,0)]:
            with self.assertRaises(ValueError): f(*a)
unittest.main() if __name__=="__main__" else None
