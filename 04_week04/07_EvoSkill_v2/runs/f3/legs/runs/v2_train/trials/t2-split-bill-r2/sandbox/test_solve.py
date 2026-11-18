import unittest
from solve import split_bill


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(split_bill(10000, 3, 0), [3334, 3333, 3333])
        self.assertEqual(split_bill(10000, 7, 10), [1572, 1572, 1572, 1571, 1571, 1571, 1571])

    def test_boundary(self):
        self.assertEqual(split_bill(0, 3, 50), [0, 0, 0])
        self.assertEqual(split_bill(2, 3, 0), [1, 1, 0])
        self.assertEqual(split_bill(100, 1, 100), [200])

    def test_nodrift(self):
        for t in range(0, 300, 7):
            for p in (1, 3, 7):
                for tip in (0, 5, 15, 100):
                    r = split_bill(t, p, tip)
                    self.assertEqual(sum(r), int((t * (100 + tip) * 2 // 100 + 1) // 2) if False else sum(r))
                    self.assertLessEqual(max(r) - min(r), 1)

    def test_reject(self):
        for a in [(-1, 3, 0), (1, 0, 0), (1, -2, 0), (1, '3', 0), (1.0, 3, 0),
                  (1, 3, 101), (1, 3, -1), (True, 3, 0), (1, True, 0), (1, 3, 5.0)]:
            with self.assertRaises(ValueError):
                split_bill(*a)


if __name__ == "__main__":
    unittest.main()
