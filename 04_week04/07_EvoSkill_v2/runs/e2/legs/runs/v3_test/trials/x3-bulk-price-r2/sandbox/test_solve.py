import unittest
from solve import bulk_price


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(bulk_price(10000, 1, False), 10700)
        self.assertEqual(bulk_price(10000, 10, False), 103255)
        self.assertEqual(bulk_price(10000, 50, True), 482503)
        self.assertEqual(bulk_price(10000, 10, True), 100674)

    def test_boundary(self):
        self.assertEqual(bulk_price(100, 9, False), 963)
        self.assertEqual(bulk_price(100, 10, False), 1033)
        self.assertEqual(bulk_price(100, 49, False), 5059)
        self.assertEqual(bulk_price(100, 50, False), 4949)
        self.assertEqual(bulk_price(0, 5, True), 0)
        self.assertEqual(bulk_price(100, 1000, False), 98975)

    def test_nodrift(self):
        self.assertEqual(bulk_price(1, 1, False), 1)
        self.assertEqual(bulk_price(5, 1, False), 5)
        self.assertIs(type(bulk_price(333, 77, True)), int)

    def test_reject(self):
        for a in [(-1, 1, False), (1, 0, False), (1, 1001, False), (1.0, 1, False),
                  ("1", 1, False), (True, 1, False), (1, 1.0, False), (1, True, False),
                  (1, 1, 1), (1, 1, None), (None, 1, False)]:
            with self.assertRaises(ValueError):
                bulk_price(*a)


if __name__ == "__main__":
    unittest.main()
