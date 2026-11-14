import unittest
from solve import cafe_bill as f

class T(unittest.TestCase):
    def test_values(self):
        self.assertEqual(f([{"price":4500,"qty":2}], False), 9630)
        self.assertEqual(f([{"price":4500,"qty":2}], True), 8667)
        self.assertEqual(f([{"price":49999,"qty":1}], False), 53499)
        self.assertEqual(f([{"price":50000,"qty":1}], False), 50825)
        self.assertEqual(f([{"price":4505,"qty":1}], True), 4338)
        self.assertEqual(f([], False), 0)
    def test_reject(self):
        for items, m in [([{"price":1,"qty":0}],False),([{"price":1.0,"qty":1}],False),
                         ([{"price":1,"qty":"2"}],False),([{"price":-1,"qty":1}],False),
                         ("x",False),([{"price":1,"qty":1}],1),([{"price":1}],False)]:
            with self.assertRaises(ValueError): f(items, m)

unittest.main() if __name__ == "__main__" else None
