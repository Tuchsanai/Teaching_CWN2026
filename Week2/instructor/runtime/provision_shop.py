"""Instructor-only port provisioning; no learner edits."""
import argparse,socket
import shop_runtime as shop
ap=argparse.ArgumentParser();ap.add_argument('--port',type=int,required=True);a=ap.parse_args()
if not 1024<=a.port<=65535:raise SystemExit('port must be 1024..65535')
s=shop.read()
if shop.live(s):raise SystemExit('stop this shop before provisioning')
with socket.socket() as sock:sock.bind(('127.0.0.1',a.port))
s['port']=a.port;shop.save(s);print('PROVISIONED',shop.url(s))
