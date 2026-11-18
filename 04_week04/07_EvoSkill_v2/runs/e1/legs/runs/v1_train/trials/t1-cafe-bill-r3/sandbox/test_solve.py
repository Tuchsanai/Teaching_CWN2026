import unittest
from solve import cafe_bill as c
def it(p,q=1): return [{"price":p,"qty":q}]
class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(c(it(10000,2),False),21400)
        self.assertEqual(c(it(10000,5),True),int(50000*.95*.9*1.07+.5))
        self.assertEqual(c([],True),0)
    def test_boundary(self):
        self.assertEqual(c(it(49999),False),53499)   # 49999*1.07=53498.93
        self.assertEqual(c(it(50000),False),50825)   # 50000*.95*1.07=50825
    def test_round(self):
        self.assertEqual(c(it(50),False),54)  # 53.5 -> 54
    def test_reject(self):
        for a in [(None,False),(it(1),1),([{"price":1.0,"qty":1}],False),([{"price":1,"qty":0}],False),([{"price":-1,"qty":1}],False),([{"price":1}],False),([1],False),([{"price":True,"qty":1}],False),([{"price":1,"qty":"3"}],False)]:
            with self.assertRaises(ValueError): c(*a)
unittest.main() if __name__=="__main__" else None
