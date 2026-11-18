import unittest
from solve import cashback as c

class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(c(20000,"gold",False),500)
        self.assertEqual(c(20000,"platinum",True),1600)
        self.assertEqual(c(20000,"gold",True),1000)
        self.assertEqual(c(20000,"silver",True),300)
    def test_boundary(self):
        self.assertEqual(c(9999,"gold",False),0)
        self.assertEqual(c(10000,"gold",False),250)
        self.assertEqual(c(0,"gold",False),0)
        self.assertEqual(c(500000,"platinum",True),20000)
        self.assertEqual(c(250000,"platinum",False),10000)
    def test_floor(self):
        self.assertEqual(c(10033,"silver",False),150)   # 150.495
        self.assertEqual(c(10001,"gold",False),250)     # 250.025
        self.assertEqual(c(10039,"platinum",True),803)  # 803.12
    def test_reject(self):
        for a in [(-1,"gold",False),(1.0,"gold",False),("3","gold",False),(True,"gold",False),(None,"gold",False),
                  (20000,"bronze",False),(20000,None,False),(5,"x",False),(20000,"gold",1),(20000,"gold",None),(20000.0,"gold",True)]:
            with self.assertRaises(ValueError): c(*a)
unittest.main() if __name__=="__main__" else None
