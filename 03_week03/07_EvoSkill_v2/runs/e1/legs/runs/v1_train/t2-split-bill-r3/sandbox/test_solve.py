import unittest
from solve import split_bill as s
class T(unittest.TestCase):
    def test_a(self):
        self.assertEqual(s(1000,3,0),[334,333,333])
        self.assertEqual(s(0,2,50),[0,0])
        self.assertEqual(s(1,1,50),[2])   # 1.5 -> 2
        self.assertEqual(s(999,1,10),[1099]) # 1098.9
        self.assertEqual(s(5,2,10),[3,3])  # 5.5->6
        self.assertEqual(s(1004,1,5),[1054]) # 1054.2
    def test_rej(self):
        for a in [(-1,1,0),(1,0,0),(1,1,101),(1,1,-1),(1.0,1,0),(1,True,0),(1,1,"5"),(None,1,0)]:
            with self.assertRaises(ValueError): s(*a)
