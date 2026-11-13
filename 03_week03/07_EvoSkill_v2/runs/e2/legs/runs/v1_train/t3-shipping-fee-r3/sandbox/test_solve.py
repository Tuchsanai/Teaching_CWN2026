import unittest
from solve import shipping_fee as f
class T(unittest.TestCase):
    def test_ok(self):
        self.assertEqual(f(1000,0,False),4000)
        self.assertEqual(f(1001,0,False),8000)
        self.assertEqual(f(5000,100,False),8000)
        self.assertEqual(f(5001,101,False),int(-(-0//1))+ 9602 if False else 9602)
        self.assertEqual(f(30000,200,True),(8000+37500)*18//10)
        self.assertEqual(f(1,0,True),6000)
        self.assertEqual(f(5001,0,False),8002)  # 8001.5 -> half-up
    def test_bad(self):
        for a in [(0,1,False),(30001,1,False),(1.0,1,False),(True,1,False),("3",1,False),(5,-1,False),(5,"1",False),(5,True,False),(5,1,1),(5,1,None)]:
            with self.assertRaises(ValueError): f(*a)
