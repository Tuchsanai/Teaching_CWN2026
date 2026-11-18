"""LAB 5 · Coordinator for synchronous data-parallel LoRA training across machines (CPU only).

Opens a TCP port (default 9000) and waits until --replicas workers have joined. A worker
is accepted only if it presents the secret stored on the rented machine (--secret-file,
created once with `python -c "import secrets;print(secrets.token_hex(32))" > cluster_secret`).

Every weight update (synchronous):
    1. receive the bf16 LoRA gradient of every replica (in parallel threads)
    2. average them in float32, round back to bf16
    3. send the same average to every replica at the same time (parallel threads)
Each replica then applies the average with its own (identical) AdamW, so all replicas stay
bit-identical; at the end every replica reports a checksum of its LoRA weights.

Wire format: 4-byte big-endian header length · JSON header · optional raw payload of
header["nbytes"] bytes.

Usage:
    python coordinator.py --replicas 2 --steps 20 --warmup 3 --out runs/B_eb8/coordinator.json
"""
import argparse
import hmac
import json
import os
import socket
import struct
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np


# ---------------------------------------------------------------- wire helpers
def recv_exact(sock, n):
    buf = bytearray(n)
    view = memoryview(buf)
    got = 0
    while got < n:
        k = sock.recv_into(view[got:], n - got)
        if k == 0:
            raise ConnectionError("peer closed")
        got += k
    return buf


def send_msg(sock, header, payload=b""):
    if payload:
        header = dict(header, nbytes=len(payload))
    h = json.dumps(header).encode()
    sock.sendall(struct.pack("!I", len(h)) + h)
    if payload:
        sock.sendall(payload)


def recv_msg(sock):
    (n,) = struct.unpack("!I", recv_exact(sock, 4))
    header = json.loads(recv_exact(sock, n))
    payload = recv_exact(sock, header["nbytes"]) if header.get("nbytes") else b""
    return header, payload


# ---------------------------------------------------------------- bf16 <-> fp32 (numpy)
def bf16_to_f32(raw):
    u16 = np.frombuffer(raw, dtype=np.uint16)
    return (u16.astype(np.uint32) << 16).view(np.float32)


def f32_to_bf16(x):
    u32 = x.astype(np.float32).view(np.uint32)
    rounding = ((u32 >> 16) & 1) + np.uint32(0x7FFF)       # round to nearest even
    return ((u32 + rounding) >> 16).astype(np.uint16).tobytes()


# ---------------------------------------------------------------- main loop
def main(a):
    with open(a.secret_file) as f:
        secret = f.read().strip()

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", a.port))
    srv.listen(64)
    print(f"[coord] listening on :{a.port}, waiting for {a.replicas} replicas", flush=True)

    conns, hellos, rejected = [], [], 0
    t_open = time.time()
    while len(conns) < a.replicas:
        c, addr = srv.accept()
        c.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        c.settimeout(a.timeout)
        try:
            h, _ = recv_msg(c)
        except Exception:
            c.close()
            continue
        if h.get("type") != "hello" or not hmac.compare_digest(str(h.get("secret", "")), secret):
            rejected += 1
            print(f"[coord] rejected {addr[0]} (wrong secret)", flush=True)
            try:
                send_msg(c, {"type": "reject"})
            finally:
                c.close()
            continue
        h.pop("secret", None)
        h["peer"] = addr[0]
        conns.append(c)
        hellos.append(h)
        print(f"[coord] replica {len(conns)}/{a.replicas} joined from {addr[0]} "
              f"({h.get('host')}, mode {h.get('mode')}, accum {h.get('accum')})", flush=True)

    accums = {h["accum"] for h in hellos}
    if len(accums) != 1:
        raise SystemExit(f"replicas disagree on accumulation: {accums}")
    accum = accums.pop()
    world = len(conns)
    eff_batch = world * accum
    t_ready = time.time()
    for r, c in enumerate(conns):
        send_msg(c, {"type": "start", "rank": r, "world": world, "steps": a.steps,
                     "effective_batch": eff_batch, "accum": accum})

    pool = ThreadPoolExecutor(max_workers=world)
    steps = []
    t_train0 = time.time()
    for s in range(a.steps):
        t0 = time.time()
        arrive = [None] * world
        msgs = [None] * world

        def _recv(r):
            msgs[r] = recv_msg(conns[r])
            arrive[r] = time.time()

        list(pool.map(_recv, range(world)))
        t_all = time.time()
        total = None
        for h, p in msgs:
            g = bf16_to_f32(p)
            total = g.copy() if total is None else total + g
        avg = f32_to_bf16(total / world)
        t_avg = time.time()

        def _send(r):
            send_msg(conns[r], {"type": "avg", "step": s}, avg)

        list(pool.map(_send, range(world)))
        t_sent = time.time()
        losses = [h["loss"] for h, _ in msgs]
        rec = {"step": s + 1,
               "loss_mean": round(float(np.mean(losses)), 5),
               "loss_per_replica": [round(x, 5) for x in losses],
               "grad_mb_per_replica": round(len(msgs[0][1]) / 1e6, 3),
               "first_to_last_arrival_s": round(max(arrive) - min(arrive), 3),
               "average_s": round(t_avg - t_all, 4),
               "broadcast_s": round(t_sent - t_avg, 4),
               "step_wall_s": round(t_sent - t0, 3)}
        steps.append(rec)
        print(f"[coord] step {s + 1}/{a.steps} loss {rec['loss_mean']:.4f} "
              f"wall {rec['step_wall_s']:.2f}s avg+bcast {rec['average_s'] + rec['broadcast_s']:.3f}s", flush=True)
    t_train1 = time.time()

    # final checksums
    finals = [None] * world

    def _final(r):
        finals[r], _ = recv_msg(conns[r])
        send_msg(conns[r], {"type": "bye"})

    list(pool.map(_final, range(world)))
    for c in conns:
        c.close()
    srv.close()

    sums = [f["checksum"] for f in finals]
    w = a.warmup
    meas = steps[w:]
    out = {"replicas": world, "accum_per_replica": accum, "effective_batch": eff_batch,
           "steps": a.steps, "warmup_excluded": w, "port": a.port, "rejected_connections": rejected,
           "wait_for_replicas_s": round(t_ready - t_open, 1),
           "train_wall_s": round(t_train1 - t_train0, 2),
           "replicas_info": hellos,
           "checksums": sums, "checksums_match": len(set(sums)) == 1,
           "summary_measured_steps": {
               "n": len(meas),
               "sec_per_update": round(float(np.mean([m["step_wall_s"] for m in meas])), 3),
               "receipts_per_sec": round(eff_batch / float(np.mean([m["step_wall_s"] for m in meas])), 3),
           },
           "per_step": steps}
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w") as f:
        json.dump(out, f, indent=2)
    print(f"[coord] done · checksums match: {out['checksums_match']} · "
          f"{out['summary_measured_steps']['sec_per_update']} s/update", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=9000)
    ap.add_argument("--replicas", type=int, required=True)
    ap.add_argument("--steps", type=int, required=True, help="number of weight updates")
    ap.add_argument("--warmup", type=int, default=0, help="first N updates excluded from the summary")
    ap.add_argument("--secret-file", default="/workspace/lab5/cluster_secret")
    ap.add_argument("--timeout", type=float, default=1800)
    ap.add_argument("--out", default="coordinator.json")
    main(ap.parse_args())
