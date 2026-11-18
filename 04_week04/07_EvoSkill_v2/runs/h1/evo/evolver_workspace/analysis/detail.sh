#!/bin/bash
name=$1; task=${name%_s*}
d=$(mktemp -d /tmp/eval_XXXX)
cp "/evo/solver_workspaces/epoch_0/$name/solve.py" "$d/"; cp "/evo/reference/baankafe/answers/$task/test_solve.py" "$d/"
cd "$d" && python3 -I -c "import sys; sys.path.insert(0,'.'); import unittest; unittest.main(module='test_solve', argv=['x','-q'], exit=False)" 2>&1 | grep -E "^(FAIL|ERROR|AssertionError|ValueError|NameError|Traceback|  File \"/tmp/eval)" | grep -v "^  File" ; cd / ; rm -rf "$d"
