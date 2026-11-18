import unittest
from solve import cashback as c

class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(c(100000,"silver",False),1500)
        self.assertEqual(c(100000,"gold",False),2500)
        self.assertEqual(c(100000,"platinum",False),4000)
        self.assertEqual(c(100000,"gold",True),5000)
        self.assertEqual(c(100000,"platinum",True),8000)
        self.assertEqual(c(100000,"silver",True),1500)
    def test_boundary(self):
        self.assertEqual(c(9999,"platinum",True),0)
        self.assertEqual(c(10000,"platinum",False),400)
        self.assertEqual(c(0,"gold",False),0)
        self.assertEqual(c(500000,"platinum",False),20000)
        self.assertEqual(c(500001,"platinum",False),20000)
        self.assertEqual(c(499999,"platinum",False),19999)
        self.assertEqual(c(10000000,"platinum",True),20000)
    def test_floor(self):
        self.assertEqual(c(10001,"silver",False),150)   # 150.015
        self.assertEqual(c(10033,"silver",False),150)   # 150.495
        self.assertEqual(c(10067,"silver",False),151)   # 151.005
        self.assertEqual(c(10020,"gold",False),250)     # 250.5
    def test_reject(self):
        for a in (-1,1.0,"3",None,True,20000.0):
            with self.assertRaises(ValueError): c(a,"gold",False)
        for t in ("bronze","Gold",None,1):
            with self.assertRaises(ValueError): c(50000,t,False)
            with self.assertRaises(ValueError): c(5,t,False)
        for b in (1,0,None,"True"):
            with self.assertRaises(ValueError): c(50000,"gold",b)
