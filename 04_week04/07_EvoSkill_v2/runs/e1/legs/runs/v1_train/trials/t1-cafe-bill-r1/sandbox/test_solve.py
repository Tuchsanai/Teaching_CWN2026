import unittest
from solve import cafe_bill as f
class T(unittest.TestCase):
    def test_n(self):
        self.assertEqual(f([], False), 0)
        self.assertEqual(f([{"price":1000,"qty":2}], False), 2140)
        self.assertEqual(f([{"price":1000,"qty":2}], True), 1926)
    def test_b(self):
        self.assertEqual(f([{"price":49999,"qty":1}], False), 53499)
        self.assertEqual(f([{"price":50000,"qty":1}], False), 50825)
        self.assertEqual(f([{"price":50000,"qty":1}], True), 45743)  # 45742.5 half-up
    def test_r(self):
        for bad in [([{"price":1.0,"qty":1}],False),([{"price":1,"qty":0}],False),([{"price":1}],False),([1],False),(None,False),([],1),([{"price":True,"qty":1}],False),([{"price":-1,"qty":1}],False)]:
            with self.assertRaises(ValueError): f(*bad)
unittest.main() if __name__=="__main__" else None
