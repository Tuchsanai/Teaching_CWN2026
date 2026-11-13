# usage: python3 -I cli_check.py <solver_dir> <reference_test_file> <param,names,comma>
# Runs the solver's CLI (JSON stdin) on every positional case in the reference test file.
import sys, ast, json, subprocess, os
solver_dir, test_file, params = sys.argv[1], sys.argv[2], sys.argv[3].split(',')
src = open(test_file, encoding='utf-8').read()
tree = ast.parse(src)
cases = []
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.Call) and isinstance(stmt.func, ast.Attribute) and stmt.func.attr == 'assertEqual':
                call, exp = stmt.args[0], ast.literal_eval(stmt.args[1])
                cases.append(('ok', call, exp))
            if isinstance(stmt, ast.With):
                for item in stmt.items:
                    call = item.context_expr
                    if isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute) and call.func.attr == 'assertRaises':
                        cases.append(('err', call.args[0] if False else stmt.body[0].value, None))
results = []
for kind, call, exp in cases:
    kwargs = {p: ast.literal_eval(a) for p, a in zip(params, call.args)}
    p = subprocess.run([sys.executable, '-I', os.path.join(solver_dir, 'solve.py')],
                       input=json.dumps(kwargs), capture_output=True, text=True, timeout=10)
    try:
        out = json.loads(p.stdout)
    except Exception:
        out = {'raw': p.stdout[-200:], 'stderr': p.stderr[-200:]}
    if kind == 'ok':
        good = out.get('ok') is True and out.get('result') == exp
    else:
        good = out.get('ok') is False and p.returncode == 2
    if not good:
        results.append((kind, kwargs, exp, out, p.returncode))
print(f"cases={len(cases)} mismatches={len(results)}")
for r in results: print('  ', r)
