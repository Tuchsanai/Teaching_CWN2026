"""LAB 5 · step 5: can Node 2 reach the coordinator port on Node 1, and what is the RTT / throughput?

On Node 1 (listens on the coordinator port 9000, which Vast maps to an external port):
    python net_probe.py server --port 9000
On Node 2:
    python net_probe.py client --host <node1 ip> --port <external port of 9000> --out net_probe.json

The client measures: TCP connect time · RTT of 1-byte ping-pong (50 rounds) ·
time to send 7.6 MB (≈ one bf16 LoRA gradient) and get it echoed back (5 rounds).
"""
import argparse
import json
import socket
import statistics
import struct
import time


def recv_exact(s, n):
    buf = bytearray(n)
    v = memoryview(buf)
    got = 0
    while got < n:
        k = s.recv_into(v[got:], n - got)
        if k == 0:
            raise ConnectionError("closed")
        got += k
    return buf


def server(a):
    srv = socket.socket()
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", a.port))
    srv.listen(4)
    print(f"listening :{a.port}", flush=True)
    c, addr = srv.accept()
    c.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    print(f"client {addr[0]}", flush=True)
    while True:
        try:
            (n,) = struct.unpack("!I", recv_exact(c, 4))
        except ConnectionError:
            break
        data = recv_exact(c, n) if n else b""
        c.sendall(struct.pack("!I", len(data)) + data)
    c.close()
    srv.close()


def client(a):
    t0 = time.time()
    s = socket.create_connection((a.host, a.port), timeout=30)
    connect_ms = (time.time() - t0) * 1000
    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    def roundtrip(payload):
        t = time.perf_counter()
        s.sendall(struct.pack("!I", len(payload)) + payload)
        (n,) = struct.unpack("!I", recv_exact(s, 4))
        recv_exact(s, n)
        return time.perf_counter() - t

    rtt = [roundtrip(b"x") * 1000 for _ in range(50)]
    big = bytes(int(a.mb * 1_000_000))
    bulk = [roundtrip(big) for _ in range(5)]
    s.close()
    out = {"target": f"{a.host}:{a.port}", "connected": True,
           "tcp_connect_ms": round(connect_ms, 1),
           "rtt_ms": {"min": round(min(rtt), 1), "median": round(statistics.median(rtt), 1),
                      "max": round(max(rtt), 1), "n": len(rtt)},
           "bulk_payload_mb": a.mb,
           "bulk_roundtrip_s": [round(x, 3) for x in bulk],
           "bulk_one_way_mbps_est": round(a.mb * 8 * 2 / statistics.median(bulk), 1)}
    print(json.dumps(out, indent=2))
    if a.out:
        with open(a.out, "w") as f:
            json.dump(out, f, indent=2)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("role", choices=["server", "client"])
    ap.add_argument("--host")
    ap.add_argument("--port", type=int, default=9000)
    ap.add_argument("--mb", type=float, default=7.6)
    ap.add_argument("--out")
    a = ap.parse_args()
    a.mb = float(a.mb)
    server(a) if a.role == "server" else client(a)
