#!/bin/bash
# poll instance status until running (or timeout seconds); prints status lines only
W=/workspace/vastapp_lab/e2e_sitesafe; ID=$1; T=${2:-150}; S=$(date +%s)
while :; do
  $W/vast.sh show instance $ID --raw > $W/inst.json 2>/dev/null
  python3 - <<PY
import json
i=json.load(open("$W/inst.json"))
print(i.get("actual_status"),"|",(i.get("status_msg") or "")[:80].strip(),"|",i.get("label"),i.get("gpu_name"),i.get("dph_total"),"| ssh",i.get("public_ipaddr"),i.get("ports",{}).get("22/tcp",[{}])[0].get("HostPort"),"| proxy",i.get("ssh_host"),i.get("ssh_port"))
PY
  grep -q '"actual_status": "running"' $W/inst.json && break
  [ $(( $(date +%s)-S )) -ge $T ] && break
  sleep 15
done
