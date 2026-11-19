#!/bin/bash
# Status + rent cost of the e2e-receipt instance only (run in the container). Prints no key values.
W=/workspace/vastapp_lab/e2e_receipt
$W/vast.sh show instance 61389598 --raw > /tmp/inst_now.json 2>/dev/null
python3 - <<'PY'
import json, time
d = json.load(open("/tmp/inst_now.json")); d = d[0] if isinstance(d, list) else d
assert d.get("label") == "e2e-receipt"
h = (time.time() - 1795068455.04) / 3600
print(d["label"], d.get("actual_status"), f'${d["dph_total"]:.4f}/h', f"{h:.3f} h", f'this instance ${h*d["dph_total"]:.3f}',
      f'+ earlier attempts ~$0.108 = ${h*d["dph_total"]+0.108:.3f}')
PY
rm -f /tmp/inst_now.json
