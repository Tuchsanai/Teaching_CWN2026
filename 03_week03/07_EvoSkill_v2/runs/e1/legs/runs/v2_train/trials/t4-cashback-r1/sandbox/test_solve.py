import unittest
from solve import cashback as c
class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(c(20000,"silver",False),300)
        self.assertEqual(c(20000,"gold",False),500)
        self.assertEqual(c(20000,"platinum",False),800)
        self.assertEqual(c(20000,"gold",True),1000)
        self.assertEqual(c(20000,"silver",True),300)
    def test_boundary(self):
        self.assertEqual(c(9999,"platinum",True),0)
        self.assertEqual(c(10000,"silver",False),150)
        self.assertEqual(c(0,"gold",False),0)
        self.assertEqual(c(500000,"platinum",False),20000)
        self.assertEqual(c(250000,"platinum",True),20000)
    def test_floor(self):
        self.assertEqual(c(10001,"silver",False),150)   # 150.015
        self.assertEqual(c(10039,"gold",False),250)     # 250.975
        self.assertEqual(c(10039,"gold",True),501)      # 501.95
    def test_reject(self):
        for a in [(-1,"gold",False),(1.0,"gold",False),("1","gold",False),(True,"gold",False),(None,"gold",False),
                  (20000,"bronze",False),(20000,None,False),(20000,"gold",1),(20000,"gold",None),(5,"x",False),(5,"gold","y")]:
            with self.assertRaises(ValueError): c(*a)
unittest.main() if __name__=="__main__" else None
