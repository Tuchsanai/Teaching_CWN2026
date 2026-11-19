#!/bin/bash
# Rent one offer (2x RTX 3090) labelled e2e-receipt, 80 GB disk, PyTorch+CUDA image, ports 22 + 8000 + 8080.
# Usage: rent.sh <OFFER_ID> <attempt_no>   (create output, which contains per-instance keys, goes to a file only)
W=/workspace/vastapp_lab/e2e_receipt; OFFER=$1; N=${2:-1}
date -Iseconds > $W/rent_start_attempt$N.txt
$W/vast.sh create instance $OFFER --image vastai/pytorch:@vastai-automatic-tag --disk 80 --ssh --direct \
  --label e2e-receipt --env '-p 8000:8000 -p 8080:8080' --raw > $W/create$N.json 2>&1
python3 -c "import json;d=json.load(open('$W/create$N.json'));print('success',d.get('success'),'new_contract',d.get('new_contract'))"
