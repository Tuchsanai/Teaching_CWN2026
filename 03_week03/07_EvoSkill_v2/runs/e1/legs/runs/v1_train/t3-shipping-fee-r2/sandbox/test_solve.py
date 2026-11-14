import unittest
from solve import shipping_fee as f

class T(unittest.TestCase):
    def test_vals(self):
        self.assertEqual(f(1000, 10, False), 4000)
        self.assertEqual(f(1001, 10, False), 8000)
        self.assertEqual(f(5000, 10, False), 8000)
        self.assertEqual(f(5001, 10, False), 8002)  # 8001.5 -> half-up
        self.assertEqual(f(10000, 100, False), 15500)
        self.assertEqual(f(10000, 101, False), 18600)
        self.assertEqual(f(10000, 101, True), 27900)
        self.assertEqual(f(500, 5, True), 6000)
        self.assertEqual(f(20000, 5, True), 45750)
    def test_pickup(self):
        self.assertEqual(f(500, 0, False), 0)
    def test_reject(self):
        for a in [(0,1,False),(30001,1,False),(20001,1,True),(1.0,1,False),("2",1,False),
                  (True,1,False),(100,-1,False),(100,"1",False),(100,1,1),(100,1,None),(100,True,False)]:
            with self.assertRaises(ValueError): f(*a)
        self.assertEqual(type(f(100,1,False)), int)
