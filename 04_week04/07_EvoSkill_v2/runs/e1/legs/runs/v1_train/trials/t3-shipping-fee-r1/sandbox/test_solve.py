import unittest
from solve import shipping_fee as f

class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(f(500, 10, False), 4000)
        self.assertEqual(f(3000, 10, False), 8000)
        self.assertEqual(f(10000, 10, False), 8000 + 7500)
        self.assertEqual(f(3000, 150, True), 14400)
    def test_boundary(self):
        self.assertEqual(f(1000, 1, False), 4000)
        self.assertEqual(f(1001, 1, False), 8000)
        self.assertEqual(f(5000, 1, False), 8000)
        self.assertEqual(f(5001, 1, False), 8002)  # 1.5 -> half-up 2
        self.assertEqual(f(1, 100, False), 4000)
        self.assertEqual(f(1, 101, False), 4800)
        self.assertEqual(f(1, 100.5, False), 4800)
        self.assertEqual(f(20000, 1, True), 8000+22500 and int((8000+22500)*1.5))
        self.assertEqual(f(30000, 1, False), 8000+37500)
        self.assertEqual(f(500, 0, True), 0)
    def test_drift(self):
        # 8000+1500*1/1000=8001.5 *1.5=12002.25 -> 12002
        self.assertEqual(f(5001, 1, True), 12002)
        # 8001.5*1.2=9601.8 -> 9602
        self.assertEqual(f(5001, 101, False), 9602)
    def test_reject(self):
        bad = [(0,1,False),(30001,1,False),(-1,1,False),(1.0,1,False),("1",1,False),(True,1,False),(None,1,False),
               (1,-1,False),(1,"1",False),(1,None,False),(1,True,False),(1,float("nan"),False),
               (1,1,1),(1,1,None),(1,1,"x"),(20001,1,True),(20001,0,True)]
        for a in bad:
            with self.assertRaises(ValueError, msg=a):
                f(*a)
if __name__ == "__main__":
    unittest.main()
