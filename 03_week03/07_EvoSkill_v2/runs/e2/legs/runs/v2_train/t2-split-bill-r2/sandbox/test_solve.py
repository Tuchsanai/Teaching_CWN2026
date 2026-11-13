import unittest
from solve import split_bill as f
class T(unittest.TestCase):
    def test_ok(self):
        self.assertEqual(f(1000,3,0),[334,333,333])
        self.assertEqual(f(1000,1,10),[1100])
        self.assertEqual(f(0,3,50),[0,0,0])
        self.assertEqual(f(1005,2,10),[553,553])  # 1105.5 -> 1106
        self.assertEqual(f(10,3,0),[4,3,3])
        self.assertEqual(sum(f(9999,7,13)),1130 and 11299)  # 9999*1.13=11298.87
    def test_bad(self):
        for a in [(-1,1,0),(1,0,0),(1,1,-1),(1,1,101),(1.0,1,0),("3",1,0),(True,1,0),(1,1,True),(None,1,0),(1,2.0,0),(1,1,float('nan'))]:
            with self.assertRaises(ValueError): f(*a)
unittest.main() if __name__=="__main__" else None
