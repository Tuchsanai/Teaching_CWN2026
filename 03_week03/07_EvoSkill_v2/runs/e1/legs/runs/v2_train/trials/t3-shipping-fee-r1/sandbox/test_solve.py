import unittest
from solve import shipping_fee as f
class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(f(500,10,False),4000)
        self.assertEqual(f(3000,10,False),8000)
        self.assertEqual(f(10000,10,False),8000+7500)
        self.assertEqual(f(10000,101,True),int(15500*1.2*1.5))
    def test_boundary(self):
        self.assertEqual(f(1000,1,False),4000); self.assertEqual(f(1001,1,False),8000)
        self.assertEqual(f(5000,1,False),8000); self.assertEqual(f(5001,1,False),8002)
        self.assertEqual(f(1000,100,False),4000); self.assertEqual(f(1000,101,False),4800)
        self.assertEqual(f(20000,1,True),int((8000+22500)*1.5))
        self.assertEqual(f(30000,1,False),8000+37500)
        self.assertEqual(f(1,0,True),0)
    def test_round(self):
        self.assertEqual(f(5001,1,False),8002)  # 8001.5 -> 8002
        self.assertEqual(f(5003,1,True),12007)  # 12006.75
    def test_reject(self):
        for a in [(0,1,False),(30001,1,False),(1.0,1,False),(True,1,False),("3",1,False),(5,-1,False),(5,1.5,False),(5,1.0,False),(5,1,1),(5,1,None),(20001,1,True),(None,1,False)]:
            with self.assertRaises(ValueError): f(*a)
unittest.main() if __name__=="__main__" else None
