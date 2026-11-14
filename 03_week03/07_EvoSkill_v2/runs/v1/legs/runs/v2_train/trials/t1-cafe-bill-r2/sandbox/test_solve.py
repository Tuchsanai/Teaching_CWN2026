import unittest
from solve import cafe_bill
class T(unittest.TestCase):
    def test_all(self):
        self.assertEqual(cafe_bill([{"price":4500,"qty":2}],False),9630)
        self.assertEqual(cafe_bill([{"price":50000,"qty":1}],False),50000*95*107//10000+ (1 if (50000*95*107)%10000>=5000 else 0))
        self.assertEqual(cafe_bill([],False),0)
        self.assertEqual(cafe_bill([{"price":4505,"qty":1}],True),4338)
    def test_reject(self):
        for a in ([{"price":1.0,"qty":1}],[{"price":1,"qty":0}],[{"price":1}],[{"price":True,"qty":1}],"x"):
            with self.assertRaises(ValueError): cafe_bill(a,False)
        with self.assertRaises(ValueError): cafe_bill([],1)
unittest.main() if __name__=="__main__" else None
