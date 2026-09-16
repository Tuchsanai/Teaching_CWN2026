"""Instructor only: loopback shop, no external dependencies or live transactions."""
import argparse, json, socket, time
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
p=argparse.ArgumentParser(); p.add_argument('--runtime',required=True); p.add_argument('--token',required=True); p.add_argument('--fd',type=int,required=True)
a=p.parse_args(); root=Path(a.runtime)
class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        with (root/'http.log').open('a') as f: f.write(time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())+' '+fmt%args+'\n')
    def do_GET(self):
        state=json.loads((root/'state.json').read_text())
        release=state['release']; shop=state['shop']; code=200
        catalog=[{'id':'DEMO-1','name':'สมุดฝึกงาน','price':99}]
        if release=='v2-bad':
            code=503; body='Service unavailable: release v2-bad failed catalog initialization'; kind='text/plain'
        elif self.path=='/':
            body=f'<!doctype html><html lang="th"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{shop}</title><style>body{{font:20px system-ui;max-width:760px;margin:60px auto;padding:24px;background:#f3f7f4;color:#173e32}}a{{display:block;background:#fff;padding:24px;margin:16px 0;border-radius:14px;color:#16654b}}small{{color:#49665c}}</style><h1>{shop}</h1><p>ร้านค้าฝึกปฏิบัติ • เวอร์ชัน {release}</p><a href="/api/products">1. ดูสินค้าทดสอบ</a><a href="/api/order-smoke">2. ตรวจคำสั่งซื้อจำลอง</a><small>ไม่มีการขาย ชำระเงิน หรือส่งสินค้าจริง</small></html>'; kind='text/html'
        elif self.path=='/api/products':
            body=json.dumps({'shop':shop,'products':catalog},ensure_ascii=False); kind='application/json'
        elif self.path=='/api/order-smoke':
            body=json.dumps({'shop':shop,'order_id':'DEMO-ORDER','product_id':'DEMO-1','quantity':2,'total':next(item['price'] for item in catalog if item['id']=='DEMO-1')*2,'persisted':False},ensure_ascii=False); kind='application/json'
        else: code=404; body='Not found'; kind='text/plain'
        payload=body.encode(); self.send_response(code); self.send_header('Content-Type',kind+'; charset=utf-8'); self.send_header('Content-Length',str(len(payload))); self.send_header('Cache-Control','no-store'); self.end_headers(); self.wfile.write(payload)
srv=HTTPServer(('127.0.0.1',0),Handler,bind_and_activate=False)
srv.socket.close(); srv.socket=socket.socket(fileno=a.fd); srv.server_address=srv.socket.getsockname(); srv.server_name='localhost'; srv.server_port=srv.server_address[1]
(root/'ready').write_text(a.token)
srv.serve_forever(poll_interval=0.1)
