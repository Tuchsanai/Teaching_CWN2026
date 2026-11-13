import unittest
from solve import shipping_fee as f

class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(f(1000,0,False),4000)
        self.assertEqual(f(1001,0,False),8000)
        self.assertEqual(f(5000,100,False),8000)
        self.assertEqual(f(5001,101,False),int((8000+1.5)*1.2+0.5))
        self.assertEqual(f(30000,101,True),int((8000+37500)*1.8))
        self.assertEqual(f(1000,101,True),7200)
    def test_half(self):
        self.assertEqual(f(5001,0,False),8002)  # 8001.5 -> 8002
    def test_reject(self):
        for a in [(0,0,False),(30001,0,False),(1,-1,False),(1.0,0,False),("1",0,False),
                  (True,0,False),(1,True,False),(1,0.0,False),(1,0,1),(1,0,None),(None,0,False)]:
            with self.assertRaises(ValueError): f(*a)
unittest.main() if __name__=="__main__" else None
