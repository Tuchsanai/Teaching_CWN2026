import unittest
from solve import shipping_fee as f
class T(unittest.TestCase):
    def test_n(self):
        self.assertEqual(f(500,10,False),4000)
        self.assertEqual(f(3000,10,False),8000)
        self.assertEqual(f(10000,10,False),15500)
        self.assertEqual(f(10000,101,True),15500*18//10)
    def test_b(self):
        self.assertEqual(f(1000,100,False),4000)
        self.assertEqual(f(1001,100,False),8000)
        self.assertEqual(f(5000,101,False),9600)
        self.assertEqual(f(5001,0,False),8002)  # 8001.5 half-up
        self.assertEqual(f(1,0,True),6000)
        self.assertEqual(f(30000,0,False),8000+37500)
    def test_r(self):
        for a in [(0,1,False),(30001,1,False),(1.0,1,False),("1",1,False),(True,1,False),(5,-1,False),(5,1.0,False),(5,1,1),(5,1,None)]:
            with self.assertRaises(ValueError): f(*a)
unittest.main() if __name__=="__main__" else None
