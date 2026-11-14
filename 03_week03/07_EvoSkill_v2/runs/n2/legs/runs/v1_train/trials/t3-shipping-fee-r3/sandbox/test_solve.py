import unittest
from solve import shipping_fee as f

class T(unittest.TestCase):
    def test_ok(self):
        self.assertEqual(f(3000,150,False),9600)
        self.assertEqual(f(5106,150,True),14686)
        self.assertEqual(f(5217,50,True),12488)
        self.assertEqual(f(1001,10,False),8000)
        self.assertEqual(f(1000,10,False),4000)
        self.assertEqual(f(30000,100,False),45500)
        self.assertEqual(f(5000,0,False),0)
    def test_reject(self):
        for a in [(0,1,False),(30001,1,False),(1.0,1,False),(True,1,False),(5,-1,False),(5,1,1),(20001,1,True)]:
            with self.assertRaises(ValueError): f(*a)
unittest.main() if __name__=="__main__" else None
