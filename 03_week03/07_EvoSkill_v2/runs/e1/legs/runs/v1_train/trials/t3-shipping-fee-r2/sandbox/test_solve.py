import unittest
from solve import shipping_fee as f

class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(f(500, 10, False), 4000)
        self.assertEqual(f(3000, 10, False), 8000)
        self.assertEqual(f(10000, 10, False), 8000 + 7500)
        self.assertEqual(f(1000, 101, True), 7200)
    def test_boundary(self):
        self.assertEqual(f(1000, 5, False), 4000)
        self.assertEqual(f(1001, 5, False), 8000)
        self.assertEqual(f(5000, 5, False), 8000)
        self.assertEqual(f(5001, 5, False), 8002)  # 8001.5 half-up
        self.assertEqual(f(1000, 100, False), 4000)
        self.assertEqual(f(1000, 100.5, False), 4800)
        self.assertEqual(f(20000, 1, True), (8000+22500)*3//2)
        self.assertEqual(f(30000, 1, False), 8000+37500)
        self.assertEqual(f(1000, 0, True), 0)
    def test_round(self):
        self.assertEqual(f(5001, 101, False), 9602)  # 9601.8
        self.assertEqual(f(5003, 5, True), 12007)   # 12006.75
    def test_reject(self):
        for a in [(0,1,False),(30001,1,False),(1.0,1,False),("1",1,False),(True,1,False),
                  (1,-1,False),(1,"1",False),(1,True,False),(1,1,1),(1,1,None),(20001,1,True),(1,float("nan"),False)]:
            with self.assertRaises(ValueError): f(*a)
unittest.main() if __name__=="__main__" else None
