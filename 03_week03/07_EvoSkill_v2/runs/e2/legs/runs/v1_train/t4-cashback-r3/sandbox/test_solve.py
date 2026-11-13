import unittest
from solve import cashback as c

class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(c(20000,"silver",False),300)
        self.assertEqual(c(20000,"gold",True),1000)
        self.assertEqual(c(50000,"platinum",False),2000)
    def test_boundary(self):
        self.assertEqual(c(9999,"gold",True),0)
        self.assertEqual(c(10000,"silver",False),150)
        self.assertEqual(c(0,"gold",False),0)
        self.assertEqual(c(500000,"platinum",False),20000)
        self.assertEqual(c(1000000,"platinum",True),20000)
    def test_round(self):
        self.assertEqual(c(10010,"silver",False),150)  # 150.15
        self.assertEqual(c(10030,"silver",False),150)  # 150.45
        self.assertEqual(c(10050,"silver",False),151)  # 150.75
        self.assertEqual(c(10100,"gold",False),253)    # 252.5 -> 253
    def test_reject(self):
        for a in (-1,1000.0,"3",True,None):
            with self.assertRaises(ValueError): c(a,"gold",False)
        for t in ("bronze",None,["gold"],1):
            with self.assertRaises(ValueError): c(20000,t,False)
        for b in (1,0,None,"True"):
            with self.assertRaises(ValueError): c(20000,"gold",b)
        with self.assertRaises(ValueError): c(-5,"gold",False)
        with self.assertRaises(ValueError): c(50,"x",False)
unittest.main() if __name__=="__main__" else None
