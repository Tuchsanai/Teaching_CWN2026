import unittest
from solve import cashback
class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cashback(100000,"silver",False),1500)
        self.assertEqual(cashback(100000,"gold",True),5000)
        self.assertEqual(cashback(100000,"platinum",False),4000)
    def test_boundary(self):
        self.assertEqual(cashback(9999,"platinum",True),0)
        self.assertEqual(cashback(10000,"silver",False),150)
        self.assertEqual(cashback(500000,"platinum",False),20000)
        self.assertEqual(cashback(600000,"platinum",True),20000)
    def test_round(self):
        self.assertEqual(cashback(10010,"silver",False),150)  # 150.15
        self.assertEqual(cashback(10030,"silver",False),150)  # 150.45
        self.assertEqual(cashback(10040,"silver",False),151)  # 150.6
        self.assertEqual(cashback(10100,"gold",False),253)    # 252.5 -> 253
    def test_reject(self):
        for a in [(-1,"gold",False),(1.0,"gold",False),("1","gold",False),(True,"gold",False),
                  (10000,"bronze",False),(10000,["gold"],False),(10000,"gold",1),(10000,"gold",None)]:
            with self.assertRaises(ValueError): cashback(*a)
unittest.main() if __name__=="__main__" else None
