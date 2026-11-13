import unittest
from solve import cafe_bill as f
class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(f([{"price":10000,"qty":2}],False),21400)
        self.assertEqual(f([{"price":10000,"qty":2}],True),19260)
        self.assertEqual(f([],False),0)
    def test_boundary(self):
        self.assertEqual(f([{"price":49999,"qty":1}],False),53499)
        self.assertEqual(f([{"price":50000,"qty":1}],False),50825)  # 50000*.95*1.07=50825
    def test_half(self):
        self.assertEqual(f([{"price":50,"qty":1}],True),48)  # 48.15
        self.assertEqual(f([{"price":5,"qty":1}],False),5)   # 5.35
    def test_reject(self):
        for items,m in [([{"price":-1,"qty":1}],False),([{"price":1,"qty":0}],False),
            ([{"price":1.0,"qty":1}],False),([{"price":"1","qty":1}],False),
            ([{"price":True,"qty":1}],False),([{"price":1}],False),(None,False),
            ([1],False),([{"price":1,"qty":1}],1),([{"price":1,"qty":1}],None)]:
            with self.assertRaises(ValueError): f(items,m)
unittest.main() if __name__=="__main__" else None
