"""Count images and boxes per class for each split (train / valid / test)."""
import sys, json, subprocess
from pathlib import Path
import yaml

root = Path(sys.argv[1] if len(sys.argv) > 1 else "/workspace/hardhat")
names = yaml.safe_load(open(root / "data.yaml"))["names"]
res = {}
for s in ["train", "valid", "test"]:
    cnt = [0] * len(names); empty = 0
    labs = list((root / s / "labels").glob("*.txt"))
    for f in labs:
        lines = [l for l in open(f) if l.strip()]
        empty += not lines
        for l in lines:
            cnt[int(l.split()[0])] += 1
    res[s] = {"images": len(list((root / s / "images").iterdir())), "labels": len(labs),
              "empty_labels": empty, "boxes": dict(zip(names, cnt))}
res["size"] = subprocess.check_output(["du", "-sh", str(root)]).decode().split()[0]
res["names"] = names
print(json.dumps(res, indent=2))
