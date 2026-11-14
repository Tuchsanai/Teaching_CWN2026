import unittest
from solve import split_bill

class T(unittest.TestCase):
    def test_ok(self):
        self.assertEqual(split_bill(10000, 3, 0), [3334, 3333, 3333])
        self.assertEqual(split_bill(10000, 7, 10), [1572]*3 + [1571]*4)
        self.assertEqual(split_bill(2, 3, 0), [1, 1, 0])
        self.assertEqual(split_bill(0, 2, 50), [0, 0])
    def test_reject(self):
        for a in [(-1,1,0),(1,0,0),(1,1,-1),(1,1,101),(1.0,1,0),(1,True,0),("1",1,0),(1,1,None)]:
            with self.assertRaises(ValueError):
                split_bill(*a)

unittest.main() if __name__ == "__main__" else None
