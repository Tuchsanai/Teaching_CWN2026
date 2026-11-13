import unittest
from solve import cashback

class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cashback(20000, "silver", False), 300)
        self.assertEqual(cashback(20000, "gold", True), 1000)
        self.assertEqual(cashback(50000, "platinum", False), 2000)
    def test_boundary(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(400000, "platinum", True), 20000)
        self.assertEqual(cashback(0, "gold", False), 0)
    def test_rounding(self):
        self.assertEqual(cashback(10033, "silver", False), 150)
        self.assertEqual(cashback(10100, "silver", False), 152)
    def test_reject(self):
        for a in [(-1,"gold",False),(1000.0,"gold",False),("3","gold",False),(True,"gold",False),
                  (None,"gold",False),(20000,"bronze",False),(20000,["x"],False),(20000,"gold",1),(20000,"gold",None)]:
            with self.assertRaises(ValueError): cashback(*a)
unittest.main() if __name__ == "__main__" else None
