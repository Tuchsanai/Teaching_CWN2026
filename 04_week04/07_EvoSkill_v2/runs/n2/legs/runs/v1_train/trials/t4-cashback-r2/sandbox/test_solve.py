import unittest
from solve import cashback

class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cashback(20000, "silver", False), 300)
        self.assertEqual(cashback(10015, "platinum", True), 801)
        self.assertEqual(cashback(10020, "gold", True), 501)
        self.assertEqual(cashback(20000, "silver", True), 600)
    def test_boundary(self):
        self.assertEqual(cashback(9999, "gold", True), 0)
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(0, "gold", False), 0)
    def test_reject(self):
        for a in [(-1,"gold",False),(1.0,"gold",False),("1","gold",False),(True,"gold",False),
                  (100,"bronze",False),(100,1,False),(100,"gold",1)]:
            with self.assertRaises(ValueError): cashback(*a)
unittest.main() if __name__ == "__main__" else None
