import unittest
from solve import bulk_price


class Normal(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(bulk_price(1000, 1, False), 1070)
        self.assertEqual(bulk_price(1000, 10, True), 10067)
        self.assertEqual(bulk_price(1000, 50, False), 49488)  # 50000*.925*1.07=49487.5 -> 49488
        

class Boundary(unittest.TestCase):
    def test_tiers(self):
        self.assertEqual(bulk_price(100, 9, False), 963)
        self.assertEqual(bulk_price(100, 10, False), 1033)   # 1000*.965*1.07=1032.55
        self.assertEqual(bulk_price(100, 49, False), 5059)   # 4900*.965*1.07=5059.4
        self.assertEqual(bulk_price(100, 50, False), 4949)   # 5000*.925*1.07=4948.75
        self.assertEqual(bulk_price(0, 1, False), 0)


class NoDrift(unittest.TestCase):
    def test_half_up(self):
        self.assertEqual(bulk_price(1000, 50, False), 49488)


class Reject(unittest.TestCase):
    def test_bad(self):
        for a in [(-1, 1, False), (100, 0, False), (100, 1001, False), (100.0, 1, False),
                  ("1", 1, False), (True, 1, False), (100, True, False), (100, 1, 1),
                  (100, 1, None), (100, 2.0, False)]:
            with self.assertRaises(ValueError):
                bulk_price(*a)


if __name__ == "__main__":
    unittest.main()
