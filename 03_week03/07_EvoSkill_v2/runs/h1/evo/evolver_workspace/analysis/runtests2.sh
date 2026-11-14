#!/bin/bash
# usage: runtests2.sh <epoch> <solver_dir_name>
ep=$1; name=$2; task=${name%_s*}
d=$(mktemp -d /tmp/eval_XXXX)
cp "/evo/solver_workspaces/epoch_$ep/$name/solve.py" "$d/" 2>/dev/null || { echo "$name: no solve.py"; exit 0; }
cp "/evo/reference/baankafe/answers/$task/test_solve.py" "$d/"
cd "$d" && python3 -I -c "import sys; sys.path.insert(0,'.'); import unittest; unittest.main(module='test_solve', argv=['x','-q'], exit=False)" 2>&1 | grep -E "^(FAIL|ERROR|AssertionError|FAILED|OK)" | sed "s/^/$name: /"
cd / ; rm -rf "$d"
