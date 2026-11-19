"""Write data_fixed.yaml next to the Roboflow data.yaml with an absolute root and split paths that exist."""
import sys
from pathlib import Path
import yaml

root = Path(sys.argv[1]).resolve()
src = yaml.safe_load((root / "data.yaml").read_text(encoding="utf-8"))
fixed = {"path": str(root), "train": "train/images", "val": "valid/images", "test": "test/images",
         "nc": src["nc"], "names": src["names"]}
for key in ("train", "val", "test"):
    assert (root / fixed[key]).is_dir(), fixed[key]
(root / "data_fixed.yaml").write_text(yaml.safe_dump(fixed, sort_keys=False, allow_unicode=True), encoding="utf-8")
print(fixed)
