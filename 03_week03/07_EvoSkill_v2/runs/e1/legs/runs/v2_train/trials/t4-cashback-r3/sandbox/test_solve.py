import unittest
from solve import cashback

class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(cashback(100000, "silver", False), 1500)
        self.assertEqual(cashback(100000, "gold", False), 2500)
        self.assertEqual(cashback(100000, "platinum", False), 4000)
        self.assertEqual(cashback(100000, "gold", True), 5000)
        self.assertEqual(cashback(100000, "silver", True), 1500)
    def test_boundary(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(10000, "platinum", False), 400)
        self.assertEqual(cashback(0, "gold", False), 0)
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(500001, "platinum", True), 20000)
        self.assertEqual(cashback(800000, "gold", False), 20000)
        self.assertEqual(cashback(800001, "gold", False), 20000)
        self.assertEqual(cashback(799999, "gold", False), 19999)
    def test_floor(self):
        self.assertEqual(cashback(10001, "silver", False), 150)   # 150.015
        self.assertEqual(cashback(10033, "silver", False), 150)   # 150.495
        self.assertEqual(cashback(10067, "silver", False), 151)   # 151.005
        self.assertEqual(cashback(10019, "gold", False), 250)     # 250.475
        self.assertEqual(cashback(10020, "gold", False), 250)     # 250.5
    def test_reject(self):
        bad = [(-1,"gold",False),(20000.0,"gold",False),("3","gold",False),(None,"gold",False),
               (True,"gold",False),(20000,"bronze",False),(20000,None,False),(20000,"Gold",False),
               (20000,"gold",1),(20000,"gold",None),(5,"bronze",False),(5,"gold","x")]
        for a in bad:
            with self.assertRaises(ValueError, msg=str(a)):
                cashback(*a)
        with self.assertRaises(ValueError):
            cashback(amount=5, tier="x", birthday=False)

if __name__ == "__main__":
    unittest.main()
