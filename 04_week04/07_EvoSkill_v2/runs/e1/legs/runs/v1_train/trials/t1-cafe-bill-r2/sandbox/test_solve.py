import unittest
from solve import cafe_bill as f
class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(f([{"price":10000,"qty":1}],False),10700)
        self.assertEqual(f([],True),0)
        self.assertEqual(f([{"price":10000,"qty":1}],True),9630)
    def test_boundary(self):
        self.assertEqual(f([{"price":49999,"qty":1}],False),53499)  # 49999*1.07=53498.93
        self.assertEqual(f([{"price":50000,"qty":1}],False),50825)  # 50000*.95*1.07
    def test_half(self):
        # 50050*.95*1.07=50875.4...; check 10050*1.07=10753.5 -> 10754
        self.assertEqual(f([{"price":10050,"qty":1}],False),10754)
    def test_reject(self):
        for items,m in [([{"price":1,"qty":0}],False),([{"price":1.0,"qty":1}],False),
            ([{"price":1,"qty":"1"}],False),([{"price":-1,"qty":1}],False),
            ([{"price":1}],False),([1],False),(None,False),([],1),([{"price":True,"qty":1}],False)]:
            with self.assertRaises(ValueError): f(items,m)
unittest.main() if __name__=="__main__" else None
