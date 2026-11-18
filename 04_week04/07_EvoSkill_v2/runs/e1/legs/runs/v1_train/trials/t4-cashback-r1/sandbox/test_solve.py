import unittest
from solve import cashback as c

class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(c(100000,"silver",False),1500)
        self.assertEqual(c(100000,"gold",False),2500)
        self.assertEqual(c(100000,"platinum",False),4000)
        self.assertEqual(c(100000,"gold",True),5000)
        self.assertEqual(c(100000,"silver",True),1500)
    def test_boundary(self):
        self.assertEqual(c(9999,"platinum",True),0)
        self.assertEqual(c(10000,"platinum",False),400)
        self.assertEqual(c(0,"gold",False),0)
        self.assertEqual(c(500000,"platinum",False),20000)
        self.assertEqual(c(500001,"platinum",False),20000)
        self.assertEqual(c(499999,"platinum",False),19999)
        self.assertEqual(c(10000000,"gold",True),20000)
    def test_floor(self):
        self.assertEqual(c(10033,"silver",False),150)   # 150.495
        self.assertEqual(c(10100,"silver",False),151)   # 151.5
        self.assertEqual(c(10020,"gold",False),250)     # 250.5
    def test_reject(self):
        for args in [(-1,"gold",False),(1.0,"gold",False),("1","gold",False),(True,"gold",False),(None,"gold",False),
                     (10000,"bronze",False),(10000,None,False),(10000,"Gold",False),(10000,"gold",1),(10000,"gold",None),
                     (5,"x",False),(5,"gold","no")]:
            with self.assertRaises(ValueError): c(*args)
unittest.main() if __name__=="__main__" else None
