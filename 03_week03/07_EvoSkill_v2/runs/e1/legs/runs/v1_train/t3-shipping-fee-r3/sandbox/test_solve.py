import unittest
from solve import shipping_fee as f

class T(unittest.TestCase):
    def test_values(self):
        self.assertEqual(f(1000, 10, False), 4000)
        self.assertEqual(f(1001, 10, False), 8000)
        self.assertEqual(f(5000, 100, False), 8000)
        self.assertEqual(f(5001, 101, False), 9602)  # 8001.5*1.2=9601.8
        self.assertEqual(f(6000, 10, False), 9500)
        self.assertEqual(f(1000, 101, True), 7200)
        self.assertEqual(f(20000, 5, True), int(f(20000, 5, False)*1.5))
        self.assertEqual(f(500, 0, True), 0)
        self.assertIs(type(f(5001, 5, True)), int)
    def test_reject(self):
        for a in [(0,1,False),(30001,1,False),(20001,1,True),(1.0,1,False),("1",1,False),
                  (True,1,False),(100,-1,False),(100,1.5,False),(100,1,1),(100,1,None)]:
            with self.assertRaises(ValueError): f(*a)
unittest.main() if __name__=="__main__" else None
