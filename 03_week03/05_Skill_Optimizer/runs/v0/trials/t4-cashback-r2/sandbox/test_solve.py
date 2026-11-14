import json, subprocess, sys
import pytest
from solve import cashback


@pytest.mark.parametrize("a,t,b,exp", [
    (9999, "platinum", True, 0),
    (10000, "silver", False, 150),
    (10000, "gold", False, 250),
    (10000, "platinum", False, 400),
    (10000, "silver", True, 300),
    (0, "gold", False, 0),
    (10033, "silver", False, 150),   # 150.495 -> 150
    (10034, "silver", False, 151),   # 150.51 -> 151
    (10010, "gold", False, 250),     # 250.25
    (10020, "gold", False, 251),     # 250.5 -> half up 251
    (600000, "platinum", False, 20000),  # ชนเพดานพอดี
    (10**9, "platinum", True, 20000),
])
def test_cashback(a, t, b, exp):
    assert cashback(a, t, b) == exp


@pytest.mark.parametrize("args,exc", [
    ((-1, "gold", False), ValueError),
    ((100.0, "gold", False), TypeError),
    ((True, "gold", False), TypeError),
    ((100, "bronze", False), ValueError),
    ((100, None, False), ValueError),
    ((100, "gold", 1), TypeError),
])
def test_invalid(args, exc):
    with pytest.raises(exc):
        cashback(*args)


def run(inp):
    return subprocess.run([sys.executable, "solve.py"], input=inp,
                          capture_output=True, text=True)


def test_cli_ok():
    r = run('{"amount": 20000, "tier": "gold", "birthday": true}')
    assert r.returncode == 0 and json.loads(r.stdout) == {"cashback": 1000}


def test_cli_error():
    for bad in ('not json', '{"amount": 1}', '{"amount": -5, "tier": "gold", "birthday": false}'):
        r = run(bad)
        assert r.returncode == 1 and "error" in json.loads(r.stdout)
