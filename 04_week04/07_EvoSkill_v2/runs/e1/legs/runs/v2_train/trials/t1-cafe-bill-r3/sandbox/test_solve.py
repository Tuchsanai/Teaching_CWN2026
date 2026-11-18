import unittest
from solve import cafe_bill as c
class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(c([{"price":10000,"qty":2}],False),21400)
        self.assertEqual(c([{"price":10000,"qty":2}],True),19260)
        self.assertEqual(c([],True),0)
    def test_boundary(self):
        self.assertEqual(c([{"price":49999,"qty":1}],False),53499)
        self.assertEqual(c([{"price":50000,"qty":1}],False),50825)
        self.assertEqual(c([{"price":50000,"qty":1}],True),45743)  # 45742.5
    def test_reject(self):
        for items,m in [([{"price":1,"qty":0}],False),([{"price":1.0,"qty":1}],False),([{"price":-1,"qty":1}],False),([{"price":1}],False),(None,False),([1],False),([{"price":True,"qty":1}],False),([],1),([{"price":"1","qty":1}],False)]:
            with self.assertRaises(ValueError): c(items,m)
unittest.main() if __name__=="__main__" else None
