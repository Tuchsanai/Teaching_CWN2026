import io
import json
import unittest
from unittest import mock

import solve
from solve import cashback


class CashbackTests(unittest.TestCase):
    def test_below_minimum(self):
        self.assertEqual(cashback(9999, "platinum", True), 0)
        self.assertEqual(cashback(0, "gold", False), 0)

    def test_minimum_boundary(self):
        self.assertEqual(cashback(10000, "silver", False), 150)
        self.assertEqual(cashback(10000, "gold", False), 250)
        self.assertEqual(cashback(10000, "platinum", False), 400)

    def test_birthday_double(self):
        self.assertEqual(cashback(10000, "gold", True), 500)

    def test_rounding_half_up(self):
        self.assertEqual(cashback(10010, "silver", False), 150)  # 150.15
        self.assertEqual(cashback(10033, "silver", False), 150)  # 150.495
        self.assertEqual(cashback(10034, "silver", False), 151)  # 150.51
        self.assertEqual(cashback(10020, "gold", False), 251)    # 250.5 -> 251

    def test_cap(self):
        self.assertEqual(cashback(10**9, "platinum", True), 20000)
        self.assertEqual(cashback(500000, "platinum", False), 20000)
        self.assertEqual(cashback(499999, "platinum", False), 20000)  # 19999.96
        self.assertEqual(cashback(499900, "platinum", False), 19996)

    def test_invalid(self):
        for args in [(-1, "gold", False), (1.5, "gold", False), ("100", "gold", False),
                     (True, "gold", False), (10000, "bronze", False),
                     (10000, None, False), (10000, "gold", 1), (10000, "gold", None)]:
            with self.assertRaises((ValueError, TypeError), msg=str(args)):
                cashback(*args)


class CliTests(unittest.TestCase):
    def run_cli(self, payload):
        with mock.patch("sys.stdin", io.StringIO(payload)), \
             mock.patch("sys.stdout", new_callable=io.StringIO) as out:
            code = solve.main([])
        return code, json.loads(out.getvalue())

    def test_ok(self):
        self.assertEqual(self.run_cli('{"amount":10000,"tier":"gold","birthday":true}'),
                         (0, {"cashback": 500}))

    def test_errors(self):
        for p in ['not json', '[]', '{"amount":1}', '{"amount":-5,"tier":"gold","birthday":false}']:
            code, res = self.run_cli(p)
            self.assertEqual(code, 1)
            self.assertIn("error", res)


if __name__ == "__main__":
    unittest.main()
