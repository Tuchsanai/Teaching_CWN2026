import json
import subprocess
import sys

import pytest

from solve import shipping_fee as f


@pytest.mark.parametrize("args,exp", [
    ((1, 0, False), 4000),
    ((1000, 100, False), 4000),
    ((1001, 0, False), 8000),
    ((5000, 0, False), 8000),
    ((5001, 0, False), 8002),      # 1.5 -> 2 (ปัดครึ่งขึ้น)
    ((6000, 0, False), 9500),
    ((30000, 0, False), 45500),
    ((1000, 100.5, False), 4800),
    ((1000, 0, True), 6000),
    ((1000, 101, True), 7200),
    ((5001, 0, True), 12002),      # 8001.5*1.5=12002.25 ปัดครั้งเดียว
    ((5003, 101, False), 9605),    # 8004.5*1.2=9605.4
])
def test_fee(args, exp):
    assert f(*args) == exp


@pytest.mark.parametrize("args", [
    (0, 1, False), (30001, 1, False), (10, -1, False), ("10", 1, False),
    (10, 1, 1), (True, 1, False), (float("nan"), 1, False),
])
def test_invalid(args):
    with pytest.raises(ValueError):
        f(*args)


def test_cli():
    r = subprocess.run([sys.executable, "solve.py"],
                       input='{"weight_g":6000,"distance_km":150,"express":true}',
                       capture_output=True, text=True)
    assert json.loads(r.stdout) == {"fee_satang": 17100}
    r = subprocess.run([sys.executable, "solve.py"], input='{"weight_g":0}',
                       capture_output=True, text=True)
    assert r.returncode == 1 and "error" in json.loads(r.stdout)
