import unittest
from solve import bulk_price as b


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(b(10000, 1, False), 10700)
        self.assertEqual(b(10000, 10, False), 103255)   # 100000*.965*1.07
        self.assertEqual(b(10000, 50, False), 494875)   # 500000*.925*1.07
        self.assertEqual(b(10000, 1, True), 10433)      # 9750*1.07=10432.5 -> up
        self.assertEqual(b(10000, 50, True), 482503)    # 462500*.975*1.07=482503.125

    def test_boundary(self):
        self.assertEqual(b(100, 9, False), 963)
        self.assertEqual(b(100, 10, False), 1033)
        self.assertEqual(b(100, 49, False), 5059)   # 4900*.965*1.07=5059.495
        self.assertEqual(b(0, 1, False), 0)

    def test_reject(self):
        for a in [(-1, 1, False), (1, 0, False), (1, 1001, False), (1.0, 1, False),
                  ("1", 1, False), (True, 1, False), (1, 1.0, False), (1, True, False),
                  (1, 1, 1), (1, 1, None), (None, 1, False), (1, [], False)]:
            with self.assertRaises(ValueError):
                b(*a)


if __name__ == "__main__":
    unittest.main()
