#!/bin/bash
# Status + rent cost of ONE labelled instance (run in the container). Prints no key values.
# usage: cost_now.sh <instance_id> <start_epoch_seconds> [label] [earlier_usd]
W=${W:-/workspace/vastapp_lab/e2e_receipt}; ID=$1; START=$2; LABEL=${3:-${LABEL:-e2e-receipt}}; EARLIER=${4:-0}
$W/vast.sh show instance $ID --raw > /tmp/inst_now.json 2>/dev/null
python3 - "$START" "$LABEL" "$EARLIER" <<'PY'
import json, sys, time
start, label, earlier = float(sys.argv[1]), sys.argv[2], float(sys.argv[3])
d = json.load(open("/tmp/inst_now.json")); d = d[0] if isinstance(d, list) else d
assert d.get("label") == label, f"label is {d.get('label')!r}, not {label!r} - refusing"
h = (time.time() - start) / 3600
print(d["label"], d.get("actual_status"), f'${d["dph_total"]:.4f}/h', f"{h:.3f} h",
      f'this instance ${h*d["dph_total"]:.3f}', f'+ earlier ${earlier:.3f} = ${h*d["dph_total"]+earlier:.3f}')
PY
rm -f /tmp/inst_now.json
