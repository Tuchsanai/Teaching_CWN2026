"""Write a curated inst.json (no tokens) + ssh_target from the raw `show instance` output."""
import json, datetime
W = "/workspace/vastapp_lab/e2e_receipt"
i = json.load(open(f"{W}/inst_raw.json"))
start = open(f"{W}/rent_start_attempt3.txt").read().strip()
p = lambda k: (i.get("ports") or {}).get(k, [{}])[0].get("HostPort")
out = {"instance_id": i["id"], "label": i.get("label"), "rent_requested_at": start,
       "start_date_unix": i.get("start_date"),
       "start_date": datetime.datetime.fromtimestamp(i["start_date"], datetime.timezone(datetime.timedelta(hours=7))).isoformat(),
       "gpu": f'{i["num_gpus"]}x {i["gpu_name"]}', "price_per_hour_usd": round(i["dph_total"], 4),
       "image": i.get("image_uuid"), "disk_gb": i.get("disk_space"), "geolocation": i.get("geolocation"),
       "public_ip": i.get("public_ipaddr"), "ssh_direct": {"host": i.get("public_ipaddr"), "port": p("22/tcp")},
       "ssh_proxy": {"host": i.get("ssh_host"), "port": i.get("ssh_port")},
       "ports": {"22/tcp": p("22/tcp"), "8000/tcp": p("8000/tcp"), "8080/tcp": p("8080/tcp")}}
json.dump(out, open(f"{W}/inst.json", "w"), indent=1)
open(f"{W}/ssh_target", "w").write(f'SSH_HOST={out["public_ip"]}\nSSH_PORT={out["ports"]["22/tcp"]}\n')
print(json.dumps(out, indent=1))
