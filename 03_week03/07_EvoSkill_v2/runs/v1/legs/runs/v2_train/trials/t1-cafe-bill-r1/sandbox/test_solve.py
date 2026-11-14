import unittest
from solve import cafe_bill
class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cafe_bill([{"price":4500,"qty":2}],False),9630)
    def test_boundary(self):
        self.assertEqual(cafe_bill([{"price":50000,"qty":1}],False),50000*95*107//10000)
        self.assertEqual(cafe_bill([{"price":49999,"qty":1}],False),53499)
    def test_drift(self):
        self.assertEqual(cafe_bill([{"price":4505,"qty":1}],True),4338)
    def test_empty(self):
        self.assertEqual(cafe_bill([],True),0)
    def test_reject(self):
        for items,m in [([{"price":4500.0,"qty":1}],False),([{"price":1,"qty":0}],False),([{"price":1}],False),
                        ([{"price":True,"qty":1}],False),("x",False),([1],False),([{"price":1,"qty":1}],1),([{"price":-1,"qty":1}],False)]:
            with self.assertRaises(ValueError): cafe_bill(items,m)
unittest.main() if __name__=="__main__" else None
