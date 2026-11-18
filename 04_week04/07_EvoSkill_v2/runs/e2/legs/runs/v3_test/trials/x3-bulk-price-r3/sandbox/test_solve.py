import unittest
from solve import bulk_price


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(bulk_price(10000, 1, False), 10700)
        self.assertEqual(bulk_price(10000, 10, False), 103255)
        self.assertEqual(bulk_price(10000, 50, True), 482503)
        self.assertEqual(bulk_price(10000, 1, True), 10433)

    def test_boundary(self):
        self.assertEqual(bulk_price(1000, 9, False), 9630)
        self.assertEqual(bulk_price(1000, 10, False), 10326)
        self.assertEqual(bulk_price(1000, 49, False), 50595)
        self.assertEqual(bulk_price(1000, 50, False), 49488)
        self.assertEqual(bulk_price(0, 5, True), 0)
        bulk_price(1, 1000, True)

    def test_nodrift(self):
        self.assertEqual(bulk_price(1, 1, False), 1)
        self.assertIs(type(bulk_price(333, 7, True)), int)

    def test_reject(self):
        for a in [(-1, 1, False), (1, 0, False), (1, 1001, False), (1.0, 1, False),
                  ("1", 1, False), (True, 1, False), (1, True, False), (1, 1.0, False),
                  (1, 1, 1), (1, 1, None), (None, 1, False)]:
            with self.assertRaises(ValueError):
                bulk_price(*a)


if __name__ == "__main__":
    unittest.main()
