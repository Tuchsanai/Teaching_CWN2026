import unittest
from solve import shipping_fee as f


class T(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(f(500, 10, False), 4000)
        self.assertEqual(f(3000, 10, False), 8000)
        self.assertEqual(f(10000, 10, False), 8000 + 7500)
        self.assertEqual(f(500, 150, True), 7200)

    def test_boundary(self):
        self.assertEqual(f(1000, 5, False), 4000)
        self.assertEqual(f(1001, 5, False), 8000)
        self.assertEqual(f(5000, 100, False), 8000)
        self.assertEqual(f(5000, 101, False), 9600)
        self.assertEqual(f(20000, 5, True), 45750)
        self.assertEqual(f(30000, 5, False), 8000 + 37500)
        self.assertEqual(f(1, 0, False), 0)

    def test_nodrift(self):
        # 5001 g: 8000+1.5 = 8001.5 -> 8002 ; express 12002.25 -> 12002
        self.assertEqual(f(5001, 5, False), 8002)
        self.assertEqual(f(5001, 5, True), 12002)
        self.assertEqual(f(5001, 101, False), 9602)  # 9601.8

    def test_reject(self):
        bad = [(0, 1, False), (30001, 1, False), (-1, 1, False), (500.0, 1, False),
               ("5", 1, False), (True, 1, False), (None, 1, False),
               (500, -1, False), (500, 1.5, False), (500, 10.0, False),
               (500, True, False), (500, "1", False), (500, 1, 1), (500, 1, None),
               (20001, 1, True), (20001, 0, True), (500, 0, "yes")]
        for a in bad:
            with self.assertRaises(ValueError, msg=str(a)):
                f(*a)


if __name__ == "__main__":
    unittest.main()
