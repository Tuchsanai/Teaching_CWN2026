# usage: python3 -I run_tests.py <solver_dir> <test_file>
import sys, unittest, importlib.util, os
solver_dir, test_file = sys.argv[1], sys.argv[2]
sys.path.insert(0, solver_dir)
spec = importlib.util.spec_from_file_location("ref_tests", test_file)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
suite = unittest.defaultTestLoader.loadTestsFromModule(mod)
res = unittest.TextTestRunner(stream=open(os.devnull, "w"), verbosity=0).run(suite)
fails = [t.id().split('.')[-1] for t, _ in res.failures + res.errors]
print(f"ran={res.testsRun} failed={len(fails)} {fails}")
