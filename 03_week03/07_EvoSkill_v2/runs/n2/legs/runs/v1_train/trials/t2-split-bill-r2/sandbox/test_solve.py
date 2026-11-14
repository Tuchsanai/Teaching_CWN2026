import unittest
from solve import split_bill as s
class T(unittest.TestCase):
    def test_all(self):
        self.assertEqual(s(10000,3,0),[3334,3333,3333])
        self.assertEqual(s(10000,7,10),[1572]*3+[1571]*4)
        self.assertEqual(s(2,3,0),[1,1,0])
        self.assertEqual(s(0,2,50),[0,0])
        for a in [(-1,1,0),(1,0,0),(1,1,101),(1,1,-1),(1.0,1,0),(1,True,0),("1",1,0)]:
            with self.assertRaises(ValueError): s(*a)
unittest.main() if __name__=="__main__" else None
