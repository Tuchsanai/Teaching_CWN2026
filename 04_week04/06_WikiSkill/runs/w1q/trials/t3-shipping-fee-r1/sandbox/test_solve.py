import unittest
from solve import shipping_fee as f


class TestSolve(unittest.TestCase):
    def test_light(self):
        self.assertEqual(f(500, 10, False), 4000)

    def test_mid(self):
        self.assertEqual(f(3000, 50, False), 8000)

    def test_heavy_excess(self):
        # 10000g: 8000 + 5*1500 = 15500
        self.assertEqual(f(10000, 10, False), 15500)

    def test_far_and_express(self):
        # 4000*1.2*1.5 = 7200
        self.assertEqual(f(1000, 101, True), 7200)

    def test_edge_1000(self):
        self.assertEqual(f(1000, 1, False), 4000)
        self.assertEqual(f(1001, 1, False), 8000)

    def test_edge_5000(self):
        self.assertEqual(f(5000, 1, False), 8000)
        # 5001g: 8000 + 1.5 = 8001.5 -> half up 8002
        self.assertEqual(f(5001, 1, False), 8002)

    def test_edge_100km(self):
        self.assertEqual(f(1000, 100, False), 4000)
        self.assertEqual(f(1000, 100.5, False), 4800)

    def test_zero_distance_free(self):
        self.assertEqual(f(30000, 0, False), 0)

    def test_express_limit(self):
        self.assertEqual(f(20000, 1, True), 45750)  # (8000+22500)*1.5
        with self.assertRaises(ValueError):
            f(20001, 1, True)
        self.assertEqual(f(30000, 1, False), 45500)

    def test_int_result(self):
        self.assertIs(type(f(5001, 101, True)), int)

    def test_reject_weight(self):
        for v in (0, -1, 30001, 100.0, True, "5", None):
            with self.assertRaises(ValueError):
                f(v, 10, False)

    def test_reject_distance(self):
        for v in (-1, -0.1, True, "5", None, float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                f(1000, v, False)

    def test_reject_express(self):
        for v in (1, 0, "yes", None):
            with self.assertRaises(ValueError):
                f(1000, 10, v)


if __name__ == "__main__":
    unittest.main()
