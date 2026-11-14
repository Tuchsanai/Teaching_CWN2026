import unittest
from solve import cashback as c
class T(unittest.TestCase):
    def test_v(self):
        self.assertEqual(c(9999,"gold",False),0)
        self.assertEqual(c(10000,"silver",False),150)
        self.assertEqual(c(10001,"silver",False),150)   # 150.015 floor
        self.assertEqual(c(10000,"silver",True),150)
        self.assertEqual(c(10000,"gold",True),500)
        self.assertEqual(c(10000,"platinum",True),800)
        self.assertEqual(c(1000000,"platinum",True),20000)
        self.assertEqual(c(0,"gold",False),0)
        self.assertIs(type(c(12345,"gold",True)),int)
    def test_rej(self):
        for a in [(-1,"gold",False),(1.0,"gold",False),("1","gold",False),(True,"gold",False),(10000,"x",False),(10000,"gold",1),(10000,None,False)]:
            with self.assertRaises(ValueError): c(*a)
