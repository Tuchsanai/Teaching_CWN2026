import unittest
from solve import shipping_fee as f

class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(f(500, 10, False), 4000)
        self.assertEqual(f(3000, 10, False), 8000)
        self.assertEqual(f(10000, 10, False), 15500)
        self.assertEqual(f(3000, 150, True), 14400)
    def test_boundary(self):
        self.assertEqual(f(1000, 100, False), 4000)
        self.assertEqual(f(1001, 100, False), 8000)
        self.assertEqual(f(5000, 100, False), 8000)
        self.assertEqual(f(5001, 100, False), 8002)  # 8000+1.5 -> half-up
        self.assertEqual(f(1000, 100.5, False), 4800)
        self.assertEqual(f(30000, 0, False), 45500)
    def test_reject(self):
        for a in [(0,1,False),(30001,1,False),(-1,1,False),(1.0,1,False),("3",1,False),(True,1,False),
                  (1,-1,False),(1,"a",False),(1,None,False),(1,float("nan"),False),(1,1,1),(1,1,None)]:
            with self.assertRaises(ValueError): f(*a)
unittest.main() if __name__ == "__main__" else None
