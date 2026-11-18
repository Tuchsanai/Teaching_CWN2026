import unittest
from solve import bulk_price as f

class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(f(10000, 1, False), 10700)
        self.assertEqual(f(10000, 10, False), 103255)
        self.assertEqual(f(10000, 50, True), 482503)
    def test_boundary(self):
        self.assertEqual(f(100, 9, False), 963)
        self.assertEqual(f(100, 10, False), 1033)
        self.assertEqual(f(100, 49, False), 5059)
        self.assertEqual(f(100, 50, False), 4949)
        self.assertEqual(f(0, 1, True), 0)
    def test_nodrift(self):
        self.assertIsInstance(f(333, 77, True), int)
        self.assertEqual(f(1, 1, False), 1)
    def test_reject(self):
        for a in [(-1,1,False),(1,0,False),(1,1001,False),(1.0,1,False),(1,1.0,False),
                  ("1",1,False),(1,True,False),(True,1,False),(1,1,1),(1,1,None),(None,1,False)]:
            with self.assertRaises(ValueError): f(*a)
